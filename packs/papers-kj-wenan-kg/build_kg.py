# -*- coding: utf-8 -*-
"""Build packs/papers-kj-wenan-kg/kg.json (科技/科研广告词 paper fragment)."""
import json

PACK = "papers-kj-wenan-kg"
ROLE = "科技/科研广告词/研究支撑"
DOM = "叙事"
OUT = "F:/AI/kesheng/packs/papers-kj-wenan-kg/kg.json"

# ---------------- Papers ----------------
# (id_suffix, title, year, cited, doi, note)
PAPERS = [
    (1, "Business Advertising Appeals as a Mirror of Cultural Dimensions: A Study of Eleven Countries",
     1996, 354, "10.1080/00913367.1996.10673512", "B2B广告诉求镜像11国文化维度"),
    (2, "A Comparison of Advertising Content: Business to Business versus Consumer Services",
     1997, 140, "10.1080/00913367.1997.10673534", "B2B与消费者服务广告内容对比"),
    (3, "What's Different about Business-to-Business Advertising?",
     1986, 1, "10.1080/02650487.1986.11106965", "B2B广告与消费广告的差异"),
    (4, "Business-to-business advertising: What are the dimensions of an effective print ad?",
     1995, 22, "10.1016/0019-8501(95)00028-9", "B2B有效平面广告的维度"),
    (5, "Business-to-Business Advertising: Which Layout Style Works Best?",
     1992, 33, "10.1080/00218499.1992.12466860", "B2B广告版式风格效果比较"),
    (6, "Copy length and industrial advertising readership",
     1986, 28, "10.1016/0019-8501(86)90034-9", "工业广告文案长度与阅读率"),
    (7, "Improving industrial advertising copy",
     1986, 13, "10.1016/0019-8501(86)90052-0", "工业广告文案的改进方法"),
    (8, "The untapped potential of B2B advertising: A literature review and future agenda",
     2019, 64, "10.1016/j.indmarman.2019.05.010", "B2B广告潜能的文献综述与议程"),
    (9, "Revisiting the theory of business-to-business advertising",
     2019, 56, "10.1016/j.indmarman.2019.03.012", "再审视B2B广告理论"),
    (10, "Tell me a story: The role of narrative transportation and the C-suite in B2B advertising",
     2019, 73, "10.1016/j.indmarman.2019.02.002", "B2B广告中叙事传输与高管叙事"),
    (11, "Is advertising an underappreciated driver of sales growth in B2B markets? Theoretical perspectives",
     2020, 24, "10.1016/j.indmarman.2020.02.019", "B2B市场广告对销售增长的驱动"),
    (12, "Low attention advertising processing in B2B markets",
     2007, 37, "10.1108/08858620710773477", "B2B市场低注意广告加工"),
    (13, "The role of emotions in B2B product advertising on social media: a family business case study",
     2022, 13, "10.1108/jfbm-12-2021-0157", "B2B社媒产品广告中情绪作用(家族企业)"),
    (14, "Endorser gender and age effects in B2B advertising",
     2022, 11, "10.1016/j.jbusres.2022.04.050", "B2B广告代言人性别年龄效应"),
    (15, "Operationalizing ad creativity and its effects in B2B advertising",
     2025, 2, "10.1016/j.indmarman.2025.02.011", "B2B广告创造性的操作化与效应"),
    (16, "B2B Advertising in an Emerging Economy: Rational vs. Emotional Appeals, and Gender Stereotypes",
     2012, 2, "", "新兴市场B2B理性vs情感诉求与性别刻板"),
    (17, "Just Give Me the Facts: Literalism vs. Symbolism in B2B Advertising",
     2011, 0, "", "B2B广告字面vs象征诉求"),
    (18, "Advertising for high-technology products in the product launch phase – a content-analysis",
     2010, 2, "10.1504/ijeme.2010.038645", "高科技品上市期广告内容分析"),
    (19, "Conceptualizing visual metaphors in high tech products advertising",
     2024, 0, "10.33919/dasc.24.7.3", "高科技品广告的视觉隐喻概念化"),
    (20, "Semiotic Tools in Technology for Promoting Hi-Tech Products in Chinese and Russian Advertising",
     2020, 3, "10.1109/comsds49898.2020.9101316", "中俄高科技品广告的符号工具"),
    (21, "The Impact of Advertising Appeals on Consumers' Perception of an Advertisement for a Technical Product",
     2020, 3, "10.1007/978-3-030-39165-2_85", "技术品广告诉求对感知的影响"),
    (22, "Advertising Effectiveness of Different Media in Promoting Technology-Oriented Ideas among Young",
     2016, 3, "10.1080/10599231.2016.1235956", "面向青年的技术导向理念广告媒介效果"),
    (23, "Forecasting of advertising effectiveness for renewable energy technologies",
     2019, 58, "10.1016/j.techfore.2019.04.009", "可再生能源技术广告效果预测"),
    (24, "Different Impacts of Advertising Appeals on Advertising Attitude for High and Low Involvement Products",
     2015, 105, "10.1177/0972150915569936", "高低卷入品诉求对广告态度的影响"),
    (25, "The Influence of Involvement on Information Processing of Rational Advertising Appeals",
     2009, 4, "10.3724/sp.j.1041.2009.00357", "卷入对理性诉求信息加工的影响"),
    (26, "Consumer response to different advertising appeals for new products",
     2010, 122, "10.1057/bm.2010.22", "新品不同广告诉求与消费响应"),
    (27, "Predispositions and the comparative effectiveness of rational, emotional and discrepant appeals",
     1987, 99, "10.1007/bf02721951", "理性/情感/不一致诉求的相对效果"),
    (28, "An Experimental Investigation of Comparative Advertising: Impact of Message Appeal, Information Level",
     1980, 134, "10.1177/002224378001700203", "比较广告的信息诉求与信息量实验"),
    (29, "The Role of User Involvement, User Involvement Types, Product Category Involvement and Advertising",
     2019, 6, "10.1177/0973258619851987", "用户/品类卷入与广告效果"),
    (30, "Advertising Claim Objectivity: Antecedents and Effects",
     1993, 199, "10.1177/002224299305700408", "广告主张客观性的前因与效应"),
    (31, "How Claim Specificity Can Improve Claim Credibility in Green Advertising",
     2018, 59, "10.2501/jar-2018-001", "主张具体性提升主张可信度"),
    (32, "Misinformation effects and rational advertising: consumer responses to advertising claims verifiability",
     2024, 0, "10.1504/ijima.2024.10062545", "主张可核实性与理性广告/虚假信息"),
    (33, "Perceived Source Credibility and Advertising Persuasiveness: An Investigation of Moderators and Mediators",
     2013, 35, "10.1080/10641734.2013.787579", "来源可信度与广告说服力(调节/中介)"),
    (34, "Comparative Advertising Effectiveness: The Role of Involvement and Source Credibility",
     1991, 269, "10.1080/00913367.1991.10673205", "比较广告中卷入与来源可信度"),
    (35, "How the credibility of places affects the processing of advertising claims",
     2023, 7, "10.1016/j.jbusres.2023.114238", "地方/来源可信度对广告主张加工"),
    (36, "Trust, advertising and science communication",
     2016, 2, "10.22323/2.15050501", "信任、广告与科学传播"),
    (37, "Assessing the impact of the Huawei Brand on the Information Communication Technology Infrastructure",
     2020, 3, "10.1007/978-3-030-47579-6_8", "华为ICT基础设施品牌影响评估"),
]

