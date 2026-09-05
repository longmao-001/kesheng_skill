# -*- coding: utf-8 -*-
"""List unique candidates (deduped by title) for manual curation."""
import json

SRC = "F:/AI/kesheng/packs/papers-kj-wenan-kg/candidates.json"
data = json.load(open(SRC, encoding="utf-8"))

seen = {}
order = []
for q, recs in data.items():
    for r in recs:
        t = (r["title"] or "").strip().lower()
        if not t:
            continue
        if t in seen:
            continue
        seen[t] = True
        r["query"] = q
        order.append(r)

order.sort(key=lambda r: -((r["cited_by_count"] or 0)))
print(f"TOTAL unique: {len(order)}\n")
for i, r in enumerate(order, 1):
    doi = (r["doi"] or "NODDOI")
    jour = (r["journal"] or "")
    q = r["query"] or ""
    print(f"{i:3d} | {r['year']} | c={r['cited_by_count'] or 0:>4} | {(r['title'] or '')[:95]}")
    print(f"     | doi={doi[:70]} | {jour[:45]} | q='{q[:40]}'")
