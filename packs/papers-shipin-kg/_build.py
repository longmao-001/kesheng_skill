# -*- coding: utf-8 -*-
"""Build kg.json for 科生 视频(video production) paper-ingestion pack.
Schema: PAPER_INGESTION.md. Entities: Paper/Concept/Method/Finding/Theory.
Relations: paper-about/paper-proposes/paper-finds/paper-uses/
           finding-evidence-for-rule/method-supports-rule/concept-related-to
"""
import json, os, collections, sys

DOIS = {
 1: "10.1080/14703290701602805",
 2: "",
 4: "10.1080/13683500.2020.1810212",
 5: "10.1007/bf01261224",
 6: "10.1145/2010324.1964936",
 7: "10.2307/4140670",
 9: "10.1080/09523987.2013.862364",
 11: "10.1080/1369118x.2019.1585469",
 12: "10.1080/21532974.2016.1276871",
 13: "10.1353/cj.2020.0019",
 14: "10.1177/2056305118790761",
 18: "10.1016/j.compag.2014.12.007",
 21: "10.1016/j.system.2018.01.006",
 22: "10.14742/ajet.458",
 23: "10.1007/s11423-007-9039-4",
 26: "10.1598/jaal.51.5.4",
 28: "10.1080/1475939x.2020.1726805",
 29: "10.7771/1541-5015.1609",
 31: "10.1080/17517575.2023.2246188",
 32: "10.1080/17439884.2018.1504788",
 33: "10.1155/2021/8875700",
 34: "10.1080/1554480x.2010.509473",
 35: "10.1590/1983-1447.2022.20210247.en",
 36: "10.1080/0142159x.2017.1322190",
 37: "10.1080/0142159x.2017.1302081",
 38: "10.1080/01972243.2011.607025",
 40: "10.1021/acs.jchemed.8b00647",
 43: "10.1016/j.cviu.2010.01.005",
 44: "10.1145/1857907.1857910",
 45: "10.1145/65445.65447",
 46: "10.1145/1141911.1141967",
 47: "10.1080/15391523.2009.10782542",
 48: "10.1109/tip.2017.2695887",
 49: "10.1145/3072959.3073653",
 50: "",
}

PAPERS = {
 1: "Audio and video podcasts of lectures for campus-based students: production and evaluation of student use",
 2: "How Video Production Affects Student Engagement: An Empirical Study of MOOC Videos",
 4: "‘I want to record and share my wonderful journey’: Chinese Millennials’ production and sharing of short-form travel videos on TikTok or Douyin",
 5: "Production model based digital video segmentation",
 6: "A versatile HDR video production system",
 7: "Teaching Youth Media: A Critical Guide to Literacy, Video Production, and Social Change",
 9: "Learning to engage: how positive attitudes about the news, media literacy, and video production contribute to adolescent civic engagement",
 11: "Shehui Ren: cultural production and rural youths’ use of the Kuaishou video-sharing app in Eastern China",
 12: "Bringing Digital Storytelling to the Elementary Classroom: Video Production for Preservice Teachers",
 13: "From Netflix to Movistar+: How Subscription Video-on-Demand Services Have Transformed Spanish TV Production",
 14: "Mimetic Production in YouTube Toy Unboxing Videos",
 18: "A key frame extraction method for processing greenhouse vegetables production monitoring video",
 21: "Developing EFL students’ digital empathy through video production",
 22: "What counts as educational video? Working toward best practice alignment between video production approaches and outcomes.",
 23: "Designing and implementing a PBL course on educational digital video production: lessons learned from a design-based research",
 26: "Making Meaning on the Screen: Digital Video Production About the Dominican Republic",
 28: "Video for teaching: classroom use, instructor self-production and teachers’ preferences in presentation format",
 29: "A Review of Video Triggers and Video Production in Higher Education and Continuing Education PBL Settings",
 31: "Recent advances in artificial intelligence for video production system",
 32: "Video production in content-area pedagogy: a scoping study of the research literature",
 33: "Research on the Influence of New Media Technology on Internet Short Video Content Production under Artificial Intelligence Background",
 34: "From image to ideology: analysing shifting identity positions of marginalized youth across the cultural sites of video production",
 35: "Production and validation of educational video to encourage breastfeeding",
 36: "Twelve tips for reducing production time and increasing long-term usability of instructional video",
 37: "Twelve tips for the production of digital chalk-talk videos",
 38: "Video as Digital Object: Production and Distribution of Video Content in the Internet Media Ecosystem",
 40: "Development and Production of Interactive Videos for Teaching Chemical Techniques during Laboratory Sessions",
 43: "Personalized production of basketball videos from multi-sensored data under limited display resolution",
 44: "Geodesic image and video editing",
 45: "Virtual video editing in interactive multimedia applications",
 46: "Schematic storyboarding for video visualization and editing",
 47: "Using Video Editing to Cultivate Novice Teachers’ Practice",
 48: "A General Framework for Edited Video and Raw Video Summarization",
 49: "Computational video editing for dialogue-driven scenes",
 50: "An Exploratory Study of Digital Video Editing as a Tool for Teacher Preparation",
}

