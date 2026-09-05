# -*- coding: utf-8 -*-
"""Fetch OpenAlex title.search candidates for 科技/科研广告词 paper fragment."""
import json
import time
import urllib.request
import urllib.parse

MAILTO = "kesheng@example.com"
PER_PAGE = 40
OUT = "F:/AI/kesheng/packs/papers-kj-wenan-kg/candidates.json"

QUERIES = [
    # --- provided task queries ---
    "technology product advertising appeal",
    "high-tech advertising message",
    "scientific instrument marketing",
    "B2B technology advertising",
    "rational appeal high involvement product",
    "product category advertising appeal effectiveness",
    "credibility advertising source",
    "high technology brand communication",
    "innovation adoption advertising",
    "industrial product advertising message",
    "science communication advertising",
    "research product marketing",
    # --- broadened on-topic supplements ---
    "advertising appeal high technology",
    "high-tech products advertising",
    "technology advertising effectiveness",
    "informational advertising appeal",
    "information advertising appeals",
    "advertising credibility",
    "source credibility advertising",
    "expert endorser credibility",
    "innovative product advertising",
    "new product advertising appeal",
    "high involvement product advertising",
    "industrial advertising",
    "business to business advertising",
    "B2B advertising",
    "technology brand communication",
    "brand credibility technology",
    "consumer electronics advertising",
    "advertising technical information",
    "objective advertising claims",
    "verifiable advertising claims",
    "advertising claims verifiable",
    "technical product advertising",
    "advertising for high technology products",
    "research product promotion",
]

BASE = "https://api.openalex.org/works?filter=title.search:{}&per-page={}&mailto={}"


def fetch(q):
    url = BASE.format(urllib.parse.quote(q), PER_PAGE, MAILTO)
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "kesheng-kg/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode("utf-8"))
            return data
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 2 ** attempt
                print(f"429 on '{q}', backoff {wait}s")
                time.sleep(wait)
            else:
                print(f"HTTPError {e.code} on '{q}'")
                return {"results": [], "error": str(e)}
        except Exception as e:
            print(f"ERR on '{q}': {e}")
            time.sleep(1)
    return {"results": [], "error": "too many retries"}


def main():
    all_results = {}
    for i, q in enumerate(QUERIES):
        data = fetch(q)
        works = data.get("results", [])
        recs = []
        for w in works:
            title = w.get("title") or w.get("display_name") or ""
            year = w.get("publication_year")
            cited = w.get("cited_by_count")
            doi = w.get("doi", "")
            if doi and doi.startswith("https://doi.org/"):
                doi = doi[len("https://doi.org/"):]
            ploc = w.get("primary_location") or {}
            src = ploc.get("source") or {}
            recs.append({
                "id": w.get("id", ""),
                "title": title,
                "year": year,
                "cited_by_count": cited,
                "doi": doi,
                "type": w.get("type", ""),
                "journal": src.get("display_name", ""),
            })
        all_results[q] = recs
        print(f"[{i+1}/{len(QUERIES)}] '{q}': {len(recs)} results")
        time.sleep(0.5)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print("saved", OUT)


if __name__ == "__main__":
    main()
