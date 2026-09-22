#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科生全量门控总检 (check_all.py) —— 一次跑完所有校验器

用法: python -X utf8 scripts/check_all.py <runs/<项目>>
作用: 依序跑本项目全部机器门控(考勤式门控), 汇总输出, 任一 FAIL 则整体 FAIL。
      输出每条门控的 PASS/FAIL + 首行摘要; FAIL 时列出对应修复方向。

覆盖(按 SOP 里程碑顺序):
  check_channel_conformance 判型 × 磁盘形态交叉校验(硬规则 #42④)：读 brief.md 的通道判定
                     （`通道：A|B|A+B`），**判 B/A+B 却缺 series-config.json 或 EPnn/ 集结构 = FAIL**
                     （防"判了 B 却不产 E1 配置 ⇒ 跨集闸被静默跳过"）；判 A 却有剧集形态 = WARN；
                     无 brief.md/缺通道字段 = exit 2 → 总检打印 `[跳过]`（不臆断判型）
  check_sop         产物存在性(简报/报告/概念/口播/分镜/prompt) + 每镜 prompt 字段完整性
  check_prompt_sheet prompt 规范(核心字段/口播单独&与口播稿一致/风格一致/参考@/负面) + R12 提示
  check_prompt_delivery prompt 交付门控(D1 SOP字段/D2 @标记贯穿/D3 负面同块/D4 禁词+专属空间标记/
                     D5 故事板纪律/D6 字卡口径/D7 校勘红线/D8 后期表述归一/D9 字卡镜负面分档)
                     —— 带 --animation-baseline 调用：D10 动画性只出待办清单，不阻断(用户 20260915 裁定)
                     —— 读 run 内 prompt-delivery-config.json 的 `channel`：**channel=A（通道 A）自动跳过
                        剧集专属 D12/D13/D10**（模板 templates/prompt-delivery-config-channelA.json）
  check_asset_pack  素材自包含(引用可解析/无后补提示词)
  check_asset_labels 素材标签门控(双向核对/prompt 缺口/命名规范/sidecar-索引一致)——**非素材类项目自动跳过**
  check_delivery    交付件版本收敛(单一执行源/交付包自包含/口播稿单一「定稿」) ← 出口前必跑
  check_series_consistency 剧集层跨集一致性(KSP-E4 D-S1–D-S8；读 runs/<季slug>/series-config.json)
                     —— **非剧集项目自动跳过**(无 series-config.json 且无 EPnn/ 目录＝单集项目)
  ads              广告禁用词(绝对化/极限词/疗效承诺/平台禁语)
  check_runs_clean  runs/ 只放项目
  check_docs_integrity SOP 文档无断链/孤岛(写了就被读到)
  check_readme_counts 文档计数不漂移(**技能级**)：总览类文档(README/`knowledge/index.md`/`docs/SOP-FLOW.md`)
                     声明的件数/条数/项数 ↔ 磁盘与代码**实测**逐项比对；漂移 = FAIL("写 X / 实际 Y")，
                     文件缺失或声明缺失 = exit 2(**空跑/缺声明不算通过**)
  check_rule_channels 规则通道标注门控(硬规则 #42①)：扫 ORCHESTRATION §5 硬规则区的每条 #NN
                     是否带适用通道标注；**新增规则(#≥43)缺标注 = FAIL**，历史 #1–#42 仅 WARN
  check_channel_assets 通道A 保留资产守护(硬规则 #42③)：11 件保留资产逐件断言存在 + .py
                     py_compile；缺件/空件/编译不过 = FAIL（防剧集化改造误伤广告线）
  check_bible_pin   圣经引用版本 pin(硬规则 #36③)：**仅剧集项目** —— 圣经 §⓪ 版本行非空
                     （版本号＋生效日期/生效集号）＋ 各集 `EPnn-brief.md` 的「引用圣经版本」
                     ＝圣经当前版本；缺圣经/版本行空/引用过期/简报缺字段 = FAIL（非剧集 `[跳过]`）
"""
import io
import os
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))


def run(name, cmd):
    """跑一项门控；返回 (name, ok, line, nlines, returncode)。

    约定：**exit 2 = 不可判定/空跑（不算通过，也不当 FAIL 混入）** —— 由调用方按门控语义处置
    （如 check_channel_conformance 无 brief.md 时跳过并打印 `[跳过] 未找到 brief.md`）。
    """
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        out = (p.stdout or "").strip()
        lines = out.splitlines() or ["(无输出)"]
        # 首行常是门控结果摘要；找第一行非 "FAIL: 用法/空跑" 的实质输出
        line = next((x for x in lines if x.strip()), "(无输出)")[:110]
        return (name, p.returncode == 0, line, len(lines), p.returncode)
    except Exception as e:  # noqa: BLE001
        return (name, False, f"执行错误: {e}", 0, 99)


def _is_undecidable(name, rc):
    """exit 2 的门控＝"不可判定/空跑"（不算通过，也不当 FAIL 混入最终裁决）。

    目前仅 `check_channel_conformance` 会以 exit 2 表达"无 brief.md / brief 缺通道字段"——
    此时**不臆断判型**、打印 `[跳过]`；其余门控的 exit 2 一律当作 FAIL 处理（不放过空跑）。
    """
    return rc == 2 and name == "check_channel_conformance"


def is_series(run_dir):
    """剧集项目判定（KSP-E0 的目录形态层）：有 series-config.json 或有 EPnn/ 集目录。"""
    if os.path.exists(os.path.join(run_dir, "series-config.json")):
        return True
    try:
        return any(os.path.isdir(os.path.join(run_dir, d)) and d.upper().startswith("EP")
                   for d in os.listdir(run_dir))
    except OSError:
        return False


def asset_root(run_dir):
    """素材类项目判定：有素材根目录（refs/assets/素材）或已有 assets_index.json；否则返回 None=跳过。"""
    for cand in ("refs", "assets", "素材", "素材库"):
        p = os.path.join(run_dir, cand)
        if os.path.isdir(p):
            return p
    if os.path.exists(os.path.join(run_dir, "assets_index.json")):
        return run_dir
    return None


def main():
    run_dir = sys.argv[1] if len(sys.argv) > 1 else None
    if not run_dir or not os.path.isdir(run_dir):
        print("用法: check_all.py <runs/<项目>>"); sys.exit(2)

    py = sys.executable
    checks = [
        ("check_sop", [py, "-X", "utf8", os.path.join(HERE, "check_sop.py"), run_dir]),
        ("check_prompt_sheet", [py, "-X", "utf8", os.path.join(HERE, "check_prompt_sheet.py"), run_dir]),
        ("check_prompt_sop", [py, "-X", "utf8", os.path.join(HERE, "check_prompt_sop.py"), run_dir]),
        # prompt 交付门控（通用版 D1–D10）：D1–D9 阻断；D10 动画性走基线（待办清单，非立刻清零项）
        ("check_prompt_delivery", [py, "-X", "utf8", os.path.join(HERE, "check_prompt_delivery.py"),
                                   run_dir, "--animation-baseline"]),
        ("check_asset_pack", [py, "-X", "utf8", os.path.join(HERE, "check_asset_pack.py"), run_dir]),
        ("check_delivery", [py, "-X", "utf8", os.path.join(HERE, "check_delivery.py"), run_dir]),
        ("ad_forbidden_words", [py, "-X", "utf8", os.path.join(HERE, "ad_forbidden_words.py"), run_dir]),
        ("check_runs_clean", [py, "-X", "utf8", os.path.join(HERE, "check_runs_clean.py")]),
        # 技能级（与项目无关）：SOP 文档是否真正嵌入技能（无断链/孤岛）
        ("check_docs_integrity", [py, "-X", "utf8", os.path.join(HERE, "check_docs_integrity.py")]),
        # 技能级（与项目无关）：总览类文档声明的计数 ↔ 磁盘/代码实测（防「README 写 8 项、实际 16 项」）
        ("check_readme_counts", [py, "-X", "utf8", os.path.join(HERE, "check_readme_counts.py")]),
        # 技能级 · 双通道守护（硬规则 #42）：规则须标适用通道 ＋ 通道 A 保留资产不得被剧集化削弱
        ("check_rule_channels", [py, "-X", "utf8", os.path.join(HERE, "check_rule_channels.py")]),
        ("check_channel_assets", [py, "-X", "utf8", os.path.join(HERE, "check_channel_assets.py")]),
    ]
    # 判型 × 磁盘形态交叉校验（硬规则 #42④）：判 B 却缺 series-config.json/EPnn 集结构
    #   ⇒ 跨集一致性闸被**静默跳过** —— 故本项放在最前（先验判型承诺，再验产物）
    checks.insert(0, ("check_channel_conformance",
                      [py, "-X", "utf8", os.path.join(HERE, "check_channel_conformance.py"), run_dir]))
    # 素材标签门控：仅素材类项目跑（有 refs/assets/素材 或 assets_index.json）；非素材类自动跳过
    aroot = asset_root(run_dir)
    if aroot:
        checks.insert(4, ("check_asset_labels",
                          [py, "-X", "utf8", os.path.join(HERE, "check_asset_labels.py"), aroot]))
    # 剧集层（KSP-E4）：仅剧集项目跑；单集项目跳过（不出 FAIL，也不假装 PASS）
    series = is_series(run_dir)
    if series:
        checks.append(("check_series_consistency",
                       [py, "-X", "utf8", os.path.join(HERE, "check_series_consistency.py"),
                        run_dir, "--season"]))
        # 圣经版本 pin（引用圣经必须 pin 版本 · 硬规则 #36③）：圣经 §⓪ 版本行非空
        #   ＋ 各集 EPnn-brief 的「引用圣经版本」＝圣经当前版本（不一致 ⇒ 圣经改版后引用静默过期）
        checks.append(("check_bible_pin",
                       [py, "-X", "utf8", os.path.join(HERE, "check_bible_pin.py"),
                        run_dir, "--via-check-all"]))

    results = [run(name, cmd) for name, cmd in checks]
    # exit 2 = 不可判定/空跑：不算 PASS（绝不静默通过），但也不当作 FAIL 混入 —— 单独列"跳过"
    skips = [(n, l) for n, ok, l, c, rc in results if not ok and _is_undecidable(n, rc)]
    fails = [(n, l) for n, ok, l, c, rc in results if not ok and not _is_undecidable(n, rc)]

    print(f"===== 科生门控总检: {os.path.basename(os.path.normpath(run_dir))} =====")
    for name, ok, line, nl, rc in results:
        if not ok and _is_undecidable(name, rc):
            print(f"[跳过] {name}（exit 2 = 不可判定/空跑，不算通过）")
        else:
            print(f"[{'PASS' if ok else 'FAIL'}] {name}")
        if line and line != "(无输出)":
            print(f"        {line}")
    if not series:
        print("[跳过] check_series_consistency —— 非剧集项目（无 series-config.json、无 EPnn/ 集目录）")
        print("[跳过] check_bible_pin —— 非剧集项目（圣经版本 pin 仅剧集项目适用）")
    if not aroot:
        print("[跳过] check_asset_labels —— 非素材类项目（无 refs/assets/素材 目录、无 assets_index.json）")
    for name, line in skips:
        if name == "check_channel_conformance" and ("未找到 brief.md" in line or "通道判定" in line):
            print(f"[跳过] check_channel_conformance —— {line}")
        elif name == "check_bible_pin":
            print(f"[跳过] check_bible_pin —— {line}")
    print("=" * 50)

    if fails:
        print(f"\n整体 FAIL：{len(fails)}/{len(checks)} 项未过。修复方向：")
        for name, line in fails:
            if name == "check_channel_conformance":
                print("  - check_channel_conformance: 判型承诺与磁盘形态不一致（判 B 却缺 series-config.json/EPnn 集结构"
                      " ⇒ 跨集闸会被静默跳过）-> 补 KSP-E1/E2 前置产出 templates/series-config.json，"
                      "或按 KSP-C 改判通道并同步 brief.md（判型＝用户拍板项）")
            elif name == "check_rule_channels":
                print("  - check_rule_channels: 新增硬规则（#≥43）未标注适用通道 -> 按硬规则 #42① 在规则末尾补"
                      " `【通道：通用】`/`（适用：A/B）` 等（历史 #1–#42 缺标注仅 WARN，不回填）")
            elif name == "check_channel_assets":
                print("  - check_channel_assets: 通道 A 保留资产缺件/空件/py_compile 不过 -> 恢复该资产"
                      "（硬规则 #42③：剧集化改造不得削弱或误伤广告/科普/科研线）；清单见 "
                      "docs/USER_SOP.md §2.6 ＋ docs/DUAL-CHANNEL-AUDIT.md §3")
            elif name == "check_bible_pin":
                print("  - check_bible_pin: 圣经 §⓪ 版本行空/缺圣经/分集简报缺「引用圣经版本」/引用版本≠圣经当前版本"
                      " -> 补 templates/show-bible.md §⓪（版本号＋生效日期＋生效集号）；"
                      "各集 EPnn-brief 回填新版本（圣经已改版 ⇒ 走 KSP-C 评估回炉范围，硬规则 #36③）")
            elif name == "check_sop":
                print("  - check_sop: 缺产物(SOP被跳过)-> 按 ORCHESTRATION §5 补齐/回退；每镜 prompt 字段缺 -> 补参考/风格/时间轴/口播/声音/负面/参数")
            elif name == "check_prompt_sheet":
                print("  - check_prompt_sheet: 缺核心字段/口播并入画面/口播与口播稿不一致/风格块不一致/参考漏@/负面空; 或格式别名误报(F-30)-> 修脚本兼容而非迁就")
            elif name == "check_prompt_sop":
                print("  - check_prompt_sop: 十步 SOP 有步骤没走/走错(如参考图裸引用、风格/口播不同源) -> 按 templates/prompt-sop.md 回对应步补齐")
            elif name == "check_prompt_delivery":
                print("  - check_prompt_delivery: SOP字段缺/@标记脱节/负面写在代码块外/废止表述残留/"
                      "故事板无线稿或运镜/字卡旧口径/项目专属空间标记越界/后期表述未归一/字卡镜负面未分档"
                      " -> 按 scripts/README-check_prompt_delivery.md 修；项目词表写进 run 内 "
                      "prompt-delivery-config.json；D10 动画性清单见 --animation-only 或基线模式输出")
            elif name == "check_asset_pack":
                print("  - check_asset_pack: 引用未在 inventory 登记/后补提示词(待补充等) -> 素材自包含, 参考图归库")
            elif name == "check_asset_labels":
                print("  - check_asset_labels: 素材标签门控未过(缺口件必然 FAIL/未登记/断链/命名不合规/sidecar 与索引打架)"
                      " -> 缺口件补 prompt 后重跑 asset_index.py；命名按 asset_schema.md §1 改名；"
                      "空跑 exit 2 = 0 文件或 0 索引(空跑不算通过)；--naming-warn/--require-vision 见脚本 --help")
            elif name == "check_delivery":
                print("  - check_delivery: 多源并存/交付包死链/口播稿多版本 -> 收敛为单一「定稿」(F-29)")
            elif name == "ad_forbidden_words":
                print("  - ad_forbidden_words: 命中广告禁用词(绝对化/极限/疗效/平台禁语) -> 改程度性/去禁词")
            elif name == "check_docs_integrity":
                print("  - check_docs_integrity: SOP 文档有断链/孤岛(写了没人读) -> 补引用或合并，确保 SOP 真正嵌入技能")
            elif name == "check_readme_counts":
                print("  - check_readme_counts: 总览类文档声明的计数与实测不符(计数漂移) -> 改**文档里的声明数字**对齐实测"
                      "（README：目录结构 `dir/ (N)` / `硬规则 1-NN` / `一键 N 项` / `N 个拍板点`；"
                      "`knowledge/index.md`：`F-01…F-NN`；`docs/SOP-FLOW.md`：`满配/单集/通用 N 项`）；"
                      "exit 2 = 文件缺失或声明缺失（补上再跑，缺声明不算通过）")
            elif name == "check_series_consistency":
                print("  - check_series_consistency: 跨集一致性(D-S1–D-S8)未过 -> 按 scripts/README-check_series_consistency.md "
                      "修；项目词表写进 runs/<季slug>/series-config.json（模板 templates/series-config.json）；"
                      "exit 2 = 缺配置/0 集/0 prompt 文件（空跑不算通过）")
            else:
                print(f"  - {name}: 见首行")
        sys.exit(1)
    print("全部 PASS ✅")


if __name__ == "__main__":
    main()
