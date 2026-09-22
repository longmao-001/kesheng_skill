#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档计数不漂移守护 (check_readme_counts.py) —— **技能级**门控（与项目无关）

来由：总览类文档（README.md 等）里的件数/条数最容易凭记忆写、写完就飘——
      「README 写 8 项门控、实际 16 项」这类漂移**不会**被任何现有门控发现（check_docs_integrity
      只查断链/孤岛，不查数字）。本脚本把**声明值**与**现场实测值**钉在一起。

用法:
  python -X utf8 scripts/check_readme_counts.py            # 人读报告
  python -X utf8 scripts/check_readme_counts.py --json     # 机器可读

实测口径（每次现场数，**禁凭记忆**）:
  1. playbooks 件数 ......... playbooks/ 下全部文件（递归，排除 __pycache__）
  2. templates 件数 ......... templates/ 下全部文件（含 *.json 通道配置）
  3. scripts 件数 ........... scripts/ 下全部文件（含 *.md 说明与 asset_schema.md）
  4. agents 件数 ............ agents/ 下全部文件（角色卡）
  5. docs 件数（md） ........ docs/ 下 *.md（**PNG/PDF 图示成品单列，不计入**）
  6. 硬规则条数 ............. orchestration/ORCHESTRATION.md「## 5. 硬规则」区内 `N. **` 条目
                             （去重；正常应为 1..N 连续 → 条数 = N）
  7. check_all 门控项数（满配） scripts/check_all.py **AST 静态解析**：`checks` 列表字面量元素
                             ＋ 任意 `checks.insert/append(...)` 调用（含条件分支）＝**上限**
                             （条件项：素材类 +1、剧集类 +2；非此类项目 check_all 打印 `[跳过]`）
  8. 用户拍板点 ............. templates/user-gate.md 速查表编号行（1..N）——权威清单
  9. FAILURE-LIBRARY 编号上限 knowledge/FAILURE-LIBRARY.md 内出现的 `F-NN` 最大值
 10. SOP-FLOW 门控项数声明 .. docs/SOP-FLOW.md 里 `单集 N 项` / `满配 N 项` 自洽性

声明来源（正则，**只认文档里真写着的数字**）:
  README.md ......... 目录结构块 `dir/ (N)`；`硬规则 1-NN`；`一键 N 项`；`N 个拍板点`
  knowledge/index.md  `F-01…F-NN`
  docs/SOP-FLOW.md .. `单集 N 项`；`满配 N 项`

退出码:
  0 = 全部声明与实测一致（PASS）
  1 = 有**计数漂移**（FAIL，逐条列出「写 X / 实际 Y」）
  2 = **文件缺失或声明缺失**（不可判定——**不当通过**；补文件/补声明后重跑）

