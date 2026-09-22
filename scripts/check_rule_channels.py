#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规则通道标注门控 (check_rule_channels.py) —— 硬规则 #42① 的机器层

依据：**硬规则 #42①**（`orchestration/ORCHESTRATION.md` §5-42）——
  「**新规则一律须标注适用通道**——每条新硬规则/门禁/模板，须写明
   「全通道通用／仅剧集／仅 AI 原生动画／仅广告（通道 A）」，**未标注适用通道的规则不得入库**
   （＝该规则将来必被误用）」；配套 `docs/DUAL-CHANNEL-AUDIT.md`（#24–#41 逐条适用通道＋限定语）。

扫什么：`orchestration/ORCHESTRATION.md` 的 **§5 硬规则**区（`## 5. 硬规则` → 下一个 `## ` 标题）。
       逐条 `#NN`（`N. **...**` 起条，含其后的 `- ` 缩进限定语行）取整块文本，检查是否带**适用通道标注**。

标注约定（任一命中即算带标注；大小写/全半角容错）：
  ① `【通道：通用】` / `【通道：A】` / `【通道：B】` / `【通道：A+B】`（约定形）
  ② `（适用：A/B）` / `（适用：全通道通用）` / `适用通道：仅剧集` 等「适用(通道)」式
  ③ 规则正文明写适用面：`全通道通用` / `通道 A 专属` / `仅剧集（通道 B）` / `仅 AI 原生动画` 等
  ④ 本仓既有的**限定语**落盘写法：`限定（限定来源＝双通道审计 20260921）`

判定：
  R1  **标注阈值内**（默认 #NN ≤ 42 · `--annotation-from` 可改）——历史条目：
      #24–#41 已由 `docs/DUAL-CHANNEL-AUDIT.md` 审计表逐条给出适用通道与限定语 ⇒ 视为已覆盖（NOTE）；
      **#1–#23 与 #42** 无标注 ⇒ 默认视为「通用」仅 **WARN**（不回填，避免历史条目阻塞门控）；
  R2  **超出阈值**（默认 #NN ≥ 43，即**新增规则**）无标注 ⇒ **FAIL**（= "未标注适用通道的规则不得入库"）；
  R3  规则块内标注写法不合法（如 `【通道：X】` 非 A/B/通用/混用枚举）⇒ **FAIL**（防随手写坏）；
  R4  规则区**一条规则都解析不到**（区段缺失/标题改名/文件缺）⇒ **exit 2**（空跑不算通过）。

「非阻断档」：本门控**以 WARN 为主**（历史 42 条不回填不阻断）；**只有新增规则（#≥43）缺标注**
          才 FAIL —— 既守住 #42①「新规则未标注不得入库」，又不因历史条目把整条链路卡死。

退出码：0 PASS（可含 WARN/NOTE）｜1 存在 FAIL（新增规则缺标注/标注非法）｜2 不可判定（空跑）

用法：
  python -X utf8 scripts/check_rule_channels.py [--file PATH] [--annotation-from NN] [--json]

