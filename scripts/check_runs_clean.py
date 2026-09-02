#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
runs/ 只放项目 守护 (check_runs_clean.py)

用法: python -X utf8 scripts/check_runs_clean.py [<runs目录>]
规则(ORCHESTRATION §5-15): runs/ 只允许项目 run —— 每个项目一个 runs/<项目slug>/。
FAIL 条件:
  - 顶层存在散文件(必须是目录)
  - 顶层目录名以 "_" 开头(_tmp-* / _lessons / _research-* 等非项目目录)
  - 顶层目录名不是合法 slug(含空格/中文/特殊字符等; slug 只允许字母数字-)
  - 目录为空(项目 run 至少有产物)
PASS: runs/ 只含项目 slug 目录。
"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
RESERVED_PREFIX = ("_", )


def main():
    runs = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runs")
    if not os.path.isdir(runs):
        print(f"PASS: {runs} 不存在或为空（无项目，即干净）")
        return
    issues = []
    for name in sorted(os.listdir(runs)):
        p = os.path.join(runs, name)
        if os.path.isfile(p):
            issues.append(f"顶层散文件(非项目): {name}")
            continue
        if name.startswith(RESERVED_PREFIX):
            issues.append(f"非项目目录(以_开头): {name}")
            continue
        if not SLUG.match(name):
            issues.append(f"非法项目slug: {name}")
            continue
        if not os.listdir(p):
            issues.append(f"空项目目录: {name}")
    if issues:
        print(f"== FAIL: runs/ 含非项目内容 ({len(issues)} 项) ==")
        for x in issues:
            print(" -", x)
        print("=> 按 ORCHESTRATION §5-15: 非项目散落物移出 runs/，临时目录删除后再交付。")
        sys.exit(1)
    print(f"== PASS: runs/ 只含项目 slug 目录 ==")


if __name__ == "__main__":
    main()
