#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科学调查报告 → 结构化 Markdown + 适配 Word 的 docx + PPT 大纲(+可选 pptx 兜底)

用法:
  python -X utf8 scripts/build_science_report.py --json <science-data.json> --out <runs/<slug>/>

产出（全部落在 --out 目录）:
  scientist-理解报告.md          结构化 Markdown（**唯一事实源**，正文也照此写进对话）
  scientist-报告.docx            真正适配 Word：封面/目录/页眉页脚页码/中文字体/首行缩进/真表格
  scientist-讲解-大纲.md          PPT 大纲（交 ppt-master 或 huashu-design 生成高保真 PPT）
  scientist-讲解.pptx             兜底版（本机 python-pptx 直出，质量一般；有技能时用技能版）

science-data.json 结构:
  {title, oneLiner, keyPoints[], timeline[], productPrinciple, sellingPoints[],
   science, data[{value,baseline,plain,cite}], pending[], depth, subtitle?, author?}

铁则: 数据有出处；不确定标"待确认"；绝不编造。
"""
import argparse
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def build_markdown(d):
    """科学报告 → 结构化 Markdown（供对话展示 + 转 docx）。"""
    L = []
    title = d.get("title", "科学讲解")
    L.append(f"# {title}\n")
    if d.get("oneLiner"):
        L.append(f"> **一句话定位**：{d['oneLiner']}\n")

    if d.get("keyPoints"):
        L.append("## 一、重点 / 核心看点\n")
        for i, x in enumerate(d["keyPoints"], 1):
            L.append(f"{i}. {x}")
        L.append("")

    if d.get("timeline"):
        L.append("## 二、时间线 / 关键节点\n")
        for x in d["timeline"]:
            L.append(f"- {x}")
        L.append("")

    if d.get("productPrinciple"):
        L.append("## 三、产品原理（怎么工作 / 构成）\n")
        L.append(str(d["productPrinciple"]).strip() + "\n")

    if d.get("sellingPoints"):
        L.append("## 四、产品卖点（用户得到的好处）\n")
        for x in d["sellingPoints"]:
            L.append(f"- {x}")
        L.append("")

    if d.get("science"):
        L.append("## 五、科学原理（背后机理 / 因果链）\n")
        L.append(str(d["science"]).strip() + "\n")

    if d.get("data"):
        L.append("## 六、关键数据（带基准 + 口语化 + 出处）\n")
        L.append("| 数据 | 对比基准 | 口语化翻译 | 出处 |")
        L.append("|---|---|---|---|")
        for r in d["data"]:
            L.append("| {v} | {b} | {p} | {c} |".format(
                v=r.get("value", ""), b=r.get("baseline", ""),
                p=r.get("plain", ""), c=r.get("cite", "")))
        L.append("")

    if d.get("pending"):
        L.append("## 七、待确认清单（不确定项）\n")
        for x in d["pending"]:
            L.append(f"- {x}")
        L.append("")

    if d.get("depth"):
        L.append("## 八、理解深度自评\n")
        L.append(f"- {d['depth']}\n")
    return "\n".join(L)


def build_deck_outline(d):
    """PPT 大纲（交 ppt-master / huashu-design；格式见 templates/science-ppt.md）。"""
    L = []
    L.append(f"# 科学讲解 PPT 大纲 · {d.get('title', '')}\n")
    L.append("> 交 `ppt-master`（原生可编辑 PPTX）或 `huashu-design`（HTML deck / 高保真视觉）生成。")
    L.append("> 配图优先取素材库条目（`assets-inventory.md`）；禁用水印/竞品/未授权图。\n")
    pages = []
    pages.append(("封面", [d.get("title", "")] + ([d["oneLiner"]] if d.get("oneLiner") else []), "主体封面图（产品/场景）"))
    if d.get("oneLiner"):
        pages.append(("一句话定位", [d["oneLiner"]], "—"))
    if d.get("keyPoints"):
        pages.append(("重点速览", d["keyPoints"][:3], "—"))
    if d.get("timeline"):
        pages.append(("时间线", d["timeline"][:6], "时间轴图"))
    if d.get("productPrinciple"):
        pages.append(("产品原理", [str(d["productPrinciple"])[:120]], "产品图/结构图"))
    if d.get("sellingPoints"):
        for i in range(0, min(len(d["sellingPoints"]), 4), 2):
            pages.append((f"产品卖点 {i // 2 + 1}", d["sellingPoints"][i:i + 2], "实测/对比图"))
    if d.get("science"):
        pages.append(("科学原理", [str(d["science"])[:120]], "原理示意图"))
    if d.get("data"):
        pages.append(("关键数据", [f"{r.get('value')}｜{r.get('plain', '')}" for r in d["data"][:5]], "曲线/参数表"))
    if d.get("pending"):
        pages.append(("待确认", d["pending"][:4], "—"))
    pages.append(("谢谢 / 展望", ["—"], "主体收尾图"))
    for i, (name, items, img) in enumerate(pages, 1):
        L.append(f"## 页{i} · {name}\n")
        for it in items:
            if str(it).strip():
                L.append(f"- {str(it)[:60]}")
        L.append(f"配图: {img}")
        L.append("出处: （标数据/图片来源）\n")
    return "\n".join(L)


def build_pptx_fallback(d, path):
    """兜底 pptx（本机直出，质量一般；优先用 ppt-master / huashu-design）。"""
    try:
        from pptx import Presentation
        from pptx.util import Inches, Pt as PPt
    except Exception as e:  # noqa: BLE001
        print(f"  [跳过 pptx 兜底] python-pptx 不可用: {e}")
        return False
    prs = Presentation()
    blank = prs.slide_layouts[6]

    def slide_text(title, lines):
        s = prs.slides.add_slide(blank)
        tb = s.shapes.add_textbox(Inches(0.7), Inches(0.5), Inches(8.6), Inches(1.0))
        tf = tb.text_frame; tf.text = title
        tf.paragraphs[0].runs[0].font.size = PPt(28); tf.paragraphs[0].runs[0].font.bold = True
        body = s.shapes.add_textbox(Inches(0.7), Inches(1.7), Inches(8.6), Inches(4.6))
        bf = body.text_frame; bf.word_wrap = True
        first = True
        for ln in lines:
            p = bf.paragraphs[0] if first else bf.add_paragraph()
            first = False
            p.text = f"· {ln}" if not str(ln).startswith("·") else str(ln)
            p.font.size = PPt(18)

    slide_text(d.get("title", "科学讲解"), [d.get("oneLiner", "")])
    if d.get("keyPoints"):
        slide_text("重点速览", d["keyPoints"][:3])
    if d.get("timeline"):
        slide_text("时间线", d["timeline"][:6])
    if d.get("productPrinciple"):
        slide_text("产品原理", [str(d["productPrinciple"])[:200]])
    if d.get("sellingPoints"):
        slide_text("产品卖点", d["sellingPoints"][:4])
    if d.get("science"):
        slide_text("科学原理", [str(d["science"])[:200]])
    if d.get("data"):
        slide_text("关键数据", [f"{r.get('value')}｜{r.get('plain', '')}｜{r.get('cite', '')}" for r in d["data"][:5]])
    if d.get("pending"):
        slide_text("待确认", d["pending"][:4])
    prs.save(path)
    return True


def main():
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser(description="科学报告 → 结构化md + Word适配docx + PPT大纲")
    ap.add_argument("--json", required=True, help="science-data.json")
    ap.add_argument("--out", required=True, help="输出目录（建议 runs/<项目slug>/）")
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--author", default="科生 · 科学顾问")
    a = ap.parse_args()

    d = json.load(io.open(a.json, encoding="utf-8-sig"))
    out = a.out
    os.makedirs(out, exist_ok=True)
    title = d.get("title", "科学讲解")

    # 1) 结构化 md（唯一事实源）
    md = build_markdown(d)
    md_path = os.path.join(out, "scientist-理解报告.md")
    with io.open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"== 科学报告生成 → {out}")
    print(f"  md   -> {md_path}")

    # 2) docx（适配 Word：封面/目录/页眉页脚/真表格）
    docx_path = os.path.join(out, "scientist-报告.docx")
    try:
        import md_to_docx
        md_to_docx.build(md_path, docx_path, title=title,
                         subtitle=a.subtitle or "科学理解报告", author=a.author)
        print(f"  docx -> {docx_path}（封面/目录/页眉页脚页码/中文字体/真表格）")
    except Exception as e:  # noqa: BLE001
        print(f"  [docx 失败] {e}")

    # 3) PPT 大纲（交 ppt-master / huashu-design）
    outline_path = os.path.join(out, "scientist-讲解-大纲.md")
    with io.open(outline_path, "w", encoding="utf-8") as f:
        f.write(build_deck_outline(d))
    print(f"  PPT大纲 -> {outline_path}")

    # 4) pptx 兜底
    pptx_path = os.path.join(out, "scientist-讲解.pptx")
    if build_pptx_fallback(d, pptx_path):
        print(f"  pptx(兜底) -> {pptx_path}")

    print("\n  ▶ 提升 PPT 质量（推荐，别用兜底版交付）：")
    print("     · ppt-master   —— 原生可编辑 PPTX（走 generate-pptx 路由；input=上面的 PPT 大纲）")
    print("     · huashu-design —— 高保真 HTML deck（视觉更强，可导 PDF/可编辑 PPTX）")
    print("     · docx 已有封面/目录/页码，可直接交用户")


if __name__ == "__main__":
    main()
