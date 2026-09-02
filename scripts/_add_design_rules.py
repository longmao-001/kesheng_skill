# -*- coding: utf-8 -*-
"""Add MiniMax-derived design-system rules to director-kg (美术 domain), then rebuild union.
Entity-level domains:['美术'] overrides the type->domain recut, so these land in 美术."""
import io, json

P = r"F:/AI/kesheng/packs/director-kg/kg.json"
d = json.load(io.open(P, encoding="utf-8-sig"))
ents = d.setdefault("entities", [])
rels = d.setdefault("relations", [])

# --- new entities (all 美术 domain) ---
new_ents = [
 {"id":"Concept:视觉风格基线","type":"Concept","name":"视觉风格基线（Visual Baseline）",
  "props":{"说明":"一次在九宫格/分镜前把全片风格定死：内容信号→基调→色板/字体，根植内容、单强调色、反默认AI审美、克制。"},
  "sources":["templates/visual-baseline.md","MiniMax Design design.md"],"domains":["美术"]},
 {"id":"Rule:风格根植内容","type":"Rule","name":"风格根植内容",
  "props":{"说明":"每个风格决策根植于内容与目的；一个因为贴合内容而选的颜色，永远胜过因为『看起来安全』而选的颜色。","出处":"MiniMax Design design.md"},
  "sources":["templates/visual-baseline.md"],"domains":["美术"]},
 {"id":"Rule:单强调色","type":"Rule","name":"单强调色",
  "props":{"说明":"全片仅一个强调色，只出现在封面/章节/数据卡表头/高亮；与背景对比≥4.5:1；不默认用蓝。","出处":"MiniMax Design design.md"},
  "sources":["templates/visual-baseline.md"],"domains":["美术"]},
 {"id":"Rule:系统色彩≤3","type":"Rule","name":"系统色彩≤3",
  "props":{"说明":"全片系统≤3色，避免视觉噪音；强调色不上正文/字幕。","出处":"MiniMax Design design.md"},
  "sources":["templates/visual-baseline.md"],"domains":["美术"]},
 {"id":"ArtStyleRule:反默认AI审美","type":"ArtStyleRule","name":"反默认AI审美",
  "props":{"说明":"禁用：白底紫渐变/海军蓝+金/卡片圆角投影堆砌/emoji当图标/默认蓝强调。","出处":"MiniMax Design design.md"},
  "sources":["templates/visual-baseline.md"],"domains":["美术"]},
 {"id":"ArtStyleRule:克制设计","type":"ArtStyleRule","name":"克制设计",
  "props":{"说明":"一页做到没有东西可删才算完成；无卡片、圆角≤4px仅提示框、无投影。","出处":"MiniMax Design design.md"},
  "sources":["templates/visual-baseline.md"],"domains":["美术"]},
 {"id":"Taboo:白底紫渐变","type":"Taboo","name":"白底紫渐变",
  "props":{"说明":"最典型的『AI生成』默认审美，禁用。"},
  "sources":["templates/visual-baseline.md"],"domains":["美术"]},
 {"id":"Taboo:海军蓝金","type":"Taboo","name":"海军蓝+金",
  "props":{"说明":"烂大街企业风，禁用。"},
  "sources":["templates/visual-baseline.md"],"domains":["美术"]},
]

# --- relations (all within director-kg plus cross-fragment refs to 美术 concepts) ---
new_rels = [
 ("Rule:风格根植内容","Concept:视觉风格基线","rule-applies-to"),
 ("Rule:单强调色","Concept:视觉风格基线","rule-applies-to"),
 ("Rule:系统色彩≤3","Concept:视觉风格基线","rule-applies-to"),
 ("ArtStyleRule:反默认AI审美","Concept:视觉风格基线","rule-applies-to"),
 ("ArtStyleRule:克制设计","Concept:视觉风格基线","rule-applies-to"),
 ("Taboo:白底紫渐变","Concept:视觉风格基线","concept-related-to"),
 ("Taboo:海军蓝金","Concept:视觉风格基线","concept-related-to"),
 ("Concept:视觉风格基线","ViStyle:风格token块","concept-related-to"),
 ("Concept:视觉风格基线","Concept:美术设计","concept-related-to"),
 ("Concept:视觉风格基线","Concept:色彩分级","concept-related-to"),
 ("Concept:视觉风格基线","Concept:场景氛围","concept-related-to"),
]

# dedupe entity ids
have_ents = {e["id"] for e in ents}
added_e = 0
for e in new_ents:
    if e["id"] in have_ents:
        continue
    ents.append(e); have_ents.add(e["id"]); added_e += 1

have_rels = {(r.get("source"), r.get("target"), r.get("type")) for r in rels}
added_r = 0
for s, t, ty in new_rels:
    key = (s, t, ty)
    if key in have_rels:
        continue
    rels.append({"source": s, "target": t, "type": ty, "props": {}})
    have_rels.add(key); added_r += 1

json.dump(d, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"added {added_e} entities, {added_r} relations to director-kg")
print("new entities:", [e["id"] for e in new_ents])
