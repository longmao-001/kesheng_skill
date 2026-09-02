# -*- coding: utf-8 -*-
"""工艺类论文按专业入库(追加到 papers-kg)"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

P = r"F:/AI/kesheng/packs/papers-kg/kg.json"
g = json.load(open(P, encoding="utf-8-sig"))
ids = {e["id"] for e in g["entities"]}

# (专业, 域, id, 标题, 年份, 核心结论, source, 关联实体)
NEW = [
    ("广告创意", "叙事", "Paper:MediumIsMessage2023", "创意媒介广告效果的元分析", "2023",
     "创意媒介(隐喻等)广告效果 meta-analysis——支撑'概念先行+创意方法库'", "https://www.tandfonline.com/doi/full/10.1080/00913367.2023.2186986", "Rule:概念先行"),
    ("口播文案", "叙事", "Paper:AdSentencePattern", "广告句式肯定/否定的说服效果", "2021",
     "肯定/否定句式对广告说服的差异化效果——支撑口播句公式F01-14的句式选择", "https://ouci.dntb.gov.ua/en/works/42rn1EX4/", "NarrationRule:克制信任律"),
    ("剪辑节奏", "剪辑", "Paper:JumpCutShortForm", "跳切与转场频率对短视频互动/持续engagement的差异影响", "2026",
     "跳切+转场频率直接改变互动与留存——支撑剪辑节奏/卡点/转场策略", "https://archives.marketing-trends-congress.com/2026/pages/PDF/paper_professor_DOST_HUANG.pdf", "ProcessRule:剪辑合成"),
    ("剪辑节奏", "剪辑", "Paper:AnatomyOfEditing", "视频剪辑解剖: AI辅助剪辑的数据集与基准", "2022",
     "剪辑动作的解剖与基准——支撑剪辑预计划/节奏的量化", "https://arxiv.org/abs/2207.09812", "ProcessRule:剪辑合成"),
    ("剪辑节奏", "剪辑", "Paper:AutoEditing", "迈向数据驱动的自动视频剪辑", "2019",
     "自动剪辑的早期范式——支撑 AI 原生后期路径", "https://arxiv.org/abs/1907.07345", "ProcessRule:剪辑合成"),
    ("剪辑理论", "剪辑", "Paper:ZeroDegreeCut", "零度剪辑、缝合体系——电影叙事惯例", "2023",
     "零度剪辑/缝合体系(叙事惯例理论)——支撑'克制、不炫技'的剪辑纪律", "http://www.artanthropology.com/wap.aspx?cid=11&cp=5&nid=1568", "ProcessRule:剪辑合成"),
    ("镜头语言/摄影", "影像", "Paper:CamMoveNL", "自然语言的镜头运动理解", "2026",
     "把自然语言映射到运镜——支撑运镜 prompt 的标准化词表", "https://arxiv.org/abs/2607.03043", "Rule:Prompt严格统一格式"),
    ("镜头语言/摄影", "影像", "Paper:DirectAVideo", "用户指定运镜与物体运动的定制视频生成", "2024",
     "运镜/运动可控生成(Direct-a-Video)——支撑'运镜指令式prompt'+单镜≤2运镜", "https://arxiv.org/abs/2402.03162", "ProcessRule:单镜抽卡"),
    ("视觉叙事", "叙事", "Paper:MAViS", "多智能体长序列视频叙事框架", "2025",
     "多智能体协同做长视频叙事(MAViS)——支撑科生'概念→分镜→口播'多角色分工", "https://arxiv.org/abs/2508.08487", "Rule:概念先行"),
    ("视觉叙事", "叙事", "Paper:VisStorySM", "社交媒体视觉叙事基准", "2019",
     "社交媒体视觉叙事基准——支撑口播/画面/字幕的叙事一致性", "https://arxiv.org/abs/1908.03505", "NarrationType:品牌形象片"),
    ("新媒体/短视频", "受众", "Paper:ShorterIsDifferent", "短即不同: 短视频平台动态特征", "2024",
     "短视频平台与长视频的机制差异——支撑科普短视频'3秒钩子+快节奏'类型参数", "https://arxiv.org/abs/2410.16058", "NarrationType:科普短视频"),
    ("新媒体/短视频", "受众", "Paper:ShortEngageLMM", "用大模型预测短视频 engagement", "2025",
     "短视频engagement预测——支撑观众代言人的'留存/钩子'检查维度", "https://arxiv.org/abs/2508.02516", "NarrationType:科普短视频"),
    ("注意力/完播", "受众", "Paper:CogLoadCompletion", "认知负荷视角下长视频完播率下降", "2021",
     "认知负荷→长视频完播率低——支撑'信息密度≤3点/分+单镜≤10s+语速档'", "https://dspace.ut.ee/bitstreams/15c57674-c541-460e-b957-b983c352d317/download", "NarrationRule:语速档位"),
    ("新媒体/质量", "工艺", "Paper:KVQ", "快手短视频质量评估", "2024",
     "短视频主观/客观质量评估(KVQ)——支撑出口闸'画面质量'维度", "https://arxiv.org/abs/2402.07220", "Rule:五层检查体系"),
]

for prof, dom, pid, title, yr, note, src, tgt in NEW:
    if pid in ids:
        continue
    g["entities"].append({
        "id": pid, "type": "Paper", "name": title, "props": {"专业": prof, "年份": yr, "核心结论": note},
        "sources": [src], "domains": [dom]})
    ids.add(pid)
    g["relations"].append({"source": pid, "target": tgt, "type": "paper-supports", "props": {}})

json.dump(g, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("papers-kg:", len(g["entities"]), "entities /", len(g["relations"]), "relations")
