#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科生统一知识图谱 · 并集构建器 (fragment → union mega-graph)

把 packs/<role>-kg/kg.json 的域片段合并成一张总图 packs/kesheng-kg/kg.json：
- 跨域重复实体(同 type+name)合并为一个节点, domains 记录归属, props/sources 取并集
- 关系保留 domain 标签(取源主体 domain), 按 (source,target,type) 去重
- id 规范: `Type:名称`(与片段一致, 合并不改变 id)
- director-kg 片段按实体类型重切为 分镜/影像/美术/剪辑/导演 五个 domain (真实剧组建制)
- KB 索引: kb/index.md 按 domain → type 分组
- Schema: schema.yaml 汇总实体类型×domain + 关系类型×domain

用法: python -X utf8 scripts/build_union_kg.py
"""
import io
import json
import os
import sys
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # F:/AI/kesheng
PACKS = os.path.join(BASE, "packs")
OUT = os.path.join(PACKS, "kesheng-kg")

# 域片段 → domain (director-kg 特殊处理: 按实体类型重切)
DOMAIN_MAP = {
    "scientist-kg": "科学",
    "screenwriter-kg": "叙事",
    "director-kg": None,          # 特殊: 见 DIRECTOR_TYPE_DOMAIN
    "director-seed": "导演",
    "prompt-kg": "prompt",
    "audience-kg": "受众",
    "redteam-kg": "红队",
    "audio-kg": "声音",
    "workflow-seed": "工艺",
    "gate-seed": "工艺",
    "sop-seed": "工艺",
    "narration-kg": "叙事",
    "xhs-cases-kg": "叙事",
    "creative-kg": "叙事",
    "lessons-kg": "工艺",
    "rednote-industry-kg": None,  # 特殊: 按实体类型分流(产业/叙事), 见 INDUSTRY_TYPE_DOMAIN
}

# 产业+小红书创意片段: 类型 → 域
INDUSTRY_TYPE_DOMAIN = {
    "IndustryConcept": "产业", "MarketData": "产业", "Company": "产业",
    "RednotePattern": "叙事", "RednoteRule": "叙事",
}

# 真实剧组建制: 旧"视觉导演"片段内容 → 新 5 域
DIRECTOR_TYPE_DOMAIN = {
    "ShotType": "分镜", "VisualMetaphor": "分镜", "Beat": "分镜",
    "Concept": "分镜", "GridTechnique": "分镜",
    "CameraMove": "影像", "MovingTechnique": "影像",
    "FeasibilityRule": "影像", "Mood": "影像",
    "ViStyle": "美术", "Scenario": "美术",
    "Transition": "剪辑",
    # 其余默认 → 导演
}

DOMAINS = ["科学", "叙事", "导演", "分镜", "美术", "影像", "声音",
           "prompt", "工艺", "受众", "红队", "剪辑", "产业"]


def load_fragments():
    frags = {}
    for d, domain in DOMAIN_MAP.items():
        p = os.path.join(PACKS, d, "kg.json")
        if not os.path.exists(p):
            print(f"[skip] {d} 片段不存在: {p}")
            continue
        with open(p, encoding="utf-8-sig") as f:
            frags[d] = (domain, json.load(f))
    return frags


def ent_domain(frag_dir, frag_domain, etype):
    if frag_dir == "director-kg":
        return DIRECTOR_TYPE_DOMAIN.get(etype, "导演")
    if frag_dir == "rednote-industry-kg":
        return INDUSTRY_TYPE_DOMAIN.get(etype, "产业")
    return frag_domain


def flat_sources(sources):
    out = []
    for s in sources or []:
        if isinstance(s, (list, tuple)):
            out.extend(str(x) for x in s)
        else:
            out.append(str(s))
    return out


def node_domain(e, frag_dir, frag_domain):
    """实体级 domain 优先(种子引擎可显式指定, 如字体→美术), 否则按片段映射."""
    if e.get("domains"):
        return list(e["domains"])
    return [ent_domain(frag_dir, frag_domain, e.get("type"))]


def main():
    frags = load_fragments()
    if not frags:
        print("没有任何片段可用"); sys.exit(1)

    # ---- 实体合并 ----
    entities = {}
    total_frag_entities = 0
    merged_count = 0
    type_domains = defaultdict(set)
    for d, (frag_domain, g) in sorted(frags.items()):
        for e in g.get("entities", []):
            total_frag_entities += 1
            eid = e.get("id") or f"{e['type']}:{e['name']}"
            domains = node_domain(e, d, frag_domain)
            if eid in entities:
                node = entities[eid]
                for dm in domains:
                    if dm not in node["domains"]:
                        node["domains"].append(dm)
                node["props"].update(e.get("props", {}))
                for s in flat_sources(e.get("sources", [])):
                    if s not in node["sources"]:
                        node["sources"].append(s)
                merged_count += 1
            else:
                entities[eid] = {
                    "id": eid, "type": e.get("type"), "name": e.get("name"),
                    "domains": list(domains),
                    "props": dict(e.get("props", {})),
                    "sources": flat_sources(e.get("sources", [])),
                }
            if e.get("type"):
                for dm in domains:
                    type_domains[e["type"]].add(dm)

    # ---- 关系合并 (domain = 源实体 domain) ----
    relations = {}
    rel_domains = defaultdict(set)
    for d, (frag_domain, g) in sorted(frags.items()):
        for r in g.get("relations", []):
            src = r.get("source")
            key = (src, r.get("target"), r.get("type"))
            src_ent = entities.get(src)
            dom = src_ent["domains"][0] if src_ent and src_ent["domains"] else (frag_domain or "导演")
            if key in relations:
                rel = relations[key]
                if dom not in rel["domains"]:
                    rel["domains"].append(dom)
            else:
                relations[key] = {"source": src, "target": r.get("target"),
                                  "type": r.get("type"), "domains": [dom]}
            rel_domains[r.get("type")].add(dom)

    # ---- 关系完整性校验 ----
    bad = [r for r in relations.values()
           if r["source"] not in entities or r["target"] not in entities]
    relations = {k: v for k, v in relations.items()
                 if v["source"] in entities and v["target"] in entities}

    entity_list = sorted(entities.values(), key=lambda n: (n["domains"][0], n["type"], n["name"]))
    relation_list = sorted(relations.values(), key=lambda r: (r["domains"][0], r["type"]))

    kg = {
        "schema_version": "1.0",
        "pack": "kesheng-kg",
        "name": "科生统一知识图谱（并集KG · 分区domain）",
        "description": "收集科生团队全部角色的知识沉淀为一张总图; domain=科学/叙事/导演/分镜/美术/影像/声音/prompt/受众/红队/剪辑",
        "domains": DOMAINS,
        "entities": entity_list,
        "relations": relation_list,
    }

    # ---- 写输出 ----
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "kg.json"), "w", encoding="utf-8") as f:
        json.dump(kg, f, ensure_ascii=False, indent=1)

    lines = [
        "# 科生统一知识图谱 Schema（并集KG · 分区domain）",
        "",
        "> 由 scripts/build_union_kg.py 从域片段自动汇总。domain=真实剧组建制(11域)。",
        "> 实体 id 规范: `Type:名称`；每节点含 domains(归属域列表)。关系含 domains(取源实体域)。",
        "",
        "## 领域分区",
        "| domain | 片段来源 | 定位 |",
        "|---|---|---|",
    ]
    frag_src = {
        "科学": "scientist-kg", "叙事": "screenwriter-kg+rednote-industry-kg", "prompt": "prompt-kg",
        "受众": "audience-kg", "红队": "redteam-kg", "声音": "audio-kg(种子)",
        "导演": "director-seed(种子)+director-kg(重切)",
        "分镜/影像/美术/剪辑": "director-kg(重切)",
        "工艺": "prompt-kg(种子引擎)",
        "产业": "rednote-industry-kg(调研入库)",
    }
    for d in DOMAINS:
        lines.append(f"| {d} | {frag_src.get(d, '—')} | 见片段 schema.yaml |")
    lines += ["", "## 实体类型 × domain", ""]
    lines.append("| 实体类型 | 归属 domain | 说明 |")
    for t in sorted(type_domains):
        lines.append(f"| {t} | {'/'.join(sorted(type_domains[t]))} | 见片段 schema.yaml |")
    lines += ["", "## 关系类型 × domain", ""]
    lines.append("| 关系类型 | 归属 domain | 说明 |")
    for t in sorted(rel_domains):
        lines.append(f"| {t} | {'/'.join(sorted(rel_domains[t]))} | 见片段 schema.yaml |")
    with open(os.path.join(OUT, "schema.yaml"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    idx = ["# 科生统一知识图谱 · 分区索引", "",
           "> 权威正文仍在原文件(sources 字段指向), 本索引只做导航。查询: `python packs/kg_query.py --domain <域> <关键词>`", ""]
    for domain in DOMAINS:
        idx.append(f"## {domain} 域")
        idx.append("")
        idx.append("| 实体 | 类型 | 一句话 | 原文 |")
        idx.append("|---|---|---|---|")
        for e in entity_list:
            if domain in e["domains"]:
                one = next(iter(e["props"].values()), "") if e["props"] else ""
                detail = str(one)[:60]
                srcs = " / ".join(e["sources"]) or "—"
                idx.append(f"| {e['name']} | {e['type']} | {detail} | {srcs} |")
        idx.append("")
    kb_dir = os.path.join(OUT, "kb")
    os.makedirs(kb_dir, exist_ok=True)
    with open(os.path.join(kb_dir, "index.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(idx) + "\n")

    # ---- 统计 ----
    print("=== 科生统一知识图谱构建完成 ===")
    print(f"域片段: {len(frags)} 个 → 总节点 {len(entities)} | 总关系 {len(relations)}")
    by_dom = defaultdict(lambda: [0, 0])
    for e in entity_list:
        for d in e["domains"]:
            by_dom[d][0] += 1
    for r in relation_list:
        for d in r["domains"]:
            by_dom[d][1] += 1
    for d in DOMAINS:
        e_cnt, r_cnt = by_dom.get(d, [0, 0])
        print(f"  {d}: 实体 {e_cnt} | 关系 {r_cnt}")
    print(f"片段原始实体 {total_frag_entities} → 合并后 {len(entities)} (跨域重复合并 {merged_count - (total_frag_entities - len(entities))} 处)")
    deg = defaultdict(int)
    for r in relation_list:
        deg[r["source"]] += 1
        deg[r["target"]] += 1
    iso_by_type = defaultdict(int)
    isolated = 0
    for e in entity_list:
        if deg[e["id"]] == 0:
            isolated += 1
            iso_by_type[e["type"]] += 1
    print(f"孤立节点(度=0): {isolated}  ({' | '.join(f'{k}={v}' for k, v in sorted(iso_by_type.items(), key=lambda kv: -kv[1]))})")
    print(f"悬空关系: {len(bad)} 条(已过滤)")

    def is_url(s):
        return s.startswith(("http://", "https://"))

    src_missing = []
    for e in entity_list:
        for s in e["sources"]:
            if is_url(s):
                continue
            if not os.path.exists(os.path.join(BASE, s)):
                src_missing.append((e["id"], s))
    if src_missing:
        print(f"⚠️ relative sources 路径不存在 {len(src_missing)} 处(前5): {src_missing[:5]}")
    else:
        print("✅ 所有 sources 均有效(相对路径存在 / URL 格式合法)")


if __name__ == "__main__":
    main()
