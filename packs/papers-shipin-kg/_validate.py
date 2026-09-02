# -*- coding: utf-8 -*-
"""Validate papers-shipin-kg/kg.json against schema + cross-reference check."""
import json, collections, os

pack = "F:/AI/kesheng/packs/papers-shipin-kg/kg.json"
kesheng = "F:/AI/kesheng/packs/kesheng-kg/kg.json"

data = json.load(open(pack, encoding="utf-8"))
print("JSON loads OK. schema_version=%s pack=%s" % (data["schema_version"], data["pack"]))

ent = data["entities"]
rel = data["relations"]

# entity id uniqueness
ids = [e["id"] for e in ent]
dup = [k for k, v in collections.Counter(ids).items() if v > 1]
print("duplicate entity ids:", dup if dup else "none")

by_type = collections.Counter(e["type"] for e in ent)
print("entities:", dict(by_type), "total:", len(ent))
rel_bit = collections.Counter(r["type"] for r in rel)
print("relations:", dict(rel_bit), "total:", len(rel))
print("ratio = %.2f (need >= 1.3)" % (len(rel) / len(ent)))

# internal endpoint check (non-Kesheng-rule endpoints)
kes = json.load(open(kesheng, encoding="utf-8"))
kes_ids = {e["id"] for e in kes["entities"]}

internal = {e["id"] for e in ent}
missing_internal = []
missing_kese = []
for r in rel:
    for ep in (r["source"], r["target"]):
        if ep in internal:
            continue
        if ep in kes_ids:
            continue
        (missing_internal if False else missing_kese).append((ep, r["type"]))

print("relation endpoints not in this pack nor kesheng-kg:", len(set(missing_kese)))
for ep, t in missing_kese:
    print("   MISSING:", t, "->", ep)

# every Concept/Method/Finding/Theory must carry sources pointing at paper DOIs present in pack
doi_set = set()
for e in ent:
    if e["type"] == "Paper":
        d = e["props"].get("DOI")
        if d:
            doi_set.add(d)
no_src = [e["id"] for e in ent if e["type"] != "Paper" and not e.get("sources")]
printed_ok = [e["id"] for e in ent if e["type"] == "Paper" and e["type"] == "Paper"]
print("non-Paper entities without sources:", no_src if no_src else "none")

# cross-check that the source DOIs referenced by non-Paper entities exist among the pack's papers
src_doi_refs = set()
for e in ent:
    if e["type"] == "Paper":
        continue
    for s in e.get("sources", []):
        src_doi_refs.add(s)
unmatched = src_doi_refs - doi_set
print("non-Paper source DOIs NOT among pack papers:", unmatched if unmatched else "none (all traceable)")

# verify the DOI props equal the source doi string for papers (integrity)
bad_doi = []
for e in ent:
    if e["type"] == "Paper":
        d = e["props"].get("DOI", "")
        if d and d not in e.get("sources", []):
            bad_doi.append((e["id"], e["props"].get("DOI")))
print("papers whose DOI not in props/sources mismatch:", bad_doi if bad_doi else "none")

print("\nALL CHECKS DONE")
