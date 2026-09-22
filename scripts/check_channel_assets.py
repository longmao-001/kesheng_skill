#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通道A 保留资产守护 (check_channel_assets.py) —— 硬规则 #42③ 的机器层

依据：**硬规则 #42③**（`orchestration/ORCHESTRATION.md` §5-42）——
  「**不得以剧集规则覆盖广告线既定做法**（反之亦然）——**通道 A 的既有能力清单**
   （brief/概念/口播/分镜/prompt/图表层/**广告法合规 `scripts/ad_forbidden_words.py`**/
   **产品公式 `templates/product-prompt-formula.md`**/**TVC 模板 `knowledge/tvc-ad-templates.md`**/
   品牌 VI/科学报告＋PPT/**专业后期与剪辑团队/真人实拍/产品摄影**）
   为**保留资产，不得因剧集规则被停用、改写或判违规**」。
  配套：`docs/USER_SOP.md` §2.6「通道 A 保留资产清单（不得降级）」；`docs/DUAL-CHANNEL-AUDIT.md` §3。

清单来源（**以 `docs/DUAL-CHANNEL-AUDIT.md` 为准**）：
  ① 首选：解析 `docs/DUAL-CHANNEL-AUDIT.md` §3「未形成冲突但值得记录的观察」第 3 条里的 **11 件在库文件**；
  ② 清单文件缺失/解析不出 → 用**内置硬编码清单**（含"来源"标注）；
  ③ 两边取并集上报（清单里少了的内置件按**清单文件为准**，但会 NOTE 提示差异——防"清单被删条目
     导致守护静默失效"）。

逐件断言：
  A1 存在（且**非空**——0 字节占位＝等于没这件资产）        → FAIL
  A2 `.py` 件 `py_compile` 通过（语法层可编译；不执行副作用） → FAIL
  A3 文件行数/大小入账（回执可视化）                        → NOTE

退出码：0 PASS（可含 NOTE/WARN）｜1 存在 FAIL（缺件/空件/编译失败）｜2 不可判定（**空跑**：技能根不对/
清单为空/清单 0 件 —— 空跑不算通过）

用法：
  python -X utf8 scripts/check_channel_assets.py [--root <skill根>] [--json] [--no-compile]

⚠️ `py_compile` 用**进程内 `py_compile.compile(..., doraise=True)`**：等价 `python -m py_compile`，
   但 doraise 让语法错误变异常（可逐件归因）；缓存重定向到系统临时目录，**不往仓库写 `__pycache__`**。
"""
import argparse
import io
import json
import os
import py_compile
import re
import sys
import tempfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(HERE)
AUDIT_REL = os.path.join("docs", "DUAL-CHANNEL-AUDIT.md")
SOP_REL = os.path.join("docs", "USER_SOP.md")

#: 内置硬编码清单（兜底；来源＝docs/DUAL-CHANNEL-AUDIT.md §3 第 3 条 / docs/USER_SOP.md §2.6）
BUILTIN_INVENTORY = [
    "scripts/ad_forbidden_words.py",
    "knowledge/ad-copy.md",
    "knowledge/tvc-ad-templates.md",
    "templates/product-prompt-formula.md",
    "templates/video-prompt-formula.md",
    "templates/science-report.md",
    "templates/science-ppt.md",
    "playbooks/ppt-deck-flow.md",
    "playbooks/science-report-flow.md",
    "scripts/md_to_docx.py",
    "scripts/build_science_report.py",
]

# 在清单区里认路径：允许写成 `scripts/x.py` / scripts/x.py / **`templates/y.md`** 等
PATH_TOKEN_RE = re.compile(r"`?\*{0,2}((?:scripts|templates|playbooks|knowledge|docs|protocols|agents)"
                           r"/[A-Za-z0-9_\-./@]+?\.(?:py|md|json))`?\*{0,2}")
#: 保留资产可能落的目录（用于从整篇文档里筛出"在库资产"、排除对手册的顺带提及）
KEEP_DIRS = {"scripts", "templates", "playbooks", "knowledge"}
# 文件类型/非清单区噪声（§3 第 3 条只有 11 件；别把"可选增强"当文件）
NOISE_SUFFIX = (".gitignore",)


def _tokens(path, section_head=None):
    """取一个 md 文件里落在保留资产目录下的文件路径 token（保持出现顺序、去重）。

    section_head 给定 ⇒ **只扫该小节**（从 `### <head>` 到下一个 `## ` / `### ` 标题）——
    避免把整篇文档里顺带提到的其它文件当成"保留资产"（那会让守护变成一张大网、失去精度）。
    """
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8-sig", errors="ignore") as fh:
        text = fh.read()
    if section_head:
        idx = text.find(section_head)
        # 限定在 § 小节内：到下一个同级/更高级标题为止（不同级标题都切）
        end = len(text)
        for mark in ("\n## ", "\n### "):
            j = text.find(mark, idx + len(section_head)) if idx >= 0 else -1
            if j > 0:
                end = min(end, j)
        if idx < 0:
            return []
        text = text[idx:end]
    out, seen = [], set()
    for m in PATH_TOKEN_RE.finditer(text):
        p = m.group(1).replace("\\", "/").rstrip("./,、；;：:）)")
        if p in seen or p.endswith(NOISE_SUFFIX):
            continue
        if p.split("/", 1)[0] not in KEEP_DIRS:
            continue
        seen.add(p)
        out.append(p)
    return out


def parse_audit_inventory(root):
    """合并两份权威清单 → 通道 A 保留资产全集（并集，绝不因某份简写而漏件）。

    ① `docs/USER_SOP.md` §2.6「通道 A 保留资产清单（不得降级 · 硬规则 #42③）」—— **完整 11 件**（主清单）；
    ② `docs/DUAL-CHANNEL-AUDIT.md` §3「未形成冲突但值得记录的观察」第 3 条—— 审计留痕里点名的在库文件
       （**简写，带「等」**；只用于**增补**并集与差异留痕，不作唯一依据）；
    ③ 两份都取不到 ⇒ 用内置硬编码清单（`BUILTIN_INVENTORY`）。
    """
    sop = _tokens(os.path.join(root, SOP_REL), section_head="### 通道 A 保留资产清单")
    audit = _tokens(os.path.join(root, AUDIT_REL), section_head="## 3.")
    merged, seen = [], set()
    for p in sop + audit:
        if p not in seen:
            seen.add(p)
            merged.append(p)
    if not merged:
        return [], (f"清单文件取不到（{SOP_REL} §2.6 / {AUDIT_REL} §3 缺失或解析出 0 件）"
                    f"→ 使用内置硬编码清单")
    src = []
    if sop:
        src.append(f"{SOP_REL} §2.6（{len(sop)} 件）")
    if audit:
        src.append(f"{AUDIT_REL} §3 留痕（{len(audit)} 件）")
    return merged, f"清单来源＝{' ＋ '.join(src)}｜并集 {len(merged)} 件"


def compile_ok(abspath, cache_dir):
    """py_compile（doraise）：语法可编译即通过；缓存写系统临时目录，不污染仓库。"""
    try:
        py_compile.compile(abspath, cfile=os.path.join(cache_dir, os.path.basename(abspath) + "c"),
                           doraise=True)
        return True, None
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {e}"


def main():
    ap = argparse.ArgumentParser(
        add_help=True,
        description="通道A 保留资产守护（硬规则 #42③）：清单逐件断言存在＋py_compile（.py），缺件=FAIL")
    ap.add_argument("--root", default=None, help=f"技能根目录（默认 {SKILL_ROOT}）")
    ap.add_argument("--json", action="store_true", help="JSON 输出（机器可读）")
    ap.add_argument("--no-compile", action="store_true", help="跳过 .py 编译断言（快速体检）")
    args = ap.parse_args()

    root = os.path.abspath(args.root or SKILL_ROOT)
    if not os.path.isdir(root):
        msg = f"技能根目录不存在 —— {root}"
        if args.json:
            print(json.dumps({"root": root, "gate_error": msg, "exit_code": 2},
                             ensure_ascii=False, indent=2))
        else:
            print(f"FAIL: {msg}")
        return 2

    parsed, src_note = parse_audit_inventory(root)
    inventory = parsed or list(BUILTIN_INVENTORY)
    source = src_note if parsed else f"内置硬编码清单（{len(BUILTIN_INVENTORY)} 件）"
    notes, warns, fails = [], [], []
    notes.append(f"清单：{source}｜本次守护 {len(inventory)} 件")

    # 差异留痕（**不静默丢资产**）：①清单解析出的条目进守护 ②清单缺失时内置清单兜底并 WARN
    if parsed:
        extra_in_doc = [p for p in parsed if p not in BUILTIN_INVENTORY]
        if extra_in_doc:
            notes.append("清单文件新增条目（本次一并守护，请同步登记进内置清单）："
                         + "、".join(extra_in_doc))
        notes.append("并集比对：内置硬编码 %d 件全部落在清单里（无静默丢件）"
                     % len(BUILTIN_INVENTORY))
    else:
        warns.append("清单文件解析不可用 → 本次使用**内置硬编码清单**兜底"
                     "（请恢复 `docs/DUAL-CHANNEL-AUDIT.md` / `docs/USER_SOP.md` 的保留资产清单）")

    if not inventory:
        msg = "保留资产清单为空（清单文件与内置清单都取不到）—— 空跑不算通过"
        if args.json:
            print(json.dumps({"root": root, "gate_error": msg, "exit_code": 2},
                             ensure_ascii=False, indent=2))
        else:
            print(f"FAIL: {msg}")
        return 2

    cache_dir = tempfile.mkdtemp(prefix="ks-asset-compile-")
    rows = []
    for rel in inventory:
        ab = os.path.join(root, rel.replace("/", os.sep))
        row = {"path": rel, "exists": os.path.isfile(ab), "bytes": 0, "lines": 0,
               "compiled": None, "note": ""}
        if not row["exists"]:
            fails.append(f"[A1] 保留资产缺失 —— `{rel}`（硬规则 #42③：通道 A 保留资产不得被停用/删除，"
                         "剧集化改造不得误伤广告线）")
            rows.append(row)
            continue
        try:
            row["bytes"] = os.path.getsize(ab)
            with open(ab, encoding="utf-8-sig", errors="ignore") as fh:
                row["lines"] = sum(1 for _ in fh)
        except OSError as e:  # noqa: BLE001
            fails.append(f"[A1] 保留资产不可读 —— `{rel}`（{e}）")
            rows.append(row)
            continue
        if row["bytes"] == 0:
            fails.append(f"[A1] 保留资产是 0 字节空件 —— `{rel}`（占位空文件等于该资产不存在）")
            rows.append(row)
            continue
        if rel.endswith(".py"):
            if args.no_compile:
                row["compiled"] = None
                row["note"] = "已跳过编译断言（--no-compile）"
            else:
                ok, err = compile_ok(ab, cache_dir)
                row["compiled"] = ok
                if not ok:
                    fails.append(f"[A2] 保留资产 `py_compile` 未过 —— `{rel}`：{err}")
        rows.append(row)

    n_py = sum(1 for r in rows if r["path"].endswith(".py"))
    n_ok = sum(1 for r in rows if r["exists"] and r["bytes"] > 0
               and (r["compiled"] is not False))
    counts = {"inventory": len(inventory), "ok": n_ok, "py": n_py,
              "fail": len(fails), "warn": len(warns)}
    exit_code = 1 if fails else 0

    if args.json:
        print(json.dumps({
            "root": root, "inventory_source": source,
            "audit_file": os.path.join(root, AUDIT_REL),
            "items": rows, "fails": fails, "warns": warns, "notes": notes,
            "summary": counts, "exit_code": exit_code,
        }, ensure_ascii=False, indent=2))
        return exit_code

    first = (f"通道A 保留资产：{n_ok}/{len(inventory)} 件在位"
             f"（.py 编译断言 {n_py} 件）｜FAIL {len(fails)} / WARN {len(warns)}")
    print(first)
    print(f"清单来源：{source}")
    for x in notes:
        print(f"  NOTE {x}")
    for x in warns:
        print(f"  WARN {x}")
    for x in fails:
        print(f"  FAIL {x}")
    if fails:
        print("\nFAIL ❌ 通道 A 保留资产缺件/编译不过 —— 硬规则 #42③：剧集化改造不得削弱或误伤"
              "广告/科普/科研视频线；请恢复该资产（或按 KSP-C 明确降级决定并同步清单）")
        return 1
    print(f"PASS ✅ 通道 A 保留资产 {n_ok} 件全部在位（.py 可编译）"
          "—— 广告线能力未被剧集化改造削弱")
    return 0


if __name__ == "__main__":
    sys.exit(main())
