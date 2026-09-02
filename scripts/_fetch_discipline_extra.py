# -*- coding: utf-8 -*-
"""Supplementary precise fetch for the weak disciplines (导演/摄影/灯光场景/视频).
Queries OpenAlex title.search with discipline-specific film terms, merges+dedupes,
then filters to genuinely-relevant film/cinema papers. Writes a clean augmented list."""
import json, io, time, urllib.request, urllib.parse

OUT = r"F:/AI/kesheng/runs/_tmp-discipline-papers-extra.json"
MAILTO = "kesheng@example.com"

# discipline -> {dom, queries, include, exclude}
D = {
 "导演": {
   "dom": "导演",
   "queries": [
     "auteur theory", "auteur", "film director", "directorial style",
     "film authorship", "cinema director", "auteurism",
   ],
   "include": ["auteur", "film director", "directorial", "cinema director",
               "filmmaker", "directing", "film authorship", "movie director",
               "director of photography", "director's", "directors'"],
   "exclude": ["board of directors", "medical director", "executive director",
               "managing director", "clinical director", "corporate", "hospital",
               "liquid crystal", "metalation", "nursing", "pharmacy", "chief executive",
               "nonprofit", "board members", "corporate governance", "ceo", "cfo",
               "school director", "sports director", "athletic director",
               "funeral director", "music director of", "choir director",
               "orchestra", "band director"],
 },
 "摄影": {
   "dom": "影像",
   "queries": [
     "cinematography", "digital cinematography", "camera movement film",
     "cinematographer", "film style cinematography", "cinematic camera",
     "camera work film", "cinematographic style",
   ],
   "include": ["cinematography", "cinematographer", "camera movement",
               "camera work", "cinematic camera", "film style", "steadicam",
               "tracking shot", "shot composition", "cinematographic style",
               "camera operator", "lens", "visual style film"],
   "exclude": ["cinematographic analysis of", "embryo", "sperm", "oocyte",
               "biomechanic", "gait", "walking", "pitching", "throwing",
               "particle image velocimetry", "piv", "cavitation", "jet",
               "vertebra", "cervical", "kinematic", "motion capture of",
               "biomedical", "cell", "microscopy", "radiology", "ultrasound",
               "surgical", "endoscopic"],
 },
 "灯光场景": {
   "dom": "美术",
   "queries": [
     "three-point lighting", "low-key lighting", "high-key lighting",
     "chiaroscuro", "film noir lighting", "lighting design theatre",
     "cinematic lighting", "lighting for film", "color grading film",
     "stage lighting design", "dramatic lighting",
   ],
   "include": ["three-point lighting", "low-key", "high-key", "chiaroscuro",
               "film noir", "lighting design", "cinematic lighting",
               "lighting for film", "color grading", "colour grading",
               "stage lighting", "dramatic lighting", "lighting technique",
               "lighting and", "lighting in", "lighting to", "lighting for"],
   "exclude": ["led", "converter", "ballast", "flyback", "photovoltaic",
               "street light", "building", "daylight", "circadian",
               "horticultur", "tomato", "lettuce", "petunia", "greenhouse",
               "light-emitting", "pfc", "driver", "energy", "solar", "squid",
               "semiconductor", "optical", "photonics", "laser"],
 },
 "视频": {
   "dom": "影像",
   "queries": [
     "short video marketing", "short-form video", "online video advertising",
     "educational video learning", "instructional video", "video storytelling",
     "branded video content", "video content marketing",
   ],
   "include": ["short video", "short-form", "video marketing", "video advertising",
               "educational video", "instructional video", "video storytelling",
               "branded video", "video content", "online video", "vlog",
               "video learning", "video and", "video in", "video for"],
   "exclude": ["vats", "lobectomy", "thorac", "epilepsy", "il-6", "bone marrow",
               "video game", "gaming", "crowdfunding", "video-eeG", "endoscopy",
               "surgery", "laparoscopic", "radiotherapy", "video laryngoscopy",
               "videofluor", "surveillance video", "video surveillance",
               "forensic video", "video coding", "video compression", "hevc",
               "mpeg", "codec", "video quality assessment", "video streaming",
               "videoconferenc", "video conferenc", "video capsule"],
 },
}

def fetch(query):
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode({
        "filter": f"title.search:{query}",
        "per-page": "40",
        "mailto": MAILTO,
    })
    req = urllib.request.Request(url, headers={"User-Agent": "kesheng-skill/1.0"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8"))

def low(s):
    return s.lower()

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
            key = low(t)
            if key in seen:
                continue
            lt = key
            if any(e in lt for e in cfg["exclude"]):
                continue
            if not any(i in lt for i in cfg["include"]):
                continue
            seen.add(key)
            doi = (w.get("doi") or "").replace("https://doi.org/", "")
            papers.append({
                "title": t,
                "year": w.get("publication_year"),
                "cited": w.get("cited_by_count", 0),
                "doi": doi,
            })
        time.sleep(0.2)
    out[disc] = {"dom": cfg["dom"], "papers": papers}
    print(f"{disc}: fetched {len(papers)} clean papers")

json.dump(out, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\nwritten ->", OUT)
