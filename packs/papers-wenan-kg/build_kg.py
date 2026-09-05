# -*- coding: utf-8 -*-
"""Build pack fragments/papers-wenan-kg/kg.json (广告文案/广告词 knowledge fragment).

Schema: docs/PAPER_INGESTION.md — 5 node types (Paper/Concept/Method/Finding/Theory)
+ 7 relation types. Confidence tiers: DB_REFERENCE (papers) vs LLM_INFERRED
(derived Concept/Method/Finding/Theory). Rule 6: quality over quantity — off-topic
papers are dropped, never invented, abstracts never written.
"""
import json
import os
import sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kg.json")
DOM = ["叙事"]

entities = []
relations = []
seen = set()


def add_entity(eid, etype, name, props, sources):
    if eid in seen:
        raise SystemExit("DUPLICATE ENTITY: " + eid)
    seen.add(eid)
    entities.append({
        "id": eid,
        "type": etype,
        "name": name,
        "domains": list(DOM),
        "props": props,
        "sources": list(sources),
    })
    return eid


def add_rel(source, reltype, target):
    if source == target:
        raise SystemExit("SELF LOOP: " + source)
    relations.append({
        "source": source,
        "type": reltype,
        "target": target,
        "domains": list(DOM),
    })


# ---------------------------------------------------------------------------
# 1. Papers  (Paper:OA-文案-NNN) — metadata only, no abstract.
# ---------------------------------------------------------------------------
# (num, title, year, cited, doi, note)
PAPERS = [
    (1, "Persuasion and advertising English: Metadiscourse in slogans and headlines", 2001, 316, "10.1016/s0378-2166(01)80026-6", "广告英语口号与标题的元话语研究"),
    (2, "Rational Versus Emotional Appeals in Newspaper Advertising: Copy, Art, and Layout Differences", 2009, 74, "10.1080/10496490903281353", "报纸广告理性vs情感诉求与文案/版式差异"),
    (3, "Discovering the Role of Emotional and Rational Appeals and Hidden Heterogeneity of Consumers in Advertising Copies for Sustainable Marketing", 2020, 62, "10.3390/su12125189", "广告文案情感/理性诉求与消费者隐异质性"),
    (4, "Be rational or be emotional: advertising appeals, service types and consumer responses", 2014, 248, "10.1108/ejm-10-2012-0613", "诉求×服务类型与消费响应"),
    (5, "Emotional or Rational? The Determination of the Influence of Advertising Appeal on Advertising Effectiveness", 2016, 79, "10.1515/saeb-2016-0130", "广告诉求对广告效果的影响判定"),
    (6, "The prevalence of emotional and rational tone in social advertising appeals", 2021, 60, "10.1108/rausp-08-2020-0187", "社会(公益)广告情感/理性诉求的普遍性"),
    (7, "Emotional and rational product appeals in televised food advertisements for children: analysis of commercials shown on US broadcast networks", 2007, 67, "10.1177/1367493507082758", "儿童电视食品广告的情感/理性产品诉求"),
    (8, "An international analysis of emotional and rational appeals in services vs goods advertising", 1999, 277, "10.1108/07363769910250769", "服务vs商品广告的情感/理性诉求国别比较"),
    (9, "Does Emotional Appeal Work in Advertising? The Rationality Behind Using Emotional Appeal to Create Favorable Brand Attitude", 2013, 54, "", "情感诉求与有利品牌态度形成"),
    (10, "Redefining Rational and Emotional Advertising Appeals as Available Processing Resources: Toward an Information Processing Perspective", 2019, 41, "10.1080/10496491.2019.1699631", "从信息加工视角重述理性/情感诉求"),
    (11, "Exploring the Relative Effectiveness of Emotional, Rational, and Combination Advertising Appeals on Sport Consumer Behavior", 2018, 31, "10.32731/smq.272.062018.02", "运动消费中理性/情感/组合诉求的相对效果"),
    (12, "The rhetorical functions of slogans: Classifications and characteristics", 1980, 91, "10.1080/01463378009369362", "口号修辞功能之分类与特征"),
    (13, "Figures of Rhetoric in Advertising Language", 1996, 699, "10.1086/209459", "广告语言中的修辞格"),
    (14, "Bilingualism and the Emotional Intensity of Advertising Language", 2008, 251, "10.1086/595022", "广告语言双语与情绪强度"),
    (15, "Persuasion and Culture: Advertising Appeals in Individualistic and Collectivistic Societies", 1994, 734, "10.1006/jesp.1994.1016", "个人主义/集体主义文化下的广告诉求选择"),
    (16, "Affect Intensity and the Consumer's Attitude toward High Impact Emotional Advertising Appeals", 1996, 166, "10.1080/00913367.1996.10673498", "影响强度与高冲击情感诉求的态度响应"),
    (17, "Advertising Appeals, Moderators, And Impact on Persuasion", 2017, 68, "10.2501/jar-2017-017", "广告诉求的调节变量与说服影响"),
    (18, "An analysis of rhetorical figures and other linguistic devices in corporation brand slogans", 2014, 46, "10.1080/13527266.2014.917331", "企业品牌口号的修辞格与语言手段"),
    (19, "Dual-Modality Disclaimers, Emotional Appeals, and Production Techniques in Food Advertising Airing During Programs Rated for Children", 2009, 71, "10.2753/joa0091-3367380407", "食品广告免责声明/情感诉求与制作技术"),
    (20, "The Power of Emotional Appeals in Advertising", 2010, 82, "10.2501/s0021849910091336", "广告情感诉求的力量"),
    (21, "The Power of Emotional Advertising Appeals: Examining Their Influence on Consumer Purchasing Behavior and Brand–Customer Relationship", 2023, 75, "10.3390/su151813337", "情感诉求对购买行为与品牌关系的影响"),
    (22, "How advertising slogans can prime evaluations of brand extensions", 1993, 115, "10.1002/mar.4220100106", "广告口号对品牌延伸评价的启动"),
    (23, "Linguistic Characteristics of Commercial and Social Advertising Slogans", 2015, 65, "10.3846/cpe.2015.275", "商业与社会广告口号的语言特征"),
    (24, "How advertising slogans can prime evaluations of brand extensions: further empirical results", 1998, 84, "10.1108/10610429810244666", "口号启动品牌延伸(进一步实证)"),
    (25, "A comparison of parents' and children's knowledge of brands and advertising slogans in the United States: implications for consumer socialization", 2000, 80, "10.1080/135272600750036346", "家长/儿童的品牌与口号知识比较"),
    (26, "Surface‐structure transformations and advertising slogans: The case for moderate syntactic complexity", 2002, 60, "10.1002/mar.10027", "口号表层结构变换与适度句法复杂度"),
    (27, "Computer-aided content analysis: What do 240 advertising slogans have in common?", 1996, 53, "10.1007/bf00557312", "240条口号计算机辅助内容分析(共性)"),
    (28, "The Analysis of some Stylistic Features of English Advertising Slogans", 2014, 33, "10.15823/zz.2014.013", "英语广告口号文体特征分析"),
    (29, "English or a Local Language in Advertising?: The Appreciation of Easy and Difficult English Slogans in the Netherlands", 2010, 97, "10.1177/0021943610364524", "口号语言(母语/英语)难易接受度"),
    (30, "Got slogan? Guidelines for creating effective slogans", 2007, 149, "10.1016/j.bushor.2007.05.002", "有效口号的创作指南"),
    (31, "Why place branding is not about logos and slogans", 2013, 128, "10.1057/pb.2013.11", "地方品牌化不只是标识口号(批判)"),
    (32, "Brands affect slogans affect brands? Competitive interference, brand equity and the brand-slogan link", 2005, 83, "10.1057/palgrave.bm.2540212", "品牌与口号双向作用与品牌资产链接"),
    (33, "The Curious Case of Behavioral Backlash: Why Brands Produce Priming Effects and Slogans Produce Reverse Priming Effects", 2010, 146, "10.1086/656577", "品牌启动与口号反向启动的差异"),
    (34, "What Makes a Slogan Memorable and Who Remembers It", 1994, 67, "10.1080/10641734.1994.10505018", "口号可记忆性及记忆人群"),
    (35, "A study of the antecedents of slogan liking", 2014, 51, "10.1016/j.jbusres.2014.05.004", "口号喜爱前因研究"),
    (36, "Consumer Response to Polysemous Brand Slogans", 2007, 54, "10.1086/510225", "多义品牌口号与消费响应"),
    (37, "The Effects of Associative Slogans on Tourists' Attitudes and Travel Intention", 2016, 67, "10.1177/0047287515627029", "联想口号对游客态度与出行意向的影响"),
    (38, "Analysing tourism slogans in top tourism destinations", 2016, 53, "10.1016/j.jdmm.2016.04.004", "顶级旅游目的地口号分析"),
    (39, "Destination brand positioning slogans – towards the development of a set of accountability criteria", 2004, 69, "", "目的地品牌定位口号的问责标准"),
]

