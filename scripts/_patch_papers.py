# -*- coding: utf-8 -*-
"""论文入图谱: 从 arXiv 抓取结果 + 多智能体经典论文 → papers-kg 片段"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

RAW = r"F:/AI/kesheng/runs/_tmp-papers.json"
KEEP_IDS = {
    "2403.05131", "2311.00949", "2405.08720", "2407.14505",   # 视频生成/叙事/prompt
    "2412.05449", "2401.05998",                               # 多智能体
    "1506.06149", "2511.09248",                               # 科普传播
    "1901.07366", "2012.11851",                               # 广告效果
}
DOMAIN = {
    "2403.05131": "影像", "2311.00949": "prompt", "2405.08720": "叙事", "2407.14505": "prompt",
    "2412.05449": "工艺", "2401.05998": "工艺",
    "1506.06149": "叙事", "2511.09248": "叙事",
    "1901.07366": "叙事", "2012.11851": "叙事",
}
NOTE = {
    "2403.05131": "T2V 全面综述(Sora as world model): 一致性/相机控制/提示遵循是开放问题——支撑'参考包+风格基线+多镜原生'的选型",
    "2311.00949": "T2V prompt 优化套件: 提示词改写对视频质量的实证——支撑 prompt 公式/负面词/抽卡",
    "2405.08720": "从叙事角度观察 T2V: 长叙事视频的连贯性缺口——支撑'口播多方案+分镜按稿切段'",
    "2407.14505": "组合式 T2V 基准: 多对象/属性/关系/动作的组合一致性量化——支撑'图文对位'与一致性检查",
    "2412.05449": "GenAI 多智能体协作设计与评估: 角色分工/对话编排对质量的影响——支撑科生角色团队与检察官",
    "2401.05998": "多智能体辩论抗攻击/纠错——支撑 M3 概念评分+红队对抗",
    "1506.06149": "科普网络视频分类学(Typologies)——支撑科普型口播的体裁选择",
    "2511.09248": "科普传播知识基础设施(SciCom Wiki)——支撑科学域知识沉淀",
    "1901.07366": "视频广告效果度量(注意力/记忆)——支撑直白型'证据即卖点'与信息密度规则",
    "2012.11851": "多模态深度预测在线视频广告效果——支撑钩子/前5秒/CTA 规则",
}
CANON = [
    ("2305.14325", "Improving Factuality and Reasoning in Language Models through Multiagent Debate", "2023",
     "工艺", "多智能体辩论提升事实性与推理(科生 M3 辩论/红队的方法论源头)", "Du et al."),
    ("2305.19118", "Encouraging Divergent Thinking in Large Language Models through Multi-Agent Debate", "2023",
     "工艺", "多智能体辩论鼓励发散思维(MAD)——支撑'盲提案+交叉质询+反假共识'", "Liang et al."),
    ("2308.00352", "MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework", "2023",
     "工艺", "SOP 化多智能体协作: 角色分工+结构化产出交接——支撑科生'角色SOP+黑板交接'", "Hong et al."),
    ("2308.08155", "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation Framework", "2023",
     "工艺", "多智能体会话编排(对话/终止条件/人工介入)——支撑科生'门控+拍板卡+停止规则'", "Wu et al."),
]

papers = []
try:
    raw = json.load(open(RAW, encoding="utf-8"))
    for p in raw:
        pid = p["id"].split("/abs/")[-1].rstrip("v0123456789") if "/abs/" in p["id"] else p["id"]
        pid = p["id"].split("/abs/")[-1].split("v")[0]
        if pid in KEEP_IDS:
            papers.append((pid, p["title"], p["year"], DOMAIN.get(pid, "科学"), NOTE.get(pid, p["summary"][:120]), "arXiv"))
except Exception as e:
    print("raw err", e)

for arx, title, yr, dom, note, authors in CANON:
    papers.append((arx, title, yr, dom, note, authors))

P = r"F:/AI/kesheng/packs/papers-kg/kg.json"
os.makedirs(os.path.dirname(P), exist_ok=True)
ents = []
for arx, title, yr, dom, note, authors in papers:
    ents.append({
        "id": f"Paper:{arx}", "type": "Paper", "name": title[:60],
        "props": {"arxiv": arx, "年份": yr, "域": dom, "核心结论": note, "作者/来源": authors},
        "sources": [f"https://arxiv.org/abs/{arx}"], "domains": [dom],
    })
# 关系: 论文→支撑的现有规则/实体
REL_TARGETS = {
    "2305.14325": "Rule:概念先行", "2305.19118": "Rule:概念先行",
    "2308.00352": "Rule:五层检查体系", "2308.08155": "Rule:五层检查体系",
    "2407.14505": "Rule:图文对位", "2405.08720": "Rule:图文对位",
    "2401.05998": "Rule:概念先行", "2412.05449": "Rule:概念先行",
    "1506.06149": "NarrationType:科普视频", "1901.07366": "NarrationType:直白规格型",
    "2012.11851": "NarrationRule:开头钩子高科版", "2311.00949": "TimeAxisRule:按秒时间轴断句",
    "2403.05131": "Rule:AI原生交付原则",
}
rels = []
for arx, _t, _y, _d, _n, _a in papers:
    tgt = REL_TARGETS.get(arx)
    if tgt:
        rels.append({"source": f"Paper:{arx}", "target": tgt, "type": "paper-supports", "props": {}})
g = {"schema_version": "1.0", "pack": "papers-kg", "role": "研究支撑",
     "entities": ents, "relations": rels}
json.dump(g, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("papers-kg:", len(ents), "entities /", len(rels), "relations")
