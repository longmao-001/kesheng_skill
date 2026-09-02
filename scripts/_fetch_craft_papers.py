# -*- coding: utf-8 -*-
"""arXiv 工艺类专业论文检索(镜头语言/视觉叙事/短视频/剪辑/注意力)"""
import io
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
NS = {"a": "http://www.w3.org/2005/Atom"}
TOPS = [
    ("镜头语言/摄影", 'all:"computational cinematography" OR all:"camera movement"'),
    ("视觉叙事/故事板", 'all:"visual storytelling" AND all:video'),
    ("新媒体/短视频", 'all:"short-form video" AND (all:engagement OR all:attention OR all:viral)'),
    ("剪辑/自动剪辑", 'all:"video editing" AND (all:automatic OR all:cinematic OR all:rhythm)'),
    ("注意力/视觉", 'all:"visual attention" AND (all:video OR all:advertisement)'),
]


def q(t, n=4):
    u = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": t, "start": 0, "max_results": n, "sortBy": "relevance"})
    d = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "kg/1.0"}), timeout=30).read().decode()
    r = ET.fromstring(d)
    for e in r.findall("a:entry", NS):
        i = (e.findtext("a:id", "", NS) or "").split("/abs/")[-1]
        ti = " ".join((e.findtext("a:title", "", NS) or "").split())
        yr = (e.findtext("a:published", "", NS) or "")[:4]
        print(f"{i} | {yr} | {ti[:95]}")


for dom, t in TOPS:
    print("==", dom, "==")
    try:
        q(t)
    except Exception as ex:
        print("ERR", repr(ex)[:90])
