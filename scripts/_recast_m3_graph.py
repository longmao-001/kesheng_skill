# -*- coding: utf-8 -*-
"""Recast M3 in the graph source seeds: 盲提案 -> 概念先行, count 1-2 -> 5."""
import io

P = r"F:/AI/kesheng/packs"
REPL = {
 f"{P}/workflow-seed/kg.json": [
   ("盲提案+整合总方案(M3)", "概念先行：生成5个创意概念→拍板→深化总方案(M3)"),
   ("盲提案·影像质感(M3)", "概念先行·影像质感(M3)"),
   ("盲提案(叙事角度)", "概念先行(叙事角度)"),
 ],
 f"{P}/director-seed/kg.json": [
   ("合并四份盲提案出总方案v1", "整合5个创意概念→概念拍板→深化为总方案v1"),
 ],
 f"{P}/papers-kg/kg.json": [
   ("支撑'盲提案+交叉质询+反假共识'", "支撑'概念先行的独立发散创意(防群体思维)+交叉评审'"),
 ],
 f"{P}/sop-seed/kg.json": [
   ("各1-2个概念", "各5个概念"),
   ("概念卡×3-4", "概念卡×5"),
 ],
}

for path, reps in REPL.items():
    txt = io.open(path, encoding="utf-8").read()
    n = 0
    for old, new in reps:
        c = txt.count(old)
        if c == 0:
            print(f"  !! {path.split(chr(92))[-1]}: '{old}' not found")
        txt = txt.replace(old, new)
        n += c
    io.open(path, "w", encoding="utf-8").write(txt)
    print(f"  {path.split(chr(92))[-1]}: {n} replacement(s)")
print("done")
