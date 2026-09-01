# -*- coding: utf-8 -*-
"""口播类型库补: 第10型 直白规格型(规格宣读式) + 用户原句示例"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

P = r"F:/AI/kesheng/packs/narration-kg/kg.json"
g = json.load(open(P, encoding="utf-8-sig"))
ids = {e["id"] for e in g["entities"]}

NEW = [
    {"id": "NarrationType:直白规格型", "type": "NarrationType", "name": "直白规格型(规格宣读式)",
     "props": {"受众": "工程师/采购/专业展商", "基调": "直接·无修饰·规格即卖点(参数自带单位/条件/关键词)",
               "语速": "250-270字/分(匀速宣读感)", "公式链": "F03定义→F08参数→F08参数→F08参数→F13收口(定位句)",
               "示例": "PHO-SC-4 激光驱动等离子体宽谱光源，覆盖170–2500nm超宽带、光谱辐射亮度超75mW/(mm²·sr·nm)，功率稳定性优于±0.2%（三环控制），寿命达1万小时，自主知识产权，面向半导体量测/检测的高性能宽谱光源。",
               "禁忌": "华丽感性词/参数不带单位不带条件/无出处数据",
               "互补": "与价值翻译型(F06)是两极: 直白=读规格给工程师, 翻译=讲价值给非专业受众; 产品片可按客户偏好选极(直白/翻译/混合)"},
     "sources": ["templates/narration-formula.md", "user_custom_example"]},
    {"id": "NarrationExample:PHO-SC-4直白规格", "type": "NarrationExample", "name": "PHO-SC-4直白规格旁白",
     "props": {"原文": "PHO-SC-4 激光驱动等离子体宽谱光源，覆盖170–2500nm超宽带、光谱辐射亮度超75mW/(mm²·sr·nm)，功率稳定性优于±0.2%（三环控制），寿命达1万小时，自主知识产权，面向半导体量测/检测的高性能宽谱光源。",
               "结构": "定义句+参数句×3(单位/条件全带)+收口定位句(自主知识产权/面向…)", "来源": "用户提供范式(2026-09)"},
     "sources": ["user_custom_example"]},
]
for e in NEW:
    if e["id"] not in ids:
        g["entities"].append(e)
        ids.add(e["id"])

KEYS = {(r["source"], r["target"], r["type"]) for r in g["relations"]}
for s, t, ty in [
    ("NarrationType:直白规格型", "NarrationFormula:F03定义句", "type-adopts-formula"),
    ("NarrationType:直白规格型", "NarrationFormula:F08参数句", "type-adopts-formula"),
    ("NarrationType:直白规格型", "NarrationFormula:F13承诺句", "type-adopts-formula"),
    ("NarrationType:直白规格型", "NarrationExample:PHO-SC-4直白规格", "type-uses-sample"),
    ("NarrationType:直白规格型", "NarrationType:产品宣传片", "type-twin"),
    ("NarrationExample:PHO-SC-4直白规格", "NarrationRule:参数价值翻译律", "example-contrasts"),
]:
    if (s, t, ty) not in KEYS:
        g["relations"].append({"source": s, "target": t, "type": ty, "props": {}})
        KEYS.add((s, t, ty))

json.dump(g, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("直白规格型 added:", len(g["entities"]), "entities")