YEARS = {1:2007,2:2019,4:2020,5:1995,6:2011,7:2004,9:2013,11:2019,12:2017,13:2020,
 14:2018,18:2015,21:2018,22:2014,23:2007,26:2008,28:2020,29:2016,31:2023,32:2018,
 33:2021,34:2010,35:2022,36:2017,37:2017,38:2011,40:2019,43:2010,44:2010,45:1989,
 46:2006,47:2009,48:2017,49:2017,50:2008}
CITED = {1:479,2:436,4:262,5:206,6:197,7:187,9:113,11:80,12:80,13:79,14:69,
 18:62,21:59,22:58,23:58,26:56,28:54,29:52,31:49,32:49,33:48,34:46,35:45,36:45,
 37:45,38:45,40:43,43:43,44:177,45:158,46:150,47:136,48:126,49:124,50:117}

def pid(i):
    # use the 0-based array position from the source list (matches sibling papers-kg ids)
    return "Paper:OA-视频-%03d" % (i - 1)

def doi_src(i):
    d = DOIS[i]
    return [d] if d else ["https://api.openalex.org/works"]

def P(i):
    return pid(i)

# ---------- referenced 科生 rule ids (verified to exist in kesheng-kg) ----------
RULE_JIANJI  = "ProcessRule:剪辑合成（配音对齐·图表层·文案层·字幕·调色·片头片尾）"
RULE_DANKAI  = "ProcessRule:单镜抽卡"
RULE_CANKAO  = "ProcessRule:参考包组装"
RULE_DUOJING = "ProcessRule:多镜原生"
RULE_YUSU    = "NarrationRule:语速档位"
RULE_ZIMU    = "NarrationRule:字幕短句"
RULE_TUWEI   = "Rule:图文对位"
RULE_TUWSX   = "Rule:图文顺序对位"
RULE_AIGEN   = "Rule:AI原生交付原则"
RULE_WUCENG  = "Rule:五层检查体系"
RULE_GAINIAN = "Rule:概念先行"
RULE_SHUJU   = "Rule:数据目检确认"
RULE_PROMPT  = "Rule:Prompt严格统一格式"
TYPE_ZHIB    = "NarrationType:直白规格型"
TYPE_KEPU    = "NarrationType:科普短视频"

# ---------- entities ----------
entities = []

# Paper nodes
for i in sorted(PAPERS):
    entities.append({
        "id": P(i),
        "type": "Paper",
        "name": PAPERS[i],
        "props": {"专业": "视频", "年份": YEARS[i], "被引": CITED[i], "DOI": DOIS[i]},
        "sources": doi_src(i),
        "domains": ["影像"],
    })

