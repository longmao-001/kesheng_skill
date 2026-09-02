# -*- coding: utf-8 -*-
"""Add reference-image selection method/rules to director-kg (影像+美术 domain),
then rebuild union. Grounds the '选对参考图' gap in the existing 图文对位/参考包组装 knowledge."""
import io, json

P = r"F:/AI/kesheng/packs/director-kg/kg.json"
d = json.load(io.open(P, encoding="utf-8-sig"))
ents = d.setdefault("entities", [])
rels = d.setdefault("relations", [])

DOM = ["影像", "美术"]
new_ents = [
 {"id":"Method:参考图选片法","type":"Method","name":"参考图选片法（对位需求→8维打分→角色+部位对应+位置）",
  "props":{"说明":"每镜先列对位需求(主体/动作状态/机位角度/必看清部件/材质/场景)，再从素材库候选按8维打分(对位度/清晰/角度/光影/占位/合规/唯一/可溯源)挑≤3张，标角色+部位对应+位置+依据口播哪句；一票否决:主体不中口播/无授权/水印竞品模糊。","出处":"templates/reference-selection.md"},
  "sources":["templates/reference-selection.md"],"domains":DOM},
 {"id":"Rule:参考图按对位需求选片","type":"Rule","name":"参考图按对位需求选片",
  "props":{"说明":"参考图必须按该镜对位需求选出——先定'这镜参考图要提供什么'再在候选里挑，不是随手拿好看的。","出处":"templates/reference-selection.md"},
  "sources":["templates/reference-selection.md"],"domains":DOM},
 {"id":"Rule:参考图锚图优先","type":"Rule","name":"参考图锚图优先",
  "props":{"说明":"主体一致性优先复用三视图/角色锚图(跨镜)，辅助参考(机位/场景/质感)才新挑，别每镜重挑一张主体图。","出处":"playbooks/consistency.md / templates/reference-selection.md"},
  "sources":["playbooks/consistency.md","templates/reference-selection.md"],"domains":DOM},
 {"id":"Rule:参考图角色部位位置必写","type":"Rule","name":"参考图角色+部位对应+位置必写",
  "props":{"说明":"每张参考图标角色(主体/部件参考/场景参考/质感参考)+部位对应(参考图<部位X>＝主体<部位X'>)+放哪位置；场景参考含主体须注明 图中<位置>的主体＝主体。","出处":"templates/product-prompt-formula.md / reference-selection.md"},
  "sources":["templates/product-prompt-formula.md","templates/reference-selection.md"],"domains":DOM},
 {"id":"Rule:参考图合规过滤","type":"Rule","name":"参考图合规过滤",
  "props":{"说明":"水印/竞品/团队合影/商标原理图/未授权/模糊到看不清部件=一票否决，不作参考喂模型。","出处":"templates/reference-selection.md"},
  "sources":["templates/reference-selection.md"],"domains":DOM},
]

new_rels = [
 ("Rule:参考图按对位需求选片","Method:参考图选片法","rule-applies-to"),
 ("Rule:参考图锚图优先","Method:参考图选片法","rule-applies-to"),
 ("Rule:参考图角色部位位置必写","Method:参考图选片法","rule-applies-to"),
 ("Rule:参考图合规过滤","Method:参考图选片法","rule-applies-to"),
 ("Method:参考图选片法","Rule:图文对位","concept-related-to"),
 ("Method:参考图选片法","ProcessRule:参考包组装","concept-related-to"),
 ("Rule:参考图按对位需求选片","Rule:图文对位","rule-implements"),
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
print("new:", [e["id"] for e in new_ents])
