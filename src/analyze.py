"""Aggregate results/*.json into a summary table (markdown + json)."""

import json
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

from negotiate import CONDITIONS

res_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "results")
rows = defaultdict(list)
for f in sorted(res_dir.glob("*_run*.json")):
    r = json.loads(f.read_text(encoding="utf-8"))
    rows[r["condition"]].append(r)


def fmt(x, d=1):
    return "-" if x is None else f"{x:.{d}f}"


summary = {}
lines = ["| Condition | n | Deal rate | Avg final price ($M, deals) | Std | Min-Max | Avg rounds | Closed by | Reservation violations |",
         "|---|---|---|---|---|---|---|---|---|"]
for cond in CONDITIONS:
    rs = rows.get(cond, [])
    if not rs:
        continue
    prices = [r["price"] for r in rs if r["deal"]]
    closers = defaultdict(int)
    for r in rs:
        closers[r["closed_by"] or "timeout"] += 1
    viol = sum(r["buyer_reservation_violated"] or r["seller_reservation_violated"] for r in rs)
    s = dict(n=len(rs), deal_rate=len(prices) / len(rs),
             avg_price=st.mean(prices) if prices else None,
             std_price=st.stdev(prices) if len(prices) > 1 else None,
             min_price=min(prices) if prices else None, max_price=max(prices) if prices else None,
             avg_rounds=st.mean(r["rounds"] for r in rs),
             closed_by=dict(closers), violations=viol, prices=prices)
    summary[cond] = s
    lines.append(f"| {cond} | {s['n']} | {s['deal_rate']:.0%} | {fmt(s['avg_price'])} | {fmt(s['std_price'])} | "
                 f"{fmt(s['min_price'],0)}-{fmt(s['max_price'],0)} | {s['avg_rounds']:.1f} | "
                 f"{', '.join(f'{k}: {v}' for k, v in closers.items())} | {viol} |")

print("\n".join(lines))
(res_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
(res_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
