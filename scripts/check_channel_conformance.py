#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
判型 × 磁盘形态交叉校验 (check_channel_conformance.py) —— 硬规则 #42④ 的机器层

依据：用户裁定 20260921（双通道并存）＋ `docs/DUAL-CHANNEL-AUDIT.md` ＋ `docs/USER_SOP.md` KSP-01
     · KSP-01 判型后，**通道写进 `brief.md`**（形如 `通道：A` / `通道：B` / `通道：A+B`）——"判型先
       行"（#42④），"是不是剧集"在立项第一步就判死；
     · **判了 B 却不落 E1 配置**（`series-config.json`）→ `scripts/check_all.py` 按磁盘形态把项目当
       **单集/非剧集**，`check_series_consistency.py`（KSP-E4）被**静默跳过**——跨集一致性闸在机器
       层完全不触发，且没有任何报错。**风险形态：最危险的失败是"静默通过"。**
     · 本脚本把"判型承诺"与"磁盘形态"对齐：**判 B（或 A+B）→ 磁盘上必须有剧集形态**；判 A 而
       磁盘上有剧集形态 → WARN（提示判型与形态不一致，可能漏填通道或漏走 KSP-C）。

判据：
  C1  brief.md 通道判定字段       读 `runs/<slug>/brief.md`，取判型字段（`通道：A/B/A+B` 及等价写法）
                                  —— **缺该字段 → WARN**（提示补）；
     C2 判 B / A+B  → 必须有        ① `series-config.json`（E1 产物·跨集闸的配置源，缺 → **FAIL**）
                                     ② 至少一个集结构：`EPnn/` 或等价（`EPnn-*` 文件/扁平式
                                        `<slug>-EPnn/`，缺 → **FAIL**）
     C3  判 A → 磁盘有剧集形态      `series-config.json` 在、或集目录在，但 brief 未标 B →
                                     **WARN**（判型与形态不一致；补通道标注或走 KSP-C 改判）
     C4  无 brief.md                 **跳过**并打印 `[跳过] 未找到 brief.md`（无判型依据，不臆断）
  · **A+B（混用）**：按 B 的形态要求执行（主体走 B 时 E1/E2 前置照走），另出 NOTE 提示"混用须走
    KSP-C 记录"（#42②）。

退出码（沿用"空跑不算通过"原则）：
  0  PASS（可含 WARN/NOTE）
  1  存在 FAIL（判 B 但缺 E1 配置/集结构 —— 跨集闸会被静默跳过）
  2  不可判定/空跑：run 目录不存在、非目录、无 `brief.md`、或 brief 里**读不出通道判定字段**

用法：
  python -X utf8 scripts/check_channel_conformance.py <runs/<项目slug>> [--json] [--brief PATH]

