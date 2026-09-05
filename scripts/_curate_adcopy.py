# -*- coding: utf-8 -*-
"""Curate ad-copy papers from the raw fetch into a clean candidate list per category."""
import json, io

SRC = r"F:/AI/kesheng/runs/_tmp-adcopy-papers.json"
OUT = r"F:/AI/kesheng/runs/candidates-wenan.json"

data = json.load(io.open(SRC, encoding="utf-8-sig"))

# off-topic drops
NEG = ["mobile advertising", "mobile payment", "sms", "social media advertising", "sponsored",
       "targeting technology", "media platforms", "technology licensing", "wireless",
       "assisted reproductive", "stem cell", "genetic", "clinical", "pharmaceutical",
       "tobacco", "smok", "quitline", "political", "candidate", "gender-role", "sexual imagery",
       "television set", "dream machine", "teachers and computer", "travel 2.0", "eye-tracking",
       "payment", "baby boomer", "app", "algorithm", "groupware", "library", "libguide",
       "recruitment", "pyramid", "energy", "gmo", "obesity epidemiology", "food insecurity",
       "organic food purchase", "sustainable food", "wine", "cigarette", "cannabis",
       "prize", "health claims nutrition", "children and television advert disclaimer",
       "disclaimer nutrition", "content analysis islamic", "indian children food",
       "consumer weight", "functional foods body", "organic food face",
       "surplus food", "government", "census", "measure", "school", "university",
       "jingle jungle music mnemonic", "brand extension prime", "market values of firms",
       "firms", "stock", "brand equity designing", "made-in", "vacation", "jubilee",
       "influencer", "celebrity", "before-after", "violence", "anxiety", "depression",
       "self-harm", "covid", "pandemic", "waste", "donation", "charity", "event study",
       "media campaign", "public service", "social marketing", "hygiene", "cancer",
       "alcohol", "cigarette", "fast fashion", "sustainability advertisement", "environment",
       "green advertising", "climate", "value", "auction", "price", "sales promotion",
       "store", "retail price", "coupon", "framing sustainable", "message framing disposal",
       "reduce food", "taste", "sodium", "sugar content", "nutrition study",
]
def low(s): return s.lower()

# keep only ad-copy/advertising-language/slogan/appeal/video-advertising papers
KEEP = ["slogan", "tagline", "advertising language", "advertising english", "copy",
        "advertising appeal", "advertising slogan", "advertis", "commercial",
        "persuasion", "rhetoric", "message", "appeal", "food advert", "rational", "emotional",
        "video advertise", "advertising video", "televis", "television advert",
        "advert creativity", "headline", "metadiscourse", "rhetorical"]

out = {}
seen_all = set()
for disc, v in data.items():
    keep = []
    for p in v["papers"]:
        t = p["title"]; lt = low(t)
        if any(n in lt for n in NEG):
            continue
        if not any(k in lt for k in KEEP):
            continue
        if lt in seen_all:
            continue
        seen_all.add(lt)
        keep.append(p)
    out[disc] = {"dom": "叙事", "papers": keep}
    print(f"{disc}: curate {len(keep)}")

combined = []
for disc, v in out.items():
    combined.extend({"disc": disc, "papers": p} for p in v["papers"])
json.dump(out, io.open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("total curated:", sum(len(v["papers"]) for v in out.values()), "->", OUT)
# quick print first 20 curated
n=0
for disc, v in out.items():
    for p in v["papers"]:
        if n<24:
            print(f"  [{disc}] {p['title'][:70]}")
        n+=1
