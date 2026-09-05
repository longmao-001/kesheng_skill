# -*- coding: utf-8 -*-
"""Validate packs/papers-wenan-kg/kg.json.

Checks:
  1. UTF-8 JSON parses.
  2. No duplicate entity ids (and ids match "Type:名称" pattern).
  3. Every relation source/target exists as an entity id, EXCEPT intentional
     cross-package references to 科生规则 (a whitelist of ids verified present in
     packs/kesheng-kg/kg.json).
  4. Conceptual check: paper ids match NNN counter; every Paper.sources set.
  5. Per-"schema" scale sanity (Paper/Concept/Method/Finding/Theory counts).
"""
import json
import os
import re
import sys

PACK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kg.json")
UNION = r"F:\AI\kesheng\packs\kesheng-kg\kg.json"

# Rule ids verified to exist in the union KG (grep'd earlier).
EXTERNAL_OK = {
    "NarrationType:直白规格型",
    "NarrationType:科普短视频",
    "NarrationRule:语速档位",
    "Rule:图文对位",
    "Rule:概念先行",
    "Rule:五层检查体系",
    "ProcessRule:单镜抽卡",
    "AudienceMode:EXP",
    "AudienceMode:PUB",
    "FailureLesson:文案白名单",
}

with open(PACK, encoding="utf-8") as f:
    data = json.load(f)

print("schema_version:", data.get("schema_version"), "| pack:", data.get("pack"))

ents = data["entities"]
rels = data["relations"]
print("entities:", len(ents), "| relations:", len(rels))

# 1. duplicate ids
ids = [e["id"] for e in ents]
dups = {i for i in ids if ids.count(i) > 1}
if dups:
    raise SystemExit("DUPLICATE IDS: %r" % (dups,))
print("OK duplicate ids: none")

# id pattern "Type:名称" and type string matches prefix
type_prefix = {"Paper": "Paper", "Concept": "Concept", "Method": "Method",
               "Finding": "Finding", "Theory": "Theory"}
for e in ents:
    prefix = type_prefix.get(e["type"])
    if prefix is None:
        raise SystemExit("UNKNOWN TYPE: " + e["type"])
    if not e["id"].startswith(prefix + ":"):
        raise SystemExit("ID/TYPE MISMATCH: %r (%s)" % (e["id"], e["type"]))
print("OK id-type pattern")

# 2. relation endpoints
id_set = set(ids)
dangling_sources = []
dangling_sources_dedup = set()
dangling_targets = set()
for r in rels:
    s = r["source"]
    t = r["target"]
    if s not in id_set:
        dangling_sources_dedup.add(s)
        dangling_sources.append((s, t))
    if t not in id_set and t not in EXTERNAL_OK:
        dangling_targets.add(t)

if dangling_sources_dedup:
    raise SystemExit("DANGLING SOURCES: %r" % (dangling_sources_dedup,))
print("OK all relation sources resolve to entities")

if dangling_targets:
    raise SystemExit("DANGLING TARGETS (not in pack & not whitelisted): %r" % (dangling_targets,))
print("OK relation targets resolve (in-pack or whitelisted 科生规则)")

# count external refs actually used
ext_used = {t for r in rels if r["target"] in EXTERNAL_OK for t in [r["target"]]}
print("external rule refs used:", sorted(ext_used))

# 3. Paper sanity
papers = [e for e in ents if e["type"] == "Paper"]
papers.sort(key=lambda e: e["id"])
nums = [int(e["id"].split("-")[-1]) for e in papers]
if nums != list(range(1, len(papers) + 1)):
    raise SystemExit("PAPER ID GAP / non-sequential: %r" % (nums,))
for e in papers:
    p = e["props"]
    for k in ("专业", "年份", "被引", "置信度", "说明"):
        if k not in p:
            raise SystemExit("PAPER missing prop %s: %s" % (k, e["id"]))
    if not e["sources"]:
        raise SystemExit("PAPER empty sources: " + e["id"])
print("OK paper id sequence 001..%03d and props/sources" % len(papers))

# 4. scale sanity per schema (soft)
by_type = {}
for e in ents:
    by_type.setdefault(e["type"], []).append(e["id"])
print("type counts:", {k: len(v) for k, v in by_type.items()})
print("relations/entity: %.2f" % (len(rels) / len(ents)))

if len(rels) < 1.3 * len(ents):
    raise SystemExit("relations under 1.3x entities")
print("OK relations >= 1.3x entities")

print("\nVALIDATION PASSED")
