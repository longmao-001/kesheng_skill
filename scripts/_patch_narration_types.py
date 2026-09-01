# -*- coding: utf-8 -*-
"""口播类型库: 9 个 NarrationType(基调/语速/公式组合/示例/禁忌)"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

P = r"F:/AI/kesheng/packs/narration-kg/kg.json"
g = json.load(open(P, encoding="utf-8-sig"))
ids = {e["id"] for e in g["entities"]}

TYPES = [
    ("NarrationType:产品宣传片", "产品宣传片(B2B工业品)", {"受众": "采购/工程师/决策者", "基调": "冷峻克制·证据信任", "语速": "240-260字/分", "公式链": "F01→F02→F04/F10→F06/F07→F08/F09→F13/F14", "示例": "它把一根头发丝的十分之一看得清清楚楚。检测线快了，良率就稳了。在10万小时测试下，亮度衰减只有0.1%。那份实测报告，我们替你整理好了。", "禁忌": "炫技词/卡通化/BGM压旁白"}, ),
    ("NarrationType:品牌形象片", "品牌形象片(企业/机构)", {"受众": "公众/客户/政府", "基调": "宏大·排比·留白", "语速": "200-220字/分", "公式链": "F12→F05→F05→F13", "示例": "我们见过凌晨的洁净间，也见过纳米尺度的光。二十年，只做一件事：把看得见的精度，交到看不见的信任里。", "禁忌": "硬参数堆砌/口号空转无画面"}, ),
    ("NarrationType:项目申报成果展示", "项目申报/成果展示", {"受众": "评审专家/主管部门", "基调": "官方大气·权威带口径", "语速": "230-250字/分", "公式链": "F02→F03→F08→F09→F13", "示例": "该项目突破了自主可控的关键技术，实现了国产替代。经权威检测，重复精度达到微米级，居国际先进水平。成果已应用于产线，为良率提升提供关键支撑。", "禁忌": "世界级/领先/填补空白等无依据词·无出处数据"}, ),
    ("NarrationType:科普视频", "科普视频(公众)", {"受众": "大众/学生", "基调": "口语·钩子·类比", "语速": "260-280字/分", "公式链": "F01→F03(类比)→F10→F12", "示例": "你看得见的每一滴水，都藏着看不见的战场。PP棉像一张网，把大颗粒挡在外面；活性炭就像海绵，把异味牢牢锁住。", "禁忌": "术语连击/宣传腔/钩子与内容脱节"}, ),
    ("NarrationType:招生宣传", "招生宣传(高校/院所)", {"受众": "学生/家长", "基调": "温暖理想·人·场景", "语速": "210-230字/分", "公式链": "F12→F05→F05→F13", "示例": "在这里，研一就能摸到真实的晶圆。导师说，科研不是刷论文，是把不可能变成能。你的人生第一块芯片，也许就刻在这间实验室。", "禁忌": "就业/待遇承诺·夸张升学率"}, ),
    ("NarrationType:融资路演", "融资路演(BP视频)", {"受众": "投资人", "基调": "问题+市场+模式·快", "语速": "280-300字/分", "公式链": "F01→F02→F08→F05→F14", "示例": "检测一台设备要等三个月？我们把它压缩到三天。在这个百亿级的市场里，卡住所有人的是'看不见的良率'。我们让每一片晶圆，都开口说话。", "禁忌": "夸大市场规模/未披露信息/技术参数注水"}, ),
    ("NarrationType:科普短视频", "科普短视频(小红书/抖音竖版)", {"受众": "泛人群", "基调": "3秒钩子·快·弹幕感", "语速": "280-300字/分", "公式链": "F01/F07→F03→F10→F14(收藏/评论)", "示例": "矿泉水瓶里藏着一座'垃圾场'？第一层滤芯，先拦住它们。点个收藏，下一条讲RO膜为什么最贵。", "禁忌": "标题党(钩子与正文脱节)/前3秒无信息量"}, ),
    ("NarrationType:大科学装置设施", "大科学装置/设施", {"受众": "公众/决策者", "基调": "敬畏·尺度·数字诗化", "语速": "190-210字/分(慢)", "公式链": "F01→F08(诗化)→F10→F13", "示例": "在这里，光走一公里，只为看清一皮米的距离。它不算出答案，它先提出问题。这就是它存在的意义。", "禁忌": "轻快配乐/节奏急促破坏庄重感"}, ),
    ("NarrationType:科研机构介绍", "科研机构/团队介绍", {"受众": "合作方/客户/招聘", "基调": "沉稳专业·人与方向并重", "语速": "235-255字/分", "公式链": "F02→F03→F05→F08→F13", "示例": "我们研究的是让检测变快的方法。三十人的团队，一半做光学，一半做算法。他们做出来的每一台设备，都在产线上替你盯住良率。", "禁忌": "过度煽情/空喊口号/人员信息失真"}, ),
]
for eid, name, props in TYPES:
    if eid not in ids:
        g["entities"].append({"id": eid, "type": "NarrationType", "name": name,
                              "props": props, "sources": ["templates/narration-formula.md", "http://hi-banma.com/1263.html", "https://cloud.kepuchina.cn/h5/detail?id=7386091920020881408"]})
        ids.add(eid)

KEYS = {(r["source"], r["target"], r["type"]) for r in g["relations"]}
MAP = {
    "NarrationType:产品宣传片": ["NarrationFormula:F01钩子句", "NarrationFormula:F06价值句", "NarrationFormula:F07对比句", "NarrationFormula:F09证据句"],
    "NarrationType:品牌形象片": ["NarrationFormula:F05属性句", "NarrationFormula:F12场景句", "NarrationFormula:F13承诺句"],
    "NarrationType:项目申报成果展示": ["NarrationFormula:F08参数句", "NarrationFormula:F09证据句", "NarrationFormula:F03定义句"],
    "NarrationType:科普视频": ["NarrationFormula:F01钩子句", "NarrationFormula:F03定义句", "NarrationFormula:F10因果句"],
    "NarrationType:招生宣传": ["NarrationFormula:F12场景句", "NarrationFormula:F05属性句", "NarrationFormula:F13承诺句"],
    "NarrationType:融资路演": ["NarrationFormula:F01钩子句", "NarrationFormula:F02痛点句", "NarrationFormula:F14CTA句"],
    "NarrationType:科普短视频": ["NarrationFormula:F01钩子句", "NarrationFormula:F03定义句", "NarrationFormula:F14CTA句"],
    "NarrationType:大科学装置设施": ["NarrationFormula:F01钩子句", "NarrationFormula:F08参数句", "NarrationFormula:F13承诺句"],
    "NarrationType:科研机构介绍": ["NarrationFormula:F03定义句", "NarrationFormula:F05属性句", "NarrationFormula:F08参数句"],
}
for tid, flist in MAP.items():
    for f in flist:
        if (tid, f, "type-adopts-formula") not in KEYS:
            g["relations"].append({"source": tid, "target": f, "type": "type-adopts-formula", "props": {}})
        KEYS.add((tid, f, "type-adopts-formula"))

# 与目标案例连线
for s, t, ty in [
    ("NarrationType:产品宣传片", "NarrationExample:麦格米特·1/3以下", "type-uses-sample"),
    ("NarrationType:科普视频", "NarrationExample:旭诚·杂质钩子", "type-uses-sample"),
]:
    if (s, t, ty) not in KEYS:
        g["relations"].append({"source": s, "target": t, "type": ty, "props": {}})
        KEYS.add((s, t, ty))

json.dump(g, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("narration types added:", len(g["entities"]), "entities /", len(g["relations"]), "relations")
