# -*- coding: utf-8 -*-
"""口播句公式体系入图谱: 14 个 NarrationFormula + 关联例句/规则"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

P = r"F:/AI/kesheng/packs/narration-kg/kg.json"
g = json.load(open(P, encoding="utf-8-sig"))
IDX = {e["id"] for e in g["entities"]}

FORMULAS = [
    ("F01钩子句", "钩子句", {"功能": "首句抓停", "模板": "反常识事实/对比真相/不可能之问, 一句戛然", "例": "看似洁净的自来水中, 仍存在微小杂质", "位置": "开头1句"}),
    ("F02痛点句", "痛点句", {"功能": "建立问题", "模板": "对象+现状缺陷/代价", "例": "检测慢了, 良率就悄悄溜走", "位置": "钩子后1-2句"}),
    ("F03定义句", "定义句", {"功能": "一句话说清是什么", "模板": "产品/概念+是+一句人话功能(术语首现即译)", "例": "套刻误差, 就是上下两层没对准", "位置": "首见产品/术语"}),
    ("F04层级句", "层级句", {"功能": "多级结构说明书", "模板": "第N重/级+动作+效果", "例": "第一重过滤: 拦截大颗粒杂质", "位置": "结构段"}),
    ("F05属性句", "属性句", {"功能": "点明独特点", "模板": "特性+受限形容词(独特/专属)+一句话特性", "例": "独特的风冷散热结构", "位置": "结构段"}),
    ("F06价值句", "价值句", {"功能": "参数→客户得到什么", "模板": "参数/特性→良率/成本/产能/保养", "例": "精度上去了, 你的良率就稳了", "位置": "价值段"}),
    ("F07对比句", "对比句", {"功能": "参照系卖点", "模板": "本产品+相对基准+超出/降低幅度", "例": "体积、重量均降至水冷激光的1/3以下", "位置": "价值段"}),
    ("F08参数句", "参数句", {"功能": "数字入耳", "模板": "数字+量级词(约/高达/仅为)+口语参照", "例": "扫描速度400mm/s", "位置": "证据段"}),
    ("F09证据句", "证据句", {"功能": "数字可信", "模板": "数据+测试条件/口径→结论", "例": "在10万小时测试下, 亮度衰减率0.1%", "位置": "证据段"}),
    ("F10因果句", "因果句", {"功能": "结构→结果", "模板": "结构/动作+于是/才+结果", "例": "增压系统, 稳定水压, 保障过滤效果", "位置": "结构段"}),
    ("F11安全句", "安全句", {"功能": "打消顾虑", "模板": "措施/机制+保障什么", "例": "具备多重保护报警功能", "位置": "信任段"}),
    ("F12场景句", "场景句", {"功能": "身临其境", "模板": "谁+在场景+做什么(第一视角/实拍)", "例": "早上8点, 检测线上的第一片晶圆", "位置": "开头/中段"}),
    ("F13承诺句", "承诺句", {"功能": "收尾落版", "模板": "品牌+保护型承诺/价值主张(不夸性能)", "例": "旭诚净水·守护您的饮用水安全", "位置": "结尾1句"}),
    ("F14CTA句", "CTA句", {"功能": "索取动作", "模板": "证据/成果+索取(报告/演示/试算)", "例": "完整实测报告, 我们整理好了", "位置": "结尾"}),
]
for fid, name, props in FORMULAS:
    eid = f"NarrationFormula:{fid}"
    if eid not in IDX:
        g["entities"].append({"id": eid, "type": "NarrationFormula", "name": name,
                              "props": props, "sources": ["templates/narration-formula.md"]})
        IDX.add(eid)

KEYS = {(r["source"], r["target"], r["type"]) for r in g["relations"]}
RELS = [
    ("NarrationExample:旭诚·杂质钩子", "NarrationFormula:F01钩子句", "example-uses-formula"),
    ("NarrationExample:麦格米特·1/3以下", "NarrationFormula:F07对比句", "example-uses-formula"),
    ("NarrationExample:麦格米特·风冷散热", "NarrationFormula:F05属性句", "example-uses-formula"),
    ("NarrationExample:麦格米特·多重保护", "NarrationFormula:F11安全句", "example-uses-formula"),
    ("NarrationExample:旭诚·增压", "NarrationFormula:F10因果句", "example-uses-formula"),
    ("NarrationExample:旭诚·第一重过滤", "NarrationFormula:F04层级句", "example-uses-formula"),
    ("NarrationExample:旭诚·第三重吸附", "NarrationFormula:F04层级句", "example-uses-formula"),
    ("NarrationExample:旭诚·第五重口感", "NarrationFormula:F04层级句", "example-uses-formula"),
    ("NarrationExample:旭诚·落版承诺", "NarrationFormula:F13承诺句", "example-uses-formula"),
    ("NarrationFormula:F01钩子句", "NarrationRule:开头钩子高科版", "formula-implements"),
    ("NarrationFormula:F03定义句", "NarrationRule:术语第一遍即译", "formula-implements"),
    ("NarrationFormula:F04层级句", "NarrationRule:层级公式句", "formula-implements"),
    ("NarrationFormula:F05属性句", "NarrationRule:克制信任律", "formula-implements"),
    ("NarrationFormula:F06价值句", "NarrationRule:参数价值翻译律", "formula-implements"),
    ("NarrationFormula:F07对比句", "NarrationRule:参数价值翻译律", "formula-implements"),
    ("NarrationFormula:F08参数句", "NarrationRule:数字口语化", "formula-implements"),
    ("NarrationFormula:F09证据句", "NarrationRule:证据句构造", "formula-implements"),
    ("NarrationFormula:F14CTA句", "NarrationRule:证据式CTA", "formula-implements"),
    ("NarrationFormula:F04层级句", "NarrationRule:字幕短句", "formula-follows"),
    ("NarrationFormula:F07对比句", "NarrationRule:克制信任律", "formula-follows"),
]
for s, t, ty in RELS:
    if (s, t, ty) not in KEYS:
        g["relations"].append({"source": s, "target": t, "type": ty, "props": {}})

json.dump(g, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("narration-kg: entities", len(g["entities"]), "relations", len(g["relations"]))
