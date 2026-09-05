# -*- coding: utf-8 -*-
"""Fetch ad-copy(promotion language) papers, especially differentiated by product category
(tech/science/ordinary/food) and video ads. Queries OpenAlex title.search, filters to
advertising-language/copy/appeal papers."""
import io, json, time, urllib.request, urllib.parse

OUT = r"F:/AI/kesheng/runs/_tmp-adcopy-papers.json"
MAILTO = "kesheng@example.com"
D = {
 "广告词核心": {
   "dom": "叙事",
   "queries": ["advertising slogan", "slogan", "tagline", "advertising copy",
               "copywriting", "advertising language", "advertising text",
               "advertising appeal", "brand slogan", "advertising message"],
   "include": ["slogan", "tagline", "copywriting", "advert", "advertising", "advertis", "ad", "promotion"],
   "exclude": ["medicine", "drug", "tobacco", "pornographic", "political advertising",
               "video game advert", "pyramid", "recruitment"],
 },
 "食品广告": {
   "dom": "叙事",
   "queries": ["food advertising appeal", "food advertisement", "food advertising message",
               "appetite appeal advertising", "emotional appeal food advertising"],
   "include": ["food", "appetite", "snack", "beverage", "food advert"],
   "exclude": ["food safety", "nutrition measure(low food)", "antibiotic", "gmo food review",
               "food insecurity", "obesity epidemiology"],
 },
 "科技/科研产品广告": {
   "dom": "叙事",
   "queries": ["technology advertising", "high-tech product advertising", "science product advertising",
               "rational appeal advertising", "feature appeal advertising",
               "innovation advertising message"],
   "include": ["technolog", "high-tech", "innovation", "rational appeal", "feature appeal",
               "scientific product", "engineer product", "tech brand"],
   "exclude": ["clinical trial", "medical therapy", "pharmaceutical ad", "smoking",
               "video game", "software feature"],
 },
 "普通品/情感广告": {
   "dom": "叙事",
   "queries": ["emotional appeal advertising", "informational emotional appeals advertising",
               "advertising effectiveness product", "consumer product advertising appeal",
               "hedonic utilitarian advertising appeal"],
   "include": ["emotional appeal", "informational appeal", "utilitarian", "hedonic",
               "advertising appeal", "consumer product advert", "advertising effectiveness"],
   "exclude": ["online learning", "app usage", "event study"],
 },
 "视频/多媒体广告": {
   "dom": "叙事",
   "queries": ["video advertising persuasion", "television advertisement message",
               "multimedia advertising effectiveness", "advertising video message recall"],
   "include": ["video advert", "television advert", "multimedia advert", "advertising video",
               "video ad", "tv advertising"],
   "exclude": ["video game", "video surveillance", "medical video", "streaming codec"],
 },
}
NEG = ["medicine","drug","tobacco","smok","clinical","pharmac","surgery","vaccine","video game",
       "gaming","security","surveillance","codec","compression","epidemiology","obesity",
       "antibiotic","smoking","prison","lawsuit","election","political party"]

def fetch(q):
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode({
        "filter": f"title.search:{q}", "per-page": "40", "mailto": MAILTO})
    req = urllib.request.Request(url, headers={"User-Agent":"kesheng-skill/1.0"})
    last=None
    for a in range(4):
        try:
            with urllib.request.urlopen(req, timeout=50) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            last=e
            if e.code==429:
                time.sleep(2.0*(a+1)); continue
            raise
    raise last

def low(s): return s.lower()
out={}
for disc,cfg in D.items():
    papers,seen=[],set()
    for q in cfg["queries"]:
        try: data=fetch(q)
        except Exception as ex:
            print(f"[{disc}] '{q}' FAIL {ex}"); continue
        for w in data.get("results",[]):
            t=(w.get("title") or "").strip()
            if not t: continue
            lt=low(t)
            if lt in seen: continue
            if any(n in lt for n in NEG): continue
            if not any(i in lt for i in cfg["include"]): continue
            seen.add(lt)
            doi=(w.get("doi") or "").replace("https://doi.org/","")
            papers.append({"title":t,"year":w.get("publication_year"),"cited":w.get("cited_by_count",0),"doi":doi})
        time.sleep(0.6)
    out[disc]={"dom":cfg["dom"],"papers":papers}
    print(f"{disc}: {len(papers)} papers")
json.dump(out, io.open(OUT,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("written ->",OUT)
