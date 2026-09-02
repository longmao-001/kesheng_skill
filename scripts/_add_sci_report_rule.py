# -*- coding: utf-8 -*-
"""Add ProcessRule:科学报告进对话 docx/ppt to sop-seed (工艺), wire to KSP-03, rebuild."""
import io, json
P = r"F:/AI/kesheng/packs/sop-seed/kg.json"
d = json.load(io.open(P, encoding="utf-8-sig"))
ents = d.setdefault("entities", []); rels = d.setdefault("relations", [])
e = {"id":"ProcessRule:科学报告进对话","type":"ProcessRule","name":"科学报告进对话+docx/PPT",
 "props":{"说明":"科学调查官 M2 完成后：完整报告写进对话(不压3行总结) + 产出 docx+PPT(可上图)；讲透 重点/时间/产品原理/产品卖点/科学原理；用 report-writer/markdown-exporter(报告)、ppt-master/markdown-exporter/pipitmk(PPT) 赋能。","出处":"orchestration/ORCHESTRATION.md §5-18"},
 "sources":["orchestration/ORCHESTRATION.md","templates/science-report.md","templates/science-ppt.md","agents/scientist.md"],"domains":["工艺"]}
if not any(x["id"] == e["id"] for x in ents):
    ents.append(e)
new = [("ProcessRule:科学报告进对话","KspStep:KSP-03 科学理解","concept-related-to")]
have = {(r.get("source"), r.get("target"), r.get("type")) for r in rels}
ar = 0
for s,t,ty in new:
    if (s,t,ty) not in have:
        rels.append({"source":s,"target":t,"type":ty,"props":{}}); ar += 1
json.dump(d, io.open(P,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("added ProcessRule:科学报告进对话 +", ar, "rel")
