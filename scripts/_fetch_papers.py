# -*- coding: utf-8 -*-
"""从 arXiv API 检索各域支撑论文, 提取元数据存 json (供图谱入库)"""
import io
import json
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

NS = {"a": "http://www.w3.org/2005/Atom", "ar": "http://arxiv.org/schemas/atom"}
TOPICS = [
    ("科学/光源", 'all:"laser-driven light source" OR all:"laser-sustained plasma"'),
    ("科学/量测", 'all:"semiconductor metrology" AND (all:scatterometry OR all:overlay OR all:ellipsometry)'),
    ("影像/视频生成", 'all:"text-to-video generation" AND (all:consistency OR all:prompt)'),
    ("工艺/多智能体", 'all:"multi-agent debate" OR all:"multi-agent collaboration" AND all:LLM'),
    ("叙事/科普传播", 'all:"science communication" AND all:video'),
    ("叙事/广告效果", 'all:"video advertising" AND (all:effectiveness OR all:attention)'),
]


def q(topic, n=4):
    u = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode({
        "search_query": topic, "start": 0, "max_results": n, "sortBy": "relevance"})
    req = urllib.request.Request(u, headers={"User-Agent": "kesheng-graph/1.0"})
    data = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    root = ET.fromstring(data)
    out = []
    for e in root.findall("a:entry", NS):
        eid = (e.findtext("a:id", default="", namespaces=NS) or "").strip()
        title = " ".join((e.findtext("a:title", default="", namespaces=NS) or "").split())
        summ = " ".join((e.findtext("a:summary", default="", namespaces=NS) or "").split())[:320]
        yr = (e.findtext("a:published", default="", namespaces=NS) or "")[:4]
        out.append({"id": eid, "title": title, "year": yr, "summary": summ})
    return out


result = []
for domain, t in TOPICS:
    try:
        papers = q(t)
        print(f"[{domain}] 命中 {len(papers)} 篇:")
        for p in papers:
            print("  -", p["id"].split("/abs/")[-1], p["year"], p["title"][:90])
            result.append({"domain": domain, **p})
    except Exception as ex:
        print(f"[{domain}] ERR {repr(ex)[:100]}")

with open(r"F:/AI/kesheng/runs/_tmp-papers.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)
print("saved", len(result), "papers -> F:/AI/kesheng/runs/_tmp-papers.json")
