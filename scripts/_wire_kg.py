# -*- coding: utf-8 -*-
"""Wire mandatory per-role domain kg_query into each role card header workflow line.
Converts the optional "(或 kg_query --domain 工艺 <role>)" into a hard first step:
读文档 -> 必跑 --depth 2 --domain <本域> <关键词>. Every keyword verified to HIT."""
import io, re, os

AG = r"F:/AI/kesheng/agents"
# card -> (primary domain, primary kw, alternate kw list)
ROLE = {
 "producer.md":          ("工艺", "门控", ["KSP"]),
 "director.md":          ("导演", "作者论", ["场面调度", "导演风格"]),
 "screenwriter.md":      ("叙事", "结构", ["口播", "旁白"]),
 "storyboard-artist.md": ("分镜", "景别", ["分镜"]),
 "art-director.md":      ("美术", "三点布光", ["色彩分级", "场景氛围"]),
 "dop.md":               ("影像", "运镜", ["构图", "景别"]),
 "sound-designer.md":    ("声音", "音乐", ["情绪"]),
 "editor.md":            ("剪辑", "节奏", ["转场"]),
 "scientist.md":         ("科学", "<根据项目替换关键词>", ["科普"]),
 "prompt-engineer.md":   ("prompt", "单镜", ["分镜"]),
 "audience-advocate.md": ("受众", "注意力", ["痛点"]),
 "red-team.md":          ("红队", "红队", ["--domain 工艺 门控"]),
}
# role display label per card (for the 读文档 anchor) — derive from existing text to avoid mismatch
label_hint = {
 "producer.md": "制片人", "director.md": "导演", "screenwriter.md": "编剧",
 "storyboard-artist.md": "分镜师", "art-director.md": "美术指导", "dop.md": "摄影指导",
 "sound-designer.md": "声音设计师", "editor.md": "剪辑师", "scientist.md": "科学顾问",
 "prompt-engineer.md": "prompt工程师", "audience-advocate.md": "观众代言人", "red-team.md": "红队",
}

def replace_header(path, dom, primary, alts):
    txt = io.open(path, encoding="utf-8").read()
    # find the (或 `python .../kg_query.py --domain 工艺 <role>`） block
    pat = re.compile(r"（或 `python F:/AI/kesheng/packs/kg_query\.py --domain 工艺 [^`]+`），按 SOP 执行。")
    new_block = (
        "；**开工必跑** `python F:/AI/kesheng/packs/kg_query.py "
        f"--depth 2 --domain {dom} {primary}`（可换查：{' / '.join(alts)}）"
        "抽取本域事实/发现/规则/论文证据。** "
        "关键主张引用图上 `权威正文` 来源，无来源不进稿。按 SOP 执行。"
    )
    txt, n = pat.subn(lambda m: new_block, txt, count=1)
    if n != 1:
        print(f"  !! {os.path.basename(path)}: pattern not matched ({n})")
    else:
        io.open(path, "w", encoding="utf-8").write(txt)
        print(f"  ok {os.path.basename(path)}")

for card, (dom, primary, alts) in ROLE.items():
    replace_header(os.path.join(AG, card), dom, primary, alts)
print("done")