paper_ids = {}
for num, title, year, cited, doi, note in PAPERS:
    eid = "Paper:OA-文案-%03d" % num
    if doi:
        src = ["https://doi.org/" + doi]
    else:
        src = ["%s (%d)" % (title, year)]
    paper_ids[num] = eid
    add_entity(
        eid, "Paper", title,
        {
            "专业": "广告文案",
            "年份": str(year),
            "被引": str(cited),
            "DOI": doi,
            "域": "叙事",
            "置信度": "DB_REFERENCE",
            "说明": note,
        },
        src,
    )


# ---------------------------------------------------------------------------
# 2. Concepts  (LLM_INFERRED)
# ---------------------------------------------------------------------------
def C(name, definition, src_papers):
    return add_entity("Concept:" + name, "Concept", name,
                      {"定义": definition, "置信度": "LLM_INFERRED", "专业": "广告文案"},
                      [paper_ids[n] for n in src_papers])


C("广告诉求(理性/情感)", "广告文案以理性信息(规格/功能/数据)或情感信息(感官/情绪/体验)为核心的说服逻辑", [1, 2, 3, 4, 5, 6, 8])
C("诉求-品类匹配", "广告诉求与产品品类/卷入度匹配时说服更强,品类是诉求选择的调节变量", [4, 7, 8, 11, 17])
C("产品卷入度", "消费者对产品的卷入/涉入水平,高涉入走理性中心路径,低涉入走情感边缘路径", [3, 4, 10, 17])
C("加工路径(中心/边缘)", "说服传播中存在中心(论据驱动)与边缘(线索驱动)两条信息加工路径", [1, 10, 16, 17])
C("广告元话语", "广告语言中的元话语与人称(we/you)作为交互标记调节劝服力", [1, 23])
C("口号修辞格", "比喻/双关/头韵/押韵等修辞格在口号中提升注意与说服", [12, 13, 18, 28, 36])
C("口号记忆/识别", "口号的可记忆性与识别度,由简短、品类关联等驱动", [26, 27, 30, 34])
C("品牌-口号链接", "口号激活品牌/品类联想并影响品牌延伸评价与品牌资产", [18, 22, 24, 32, 33])
C("双语广告(情绪强度)", "广告语言使用母语或外语影响口号的情绪强度与情感反应", [14, 29])
C("广告态度/品牌态度", "消费者对广告及品牌的整体评价,情感诉求常通过态度中介购买", [9, 16, 20, 21, 35])
C("口号简洁性", "口号的简短/精炼程度,过繁降低加工与记忆", [26, 27, 30])
C("视频广告劝服线索", "视频广告中的社会/幽默/叙事等劝服线索如何驱动观看与传播", [7, 11, 19, 21])

