#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt Sheet 严格校验 (check_prompt_sheet.py)

用法: python -X utf8 scripts/check_prompt_sheet.py <runs/<项目>>
校验模板规范 (templates/prompt-sheet.md / product-prompt-formula.md / video-prompt-formula.md)。
兼容两种既有生产格式，任选其一都能校验，不因格式别名误报：
  A) R1-R11 七段：参考→风格→时间轴→口播→声音→负面→参数（**字段**：）
  B) 九段/视频：参数→参考→风格→镜头→时间轴→主体→声音→口播→负面→强制约束（【字段】）
两格式核心字段同名；A 多"严格顺序/参数关键词"，B 多"镜头/主体/强制约束"。
校验目标 = 防交付物残缺/口播脱节/风格不一致/参考图漏挂，而非死守一种写法。

判定：
  FAIL  = 核心字段缺失或为空 / 口播并入他字段 / 口播与口播稿不一致 / 风格块不一致 / 参考无@ / 负面为空
  WARN  = 参数关键词(档/抽卡/失败)不全 / 图文对位无共现词（交检察官人工）
  (文件命名、README、平台词表保留，R9/R8/R10 不因别名松绑)
"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

PLATFORMS = {"Seedance2.5", "Jimeng", "Kling", "LibTV", "Vidu", "Hailuo", "Wan", "Runway", "cgprism"}
ROUTES = {"T2V", "I2V", "参考生视频", "首尾帧", "多镜原生", "人工数据卡"}

# 核心字段（两格式共同要求）。顺序在 A 格式中强制；B 格式只查存在。
CORE = ["参考", "风格", "时间轴", "口播", "声音", "负面", "参数"]
# B(九段)格式额外字段（合法，不作残缺判据）
EXTRA = {"镜头", "主体", "强制约束", "构图", "光线", "细节"}

TITLE_RE = re.compile(r"^###\s+镜头\s+(\S+)\s*·\s*(\d+(?:\.\d+)?)s\s*·\s*(.+)$")
SEG_RE = re.compile(r"^(\d+)-(\d+)(?:秒|s)\s*[\[\[【]?\s*.*")
NONALNUM = re.compile(r"[，。；、：\s·《》「」“”（）()\[\]【】_\-:/|]")


def _route(n):
    """把路线里的括注（如 '参考生视频（产品·九段）' / 'I2V（开场·宏大·无工厂）'）抽出主名。"""
    return re.sub(r"[（(].*?[)）]", "", n).strip()


def _norm(s):
    return NONALNUM.sub("", s or "")