⚠️ 空跑绝不等于通过：无 brief.md / 无通道字段一律 exit 2，绝不输出 PASS。
⚠️ 本脚本**不改判型**（判型是用户拍板项）；它只把"判了 B 却没落 E1 配置"这一静默失效路径变成 FAIL。
"""
import argparse
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ---------------------------------------------------------------- 判型字段解析
# 判型字段：允许中英文冒号/等号、全角、Markdown 强调符（`**通道**：B` / `| **通道判定** | 通道 B |`）
#   例：`通道：A` / `**通道**：B` / `通道＝A+B` / `通道: A / B` / `（通道：A＋B）`
# 两类字段名（互斥优先）：`通道判定/通道类型/通道归属`（值可隔表格竖线） ｜ 裸 `通道`（值须紧跟分隔符）
CHANNEL_FIELD = (r"(?:\*\*|__)?\s*(?:判定|类型|归属)\s*(?:\*\*|__)?"
                 r"|(?=(?:\*\*|__)?\s*[:：=＝])")
CHANNEL_LINE_RE = re.compile(
    r"通道\s*(?:\*\*|__)?\s*"                            # 字段名（可带强调符）
    r"(?:" + CHANNEL_FIELD + r")"                        # ⚠️ 必须成组：否则 | 会把整个正则劈成两条
    r"[\s｜|]*[:：=＝]?[\s｜|*_]*"                        # 分隔符（判定型可省/隔竖线）
    r"(?P<val>[ABCＡＢＣ](?:\s*[+＋/、]\s*[ABCＡＢＣ])?)",  # 值：A / B / C / A+B / A+C / A/B
    re.I,
)
# 裸「通道 A」「通道走 A」的直述写法（无冒号/等号）
CHANNEL_INLINE_RE = re.compile(
    r"通道\s*(?:是|为|走)?\s*(?P<val>[ABCＡＢＣ](?:\s*[+＋/、]\s*[ABCＡＢＣ])?)(?![0-9A-Za-z])",
    re.I,
)
FULLWIDTH = str.maketrans("ＡＢＣ＋", "ABC+")

# 集结构：目录 EPnn/ ；文件 EPnn-*.md ；扁平式 <slug>-EPnn/
EP_DIR_RE = re.compile(r"^EP\s*\d{1,2}$", re.I)
EP_FLAT_DIR_RE = re.compile(r"-EP\s*\d{1,2}$", re.I)
EP_FILE_RE = re.compile(r"^EP\s*\d{1,2}[^0-9]", re.I)
SERIES_CONFIG = "series-config.json"

SKIP_NO_BRIEF = "[跳过] 未找到 brief.md"


def _norm(raw):
    """把命中的值归一为 'A' / 'B' / 'C' / 'A+B' / 'A+C'（多通道混写按升序用 '+' 连接）。"""
    if not raw:
        return None
    letters = re.findall(r"[ABC]", raw.translate(FULLWIDTH), re.I)
    up = sorted({c.upper() for c in letters})
    return "+".join(up) if up else None


def parse_channel(text):
    """从 brief.md 文本取通道判定；返回 (归一化通道, 命中原行, 行号) 或 (None, None, None)。

    一行内可能多次出现「通道」字样（如 Markdown 表格 `| **通道判定** | 通道 B |`）——
    逐次取匹配，直到**真的读出 A/B 值**为止（字段名出现在前、值在后时不漏读）。
    """
    lines = text.splitlines()
    for i, ln in enumerate(lines, 1):
        for m in CHANNEL_LINE_RE.finditer(ln):
            ch = _norm(m.group("val") if "val" in m.groupdict() else None)
            if ch:
                return ch, ln.strip(), i
    # 退一步：无分隔符的行内直述（`通道 A` / `通道走 B`）
    for i, ln in enumerate(lines, 1):
        for m in CHANNEL_INLINE_RE.finditer(ln):
            ch = _norm(m.group("val") if "val" in m.groupdict() else None)
            if ch:
                return ch, ln.strip(), i
    return None, None, None


def disk_form(run_dir):
    """磁盘形态：返回 (有 series-config.json, 集结构证据 list)。"""
    has_cfg = os.path.isfile(os.path.join(run_dir, SERIES_CONFIG))
    eps = []
    try:
        for name in sorted(os.listdir(run_dir)):
            full = os.path.join(run_dir, name)
            if os.path.isdir(full) and (EP_DIR_RE.match(name) or EP_FLAT_DIR_RE.match(name)):
                eps.append(name + "/")
            elif os.path.isfile(full) and EP_FILE_RE.match(name):
                eps.append(name)
    except OSError:
        pass
    return has_cfg, eps


def main():
    ap = argparse.ArgumentParser(
        add_help=True,
        description="判型 × 磁盘形态交叉校验（硬规则 #42④）：判 B 却缺 series-config.json/EPnn 集结构 = FAIL")
    ap.add_argument("run_dir", help="runs/<项目slug> 目录")
    ap.add_argument("--json", action="store_true", help="JSON 输出（机器可读）")
    ap.add_argument("--brief", default=None, help="显式指定 brief.md 路径（默认 <run目录>/brief.md）")
    args = ap.parse_args()

    run_dir = args.run_dir
    if not os.path.isdir(run_dir):
        msg = f"run 目录不存在或不是目录 —— {run_dir}（用法: check_channel_conformance.py <runs/<项目slug>>）"
        if args.json:
            print(json.dumps({"run_dir": os.path.abspath(run_dir), "gate_error": msg,
                              "exit_code": 2}, ensure_ascii=False, indent=2))
        else:
            print(f"FAIL: {msg}")
        return 2

    brief = args.brief or os.path.join(run_dir, "brief.md")
    if not os.path.isfile(brief):
        if args.json:
            print(json.dumps({"run_dir": os.path.abspath(run_dir), "brief": None,
                              "skipped": True, "reason": "未找到 brief.md",
                              "exit_code": 2}, ensure_ascii=False, indent=2))
        else:
            print(SKIP_NO_BRIEF)
            print("（无判型依据 → 本门控不臆断通道；请先按 KSP-01 判型并在 brief.md 写死通道）")
        return 2

    with open(brief, encoding="utf-8-sig", errors="ignore") as fh:
        text = fh.read()
    channel, hit_line, hit_no = parse_channel(text)
    has_cfg, eps = disk_form(run_dir)
    fails, warns, notes = [], [], []

    if channel is None:
        has_cfg0, eps0 = disk_form(run_dir)
        msg = (f"brief.md 缺「通道判定」字段（判型先行·硬规则 #42④）—— "
               "请在 brief.md 写死一行，形如 `通道：A` / `通道：B` / `通道：A+B` / `通道：C`"
               "（模棱两可默认 A；判型是用户拍板项，承 docs/USER_SOP.md KSP-01 通道判定卡）")
        form0 = ("剧集形态（series-config.json 在）" if has_cfg0
                 else ("有集结构 " + ", ".join(eps0[:4]) if eps0 else "单集/广告片形态"))
        extra = []
        if has_cfg0 or eps0:
            extra.append("⚠️ 磁盘形态已达剧集标准（" + form0 + "），**但判型未落盘** —— "
                         "判型不可判、跨集闸照样会被跳过；KSP-01 判型卡必须回填 brief.md "
                         "（剧集 ⇒ 写 `通道：B`；确为通道 A（广告/科普/科研，多版本）⇒ 说明为何"
                         "存在 series-config.json/EPnn 并走 KSP-C 改判）")
        if args.json:
            print(json.dumps({"run_dir": os.path.abspath(run_dir), "brief": os.path.abspath(brief),
                              "channel": None, "warns": [msg], "notes": extra,
                              "disk": {"series_config": has_cfg0, "ep_structures": eps0, "form": form0},
                              "note": "缺通道字段 → 判型不可判定（WARN 提示补字段，按空跑 exit 2）",
                              "summary": {"fail": 0, "warn": 1 + len(extra)}, "exit_code": 2},
                             ensure_ascii=False, indent=2))
        else:
            print(f"WARN 通道判定字段缺失｜磁盘形态 {form0}｜FAIL 0 / WARN {1 + len(extra)}")
            print(f"  WARN {msg}")
            for x in extra:
                print(f"  WARN {x}")
            print("不可判定（exit 2）：无通道字段 ⇒ 判型未落盘，本门控不作 PASS/FAIL 结论")
        return 2

    # ---- C1 判型字段已读出（缺字段的 WARN 分支在上面 exit 2 已覆盖）----
    notes.append(f"判型：通道 {channel}（来源 {os.path.relpath(brief, run_dir).replace(os.sep, '/')}:{hit_no}）")

    # ---- C2 判 B / A+B → 必须有 series-config.json ＋ 至少一个集结构 ----
    if channel in ("B", "A+B"):
        if not has_cfg:
            fails.append(
                f"[C2] 判了通道 {channel} 但磁盘上无 {SERIES_CONFIG} —— "
                "KSP-E1（全季分集大纲）产物缺失 ⇒ check_all.py 按磁盘形态判为"
                "单集/非剧集项目，check_series_consistency.py（KSP-E4 跨集一致性闸）被**静默跳过**。"
                "处置：先补 KSP-E1/E2 前置并产出 <季slug>/series-config.json（模板 templates/series-config.json），"
                "再开工单集（承硬规则 #35/#40）")
        if not eps:
            fails.append(
                f"[C2] 判了通道 {channel} 但磁盘上无任何集结构（EPnn/ 目录、EPnn-*.md 或扁平式 "
                "<slug>-EPnn/）—— 剧集产物须按集组织（硬规则 #40①）；"
                "无集结构 ⇒ 跨集层门控无输入 ⇒ 跨集一致性闸形同不存在")
        if channel == "A+B":
            notes.append("通道 A+B（混用）：按 B 的形态要求执行；主通道链路为准，"
                         "**混用/切换须走 KSP-C 变更决策卡留痕**（硬规则 #42②，禁静默切换）")

    # ---- C3 判 A → 磁盘却有剧集形态 = 判型与形态不一致 ----
    if channel == "A":
        if has_cfg:
            warns.append(
                f"[C3] brief.md 判为通道 A，但磁盘上存在 {SERIES_CONFIG} —— 判型与形态不一致："
                "①若项目确为剧集 ⇒ 补写 `通道：B`（判型写死）并走 KSP-C；"
                "②若确为通道 A（广告/科普/科研，含多版本交付）⇒ 该配置/集目录属剧集形态误挂，"
                "通道 A 应按「项目 slug ＋ 版本子目录」组织、**禁套 EPnn/**（硬规则 #40 限定语）")
        if eps:
            warns.append(
                f"[C3] brief.md 判为通道 A，但磁盘上有集结构 {', '.join(eps[:6])}"
                f"{'…' if len(eps) > 6 else ''} —— 判型与形态不一致（同 C3 处置两种方向）")

    # ---- 汇总 ----
    disk_desc = ("剧集形态（series-config.json 在；集结构 " + (", ".join(eps[:4]) + ("…" if len(eps) > 4 else ""))
                 + ")" if has_cfg and eps else
                 ("仅 series-config.json（无集结构）" if has_cfg else
                  ("仅集结构 " + ", ".join(eps[:4]) + ("…" if len(eps) > 4 else "") if eps else
                   "单集/广告片形态（无 series-config.json、无 EPnn/）")))
    exit_code = 1 if fails else 0

    if args.json:
        print(json.dumps({
            "run_dir": os.path.abspath(run_dir),
            "brief": os.path.abspath(brief),
            "channel": channel, "channel_evidence": hit_line, "channel_line": hit_no,
            "disk": {"series_config": has_cfg, "ep_structures": eps, "form": disk_desc},
            "fails": fails, "warns": warns, "notes": notes,
            "summary": {"fail": len(fails), "warn": len(warns), "note": len(notes)},
            "exit_code": exit_code,
        }, ensure_ascii=False, indent=2))
        return exit_code

    first = f"通道判定 {channel}｜磁盘形态 {disk_desc}｜FAIL {len(fails)} / WARN {len(warns)}"
    print(first)
    print(f"简报：{os.path.relpath(brief, run_dir).replace(os.sep, '/')}（判型行 L{hit_no}）")
    for x in notes:
        print(f"  NOTE {x}")
    for x in warns:
        print(f"  WARN {x}")
    for x in fails:
        print(f"  FAIL {x}")
    if fails:
        print("\nFAIL ❌ 判型承诺与磁盘形态不一致 —— 修复方向："
              "①补 E1/E2 前置并产出 series-config.json；②或按 KSP-C 改判通道并同步 brief.md"
              "（判型是用户拍板项，脚本不改判）")
        return 1
    print("PASS ✅ 判型与磁盘形态一致（跨集闸不会被静默跳过）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
