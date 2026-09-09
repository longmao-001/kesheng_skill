#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科生全量门控总检 (check_all.py) —— 一次跑完所有校验器

用法: python -X utf8 scripts/check_all.py <runs/<项目>>
作用: 依序跑本项目全部机器门控(考勤式门控), 汇总输出, 任一 FAIL 则整体 FAIL。
      输出每条门控的 PASS/FAIL + 首行摘要; FAIL 时列出对应修复方向。

覆盖(按 SOP 里程碑顺序):
  check_sop         产物存在性(简报/报告/概念/口播/分镜/prompt) + 每镜 prompt 字段完整性
  check_prompt_sheet prompt 规范(核心字段/口播单独&与口播稿一致/风格一致/参考@/负面) + R12 提示
  check_asset_pack  素材自包含(引用可解析/无后补提示词)
  check_delivery    交付件版本收敛(单一执行源/交付包自包含/口播稿单一「定稿」) ← 出口前必跑
  ads              广告禁用词(绝对化/极限词/疗效承诺/平台禁语)
  check_runs_clean  runs/ 只放项目
"""
import io
import os
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))


def run(name, cmd):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        out = (p.stdout or "").strip()
        line = (out.splitlines() or ["(无输出)"])[0][:110]
        return (name, p.returncode == 0, line, len(out.splitlines()))
    except Exception as e:  # noqa: BLE001
        return (name, False, f"执行错误: {e}", 0)


def main():
    run_dir = sys.argv[1] if len(sys.argv) > 1 else None
    if not run_dir or not os.path.isdir(run_dir):
        print("用法: check_all.py <runs/<项目>>"); sys.exit(2)

    py = sys.executable
    checks = [
        ("check_sop", [py, "-X", "utf8", os.path.join(HERE, "check_sop.py"), run_dir]),
        ("check_prompt_sheet", [py, "-X", "utf8", os.path.join(HERE, "check_prompt_sheet.py"), run_dir]),
        ("check_asset_pack", [py, "-X", "utf8", os.path.join(HERE, "check_asset_pack.py"), run_dir]),
        ("check_delivery", [py, "-X", "utf8", os.path.join(HERE, "check_delivery.py"), run_dir]),
        ("ad_forbidden_words", [py, "-X", "utf8", os.path.join(HERE, "ad_forbidden_words.py"), run_dir]),
        ("check_runs_clean", [py, "-X", "utf8", os.path.join(HERE, "check_runs_clean.py")]),
    ]

    results = [run(name, cmd) for name, cmd in checks]
    fails = [(n, l, c) for n, ok, l, c in results if not ok]

    print(f"===== 科生门控总检: {os.path.basename(os.path.normpath(run_dir))} =====")
    for name, ok, line, nl in results:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        if line and line != "(无输出)":
            print(f"        {line}")
    print("=" * 50)

    if fails:
        print(f"\n整体 FAIL：{len(fails)}/{len(checks)} 项未过。修复方向：")
        for name, line, _ in fails:
            if name == "check_sop":
                print("  - check_sop: 缺产物(SOP被跳过)-> 按 ORCHESTRATION §5 补齐/回退；每镜 prompt 字段缺 -> 补参考/风格/时间轴/口播/声音/负面/参数")
            elif name == "check_prompt_sheet":
                print("  - check_prompt_sheet: 缺核心字段/口播并入画面/口播与口播稿不一致/风格块不一致/参考漏@/负面空; 或格式别名误报(F-30)-> 修脚本兼容而非迁就")
            elif name == "check_asset_pack":
                print("  - check_asset_pack: 引用未在 inventory 登记/后补提示词(待补充等) -> 素材自包含, 参考图归库")
            elif name == "check_delivery":
                print("  - check_delivery: 多源并存/交付包死链/口播稿多版本 -> 收敛为单一「定稿」(F-29)")
            elif name == "ad_forbidden_words":
                print("  - ad_forbidden_words: 命中广告禁用词(绝对化/极限/疗效/平台禁语) -> 改程度性/去禁词")
            else:
                print(f"  - {name}: 见首行")
        sys.exit(1)
    print("全部 PASS ✅")


if __name__ == "__main__":
    main()