接入: `scripts/check_all.py`（技能级项，随 `check_docs_integrity` / `check_rule_channels` 一同常跑）
"""
import argparse
import ast
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                      # 技能根 = C:\Users\Win10\.dsh\skills\kesheng

README = os.path.join(ROOT, "README.md")
INDEX = os.path.join(ROOT, "knowledge", "index.md")
SOPFLOW = os.path.join(ROOT, "docs", "SOP-FLOW.md")
ORCH = os.path.join(ROOT, "orchestration", "ORCHESTRATION.md")
CHECKALL = os.path.join(HERE, "check_all.py")
USERGATE = os.path.join(ROOT, "templates", "user-gate.md")
FAILLIB = os.path.join(ROOT, "knowledge", "FAILURE-LIBRARY.md")


# ---------------------------------------------------------------- 现场实测

def _files(rel, suffix=None):
    """递归列件（排除 __pycache__）；suffix 为 None 时全收。"""
    d = os.path.join(ROOT, rel.replace("/", os.sep))
    out = []
    for base, dirs, names in os.walk(d):
        dirs[:] = [x for x in dirs if x != "__pycache__"]
        for n in names:
            if suffix and not n.endswith(suffix):
                continue
            out.append(os.path.join(base, n))
    return sorted(out)


def count_dir(rel, suffix=None):
    return len(_files(rel, suffix))


def count_rules():
    """ORCHESTRATION §5 硬规则条数：取 §5 区内 `N. **` 去重编号，校验 1..max 连续。"""
    txt = read_text(ORCH)
    lines = txt.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if re.match(r"^##\s*5\.", ln):
            start = i
            break
    if start is None:
        raise AssertionError("ORCHESTRATION.md 未找到「## 5. 硬规则」标题")
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^##\s", lines[j]):
            end = j
            break
    nums = []
    for ln in lines[start:end]:
        m = re.match(r"^\s*(\d{1,2})\.\s+\*\*", ln)
        if m:
            nums.append(int(m.group(1)))
    uniq = sorted(set(nums))
    if not uniq:
        raise AssertionError("§5 硬规则区未解析到任何 `N. **` 条目")
    if uniq != list(range(1, uniq[-1] + 1)):
        raise AssertionError(f"§5 硬规则编号不连续：{uniq}")
    if len(uniq) != len(nums):
        raise AssertionError("§5 硬规则存在重复编号")
    return uniq[-1]


def count_check_all():
    """check_all.py 门控项数（满配）：AST 解析 checks 列表 ＋ checks.insert/append 调用。"""
    src = read_text(CHECKALL)
    tree = ast.parse(src)
    total = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if (isinstance(t, ast.Name) and t.id == "checks"
                        and isinstance(node.value, ast.List)):
                    total += len(node.value.elts)
        if isinstance(node, ast.Call):
            fn = node.func
            if (isinstance(fn, ast.Attribute) and fn.attr in ("insert", "append")
                    and isinstance(fn.value, ast.Name) and fn.value.id == "checks"):
                total += 1
    if total == 0:
        raise AssertionError("check_all.py 未解析到 checks 门控清单")
    return total


def count_user_gates():
    """templates/user-gate.md 速查表编号行 1..N。"""
    txt = read_text(USERGATE)
    nums = sorted({int(m.group(1)) for m in re.finditer(r"(?m)^\|\s*(\d{1,2})\s*\|", txt)})
    if not nums:
        raise AssertionError("user-gate.md 未解析到编号拍板点行")
    if nums != list(range(1, nums[-1] + 1)):
        raise AssertionError(f"user-gate.md 拍板点编号不连续：{nums}")
    return nums[-1]


def count_failure_library():
    """FAILURE-LIBRARY.md 内 F-NN 最大值。"""
    txt = read_text(FAILLIB)
    f = sorted({int(m.group(1)) for m in re.finditer(r"F-(\d{2,3})", txt)})
    if not f:
        raise AssertionError("FAILURE-LIBRARY.md 未解析到 F-NN 编号")
    missing = [n for n in range(1, f[-1] + 1) if n not in f]
    if missing:
        raise AssertionError(f"FAILURE-LIBRARY 编号缺口：{missing}")
    return f[-1]


# ---------------------------------------------------------------- 读文档 / 抽声明

def read_text(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def linea(path, pattern):
    """返回 [(行号, 匹配文本)]，供「写 X/Y 在第几行」定位。"""
    out = []
    for i, ln in enumerate(read_text(path).splitlines(), 1):
        if re.search(pattern, ln):
            out.append((i, ln.strip()))
    return out


class Report:
    def __init__(self):
        self.rows = []      # (metric, actual, ok, decls)
        self.drift = []     # (metric, actual, src, line, declared)
        self.missing = []   # (what, path)
        self.errors = []    # 解析异常

    def add(self, metric, actual, decls):
        """decls = [(src, line, value)]；value=None 表示该处未声明。"""
        if not decls:
            self.missing.append((metric, "（声明缺失）"))
            self.rows.append((metric, actual, None, []))
            return
        ok = all(v == actual for _, _, v in decls)
        if not ok:
            for src, line, v in decls:
                if v != actual:
                    self.drift.append((metric, actual, src, line, v))
        self.rows.append((metric, actual, ok, decls))


def main():
    ap = argparse.ArgumentParser(description="文档计数不漂移守护")
    ap.add_argument("--json", action="store_true", help="机器可读输出")
    a = ap.parse_args()

    rep = Report()
    need = [README, INDEX, SOPFLOW, ORCH, CHECKALL, USERGATE, FAILLIB]
    for p in need:
        if not os.path.exists(p):
            rep.missing.append(("文件缺失", p))
    if rep.missing:
        _emit_missing(rep, a.json)
        sys.exit(2)

    # ---- 实测
    try:
        actual = {
            "playbooks": count_dir("playbooks"),
            "templates": count_dir("templates"),
            "scripts": count_dir("scripts"),
            "agents": count_dir("agents"),
            "docs_md": count_dir("docs", ".md"),
            "rules": count_rules(),
            "check_all": count_check_all(),
            "user_gates": count_user_gates(),
            "failures": count_failure_library(),
        }
    except (AssertionError, SyntaxError) as e:            # noqa: BLE001
        rep.errors.append(str(e))
        _emit_missing(rep, a.json)
        sys.exit(2)

    readme = read_text(README)
    index = read_text(INDEX)
    sopflow = read_text(SOPFLOW)

    def decls_readme(pattern):
        out = []
        for ln_no, ln in linea(README, pattern):
            m = re.search(pattern, ln)
            out.append(("README.md", ln_no, int(m.group(1))))
        return out

    # 1-5 目录结构块：`dir/ (N)`（README §四 代码块）
    for key, pat in (("playbooks", r"^playbooks/\s+\((\d+)\)"),
                     ("templates", r"^templates/\s+\((\d+)\)"),
                     ("scripts", r"^scripts/\s+\((\d+)\)"),
                     ("agents", r"^agents/\s+\((\d+)\)"),
                     ("docs_md", r"^docs/\s+\((\d+)\)")):
        rep.add(key, actual[key], decls_readme(pat))

    # 6 硬规则 1-NN（README 内**每一处**都必须等于实测）
    rep.add("rules", actual["rules"],
            decls_readme(r"硬规则\s*1\s*[-–—~]\s*(\d+)") +
            [("orchestration/ORCHESTRATION.md", ln, int(m.group(1)))
             for ln, m in [(i, re.search(r"硬规则\s*1\s*[-–—~]\s*(\d+)", l))
                           for i, l in enumerate(read_text(ORCH).splitlines(), 1)] if m])

    # 7 check_all「一键 N 项」（README 内每一处）
    rep.add("check_all", actual["check_all"],
            decls_readme(r"一键[^\d\n]{0,12}?(\d+)\s*项"))

    # 8 拍板点「N 个拍板点」（README 内每一处）
    rep.add("user_gates", actual["user_gates"],
            decls_readme(r"(\d+)\s*个拍板点"))

    # 9 FAILURE-LIBRARY 编号范围（knowledge/index.md 声明：**F-01…F-NN** 连续）
    #    注意口径：必须带连字符且用省略号连接（`F-01…F-61`）——避免误抓 `F01-F14`（口播句公式）一类同形写法
    decls = []
    for ln_no, ln in enumerate(index.splitlines(), 1):
        for m in re.finditer(r"F-\d{2,3}\s*[…~]\s*F-(\d{2,3})", ln):
            decls.append(("knowledge/index.md", ln_no, int(m.group(1))))
    rep.add("failures", actual["failures"], decls)

    # 10 SOP-FLOW 自洽：单集 N 项 ＝ 通用 + 素材类1；满配 M 项 ＝ 通用 + 素材1 + 剧集2
    base = actual["check_all"] - 3       # 满配 - 素材类1 - 剧集类2 = 通用常跑
    for ln_no, ln in enumerate(sopflow.splitlines(), 1):
        m = re.search(r"单集\s*(\d+)\s*项", ln)
        if m:
            rep.add("sop_flow_单集", base + 1, [("docs/SOP-FLOW.md", ln_no, int(m.group(1)))])
        m = re.search(r"满配\s*(\d+)\s*项", ln)
        if m:
            rep.add("sop_flow_满配", actual["check_all"],
                    [("docs/SOP-FLOW.md", ln_no, int(m.group(1)))])
        m = re.search(r"下面\s*(\d+)\s*项", ln)
        if m:
            rep.add("sop_flow_附二项数", actual["check_all"],
                    [("docs/SOP-FLOW.md", ln_no, int(m.group(1)))])

    # SOP-FLOW 里声明的通用常跑项数（若有）
    for ln_no, ln in enumerate(sopflow.splitlines(), 1):
        m = re.search(r"通用\s*(\d+)\s*项", ln)
        if m:
            rep.add("sop_flow_通用", base, [("docs/SOP-FLOW.md", ln_no, int(m.group(1)))])

    # ---- 输出
    if a.json:
        print(json.dumps({
            "actual": actual,
            "base_always": base,
            "drift": [{"metric": m, "actual": act, "src": s, "line": l, "declared": d}
                      for m, act, s, l, d in rep.drift],
            "missing": [{"what": w, "where": p} for w, p in rep.missing],
        }, ensure_ascii=False, indent=2))

    print("== 文档计数守护：总览类文档声明 ↔ 磁盘/代码实测 ==")
    print(f"实测：playbooks {actual['playbooks']} · templates {actual['templates']} · "
          f"scripts {actual['scripts']} · agents {actual['agents']} · docs(md) {actual['docs_md']}")
    print(f"      ORCHESTRATION §5 硬规则 1-{actual['rules']}（{actual['rules']} 条）· "
          f"check_all 满配 {actual['check_all']} 项（通用常跑 {base}）· "
          f"拍板点 {actual['user_gates']} 个 · FAILURE-LIBRARY F-01…F-{actual['failures']}")
    print("-" * 66)
    for metric, act, ok, decls_ in rep.rows:
        if ok is None:
            print(f"  [跳过] {metric}: 实测 {act} —— 文档未声明该计数（补声明后可受守护）")
            continue
        srcs = "、".join(f"{s} L{l}" for s, l, _ in decls_)
        print(f"  [{'PASS' if ok else 'FAIL'}] {metric}: 实测 {act} ← {srcs}")
    print("-" * 66)

    if rep.drift:
        print(f"FAIL：{len(rep.drift)} 处计数漂移（README 写 X / 实际 Y）：")
        for metric, act, src, line, declared in rep.drift:
            print(f"  - [计数漂移] {src} L{line}：{metric} 写 {declared} / 实际 {act}")
        print("\n修复方向：改**声明**（文档里的数字）对齐实测，不要改实测口径去迁就文档；"
              "若件数确实该变（新增文件/新增规则/新增门控），同步更新文档声明后再跑本项。")
        sys.exit(1)

    if rep.missing:
        _emit_missing(rep, a.json)
        sys.exit(2)

    print(f"PASS ✅ 总览类文档计数与实测一致（{len([r for r in rep.rows if r[2] is not None])} 项受守护；"
          f"{len([r for r in rep.rows if r[2] is None])} 项文档未声明，跳过）")


def _emit_missing(rep, as_json):
    if as_json:
        print(json.dumps({"missing": [{"what": w, "where": p} for w, p in rep.missing],
                          "errors": rep.errors}, ensure_ascii=False, indent=2))
        return
    if rep.errors:
        print("FAIL：计数口径解析异常（不可判定，不算通过）：")
        for e in rep.errors:
            print(f"  - {e}")
    if rep.missing:
        print("不可判定（exit 2）：以下文件缺失或声明缺失，**空跑/缺声明不算通过**：")
        for what, where in rep.missing:
            print(f"  - {what}：{where}")


if __name__ == "__main__":
    main()
