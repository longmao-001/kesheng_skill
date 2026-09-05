#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SOP 完整性门控 (check_sop.py)

按里程碑检查 runs/<项目>/ 该有的产物是否齐全（考勤式门控：哪步被跳过→缺哪个产物=FAIL）。
用法: python -X utf8 scripts/check_sop.py <runs/<项目>>
* 有产物 = 该步做了；缺 = 检出跳 SOP → 打回补做/回退（制片人门控；见 ORCHESTRATION §5/§7）。
"""
import io, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def main():
    run = sys.argv[1] if len(sys.argv) > 1 else None
    if not run or not os.path.isdir(run):
        print("用法: check_sop.py <runs/<项目>>"); sys.exit(2)

    def has(p): return os.path.exists(os.path.join(run, p))
    def any_of(ps): return any(has(p) for p in ps)
    def glob_list(pat):
        import glob
        return [os.path.basename(x) for x in glob.glob(os.path.join(run, pat))]

    issues = []
    def req(step, cond, desc, needed):
        if cond: pass
        else: issues.append((step, desc, needed))

    # KSP-01/02 简报+定档
    req("KSP-01/02", any_of(["brief.md", "m1-汇总.md", "STATE.md"]) or glob_list("brief*.md"), "需求简报+预注册+定档", "brief.md/m1-汇总.md")
    # KSP-03 科学理解+报告+docx/PPT+拍板记录(审阅'继续')
    req("KSP-03", any_of(["scientist-理解报告.md", "science-data.json"]) or glob_list("scientist-*"), "科学理解报告", "scientist-理解报告.md")
    req("KSP-03", has("scientist-报告.docx"), "docx 报告", "scientist-报告.docx")
    req("KSP-03", has("scientist-讲解.pptx"), "PPT", "scientist-讲解.pptx")
    req("KSP-03", any_of(["m2-纪要.md", "m3-定稿.md"]) or glob_list("m2-纪要*"), "报告审阅/讨论纪要(用户'继续')", "m2-纪要.md 或 拍板记录")
    # 素材库(自建)
    req("素材库", has("assets-inventory.md"), "自建素材库存档", "assets-inventory.md")
    # KSP-03.5 主题共识+重点
    req("KSP-03.5", any_of(["ksp035-重点协议.md", "style-baseline-固化.md"]) or glob_list("ksp03*"), "主题共识+内容重点协议", "ksp035-重点协议.md")
    # KSP-04/M3 概念先行+评分+拍板
    req("KSP-04", any_of(glob_list("*-概念先行.md") + ["m3-proposal.md", "director-概念先行.md"]), "概念先行(各角色观点)", "*-概念先行.md")
    req("KSP-04", any_of(["m3-scoring.md", "m3-定稿.md"]), "概念评分/拍板", "m3-scoring.md")
    # 风格基线/美术(baseline)
    req("风格基线", any_of(["style-baseline-固化.md", "art-director-美术方案.md", "art-director-色板更新.md"]), "风格基线(含用户拍板)", "style-baseline-固化.md")
    # M4 分镜+口播+声音+摄影
    req("M4分镜", any_of(["storyboard-分镜表.md", "storyboard-九宫格方案.md"]), "分镜表", "storyboard-分镜表.md")
    req("M4口播", any_of(glob_list("screenwriter-口播稿*") ), "口播稿(含定稿)", "screenwriter-口播稿*.md")
    req("M4声音", any_of(["sound-声音方案.md"]), "声音方案", "sound-声音方案.md")
    req("M4摄影", any_of(["dop-摄影方案.md"]), "摄影方案", "dop-摄影方案.md")
    # prompt + 校验
    prompts = glob_list("m4-prompts/prompts-*.md")
    req("M4prompt", bool(prompts), "逐镜 prompt", "m4-prompts/prompts-*.md")
    # 科学复核(检察官 L3) + 红队前置闸
    req("L3复核", any_of(["scientist-科学复核.md", "scientist-硬约束清单.md"]), "科学复核(L3事实检察官)", "scientist-科学复核.md")
    req("红队闸", any_of(["m4-gate-red.md", "m5-gate-red.md"]), "红队闸(前置/出口)", "m4-gate-red.md")

    # 每镜 prompt 完整性（prompt SOP 十步考勤）：每镜必含 参考(挂载清单)/风格/时间轴/口播/声音/负面/参数
    import re
    PF = ["参考", "风格", "时间轴", "口播", "声音", "负面", "参数"]
    md = os.path.join(run, "m4-prompts")
    if os.path.isdir(md):
        import glob as _glob
        for pf in sorted(_glob.glob(os.path.join(md, "prompts-*.md"))):
            shot = None; fields = set()
            for line in io.open(pf, encoding="utf-8-sig"):
                s = line.strip()
                if s.startswith("### 镜头"):
                    if shot is not None:
                        missing = [f for f in PF if f not in fields]
                        if missing: issues.append((f"prompt[{os.path.basename(pf)}] 镜{shot[:18]}", "每镜 prompt 字段不全(缺)", "/".join(missing)))
                    shot = s; fields = set()
                elif s.startswith("**") and "**：" in s:
                    name = s[2:].split("**：", 1)[0].strip()
                    fields.add(name)
                elif s.startswith("**") and s.endswith("**"):
                    nm = s[2:-2].strip()
                    if nm in PF: fields.add(nm)
            if shot is not None:
                missing = [f for f in PF if f not in fields]
                if missing: issues.append((f"prompt[{os.path.basename(pf)}] 镜{shot[:18]}", "每镜 prompt 字段不全(缺)", "/".join(missing)))

    if issues:
        print(f"== check_sop FAIL: 检出跳 SOP / 缺产物 {len(issues)} 步 ==")
        for step, desc, needed in issues:
            print(f"  - 缺[{step}] {desc}（需要 {needed}）")
        print("=> 按 ORCHESTRATION §5 门控：补齐/回退到缺的那步，不跳 SOP；制片人门控 + check_sop.py 兜底。")
        sys.exit(1)
    print(f"== check_sop PASS: runs/{os.path.basename(run)} 各里程碑 SOP 产物齐 ==")

if __name__ == "__main__":
    main()