# ---------------- Concepts ----------------
CONCEPTS = {
    "Concept:科技品理性诉求(规格/数据)": {
        "name": "科技品理性诉求(规格/数据)",
        "定义": "以产品规格/技术参数/性能数据为核心的说服逻辑，适用于科技/科研/工业品，走理性中心路径",
        "papers": [18, 21, 24, 25, 27, 28],
    },
    "Concept:技术信息可核实性": {
        "name": "技术信息可核实性",
        "定义": "技术陈述能被权威/实测验真核实的程度，是科技品广告信任的前提",
        "papers": [30, 31, 32, 35],
    },
    "Concept:权威/实测来源可信度": {
        "name": "权威/实测来源可信度",
        "定义": "权威机构/实测数据/专家背书带来的来源可信度，是驱动说服与态度的关键变量",
        "papers": [14, 33, 34, 35, 36],
    },
    "Concept:B2B工业品诉求(性能/可靠/一致)": {
        "name": "B2B工业品诉求(性能/可靠/一致)",
        "定义": "面向专业采购者/工程师的工业品广告，强调性能/可靠性/一致性等理性买点",
        "papers": [1, 2, 4, 6, 11, 17],
    },
    "Concept:科技品卷入度与诉求匹配": {
        "name": "科技品卷入度与诉求匹配",
        "定义": "科技品卷入/涉入程度决定诉求路径：高卷入走理性中心、低卷入走情感/象征，需匹配",
        "papers": [24, 25, 26, 29],
    },
    "Concept:认知负荷(技术堆砌)": {
        "name": "认知负荷(技术堆砌)",
        "定义": "过多技术术语/参数/复杂陈述造成的认知负荷，降低加工深度与信任，需克制",
        "papers": [6, 12, 18],
    },
    "Concept:科技品视觉隐喻/符号": {
        "name": "科技品视觉隐喻/符号",
        "定义": "用视觉隐喻与符号转译抽象技术，提升理解、记忆与区分度",
        "papers": [17, 19, 20],
    },
    "Concept:科技品广告合规(绝对化禁忌)": {
        "name": "科技品广告合规(绝对化禁忌)",
        "定义": "科技/科研广告禁用绝对化/疗效类表述，用可核实规格+数据替代，规避合规风险",
        "papers": [30, 31, 32],
    },
    "Concept:应用证据(实测/案例)": {
        "name": "应用证据(实测/案例)",
        "定义": "以使用场景/应用实测/客户案例作为说服证据，降低抽象技术的不确定感",
        "papers": [10, 22, 23, 37],
    },
    "Concept:专家信任(科研数据语言)": {
        "name": "专家信任(科研数据语言)",
        "定义": "用科研制图/数据语言/专业表达与专家对话群体沟通，获得专家信任",
        "papers": [18, 25, 36],
    },
    "Concept:科技品牌沟通(新技术采用)": {
        "name": "科技品牌沟通(新技术采用)",
        "定义": "面向新技术采用/创新扩散的品牌沟通，降低采用焦虑并建立技术信任",
        "papers": [11, 22, 23, 37],
    },
}