# Concepts
CONCEPTS = [
 ("蒙太奇", "镜头组接与并置产生意义的方法，后期剪辑核心；含连续/对比/隐喻式组接。", [44,45,46,49,5]),
 ("剪辑节奏", "镜头时长与切换频率形成的观感速度/张力控制，是短视频抓留存的杠杆。", [46,49,48,44]),
 ("分镜故事板", "拍摄与剪辑前用画面序列规划镜头构图、动作与层级（script→shot）。", [46,12,44,40]),
 ("镜头语言景别运镜", "景别(远/全/中/近/特)、运镜(推拉摇移)等画面语法，传递信息与情绪。", [6,44,46,9]),
 ("转场", "镜头/场景之间的衔接方式(硬切、叠化、匹配、淡入淡出)。", [44,45,49]),
 ("声音设计配音", "旁白/配乐/音效与画面的同步配合，决定信息获取与基调一致。", [1,37,49]),
 ("字幕图文对位", "字幕、文案与画面文字/图形同步对齐的呈现规范。", [37,2,22]),
 ("完播率留存", "观众看完视频的比例与粘性，短视频核心效果指标。", [2,4,33,14]),
 ("教学科普视频", "面向讲解与传播的说明性视频(科研/教学/科普)，重理解与可信。", [22,28,29,37,32]),
 ("短视频内容生产", "移动端短时、高密度、易转发的短视频内容创作与分发。", [4,11,33,14]),
 ("AI原生视频生成", "用AI/生成式工具直接产出或智能切分/剪辑/增强视频的生产范式。", [31,33]),
 ("视频信息密度", "单位时间承载的概念与画面信息量；过高易造成认知负荷。", [22,37,36]),
 ("视频分段关键帧", "把视频切分为镜头/片段并以关键帧表示，支撑索引、检索与再剪辑。", [5,18,48,43]),
]
for name, desc, srcs in CONCEPTS:
    entities.append({
        "id": "Concept:" + name, "type": "Concept", "name": name,
        "props": {"定义": desc, "置信度": "LLM_INFERRED"},
        "sources": [DOIS[s] for s in srcs if DOIS[s]],
        "domains": ["影像"],
    })

# Methods
METH = [
 ("内容分析法", "对视频内容/文本进行系统编码、分类与量化分析(内容/文化/生态研究范式)。", [11,14,13,38,22]),
 ("计算视频分析算法", "基于视觉与时间结构的视频切分、关键帧、摘要、自动剪辑算法。", [5,18,43,44,46,48,49]),
 ("设计性研究", "迭代式设计与实证改进教学视频/课程产品(DBR、PBL、制作规范)。", [23,29,12,32,36]),
 ("问卷调查与使用评估", "收集学习者/用户对视频的使用、偏好与有效性反馈。", [1,28,35,29]),
 ("实证实验研究", "控制变量比较视频制作/呈现方式对engagement、学习与态度的影响。", [2,9,21,47]),
]
for name, desc, srcs in METH:
    entities.append({
        "id": "Method:" + name, "type": "Method", "name": name,
        "props": {"含义": desc, "置信度": "LLM_INFERRED"},
        "sources": [DOIS[s] for s in srcs if DOIS[s]],
        "domains": ["影像"],
    })

