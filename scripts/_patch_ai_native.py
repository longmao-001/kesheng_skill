# -*- coding: utf-8 -*-
"""更新 AI原生交付原则: 交付物=多平台上手包, 用户=多平台画布自玩"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

P = r"F:/AI/kesheng/packs/sop-seed/kg.json"
g = json.load(open(P, encoding="utf-8-sig"))
for e in g["entities"]:
    if e["id"] == "Rule:AI原生交付原则":
        e["props"] = {
            "用户定位": "只冲着AI视频生成来; 主玩法=自己在多个平台(画布/节点: LibTV/即梦/可灵/Seedance)操作生成, 默认无专业后期能力",
            "铁则": "核心交付物=多平台上手素材包: 每镜【平台对照prompt(Seedance2.5/即梦/可灵/LibTV各一份)+参考图包+口播+抽卡建议+画布操作步骤】, 用户拿着任选平台开玩",
            "后期边界": "剪映10分钟一键是可选加分项; 专业后期(剪辑/调色LUT/曲线动画重绘/LUFS混音/排版压字)=可选增强, 绝不是交付前提",
            "交付两档": "A档多平台上手包(默认) / 附送剪映傻瓜执行单(可选) / B档专业交接单(用户主动要求才给)",
        }
json.dump(g, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("AI原生交付原则 updated")
