# -*- coding: utf-8 -*-
"""Japanese-research-angle fetch for the film disciplines (user request: Japan researches
this a lot). Queries OpenAlex title.search for Japan/Japanese-cinema/anime-auteur/film
studies, filters to genuinely film-relevant, and writes runs/_tmp-discipline-papers-jp.json."""
import json, io, time, urllib.request, urllib.parse

OUT = r"F:/AI/kesheng/runs/_tmp-discipline-papers-jp.json"
MAILTO = "kesheng@example.com"

D = {
 "导演": {
   "dom": "导演",
   "queries": [
     "anime auteur", "anime director", "Miyazaki auteur", "Japanese cinema",
     "anime authorship", "contemporary anime director", "anime adaptation",
     "anime film studies", "Miyazaki Hayao", "Japanese film history",
   ],
   "include": ["anime", "miyazaki", "japanese cinema", "japanese film",
               "auteur", "japan", "hayao", "anime director"],
   "exclude": ["board", "medical", "corporate", "hospital"],
 },
 "摄影": {
   "dom": "影像",
   "queries": [
     "Japanese photography", "photography Japan culture",
     "Japanese photographic", "photography and Japan",
   ],
   "include": ["photography", "photographic", "japan"],
   "exclude": ["medical", "radiology", "microscopy", "surgical", "embryo",
               "optical sensor", "imaging technique"],
 },
 "灯光场景": {
   "dom": "美术",
   "queries": [
     "anime lighting design", "Japanese stage lighting", "lighting design Japan",
     "illumination design theatre Japan",
   ],
   "include": ["lighting", "illumination", "stage", "japan"],
   "exclude": ["led", "converter", "building", "energy", "daylight", "driver",
               "circadian", "street light"],
 },
 "视频": {
   "dom": "影像",
   "queries": [
     "anime production", "Japanese animation", "anime industry",
     "anime cultural", "animated film Japan",
   ],
   "include": ["anime", "animation", "animated film", "japan"],
   "exclude": ["surgery", "medical", "video game", "coding", "compression",
               "surveillance", "vats", "epilepsy"],
 },
}

def fetch(query):
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode({
        "filter": f"title.search:{query}",
        "per-page": "40",
        "mailto": MAILTO,
    })
    req = urllib.request.Request(url, headers={"User-Agent": "kesheng-skill/1.0"})
    last = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            last = e
            if e.code == 429:
                time.sleep(2.0 * (attempt + 1))  # backoff on rate limit
                continue
            raise
    raise last

def low(s): return s.lower()

out = {}
for disc, cfg in D.items():
    papers, seen = [], set()
    for q in cfg["queries"]:
        try:
            data = fetch(q)
        except Exception as e:
            print(f"[{disc}] query '{q}' FAILED: {e}")
            continue
        for w in data.get("results", []):
            t = (w.get("title") or "").strip()
            if not t:
                continue
            lt = low(t)
            if lt in seen:
                continue
            if any(e in lt for e in cfg["exclude"]):
                continue
            if not any(i in lt for i in cfg["include"]):
                continue
            seen.add(lt)
            doi = (w.get("doi") or "").replace("https://doi.org/", "")
            papers.append({"title": t, "year": w.get("publication_year"),
                           "cited": w.get("cited_by_count", 0), "doi": doi})
        time.sleep(1.2)
    out[disc] = {"dom": cfg["dom"], "papers": papers}
    print(f"{disc}: fetched {len(papers)} clean papers")

json.dump(out, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\nwritten ->", OUT)
