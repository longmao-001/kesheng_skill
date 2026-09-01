# -*- coding: utf-8 -*-
"""用户原话(25条) → 失败图书馆增补 + 补3条新规则(口播首句产品名/图文顺序对位/零门槛措辞)"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 1) 失败图书馆追加用户原话证据段
LIB = r"F:/AI/kesheng/runs/_lessons/FAILURE-LIBRARY.md"
ADD = """

## 📣 用户原话证据（session-774f5b97，2026-08 玦芯 PHO-SC-4 对话，25 条）

| 原话(节选) | 教训 | 已固化 |
|---|---|---|
| "你怎就这么爱这句话呢？这句话就不像人能讲出来的" | 口播必须像人话，不写"文案腔" | 直白规格型+价值翻译双极；口播句公式 F01-F14 |
| "等一下，我的口播第一句话应该是产品名啊" | **口播第一句=产品全名** | 本次补 Rule:口播首句产品名 |
| "素材包预览里的分镜预览里面也要同步更改，其他的也是啊" | 改一处必须全局同步 | F-05 残留一致性 + check_residual.py |
| "帮我打开…我不确定他改了没" | 用户要眼见为实 | 证据先行(拍板前展示文件) |
| "logo 你自己网上下载" | 素材团队自己搜好 | 图料三件套+零意外自包含 |
| "字幕好像和口播稿不同步啊" / "你懂字幕和口播稿之间的关系吗" / "完全没按着我说" | 字幕=口播逐句同步 | 规则#12 字幕=口播逐句 |
| "稳了不白测是哪儿来的？口播稿里可没有…总想加一些错误的口语化" | **零自创文案** | 规则#13 文案白名单 |
| "这居然还得我教你，给我固定到 skill 里面" | 教训必须固化 | 失败图书馆 KSP-07 闭环 |
| "你看分镜合理吗？第一句话是第八镜才说？" | **口播首句必须在首镜说** | 本次补 Rule:图文顺序对位 |
| "9-13 镜无口播…删掉就行" | 冗余段可选/默认最小结构 | 口播多方案+直白型默认最简 |
| "人工层是什么？我说我有能力做人工层？" | **禁专业术语吓用户** | 本次补 Rule:零门槛措辞 |
| "参考图你从素材包直接推荐就好，为什么还需要我再去找" | 参考图直接给到 | 零意外+图文对位+素材速查表 |
| "你要用参考图也得跟口播内容对得上啊！！" | 图文对位 | Rule:图文对位(R12+检察官硬查) |

"""
with open(LIB, "a", encoding="utf-8") as f:
    f.write(ADD)

# 2) 补 3 条规则进图谱
P = r"F:/AI/kesheng/packs/sop-seed/kg.json"
g = json.load(open(P, encoding="utf-8-sig"))
ids = {e["id"] for e in g["entities"]}
NEW = [
    {"id": "Rule:口播首句产品名", "type": "Rule", "name": "口播首句=产品全名",
     "props": {"铁则": "口播第一句话必须是产品全名(如'PHO-SC-4 激光驱动等离子体宽谱光源：…'), 不得用意象句/文案腔开场", "来源": "用户原话: '等一下 我的口播第一句话应该是产品名啊'"},
     "sources": ["runs/_lessons/FAILURE-LIBRARY.md"], "domains": ["叙事"]},
    {"id": "Rule:图文顺序对位", "type": "Rule", "name": "图文顺序对位",
     "props": {"铁则": "口播首句必须在首镜(镜1)出现; 口播节拍顺序与分镜顺序一一对应, 不得第1句跑到第8镜", "来源": "用户原话: '你看分镜合理吗？第一句话是第八镜才说？'"},
     "sources": ["runs/_lessons/FAILURE-LIBRARY.md"], "domains": ["工艺"]},
    {"id": "Rule:零门槛措辞", "type": "Rule", "name": "零门槛措辞",
     "props": {"铁则": "交付文档/对话禁用专业术语吓用户: '人工层/图表层/首帧/后期/LUT/压字' 一律替换为零门槛表述('模板/样张直接拖进剪映/一键/照着点')", "来源": "用户原话: '人工层是什么？我说我有能力做人工层？'"},
     "sources": ["runs/_lessons/FAILURE-LIBRARY.md"], "domains": ["工艺"]},
]
for e in NEW:
    if e["id"] not in ids:
        g["entities"].append(e)
        ids.add(e["id"])
KEYS = {(r["source"], r["target"], r["type"]) for r in g["relations"]}
for s, t, ty in [
    ("Rule:口播首句产品名", "KspStep:KSP-05分镜执行", "rule-governs"),
    ("Rule:图文顺序对位", "Rule:图文对位", "rule-reinforces"),
    ("Rule:零门槛措辞", "Rule:AI原生交付原则", "rule-serves"),
]:
    if (s, t, ty) not in KEYS:
        g["relations"].append({"source": s, "target": t, "type": ty, "props": {}})
        KEYS.add((s, t, ty))
json.dump(g, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("失败图书馆增补 + 3 规则入库 done")
