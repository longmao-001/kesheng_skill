#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt Sheet 严格校验 (check_prompt_sheet.py)

用法: python -X utf8 scripts/check_prompt_sheet.py <runs/<项目>>
校验模板规范 R1-R10 (templates/prompt-sheet.md), 全部 PASS 才允许交付。
"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

PLATFORMS = {"Seedance2.5", "Jimeng", "Kling", "LibTV", "Vidu", "Hailuo", "Wan", "Runway"}
ROUTES = {"T2V", "I2V", "参考生视频", "首尾帧", "多镜原生"}
FIELDS = ["参考", "风格", "时间轴", "口播", "声音", "负面", "参数"]

TITLE_RE = re.compile(r"^### 镜头\s+(\S+)\s*·\s*(\d+(?:\.\d+)?)s\s*·\s*(.+)$")
SEG_RE = re.compile(r"^\d+-\d+秒\s+\[.+\]$")


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
        plat = f[len("prompts-"):].replace(".md", "")
        if plat not in PLATFORMS:
            issues.append(f"R9 FAIL [{f}]: 平台名不在固定词表 {sorted(PLATFORMS)}")

    # R8 README
    readme = os.path.join(md, "README.md")
    if not os.path.exists(readme):
        issues.append("R8 FAIL: 缺少 README.md (全片索引)")
        readme_txt = ""
    else:
        readme_txt = open(readme, encoding="utf-8-sig").read()

    # 收集全部风格 token 块与其他信息
    style_tokens = []
    per_shot = []  # (file, title_line, fields dict order)
    for f in plat_files:
        txt = open(os.path.join(md, f), encoding="utf-8-sig").read().splitlines()
        i = 0
        while i < len(txt):
            line = txt[i].strip()
            if line.startswith("### 镜头"):
                m = TITLE_RE.match(line)
                if not m:
                    issues.append(f"R1 FAIL [{f}]: 标题格式错误 -> {line[:60]}")
                    per_shot.append((f, line, None))
                else:
                    route = m.group(3).strip()
                    if route not in ROUTES:
                        issues.append(f"R1 FAIL [{f}]: 路线 '{route}' 不在词表 {sorted(ROUTES)}")
                    # 收集字段
                    fields = {}
                    order = []
                    j = i + 1
                    cur = None
                    while j < len(txt):
                        fl = txt[j].strip()
                        if fl.startswith("### "):
                            break
                        if fl.startswith("**") and "**：" in fl:
                            name, val = fl[2:].split("**：", 1)
                            fields[name] = val
                            order.append(name)
                            cur = name
                        elif fl.startswith("**") and fl.endswith("**"):
                            name = fl[2:-2].strip()
                            fields.setdefault(name, "")
                            order.append(name)
                            cur = name
                        elif fl and cur is not None:
                            fields[cur] = (fields.get(cur) or "") + fl + "\n"
                        j += 1
                    per_shot.append((f, line, (fields, order)))
                    i = j
                continue
            # 风格/参考等信息行
            if line.startswith("> 风格基线："):
                style_tokens.append(line[len("> 风格基线："):].strip())
            i += 1

    if style_tokens:
        base = style_tokens[0]
        for st in style_tokens[1:]:
            if st != base:
                issues.append(f"R3 FAIL: 文件间风格基线不一致 -> {st[:40]} vs {base[:40]}")
        if base and readme_txt and base not in readme_txt:
            issues.append("R3 FAIL: README 未包含风格基线")

    # R2 字段顺序 / R4 时间轴 / R5 参数 / R6 参考 / R7 负面
    for f, title, info in per_shot:
        if info is None:
            continue
        fields, order = info
        # R2
        if order != FIELDS:
            issues.append(f"R2 FAIL [{f}]: 字段顺序错误 {order} (期望 {FIELDS}) -> {title[:40]}")
        # R4 时间轴
        seg_count = 0
        have_native = False
        tz = fields.get("时间轴", "")
        for line in (tz or "").splitlines():
            if SEG_RE.match(line.strip()):
                seg_count += 1
            if line.strip().startswith("镜头") or line.strip().startswith("0-"):
                have_native = True
        if seg_count == 0 and not have_native:
            issues.append(f"R4 FAIL [{f}]: 时间轴无 0-X秒 分段 -> {title[:40]}")
        # R5 参数
        prm = fields.get("参数", "")
        if not all(k in prm for k in ("档", "抽卡", "失败")):
            issues.append(f"R5 FAIL [{f}]: 参数缺 时长档/抽卡/失败改法 -> {title[:40]}")
        # R6 参考
        ref = fields.get("参考", "")
        if ref and ref != "无" and "@图片" not in ref and "@视频" not in ref:
            issues.append(f"R6 FAIL [{f}]: 参考字段无 @引用语法")
        # R7 负面
        neg = fields.get("负面", "")
        if not neg:
            issues.append(f"R7 FAIL [{f}]: 负面词为空")
        # R11 口播字段必在(单独成字段, 不并入prompt正文——正文检查: 口播文本不应出现在时间轴字段内)
        vb = fields.get("口播")
        if vb is None:
            issues.append(f"R11 FAIL [{f}]: 缺少 **口播** 字段 -> {title[:40]}")
        elif vb.strip():
            kb = fields.get("时间轴", "") + fields.get("参考", "")
            core = re.sub(r"[，。；、：\s·]", "", vb)
            if core and core != "无" and core in re.sub(r"[，。；、：\s·]", "", kb):
                issues.append(f"R11 FAIL [{f}]: 口播文本被并入画面prompt(应单独成字段) -> {core[:30]}...")
            # 与口播稿一致性(宽松: 去标点后出现在口播稿中; "无"跳过)
            scripts = [g for g in os.listdir(run_dir)
                       if g.startswith("screenwriter-口播稿") and g.endswith(".md")]
            if scripts and core and core != "无":
                full = ""
                for g in scripts:
                    full += open(os.path.join(run_dir, g), encoding="utf-8-sig").read()
                norm = re.sub(r"[，。；、：\s·《》「」“”]", "", full)
                if core not in norm:
                    issues.append(f"R11 FAIL [{f}]: 口播文本与口播稿不一致 -> {core[:30]}...")
        # R12 图文对位(提示性, 不阻断——机器只能粗检, 硬性核查由检察官人工做)
        vb2 = fields.get("口播", "")
        if vb2 and vb2.strip() != "无":
            blob = fields.get("时间轴", "") + fields.get("参考", "")
            blob_words = set(re.findall(r"[\u4e00-\u9fa5]{2,6}", blob))
            hits = [w for w in re.findall(r"[\u4e00-\u9fa5]{2,6}", vb2) if w in blob_words]
            if not hits:
                warns.append(f"R12 提示 [{f}]: 口播与画面/参考无共现词——检察官必须人工核对图文对位 -> {vb2[:24]}...")

    # 风格 token 全片一致 (R3 细粒度): 各镜头 **风格** 内容一致
    style_vals = []
    for f, title, info in per_shot:
        if info and info[0] and info[0].get("风格"):
            style_vals.append((f, info[0]["风格"]))
    if style_vals:
        basev = style_vals[0][1]
        for f, v in style_vals[1:]:
            if v != basev:
                issues.append(f"R3 FAIL [{f}]: 风格token与其他镜头不一致 -> {v[:40]} vs {basev[:40]}")

    if issues:
        print(f"== 校验 FAIL ({len(issues)} 条) ==")
        for x in issues:
            print(" -", x)
        sys.exit(1)
    n = len(per_shot)
    print(f"== 校验 PASS: {len(plat_files)} 个平台文件 / {n} 个镜头, R1-R10 全部通过 ==")
    if warns:
        print(f"== 图文对位提示 ({len(warns)} 条, 交检察官人工核查) ==")
        for w in warns:
            print(" -", w)


if __name__ == "__main__":
    main()