⚠️ 空跑绝不等于通过：0 条规则/找不到 §5 硬规则区一律 exit 2。
⚠️ 本门控**只查"有没有标注"**，不判定标注内容对不对（内容正确性由 `docs/DUAL-CHANNEL-AUDIT.md` 审计）。
"""
import argparse
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(HERE)
DEFAULT_FILE = os.path.join(SKILL_ROOT, "orchestration", "ORCHESTRATION.md")

# 硬规则区：`## 5. 硬规则` → 下一个二级标题
SECTION_RE = re.compile(r"^##\s*5\.?\s*硬规则\s*$", re.M)
NEXT_SECTION_RE = re.compile(r"^##\s+\S", re.M)
# 规则起条：`42. **双通道并存…**`（允许 3 空格内缩进、全角句点）
RULE_RE = re.compile(r"^(?: {0,3})(\d{1,3})\s*[.、．]\s*\S")
# 规则块边界：下一条起条前的所有行；块终止于空行＋非缩进行（由解析逻辑控制）
CONT_LINE_RE = re.compile(r"^(?: {2,}|\t|-{1,2}\s|\s{3,})\S")

# ---------- 标注识别（任一命中即算带标注） ----------
ANN_BRACKET_RE = re.compile(
    r"【\s*通道\s*[:：]\s*(?P<v>[^】]{0,20}?)】"
    r"|（\s*通道\s*[:：]\s*(?P<v2>[^）]{0,20}?)）"
    r"|\(\s*通道\s*[:：]\s*(?P<v3>[^)]{0,20}?)\)"
)
ANN_APPLY_RE = re.compile(
    r"适用(?:的)?通道\s*[:：=＝]\s*(?P<v>[^\n，。；)）]{1,24})"
    r"|（\s*适用\s*[:：]\s*(?P<v2>[^）]{1,24})）"
    r"|\(\s*适用\s*[:：]\s*(?P<v3>[^)]{1,24})\)"
)
# 正文明写适用面（含既有「限定」写法）—— 只认**显式适用面断言**，不认规则正文里顺带的「通道 B」等提及
ANN_INLINE_RE = re.compile(
    r"全通道通用|全通道适用|全通道保留|全通道无豁免|两通道共用|两通道通用"
    r"|本(?:条|规则)\s*仅适用(?:于)?\s*[^\n，。；]{0,24}"
    r"|本(?:条|规则)\s*适用(?:于)?\s*[^\n，。；]{0,24}"
    r"|适用(?:通道|范围)\s*[:：=＝]"
    r"|限定（限定来源＝双通道审计",
)
VALID_ANN_TOKENS = re.compile(r"通用|全通道|A|B|动画|剧集|广告|水墨|混用|两通道")


def find_section(text):
    """返回 §5 硬规则区文本 (start_line, section_text) 或 (None, None)。"""
    m = SECTION_RE.search(text)
    if not m:
        return None, None
    start = m.end()
    nxt = NEXT_SECTION_RE.search(text, start)
    end = nxt.start() if nxt else len(text)
    return text[:m.start()].count("\n") + 1, text[start:end]


def parse_rules(section, base_line):
    """把 §5 区解析成 [{num, line, body}]（body＝该规则起条行＋其后缩进/连行）。"""
    rules = []
    cur = None
    for i, ln in enumerate(section.splitlines()):
        m = RULE_RE.match(ln)
        if m:
            if cur:
                rules.append(cur)
            cur = {"num": int(m.group(1)), "line": base_line + i + 1, "body": [ln]}
            continue
        if cur is None:
            continue
        if not ln.strip():                      # 空行：向后看是否仍有缩进连行
            cur["body"].append(ln)
            continue
        if CONT_LINE_RE.match(ln) or ln.startswith(" "):
            cur["body"].append(ln)
            continue
        # 非缩进新内容 = 该规则块结束
        rules.append(cur)
        cur = None
    if cur:
        rules.append(cur)
    for r in rules:
        r["text"] = "\n".join(r["body"]).strip()
    return rules


def detect_annotation(body):
    """返回 (有无标注, 标注原文或 None, 是否写法非法)。"""
    for rx in (ANN_BRACKET_RE, ANN_APPLY_RE):
        m = rx.search(body)
        if m:
            raw = m.group(0)
            val = next((g for g in m.groups() if g), "")
            ok = bool(VALID_ANN_TOKENS.search(val))
            return True, raw, (not ok)
    m = ANN_INLINE_RE.search(body)
    if m:
        return True, m.group(0), False
    return False, None, False


def main():
    ap = argparse.ArgumentParser(
        add_help=True,
        description="规则通道标注门控（硬规则 #42①）：扫 ORCHESTRATION §5 硬规则区，逐条查适用通道标注")
    ap.add_argument("--file", default=None, help=f"手册路径（默认 {DEFAULT_FILE}）")
    ap.add_argument("--annotation-from", type=int, default=43, metavar="NN",
                    help="从第 NN 条起为『新规则』，缺标注即 FAIL（默认 43＝#42 之后新增）")
    ap.add_argument("--json", action="store_true", help="JSON 输出（机器可读）")
    args = ap.parse_args()

    path = args.file or DEFAULT_FILE
    if not os.path.isfile(path):
        msg = (f"手册文件不存在 —— {path}"
               "（用法: check_rule_channels.py [--file orchestration/ORCHESTRATION.md]）")
        if args.json:
            print(json.dumps({"file": os.path.abspath(path), "gate_error": msg,
                              "exit_code": 2}, ensure_ascii=False, indent=2))
        else:
            print(f"FAIL: {msg}")
        return 2

    with open(path, encoding="utf-8-sig", errors="ignore") as fh:
        text = fh.read()
    base_line, section = find_section(text)
    if section is None:
        msg = (f"找不到 `## 5. 硬规则` 区段 —— {os.path.basename(path)}"
               "（区段标题被改名/删除 ⇒ 无法判定，空跑不算通过）")
        if args.json:
            print(json.dumps({"file": os.path.abspath(path), "gate_error": msg,
                              "exit_code": 2}, ensure_ascii=False, indent=2))
        else:
            print(f"FAIL: {msg}")
        return 2

    rules = parse_rules(section, base_line)
    if not rules:
        msg = (f"§5 硬规则区解析出 0 条规则（起条格式应为 `N. **…**`）—— "
               f"{os.path.basename(path)} L{base_line} 起（空跑不算通过）")
        if args.json:
            print(json.dumps({"file": os.path.abspath(path), "section_line": base_line,
                              "gate_error": msg, "exit_code": 2}, ensure_ascii=False, indent=2))
        else:
            print(f"FAIL: {msg}")
        return 2

    fails, warns, notes, annotated = [], [], [], []
    legacy_cov, legacy_warn, illegal = [], [], []

    for r in rules:
        has, raw, bad = detect_annotation(r["text"])
        tag = f"#{r['num']}(L{r['line']})"
        if has and not bad:
            annotated.append((tag, raw))
        elif has and bad:
            illegal.append((tag, raw))
        elif r["num"] >= args.annotation_from:
            fails.append(
                f"[R2] 新增规则 {tag} **缺适用通道标注** —— 硬规则 #42①：新规则须写明"
                "「全通道通用／仅剧集／仅 AI 原生动画／仅广告（通道 A）」，未标注不得入库。"
                f"处置：在该规则末尾补 `【通道：通用】` 或 `（适用：A/B）`（原文见 {os.path.basename(path)}）")
        elif 24 <= r["num"] <= 41:
            legacy_cov.append(tag)
        elif r["num"] == 42:
            # #42 自带适用面正文（"全通道通用"），detect_annotation 应已命中；兜底归入"已验证"层
            notes.append(f"#42(L{r['line']}) 未见结构化标注，但正文含适用面断言（本条为双通道铁则）")
        else:
            legacy_warn.append(tag)
            warns.append(
                f"[R1] 历史规则 {tag} 无适用通道标注 —— 默认视为「通用」（仅 WARN，不回填）；"
                "后续这些规则若被改动/复用，须按 #42① 补标注")

    for tag, raw in illegal:
        fails.append(
            f"[R3] 规则 {tag} 的通道标注写法非法（`{raw}`）—— 枚举只允许 "
            "通用／全通道／A／B／A+B（混用）／仅剧集／仅 AI 原生动画／仅广告，"
            "请改成 `【通道：通用】` 这类约定形")

    if legacy_cov:
        notes.append("历史条目 #" + "/#".join(re.sub(r"^#(\d+)\(L\d+\)$", r"\1", t) for t in legacy_cov)
                     + " 未写内联标注，但已由 `docs/DUAL-CHANNEL-AUDIT.md` 审计表逐条给出"
                       "适用通道与限定语 ⇒ 视为已覆盖（本次不判 FAIL）")
        # 兜底：审计表缺失时把"已覆盖"降级为 WARN（防"审计表删了，覆盖就成了空口"）
        audit = os.path.join(SKILL_ROOT, "docs", "DUAL-CHANNEL-AUDIT.md")
        if not os.path.isfile(audit):
            warns.append("[R1] `docs/DUAL-CHANNEL-AUDIT.md` 不存在 —— #24–#41 的『已覆盖』失去依据，"
                         "请恢复审计表或为这些条目补内联标注")

    counts = {"total": len(rules), "annotated": len(annotated),
              "legacy_covered": len(legacy_cov), "legacy_generic": len(legacy_warn),
              "fail": len(fails), "warn": len(warns)}
    exit_code = 1 if fails else 0

    if args.json:
        print(json.dumps({
            "file": os.path.abspath(path), "section_line": base_line,
            "annotation_from": args.annotation_from,
            "rules": [{"num": r["num"], "line": r["line"]} for r in rules],
            "annotated": [{"rule": t, "annotation": a} for t, a in annotated],
            "legacy_covered_24_42": legacy_cov, "legacy_generic": legacy_warn,
            "fails": fails, "warns": warns, "notes": notes,
            "summary": counts, "exit_code": exit_code,
        }, ensure_ascii=False, indent=2))
        return exit_code

    print(f"规则通道标注：共 {counts['total']} 条硬规则｜带标注 {counts['annotated']}"
          f"｜审计表覆盖 {counts['legacy_covered']}｜历史默认通用 {counts['legacy_generic']}"
          f"｜FAIL {counts['fail']} / WARN {counts['warn']}")
    print(f"手册：{os.path.relpath(path, SKILL_ROOT).replace(os.sep, '/')}（§5 硬规则 L{base_line} 起）"
          f"｜新增规则阈值 #≥{args.annotation_from}")
    if annotated:
        covered = "；".join(f"#{re.sub(r'^#(\\d+).*', r'\\1', t)}「{a}」" for t, a in annotated[:12])
        print(f"  NOTE 已带标注：{covered}{'…' if len(annotated) > 12 else ''}")
    for x in notes:
        print(f"  NOTE {x}")
    for x in warns:
        print(f"  WARN {x}")
    for x in fails:
        print(f"  FAIL {x}")
    if fails:
        print("\nFAIL ❌ 新增硬规则未标注适用通道 —— 按 #42① 补 `【通道：…】` 后再入库")
        return 1
    print("PASS ✅ 新增规则（#≥%d）均有适用通道标注；历史条目按审计表覆盖/默认通用（WARN 不阻断）"
          % args.annotation_from)
    return 0


if __name__ == "__main__":
    sys.exit(main())
