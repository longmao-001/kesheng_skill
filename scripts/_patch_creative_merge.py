# -*- coding: utf-8 -*-
"""creative-director-skill + koda-stack 融入科生: 20方法论/洞察规则/6维评分/三轴/管线映射 → 图谱"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

LIB = "libs/creative-director-skill/creative-director"
SRC = [LIB + "/references/methods-catalog.md"]
SRC2 = [LIB + "/SKILL.md", LIB + "/references/scoring-calibration.md"]
SRC3 = ["libs/koda-stack/README.md"]

METHODS = [
    ("SIT结构模板", "A结构模板", "用既定结构模板(替代/去除/统一/倍增等)改造成熟物, 替代自由联想"),
    ("SCAMPER", "A结构模板", "替代Substitute/组合Combine/调整Adapt/放大Magnify/挪作他用Put/删除Eliminate/重排Reverse 逐项推演"),
    ("TRIZ广告十原则", "A结构模板", "发明问题解决理论的广告化十原则, 从矛盾中找创意解法"),
    ("形态分析法", "A结构模板", "把对象拆成维度×取值矩阵, 交叉组合出新概念"),
    ("双关联Bisociation", "B联想碰撞", "两个不相干领域碰撞出新意义(如'洗衣机×动物园')"),
    ("随机闯入/随机词", "B联想碰撞", "随机词/随机概念强制进入, 打破思维定势"),
    ("强制连接", "B联想碰撞", "把两件毫无关系的事物按规则连接"),
    ("综摄法Synectics", "B联想碰撞", "类比/明喻/个人代入/幻想 四类比驱动创新"),
    ("反向头脑风暴", "C反转颠覆", "先列出'怎么把这事做砸', 再反向得到妙招"),
    ("最烂想法", "C反转颠覆", "先产出最糟糕的10个想法, 常有意外可用的"),
    ("挑衅PO", "C反转颠覆", "用'PO'挑衅句('角度必须消失')开启颠覆"),
    ("奥博李克策略", "D重组扰动", "随机'扰乱卡'指令打破推理链(如'拔掉最重要的钉子')"),
    ("六顶思考帽", "D重组扰动", "白事实/红情感/黑批判/黄乐观/绿创造/蓝流程 分角色思考"),
    ("迪士尼创意策略", "D重组扰动", "梦想家→现实家→批评家 三角色轮流推进"),
    ("疯狂8连", "E量产", "8分钟8个草图, 先量后质"),
    ("脑写6-3-5", "E量产", "6人×3想法×5轮 纸上接力, 无噪音量产"),
    ("星爆提问Starbursting", "E量产", "围绕想法的5W1H层层提问, 暴露盲点"),
    ("第一性原理", "F加成", "回到最基本物理/事实做推理, 不套用类比与惯例"),
    ("横向思维工具箱", "F加成", "de Bono横向思维系列(逃逸概念/插入随机/操作词)"),
    ("设计冲刺草图", "F加成", "三遍变体草图+热身后画故事板, 快筛概念"),
]
PATCH = []
for i, (n, c, d) in enumerate(METHODS, 1):
    PATCH.append({"id": f"IdeationMethod:{n}", "type": "IdeationMethod", "name": n,
                  "props": {"分类": c, "说明": d}, "sources": SRC, "domains": ["叙事"]})

PATCH += [
    {"id": "InsightRule:四点洞察", "type": "InsightRule", "name": "Pollard四点洞察", "props": {"链条": "Problem难题→Insight洞察→Advantage优势→Strategy策略", "格式": "[受众]想要[X], 但[Y]在阻碍, 因为[Z]", "质检": "听完是否'对, 就是这个, 但我从没这么说'——刷新世界观才算洞察", "铁律": "洞察先于创意: 没有洞察不做创意"}, "sources": SRC2, "domains": ["叙事"]},
    {"id": "EvalRule:评分标定", "type": "EvalRule", "name": "创意评分标定(戛纳校准)", "props": {"六维权重": "原创性0.25/策略契合0.20/情绪反应0.20/可行性0.15/延展性0.10/简洁0.10", "三轴门控": "轴1简报合规(硬门)→轴2创意强度(六维加权)→轴3延展性/创意层级", "防膨胀": "禁用'还不错'式灌分; 多视角面板(策略/创意/执行/客户)打分", "打回": "评分<7.0或平台期→案例浸泡(重读8-12个传奇案例)再回洞察阶段"}, "sources": SRC2, "domains": ["工艺"]},
    {"id": "CreativeRule:简洁即暴力", "type": "CreativeRule", "name": "简洁即暴力", "props": {"原则": "最好的创意一句话能讲清(Simplicity as Violence)", "只讲一个": "大创意只回答一个洞察; 说不清=不够好"}, "sources": SRC2, "domains": ["叙事"]},
    {"id": "CreativeRule:重组合法", "type": "CreativeRule", "name": "重组合法(跨界拼装)", "props": {"规则": "允许: A案例的洞察+B案例的机制+C案例的情绪 重组; 必须注明拼了哪些卡(溯源), 这是戛纳精选的常规做法而非抄袭"}, "sources": SRC2, "domains": ["叙事"]},
    {"id": "CreativeRule:结构方法代替自由联想", "type": "CreativeRule", "name": "结构方法代替自由联想", "props": {"规则": "创意生成必须用结构化方法论(SIT/SCAMPER/TRIZ/双关联…20法), 禁止'灵光一现'式自由联想", "方法目录": "kg_query --domain 叙事 IdeationMethod / libs/creative-director-skill/references/methods-catalog.md"}, "sources": SRC, "domains": ["工艺"]},
    {"id": "PipelineMapping:koda十步", "type": "PipelineMapping", "name": "Koda十步管线映射科生", "props": {"映射": "brief=KSP-02简报(制片人)→concept=KSP-04概念(导演)→script=口播稿(编剧)→storyboard=分镜表(分镜师)→art-direction=美术方案(美术指导)→trends=受众与市场(观众代言人)→generate=逐镜prompt(prompt工程师)→assemble=AI原生后期(剪辑师)→publish=交付签收(KSP-06)→repurpose=多平台复用(图文切片/重剪)", "参考": "libs/koda-stack/skills/ 10 个 skill 同名对应"}, "sources": SRC3, "domains": ["工艺"]},
]

P = r"F:/AI/kesheng/packs/creative-kg/kg.json"
os.makedirs(os.path.dirname(P), exist_ok=True)
g = {"schema_version": "1.0", "pack": "creative-kg", "role": "导演/创意",
     "entities": PATCH, "relations": []}
ids = {e["id"] for e in PATCH}
KEYS = set()
for i, (n, c, d) in enumerate(METHODS, 1):
    pass
# 关系: 方法-分类 → 概念先行规则(跨片段 id, 合并时解析)
RELS = [
    ("InsightRule:四点洞察", "Rule:概念先行", "insight-feeds"),
    ("EvalRule:评分标定", "Rule:概念先行", "eval-for"),
    ("CreativeRule:简洁即暴力", "Rule:概念先行", "principle-of"),
    ("CreativeRule:重组合法", "Rule:概念先行", "principle-of"),
    ("CreativeRule:结构方法代替自由联想", "Rule:概念先行", "principle-of"),
]
for s, t, ty in RELS:
    g["relations"].append({"source": s, "target": t, "type": ty, "props": {}})
for i, (n, c, d) in enumerate(METHODS, 1):
    g["relations"].append({"source": f"IdeationMethod:{n}", "target": "Rule:概念先行", "type": "method-for", "props": {}})
    g["relations"].append({"source": f"IdeationMethod:{n}", "target": "InsightRule:四点洞察", "type": "method-requires", "props": {}})
g["relations"].append({"source": "PipelineMapping:koda十步", "target": "KspStep:KSP-04创意概念", "type": "pipeline-refs", "props": {}})
json.dump(g, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("creative-kg:", len(g["entities"]), "entities /", len(g["relations"]), "relations")
