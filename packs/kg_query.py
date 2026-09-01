#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科生统一知识图谱 · 查询接口 (kg_query)

用法:
  python packs/kg_query.py <关键词...>                     # 全图检索
  python packs/kg_query.py --domain 科学 <关键词...>        # 限定 domain 检索 (科学/叙事/视觉/prompt/受众/红队)
  python packs/kg_query.py --domain 红队 --list            # 列出某域全部实体
  python packs/kg_query.py --stats                        # 图统计
  python packs/kg_query.py --depth 2 --domain 视觉 运镜     # 2跳邻居 (更宽的RAG上下文)

输出: 匹配实体的 RAG 上下文 (属性 + 1跳邻居 + 权威正文路径), 可直接注入 subagent prompt。
"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = os.path.dirname(os.path.abspath(__file__))
KG_PATH = os.path.join(BASE, "kesheng-kg", "kg.json")


def load():
    with open(KG_PATH, encoding="utf-8-sig") as f:
        return json.load(f)


def build_adj(kg):
    adj = {}
    for r in kg["relations"]:
        adj.setdefault(r["source"], []).append(("out", r["type"], r["target"]))
        adj.setdefault(r["target"], []).append(("in", r["type"], r["source"]))
    return adj


def hit(entity, q):
    if not q:
        return True
    q = q.strip().lower()
    name = (entity.get("name") or "").lower()
    if q in name or name in q:
        return 3
    if q in (entity.get("type") or "").lower():
        return 2
    for v in entity.get("props", {}).values():
        if isinstance(v, str) and q in v.lower():
            return 1
    return 0


def main():
    args = sys.argv[1:]
    domain = None
    depth = 1
    stats = False
    list_only = False
    query = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--domain" and i + 1 < len(args):
            domain = args[i + 1]; i += 2
        elif a == "--depth" and i + 1 < len(args):
            depth = int(args[i + 1]); i += 2
        elif a == "--stats":
            stats = True; i += 1
        elif a == "--list":
            list_only = True; i += 1
        elif a.startswith("--"):
            print(f"未知参数: {a}"); sys.exit(2)
        else:
            query.append(a); i += 1

    kg = load()
    adj = build_adj(kg)
    ents = {e["id"]: e for e in kg["entities"]}

    if stats:
        from collections import Counter
        ec, rc = Counter(), Counter()
        for e in kg["entities"]:
            for d in e["domains"]:
                ec[d] += 1
        for r in kg["relations"]:
            for d in r["domains"]:
                rc[d] += 1
        print(f"科生统一知识图谱: {len(kg['entities'])} 实体 / {len(kg['relations'])} 关系")
        for d in kg.get("domains", []):
            print(f"  {d}: 实体 {ec.get(d,0)} | 关系 {rc.get(d,0)}")
        return

    q = " ".join(query)
    hits = sorted(((hit(e, q), e) for e in kg["entities"] if (not domain or domain in e["domains"])),
                  key=lambda t: -t[0])
    hits = [(s, e) for s, e in hits if s > 0]
    if not hits:
        print(f"[kg_query] 未命中: domain={domain or '全部'} query='{q}'")
        return
    if list_only:
        for _, e in hits:
            print(f"{e['id']}  [{','.join(e['domains'])}]")
        return

    shown = 0
    for score, e in hits:
        if shown >= 12:
            print(f"...(其余 {len(hits) - shown} 个命中, 用更精确关键词)")
            break
        shown += 1
        print(f"### {e['name']}  [{e['type']}]  (域: {'/'.join(e['domains'])})")
        for k, v in e.get("props", {}).items():
            print(f"  - {k}: {v}")
        if e.get("sources"):
            print(f"  权威正文: {' / '.join(e['sources'])}")
        seen = set()
        for direction, rel_type, nb in adj.get(e["id"], []):
            if (direction, rel_type, nb) in seen:
                continue
            seen.add((direction, rel_type, nb))
            n = ents.get(nb)
            if not n:
                continue
            arrow = "<-" if direction == "in" else "->"
            print(f"  {rel_type} {arrow} {n['name']} [{n['type']}]")
            if depth >= 2:
                for d2, r2, nb2 in adj.get(nb, [])[:5]:
                    n2 = ents.get(nb2)
                    if n2 and n2["id"] != e["id"]:
                        print(f"      └ {rel_type}/{r2} -> {n2['name']}")
        print()


if __name__ == "__main__":
    main()