# ---------------------------------------------------------------------------
# 3. Methods  (LLM_INFERRED)
# ---------------------------------------------------------------------------
def M(name, point, src_papers):
    return add_entity("Method:" + name, "Method", name,
                      {"要点": point, "置信度": "LLM_INFERRED", "专业": "广告文案"},
                      [paper_ids[n] for n in src_papers])


M("内容分析法(广告语言)", "对广告文案/口号做系统编码与频次统计,归纳诉求与语言特征", [2, 7, 19])
M("受众实验(诉求操纵)", "操纵理性/情感诉求并测量态度/购买意向,检验诉求主效应与调节", [9, 11, 16, 4])
M("元分析(广告效果)", "合并多项广告效果研究的效应量,检验诉求与调节变量的一致性结论", [17, 20])
M("计算机辅助文本分析", "用程序对大批口号做词汇/句式自动分析,识别语言共性", [23, 27])
M("语言风格分析(口号修辞)", "从文体学角度分析口号的修辞手法、句法与语言风格", [12, 13, 18, 28, 29])

# ---------------------------------------------------------------------------
# 4. Findings  (LLM_INFERRED) — "某条件→某效应", 可操作
# ---------------------------------------------------------------------------
def F(name, conclusion, src_papers):
    return add_entity("Finding:" + name, "Finding", name,
                      {"结论": conclusion, "置信度": "LLM_INFERRED"},
                      [paper_ids[n] for n in src_papers])


