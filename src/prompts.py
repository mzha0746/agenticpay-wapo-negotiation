"""Prompt templates.

BUYER_TEMPLATE / SELLER_TEMPLATE are Tables 14 and 15 of the AgenticPay paper
(arXiv:2602.06008) copied verbatim; only the {placeholders} are filled in.
Persona facts are injected through {context} (and {preference_guidance} for the
buyer), which is exactly where the paper's framework puts agent-specific info.
Buyer strategy variants are appended as an extra block before the final
"Now, respond as Buyer:" line; the seller prompt is never changed between
variants.
"""

from facts import (BEZOS_SELF, GRAHAM_SELF, PUBLIC_ASSET, BEZOS_ABOUT_GRAHAM,
                    GRAHAM_ABOUT_BEZOS, bullets)

BUYER_TEMPLATE = """You are {name}, a buyer looking for a good deal. You are polite, strategic, and want to get the best price within your budget.
Context Information: {context}
Current Negotiation State: {current_state}
Conversation History: {conversation_history}
Please respond naturally as {name} would. Be strategic but realistic in your negotiation.
IMPORTANT:
- Your top price is ${max_price} (confidential, do not reveal).
- Current product information: {product_info}
- Available products: {available_products}
- Consider the environment: {environment_info}.
- CRITICAL: In each turn, you MUST make exactly ONE price offer for the product using the format:
### BUYER_PRICE($X) ###
- IMPORTANT: BUYER_PRICE($X) must be the TOTAL PRICE for the entire order/transaction, NOT a per-unit price.
If ordering multiple units/items, $X should be the total amount you will pay.
Example: For 10,000 units at $0.40 each, use ### BUYER_PRICE($4000) ###, NOT ### BUYER_PRICE($0.40) ###
- Example: "I can offer ### BUYER_PRICE($10) ### for this product."
- Example: "How about ### BUYER_PRICE($12.50) ###?"
- This specific format is required for the system to correctly extract your offer price.
- NEVER reveal your maximum acceptable price to the seller.
{msg_rule}- Keep communication short (150 words or less), clear, and focused on negotiation.
DEAL AGREEMENT INSTRUCTION:
- Only finalize the transaction when you believe the price is reasonably balanced.
- If you decide to accept the deal, you MUST include the exact phrase "MAKE_DEAL" in your response.
- Example: "That sounds acceptable to me. MAKE_DEAL"
USER PREFERENCES: {preference_guidance}
{strategy}Now, respond as {name}:"""

SELLER_TEMPLATE = """You are {name}, a seller trying to maximize profit while being reasonable. You are professional, friendly, and want to close a deal that benefits both parties.
Context Information: {context}
Current Negotiation State: {current_state}
Conversation History: {conversation_history}
Please respond naturally as {name} would. Be strategic but realistic in your negotiation.
IMPORTANT REMINDERS:
- Your initial asking price is ${initial_price}.
- Your minimum acceptable price (confidential) is ${min_price}. Never reveal it.
- Current product information: {product_info}
- Available products: {available_products}
- Consider the environment factors: {environment_info}.
- CRITICAL: In each turn, you MUST make exactly ONE price offer for the product using the format:
### SELLER_PRICE($X) ###
- IMPORTANT: SELLER_PRICE($X) must be the TOTAL PRICE for the entire order/transaction, NOT a per-unit price.
If selling multiple units/items, $X should be the total amount the buyer will pay.
Example: For 10,000 units at $0.40 each, use ### SELLER_PRICE($4000) ###, NOT ### SELLER_PRICE($0.40) ###
- Example: "I can offer ### SELLER_PRICE($15) ### for this product."
- Example: "How about ### SELLER_PRICE($13.00) ###?"
- This specific format is required for the system to correctly extract your offer price.
- NEVER reveal your minimum acceptable price to the buyer.
{msg_rule}- Keep communication short (150 words or less), professional, and negotiation-focused.
DEAL AGREEMENT INSTRUCTION:
- Only finalize the transaction when you believe the price is reasonably balanced.
- If you decide to accept the deal, you MUST include the exact phrase "MAKE_DEAL" in your response.
- Example: "I accept your offer. MAKE_DEAL"
Now, respond as {name}:"""

# ---- Shared scenario (same for every condition) ----
PRODUCT_INFO = {
    "name": "The Washington Post newspaper publishing businesses",
    "includes": ["The Washington Post", "Express", "The Gazette Newspapers", "Southern Maryland Newspapers",
                 "Fairfax County Times", "El Tiempo Latino", "Greater Washington Publishing", "Robinson Terminal"],
    "excludes": ["Slate, TheRoot.com, Foreign Policy", "WaPo Labs, SocialCode",
                 "downtown DC headquarters building and certain other real estate"],
    "condition": "Iconic 136-year-old brand; revenue declining, operating losses in 2011-2012",
    "price_unit": "USD millions",
}
ENVIRONMENT_INFO = {
    "date": "July 2013",
    "setting": "Private talks, Allen & Co. conference, Sun Valley, Idaho",
    "currency": "All prices are in millions of US dollars ($300 means $300 million)",
}
# Harness fix (applied identically to buyer AND seller, never varied between buyer
# variants): with the verbatim Table 14/15 prompts Qwen3-4B replies with only the
# price tag ("### BUYER_PRICE($300) ###") and never talks, so persona facts and
# arguments can't matter. This one line restores natural-language messages.
MSG_RULE = "- Write your reply as a natural-language message to the other party (2-5 sentences) that includes your one price offer tag.\n"
AVAILABLE_PRODUCTS = "Only the product above (single-asset deal)."
INITIAL_PRICE = 400
BUYER_MAX = 350
SELLER_MIN = 200


