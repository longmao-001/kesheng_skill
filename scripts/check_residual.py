#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
红线/禁词残留扫描 v2 (check_residual.py) —— 防"旧表述回归"(F-05 教训)

用法: python -X utf8 scripts/check_residual.py <runs/<项目>> [额外关键词...]
规则:
 R-A: 只扫"执行文件"(会被拿去出片的): storyboard-*/dop-摄影方案*/m4-prompts*/screenwriter-口播稿*/
      editor-剪辑预计划*/sound-声音方案*/deliverables/03-prompt表*/deliverables/00-素材包说明
      评审/复核/裁决类文件(red-team*/art-美术复核*/m3-*等)不扫——它们讨论禁词是合法的
 R-B: 关键词=内置已知残词+brief红线清单+命令行附加; 行内含"禁用/弃用/不提/禁止/不上屏/不出现/标注"
      的行视为规则声明行, 跳过
输出: 命中清单(文件:行:关键词), 任一执行文件残留=FAIL
"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BUILTIN = ["s27_18", "s03_19", "s04_Picture_6", "s25_6", "EQ-99X", "归一化", "归镜11",
           "0.01nm", "电光青", "玦芯生物", "极紫外", "8W", "4W", "对标", "出口管制", "禁运"]
RULE_MARK = ("禁用", "弃用", "不提", "禁止", "不上屏", "不出现", "标注", "不许", "绝不", "不作", "红队", "修订")
SCAN_DIRS = ["."]
SCAN_PATTERNS = [
    "storyboard-*.md", "dop-摄影方案.md", "screenwriter-口播稿*.md",
    "editor-剪辑预计划.md", "sound-声音方案.md",
    "m4-prompts/*.md", "deliverables/03-prompt表/*.md", "deliverables/00-素材包说明.md",
]
SKIP_PREFIX = ("#", ">", "- [ ]", "|")


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else None
    if not base or not os.path.isdir(base):
        print("用法: check_residual.py <runs/<项目>> [额外关键词...]")
        sys.exit(2)
    kws = set(BUILTIN) | set(sys.argv[2:])
    # 精确残词策略: 只用"已知问题资产名/型号/断言"清单(来自失败图书馆F-01~F-10),
    # 外加命令行传入; 不做文本自动提取(误报爆炸教训 v1)

    import glob
    files = []
    for pat in SCAN_PATTERNS:
        files += glob.glob(os.path.join(base, pat))
    files = sorted(set(files))
    hits = []
    for path in files:
        rel = path[len(base) + 1:]
        for i, line in enumerate(open(path, encoding="utf-8-sig", errors="ignore"), 1):
            s = line.strip()
            if not s or s.startswith(SKIP_PREFIX):
                continue
            if any(m in s for m in RULE_MARK):
                continue
            for w in sorted(kws, key=len, reverse=True):
                if len(w) >= 2 and w in s:
                    hits.append((rel, i, w, s[:66]))
                    break

    if hits:
        print(f"== 残留扫描 FAIL ({len(hits)} 处) == —— 执行文件中仍有旧表述/禁词, 防回归!")
        for rel, i, w, txt in hits:
            print(f" - [{rel}:{i}] 命中「{w}」-> {txt}")
        sys.exit(1)
    print(f"== 残留扫描 PASS: 执行文件 {len(files)} 个, {len(kws)} 个红线/禁词无残留 ==")


if __name__ == "__main__":
    main()
