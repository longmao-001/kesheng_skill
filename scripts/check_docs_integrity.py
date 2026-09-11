#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科生文档完整性校验 (check_docs_integrity.py) —— SOP 是否真正"嵌入"技能

防止三种"嵌不进技能"的问题：
  A. 断链   —— 文档引用了**技能内**不存在的文件（真错 → FAIL）
  B. 孤岛   —— SOP/模板写了却没人引用（读不到 → FAIL）
  C. 不一致 —— 启动必读清单 / 门控脚本名 与实际不符（FAIL）
另有 WARN 桶：疑似 run 产物 / 外部技能 / 示例 的引用，列出来供人工确认（不阻断）。

用法: python -X utf8 scripts/check_docs_integrity.py [--root F:/AI/kesheng]
"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 扫描范围的"技能文档"（不含 runs/ 项目产物、libs/ 第三方、packs/ 图谱）
SCAN_DIRS = ["", "docs", "playbooks", "templates", "agents", "orchestration",
             "protocols", "knowledge"]

REF = re.compile(r"`([A-Za-z0-9_\-./\u4e00-\u9fa5]+\.(?:md|py|js|json|yaml|yml|sh))`")

# 技能自身的目录前缀：以这些开头的引用若解析不到 = **真断链**（FAIL）
SKILL_PREFIX = ("docs/", "playbooks/", "templates/", "agents/", "orchestration/",
                "protocols/", "knowledge/", "scripts/", "packs/", "kb/")

# run 产物命名（runs/<slug>/ 黑板文件）：静默归类，不刷屏
RUN_ARTIFACT = re.compile(
    r"^(?:m[1-5]|m4\.5|ksp03|L[1-5]|STATE\.md$|brief\.md$|decision-log|science-data\.json$|"
    r"extract-report\.md$|assets-inventory[-.]|prompts-|concepts|delivery|refs/|style-baseline|"
    r"scientist-|storyboard-|screenwriter-|sound-|sound-design-|dop-|editor-|audience-|"
    r"director-|art-director-|producer-|inspector-|red-team-|检查裁决书|"
    r".*-(?:评审单|复核|纪要|大纲|检查报告|理解报告|抽图候选|概念先行|口播稿|分镜表|"
    r"摄影方案|声音方案|剪辑预计划|美术方案|受众模型|定剪意见|艺术阐述|艺术基调))", re.I)

# 不是"技能文件"的引用（外部技能如 ppt-master/huashu-design 的路径与 gate 文件 / 示例）
EXEMPT = re.compile(
    r"^(runs/|brand-spec\.md$|direction-approved\.md$|导演稿\.md$|"
    r"workflows/|references/|assets/|NotInList|shortcuts|\.\./)", re.I)

# 孤岛豁免：知识语料（经 kg_query/按需读，非 SOP）+ 索引 + 设计文档
ORPHAN_EXEMPT = re.compile(
    r"^(kb/|knowledge/(?!FAILURE-LIBRARY|index)|docs/(DESIGN|KG_DOMAIN_DESIGN|PAPER_INGESTION)\.md)|"
    r"^(README\.md$|knowledge/index\.md$|docs/ROLE_WORKFLOWS\.md$)", re.I)


def build_index(root):
    """全树文件名索引（含 packs/ 与 libs/，它们也是技能的一部分）。"""
    rels, by_base = set(), {}
    skip = ("runs", "node_modules", ".git", "__pycache__")
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip]
        for f in filenames:
            p = os.path.join(dirpath, f)
            r = os.path.relpath(p, root).replace("\\", "/")
            rels.add(r)
            by_base.setdefault(f, []).append(r)
    return rels, by_base


