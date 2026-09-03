# -*- coding: utf-8 -*-
"""Add the 10 复盘-optimization rules to workflow-seed (工艺), wire to 五层检查体系, rebuild."""
import io, json
P = r"F:/AI/kesheng/packs/workflow-seed/kg.json"
d = json.load(io.open(P, encoding="utf-8-sig"))
ents = d.setdefault("entities", []); rels = d.setdefault("relations", [])

def add(eid, name, desc, src):
    e = {"id": eid, "type": "Rule", "name": name,
         "props": {"说明": desc, "出处": "runs/_lessons/FAILURE-LIBRARY.md(泛化) / 项目复盘总结.md"},
         "sources": ["knowledge/FAILURE-LIBRARY.md", src], "domains": ["工艺"]}
    if not any(x["id"] == eid for x in ents):
        ents.append(e)

add("Rule:用户定方向拍板",
    "用户定方向(风格全局视觉/品牌/受众=拍板项)",
    "强调色/主色/画风/品牌名/用字/logo/受众模式(EXP直白) 是用户拍板项，必须在简报/定档就问，勿当团队判断 M3 才落；EXP=直白规格/术语不解释/字幕注承担，PUB=才科普。来源 失败F-11/F-18/F-14。",
    "orchestration/ORCHESTRATION.md §5-20")
add("Rule:参考图挂载清单必写",
    "每镜 prompt 必带参考图挂载清单",
    "每镜 prompt 交付自带『参考图挂载清单』(文件+取哪部分→放哪)，不带=不合格。来源 失败F-12。",
    "orchestration/ORCHESTRATION.md §5-21")
add("Rule:产品结构必读真图",
    "写产品/结构镜头前必看参考图+依真实结构",
    "写产品/结构镜头前必 read_image 看参考图 + 依真实产品结构(两件套/内部腔体/部件)，不凭印象堆它没有的细节。来源 失败F-13。",
    "orchestration/ORCHESTRATION.md §5-21")
add("Rule:数据卡锁值大字号",
    "数据卡/曲线默认大字号+锁值，不让AI生成数字",
    "图表层/数据卡默认大字号(主值≥8-10%画面高)+等宽；数据一律用数据卡字卡图参考锁值，不让AI生成数字。来源 失败F-15。",
    "orchestration/ORCHESTRATION.md §5-22")
add("Rule:信息点去重",
    "分镜前信息点去重",
    "同一数据点(10000h/±0.2%/衰减<10%)只讲一次，重复即删。来源 失败F-17。",
    "orchestration/ORCHESTRATION.md §5-22")
add("Rule:AI反模式负面词前置",
    "科学/品牌红线 AI 反模式负面词前置写全",
    "大光球/激光束/彩虹/改造设备/镀铬反光/合成一台 等 AI 反模式负面词前置写全作每镜强制反面，不翻车再补。来源 失败F-16。",
    "orchestration/ORCHESTRATION.md §5-22")

for eid in ["Rule:用户定方向拍板","Rule:参考图挂载清单必写","Rule:产品结构必读真图",
            "Rule:数据卡锁值大字号","Rule:信息点去重","Rule:AI反模式负面词前置"]:
    rel = (eid, "Rule:五层检查体系", "concept-related-to")
    if rel not in {(r.get("source"), r.get("target"), r.get("type")) for r in rels}:
        rels.append({"source": eid, "target": "Rule:五层检查体系", "type": "concept-related-to", "props": {}})

json.dump(d, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("added 6 rules + wired to 五层检查体系")
