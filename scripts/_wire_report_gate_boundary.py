# -*- coding: utf-8 -*-
"""Wire UserGate:报告审阅 as the M2->M3 boundary: 主题共识(03.5) comes after the report gate."""
import io, json
P = r"F:/AI/kesheng/packs/sop-seed/kg.json"
d = json.load(io.open(P, encoding="utf-8-sig"))
rels = d.setdefault("relations", [])
new = [("KspStep:KSP-03.5主题共识", "UserGate:报告审阅(中间交付件)", "ksp-after-gate")]
have = {(r.get("source"), r.get("target"), r.get("type")) for r in rels}
ar = 0
for s,t,ty in new:
    if (s,t,ty) not in have:
        rels.append({"source":s,"target":t,"type":ty,"props":{}}); ar += 1
json.dump(d, io.open(P,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("added", ar, "rel (KSP-03.5 after report gate)")