F("理性诉求-高涉入科技品效应", "理性/规格诉求×科技/高涉入产品 → 可信度/专业感↑ (适用: 直白规格型; 高涉入走中心路径)", [2, 4, 8, 17])
F("情感诉求-食品效应", "情感/感官诉求×食品 → 食欲/购买冲动↑ (适用: 食品广告词)", [7, 19])
F("情感诉求-普通品效应", "情感诉求×普通低涉入品 → 品牌情感/参与↑ (适用: 大众消费广告词)", [9, 11, 20, 21])
F("诉求-品类匹配效应", "诉求与产品卷入度/品类类型匹配 → 广告态度↑ (匹配是关键调节变量)", [4, 8, 11, 17])
F("口号简洁-品名记忆效应", "口号简短·含明确产品名 → 记忆/识别↑ (适用: 品牌记忆型口号)", [26, 27, 30, 34])
F("口号修辞-说服效应", "口号用修辞(比喻/双关/头韵) → 说服/记忆↑ (适用: 概念型口号)", [12, 13, 18, 28])
F("元话语-劝服效应", "广告语言元话语/人称(we/you) → 劝服↑", [1, 23])
F("视频劝服线索-传播效应", "视频广告劝服线索(社会/幽默/叙事) → 病毒传播/观看↑", [11, 19, 21, 17])
F("口号句法复杂度-记忆效应", "适度句法复杂度(非过度简单/复杂) → 记忆/理解↑", [26, 27, 30])
F("双语口号-情绪强度效应", "母语口号 → 情绪强度/情感反应↑ (外语口号理解成本高)", [14, 29])
F("文化-诉求匹配效应", "个人主义文化×理性诉求 / 集体主义文化×情感诉求 → 说服↑", [15])
F("口号多义-加工效应", "适度双关/多义口号 → 加工深度/品牌兴趣↑ (过度多义反损清晰)", [13, 18, 36])

# ---------------------------------------------------------------------------
# 5. Theories  (LLM_INFERRED)
# ---------------------------------------------------------------------------
def T(name, point, src_papers):
    return add_entity("Theory:" + name, "Theory", name,
                      {"要点": point, "置信度": "LLM_INFERRED", "专业": "广告文案"},
                      [paper_ids[n] for n in src_papers])


T("精细加工可能性模型(ELM)", "说服存在中心与边缘两条加工路径;高涉入走中心(论据),低涉入走边缘(情感/线索)", [1, 4, 10, 16, 17])
T("说服-文化价值理论", "文化价值(个人主义/集体主义)决定何种诉求更有效,诉求需与文化契合", [15])
T("叙事传输理论", "视频广告中的叙事/故事引起沉浸传输,弱化抗辩并提升态度与传播", [8, 11, 17, 20, 21])
T("修辞学/语言风格理论", "口号修辞格与语言风格通过对形式的注意与共鸣影响说服与记忆", [12, 13, 18, 28])
T("启动理论(口号品牌延伸)", "口号作为启动刺激激活品牌/品类联想,进而影响品牌延伸与品牌资产评价", [22, 24, 32, 33])

