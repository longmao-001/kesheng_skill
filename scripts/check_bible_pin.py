#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
圣经引用版本 pin 门控 (check_bible_pin.py) —— 「引用圣经必须 pin 版本」的机器层

依据：**用户裁定 20260921**（双通道）+ 硬规则 **#36②③**（圣经＝跨集单一事实源；**圣经版本与生效集号
写死，禁静默改版**）＋ 本次闭环条目（`docs/DUAL-CHANNEL-AUDIT.md` §4-5 / §5-T1）：
  **跨项目/衍生片引用圣经时必须 pin 版本，防圣经改版后静默过期** —— 引用方（某集 / 衍生宣传片）
  若只写"见圣经"，圣经一改版就无从判断它用的是哪一版，色值/字形/母题/红线会**静默漂移**。
  模板层已加必填字段（`templates/show-bible.md` **§⓪ 本册版本与引用登记**、
  `templates/episode-brief.md`「引用圣经版本（路径＋版本号/日期）」）；本脚本把该约定变成**机器门控**。

判据（**仅剧集项目**跑；非剧集 = `[跳过]`）：
  B1 剧集项目**必须有圣经文件**：取 `series-config.json` 的 `show_bible_file`（默认 `show-bible.md`）；
     候选 `<季>/show-bible.md`、`<季>/series/show-bible.md`、`<季>/<show_bible_file>`；**都没有 = FAIL**
  B2 圣经 **§⓪ 版本行非空**：须给出 ①**版本号**（`v3`／`版本3`／`版本号：v3`）②**生效日期**
     （`YYYY-MM-DD`）或**生效集号**（`EP01–EP08`／`生效集号 EP01–EP08`）——三者皆无 = FAIL；
     **§⓪ 段整体缺失 = FAIL**（提示补 `templates/show-bible.md` §⓪）
  B3 每集 `EPnn-brief.md`（或等价命名）的**「引用圣经版本」必须 = 圣经当前版本** —— 不一致 = **FAIL**
     （提示"圣经已改版、该集引用过期，须回填新版本或走 KSP-C 评估回炉范围"，承 #36③）
  B4 分集简报**缺该字段 = FAIL**（缺字段 = 不可判过期，等于没 pin）；集目录里**一个 brief 都没有** =
     WARN（可能是尚未开工的季，不误判为 FAIL）

退出码（**空跑不算通过**）：
  0  PASS（可含 WARN/NOTE）
  1  存在 FAIL（缺圣经 / 版本行空 / 引用过期 / brief 缺字段）
  2  不可判定：run 目录不存在、**非剧集项目（`[跳过]`）**、季目录里找不到任何可判对象
     （加 `--via-check-all` 时，`check_all.py` 把 1 当 FAIL、2 当 `[跳过]`）

用法：
  python -X utf8 scripts/check_bible_pin.py <runs/<季slug>> [--json] [--via-check-all]

⚠️ 剧集判定与 `check_all.py`/`check_channel_conformance.py` 同口径（目录形态层）：
   有 `series-config.json` 或 `EPnn/`（含扁平式 `<slug>-EPnn/`）＝剧集。
