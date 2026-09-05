# -*- coding: utf-8 -*-
"""Tight-curate ad-copy to ~55 strong, category-balanced candidates."""
import json, io
from collections import Counter

SRC = r"F:/AI/kesheng/runs/_tmp-adcopy-papers.json"
OUT = r"F:/AI/kesheng/runs/candidates-wenan-top.json"
data = json.load(io.open(SRC, encoding="utf-8-sig"))

NEG = ["jingle", "market values of firms", "brand extension prime", "yachting", "airline",
       "cosmetics", "parents children", "maker", "case frame", "word vector", "generator",
       "organon model", "illocutionary", "catalog", "membership", "buhler", "intercultural",
       "phraseological", "web", "medium", "sponsorship", "sports", "spectator",
       "mobile", "sms", "payment", "social media advertising", "sponsored", "targeting",
       "platform", "licensing", "wireless", "assisted reproductive", "stem cell",
       "pharmac", "tobacco", "smok", "quitline", "political", "candidate", "gender-role",
       "sexual", "reproductive", "covid", "charity", "donation", "media campaign",
       "public service", "hygiene", "cancer", "alcohol", "diet", "health claims nutrition",
       "food safety", "insecure", "purchase organic", "sustainable surplus", "wine",
       "legislation", "government", "children television disclaimer", "alleged",
       "ban", "impression", "measure", "school", "tourism sustainable",
       "designing brand equity", "made-in", "vacation", "highly recalled",
]
KEEP = ["slogan", "advertising language", "advertising english", "copy", "advertis",
        "persuasion", "rhetor", "message", "appeal", "commercial", "food advertis",
        "video advertise", "advertising video", "televis advert", "rational", "emotional",
        "metadiscourse", "headline", "consumer attitude", "brand equity advertising",
        "advert creative", "viral"]

def low(s): return s.lower()

best = []  # (score, disc, paper)
prime = ["slogan", "advertising language", "persuasion", "rhetor", "appeal", "rational", "emotional",
         "video advert", "advertising video", "advertising copy", "metadiscourse", "advert message"]
for disc, v in data.items():
    for p in v["papers"]:
        t = p["title"]; lt = low(t)
        if any(n in lt for n in NEG):
            continue
        if not any(k in lt for k in KEEP):
            continue
        sc = sum(1 for k in prime if k in lt) * 2 + (10 if p.get("cited", 0) > 30 else (5 if p.get("cited", 0) > 10 else 0))
        best.append((sc, disc, p))

best.sort(key=lambda x: -x[0])
seen = set(); ok = []
for sc, disc, p in best:
    if low(p["title"]) in seen:
        continue
    seen.add(low(p["title"]))
    p = dict(p); p["disc"] = disc
    ok.append(p)
# ensure category balance: keep top ~55
sel = ok[:55]
json.dump({"dom": "叙事", "papers": sel},
          io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("picked", len(sel), "of", len(ok))
print("category mix:", Counter(p["disc"] for p in sel))
for p in sel[:30]:
    print(f"  [{p['disc']}][{p['year']}]{p['title'][:66]}")