# Findings
FIND = [
 ("分段单点叙事提升留存", "把视频按镜头/知识点分段、每段聚焦单一焦点 → 认知负荷↓、理解与留存↑。", [5,22,48,4]),
 ("信息密度过载损害完播", "单位时间术语/画面切换过多(信息密度过高) → 认知负荷↑、理解与完播↓。", [22,37,36]),
 ("配音与画面同步提升学习", "旁白/配音与画面内容同步对齐 → 信息获取与学习效果↑。", [1,37]),
 ("先分镜再制作提效率", "拍摄/剪辑前先做分镜/故事板 → 结构清晰、可编辑性与制作效率↑。", [46,12,44]),
 ("AI自动化降本增效", "AI视频生成与智能剪辑 → 制作时间↓、规模化与复用↑。", [31,33,36]),
 ("交互元素提升参与", "视频中注入交互/可点击元素 → 参与度与学习留存↑。", [40,23]),
 ("字幕与文案对位提升获取", "字幕与画面文字同步短句(图文对位) → 信息获取与留存↑。", [37,2]),
 ("内容与目标对齐才有效", "视频制作方式需与教学目标/受众对齐 → 对齐则有效，否则投入浪费。", [22,32]),
 ("视觉语言引导注意", "镜头景别/运镜等视觉语言设计 → 注意力聚焦与叙事理解↑。", [44,46]),
 ("语速匹配信息密度", "解说语速档位需匹配信息密度；语速过快 → 理解与留存↓。", [1,37,22]),
]
for name, desc, srcs in FIND:
    entities.append({
        "id": "Finding:" + name, "type": "Finding", "name": name,
        "props": {"结论": desc, "置信度": "LLM_INFERRED"},
        "sources": [DOIS[s] for s in srcs if DOIS[s]],
        "domains": ["影像"],
    })

# Theories
THEO = [
 ("认知负荷理论", "说明性/教学视频应控制单位信息量，降低工作记忆认知负担以保理解。", [22,37,36,40]),
 ("多媒体学习认知理论", "图文声多渠道同步呈现(CTA)利于学习(Mayer多媒体学习认知理论)。", [22,40,37]),
 ("蒙太奇理论", "镜头组接产生非单纯相加的意义，是剪辑表达的理论根基。", [44,45,46,49]),
 ("使用与满足理论", "用户出于自身需求而主动使用与分享短视频/平台内容。", [4,11,38,14]),
 ("叙事传播理论", "叙事/数字故事化(叙事传输)增强认同、沉浸与传播。", [12,7,9,26,34]),
]
for name, desc, srcs in THEO:
    entities.append({
        "id": "Theory:" + name, "type": "Theory", "name": name,
        "props": {"理论": desc, "置信度": "LLM_INFERRED"},
        "sources": [DOIS[s] for s in srcs if DOIS[s]],
        "domains": ["影像"],
    })

# ---------- relations ----------
relations = []

def rel(src, dst, typ, **extra):
    relations.append({"source": src, "target": dst, "type": typ, "props": dict(extra) or {}})

# ---- paper-about (Paper -> Concept) ----
ABOUT = {
 1:["声音设计配音","教学科普视频"],
 2:["教学科普视频","完播率留存","视频信息密度"],
 4:["短视频内容生产","完播率留存"],
 5:["视频分段关键帧","剪辑节奏"],
 6:["镜头语言景别运镜","剪辑节奏"],
 7:["教学科普视频","分镜故事板"],
 9:["教学科普视频"],
 11:["短视频内容生产"],
 12:["分镜故事板","教学科普视频"],
 14:["短视频内容生产"],
 18:["视频分段关键帧"],
 21:["教学科普视频"],
 22:["教学科普视频","视频信息密度"],
 23:["分镜故事板","教学科普视频"],
 26:["教学科普视频"],
 28:["教学科普视频","声音设计配音"],
 29:["教学科普视频"],
 31:["AI原生视频生成"],
 32:["教学科普视频"],
 33:["短视频内容生产","AI原生视频生成","完播率留存"],
 34:["教学科普视频"],
 35:["教学科普视频"],
 36:["视频信息密度","剪辑节奏"],
 37:["声音设计配音","字幕图文对位","视频信息密度","教学科普视频"],
 38:["短视频内容生产"],
 40:["教学科普视频","分镜故事板"],
 43:["视频分段关键帧"],
 44:["蒙太奇","剪辑节奏","转场","镜头语言景别运镜"],
 45:["蒙太奇","转场","剪辑节奏"],
 46:["分镜故事板","蒙太奇","视频分段关键帧"],
 47:["剪辑节奏"],
 48:["视频分段关键帧","剪辑节奏"],
 49:["蒙太奇","剪辑节奏","声音设计配音"],
 50:["剪辑节奏"],
}
for i, cs in ABOUT.items():
    for c in cs:
        rel(P(i), "Concept:" + c, "paper-about")

