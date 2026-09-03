# -*- coding: utf-8 -*-
"""Add 素材智能入库 knowledge (多模态拆解+反推prompt+质量分) to director-kg, wire, rebuild."""
import io, json
P = r"F:/AI/kesheng/packs/director-kg/kg.json"
d = json.load(io.open(P, encoding="utf-8-sig"))
ents = d.setdefault("entities", []); rels = d.setdefault("relations", [])
DOM = ["美术", "影像"]
new_ents = [
 {"id":"Concept:素材反推提示词","type":"Concept","name":"素材图反推提示词(AI合成)",
  "props":{"说明":"每张素材用 read_image 看真图后反推一段『用 AI 再生出这张图』的 prompt（主体+构图+光线+风格+细节+负面）；是文字检索键，也直接复用为生成稿。","出处":"templates/assets-inventory.md §〇"},
  "sources":["templates/assets-inventory.md","scripts/annotate_assets.py"],"domains":DOM},
 {"id":"Concept:素材质量分","type":"Concept","name":"素材质量分(★1-5)",
  "props":{"说明":"每张素材入库即打分（清晰0.25/主体完整0.25/构图0.15/光影0.15/用途匹配0.20 加权→0-1→★；合规=一票否决/禁）；选图/做图按 高分优先，★≥4 优先、★<3 除非无替代。","出处":"templates/assets-inventory.md §三"},
  "sources":["templates/assets-inventory.md"],"domains":DOM},
 {"id":"ProcessRule:素材多模态拆解入库","type":"ProcessRule","name":"素材智能入库(拆解+反推prompt+打分)",
  "props":{"说明":"每张素材入库做三件套：①多模态拆解标签(物品/任务/场景/结构/质感/数据/品牌/实拍) ②AI合成反推prompt ③质量分；选图/做图时按 内容标签/反推prompt 文字匹配对位需求 + 高分优先，快。","出处":"templates/assets-inventory.md §〇"},
  "sources":["templates/assets-inventory.md","scripts/annotate_assets.py"],"domains":["工艺"]},
]
have = {e["id"] for e in ents}
ae=0
for e in new_ents:
    if e["id"] not in have: ents.append(e); have.add(e["id"]); ae+=1
new_rels = [
 ("Concept:素材反推提示词","Method:参考图选片法","concept-related-to"),
 ("Concept:素材质量分","Method:参考图选片法","concept-related-to"),
 ("Concept:素材质量分","Rule:五层检查体系","concept-related-to"),
 ("Concept:素材反推提示词","Rule:图文对位","concept-related-to"),
 ("ProcessRule:素材多模态拆解入库","Concept:素材质量分","concept-related-to"),
 ("ProcessRule:素材多模态拆解入库","Concept:素材反推提示词","concept-related-to"),
]
have2 = {(r.get("source"),r.get("target"),r.get("type")) for r in rels}
ar=0
for s,t,ty in new_rels:
    if (s,t,ty) not in have2: rels.append({"source":s,"target":t,"type":ty,"props":{}}); ar+=1
json.dump(d, io.open(P,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"added {ae} ents, {ar} rels")
