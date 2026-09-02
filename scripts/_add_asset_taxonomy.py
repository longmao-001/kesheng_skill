# -*- coding: utf-8 -*-
"""Add asset-library taxonomy & naming rules to director-kg (美术/工艺), rebuild union."""
import io, json

P = r"F:/AI/kesheng/packs/director-kg/kg.json"
d = json.load(io.open(P, encoding="utf-8-sig"))
ents = d.setdefault("entities", [])
rels = d.setdefault("relations", [])

new_ents = [
 {"id":"Concept:素材库分类两轴","type":"Concept","name":"素材库分类（两轴）",
  "props":{"说明":"用途分级（IN直接入镜/RF参考图/CT内容参考）× 内容类型（MAIN主体锚/PART部件/SCENE场景/TEXT质感/STR结构/DATA图表/BRAND品牌/RAW实拍）；文件名=条目ID。","出处":"templates/assets-inventory.md"},
  "sources":["templates/assets-inventory.md","playbooks/production-workflow.md"],"domains":["美术"]},
 {"id":"Rule:素材文件名即条目ID","type":"Rule","name":"素材文件名即条目ID",
  "props":{"说明":"文件名编码 用途/类型/主体/视角，引用一律用文件名（选片/分镜/prompt 的 @图号），禁止凭记忆翻文件夹。","出处":"templates/assets-inventory.md"},
  "sources":["templates/assets-inventory.md"],"domains":["美术"]},
 {"id":"ProcessRule:素材库命名规范","type":"ProcessRule","name":"素材库命名规范",
  "props":{"说明":"源素材 `<用途>_<类型>_<主体>_<视角或部位>_<版本>`；生成资产 `项目_镜号_内容_版本`。名字要能回答 干什么用/是什么/拍什么。","出处":"templates/assets-inventory.md / production-workflow.md"},
  "sources":["templates/assets-inventory.md","playbooks/production-workflow.md"],"domains":["工艺"]},
]

new_rels = [
 ("Concept:素材库分类两轴","Method:参考图选片法","concept-related-to"),
 ("Rule:素材文件名即条目ID","Method:参考图选片法","rule-applies-to"),
 ("Concept:素材库分类两轴","Rule:图文对位","concept-related-to"),
 ("ProcessRule:素材库命名规范","Concept:素材库分类两轴","rule-implements"),
]

have_ents = {e["id"] for e in ents}
ae = 0
for e in new_ents:
    if e["id"] in have_ents:
        continue
    ents.append(e); have_ents.add(e["id"]); ae += 1

have_rels = {(r.get("source"), r.get("target"), r.get("type")) for r in rels}
ar = 0
for s, t, ty in new_rels:
    if (s, t, ty) in have_rels:
        continue
    rels.append({"source": s, "target": t, "type": ty, "props": {}})
    have_rels.add((s, t, ty)); ar += 1

json.dump(d, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"added {ae} entities, {ar} relations to director-kg")
