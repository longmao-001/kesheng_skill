# -*- coding: utf-8 -*-
"""按专业高精度检索文献(OpenAlex title.search) + 重建 papers-kg(清掉坏数据)"""
import io
import json
import sys
import urllib.parse
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

OA = "https://api.openalex.org/works"
DISC = [
    ("广告", "叙事", ["advertising", "advertisement", "ad campaign", "brand advertising", "commercial advertising"]),
    ("视频", "影像", ["video production", "video editing", "filmmaking", "film production", "video content"]),
    ("商业媒体", "产业", ["branded content", "commercial media", "advertising media", "brand communication", "media marketing"]),
    ("编剧", "叙事", ["screenwriting", "screenplay", "scriptwriting", "film narrative", "screenplay structure"]),
    ("导演", "导演", ["film director", "directorial", "auteur", "film directing", "film direction"]),
    ("摄影", "影像", ["cinematography", "cinematographer", "camera movement", "film camera", "cinematic"]),
    ("灯光场景", "美术", ["film lighting", "lighting design", "production design", "set design", "scene design"]),
    ("调度", "导演", ["mise-en-scene", "film staging", "blocking", "film choreography", "staging"]),
]


def fetch_title(term, per=50):
    params = {"filter": f"title.search:{term}", "per-page": per, "sort": "cited_by_count:desc",
              "mailto": "kg@example.com", "select": "id,title,publication_year,cited_by_count,doi,type"}
    u = OA + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(u, headers={"User-Agent": "kesheng-graph/1.0"})
    return json.loads(urllib.request.urlopen(req, timeout=40).read().decode("utf-8")).get("results", [])


out = {}
for prof, dom, terms in DISC:
    got = {}
    for t in terms:
        try:
            for w in fetch_title(t):
                if w.get("type") != "article" or not w.get("title"):
                    continue
                oid = w["id"].rsplit("/", 1)[-1]
                if oid not in got:
                    got[oid] = {"title": w["title"], "year": w.get("publication_year"),
                                "cited": w.get("cited_by_count") or 0,
                                "doi": (w.get("doi") or "").replace("https://doi.org/", "")}
        except Exception as ex:
            print(f"[{prof}] '{t}' ERR {repr(ex)[:70]}")
        if len(got) >= 50:
            break
    out[prof] = (dom, list(got.values())[:50])
    print(f"[{prof}] {len(out[prof][1])} 篇 | 样例: {out[prof][1][0]['title'][:70] if out[prof][1] else 'N/A'}")

with open(r"F:/AI/kesheng/runs/_tmp-discipline-papers.json", "w", encoding="utf-8") as f:
    json.dump({k: {"dom": v[0], "papers": v[1]} for k, v in out.items()}, f, ensure_ascii=False, indent=1)

# 重建 papers-kg: 清除旧 Paper:OA-* 与 PaperTopic:*, 保留手选 28 篇
P = r"F:/AI/kesheng/packs/papers-kg/kg.json"
g = json.load(open(P, encoding="utf-8-sig"))
g["entities"] = [e for e in g["entities"] if not (e["id"].startswith("Paper:OA-") or e["id"].startswith("PaperTopic:"))]
keep_ids = {e["id"] for e in g["entities"]}
g["relations"] = [r for r in g["relations"] if r["source"] in keep_ids and r["target"] in keep_ids]
ids = set(keep_ids)
KEYS = {(r["source"], r["target"], r["type"]) for r in g["relations"]}
HUB_REL = {"广告": "Rule:概念先行", "视频": "ProcessRule:单镜抽卡", "商业媒体": "Rule:AI原生交付原则",
           "编剧": "NarrationType:直白规格型", "导演": "Rule:概念先行", "摄影": "Rule:图文对位",
           "灯光场景": "Rule:图文对位", "调度": "Rule:图文对位"}
for prof, (dom, papers) in out.items():
    hub = f"PaperTopic:{prof}专业"
    g["entities"].append({"id": hub, "type": "PaperTopic", "name": f"{prof}专业文献",
                          "props": {"专业": prof, "规模": len(papers), "说明": "标题精确匹配+按被引排序(OpenAlex)"},
                          "sources": ["https://api.openalex.org/works"], "domains": [dom]})
    ids.add(hub)
    if HUB_REL.get(prof):
        g["relations"].append({"source": hub, "target": HUB_REL[prof], "type": "topic-supports", "props": {}})
    for i, p in enumerate(papers):
        pid = f"Paper:OA-{prof}-{i:03d}"
        g["entities"].append({"id": pid, "type": "Paper", "name": p["title"][:80],
                              "props": {"专业": prof, "年份": p["year"], "被引": p["cited"], "DOI": p["doi"]},
                              "sources": ["https://api.openalex.org/works"], "domains": [dom]})
        ids.add(pid)
        g["relations"].append({"source": pid, "target": hub, "type": "paper-in-topic", "props": {}})
json.dump(g, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("papers-kg 重建:", len(g["entities"]), "entities /", len(g["relations"]), "relations")
