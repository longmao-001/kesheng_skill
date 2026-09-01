# -*- coding: utf-8 -*-
"""更新 xhs-cases-kg: 视频逐帧审阅结果 + 新增视觉手法模式实体"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

P = r"F:/AI/kesheng/packs/xhs-cases-kg/kg.json"
g = json.load(open(P, encoding="utf-8-sig"))

UPD = {
    "XhsCase:工业产品实拍加动画结合": (
        "视频实测(74.8s 麦格米特LUX-1200激光焊机): 参数尺寸图(630/550/335mm+≤50KG+"
        "「体积重量降至水冷激光1/3以下」)→风冷散热内部原理动画(蓝气流进/橙热流出)→"
        "真实面板UI特写(板厚1.0mm/扫描速度400mm/s/峰值800W/安全地锁)→"
        "三分屏实测(碳钢/不锈钢/铝合金2mm同台火花)→品牌落版",
    ),
    "XhsCase:AI产品动画工作流实录": (
        "视频实测(15.5s 旭诚净水机): 钩子「看似洁净的自来水中仍含微小杂质」→增压系统→"
        "第一重过滤拦截大颗粒(PP棉)→第三重深度吸附(活性炭)→第五重改善口感(RO膜孔圆形放大镜标注)→"
        "厨房真实场景落版「旭诚净水·守护饮用水安全」; 逐级字幕「第N重过滤」+圆形画中画+约1.5s/镜快节奏",
    ),
}
for e in g["entities"]:
    if e["id"] in UPD:
        e["props"]["视频实测"] = UPD[e["id"]][0]

NEW = [
    {"id": "VideoPattern:层级字幕", "type": "VideoPattern", "name": "层级字幕标注",
     "props": {"用法": "第N重过滤/第N级/第N步句式的屏幕字幕, 一镜一个层级, 观众秒懂结构顺序",
               "来源": "旭诚净水机动画(第一/第三/第五重过滤)", "适用": "流程/级数/步骤型 内部结构动画"},
     "sources": ["https://www.xiaohongshu.com/discovery/item/6a0efb520000000007021ae9"], "domains": ["叙事"]},
    {"id": "VideoPattern:圆形放大镜标注", "type": "VideoPattern", "name": "圆形放大镜画中画",
     "props": {"用法": "圆形镜头放大关键局部(膜孔/结构/接缝), 与全景同框, 细节不靠嘴说",
               "来源": "旭诚净水机动画(RO膜孔放大)", "适用": "材料/表面/结构细节展示"},
     "sources": ["https://www.xiaohongshu.com/discovery/item/6a0efb520000000007021ae9"], "domains": ["叙事", "分镜"]},
    {"id": "VideoPattern:三分屏实测对比", "type": "VideoPattern", "name": "三分屏实测对比",
     "props": {"用法": "同机位三路同台实测(碳钢/不锈钢/铝合金2mm), 火花同帧, 信任度最高的一镜",
               "来源": "麦格米特激光焊机宣传片", "适用": "多材料/多工况性能展示"},
     "sources": ["https://www.xiaohongshu.com/discovery/item/69153230000000000d03c141"], "domains": ["叙事"]},
    {"id": "VideoPattern:参数尺寸图", "type": "VideoPattern", "name": "参数尺寸图+卖点大字",
     "props": {"用法": "产品三视图+尺寸标注+一句对比卖点大字(体积重量降至1/3以下), 数据字卡入画面",
               "来源": "麦格米特激光焊机宣传片", "适用": "工业品参数交代与卖点对比"},
     "sources": ["https://www.xiaohongshu.com/discovery/item/69153230000000000d03c141"], "domains": ["叙事", "分镜"]},
]
NEW_IDS = {e["id"] for e in g["entities"]}
for e in NEW:
    if e["id"] not in NEW_IDS:
        g["entities"].append(e)

g["relations"] += [
    {"source": "VideoPattern:三分屏实测对比", "target": "RednotePattern:对比实测型", "type": "pattern-implements", "props": {}},
    {"source": "VideoPattern:参数尺寸图", "target": "RednotePattern:痛点参数型", "type": "pattern-implements", "props": {}},
    {"source": "VideoPattern:圆形放大镜标注", "target": "VisualMetaphor:微观穿越", "type": "pattern-supports", "props": {}},
    {"source": "XhsCase:AI产品动画工作流实录", "target": "VideoPattern:层级字幕", "type": "case-uses", "props": {}},
    {"source": "XhsCase:AI产品动画工作流实录", "target": "VideoPattern:圆形放大镜标注", "type": "case-uses", "props": {}},
    {"source": "XhsCase:工业产品实拍加动画结合", "target": "VideoPattern:三分屏实测对比", "type": "case-uses", "props": {}},
    {"source": "XhsCase:工业产品实拍加动画结合", "target": "VideoPattern:参数尺寸图", "type": "case-uses", "props": {}},
]

json.dump(g, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("xhs-cases updated: entities", len(g["entities"]), "relations", len(g["relations"]))
