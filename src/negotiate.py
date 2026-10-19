"""1 buyer x 1 seller x 1 product negotiation, following AgenticPay Task1 mechanics.

Mechanics mirrored from agenticpay/envs/single_buyer_product_seller/Task1_basic_price_negotiation.py:
  * each round the buyer speaks first, then the seller (who sees the buyer's message);
  * prices are parsed from ### BUYER_PRICE($X) ### / ### SELLER_PRICE($X) ### (same regex);
  * max_rounds = 20 (agenticpay/examples/config.py), price_tolerance = 0;
  * if seller_price <= buyer_price the deal closes at the seller's price.
Plus the MAKE_DEAL protocol from the paper's prompts (Tables 14/15): a party that
says MAKE_DEAL accepts the counterpart's most recent offer.

The LLM is any OpenAI-compatible /v1/chat/completions server, e.g.
  llama-server -m Qwen3-4B-Instruct-2507-Q8_0.gguf      (what we used)
  vllm serve Qwen/Qwen3-4B-Instruct-2507               (same script, full-precision weights)
"""

import argparse
import json
import re
import time
from pathlib import Path

import requests

from prompts import build_buyer_prompt, build_seller_prompt, BUYER_MAX, SELLER_MIN

MAX_ROUNDS = 20
PRICE_RE = r'###\s*(?:BUYER_PRICE|SELLER_PRICE)\s*\(\$([\d,]+\.?\d*)\)\s*###'


class ChatLLM:
    def __init__(self, base_url, model, temperature, top_p, top_k, max_tokens):
        self.url = base_url.rstrip("/") + "/v1/chat/completions"
        self.model = model
        self.sampling = dict(temperature=temperature, top_p=top_p, top_k=top_k, max_tokens=max_tokens)

    def generate(self, prompt: str, seed: int) -> str:
        body = {"model": self.model, "messages": [{"role": "user", "content": prompt}], "seed": seed, **self.sampling}
        r = requests.post(self.url, json=body, timeout=600)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()


def extract_price(text):
    m = re.findall(PRICE_RE, text, re.IGNORECASE)
    if not m:
        return None
    try:
        return float(m[-1].replace(",", ""))
    except ValueError:
        return None


def format_history(history):
    if not history:
        return "No conversation history yet."
    return "\n" + "\n".join(f"[Round {h['round']}] {h['role'].upper()}: {h['content']}" for h in history)


def run_negotiation(llm, persona, strategy, seed, msg_rule=True):
    history, buyer_price, seller_price = [], None, None
    result = {"deal": False, "price": None, "rounds": MAX_ROUNDS, "closed_by": None}
    call = 0
    for rnd in range(MAX_ROUNDS):
        state = {"current_round": rnd, "max_rounds": MAX_ROUNDS,
                 "rounds_remaining": MAX_ROUNDS - rnd,
                 "buyer_last_offer": buyer_price, "seller_last_offer": seller_price}

        # Buyer turn
        msg = llm.generate(build_buyer_prompt(state, format_history(history), persona, strategy, msg_rule), seed * 1000 + call)
        call += 1
        history.append({"round": rnd, "role": "buyer", "content": msg})
        p = extract_price(msg)
        if "MAKE_DEAL" in msg and seller_price is not None:
            result.update(deal=True, price=seller_price, rounds=rnd + 1, closed_by="buyer MAKE_DEAL")
            result["buyer_offer_in_accept_msg"] = p
            break
        if p is not None:
            buyer_price = p

        # Seller turn (sees buyer's message)
        state.update(buyer_last_offer=buyer_price)
        msg = llm.generate(build_seller_prompt(state, format_history(history), persona, msg_rule), seed * 1000 + call)
        call += 1
        history.append({"round": rnd, "role": "seller", "content": msg})
        p = extract_price(msg)
        if "MAKE_DEAL" in msg and buyer_price is not None:
            result.update(deal=True, price=buyer_price, rounds=rnd + 1, closed_by="seller MAKE_DEAL")
            result["seller_offer_in_accept_msg"] = p
            break
        if p is not None:
            seller_price = p

        # Repo rule: seller's ask <= buyer's bid -> deal at seller's price
        if buyer_price is not None and seller_price is not None and seller_price <= buyer_price:
            result.update(deal=True, price=seller_price, rounds=rnd + 1, closed_by="prices crossed")
            break

    result.update(
        last_buyer_offer=buyer_price, last_seller_offer=seller_price,
        buyer_reservation_violated=bool(result["deal"] and result["price"] > BUYER_MAX),
        seller_reservation_violated=bool(result["deal"] and result["price"] < SELLER_MIN),
        history=history)
    return result


CONDITIONS = {
    # name: (persona facts?, buyer strategy, natural-language message rule?)
    "paper_verbatim": (False, "original", False),
    "paper_default": (False, "original", True),
    "persona_original": (True, "original", True),
    "persona_anchor_evidence": (True, "anchor_evidence", True),
    "persona_schedule_value": (True, "schedule_value", True),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:8080")
    ap.add_argument("--model", default="Qwen3-4B-Instruct-2507")
    ap.add_argument("--conditions", nargs="+", default=list(CONDITIONS))
    ap.add_argument("--runs", type=int, default=10)
    ap.add_argument("--temperature", type=float, default=0.7)   # Qwen3-2507 recommended sampling
    ap.add_argument("--top-p", type=float, default=0.8)
    ap.add_argument("--top-k", type=int, default=20)
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--out", default="results")
    args = ap.parse_args()

    llm = ChatLLM(args.base_url, args.model, args.temperature, args.top_p, args.top_k, args.max_tokens)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for cond in args.conditions:
        persona, strategy, msg_rule = CONDITIONS[cond]
        for i in range(args.runs):
            f = out / f"{cond}_run{i:02d}.json"
            if f.exists():  # resumable
                continue
            t0 = time.time()
            res = run_negotiation(llm, persona, strategy, seed=i + 1, msg_rule=msg_rule)
            res.update(condition=cond, run=i, seed=i + 1, seconds=round(time.time() - t0, 1),
                       sampling=llm.sampling, model=args.model)
            f.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"{cond} run{i}: deal={res['deal']} price={res['price']} rounds={res['rounds']} "
                  f"({res['closed_by']}, {res['seconds']}s)", flush=True)


if __name__ == "__main__":
    main()
