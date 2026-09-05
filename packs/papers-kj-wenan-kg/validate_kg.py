# -*- coding: utf-8 -*-
"""Validate packs/papers-kj-wenan-kg/kg.json."""
import json
import re

PATH = "F:/AI/kesheng/packs/papers-kj-wenan-kg/kg.json"
KG = json.load(open(PATH, encoding="utf-8"))

errors = []
warnings = []

# 1. top-level schema
assert KG["schema_version"] == "1.0", "schema_version"
assert KG["pack"] == "papers-kj-wenan-kg", "pack"
assert KG["role"] == "科技/科研广告词/研究支撑", "role"
assert KG["dom"] == "叙事", "dom"

entities = KG["entities"]
relations = KG["relations"]

ids = {}
for e in entities:
    iid = e["id"]
    if iid in ids:
        errors.append(f"duplicate id: {iid}")
    ids[iid] = e["type"]

# Expected types
paper_ids = []
for e in entities:
    t = e["type"]
    if t == "Paper":
        if not re.fullmatch(r"Paper:OA-科技广告词-\d{3}", e["id"]):
            errors.append(f"bad paper id format: {e['id']}")
        paper_ids.append(e["id"])
        # paper props
        p = e["props"]
        for k in ("专业", "年份", "被引", "DOI", "域", "置信度", "说明"):
            if k not in p:
                errors.append(f"{e['id']} missing prop {k}")
        if e["props"]["置信度"] != "DB_REFERENCE":
            errors.append(f"{e['id']} confidence not DB_REFERENCE")
        if len(e["sources"]) < 1:
            errors.append(f"{e['id']} no source")
    elif t in ("Concept", "Method", "Finding", "Theory"):
        if e["props"].get("置信度") != "LLM_INFERRED":
            errors.append(f"{e['id']} confidence not LLM_INFERRED")
        # sources must be local paper ids
        for s in e["sources"]:
            if s not in ids:
                errors.append(f"{e['id']} sources->{s} dangling")
            elif ids[s] != "Paper":
                errors.append(f"{e['id']} sources->{s} not a Paper")
    else:
        errors.append(f"unknown type {t} for {e['id']}")

# paper sources format
for e in entities:
    if e["type"] == "Paper" and e["id"] in paper_ids:
        for s in e["sources"]:
            if not (s.startswith("https://doi.org/") or re.search(r"\(\d{4}\)$", s)):
                errors.append(f"{e['id']} source format bad: {s}")

# 2. relations
# cross-package rule refs allowed only for finding-evidence-for-rule / method-supports-rule
ALLOWED_RULE_REFS = {
    "NarrationType:直白规格型", "NarrationType:科普短视频", "AudienceMode:EXP",
    "AudienceMode:IND", "AudienceMode:PUB", "NarrationRule:语速档位",
    "Rule:图文对位", "Rule:概念先行", "Rule:五层检查体系",
    "NegativeRule:广告禁用词", "FailureLesson:文案白名单",
}
LOCAL_TYPES = {"paper-about", "paper-proposes", "paper-finds", "paper-uses", "concept-related-to"}

for r in relations:
    src, tgt, rtype = r["source"], r["target"], r["type"]
    if src not in ids:
        errors.append(f"relation source dangling: {rtype} {src}")
    if tgt in ids:
        continue
    # dangling target
    if rtype in ("finding-evidence-for-rule", "method-supports-rule"):
        if tgt in ALLOWED_RULE_REFS:
            continue
        errors.append(f"rule target not in allow-list: {rtype} -> {tgt}")
    else:
        errors.append(f"relation target dangling: {rtype} {tgt}")

# type range check for relations
for r in relations:
    if r["type"] not in LOCAL_TYPES | {"finding-evidence-for-rule", "method-supports-rule"}:
        errors.append(f"unknown relation type {r['type']}")

# counts
from collections import Counter
tc = Counter(e["type"] for e in entities)
print("== counts ==")
print("entities:", len(entities))
print("papers:", tc["Paper"], "concepts:", tc["Concept"], "methods:", tc["Method"],
      "findings:", tc["Finding"], "theories:", tc["Theory"])
print("relations:", len(relations), "| ratio:", round(len(relations) / len(entities), 2))
print("== rule refs ==")
rule_refs = Counter(r["target"] for r in relations if r["type"] in ("finding-evidence-for-rule", "method-supports-rule"))
for k, v in sorted(rule_refs.items()):
    print(f"  {k}: {v}")

if errors:
    print("\n== ERRORS ==")
    for e in errors:
        print("  ", e)
else:
    print("\nVALIDATION OK: no duplicate ids, no dangling local endpoints, rule refs all in allow-list.")
if warnings:
    print("\nWARNINGS:", warnings)
