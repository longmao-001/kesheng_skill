# -*- coding: utf-8 -*-
"""直白规格型: 更换标准示例 + 新增两个不同主体示例(检测系统/净水机)"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

P = r"F:/AI/kesheng/packs/narration-kg/kg.json"
g = json.load(open(P, encoding="utf-8-sig"))
ids = {e["id"] for e in g["entities"]}
SRC = ["templates/narration-formula.md", "http://www.tianzhuniu.com/172.html", "https://m.instrument.com.cn/zhuti/44755/news.html"]

NEW = [
    {"id": "NarrationExample:检测系统直白规格", "type": "NarrationExample", "name": "X-2000检测系统直白版",
     "props": {"原文": "X-2000 明场缺陷检测系统。分辨率 0.3μm，产能 800 片/小时，检出灵敏度 99.5%（以 90nm 线宽测试图形为基准），重复性优于 1%。适配 28nm 及以上节点，已交付国内 12 英寸产线。",
               "结构": "定义句+参数×4(单位/条件全带)+应用归属(适配/已交付)", "来源": "范式改编(参数为占位, 待项目实测替换)"},
     "sources": SRC},
    {"id": "NarrationExample:净水机直白规格", "type": "NarrationExample", "name": "净水机直白版",
     "props": {"原文": "旭诚净水机。五级过滤：PP棉、UDF、CTO、RO膜、后置矿化。RO膜孔径 0.0001 微米，额定净水量 4000L，产水率 65%，一级水效。家用即饮，出水直喝。",
               "结构": "定义+级数罗列+核心参数×3+水效等级+应用句", "来源": "按旭诚案例改编(参数为占位, 待核实)"},
     "sources": ["https://www.xiaohongshu.com/discovery/item/6a0efb520000000007021ae9", "templates/narration-formula.md"]},
]
for e in NEW:
    if e["id"] not in ids:
        g["entities"].append(e)
        ids.add(e["id"])

# 标准示例换成 检测系统直白版(科生主流产品语境)
for e in g["entities"]:
    if e["id"] == "NarrationType:直白规格型":
        e["props"]["示例"] = "X-2000 明场缺陷检测系统。分辨率 0.3μm，产能 800 片/小时，检出灵敏度 99.5%（以 90nm 线宽测试图形为基准），重复性优于 1%。适配 28nm 及以上节点，已交付国内 12 英寸产线。"

KEYS = {(r["source"], r["target"], r["type"]) for r in g["relations"]}
for s, t, ty in [
    ("NarrationType:直白规格型", "NarrationExample:检测系统直白规格", "type-uses-sample"),
    ("NarrationType:直白规格型", "NarrationExample:净水机直白规格", "type-uses-sample"),
    ("NarrationExample:净水机直白规格", "NarrationDirectPattern:分组宣读", "sample-shows-pattern"),
    ("NarrationExample:检测系统直白规格", "NarrationDirectPattern:纯参数宣读", "sample-shows-pattern"),
]:
    if (s, t, ty) not in KEYS:
        g["relations"].append({"source": s, "target": t, "type": ty, "props": {}})
        KEYS.add((s, t, ty))

json.dump(g, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("新示例 added:", len(g["entities"]), "entities")