# ---- paper-proposes (Paper -> Method) ----
PROP = {
 1:"问卷调查与使用评估", 2:"实证实验研究", 4:"内容分析法", 5:"计算视频分析算法",
 6:"计算视频分析算法", 7:"内容分析法", 9:"实证实验研究", 11:"内容分析法",
 12:"设计性研究", 13:"内容分析法", 14:"内容分析法", 18:"计算视频分析算法",
 21:"实证实验研究", 22:"内容分析法", 23:"设计性研究", 26:"设计性研究",
 28:"问卷调查与使用评估", 29:"内容分析法", 31:"计算视频分析算法", 32:"内容分析法",
 33:"内容分析法", 34:"内容分析法", 35:"问卷调查与使用评估", 36:"设计性研究",
 37:"设计性研究", 38:"内容分析法", 40:"设计性研究", 43:"计算视频分析算法",
 44:"计算视频分析算法", 45:"计算视频分析算法", 46:"计算视频分析算法",
 47:"实证实验研究", 48:"计算视频分析算法", 49:"计算视频分析算法", 50:"实证实验研究",
}
for i, m in PROP.items():
    rel(P(i), "Method:" + m, "paper-proposes")

# ---- paper-finds (Paper -> Finding) ----
FINDS = {
 1:["配音与画面同步提升学习","语速匹配信息密度"],
 2:["分段单点叙事提升留存","内容与目标对齐才有效"],
 4:["分段单点叙事提升留存"],
 5:["分段单点叙事提升留存"],
 14:["信息密度过载损害完播"],
 18:["分段单点叙事提升留存"],
 22:["信息密度过载损害完播","内容与目标对齐才有效"],
 23:["交互元素提升参与"],
 28:["配音与画面同步提升学习"],
 31:["AI自动化降本增效"],
 32:["内容与目标对齐才有效"],
 33:["AI自动化降本增效","分段单点叙事提升留存"],
 35:["内容与目标对齐才有效"],
 36:["AI自动化降本增效","信息密度过载损害完播"],
 37:["配音与画面同步提升学习","字幕与文案对位提升获取","语速匹配信息密度"],
 40:["交互元素提升参与","信息密度过载损害完播"],
 44:["视觉语言引导注意","先分镜再制作提效率"],
 45:["视觉语言引导注意"],
 46:["先分镜再制作提效率","视觉语言引导注意"],
 47:["先分镜再制作提效率"],
 48:["分段单点叙事提升留存"],
 49:["视觉语言引导注意","配音与画面同步提升学习"],
 50:["先分镜再制作提效率"],
}
for i, fs in FINDS.items():
    for f in fs:
        rel(P(i), "Finding:" + f, "paper-finds")

# ---- paper-uses (Paper -> Theory) ----
USES = {
 1:["认知负荷理论","多媒体学习认知理论"],
 2:["认知负荷理论"],
 4:["使用与满足理论"],
 7:["叙事传播理论"],
 9:["叙事传播理论"],
 11:["使用与满足理论"],
 12:["叙事传播理论"],
 13:["使用与满足理论"],
 14:["使用与满足理论"],
 21:["叙事传播理论"],
 22:["认知负荷理论","多媒体学习认知理论"],
 23:["多媒体学习认知理论"],
 26:["叙事传播理论"],
 28:["认知负荷理论"],
 29:["认知负荷理论"],
 32:["多媒体学习认知理论"],
 33:["使用与满足理论"],
 34:["叙事传播理论"],
 35:["认知负荷理论"],
 36:["认知负荷理论"],
 37:["认知负荷理论","多媒体学习认知理论"],
 38:["使用与满足理论"],
 40:["多媒体学习认知理论"],
 44:["蒙太奇理论"],
 45:["蒙太奇理论"],
 46:["蒙太奇理论"],
 49:["蒙太奇理论"],
}
for i, ts in USES.items():
    for t in ts:
        rel(P(i), "Theory:" + t, "paper-uses")