def main():
    run_dir = sys.argv[1] if len(sys.argv) > 1 else None
    if not run_dir or not os.path.isdir(run_dir):
        print("用法: check_prompt_sheet.py <runs/<项目>>"); sys.exit(2)
    md = os.path.join(run_dir, "m4-prompts")
    if not os.path.isdir(md):
        print(f"FAIL: 缺少 m4-prompts 目录 ({md})"); sys.exit(1)

    issues = []
    warns = []
    files = sorted(f for f in os.listdir(md) if f.endswith(".md"))
    plat_files = [f for f in files if f.startswith("prompts-")]

    # R9 命名
    for f in plat_files:
        plat = _route(f[len("prompts-"):].replace(".md", ""))
        if plat not in PLATFORMS:
            issues.append(f"R9 FAIL [{f}]: 平台名不在固定词表 {sorted(PLATFORMS)}")

    # R8 README
    readme = os.path.join(md, "README.md")
    if not os.path.exists(readme):
        issues.append("R8 FAIL: 缺少 README.md (全片索引)")
        readme_txt = ""
    else:
        readme_txt = open(readme, encoding="utf-8-sig").read()

    style_tokens = []
    per_shot = []  # (file, title_line, fields_dict, order_list)

    FIELD_START = re.compile(r"^(?:【([^】]+)】|(?:[*-]\s*)?\*\*([^*]+)\*\*[:：]?)\s*(.*)$")

    for f in plat_files:
        txt = open(os.path.join(md, f), encoding="utf-8-sig").read().splitlines()
        i = 0
        while i < len(txt):
            line = txt[i].strip()
            if line.startswith("### 镜头"):
                m = TITLE_RE.match(line)
                if not m:
                    issues.append(f"R1 FAIL [{f}]: 标题格式错误 -> {line[:60]}")
                    per_shot.append((f, line, {}, []))
                else:
                    route = _route(m.group(3))
                    if route not in ROUTES:
                        issues.append(f"R1 FAIL [{f}]: 路线 '{route}' 不在词表 {sorted(ROUTES)}")
                    fields = {}
                    order = []
                    j = i + 1
                    cur = None
                    while j < len(txt):
                        fl = txt[j].strip()
                        if fl.startswith("### "):
                            break
                        ms = FIELD_START.match(fl)
                        if ms:
                            name = (ms.group(1) or ms.group(2) or "").strip()
                            if name:
                                name = name.lstrip("*").strip()
                                fields.setdefault(name, "")
                                order.append(name)
                                cur = name
                                if ms.group(3):
                                    fields[name] = ms.group(3).strip()
                        elif fl and cur is not None:
                            fields[cur] = (fields.get(cur) or "") + fl + "\n"
                        j += 1
                    per_shot.append((f, line, fields, order))
                    i = j
                continue
            if line.startswith("> 风格基线："):
                style_tokens.append(line[len("> 风格基线："):].strip())
            i += 1

    # R3 风格基线（跨文件）
    if style_tokens:
        base = style_tokens[0]
        for st in style_tokens[1:]:
            if st != base:
                issues.append(f"R3 FAIL: 文件间风格基线不一致 -> {st[:40]} vs {base[:40]}")
        if base and readme_txt and base not in readme_txt:
            issues.append("R3 FAIL: README 未包含风格基线")

    # 逐镜硬检查 + 字段值非空 + 口播/风格/参考/负面
    style_vals = []
    for f, title, fields, order in per_shot:
        if not fields:
            continue
        # 字段非空（核心字段值允许"无/无参考"占位，但必须存在该字段且有内容）
        for cf in CORE:
            if cf not in fields:
                issues.append(f"CORE FAIL [{f}]: 缺字段 **{cf}** -> {title[:40]}")
            else:
                val = (fields.get(cf) or "").strip()
                if not val:
                    issues.append(f"CORE FAIL [{f}]: 字段 **{cf}** 为空 -> {title[:40]}")
        # R2 严格顺序（仅当七段格式、字段集与 CORE 相等时强制）
        if set(order) == set(CORE) and order != CORE:
            issues.append(f"R2 FAIL [{f}]: 字段顺序错误 {order} (期望 {CORE}) -> {title[:40]}")
        # R4 时间轴分段
        tz = fields.get("时间轴", "")
        if not any(SEG_RE.match(ln.strip()) for ln in (tz or "").splitlines() if ln.strip()):
            issues.append(f"R4 FAIL [{f}]: 时间轴无 0-X秒 分段 -> {title[:40]}")
        # 参数（WARN：关键词不全；R5 原为 FAIL，放宽为 WARN 因 九段格式常把 档/抽卡 写在别处）
        prm = fields.get("参数", "")
        absent = [k for k in ("档", "抽卡", "失败", "时长") if k not in prm]
        if absent:
            warns.append(f"R5 提示 [{f}]: 参数未含 {'/'.join(absent)} -> {title[:40]}")
        # R6 参考挂载 @ 语法（"无"占位及后缀括注视为无参考，跳过）
        ref = fields.get("参考", "").strip()
        ref_base = _route(ref)
        if ref and ref_base != "无" and "@" not in ref:
            issues.append(f"R6 FAIL [{f}]: 参考字段无 @引用语法")
        # R7 负面非空
        neg = fields.get("负面", "").strip()
        if not neg or _norm(neg) == "无":
            # 允许"无"占位，但须明写；这里有内容则过
            issues.append(f"R7 FAIL [{f}]: 负面词为空")
        # R11 口播单独成字段 + 与口播稿一致
        vb = fields.get("口播", "")
        if vb is None:
            issues.append(f"R11 FAIL [{f}]: 缺少 **口播** 字段 -> {title[:40]}")
        elif vb.strip():
            kb = fields.get("时间轴", "") + fields.get("参考", "") + fields.get("主体", "")
            core_vb = _norm(vb)
            if core_vb and core_vb != "无" and core_vb in _norm(kb):
                issues.append(f"R11 FAIL [{f}]: 口播文本被并入画面prompt -> {core_vb[:30]}...")
            scripts = [g for g in os.listdir(run_dir)
                       if g.startswith("screenwriter-口播稿") and g.endswith(".md")]
            if scripts and core_vb and core_vb != "无":
                full = ""
                for g in scripts:
                    full += open(os.path.join(run_dir, g), encoding="utf-8-sig").read()
                if core_vb not in re.sub(r"\s", "", _norm(full)):
                    issues.append(f"R11 FAIL [{f}]: 口播文本与口播稿不一致 -> {core_vb[:30]}...")
        # R3 每镜风格一致
        sv = fields.get("风格", "").strip()
        if sv:
            style_vals.append((f, sv))

    # R3 全片风格 token 一致（逐镜）
    if style_vals:
        basev = style_vals[0][1]
        for f, v in style_vals[1:]:
            if v != basev:
                issues.append(f"R3 FAIL [{f}]: 风格token与其他镜头不一致 -> {v[:40]} vs {basev[:40]}")

    # R12 图文对位（提示性）
    for f, title, fields, _o in per_shot:
        vb2 = fields.get("口播", "").strip()
        if vb2 and _norm(vb2) != "无":
            blob = fields.get("时间轴", "") + fields.get("参考", "") + fields.get("主体", "")
            blob_words = set(re.findall(r"[\u4e00-\u9fa5]{2,6}", blob))
            hits = [w for w in re.findall(r"[\u4e00-\u9fa5]{2,6}", vb2) if w in blob_words]
            if not hits:
                warns.append(f"R12 提示 [{f}]: 口播与画面/参考无共现词——检察官必须人工核对图文对位 -> {vb2[:24]}...")

    if issues:
        print(f"== 校验 FAIL ({len(issues)} 条) ==")
        for x in issues:
            print(" -", x)
        sys.exit(1)
    n = len(per_shot)
    print(f"== 校验 PASS: {len(plat_files)} 个平台文件 / {n} 个镜头, 核心字段/口播/风格/参考/负面 通过 ==")
    if warns:
        print(f"== 提示 ({len(warns)} 条, WARN 不阻断) ==")
        for w in warns:
            print(" -", w)


if __name__ == "__main__":
    main()
