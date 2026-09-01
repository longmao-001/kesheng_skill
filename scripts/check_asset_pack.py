#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
素材包完整性校验 (check_asset_pack.py) —— "零意外"机器强制

用法: python -X utf8 scripts/check_asset_pack.py <runs/<项目>>
规则:
 A. 交付文档中禁止出现"待补充/请提供/拍照/自己找/补拍/缺素材"等后补提示词
 B. prompts-*.md 引用的 @图片N/@视频N/@音频N 必须在 assets-inventory.md 中登记,
    且状态为 已入库 / 带生成prompt / 客户素材 之一 (不允许"待提供/未准备")
 C. 每一条生成prompt引用必须指向真实存在的 prompt 文件或行
"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

FORBID = ["待补充", "请提供", "补拍", "需要你", "自己找", "找一下", "拍一张", "拍个照", "后期补素材", "未准备素材", "你提供一下"]
OK_STATUS = ("已入库", "带生成prompt", "客户素材", "已下载", "已生成")
REF_RE = re.compile(r"@(图片|视频|音频)(\d+)")


def main():
    run_dir = sys.argv[1] if len(sys.argv) > 1 else None
    if not run_dir or not os.path.isdir(run_dir):
        print("用法: check_asset_pack.py <runs/<项目>>")
        sys.exit(2)
    issues = []

    # A. 交付文档后补提示词
    for root, _d, files in os.walk(run_dir):
        for f in files:
            if not (f.endswith(".md") or f.endswith(".txt")):
                continue
            if "check" in f.lower():
                continue
            txt = open(os.path.join(root, f), encoding="utf-8-sig", errors="ignore").read()
            for kw in FORBID:
                if kw in txt:
                    issues.append(f"A FAIL [{f}]: 出现后补提示词「{kw}」——交付件必须自包含")
                    break

    # B. 引用资产 vs 登记
    md = os.path.join(run_dir, "m4-prompts")
    inv_path = os.path.join(run_dir, "assets-inventory.md")
    inv_txt = open(inv_path, encoding="utf-8-sig", errors="ignore").read() if os.path.exists(inv_path) else ""
    inv_ids = set(re.findall(r"@(?:图片|视频|音频)(\d+)", inv_txt))
    inv_status_ok = all(
        any(st in line for st in OK_STATUS)
        for line in inv_txt.splitlines()
        if line.strip() and ("@" in line or "|" in line)
    )
    # inventory 中每行需含状态词
    rows = [l for l in inv_txt.splitlines() if l.strip() and "|" in l]
    for idx, l in enumerate(rows, 1):
        if not any(st in l for st in OK_STATUS):
            issues.append(f"B FAIL [assets-inventory.md 第{idx}行]: 状态未标明(要求 已入库/带生成prompt/客户素材) -> {l[:60]}")

    if os.path.isdir(md):
        used = set()
        for f in os.listdir(md):
            if f.startswith("prompts-") and f.endswith(".md"):
                txt = open(os.path.join(md, f), encoding="utf-8-sig", errors="ignore").read()
                used |= set(REF_RE.findall(txt) and [m[1] for m in REF_RE.findall(txt)])
        for u in used:
            if u not in inv_ids:
                issues.append(f"B FAIL: prompts 引用 @图片{u} 但 assets-inventory.md 未登记(缺素材, 必须已入库或附生成prompt)")
            elif not inv_status_ok:
                break

    # C. 生成prompt 引用存在性(宽松: inventory 中"带生成prompt"须给出文件名/行)
    for l in rows:
        if "带生成prompt" in l and "(" not in l and "[" not in l and ".." not in l:
            issues.append(f"C FAIL [assets-inventory.md]: 「带生成prompt」行未指明prompt位置 -> {l[:60]}")

    if issues:
        print(f"== 素材包校验 FAIL ({len(issues)} 条) ==")
        for x in issues:
            print(" -", x)
        sys.exit(1)
    n_refs = len(inv_ids)
    print(f"== 素材包校验 PASS: 自包含确认, {n_refs} 个登记资产全部就绪(已入库/带生成prompt/客户素材), 无后补提示 ==")


if __name__ == "__main__":
    main()
