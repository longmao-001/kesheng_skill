# -*- coding: utf-8 -*-
"""Mirror M3=概念先行(+5概念) across docs, card headers, and 产物名. Recast old 盲提案 framings."""
import io, glob, os

ROOT = r"F:/AI/kesheng"
MD_GLOB = ["agents/*.md", "SKILL.md", "README.md", "docs/*.md", "orchestration/*.md",
           "protocols/*.md", "playbooks/*.md", "templates/*.md"]

# universal (apply everywhere)
UNI = [
 ("盲提案时禁止读其他提案", "概念独立生成时禁止互读概念（拍板时才并列展示）"),
 ("各出 **1-2 个创意概念**", "各出 **5 个创意概念**"),
 ("各出 1-2 个创意概念", "各出 5 个创意概念"),
 ("_盲提案.md", "_概念.md"),
 # user-gate #9 概念拍板 5 options
 ("概念A（Recommended）/ 概念B / 概念C / 融合两个概念（指出）/ 自定义",
  "概念A / 概念B / 概念C / 概念D / 概念E（Recommended）/ 融合两个概念（指出）/ 自定义"),
]

# contextual (nounce old blind-proposal framings -> concept-first)
CTX = [
 ("作为旧\"盲提案×4+评审\"", "作为旧\"盲提案×4+评审\"（已被概念先行取代）"),
 ("盲提案×3 + 交叉质询 + 红队", "概念先行（多方向创意）+ 概念拍板 + 红队"),
 ("盲提案×4（编剧/分镜师/摄影指导/导演总方案）→ 交叉质询×4（L 档+红队）→ 导演整合、制片人按预注册标准裁决",
  "概念先行（编剧/分镜师/摄影指导/导演各出 5 个创意方向）→ 概念拍板（选一/融合）→ 导演深化、制片人按预注册标准复核"),
 ("盲提案×3 → 交叉质询 → 裁决", "概念先行（多方向）→ 概念拍板 → 深化"),
 ("盲提案×3", "概念先行（多方向）"),
 ("盲提案×4", "概念先行（多方向）"),
 ("盲提案 3 路", "概念先行（并行出概念）"),
 ("盲提案 4 路", "概念先行（并行出概念）"),
 ("盲提案并行 4 路 → 交叉质询并行 4 路", "概念先行并行 4 路 → 概念拍板"),
 ("盲提案限 4 份（编剧/分镜师/摄影指导/导演）", "概念先行限多方向（编剧/分镜师/摄影指导/导演各出概念）"),
 ("盲提案3路 → 质询3路(+红队)", "概念先行（多方向）→ 概念拍板"),
 ("盲提案3路 → 质询3路", "概念先行（多方向）→ 概念拍板"),
 ("盲提案（+可选交叉质询+红队）", "概念先行（+可选红队评审）"),
 ("盲提案4路(编剧/分镜/摄影/导演)", "概念先行（编剧/分镜/摄影/导演各出概念并展示）"),
 ("盲提案+质询", "概念先行+概念拍板"),
 ("盲提案→质询→导演整合 v1", "概念先行→概念拍板→导演深化 v1"),
 ("盲提案→质询→导演整合", "概念先行→概念拍板→导演深化"),
 ("盲提案（叙事角度）→质询", "概念先行（叙事角度）"),
 ("M3 合并四份盲提案出总方案v1", "M3 整合5个创意概念→拍板→深化总方案v1"),
 ("跳过盲提案直接跟风", "没出可对比的概念就带偏/跟风"),
 ("M3 盲提案", "M3 概念先行"),
]

files = set()
for g in MD_GLOB:
    for p in glob.glob(os.path.join(ROOT, g)):
        files.add(p)

tot = 0
for p in sorted(files):
    txt = io.open(p, encoding="utf-8").read()
    orig = txt
    for old, new in CTX:
        txt = txt.replace(old, new)
    for old, new in UNI:
        txt = txt.replace(old, new)
    # catch-all: any residual 盲提案 in normal doc prose -> 概念先行 (except legacy/failure-lib which may keep the term)
    if "FAILURE-LIBRARY" not in p:
        txt = txt.replace("盲提案", "概念先行")
    if txt != orig:
        io.open(p, "w", encoding="utf-8").write(txt)
        tot += 1
        print(f"  updated {os.path.relpath(p, ROOT)}")
print(f"\ntotal files changed: {tot}")
