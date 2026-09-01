# -*- coding: utf-8 -*-
"""直白规格型子体系: 5宣读范式 + 6纪律 + 4示例"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

P = r"F:/AI/kesheng/packs/narration-kg/kg.json"
g = json.load(open(P, encoding="utf-8-sig"))
ids = {e["id"] for e in g["entities"]}
SRC = ["templates/narration-formula.md", "http://www.tianzhuniu.com/172.html", "https://m.instrument.com.cn/zhuti/44755/news.html"]

NEW = [
    {"id": "NarrationDirectPattern:纯参数宣读", "type": "NarrationDirectPattern", "name": "纯参数宣读",
     "props": {"结构": "定义句→参数句×N(单位/条件/±全带)→收口定位句", "例": "PHO-SC-4…覆盖170-2500nm…辐射亮度超75…稳定性优于±0.2%…寿命1万小时…自主知识产权，面向…",
               "适用": "官网/展板视频/选型资料配套", "注意": "指标≤6个, 超了交给图表层"},
     "sources": SRC},
    {"id": "NarrationDirectPattern:参数加应用一句", "type": "NarrationDirectPattern", "name": "参数+应用一句",
     "props": {"结构": "规格连发后补一句'用来做什么'", "例": "…寿命达1万小时。它用在半导体检测线上，替你看住每一片晶圆。",
               "适用": "半专业观众/行业媒体", "注意": "应用句只说场景, 不夸大能力"},
     "sources": SRC},
    {"id": "NarrationDirectPattern:参数加对比基准", "type": "NarrationDirectPattern", "name": "参数+对比基准",
     "props": {"结构": "每个指标给参照系(同类水平/上一代/行业标准)", "例": "…辐射亮度超75mW/(mm²·sr·nm)，约为传统氙灯的3倍。",
               "适用": "选型工程师", "注意": "对比基准必须真实可核, 无据不写"},
     "sources": SRC},
    {"id": "NarrationDirectPattern:分组宣读", "type": "NarrationDirectPattern", "name": "分组宣读(归类式)",
     "props": {"结构": "按维度分组: 光谱性能→输出亮度→稳定性→寿命→产权→应用, 每维度1-2句", "例": "光谱上：覆盖170-2500nm超宽带。亮度上：辐射亮度超75…。稳定性上：优于±0.2%（三环控制）。",
               "适用": "3分钟以上/申报配套", "注意": "维度顺序按客户最关心排序, 可调"},
     "sources": SRC},
    {"id": "NarrationDirectPattern:展会口播", "type": "NarrationDirectPattern", "name": "展会口播(短句分点)",
     "props": {"结构": "短句分点(5-8字一句), 像现场介绍", "例": "PHO-SC-4。宽谱光源。170到2500纳米。亮度高。寿命一万小时。国产，自主产权。",
               "适用": "展会/现场/抖音竖版工业账号", "注意": "段落间留停顿, 语速略放"},
     "sources": SRC},
    {"id": "DirectRule:参数纪律", "type": "DirectRule", "name": "参数纪律", "props": {"规则": "每个参数必须带单位/量纲; 幅度类带±/优于/达到; 条件类带(三环控制/测试条件); 指标≤6个, 超了交给图表层", "红线": "无出处数字说出口=科学错误"}, "sources": SRC},
    {"id": "DirectRule:排序纪律", "type": "DirectRule", "name": "排序纪律", "props": {"规则": "指标排序按客户最关心: 通常 波段范围→亮度→稳定性→寿命→产权→应用; 客户口径不同可调(采购看寿命价格, 工程师看精度)"}, "sources": SRC},
    {"id": "DirectRule:收口纪律", "type": "DirectRule", "name": "收口纪律", "props": {"规则": "结尾必须有一句'归属句': 面向…/应用于…/自主知识产权/国产替代——三选一或组合, 不给纯参数无归属"}, "sources": SRC},
    {"id": "DirectRule:禁修辞", "type": "DirectRule", "name": "禁修辞", "props": {"规则": "直白型禁: 比喻/排比反问/感叹号/感性形容词(极致/完美/颠覆); 数字中性陈述(用'达/超/优于'而非'高达/仅'的夸张量级)"}, "sources": SRC},
    {"id": "DirectRule:宣读语速", "type": "DirectRule", "name": "宣读语速", "props": {"规则": "250-270字/分均匀宣读; 数字与单位之间略停(±0.2%这一口型要稳); 关键词(自主知识产权)加重音"}, "sources": SRC},
    {"id": "DirectRule:混合极规则", "type": "DirectRule", "name": "混合极规则", "props": {"规则": "双受众时: 先直白宣读规格(给工程师) → 再一句价值翻译(给决策者) → 收口归属句; 拒绝长比喻与情绪堆叠"}, "sources": SRC},
    {"id": "NarrationExample:PHO-SC-4分组宣读", "type": "NarrationExample", "name": "PHO-SC-4分组宣读版",
     "props": {"原文": "光谱上：覆盖170-2500nm超宽带。亮度上：光谱辐射亮度超75mW/(mm²·sr·nm)。稳定性上：功率漂移优于±0.2%（三环控制）。寿命上：一万小时。产权上：自主知识产权。它用在半导体检测线上。",
               "结构": "分组宣读", "来源": "范式改编"}, "sources": SRC},
    {"id": "NarrationExample:PHO-SC-4对比基准", "type": "NarrationExample", "name": "PHO-SC-4对比基准版",
     "props": {"原文": "PHO-SC-4：170-2500nm 超宽带，辐射亮度超75mW/(mm²·sr·nm)，约为传统氙灯的3倍；功率优于±0.2%，寿命一万小时。自主知识产权，面向半导体量测检测。",
               "结构": "参数+对比基准", "来源": "范式改编(对比数据标注待核实)"}, "sources": SRC},
    {"id": "NarrationExample:PHO-SC-4展会口播", "type": "NarrationExample", "name": "PHO-SC-4展会口播版",
     "props": {"原文": "PHO-SC-4。宽谱光源。170到2500纳米。亮度高。一万小时寿命。国产。自主产权。",
               "结构": "展会口播短句分点", "来源": "范式改编"}, "sources": SRC},
    {"id": "NarrationExample:仪器直白规格体", "type": "NarrationExample", "name": "分光光度计式直白规格",
     "props": {"原文": "双光束紫外可见分光光度计。波长范围190-1100nm，光谱带宽1nm，吸光度准确度±0.005A。以'新时代的标准'为开发理念，面向科研与QC实验室。",
               "结构": "参数+理念句+应用归属", "来源": "按仪器行业惯例改编(参考分光光度计文案, 参数为占位示例)"}, "sources": SRC},
]
for e in NEW:
    if e["id"] not in ids:
        g["entities"].append(e)
        ids.add(e["id"])

KEYS = {(r["source"], r["target"], r["type"]) for r in g["relations"]}
for s, t, ty in [
    ("NarrationType:直白规格型", "NarrationDirectPattern:纯参数宣读", "type-uses-pattern"),
    ("NarrationType:直白规格型", "NarrationDirectPattern:参数加应用一句", "type-uses-pattern"),
    ("NarrationType:直白规格型", "NarrationDirectPattern:参数加对比基准", "type-uses-pattern"),
    ("NarrationType:直白规格型", "NarrationDirectPattern:分组宣读", "type-uses-pattern"),
    ("NarrationType:直白规格型", "NarrationDirectPattern:展会口播", "type-uses-pattern"),
    ("NarrationDirectPattern:纯参数宣读", "DirectRule:参数纪律", "pattern-follows"),
    ("NarrationDirectPattern:分组宣读", "DirectRule:排序纪律", "pattern-follows"),
    ("NarrationDirectPattern:展会口播", "DirectRule:宣读语速", "pattern-follows"),
    ("NarrationDirectPattern:参数加对比基准", "DirectRule:禁修辞", "pattern-follows"),
    ("NarrationDirectPattern:参数加应用一句", "DirectRule:混合极规则", "pattern-follows"),
    ("NarrationType:直白规格型", "NarrationExample:PHO-SC-4分组宣读", "type-uses-sample"),
    ("NarrationType:直白规格型", "NarrationExample:PHO-SC-4对比基准", "type-uses-sample"),
    ("NarrationType:直白规格型", "NarrationExample:PHO-SC-4展会口播", "type-uses-sample"),
    ("NarrationType:直白规格型", "NarrationExample:仪器直白规格体", "type-uses-sample"),
    ("NarrationType:直白规格型", "DirectRule:混合极规则", "type-adopts-rule"),
]:
    if (s, t, ty) not in KEYS:
        g["relations"].append({"source": s, "target": t, "type": ty, "props": {}})
        KEYS.add((s, t, ty))

json.dump(g, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("直白子体系 added:", len(g["entities"]), "entities /", len(g["relations"]), "relations")
