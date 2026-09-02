# -*- coding: utf-8 -*-
"""重拉「灯光场景」专业(影视灯光/美术/场景方向), 回写清单 json"""
import io
import json
import sys
import urllib.parse
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
OA = "https://api.openalex.org/works"
TERMS = ["cinematic lighting", "stage lighting", "lighting design", "film colour",
         "color grading", "production design", "art direction", "set design",
         "scenography", "theatre lighting", "film lighting"]


def fetch(term, per=50):
    params = {"filter": f"title.search:{term}", "per-page": per, "sort": "cited_by_count:desc",
              "mailto": "kg@example.com", "select": "id,title,publication_year,cited_by_count,doi,type"}
    u = OA + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(u, headers={"User-Agent": "kg/1.0"})
    return json.loads(urllib.request.urlopen(req, timeout=40).read().decode("utf-8")).get("results", [])


got = {}
for t in TERMS:
    try:
        for w in fetch(t):
            if w.get("type") != "article" or not w.get("title"):
                continue
            oid = w["id"].rsplit("/", 1)[-1]
            if oid not in got:
                got[oid] = {"title": w["title"], "year": w.get("publication_year"),
                            "cited": w.get("cited_by_count") or 0,
                            "doi": (w.get("doi") or "").replace("https://doi.org/", "")}
    except Exception as ex:
        print(f"'{t}' ERR {repr(ex)[:60]}")
    if len(got) >= 50:
        break
papers = list(got.values())[:50]
print("灯光场景 重拉:", len(papers), "篇")
for p in papers[:8]:
    print("  -", p["title"][:70])

P = r"F:/AI/kesheng/runs/_tmp-discipline-papers.json"
g = json.load(open(P, encoding="utf-8"))
g["灯光场景"] = {"dom": "美术", "papers": papers}
json.dump(g, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("回写 json 完成")
