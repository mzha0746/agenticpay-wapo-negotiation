"""Diagnostic: how closely the schedule_value buyer followed its concession schedule."""
import glob
import json
import sys

sys.path.insert(0, "../src")
from negotiate import extract_price

SCHEDULE = [150, 165, 178, 188, 196, 203, 209, 214] + [min(214 + 3 * k, 250) for k in range(1, 13)]
over = tot = 0
for f in sorted(glob.glob("persona_schedule_value_run*.json")):
    r = json.load(open(f, encoding="utf-8"))
    offs = [extract_price(h["content"]) for h in r["history"] if h["role"] == "buyer"]
    for rnd, p in enumerate(offs):
        tot += 1
        over += p is not None and p > SCHEDULE[rnd] + 0.01
    sellers = [extract_price(h["content"]) for h in r["history"] if h["role"] == "seller"]
    print(f[-11:-5], "buyer:", offs, "| seller:", sellers)
print("buyer offers above schedule:", over, "/", tot)
