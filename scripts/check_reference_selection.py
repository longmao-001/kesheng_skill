#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参考图选片校验 (check_reference_selection.py)

用法: python -X utf8 scripts/check_reference_selection.py <runs/<项目>>

检查每镜【参考】字段是否按 templates/reference-selection.md 选出（对位需求→角色+部位对应+位置→合规）。
把"选错图/用错参考/含禁图"变成可自动拦截；输出 PASS/FAIL + 逐镜明细。
"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

TITLE_RE = re.compile(r"^### 镜头\s+(\S+)\s*·\s*(\d+(?:\.\d+)?)s\s*·\s*(.+)$")

ROLE_KEYS = ["主体", "部件参考", "场景参考", "质感参考"]
FORBIDDEN = ["水印", "竞品", "团队合影", "团队合照", "未授权", "商标原理", "模糊", "打码"]
REF_RE = re.compile(r"@(?:图|图片)\s*(\d+)")


def parse_shots(md_dir):
    shots = []
    for f in sorted(x for x in os.listdir(md_dir) if x.startswith("prompts-") and x.endswith(".md")):
        txt = open(os.path.join(md_dir, f), encoding="utf-8-sig").read().splitlines()
        i = 0
        while i < len(txt):
            line = txt[i].strip()
            if line.startswith("### 镜头"):
                m = TITLE_RE.match(line)
                title = line
                fields = {}
                j = i + 1
                cur = None
                while j < len(txt):
                    fl = txt[j].strip()
                    if fl.startswith("### "):
                        break
                    if fl.startswith("**") and "**：" in fl:
                        name, val = fl[2:].split("**：", 1)
                        fields[name] = val
                        cur = name
                    elif fl.startswith("**") and fl.endswith("**"):
                        name = fl[2:-2].strip()
                        fields.setdefault(name, "")
                        cur = name
                    elif fl and cur is not None:
                        fields[cur] = (fields.get(cur) or "") + fl + "\n"
                    j += 1
                shots.append((f, title, fields))
                i = j
                continue
            i += 1
    return shots


def main():
    run_dir = sys.argv[1] if len(sys.argv) > 1 else None
    if not run_dir or not os.path.isdir(run_dir):
        print("用法: check_reference_selection.py <runs/<项目>>"); sys.exit(2)
    md = os.path.join(run_dir, "m4-prompts")
    if not os.path.isdir(md):
        print(f"FAIL: 缺少 m4-prompts 目录 ({md})"); sys.exit(1)

    issues = []
    warns = []
    n_ref_shots = 0
    n_shots = 0

    for f, title, fields in parse_shots(md):
        n_shots += 1
        ref = fields.get("参考", "") or ""
        if not ref.strip() or ref.strip() == "无":
            continue
        n_ref_shots += 1
        refs = REF_RE.findall(ref)
        if refs and len(refs) > 3:
            issues.append(f"选片FAIL [{f}] {title[:34]}: 参考图 {len(refs)} 张 > 3（超图片节点上限，选最需要的3张）")

        # 角色标注
        has_role = any(k in ref for k in ROLE_KEYS)
        if refs and not has_role:
            issues.append(f"选片FAIL [{f}] {title[:34]}: 引用了 @图 但未标「角色」（主体/部件参考/场景参考/质感参考）")
        # 部件/场景参考必须部位对应 + 位置
        if refs and ("部件参考" in ref or "场景参考" in ref):
            if "＝" not in ref and "=" not in ref:
                issues.append(f"选片FAIL [{f}] {title[:34]}: 部件/场景参考未标「部位对应」(参考图<部位X>＝主体<部位X'>)")
            pos_ok = any(x in ref for x in ["位置", "取该主体", "用于背景", "位于"]) or re.search(r"放[入到]?[^。；]{0,8}", ref)
            if not pos_ok:
                issues.append(f"选片FAIL [{f}] {title[:34]}: 部件/场景参考未写「放哪位置」（或场景参考含主体注明 图中<位置>的主体=主体）")
        # 禁图
        for bad in FORBIDDEN:
            if bad in ref:
                issues.append(f"选片FAIL [{f}] {title[:34]}: 参考图含禁图信号「{bad}」（水印/竞品/团队照/未授权/商标原理/模糊=一票否决）")

        # 对位粗检：参考 ↔ 口播 共现词
        vb = fields.get("口播", "") or ""
        if vb.strip() and vb.strip() != "无":
            ref_words = set(re.findall(r"[\u4e00-\u9fa5]{2,6}", ref))
            vb_words = set(re.findall(r"[\u4e00-\u9fa5]{2,6}", vb))
            hits = [w for w in vb_words if any(w in r or r in w for r in ref_words)]
            if vb_words and not hits:
                warns.append(f"选片提示 [{f}] {title[:34]}: 参考图与口播无共现词——参考图可能不对位，检察官人工核对（对位需求/角色/部位对应）")

    print(f"== 参考图选片校验 == 共 {n_shots} 镜, 其中 {n_ref_shots} 镜引用参考图")
    if issues:
        print(f"== FAIL ({len(issues)} 条) ==")
        for x in issues:
            print(" -", x)
        print("=> 按 templates/reference-selection.md 逐镜重选参考图（对位需求→8维打分→角色+部位对应+位置→禁图一票否决）")
        sys.exit(1)
    print(f"== PASS: 参考图角色/部位对应/位置标齐，无禁图，引用 ≤3 张 ==")
    if warns:
        print(f"== 对位提示 ({len(warns)} 条, 交检察官人工核对) ==")
        for w in warns:
            print(" -", w)


if __name__ == "__main__":
    main()