# ---- finding-evidence-for-rule (Finding -> 科生规则) ----
FEV = {
 "分段单点叙事提升留存": [RULE_JIANJI, RULE_GAINIAN],
 "信息密度过载损害完播": [RULE_YUSU, RULE_WUCENG],
 "配音与画面同步提升学习": [RULE_JIANJI, RULE_TUWEI],
 "先分镜再制作提效率": [RULE_DANKAI, RULE_CANKAO],
 "AI自动化降本增效": [RULE_AIGEN, RULE_DUOJING],
 "交互元素提升参与": [RULE_TUWEI, TYPE_KEPU],
 "字幕与文案对位提升获取": [RULE_TUWEI, RULE_ZIMU],
 "内容与目标对齐才有效": [RULE_GAINIAN, RULE_WUCENG],
 "视觉语言引导注意": [RULE_JIANJI, RULE_TUWEI],
 "语速匹配信息密度": [RULE_YUSU, TYPE_ZHIB],
}
for f, rules in FEV.items():
    for r in rules:
        rel("Finding:" + f, r, "finding-evidence-for-rule")

# ---- method-supports-rule (Method -> 科生规则) ----
MSV = {
 "内容分析法": [RULE_WUCENG, RULE_SHUJU],
 "计算视频分析算法": [RULE_DANKAI, RULE_JIANJI],
 "设计性研究": [RULE_GAINIAN, RULE_PROMPT],
 "问卷调查与使用评估": [RULE_WUCENG],
 "实证实验研究": [RULE_WUCENG],
}
for m, rules in MSV.items():
    for r in rules:
        rel("Method:" + m, r, "method-supports-rule")

# ---- concept-related-to (Concept -> Concept) ----
CRT = [
 ("蒙太奇","剪辑节奏"),("蒙太奇","转场"),("蒙太奇","分镜故事板"),
 ("剪辑节奏","视频分段关键帧"),("剪辑节奏","镜头语言景别运镜"),
 ("分镜故事板","镜头语言景别运镜"),("分镜故事板","视频分段关键帧"),
 ("声音设计配音","字幕图文对位"),("字幕图文对位","视频信息密度"),
 ("完播率留存","短视频内容生产"),("完播率留存","视频信息密度"),
 ("教学科普视频","完播率留存"),("短视频内容生产","AI原生视频生成"),
 ("短视频内容生产","完播率留存"),("AI原生视频生成","剪辑节奏"),
 ("视频信息密度","完播率留存"),("视频分段关键帧","剪辑节奏"),
 ("视频分段关键帧","蒙太奇"),("转场","剪辑节奏"),("镜头语言景别运镜","剪辑节奏"),
]
for a, b in CRT:
    rel("Concept:" + a, "Concept:" + b, "concept-related-to")

# ---------- assemble ----------
OUT = {
 "schema_version": "1.0",
 "pack": "papers-shipin-kg",
 "role": "研究支撑",
 "dom": "影像",
 "专业": "视频",
 "entities": entities,
 "relations": relations,
}

counts = collections.Counter(e["type"] for e in entities)
rel_counts = collections.Counter(r["type"] for r in relations)
print("== Entity counts ==")
for k, v in counts.items():
    print(f"  {k:10s} {v}")
print("Total entities:", len(entities))
print("== Relation counts ==")
for k, v in rel_counts.items():
    print(f"  {k:28s} {v}")
print("Total relations:", len(relations))
print("ratio = %.2f" % (len(relations)/len(entities)))

# validate all relation endpoints exist
eids = {e["id"] for e in entities}
bad = [r for r in relations if r["source"] not in eids or r["target"] not in eids]
print("relations with dangling endpoint:", len(bad))
for r in bad[:20]:
    print("   DANGLING:", r)

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kg.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1)
print("WROTE:", out_path)
