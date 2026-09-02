#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
素材批量分类+命名 (classify_assets.py)

按 templates/assets-inventory.md 的「用途分级×内容类型」+「文件名=条目ID」命名规范，
扫描一个素材目录，按文件名关键词自动分类并提议新名，可选批量重命名 + 生成 assets-inventory.md。

用法:
  python scripts/classify_assets.py <素材目录> [--subject 量测机台] [--apply] [--inv assets-inventory.md]
  (不带 --apply = 只打印分类/命名提议表，不做任何改动)

命名: <用途>_<类型>_<主体>_<视角或部位>[_<版本>].<ext>
  用途: IN直接入镜 / RF参考图 / CT内容参考
  类型: MAIN主体锚/PART部件/SCENE场景/TEXT质感/STR结构/DATA图表/BRAND品牌/RAW实拍
"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".mp4", ".mov", ".avi"}

# 关键词 → (用途, 类型)  按"像哪个"分类，仅供提议，最终人工确认
RULE = [
 (["logo", "vi", "标准色", "标志"], ("RF", "BRAND")),
 (["曲线", "折线", "图表", "表格", "数据", "测试", "规格"], ("CT", "DATA")),
 (["接口", "结构", "爆炸", "爆炸图", "示意图", "原理", "剖视", "剖面", "解剖"], ("CT", "STR")),
 (["视频", "实拍", "装机", "现场", "案例", "demo"], ("IN", "RAW")),
 (["场景", "实验室", "车间", "流水线", "环境", "背景", "机房"], ("RF", "SCENE")),
 (["材质", "质感", "拉丝", "磨砂", "表面", "纹理", "细节", "微距"], ("RF", "TEXT")),
 (["三视图", "正视图", "侧", "俯", "顶", "45", "多角度", "渲染", "外观", "整机"], ("RF", "MAIN")),
 (["鳍片", "出光", "接口", "灯", "面板", "开关", "部件", "局部", "logo特写"], ("RF", "PART")),
]
VIEW_RE = re.compile(r"(正视图|侧视图|俯视图|顶视图|三视图|45°|剖视|特写|正|侧|俯|顶|45|局部)")


def classify(name):
    low = name.lower()
    for kws, val in RULE:
        if any(k in name for k in kws):
            return val, [k for k in kws if k in name]
    return ("RF", "MAIN"), []  # 默认主体锚, 待确认


def pick_view(name):
    m = VIEW_RE.search(name)
    return m.group(1) if m else "视角待定"


def main():
    args = sys.argv[1:]
    if not args or not os.path.isdir(args[0]):
        print("用法: classify_assets.py <素材目录> [--subject 主体] [--apply] [--inv <file>]"); sys.exit(2)
    folder = args[0]
    subject = "主体"
    apply_rename = False
    inv_path = None
    i = 1
    while i < len(args):
        if args[i] == "--subject" and i + 1 < len(args):
            subject = args[i + 1]; i += 2
        elif args[i] == "--apply":
            apply_rename = True; i += 1
        elif args[i] == "--inv" and i + 1 < len(args):
            inv_path = args[i + 1]; i += 2
        else:
            i += 1

    files = sorted(f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in EXT
                   and not f.startswith("."))
    if not files:
        print("目录内没有图片/视频素材"); sys.exit(0)

    rows, rename_map = [], []
    seen_seq = {}
    print(f"== 素材分类+命名提议（{len(files)} 个，{folder}）==  主体<{subject}>")
    for f in files:
        name, ext = os.path.splitext(f)
        (use, typ), matched = classify(name)
        view = pick_view(name)
        # 同 用途_类型 递增序号
        key = (use, typ)
        seen_seq[key] = seen_seq.get(key, 0) + 1
        seq = f"{seen_seq[key]:02d}"
        newname = f"{use}_{typ}_{subject}_{view}_{seq}{ext}"
        rename_map.append((f, newname))
        flag = "" if matched else "  (未匹配关键词, 默认RF_MAIN, 请人工确认)"
        rows.append((f, use, typ, view, seq, matched))
        print(f"  {f:44s} -> {newname}{flag}")

    if apply_rename:
        print("\n== 应用重命名 ==")
        for old, new in rename_map:
            if old != new:
                os.rename(os.path.join(folder, old), os.path.join(folder, new))
                print(f"  renamed {old} -> {new}")
    else:
        print("\n(仅提议，未改文件；加 --apply 批量重命名；先备份再跑)")

    if inv_path:
        with io.open(inv_path, "w", encoding="utf-8") as fh:
            fh.write(f"# 素材库清单（Assets Inventory）—— {subject}\n\n")
            fh.write("| 条目ID(=文件名) | 用途分级 | 内容类型 | 主体 | 视角·部位 | 来源·授权 | 备注 |\n|---|---|---|---|---|---|---|\n")
            for old, new in rename_map:
                use, typ = new.split("_")[0], new.split("_")[1]
                fh.write(f"| `{new}` | {use} | {typ} | {subject} | {pick_view(old)} | 待补 | 待确认分类 |\n")
        print(f"\n已生成台账 {inv_path}")


if __name__ == "__main__":
    main()
