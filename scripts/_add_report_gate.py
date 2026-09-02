# -*- coding: utf-8 -*-
"""Add UserGate:报告审阅(中间交付件) to sop-seed (工艺), wire to KSP-03 + 制片人工作流程, rebuild."""
import io, json
P = r"F:/AI/kesheng/packs/sop-seed/kg.json"
d = json.load(io.open(P, encoding="utf-8-sig"))
ents = d.setdefault("entities", []); rels = d.setdefault("relations", [])
e = {"id":"UserGate:报告审阅(中间交付件)","type":"UserGate","name":"报告审阅（中间交付件）",
 "props":{"里程碑":"KSP-03","问题":"科学调查报告是否已读完、可进入下一步",
   "选项":"已读完·继续(Recommended) / 需修改（指出哪里）/ 补充材料（列缺的）",
   "推荐":"已读完·继续","规则":"收到用户「继续」前禁止推进任何后续环节/拍板选项（ORCHESTRATION §5-10 先读后谈）",
   "依据":"orchestration/ORCHESTRATION.md §5-10 / docs/USER_SOP.md KSP-03"},
 "sources":["orchestration/ORCHESTRATION.md","docs/USER_SOP.md","templates/science-report.md"],"domains":["工艺"]}
if not any(x["id"] == e["id"] for x in ents):
    ents.append(e)
new = [("KspStep:KSP-03 科学理解","UserGate:报告审阅(中间交付件)","ksp-has-gate"),
       ("UserGate:报告审阅(中间交付件)","RoleWorkflow:制片人工作流程","gate-in")]
have = {(r.get("source"), r.get("target"), r.get("type")) for r in rels}
ar = 0
for s,t,ty in new:
    if (s,t,ty) not in have:
        rels.append({"source":s,"target":t,"type":ty,"props":{}}); ar += 1
json.dump(d, io.open(P,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("added UserGate:报告审阅 +", ar, "rel")
