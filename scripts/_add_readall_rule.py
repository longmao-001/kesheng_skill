# -*- coding: utf-8 -*-
"""Add ProcessRule:启动读全核心流程 to workflow-seed (工艺), wire, rebuild."""
import io, json
P = r"F:/AI/kesheng/packs/workflow-seed/kg.json"
d = json.load(io.open(P, encoding="utf-8-sig"))
ents = d.setdefault("entities", []); rels = d.setdefault("relations", [])
e = {"id":"ProcessRule:启动读全核心流程","type":"ProcessRule","name":"启动读全核心流程",
 "props":{"说明":"每次接手任务，制片人先读全核心流程全集（USER_SOP/ORCHESTRATION/quality-gate/production-workflow/user-gate，见 SKILL.md 启动必读）再开工；未读全前禁止派活/建文件。知识库(kg 等)用 kg_query 按需查，不一次全读；产物只落 runs/项目 (与 runs只放项目 联动)，根治到处建文件。","出处":"SKILL.md 启动必读 / ORCHESTRATION §5-19"},
 "sources":["SKILL.md","orchestration/ORCHESTRATION.md","docs/USER_SOP.md"],"domains":["工艺"]}
if not any(x["id"] == e["id"] for x in ents):
    ents.append(e)
new = [("ProcessRule:启动读全核心流程","RoleWorkflow:制片人工作流程","concept-related-to"),
       ("ProcessRule:启动读全核心流程","ProcessRule:runs只放项目","concept-related-to")]
have = {(r.get("source"), r.get("target"), r.get("type")) for r in rels}
ar = 0
for s,t,ty in new:
    if (s,t,ty) not in have:
        rels.append({"source":s,"target":t,"type":ty,"props":{}}); ar += 1
json.dump(d, io.open(P,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("added ProcessRule:启动读全核心流程 +", ar, "rel")
