#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
素材智能入库脚手架 (annotate_assets.py)

按 templates/assets-inventory.md 的「智能入库三件套」为每个素材生成待填充台账行 + SOP 提醒。
多模态拆解/反推prompt/打分 需用 read_image 看真图后人工/agent 填充（这是文字检索键）。

用法:
  python scripts/annotate_assets.py <素材目录> [--subject 主体] [--out <assets-annotate.md>]
  (默认打印；--out 写入文件)
"""
import io, os, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".mp4", ".mov"}
# 分类关键词 (复用 classify_assets 的粗判)
RULES = [
 (["logo","vi","标志"], ("RF","BRAND")),
 (["曲线","折线","图表","数据","测试","规格"], ("CT","DATA")),
 (["接口","结构","爆炸","原理","剖视","剖面"], ("CT","STR")),
 (["视频","实拍","装机","现场","案例"], ("IN","RAW")),
 (["场景","实验室","车间","环境","背景"], ("RF","SCENE")),
 (["材质","质感","拉丝","磨砂","表面"], ("RF","TEXT")),
 (["三视图","正","侧","俯","顶","45","渲染","外观","整机"], ("RF","MAIN")),
 (["鳍片","出光","接口","灯","面板","开关","部件","局部"], ("RF","PART")),
]
VIEW_RE = re.compile(r"(正视图|侧视图|俯视图|45°|剖视|特写|局部|正|侧|俯|顶|45)")

def classify(name):
    for kws, v in RULES:
        if any(k in name for k in kws):
            return v
    return ("RF","MAIN")

def view(name):
    m = VIEW_RE.search(name); return m.group(1) if m else "待定"

def main():
    args = sys.argv[1:]; folder = None; subject="主体"; out=None; i=0
    while i < len(args):
        if args[i] in ("--subject",) and i+1 < len(args): subject=args[i+1]; i+=2
        elif args[i]=="--out" and i+1 < len(args): out=args[i+1]; i+=2
        else: folder=args[i]; i+=1
    if not folder or not os.path.isdir(folder):
        print("用法: annotate_assets.py <素材目录> [--subject 主体] [--out <file>]"); sys.exit(2)
    files = sorted(f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in EXT and not f.startswith("."))
    if not files:
        print("目录无图片/视频"); sys.exit(0)
    rows = []
    seq = {}
    for f in files:
        name, ext = os.path.splitext(f)
        (use, typ), = [classify(name)]
        key=(use,typ); seq[key]=seq.get(key,0)+1
        newid=f"{use}_{typ}_{subject}_{view(name)}_{seq[key]:02d}{ext}"
        rows.append((newid, use, typ, subject, view(name)))
    lines = ["# 素材智能入库（待多模态识别填充）", "",
             f"> 每张用 `read_image` 看真图，填：①内容标签(物品/任务/场景/结构/质感/数据/品牌/实拍) ②AI合成反推prompt ③质量分(★1-5，合规一票否决)。",
             "| 条目ID(=文件名) | 用途分级 | 内容类型 | 主体 | 视角·部位 | 内容标签 | AI合成反推prompt | 质量分 | 来源·授权 | 备注 |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for newid, use, typ, subj, v in rows:
        lines.append(f"| `{newid}` | {use} | {typ} | {subj} | {v} | 待填:物品/任务/场景/结构/质感/数据/品牌/实拍 | 待填:文生图prompt | ★待填 | 待补 | 待确认 |")
    txt = "\n".join(lines) + "\n"
    if out:
        io.open(out, "w", encoding="utf-8").write(txt); print(f"written -> {out}")
    else:
        print(txt)
    print(f"\n({len(files)} 素材 → 每条用 read_image 看真图后填 内容标签/AI合成反推prompt/质量分；打分维度见 templates/assets-inventory.md §三)")

if __name__ == "__main__":
    main()