# ---------------------------------------------------------------------------
# 6. Relations
# ---------------------------------------------------------------------------
# paper-about : Paper -> Concept
ABOUT = {
    1: ["广告元话语", "加工路径(中心/边缘)"],
    2: ["广告诉求(理性/情感)", "广告态度/品牌态度"],
    3: ["广告诉求(理性/情感)", "产品卷入度"],
    4: ["广告诉求(理性/情感)", "诉求-品类匹配", "产品卷入度"],
    5: ["广告诉求(理性/情感)"],
    6: ["广告诉求(理性/情感)"],
    7: ["广告诉求(理性/情感)", "诉求-品类匹配", "视频广告劝服线索"],
    8: ["诉求-品类匹配", "广告诉求(理性/情感)"],
    9: ["广告态度/品牌态度", "广告诉求(理性/情感)"],
    10: ["加工路径(中心/边缘)", "广告诉求(理性/情感)"],
    11: ["诉求-品类匹配", "视频广告劝服线索"],
    12: ["口号修辞格", "口号记忆/识别"],
    13: ["口号修辞格"],
    14: ["双语广告(情绪强度)", "口号修辞格"],
    15: ["广告诉求(理性/情感)", "诉求-品类匹配"],
    16: ["加工路径(中心/边缘)", "广告态度/品牌态度"],
    17: ["诉求-品类匹配", "产品卷入度"],
    18: ["口号修辞格", "品牌-口号链接"],
    19: ["视频广告劝服线索", "口号修辞格", "诉求-品类匹配"],
    20: ["广告态度/品牌态度", "广告诉求(理性/情感)"],
    21: ["广告态度/品牌态度", "广告诉求(理性/情感)"],
    22: ["品牌-口号链接", "口号记忆/识别"],
    23: ["口号记忆/识别", "口号修辞格"],
    24: ["品牌-口号链接"],
    25: ["口号记忆/识别"],
    26: ["口号记忆/识别", "口号简洁性"],
    27: ["口号修辞格", "口号简洁性", "口号记忆/识别"],
    28: ["口号修辞格"],
    29: ["双语广告(情绪强度)", "口号记忆/识别"],
    30: ["口号简洁性", "口号记忆/识别"],
    31: ["品牌-口号链接", "广告态度/品牌态度"],
    32: ["品牌-口号链接", "口号记忆/识别"],
    33: ["品牌-口号链接", "加工路径(中心/边缘)"],
    34: ["口号记忆/识别", "口号简洁性"],
    35: ["广告态度/品牌态度", "口号记忆/识别"],
    36: ["口号修辞格", "广告态度/品牌态度"],
    37: ["口号记忆/识别", "广告态度/品牌态度"],
    38: ["口号记忆/识别", "口号修辞格"],
    39: ["广告态度/品牌态度", "口号记忆/识别"],
}
for num, cl in ABOUT.items():
    for name in cl:
        add_rel(paper_ids[num], "paper-about", "Concept:" + name)

# paper-finds : Paper -> Finding
FINDS = {
    "理性诉求-高涉入科技品效应": [2, 4, 8, 17],
    "情感诉求-食品效应": [7, 19],
    "情感诉求-普通品效应": [9, 11, 20, 21],
    "诉求-品类匹配效应": [4, 8, 11, 17],
    "口号简洁-品名记忆效应": [26, 27, 30, 34],
    "口号修辞-说服效应": [12, 13, 18, 28],
    "元话语-劝服效应": [1, 23],
    "视频劝服线索-传播效应": [11, 19, 21, 17],
    "口号句法复杂度-记忆效应": [26, 27, 30],
    "双语口号-情绪强度效应": [14, 29],
    "文化-诉求匹配效应": [15],
    "口号多义-加工效应": [13, 18, 36],
}
for fname, nums in FINDS.items():
    for n in nums:
        add_rel(paper_ids[n], "paper-finds", "Finding:" + fname)

# paper-uses : Paper -> Theory
USES = {
    "精细加工可能性模型(ELM)": [1, 4, 10, 16, 17],
    "说服-文化价值理论": [15],
    "叙事传输理论": [8, 11, 17, 20, 21],
    "修辞学/语言风格理论": [12, 13, 18, 28],
    "启动理论(口号品牌延伸)": [22, 24, 32, 33],
}
for tname, nums in USES.items():
    for n in nums:
        add_rel(paper_ids[n], "paper-uses", "Theory:" + tname)

# paper-proposes : Paper -> Method
PROPOSES = {
    "内容分析法(广告语言)": [2, 7, 19],
    "受众实验(诉求操纵)": [4, 9, 11, 16],
    "元分析(广告效果)": [17, 20],
    "计算机辅助文本分析": [23, 27],
    "语言风格分析(口号修辞)": [12, 13, 18, 28, 29],
}
for mname, nums in PROPOSES.items():
    for n in nums:
        add_rel(paper_ids[n], "paper-proposes", "Method:" + mname)

