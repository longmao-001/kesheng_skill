# -*- coding: utf-8 -*-
"""把两支小红书工业品视频的字幕/口播词采样入库(narration-kg): NarrationExample + 2条公式规则"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

P = r"F:/AI/kesheng/packs/narration-kg/kg.json"
g = json.load(open(P, encoding="utf-8-sig"))
IDX = {e["id"]: e for e in g["entities"]}

# 2 条新公式规则
RULES = [
    {"id": "NarrationRule:层级公式句", "type": "NarrationRule", "name": "层级公式句",
     "props": {"公式": "第N重/第N级 + 动作 + 效果(一句话)", "例": "第一重过滤：拦截大颗粒杂质 / 第三重过滤：深度吸附，进一步净化水质",
               "适用": "多级/多步流程型产品(过滤/检测/反应), 一镜一句, 观众秒懂结构顺序"},
     "sources": ["https://www.xiaohongshu.com/discovery/item/6a0efb520000000007021ae9"]},
    {"id": "NarrationRule:字幕短句", "type": "NarrationRule", "name": "字幕短句",
     "props": {"规则": "信息型字幕/旁白≤14字为宜, 一句一信息, 与画面动作同拍", "反例": "一句话塞两个信息点+一条参数",
               "与构图分工": "画面演结构, 口播说'是什么效果'——旁白不抢画面(配套)"},
     "sources": ["https://www.xiaohongshu.com/discovery/item/69153230000000000d03c141", "agents/screenwriter.md"]},
]

# 真实口播/字幕例句采样
EXAMPLES = [
    {"id": "NarrationExample:麦格米特·1/3以下", "type": "NarrationExample", "name": "体积重量降至水冷激光1/3以下",
     "props": {"原文": "体积、重量均降至水冷激光的1/3以下", "结构": "对比基准卖点句(相对参照, 不报绝对重量)", "画面": "参数尺寸图+≤50KG大字"},
     "sources": ["https://www.xiaohongshu.com/discovery/item/69153230000000000d03c141"]},
    {"id": "NarrationExample:麦格米特·风冷散热", "type": "NarrationExample", "name": "独特的风冷散热结构",
     "props": {"原文": "独特的风冷散热结构", "结构": "属性点明短句(6+4字), 画面负责讲原理(气流动画)", "规矩": "不夸词, '独特'即最大形容词"},
     "sources": ["https://www.xiaohongshu.com/discovery/item/69153230000000000d03c141"]},
    {"id": "NarrationExample:麦格米特·多重保护", "type": "NarrationExample", "name": "具备多重保护报警功能",
     "props": {"原文": "具备多重保护报警功能", "结构": "安全价值句, 画面配真实面板UI(安全地锁/报警) ", "信任": "证据在画面, 不靠嘴吹"},
     "sources": ["https://www.xiaohongshu.com/discovery/item/69153230000000000d03c141"]},
    {"id": "NarrationExample:旭诚·杂质钩子", "type": "NarrationExample", "name": "看似洁净仍含微小杂质",
     "props": {"原文": "看似洁净的自来水中，仍存在微小杂质", "结构": "反常识钩子句(打破'看着干净=干净'), 开场问题引入", "画面": "自来水管第一视角穿越"},
     "sources": ["https://www.xiaohongshu.com/discovery/item/6a0efb520000000007021ae9"]},
    {"id": "NarrationExample:旭诚·增压", "type": "NarrationExample", "name": "增压系统稳定水压保障过滤效果",
     "props": {"原文": "增压系统，稳定水压，保障过滤效果", "结构": "结构+功能+结果 因果三连句", "画面": "水泵三维动画"},
     "sources": ["https://www.xiaohongshu.com/discovery/item/6a0efb520000000007021ae9"]},
    {"id": "NarrationExample:旭诚·第一重过滤", "type": "NarrationExample", "name": "第一重过滤拦截大颗粒杂质",
     "props": {"原文": "第一重过滤：拦截大颗粒杂质", "结构": "层级+动作+效果(第N重公式句)", "画面": "PP棉纤维网特写"},
     "sources": ["https://www.xiaohongshu.com/discovery/item/6a0efb520000000007021ae9"]},
    {"id": "NarrationExample:旭诚·第三重吸附", "type": "NarrationExample", "name": "第三重过滤深度吸附",
     "props": {"原文": "第三重过滤：深度吸附，进一步净化水质", "结构": "层级+动作+递进效果", "画面": "活性炭颗粒特写"},
     "sources": ["https://www.xiaohongshu.com/discovery/item/6a0efb520000000007021ae9"]},
    {"id": "NarrationExample:旭诚·第五重口感", "type": "NarrationExample", "name": "第五重过滤改善口感",
     "props": {"原文": "第五重过滤：改善口感，让水更甘甜", "结构": "层级+结果+感受词(落到体感)", "画面": "RO膜孔圆形放大镜标注"},
     "sources": ["https://www.xiaohongshu.com/discovery/item/6a0efb520000000007021ae9"]},
    {"id": "NarrationExample:旭诚·落版承诺", "type": "NarrationExample", "name": "旭诚净水守护饮用水安全",
     "props": {"原文": "旭诚净水·守护您的饮用水安全", "结构": "品牌+承诺(保护型承诺句, 不夸性能)", "画面": "厨房真实场景落版"},
     "sources": ["https://www.xiaohongshu.com/discovery/item/6a0efb520000000007021ae9"]},
]

for e in RULES + EXAMPLES:
    if e["id"] not in IDX:
        g["entities"].append(e)
        IDX[e["id"]] = e

G = g["relations"]
KEYS = {(r["source"], r["target"], r["type"]) for r in G}
RELS = [
    ("NarrationExample:麦格米特·1/3以下", "NarrationRule:参数价值翻译律", "example-shows-rule"),
    ("NarrationExample:麦格米特·1/3以下", "NarrationRule:克制信任律", "example-shows-rule"),
    ("NarrationExample:麦格米特·风冷散热", "NarrationRule:字幕短句", "example-shows-rule"),
    ("NarrationExample:麦格米特·多重保护", "NarrationRule:证据句构造", "example-shows-rule"),
    ("NarrationExample:旭诚·杂质钩子", "NarrationRule:开头钩子高科版", "example-shows-rule"),
    ("NarrationExample:旭诚·增压", "NarrationRule:参数价值翻译律", "example-shows-rule"),
    ("NarrationExample:旭诚·第一重过滤", "NarrationRule:层级公式句", "example-shows-rule"),
    ("NarrationExample:旭诚·第三重吸附", "NarrationRule:层级公式句", "example-shows-rule"),
    ("NarrationExample:旭诚·第五重口感", "NarrationRule:层级公式句", "example-shows-rule"),
    ("NarrationExample:旭诚·第五重口感", "NarrationRule:卖结果不卖功能", "example-shows-rule"),
    ("NarrationExample:旭诚·落版承诺", "NarrationRule:证据式CTA", "example-shows-rule"),
    ("NarrationRule:层级公式句", "NarrationRule:字幕短句", "rule-supports"),
    ("NarrationRule:层级公式句", "NarrationRule:旁白不抢画面", "rule-pairs"),
    ("NarrationExample:旭诚·杂质钩子", "XhsCase:AI产品动画工作流实录", "example-from-case"),
    ("NarrationExample:麦格米特·1/3以下", "XhsCase:工业产品实拍加动画结合", "example-from-case"),
]
for s, t, ty in RELS:
    if (s, t, ty) not in KEYS:
        G.append({"source": s, "target": t, "type": ty, "props": {}})

json.dump(g, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("narration-kg updated: entities", len(g["entities"]), "relations", len(g["relations"]))
