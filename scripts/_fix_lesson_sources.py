# -*- coding: utf-8 -*-
"""修复 lessons-kg 里指向已删旧run文件的source → 失败图书馆"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
P = r"F:/AI/kesheng/packs/lessons-kg/kg.json"
OLD = "F:/AI/DS harness/runs/20260830-pho-sc4/red-team-M4关闭确认.md"
NEW = "runs/_lessons/FAILURE-LIBRARY.md"
g = json.load(open(P, encoding="utf-8-sig"))
n = 0
for e in g["entities"]:
    if OLD in (e.get("sources") or []):
        e["sources"] = [NEW if s == OLD else s for s in e["sources"]]
        n += 1
json.dump(g, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("fixed", n, "entities")
