#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科生 prompt 域 · 种子扩增引擎 (平台版本 × 镜头类型 → 组合公式)

输入:  packs/prompt-kg/expand_tables.json   (子agent从权威手册抽取的能力矩阵表)
       packs/prompt-kg/kg.json              (人工抽取的 70 实体核心, 首次运行备份为 kg.hand.json)
输出:  packs/prompt-kg/kg.json              (核心 + 组合公式种子, 目标 ≥1000 实体)
规则:  组合公式 = 平台版本(语法/路线/时长/负面/语言) × 镜头类型(prompt句式/画面要点/情绪作用)
       每对象 source 指向权威手册真实路径, 不凭空发明; 可反复重跑(幂等: 手工核心先备份)

用法: python -X utf8 scripts/expand_prompt_seed.py
"""
import io
import json
import os
import shutil
import sys
from collections import OrderedDict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(BASE, "packs", "prompt-kg")
TABLES = os.path.join(PKG, "expand_tables.json")
FRAG = os.path.join(PKG, "kg.json")
HAND = os.path.join(PKG, "kg.hand.json")
DEFAULT_SRC = ["playbooks/platform-prompts.md", "knowledge/seedance-template-library.md",
               "knowledge/prompt-reverse.md", "knowledge/camera-language.md",
               "playbooks/consistency.md"]


def load(p, default=None):
    if not os.path.exists(p):
        return default
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def src(o):
    s = o.get("sources") or o.get("source") or DEFAULT_SRC
    if isinstance(s, str):
        s = [s]
    return list(s)


def main():
    tables = load(TABLES)
    if not tables:
        print("缺少 expand_tables.json — 先跑子 agent 产出能力矩阵表"); sys.exit(1)

    core = load(FRAG) or {"schema_version": "1.0", "pack": "prompt-kg", "role": "prompt工程师",
                          "entities": [], "relations": []}
    if not os.path.exists(HAND):
        shutil.copyfile(FRAG, HAND)
        print(f"[备份] 手工核心 → {os.path.relpath(HAND, BASE)}")

    platforms = tables.get("platforms", [])
    shots = tables.get("shots", [])
    moves = tables.get("moves", [])
    tags = tables.get("tags", [])
    negatives = tables.get("negatives", [])
    failfix = tables.get("failfix", [])

    ents = OrderedDict()   # id -> node
    rels = OrderedDict()   # (s,t,type) -> rel
    for e in core.get("entities", []):
        ents[e["id"]] = e
    for r in core.get("relations", []):
        rels[(r["source"], r["target"], r["type"])] = r

    # 旧公式口径修正: 单镜多动作/长动态同样按时间轴分段 (2026-09)
    _tf = "PromptFormula:Seedance时间轴分镜公式"
    if _tf in ents:
        ents[_tf]["props"]["适用"] = "多镜一次成片; 单镜>6s或多动作/变速/光效变化同样按时间轴分段(0-2秒[...]), ≤6s单动作才用一段式通用公式"

    # 旧范式口径修正: 首帧不是"默认优先/必须"——参考包(全能参考)→多镜原生→首帧仅I2V兜底 (2026-09, 用户要求)
    # ProcessRule 的修正直接改在数据源 expand_tables2.json(引擎每次从数据源生成, 此处只修正 core 实体)
    _fix3 = "GenerateRoute:图生视频I2V"
    if _fix3 in ents:
        ents[_fix3]["props"]["流程"] = "仅当走I2V路线: 先生成正确静帧(文生图+参考图)→科学顾问验收(科研片结构必须对)→图生视频; 全能参考平台不用单独首帧——参考包直接锚定"
        ents[_fix3]["props"]["定位"] = "参考包优先范式下的兜底路线(无参考包/平台仅I2V时); 精确结构多角度参考图>单张首帧"

    def add_ent(eid, etype, name, props, sources, domains=None):
        if eid in ents:
            ents[eid]["props"].update(props)
            ents[eid].setdefault("sources", [])
            for s in sources:
                if s not in ents[eid]["sources"]:
                    ents[eid]["sources"].append(s)
            if domains:
                for d in domains:
                    if d not in ents[eid].setdefault("domains", []):
                        ents[eid]["domains"].append(d)
        else:
            node = {"id": eid, "type": etype, "name": name,
                    "props": dict(props), "sources": list(sources)}
            if domains:
                node["domains"] = list(domains)
            ents[eid] = node

    def add_rel(src_id, tgt_id, rtype):
        key = (src_id, tgt_id, rtype)
        if key not in rels:
            rels[key] = {"source": src_id, "target": tgt_id, "type": rtype, "domains": ["prompt"]}

    # ---- 平台版本实体 ----
    print(f"平台矩阵: {len(platforms)} 个平台版本")
    for p in platforms:
        pname = f"{p['name']}{p.get('version', '')}"
        add_ent(f"Platform:{pname}", "Platform", pname, {
            "类型": "平台版本",
            "语法要点": p.get("syntax", ""),
            "支持路线": " / ".join(p.get("routes", [])) or "—",
            "时长档": " / ".join(p.get("durations", [])) or "—",
            "写作语言": p.get("lang", ""),
            "参数语法": " / ".join(p.get("params", [])) or "—",
            "负面词": " / ".join(p.get("negatives", [])) or "—",
        }, src(p))

    # ---- 镜头/运镜/标签/负面/路线 实体 ----
    shot_ids = {}
    for sh in shots:
        cid = f"ShotType:{sh['name']}"
        if cid in ents:
            cid = f"ShotType:{sh['cat']}-{sh['name']}"
        shot_ids[sh["name"]] = cid
        add_ent(cid, "ShotType", sh["name"], {
            "分类": sh.get("cat", ""),
            "画面要点": sh.get("props", {}).get("画面要点", ""),
            "情绪作用": sh.get("props", {}).get("情绪作用", ""),
            "prompt句式": sh.get("props", {}).get("prompt句式", ""),
            "典型用法": sh.get("props", {}).get("典型用法", ""),
        }, src(sh))
    for m in moves:
        add_ent(f"CameraMove:{m['name']}", "CameraMove", m["name"], {
            "英文写法": m.get("en", ""), "情绪效果": m.get("mood", ""),
            "动感写法": m.get("writeup", ""),
        }, src(m))
    for t in tags:
        add_ent(f"Tag:{t['name']}", "Tag", t["name"], {
            "分类": t.get("cat", ""), "prompt写法": t.get("writeup", ""),
        }, src(t))
    for n in negatives:
        add_ent(f"NegativeRule:{n['cn']}", "NegativeRule", n["cn"], {
            "英文写法": n.get("en", ""), "适用": n.get("use", ""),
        }, src(n))
    routes = OrderedDict()
    for p in platforms:
        for rt in p.get("routes", []):
            if rt and rt not in routes:
                routes[rt] = None
                add_ent(f"GenerateRoute:{rt}", "GenerateRoute", rt, {
                    "说明": "由平台矩阵汇总(各平台支持情况见 Platform 实体)",
                }, src(p))
    for f in failfix:
        add_ent(f"FailFix:{f['fail']}", "FailFix", f["fail"], {
            "修复": f.get("fix", ""),
        }, [f.get("source") or DEFAULT_SRC[0]])

    # ---- 风格方向 + 流程实体 (expand_tables2.json) ----
    tables2 = load(os.path.join(PKG, "expand_tables2.json")) or {}
    styles = tables2.get("styles", [])
    processes = tables2.get("processes", [])
    for st in styles:
        add_ent(f"StyleDirection:{st['name']}", "StyleDirection", st["name"], {
            "气质": st.get("desc", ""),
            "色板": st.get("palette", ""),
            "光影写法": st.get("light", ""),
            "氛围词": st.get("atmosphere", ""),
            "风格token示例": st.get("styleToken", ""),
            "适用题材": st.get("subjects", ""),
            "禁忌": st.get("taboo", ""),
        }, src(st), domains=["美术", "prompt"])
    for pr in processes:
        add_ent(f"ProcessRule:{pr['name']}", "ProcessRule", pr["name"], {
            "说明": pr.get("desc", ""),
            "步骤": " → ".join(pr.get("steps", [])),
            "硬规则": "；".join(pr.get("rules", [])),
            "适用场景": pr.get("scenes", ""),
        }, src(pr), domains=["工艺"])

    # ---- 画风 (expand_tables3.json): ArtStyle + 画风一致性规则 ----
    tables3 = load(os.path.join(PKG, "expand_tables3.json")) or {}
    art_styles = tables3.get("artStyles", [])
    style_rules = tables3.get("styleRules", [])
    for st in art_styles:
        add_ent(f"ArtStyle:{st['name']}", "ArtStyle", st["name"], {
            "大类": st.get("category", ""),
            "定义": st.get("definition", ""),
            "关键词": " / ".join(st.get("keywords", [])),
            "画风写法": st.get("writing", ""),
            "色彩体系": st.get("palette", ""),
            "光影特征": st.get("lighting", ""),
            "适用题材": st.get("subjects", ""),
            "平台适配": st.get("compat", ""),
            "翻车风险": st.get("risk", ""),
        }, src(st), domains=["美术", "prompt"])
    for sr in style_rules:
        add_ent(f"ArtStyleRule:{sr['name']}", "ArtStyleRule", sr["name"], {
            "硬规则": "；".join(sr.get("rules", [])),
        }, src(sr), domains=["工艺"])

    # ---- 字体库 (expand_tables4.json): FontFamily + 字体规范 (归属美术域) ----
    tables4 = load(os.path.join(PKG, "expand_tables4.json")) or {}
    fonts = tables4.get("fonts", [])
    font_rules = tables4.get("fontRules", [])
    for fnt in fonts:
        add_ent(f"FontFamily:{fnt['name']}", "FontFamily", fnt["name"], {
            "类别": fnt.get("family", ""),
            "风格特征": fnt.get("style", ""),
            "字重": " / ".join(fnt.get("weights", [])),
            "用途": fnt.get("usage", ""),
            "授权": fnt.get("license", ""),
            "备注": fnt.get("notes", ""),
        }, src(fnt), domains=["美术"])
    for fr in font_rules:
        add_ent(f"FontRule:{fr['name']}", "FontRule", fr["name"], {
            "硬规则": "；".join(fr.get("rules", [])),
        }, src(fr), domains=["美术"])

    # ---- 路线选择规则 (expand_tables.json routeRules, 工艺域): 全能参考包优先 ----
    route_rules = tables.get("routeRules", [])
    for rr in route_rules:
        add_ent(f"RouteRule:{rr['name']}", "RouteRule", rr["name"], {
            "硬规则": "；".join(rr.get("rules", [])),
        }, src(rr), domains=["工艺"])

    # ---- 按秒时间轴规则 (expand_tables.json timeAxisRules, prompt 域): 0-2秒[…] 断句 ----
    time_axis_rules = tables.get("timeAxisRules", [])
    for tr in time_axis_rules:
        add_ent(f"TimeAxisRule:{tr['name']}", "TimeAxisRule", tr["name"], {
            "硬规则": "；".join(tr.get("rules", [])),
        }, src(tr), domains=["prompt", "工艺"])

    # ---- 组合公式: 平台版本 × 镜头类型 ----
    formula_count = 0
    for p in platforms:
        pname = f"{p['name']}{p.get('version', '')}"
        for sh in shots:
            fid = f"PromptFormula:{pname}-{sh['name']}"
            add_ent(fid, "PromptFormula", f"{pname} × {sh['name']}", {
                "平台": pname,
                "镜头": sh["name"],
                "主体与动作": sh.get("props", {}).get("典型用法", ""),
                "画面要点": sh.get("props", {}).get("画面要点", ""),
                "镜头语言句": sh.get("props", {}).get("prompt句式", ""),
                "平台语法": p.get("syntax", ""),
                "生成路线": " / ".join(p.get("routes", [])) or "—",
                "时长档": " / ".join(p.get("durations", [])) or "—",
                "写作语言": p.get("lang", ""),
                "负面词": " / ".join(p.get("negatives", [])) or "—",
            }, list(dict.fromkeys(src(p) + src(sh))))
            add_rel(fid, f"Platform:{pname}", "formula-for-platform")
            add_rel(fid, shot_ids[sh["name"]], "formula-for-shot")
            formula_count += 1

    # ---- 风格组合公式: 平台版本 × 风格方向 ----
    style_formula_count = 0
    for p in platforms:
        pname = f"{p['name']}{p.get('version', '')}"
        for st in styles:
            fid = f"PromptStyleFormula:{pname}×{st['name']}"
            add_ent(fid, "PromptStyleFormula", f"{pname} × {st['name']}", {
                "平台": pname,
                "风格": st["name"],
                "风格token句": st.get("styleToken", ""),
                "色板句": st.get("palette", ""),
                "光影句": st.get("light", ""),
                "氛围句": st.get("atmosphere", ""),
                "适用题材": st.get("subjects", ""),
                "禁忌": st.get("taboo", ""),
                "平台语法": p.get("syntax", ""),
            }, list(dict.fromkeys(src(p) + src(st))))
            add_rel(fid, f"Platform:{pname}", "style-formula-for-platform")
            add_rel(fid, f"StyleDirection:{st['name']}", "style-formula-for-style")
            style_formula_count += 1

    # ---- 流程关联 (process-uses) ----
    name2id = {}
    for m in moves:
        name2id[m["name"]] = f"CameraMove:{m['name']}"
    for t in tags:
        name2id[t["name"]] = f"Tag:{t['name']}"
    for p in platforms:
        name2id[p["name"]] = f"Platform:{p['name']}{p.get('version', '')}"
        if p.get("version"):
            name2id.setdefault(p["name"], f"Platform:{p['name']}{p.get('version','')}")
    for rn in routes:
        name2id[rn] = f"GenerateRoute:{rn}"
    for k, v in shot_ids.items():
        name2id.setdefault(k, v)
    process_rels = 0
    for pr in processes:
        pid = f"ProcessRule:{pr['name']}"
        for rel in pr.get("relates", []) or []:
            tgt = name2id.get(rel)
            if tgt and tgt in ents:
                add_rel(pid, tgt, "process-uses")
                process_rels += 1

    artrule_rels = 0
    for sr in style_rules:
        sid = f"ArtStyleRule:{sr['name']}"
        for rel in sr.get("relates", []) or []:
            tgt = name2id.get(rel)
            if tgt and tgt in ents:
                add_rel(sid, tgt, "artstyle-rule-uses")
                artrule_rels += 1

    for fnt in fonts:
        name2id.setdefault(fnt["name"], f"FontFamily:{fnt['name']}")
    fontrule_rels = 0
    for fr in font_rules:
        fid_ = f"FontRule:{fr['name']}"
        for rel in fr.get("relates", []) or []:
            tgt = name2id.get(rel)
            if tgt and tgt in ents:
                add_rel(fid_, tgt, "font-rule-uses")
                fontrule_rels += 1

    route_rels = 0
    for rr in route_rules:
        rid = f"RouteRule:{rr['name']}"
        for rel in rr.get("relates", []) or []:
            tgt = name2id.get(rel)
            if tgt and tgt in ents:
                add_rel(rid, tgt, "route-rule-uses")
                route_rels += 1

    timeaxis_rels = 0
    for tr in time_axis_rules:
        tid = f"TimeAxisRule:{tr['name']}"
        for rel in tr.get("relates", []) or []:
            tgt = name2id.get(rel)
            if tgt and tgt in ents:
                add_rel(tid, tgt, "timeaxis-rule-uses")
                timeaxis_rels += 1

    # ---- 画风组合公式: 平台版本 × 画风 ----
    art_formula_count = 0
    for p in platforms:
        pname = f"{p['name']}{p.get('version', '')}"
        for st in art_styles:
            fid = f"ArtStyleFormula:{pname}×{st['name']}"
            add_ent(fid, "ArtStyleFormula", f"{pname} × {st['name']}", {
                "平台": pname,
                "画风": st["name"],
                "画风写法": st.get("writing", ""),
                "关键词": " / ".join(st.get("keywords", [])),
                "色彩光影句": f"{st.get('palette','')}；{st.get('lighting','')}",
                "适用题材": st.get("subjects", ""),
                "翻车风险": st.get("risk", ""),
                "平台语法": p.get("syntax", ""),
            }, list(dict.fromkeys(src(p) + src(st))))
            add_rel(fid, f"Platform:{pname}", "artstyle-formula-for-platform")
            add_rel(fid, f"ArtStyle:{st['name']}", "artstyle-formula-for-style")
            art_formula_count += 1

    # ---- 语义兜底连线 (保守文本匹配, 补孤立叶节点) ----
    def has_rel(sid):
        return any(k[0] == sid for k in rels)

    move_links = 0
    for m in moves:
        mid = f"CameraMove:{m['name']}"
        for sname, sid in shot_ids.items():
            node = ents.get(sid) or {}
            blob = " ".join(str(v) for v in node.get("props", {}).values())
            if m["name"] in blob:
                add_rel(sid, mid, "shot-uses-move")
                move_links += 1
    neg_links = 0
    for n in negatives:
        nid = f"NegativeRule:{n['cn']}"
        for p in platforms:
            pid = f"Platform:{p['name']}{p.get('version', '')}"
            for x in p.get("negatives", []) or []:
                if n["cn"] and (n["cn"] in x or x in n["cn"]):
                    add_rel(pid, nid, "negative-for-platform")
                    neg_links += 1
                    break
    proc_links = 0
    for pr in processes:
        pid = f"ProcessRule:{pr['name']}"
        if has_rel(pid):
            continue
        for sname, sid in shot_ids.items():
            if sname in pr["name"] or pr["name"] in sname:
                add_rel(pid, sid, "process-for-shot")
                proc_links += 1
                break
    fr_redline = "FontRule:商用授权红线"
    font_links = 0
    if fr_redline in ents:
        for fnt in fonts:
            add_rel(f"FontFamily:{fnt['name']}", fr_redline, "governed-by")
            font_links += 1
    artrule_links2 = 0
    for sr in style_rules:
        sid = f"ArtStyleRule:{sr['name']}"
        if has_rel(sid):
            continue
        for st in art_styles:
            if st["name"] in sr["name"] or sr["name"] in st["name"]:
                add_rel(sid, f"ArtStyle:{st['name']}", "artstyle-rule-for-style")
                artrule_links2 += 1
                break

    print(f"[兜底连线] 运镜→镜头 {move_links} | 负面→平台 {neg_links} | 流程→镜头 {proc_links} | 字体→授权红线 {font_links} | 画风规则→画风 {artrule_links2}")

    for p in platforms:
        pname = f"{p['name']}{p.get('version', '')}"
        for rt in p.get("routes", []):
            if rt:
                add_rel(f"Platform:{pname}", f"GenerateRoute:{rt}", "platform-supports-route")

    # ---- 输出 ----
    ents_out = sorted(ents.values(), key=lambda e: (e["type"], e["name"]))
    rels_out = sorted(rels.values(), key=lambda r: (r["type"], r["source"]))

    # 悬空过滤
    ids = {e["id"] for e in ents_out}
    rels_out = [r for r in rels_out if r["source"] in ids and r["target"] in ids]

    out = {
        "schema_version": "1.0",
        "pack": "prompt-kg",
        "role": "prompt工程师",
        "description": "prompt 域种子: 人工核心(kg.hand.json) + 组合公式种子(平台版本×镜头类型, expand_prompt_seed.py 生成)",
        "entities": ents_out,
        "relations": rels_out,
    }
    with open(FRAG, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    by_type = {}
    for e in ents_out:
        by_type[e["type"]] = by_type.get(e["type"], 0) + 1
    print("=== prompt 域种子扩增完成 ===")
    print(f"平台版本 {len(platforms)} × 镜头类型 {len(shots)} → 镜头公式 {formula_count}")
    print(f"平台版本 {len(platforms)} × 风格方向 {len(styles)} → 风格公式 {style_formula_count}")
    print(f"平台版本 {len(platforms)} × 画风 {len(art_styles)} → 画风公式 {art_formula_count}")
    print(f"流程 {len(processes)} (关联 {process_rels}) | 画风规则 {len(style_rules)} (关联 {artrule_rels}) | 路线规则 {len(route_rules)} (关联 {route_rels}) | 时间轴规则 {len(time_axis_rules)} (关联 {timeaxis_rels}) | 风格方向 {len(styles)} | 画风 {len(art_styles)} | 运镜 {len(moves)} | 标签 {len(tags)} | 负面 {len(negatives)} | 字体 {len(fonts)} (规范 {len(font_rules)}, 关联 {fontrule_rels}, 域=美术)")
    print(f"实体总数: {len(ents_out)} | 关系总数: {len(rels_out)}")
    print("实体类型分布:", " | ".join(f"{k}={v}" for k, v in sorted(by_type.items(),
          key=lambda kv: -kv[1])))


if __name__ == "__main__":
    main()