# ---------------- Methods ----------------
METHODS = {
    "Method:内容分析法(科技/工业广告)": {
        "name": "内容分析法(科技/工业广告)",
        "要点": "对科技/工业广告文案、诉求、符号做系统编码与频次统计，归纳诉求与语言特征",
        "papers": [1, 2, 18, 20],
    },
    "Method:受众实验(诉求操纵·科技品)": {
        "name": "受众实验(诉求操纵·科技品)",
        "要点": "操纵理性/情感诉求并测量信任/态度/购买意向，检验诉求主效应与卷入度调节",
        "papers": [24, 25, 27, 28],
    },
    "Method:来源可信度实验(权威/实测)": {
        "name": "来源可信度实验(权威/实测)",
        "要点": "操纵权威/实测/专家等来源并测量说服与态度，识别可信度中介与调节",
        "papers": [33, 34, 35],
    },
    "Method:跨文化内容比较(B2B诉求)": {
        "name": "跨文化内容比较(B2B诉求)",
        "要点": "跨国家/跨语言比较B2B与高科技广告的诉求/符号，识别文化差异",
        "papers": [1, 20],
    },
    "Method:文献综述/议程(科技广告研究)": {
        "name": "文献综述/议程(科技广告研究)",
        "要点": "系统综诉B2B/科技广告研究并设定未来议程，提炼理论缺口",
        "papers": [8, 9],
    },
    "Method:问卷/实证调查(工业品采购)": {
        "name": "问卷/实证调查(工业品采购)",
        "要点": "面向专业采购者/工程师做问卷与版面测试，评估广告文案长度/版式/关键买点",
        "papers": [4, 6, 12],
    },
}

