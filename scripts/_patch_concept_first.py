# -*- coding: utf-8 -*-
"""KSP-04 概念先行改造: KspStep 更新 + 概念先行规则 + KSP-04 依赖修正"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# sop-seed: 更新 KSP-04 + 加规则
P = r"F:/AI/kesheng/packs/sop-seed/kg.json"
g = json.load(open(P, encoding="utf-8-sig"))
for e in g["entities"]:
    if e["id"] == "KspStep:KSP-04方案对抗":
        e["id"] = "KspStep:KSP-04创意概念"
        e["name"] = "KSP-04 创意概念先行"
        e["props"] = {"动作": "Ideation概念生成(导演/编剧/摄影各1-2个概念: 大创意+基调+为什么成立)→Evaluation评分(预注册/传播力/科学/可执行+红队挑战)→Presentation概念拍板#9→Refine只深化所选概念→九宫格(04.5)",
                      "用户角色": "概念拍板(选一/融合)", "门控": "概念拍板通过+深化方案获批",
                      "产出": "概念卡×3-4+评分表/深化方案m3-proposal.md", "规范": "docs/USER_SOP.md §KSP-04"}
if "Rule:概念先行" not in {e["id"] for e in g["entities"]}:
    g["entities"].append({
        "id": "Rule:概念先行", "type": "Rule", "name": "概念先行(agency流程)",
        "props": {"流程": "Insight(洞察,=重点协议)→Ideation(概念生成: SIT/SCAMPER/TRIZ/Bisociation等)→Evaluation(戛纳式评分+红队挑战)→Presentation(客户选概念)→Refine(只深化选中概念)",
                  "纠正": "禁止'多角色盲出完整方案再评审'——方案互相打架且执行细节前置; 概念层面先竞标, 选中才深化",
                  "参考": "creative-director-skill (smixs): 20+ ideation methodologies, Cannes-calibrated scoring, brief→deck"},
        "sources": ["https://www.freemcplab.com/i18n/zh-CN/play/creative-director-skill/", "https://github.com/timkoda/koda-stack"]})
KEYS = {(r["source"], r["target"], r["type"]) for r in g["relations"]}
for s, t, ty in [
    ("Rule:概念先行", "KspStep:KSP-04创意概念", "rule-governs"),
    ("KspStep:KSP-03.5主题共识", "KspStep:KSP-04创意概念", "ksp-feeds"),
]:
    if (s, t, ty) not in KEYS:
        g["relations"].append({"source": s, "target": t, "type": ty, "props": {}})
        KEYS.add((s, t, ty))
json.dump(g, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("sop-seed KSP-04 updated")