"""
import argparse
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

SKIP_NOT_SERIES = "[跳过] 非剧集项目（无 series-config.json、无 EPnn/ 集目录）"

# ---------- 剧集形态 ----------
SERIES_CONFIG = "series-config.json"
EP_DIR_RE = re.compile(r"^EP\s*\d{1,2}$", re.I)
EP_FLAT_DIR_RE = re.compile(r"-EP\s*\d{1,2}$", re.I)
# 分集简报：EP01-brief.md / EP1-brief.md / EP01-分集简报.md / EP01_brief.md
BRIEF_RE = re.compile(r"^EP\s*(\d{1,2})\s*[-_－—]?\s*(?:brief|分集简报)", re.I)
# 圣经候选（按优先级）
BIBLE_CANDIDATES = ("show-bible.md", os.path.join("series", "show-bible.md"))
# 其它可能的圣经命名（兜底扫描，避免因命名差异误判"缺圣经"）
BIBLE_FALLBACK_RE = re.compile(r"(?:show[-_]?bible|风格圣经|圣经).*\.md$", re.I)

# ---------- 版本行解析 ----------
BIBLE_MARK_ZERO = re.compile(r"§\s*[⓪0O零]")          # §⓪ 标题（段存在的判据）
BIBLE_MARK_TITLE = re.compile(r"本册版本与引用登记")     # 段标题文字（§ 符号被改动时的兜底）
VER_RE = re.compile(r"(?:版本\s*号?\s*[:：=＝]?\s*)?\bv\s*(\d{1,3})\b|版本\s*号?\s*[:：=＝]?\s*(\d{1,3})", re.I)
DATE_RE = re.compile(r"(20\d{2})\s*[-/年]\s*(\d{1,2})\s*[-/月]\s*(\d{1,2})\s*日?")
EP_RANGE_RE = re.compile(r"EP\s*0*(\d{1,2})\s*(?:[–—~～\-至到]|\s+)\s*EP?\s*0*(\d{1,2})", re.I)
EP_ONE_RE = re.compile(r"EP\s*0*(\d{1,2})", re.I)
# 「引用圣经版本」字段（表格行 / 加粗字段 / 列表项 三种写法）
REF_FIELD_RE = re.compile(
    r"引用\s*圣经\s*版本[^\n|]{0,24}[|｜:：=＝]?\s*(?P<val>[^\n|]*)"
    r"|(?:\*\*|【)?\s*引用圣经版本(?:\*\*|】)?\s*[：:]\s*(?P<val2>[^\n]*)",
    re.I,
)


def is_series(run_dir):
    """剧集判定（与 check_all.py 同口径）：有 series-config.json 或有 EPnn/（含扁平式）。"""
    if os.path.isfile(os.path.join(run_dir, SERIES_CONFIG)):
        return True
    try:
        return any(os.path.isdir(os.path.join(run_dir, d))
                   and (EP_DIR_RE.match(d) or EP_FLAT_DIR_RE.match(d))
                   for d in os.listdir(run_dir))
    except OSError:
        return False


def find_bible(run_dir):
    """找圣经文件：先 series-config.json 的 show_bible_file，再候选名，再兜底扫描。"""
    cfg_file = os.path.join(run_dir, SERIES_CONFIG)
    declared = None
    if os.path.isfile(cfg_file):
        try:
            with open(cfg_file, encoding="utf-8-sig") as fh:
                data = json.load(fh)
            if isinstance(data, dict) and data.get("show_bible_file"):
                declared = str(data["show_bible_file"]).strip()
        except Exception:  # noqa: BLE001
            declared = None
    cands = list(BIBLE_CANDIDATES)
    if declared:
        cands = [declared, os.path.join("series", declared)] + cands
    for rel in cands:
        p = os.path.join(run_dir, rel)
        if os.path.isfile(p):
            return p, rel, declared
    # 兜底：季根/series/ 下的 *bible*.md / *圣经*.md
    for sub in ("", "series"):
        d = os.path.join(run_dir, sub) if sub else run_dir
        if not os.path.isdir(d):
            continue
        try:
            for name in sorted(os.listdir(d)):
                if name.lower().endswith(".md") and BIBLE_FALLBACK_RE.search(name) \
                        and "brief" not in name.lower():
                    return os.path.join(d, name), (f"{sub}/{name}" if sub else name), declared
        except OSError:
            pass
    return None, None, declared


def parse_bible_version(text):
    """取圣经 §⓪ 的版本信息；返回 dict(version, date, ep_range, token, evidence, has_mark, block_found)。"""
    out = {"version": None, "date": None, "ep_range": None, "token": None,
           "evidence": None, "has_mark": False, "block_found": False}
    m = BIBLE_MARK_ZERO.search(text) or BIBLE_MARK_TITLE.search(text)
    if not m:
        return out
    out["has_mark"] = True
    # 版本行＝§⓪ 之后到下一个 `## ` 之间的文本（表格行/列表项均可）
    seg = text[m.start():]
    nxt = seg.find("\n## ")
    if nxt > 0:
        seg = seg[:nxt]
    out["block_found"] = True
    # ⚠️ 版本号/生效日期/生效集号常分处 §⓪ 表的三行（如 `| **本册版本号** | v3 |` 与
    #    `| **本册生效日期 / 生效集号** | 2026-09-21 ／ EP01–EP08 |`）⇒ **必须在整段内分别取**，
    #    只盯着"版本号那一行"会把日期/集号漏掉（漏掉就判不出"改了日期但没升版本号"的过期）。
    vm = VER_RE.search(seg)
    dm = DATE_RE.search(seg)
    em = EP_RANGE_RE.search(seg) or EP_ONE_RE.search(seg)
    if vm:
        out["version"] = "v" + (vm.group(1) or vm.group(2))
    if dm:
        out["date"] = f"{dm.group(1)}-{int(dm.group(2)):02d}-{int(dm.group(3)):02d}"
    if em:
        if em.re is EP_RANGE_RE:
            out["ep_range"] = f"EP{int(em.group(1)):02d}-EP{int(em.group(2)):02d}"
        else:
            out["ep_range"] = f"EP{int(em.group(1)):02d}"
    vline = next((ln.strip() for ln in seg.splitlines() if VER_RE.search(ln)), None)
    out["evidence"] = (vline or "(§⓪ 段内未见版本行)")[:150]
    if out["date"] and out["ep_range"]:
        out["evidence"] = (out["evidence"] + f" ／ {out['date']} ／ {out['ep_range']}")[:190]
    parts = [x for x in (out["version"], out["date"], out["ep_range"]) if x]
    out["token"] = " ".join(parts) if parts else None
    return out


def find_briefs(run_dir):
    """列出 (集号, 相对路径, 绝对路径)：季根、EPnn/、扁平式 <slug>-EPnn/ 三处都找 EPnn-brief.md。"""
    found = []
    try:
        entries = sorted(os.listdir(run_dir))
    except OSError:
        return found
    for name in entries:
        full = os.path.join(run_dir, name)
        if os.path.isdir(full) and (EP_DIR_RE.match(name) or EP_FLAT_DIR_RE.match(name)):
            try:
                for sub in sorted(os.listdir(full)):
                    m = BRIEF_RE.match(sub)
                    if m and sub.lower().endswith(".md"):
                        found.append((f"EP{int(m.group(1)):02d}",
                                      f"{name}/{sub}", os.path.join(full, sub)))
            except OSError:
                pass
        else:
            m = BRIEF_RE.match(name)
            if m and name.lower().endswith(".md"):
                found.append((f"EP{int(m.group(1)):02d}", name, full))
    return found


def parse_ref(text):
    """取分集简报里「引用圣经版本」字段值；返回 (值, 命中行) 或 (None, None)。"""
    for i, ln in enumerate(text.splitlines(), 1):
        m = REF_FIELD_RE.search(ln)
        if not m:
            continue
        val = next((g for g in m.groups() if g), "").strip()
        return val, (i, ln.strip())
    return None, None


def ref_tokens(val):
    """把引用值归一为 token（版本号＋日期/集号），用于与圣经当前版本比对。"""
    if not val:
        return None
    vm = VER_RE.search(val)
    dm = DATE_RE.search(val)
    em = EP_RANGE_RE.search(val) or EP_ONE_RE.search(val)
    parts = []
    if vm:
        parts.append("v" + (vm.group(1) or vm.group(2)))
    if dm:
        parts.append(f"{dm.group(1)}-{int(dm.group(2)):02d}-{int(dm.group(3)):02d}")
    if em:
        if em.re is EP_RANGE_RE:
            parts.append(f"EP{int(em.group(1)):02d}-EP{int(em.group(2)):02d}")
        else:
            parts.append(f"EP{int(em.group(1)):02d}")
    return " ".join(parts) if parts else None


def _fail_json(msg, run_dir, code):
    print(json.dumps({"run_dir": os.path.abspath(run_dir) if run_dir else None,
                      "gate_error": msg, "exit_code": code}, ensure_ascii=False, indent=2))
    return code


def main():
    ap = argparse.ArgumentParser(
        add_help=True,
        description="圣经引用版本 pin 门控：圣经 §⓪ 版本行非空 ＋ 每集引用版本＝圣经当前版本（仅剧集项目）")
    ap.add_argument("run_dir", help="runs/<季slug> 目录")
    ap.add_argument("--json", action="store_true", help="JSON 输出（机器可读）")
    ap.add_argument("--via-check-all", action="store_true",
                    help="由 check_all.py 调用（语义一致；保留给未来差异化处置）")
    args = ap.parse_args()

    run_dir = args.run_dir
    if not os.path.isdir(run_dir):
        msg = (f"run 目录不存在或不是目录 —— {run_dir}"
               "（用法: check_bible_pin.py <runs/<季slug>>）")
        if args.json:
            return _fail_json(msg, run_dir, 2)
        print(f"FAIL: {msg}")
        return 2

    if not is_series(run_dir):
        if args.json:
            print(json.dumps({"run_dir": os.path.abspath(run_dir), "series": False,
                              "skipped": True, "reason": "非剧集项目", "exit_code": 2},
                             ensure_ascii=False, indent=2))
        else:
            print(SKIP_NOT_SERIES)
        return 2

    fails, warns, notes = [], [], []
    bible_path, bible_rel, declared = find_bible(run_dir)
    briefs = find_briefs(run_dir)
    notes.append(f"剧集项目：圣经候选 {bible_rel or '（未找到）'}"
                 + (f"（series-config.json 声明 {declared}）" if declared else "")
                 + f"｜分集简报 {len(briefs)} 份")

    # ---------- B1 剧集必须有圣经 ----------
    bible = {"version": None, "token": None, "evidence": None}
    if not bible_path:
        fails.append("[B1] 剧集项目**找不到圣经文件**（候选：`show-bible.md`、`series/show-bible.md`、"
                     "`series-config.json.show_bible_file`）—— 圣经是跨集单一事实源（硬规则 #36②），"
                     "缺圣经 ⇒ 跨集口径无依据、引用版本更无从 pin。处置：按 KSP-E2 产出 "
                     "`<季slug>/show-bible.md`（模板 templates/show-bible.md）")
    else:
        with open(bible_path, encoding="utf-8-sig", errors="ignore") as fh:
            btext = fh.read()
        bible = parse_bible_version(btext)
        if not bible["has_mark"]:
            fails.append(f"[B2] 圣经 `{bible_rel}` **缺 §⓪「本册版本与引用登记」段** —— "
                         "跨项目/衍生片引用圣经必须 pin 版本，圣经自身先要有版本闸。"
                         "处置：按 templates/show-bible.md 补 §⓪（版本号＋生效日期＋生效集号＋引用登记）")
        elif not bible["token"]:
            fails.append(f"[B2] 圣经 `{bible_rel}` 的 §⓪ **版本行为空/不可判**（版本号、生效日期、"
                         f"生效集号三者皆缺）｜证据：{bible['evidence']} —— "
                         "至少写 `v__` ＋ `YYYY-MM-DD` 或 `EP__–EP__`，否则引用方无法判过期")
        else:
            notes.append(f"圣经 `{bible_rel}`：当前版本 = **{bible['token']}**（证据：{bible['evidence']}）")

    # ---------- B3/B4 每集引用版本必须 = 圣经当前版本 ----------
    if not briefs:
        warns.append("[B4] 季目录下**未找到任何分集简报**（`EPnn-brief.md`）—— 可能是尚未开工的季，"
                     "本项不判 FAIL；开工后每集必须补「引用圣经版本」字段（模板 templates/episode-brief.md）")
    for ep, rel, path in briefs:
        with open(path, encoding="utf-8-sig", errors="ignore") as fh:
            t = fh.read()
        val, hit = parse_ref(t)
        if val is None:
            fails.append(f"[B4] `{rel}` **缺「引用圣经版本（路径＋版本号/日期）」字段** —— "
                         "缺字段＝不可判过期＝等于没 pin（模板 templates/episode-brief.md「一、集级基本盘」必填行）")
            continue
        if not val or not ref_tokens(val):
            fails.append(f"[B4] `{rel}` 的「引用圣经版本」**写不出可判版本**（值：`{val}`）—— "
                         "只写「见圣经」不合格，须写路径＋版本号/日期（例：`show-bible.md ｜ v3 ｜ 2026-09-21 生效`）")
            continue
        tk = ref_tokens(val)
        if not bible["token"]:
            notes.append(f"[B3] `{rel}` 引用 `{val}` —— 圣经版本行不可判（已按 B2 计 FAIL），本集比对跳过")
            continue
        if tk != bible["token"]:
            # 比对层次（避免"圣经写全套、引用只写版本号"被误判过期；真正过期＝版本号不同）：
            #   ① 双方都有版本号 ⇒ 版本号不同＝**过期**（圣经改版未回填）；相同＝继续看日期
            #   ② 双方都有日期   ⇒ 日期不同＝**过期**（引用的是旧版生效日）
            #   ③ 引用缺日期/集号（圣经写全）⇒ 不算过期，出 NOTE 提示可写全
            tk_v, tk_d = (tk.split(" ") + [None, None])[0], \
                (tk.split(" ")[1] if len(tk.split(" ")) > 1 else None)
            b_v, b_d = (bible["token"].split(" ") + [None, None])[0], \
                (bible["token"].split(" ")[1] if len(bible["token"].split(" ")) > 1 else None)
            stale = []
            if tk_v and b_v and tk_v != b_v:
                stale.append(f"版本号 {tk_v} ≠ 圣经 {b_v}")
            elif tk_d and b_d and tk_d != b_d:
                stale.append(f"生效日期 {tk_d} ≠ 圣经 {b_d}")
            if stale:
                fails.append(f"[B3] `{rel}` 的**引用圣经版本已过期**（{'；'.join(stale)}）—— "
                             f"该集引用 `{tk}`，圣经当前 `{bible['token']}`（`{bible_rel}`）｜"
                             "**圣经已改版、该集引用过期**：处置＝回填新版本号（并同步该集需重述的口径），"
                             "或走 **KSP-C** 评估回炉范围（承硬规则 #36③ 禁静默改版）")
            else:
                notes.append(f"[B3] `{rel}` 引用 `{val}`（token `{tk}`）与圣经当前 `{bible['token']}` "
                             "**版本号一致**（引用未写全日期/集号，按版本号等价通过）")
        else:
            notes.append(f"[B3] `{rel}` 引用 `{tk}` ＝ 圣经当前版本 ✅")

    exit_code = 1 if fails else 0
    counts = {"fail": len(fails), "warn": len(warns),
              "briefs": len(briefs), "bible": bible_rel,
              "bible_token": bible["token"]}

    if args.json:
        print(json.dumps({
            "run_dir": os.path.abspath(run_dir), "series": True,
            "bible": bible_rel, "bible_token": bible["token"], "bible_evidence": bible["evidence"],
            "declared_show_bible_file": declared,
            "briefs": [{"ep": ep, "path": rel, "ref": parse_ref(open(p, encoding="utf-8-sig",
                                                                     errors="ignore").read())[0]}
                       for ep, rel, p in briefs],
            "fails": fails, "warns": warns, "notes": notes,
            "summary": counts, "exit_code": exit_code,
        }, ensure_ascii=False, indent=2))
        return exit_code

    print(f"圣经版本 pin：圣经 `{bible_rel or '（缺）'}`"
          f"｜当前版本 {bible['token'] or '（不可判）'}｜分集简报 {len(briefs)} 份"
          f"｜FAIL {len(fails)} / WARN {len(warns)}")
    for x in notes:
        print(f"  NOTE {x}")
    for x in warns:
        print(f"  WARN {x}")
    for x in fails:
        print(f"  FAIL {x}")
    if fails:
        print("\nFAIL ❌ 圣经版本 pin 未过（缺圣经/版本行空/集引用过期/简报缺字段）—— "
              "跨项目与衍生片引用圣经必须 pin 版本，防圣经改版后静默过期（硬规则 #36③）")
        return 1
    print("PASS ✅ 圣经 §⓪ 版本行非空，且各集「引用圣经版本」均与圣经当前版本一致")
    return 0


if __name__ == "__main__":
    sys.exit(main())
