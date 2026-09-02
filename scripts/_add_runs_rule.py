# -*- coding: utf-8 -*-
"""Add ProcessRule:runs只放项目 to workflow-seed (工艺), wire to 五层检查体系, rebuild."""
import io, json

P = r"F:/AI/kesheng/packs/workflow-seed/kg.json"
d = json.load(io.open(P, encoding="utf-8-sig"))
ents = d.setdefault("entities", [])
rels = d.setdefault("relations", [])

new_ent = {"id":"ProcessRule:runs只放项目","type":"ProcessRule","name":"runs只放项目",
 "props":{"说明":"runs/ 只允许项目 run（每项目一个 runs/<项目slug>/）；非项目散落/临时（_tmp-*/_lessons/_research-*）一律不进或交付前删；交付前跑 scripts/check_runs_clean.py 守护。","出处":"orchestration/ORCHESTRATION.md §5-15"},
 "sources":["orchestration/ORCHESTRATION.md","scripts/check_runs_clean.py"],"domains":["工艺"]}
if not any(e["id"] == new_ent["id"] for e in ents):
    ents.append(new_ent)
new_rels = [("ProcessRule:runs只放项目","Rule:五层检查体系","concept-related-to")]
have = {(r.get("source"), r.get("target"), r.get("type")) for r in rels}
ar = 0
for s, t, ty in new_rels:
    if (s, t, ty) not in have:
        rels.append({"source": s, "target": t, "type": ty, "props": {}}); ar += 1
json.dump(d, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"added ProcessRule:runs只放项目 + {ar} relation")
