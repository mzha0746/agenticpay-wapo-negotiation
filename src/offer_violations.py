"""Diagnostic: offers (not just deals) that crossed a party's own reservation price."""
import glob
import json
from collections import Counter

from negotiate import extract_price
from prompts import BUYER_MAX, SELLER_MIN

c = Counter()
for f in glob.glob("../results/*_run*.json"):
    r = json.load(open(f, encoding="utf-8"))
    for h in r["history"]:
        p = extract_price(h["content"])
        if h["role"] == "seller" and p is not None and p < SELLER_MIN:
            c[(r["condition"], "seller offer < 200")] += 1
        if h["role"] == "buyer" and p is not None and p > BUYER_MAX:
            c[(r["condition"], "buyer offer > 350")] += 1
        if "350" in h["content"] and h["role"] == "buyer":
            c[(r["condition"], "buyer mentions 350")] += 1
        if "200" in h["content"] and h["role"] == "seller" and "SELLER_PRICE($200)" not in h["content"]:
            c[(r["condition"], "seller mentions 200 outside tag")] += 1
for k in sorted(c):
    print(k, c[k])