def resolve(ref, rels, by_base):
    r = ref.lstrip("./")
    if r in rels:
        return r
    base = os.path.basename(r)
    if base in by_base:
        return by_base[base][0]
    return None


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if "--root" in sys.argv:
        root = sys.argv[sys.argv.index("--root") + 1]
    rels, by_base = build_index(root)

    docs = []
    for d in SCAN_DIRS:
        base = os.path.join(root, d)
        if not os.path.isdir(base):
            continue
        for f in sorted(os.listdir(base)):
            if f.endswith((".md", ".py", ".js", ".json")):
                p = os.path.join(base, f)
                if os.path.isfile(p):
                    docs.append(p)
    md_docs = [p for p in docs if p.endswith(".md")]

    fails, warns = [], []
    quiet = 0
    refs_of = {}

    for p in docs:
        rp = os.path.relpath(p, root).replace("\\", "/")
        try:
            txt = io.open(p, encoding="utf-8-sig", errors="ignore").read()
        except Exception:  # noqa: BLE001
            continue
        got = set()
        for m in REF.finditer(txt):
            ref = m.group(1)
            if any(c in ref for c in "<>*N") and not os.path.exists(os.path.join(root, ref)):
                continue                                   # 占位（<平台>/prompts-*.md 等）
            hit = resolve(ref, rels, by_base)
            if hit:
                got.add(hit)
                continue
            # 解析不到：只有"技能目录前缀"的引用才算真断链；其余多为 run 产物/示例
            if ref.startswith(SKILL_PREFIX):
                fails.append(f"A 断链 [{rp}]: 引用技能内不存在的文件 `{ref}`")
            elif EXEMPT.search(ref):
                warns.append(f"A(外部) [{rp}]: `{ref}` 视为外部技能/示例")
            elif RUN_ARTIFACT.search(os.path.basename(ref)):
                quiet += 1                                    # run 产物，静默计数
            else:
                warns.append(f"A(待确认) [{rp}]: `{ref}` 技能内无此文件，也不是已知 run 产物命名")
        refs_of[rp] = got

    # B. 孤岛：从 SKILL.md 出发 3 跳可达
    start = "SKILL.md"
    reach = {start} if start in rels else set()
    frontier = [start]
    for _ in range(3):
        nxt = []
        for f in frontier:
            for t in refs_of.get(f, ()):
                if t not in reach:
                    reach.add(t)
                    if t.endswith(".md"):
                        nxt.append(t)
        frontier = nxt
    for p in md_docs:
        rp = os.path.relpath(p, root).replace("\\", "/")
        if rp in reach or ORPHAN_EXEMPT.search(rp) or os.path.basename(rp).startswith("_"):
            continue
        fails.append(f"B 孤岛 [{rp}]: 未被 SKILL.md（3 跳内）引用 → SOP 未嵌入，读不到")

    # C/D. 启动必读 + 门控脚本
    skill = os.path.join(root, "SKILL.md")
    if os.path.exists(skill):
        txt = io.open(skill, encoding="utf-8-sig", errors="ignore").read()
        m = re.search(r"##\s*启动必读", txt)
        if m:
            seg = txt[m.end():m.end() + 2000]
            seg = seg.split("\n## ")[0]
            for mm in re.finditer(r"`([^`]+\.md)`", seg):
                if not os.path.exists(os.path.join(root, mm.group(1))):
                    fails.append(f"C 启动必读: 列出的 `{mm.group(1)}` 不存在")
        for mm in re.finditer(r"scripts/([a-z_]+\.py)", txt):
            if not os.path.exists(os.path.join(root, "scripts", mm.group(1))):
                fails.append(f"D 门控脚本: SKILL.md 提到 scripts/{mm.group(1)} 不存在")

    print(f"== 文档完整性: {len(docs)} 文件（{len(md_docs)} md）· 可达 {len(reach)} · run产物引用 {quiet} 条（已静默）==")
    if fails:
        print(f"\nFAIL（{len(fails)}）:")
        for x in sorted(set(fails)):
            print("  -", x)
    if warns:
        print(f"\nWARN（{len(warns)}，确认为产物/外部即可忽略）:")
        for x in sorted(set(warns))[:25]:
            print("  -", x)
        if len(set(warns)) > 25:
            print(f"  … 共 {len(set(warns))} 条")
    if fails:
        sys.exit(1)
    print("\nPASS: 无断链 / 无孤岛 / 启动必读与门控脚本一致")


if __name__ == "__main__":
    main()