# concept-related-to : Concept -> Concept
REL_CONCEPTS = [
    ("广告诉求(理性/情感)", "加工路径(中心/边缘)"),
    ("广告诉求(理性/情感)", "诉求-品类匹配"),
    ("诉求-品类匹配", "产品卷入度"),
    ("口号修辞格", "口号记忆/识别"),
    ("口号修辞格", "品牌-口号链接"),
    ("口号简洁性", "口号记忆/识别"),
    ("双语广告(情绪强度)", "口号修辞格"),
    ("广告元话语", "广告诉求(理性/情感)"),
    ("广告态度/品牌态度", "加工路径(中心/边缘)"),
    ("视频广告劝服线索", "广告诉求(理性/情感)"),
    ("口号记忆/识别", "广告元话语"),
    ("产品卷入度", "加工路径(中心/边缘)"),
]
for a, b in REL_CONCEPTS:
    add_rel("Concept:" + a, "concept-related-to", "Concept:" + b)

# --- 与科生规则接线 (existing ids, verified in kesheng-kg/kg.json) ---
# finding-evidence-for-rule : Finding -> 科生规则
EVIDENCE_FOR_RULE = {
    "理性诉求-高涉入科技品效应": ["NarrationType:直白规格型", "AudienceMode:EXP"],
    "情感诉求-食品效应": ["NarrationType:科普短视频", "AudienceMode:PUB"],
    "情感诉求-普通品效应": ["NarrationType:科普短视频", "AudienceMode:PUB"],
    "诉求-品类匹配效应": ["Rule:概念先行", "Rule:五层检查体系"],
    "口号简洁-品名记忆效应": ["FailureLesson:文案白名单", "Rule:图文对位"],
    "口号修辞-说服效应": ["Rule:概念先行", "FailureLesson:文案白名单"],
    "元话语-劝服效应": ["FailureLesson:文案白名单", "Rule:五层检查体系"],
    "视频劝服线索-传播效应": ["NarrationType:科普短视频", "Rule:概念先行"],
    "口号句法复杂度-记忆效应": ["Rule:图文对位", "NarrationRule:语速档位"],
    "双语口号-情绪强度效应": ["AudienceMode:PUB", "Rule:概念先行"],
    "文化-诉求匹配效应": ["Rule:五层检查体系", "Rule:概念先行"],
    "口号多义-加工效应": ["FailureLesson:文案白名单", "Rule:概念先行"],
}
for fname, rules in EVIDENCE_FOR_RULE.items():
    for r in rules:
        add_rel("Finding:" + fname, "finding-evidence-for-rule", r)

# method-supports-rule : Method -> 科生规则
METHOD_SUPPORTS_RULE = {
    "内容分析法(广告语言)": ["Rule:五层检查体系", "FailureLesson:文案白名单", "Rule:图文对位"],
    "受众实验(诉求操纵)": ["Rule:五层检查体系", "Rule:概念先行"],
    "元分析(广告效果)": ["Rule:五层检查体系"],
    "计算机辅助文本分析": ["Rule:五层检查体系", "FailureLesson:文案白名单", "Rule:图文对位"],
    "语言风格分析(口号修辞)": ["Rule:概念先行", "FailureLesson:文案白名单"],
}
for mname, rules in METHOD_SUPPORTS_RULE.items():
    for r in rules:
        add_rel("Method:" + mname, "method-supports-rule", r)

# ---------------------------------------------------------------------------
# 7. Emit
# ---------------------------------------------------------------------------
os.makedirs(os.path.dirname(OUT), exist_ok=True)
pack = {
    "schema_version": "1.0",
    "pack": "papers-wenan-kg",
    "role": "广告文案/研究支撑",
    "dom": "叙事",
    "entities": entities,
    "relations": relations,
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(pack, f, ensure_ascii=False, indent=1)

# stats
from collections import Counter
tc = Counter(e["type"] for e in entities)
print("OUT:", OUT)
print("entities total:", len(entities), dict(tc))
print("relations total:", len(relations))
print("relations/entity: %.2f" % (len(relations) / len(entities)))
