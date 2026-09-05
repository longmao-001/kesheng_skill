# -*- coding: utf-8 -*-
"""Add ProcessRule:科学检察官报告规范 to workflow-seed (工艺), wire to 五层检查体系, rebuild."""
import io, json
P = r"F:/AI/kesheng/packs/workflow-seed/kg.json"
d = json.load(io.open(P, encoding="utf-8-sig"))
ents = d.setdefault("entities", []); rels = d.setdefault("relations", [])
e = {"id":"ProcessRule:科学检察官报告规范","type":"ProcessRule","name":"科学检察官(L3)报告规范",
 "props":{"说明":"L3 事实检察官按 templates/l3-fact-inspector-report.md 报告：断言→证据(原文/截图/DOI)→判定→建议改法→推翻条件；三态裁决(PASS/CONDITIONAL/BLOCK)；孤儿数字/教科书当本机/大概率待确认当证据=FAIL；绝对化词 ad_forbidden_words。参考 atelier(report-writer 质检≥90% + safety-officer 三态/对抗找茬)。","出处":"templates/l3-fact-inspector-report.md / atelier report-writer+safety-officer"},
 "sources":["templates/l3-fact-inspector-report.md","agents/inspector.md","agents/scientist.md"],"domains":["工艺"]}
if not any(x["id"] == e["id"] for x in ents):
    ents.append(e)
rel = ("ProcessRule:科学检察官报告规范","Rule:五层检查体系","concept-related-to")
if rel not in {(r.get("source"),r.get("target"),r.get("type")) for r in rels}:
    rels.append({"source":rel[0],"target":rel[1],"type":rel[2],"props":{}})
json.dump(d, io.open(P,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("added ProcessRule:科学检察官报告规范")