# ---------------- Findings ----------------
# rules = target existing rule ids (cross-package rule refs are intentional)
FINDINGS = {
    "Finding:科技品理性规格诉求-专业可信效应": {
        "name": "科技品理性规格诉求-专业可信效应",
        "结论": "理性/规格诉求×科技/高涉入品 → 可信度/专业感↑ (适用: 直白规格型; 高涉入走中心路径)",
        "papers": [18, 24, 25, 27],
        "rules": ["NarrationType:直白规格型", "AudienceMode:EXP", "AudienceMode:IND"],
    },
    "Finding:技术数据可核实-信任效应": {
        "name": "技术数据可核实-信任效应",
        "结论": "技术细节/数据可核实 → 信任↑; 过度技术堆砌 → 认知负荷↓(克制)",
        "papers": [30, 31, 32, 35],
        "rules": ["NegativeRule:广告禁用词", "Rule:五层检查体系"],
    },
    "Finding:权威/实测来源可信-说服效应": {
        "name": "权威/实测来源可信-说服效应",
        "结论": "来源可信度(权威/实测/专家) → 广告说服与品牌态度↑",
        "papers": [14, 33, 34, 36],
        "rules": ["AudienceMode:EXP", "Rule:概念先行"],
    },
    "Finding:B2B工业品性能可靠-采购信任效应": {
        "name": "B2B工业品性能可靠-采购信任效应",
        "结论": "B2B/工业品强调性能/可靠性/一致性 → 专业采购者信任↑",
        "papers": [2, 4, 6, 11, 17],
        "rules": ["AudienceMode:IND", "Rule:图文对位"],
    },
    "Finding:高卷入理性优于情感-科技品效应": {
        "name": "高卷入理性优于情感-科技品效应",
        "结论": "产品卷入度高 → 理性诉求优于情感; 低卷入 → 情感/象征诉求更有效",
        "papers": [24, 26, 27, 29],
        "rules": ["NarrationType:直白规格型", "AudienceMode:IND"],
    },
    "Finding:绝对化禁忌-合规信任效应": {
        "name": "绝对化禁忌-合规信任效应",
        "结论": "科技/科研广告避免绝对化(最/第一/根治) → 合规+信任↑ (接 ad_forbidden_words)",
        "papers": [30, 31, 32],
        "rules": ["NegativeRule:广告禁用词", "Rule:五层检查体系"],
    },
    "Finding:科研数据语言-专家信任效应": {
        "name": "科研数据语言-专家信任效应",
        "结论": "科研设备用科研制图/数据/专业语言 → 专家(EXP)信任↑",
        "papers": [18, 25, 36],
        "rules": ["AudienceMode:EXP", "Rule:图文对位"],
    },
    "Finding:应用证据-科技品采用效应": {
        "name": "应用证据-科技品采用效应",
        "结论": "使用场景/应用证据(实测/案例) → 科技品采用意愿↑",
        "papers": [10, 22, 23, 37],
        "rules": ["Rule:概念先行", "AudienceMode:IND"],
    },
    "Finding:科技品视觉隐喻-理解记忆效应": {
        "name": "科技品视觉隐喻-理解记忆效应",
        "结论": "视觉隐喻/符号转译抽象技术 → 科技品理解与记忆↑",
        "papers": [17, 19, 20],
        "rules": ["Rule:图文对位", "Rule:概念先行"],
    },
    "Finding:科技品新媒体低注意-简洁效应": {
        "name": "科技品新媒体低注意-简洁效应",
        "结论": "低注意/信息流环境 → 文案简洁+单点信息更有效",
        "papers": [5, 6, 12],
        "rules": ["NarrationRule:语速档位", "Rule:五层检查体系"],
    },
    "Finding:科技品广告创造-记忆区分效应": {
        "name": "科技品广告创造-记忆区分效应",
        "结论": "适度创意/鲜明主张 → 科技品广告记忆与区分度↑(不因堆砌牺牲可信)",
        "papers": [9, 10, 15],
        "rules": ["FailureLesson:文案白名单", "Rule:概念先行"],
    },
}

# ---------------- Theories ----------------
THEORIES = {
    "Theory:科技品中心-边缘路径说服": {
        "name": "科技品中心-边缘路径说服",
        "要点": "科技品说服沿中心(论据/规格)与边缘(情感/象征)两条路径；高涉入走中心、低涉入走边缘",
        "papers": [24, 25, 27],
    },
    "Theory:科技品来源可信度理论": {
        "name": "科技品来源可信度理论",
        "要点": "权威/专家/实测来源的可信度经由信赖中介提升广告说服力与信任",
        "papers": [14, 33, 34, 36],
    },
    "Theory:创新扩散采用理论(科技品)": {
        "name": "创新扩散采用理论(科技品)",
        "要点": "科技品采用受创新属性/不确定性影响，广告提供信息与可核实证据以降低采用焦虑",
        "papers": [11, 22, 23, 37],
    },
    "Theory:B2B工业品购买决策理论": {
        "name": "B2B工业品购买决策理论",
        "要点": "工业品依赖专业/理性采购决策，广告以性能/可靠/一致等买点支持集体采购评估",
        "papers": [4, 6, 9, 11, 17],
    },
}

# ---------------- concept-related-to ----------------
CONCEPT_REL = [
    ("Concept:科技品理性诉求(规格/数据)", "Concept:技术信息可核实性"),
    ("Concept:科技品理性诉求(规格/数据)", "Concept:科技品卷入度与诉求匹配"),
    ("Concept:科技品卷入度与诉求匹配", "Concept:认知负荷(技术堆砌)"),
    ("Concept:技术信息可核实性", "Concept:科技品广告合规(绝对化禁忌)"),
    ("Concept:权威/实测来源可信度", "Concept:专家信任(科研数据语言)"),
    ("Concept:科技品视觉隐喻/符号", "Concept:科技品理性诉求(规格/数据)"),
    ("Concept:应用证据(实测/案例)", "Concept:科技品牌沟通(新技术采用)"),
    ("Concept:B2B工业品诉求(性能/可靠/一致)", "Concept:应用证据(实测/案例)"),
    ("Concept:专家信任(科研数据语言)", "Concept:科技品视觉隐喻/符号"),
    ("Concept:科技品广告合规(绝对化禁忌)", "Concept:认知负荷(技术堆砌)"),
]