def _facts_block(title, facts):
    return f"\n- {title}:\n{bullets(facts)}"


def buyer_context(persona: bool) -> str:
    ctx = ("- user_requirement: Acquire The Washington Post newspaper publishing businesses\n"
           f"- max_price: {BUYER_MAX}")
    if persona:
        ctx += _facts_block("who_you_are (public information)", BEZOS_SELF)
        ctx += _facts_block("about_the_seller (public information)", BEZOS_ABOUT_GRAHAM)
        ctx += _facts_block("public_facts_about_the_asset", PUBLIC_ASSET)
    return ctx


def seller_context(persona: bool) -> str:
    ctx = f"- min_price: {SELLER_MIN}"
    if persona:
        ctx += _facts_block("who_you_are (public information)", GRAHAM_SELF)
        ctx += _facts_block("about_the_buyer (public information)", GRAHAM_ABOUT_BEZOS)
        ctx += _facts_block("public_facts_about_the_asset", PUBLIC_ASSET)
    return ctx


def buyer_preferences(persona: bool) -> str:
    if not persona:
        return "None specified."
    return ("You are a disciplined, data-driven, long-term investor. You are buying with your own money, "
            "you do not need this deal, and you value the Post's journalism and its future more than a quick win.")


# ---- Buyer strategy variants (only the buyer prompt changes) ----
STRATEGIES = {
    "original": "",

    # Variant A: classic negotiation tactics grounded in the public facts.
    "anchor_evidence": """NEGOTIATION STRATEGY (private, follow it):
- Anchor low: open well below what you expect to pay (around $150) and justify it with the public numbers: seven straight years of revenue decline, a $53.7M operating loss in 2012, widening losses in Q1 2013, circulation falling ~8% a year, and the headquarters building not included.
- Value the business as a turnaround that needs years of your own investment; say so explicitly.
- Concede slowly and in shrinking steps (e.g., +$20, then +$10, then +$5). Never jump to meet the seller halfway, and never "split the difference".
- Remind the seller that you do not need this deal (strong alternatives for your capital) and that the paper's best future is with an owner who can fund losses patiently.
- Your private target is about $220. Do not say MAKE_DEAL above $250 unless the negotiation is about to run out of rounds.
""",

    # Variant B: Variant A + an explicit concession schedule and non-price value trade.
    "schedule_value": """NEGOTIATION STRATEGY (private, follow it exactly):
- Your offers follow a fixed concession schedule by round number: round 0: $150, round 1: $165, round 2: $178, round 3: $188, round 4: $196, round 5: $203, round 6: $209, round 7: $214, round 8+: +$3 per round, never above $250. Never offer more than the schedule allows, even if the seller pushes.
- Instead of conceding on price, give the seller what he truly cares about at no cost to you: keep the current publisher and editors, protect the newsroom's independence, commit to long-term investment in digital journalism, and pay all cash with a quick, certain close (no financing risk for his shareholders).
- Justify your price with the public numbers (seven years of revenue decline, $53.7M operating loss in 2012, widening Q1 2013 loss, falling circulation, headquarters building excluded).
- If the seller's latest offer is at or below your schedule price for this round, accept it with MAKE_DEAL. Otherwise make your scheduled offer.
""",
}


def build_buyer_prompt(state: dict, history: str, persona: bool, strategy: str, msg_rule: bool = True) -> str:
    strat = STRATEGIES[strategy]
    return BUYER_TEMPLATE.format(
        name="Jeff Bezos" if persona else "Buyer",
        context=buyer_context(persona), current_state=_fmt_state(state),
        conversation_history=history, max_price=BUYER_MAX, product_info=PRODUCT_INFO,
        available_products=AVAILABLE_PRODUCTS, environment_info=ENVIRONMENT_INFO,
        preference_guidance=buyer_preferences(persona),
        strategy=(strat + "\n") if strat else "", msg_rule=MSG_RULE if msg_rule else "")


def build_seller_prompt(state: dict, history: str, persona: bool, msg_rule: bool = True) -> str:
    return SELLER_TEMPLATE.format(
        name="Donald Graham" if persona else "Seller",
        context=seller_context(persona), current_state=_fmt_state(state),
        conversation_history=history, initial_price=INITIAL_PRICE, min_price=SELLER_MIN,
        product_info=PRODUCT_INFO, available_products=AVAILABLE_PRODUCTS,
        environment_info=ENVIRONMENT_INFO, msg_rule=MSG_RULE if msg_rule else "")


def _fmt_state(state: dict) -> str:
    return "\n" + "\n".join(f"- {k}: {v}" for k, v in state.items())
