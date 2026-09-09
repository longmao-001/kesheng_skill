#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交付包一致性 / 版本收敛门控 (check_delivery.py)

背景：出口评审（L4）最伤的一次是与项目无关的"交付件版本漂移/多源并存"——
  * 三套 prompt 文件（m4-prompts 90s / prompts-cgprism-逐镜 75s / delivery 90s），时长/口播切分不一致；
  * delivery/README 引用不在包内的文件（声音/剪辑），成死链；
  * delivery/storyboard 标题 v3/90s 与正文 v9/75s 自相矛盾；
  * 系统没有一道闸能拦住它 → 白白 CONDITIONAL。

本脚本就是要补上这道闸。只当 run 已有 delivery/ 或 出口件时启用：

  A) 单一执行源：prompts 执行文件只应有一份（m4-prompts/prompts-*.md 为准）；
     若 run 根/其他处另有同题 prompt 文件（如 prompts-cgprism-逐镜.md），且
     delivery/README 引用的是这一份而非 m4-prompts → 判"多源并存" FAIL。
  B) 交付包自包含：delivery/*.md 里内联 `` `文件路径` `` 引用必须在 delivery/ 内
     能找到（或为 URL / 外部资源）；引用了 m2/sound、m2/editor 这类 run 根目录件
     而没打进 delivery/ → 判"死链/包不自包含" FAIL。
  C) 版本漂移：delivery 或 run 根 同时存在多个 screenwriter-口播稿-定稿v*.md
     （v9 与 v10 并存），或 delivery 分镜表标题版本与正文时长/口播版本不一致 → FAIL。

用法: python -X utf8 scripts/check_delivery.py <runs/<项目>>

注：本闸是"考勤式门控"的交付层补充，与 check_sop.py（产物存在性）/check_prompt_sheet.py
    （prompt 完整性）正交。制片人出口前必跑。
"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def _inline_refs(txt):
    """抓 markdown 内联文档/文件路径引用：反引号 `` `x.md` `` 与「(见 x.md) / （见x.md） / 参照 x.md」。"""
    refs = set(re.findall(r"`([^`]+\.(?:md|py|mp4|png|jpg|jpeg|docx|pptx|txt|zip))`", txt))
    refs |= set(re.findall(r"[（(](?:见|参见|参照|按)?\s*([\w./\\-]+\.(?:md|docx|pptx|txt))", txt))
    return refs


def _url_or_external(s):
    s = s.strip().rstrip("/")
    if s.startswith(("http://", "https://", "ftp://")):
        return True
    # 无扩展名 / 以"见"字开头/中文措辞引用 视为叙述，不判
    if not re.search(r"\.[A-Za-z0-9]{2,5}$", s):
        return True
    return False


def main():
    run = sys.argv[1] if len(sys.argv) > 1 else None
    if not run or not os.path.isdir(run):
        print("用法: check_delivery.py <runs/<项目>>"); sys.exit(2)
    issues = []
    warns = []

    deliv = os.path.join(run, "delivery")
    m4 = os.path.join(run, "m4-prompts")

    # ---- A) 多源并存 prompt 执行件 ----
    m4_prompts = [f for f in (os.listdir(m4) if os.path.isdir(m4) else []) if f.endswith(".md")]
    # run 根目录与 delivery 副目录的同题 prompt 文件
    extra_prompts = []
    for base in (run, deliv):
        if os.path.isdir(base):
            for f in os.listdir(base):
                if f.startswith("prompts-") and f.endswith(".md"):
                    extra_prompts.append(os.path.join(base, f).replace(run + os.sep, ""))
    if os.path.isdir(deliv):
        deliv_prompts = [f for f in os.listdir(deliv) if f.startswith("prompts-") and f.endswith(".md")]
        # m4-prompts 与 delivery 若都有同平台 prompt 文件，判"双写"（除非二者内容完全一致）
        for f in deliv_prompts:
            m4f = os.path.join(m4, f)
            df = os.path.join(deliv, f)
            if os.path.isfile(m4f) and os.path.isfile(df):
                if open(m4f, encoding="utf-8-sig", errors="ignore").read() != open(df, encoding="utf-8-sig", errors="ignore").read():
                    issues.append(f"A FAIL: 同题 prompt '{f}' 在 m4-prompts/ 与 delivery/ 内容不一致(双源漂移)")
        # 若 delivery 引用了不在 m4-prompts 的平台 prompt、而 run 根另有同名 → 多源并存
        readme = os.path.join(deliv, "README.md")
        if os.path.isfile(readme):
            rtxt = open(readme, encoding="utf-8-sig", errors="ignore").read()
            for ref in _inline_refs(rtxt):
                if ref.startswith("prompts-"):
                    # 引用非 m4-prompts 一致件？引用了 run 根或别处件 = 指向漂移源
                    if ref not in m4_prompts and os.path.exists(os.path.join(run, ref)):
                        issues.append(f"A FAIL: delivery/README 引用 '<run>/…/{ref}' 而非 m4-prompts/{ref}（多源并存）")

    # ---- B) 交付包自包含（死链）—— 只对 delivery/README.md（上手包索引，自包含契约）核 ----
    if os.path.isdir(deliv):
        readme = os.path.join(deliv, "README.md")
        if os.path.isfile(readme):
            txt = open(readme, encoding="utf-8-sig", errors="ignore").read()
            for ref in _inline_refs(txt):
                if _url_or_external(ref):
                    continue
                target = os.path.normpath(os.path.join(deliv, ref))
                # 引用必须能落到 delivery/ 内；引用了一个确实存在但没打进包的文件 = 死链/不自包含
                if not os.path.exists(target):
                    if os.path.exists(os.path.join(run, ref)):
                        issues.append(f"B FAIL [delivery/README.md]: 引用 '{ref}' 在 run 根存在但未打进 delivery/（上手包不自包含/死链）")
                    else:
                        warns.append(f"B 提示 [delivery/README.md]: 引用 '{ref}' 未找到，请确认是否为外部资源")

    # ---- C) 版本漂移 ----
    # C1 多个 口播稿-定稿v*.md 并存
    for base in (run, deliv):
        if not os.path.isdir(base):
            continue
        scripts = [f for f in os.listdir(base) if f.startswith("screenwriter-口播稿") and "定稿v" in f]
        if len(scripts) > 1:
            issues.append(f"C FAIL: 同时存在多个口播稿版本 {sorted(scripts)}（版本漂移，交付前收敛为单一「定稿」）")
    # C2 delivery 分镜表 标题版本 vs 正文版本不一致
    for base in (deliv, run):
        if not os.path.isdir(base):
            continue
        for f in os.listdir(base):
            if f.startswith("storyboard-分镜表") and f.endswith(".md"):
                txt = open(os.path.join(base, f), encoding="utf-8-sig", errors="ignore").read()
                # 标题标注版本
                title_v = re.search(r"(?:v\d+|\d+[sS])", txt[:600])
                # 正文出现的"约75s"或口播 v9
                body_dur = re.findall(r"(约)?\s*(7[0-9]|8[0-9]|9[0-9])\s*s", txt)
                dur_set = sorted(set(tuple(d) for d in body_dur))
                # 若标题出现 90s 而正文只出现 75s → 漂移
                title_has_90 = bool(re.search(r"(90s|约90|90 秒)", txt[:1200]))
                body_has_75 = bool(re.search(r"(约75s|~75s|75 s)", txt))
                if title_has_90 and body_has_75:
                    issues.append(f"C FAIL [{f}]: 分镜表标题=90s 但正文含 75s 表述（版本漂移）")
                break

    if issues:
        print(f"== 交付包一致性 FAIL ({len(issues)} 条) ==")
        for x in issues:
            print(" -", x)
        print("=> 按制：单一执行源(m4-prompts) + 交付包自包含 + 版本收敛为单一定稿；修复后再交付。")
        sys.exit(1)
    print("== 交付包一致性 PASS: 单一执行源 / 交付包自包含 / 版本收敛 ==")
    if warns:
        print("== 提示 == ")
        for w in warns:
            print(" -", w)


if __name__ == "__main__":
    main()