# ---------------- Build ----------------
entities = []
relations = []

pid = lambda n: f"Paper:OA-科技广告词-{n:03d}"

# Papers
for (n, title, year, cited, doi, note) in PAPERS:
    props = {
        "专业": "科技广告词",
        "年份": str(year),
        "被引": str(cited),
        "DOI": doi,
        "域": DOM,
        "置信度": "DB_REFERENCE",
        "说明": note,
    }
    src = ["https://doi.org/" + doi] if doi else [f"{title} ({year})"]
    entities.append({
        "id": pid(n), "type": "Paper", "name": title,
        "domains": [DOM], "props": props, "sources": src,
    })

# Concepts
for cid, c in CONCEPTS.items():
    entities.append({
        "id": cid, "type": "Concept", "name": c["name"],
        "domains": [DOM],
        "props": {"定义": c["定义"], "置信度": "LLM_INFERRED", "专业": "科技广告词"},
        "sources": [pid(p) for p in c["papers"]],
    })
    for p in c["papers"]:
        relations.append({"source": pid(p), "type": "paper-about", "target": cid, "domains": [DOM]})

# Methods
for mid, m in METHODS.items():
    entities.append({
        "id": mid, "type": "Method", "name": m["name"],
        "domains": [DOM],
        "props": {"要点": m["要点"], "置信度": "LLM_INFERRED", "专业": "科技广告词"},
        "sources": [pid(p) for p in m["papers"]],
    })
    for p in m["papers"]:
        relations.append({"source": pid(p), "type": "paper-proposes", "target": mid, "domains": [DOM]})

# Findings
for fid, f in FINDINGS.items():
    entities.append({
        "id": fid, "type": "Finding", "name": f["name"],
        "domains": [DOM],
        "props": {"结论": f["结论"], "置信度": "LLM_INFERRED"},
        "sources": [pid(p) for p in f["papers"]],
    })
    for p in f["papers"]:
        relations.append({"source": pid(p), "type": "paper-finds", "target": fid, "domains": [DOM]})
    for r in f["rules"]:
        relations.append({"source": fid, "type": "finding-evidence-for-rule", "target": r, "domains": [DOM]})

# Theories
for tid, t in THEORIES.items():
    entities.append({
        "id": tid, "type": "Theory", "name": t["name"],
        "domains": [DOM],
        "props": {"要点": t["要点"], "置信度": "LLM_INFERRED", "专业": "科技广告词"},
        "sources": [pid(p) for p in t["papers"]],
    })
    for p in t["papers"]:
        relations.append({"source": pid(p), "type": "paper-uses", "target": tid, "domains": [DOM]})

# method-supports-rule
METHOD_RULES = {
    "Method:内容分析法(科技/工业广告)": ["Rule:五层检查体系", "FailureLesson:文案白名单", "Rule:图文对位"],
    "Method:受众实验(诉求操纵·科技品)": ["Rule:五层检查体系", "Rule:概念先行"],
    "Method:来源可信度实验(权威/实测)": ["Rule:概念先行", "AudienceMode:EXP"],
    "Method:跨文化内容比较(B2B诉求)": ["Rule:五层检查体系"],
    "Method:文献综述/议程(科技广告研究)": ["Rule:五层检查体系"],
    "Method:问卷/实证调查(工业品采购)": ["Rule:图文对位", "FailureLesson:文案白名单"],
}
for mid, rules in METHOD_RULES.items():
    for r in rules:
        relations.append({"source": mid, "type": "method-supports-rule", "target": r, "domains": [DOM]})

# concept-related-to
for a, b in CONCEPT_REL:
    relations.append({"source": a, "type": "concept-related-to", "target": b, "domains": [DOM]})

kg = {
    "schema_version": "1.0",
    "pack": PACK,
    "role": ROLE,
    "dom": DOM,
    "entities": entities,
    "relations": relations,
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(kg, f, ensure_ascii=False, indent=2)

print("entities:", len(entities))
print("relations:", len(relations))
print("papers:", len(PAPERS), "concepts:", len(CONCEPTS), "methods:", len(METHODS),
      "findings:", len(FINDINGS), "theories:", len(THEORIES))
print("ratios: relations/entities =", round(len(relations) / len(entities), 2))
print("wrote", OUT)
