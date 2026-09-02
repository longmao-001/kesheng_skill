#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科学调查报告 → docx + pptx 生成器 (build_science_report.py)

用法:
  python scripts/build_science_report.py --json <science-data.json> [--out <runs/<slug>/scientist-讲解.pptx>]

science-data.json 结构:
  {title, oneLiner, keyPoints[str], timeline[str], productPrinciple,
   sellingPoints[str], science, data[{value,baseline,plain,cite}], pending[str], depth}

依赖: python-docx / python-pptx (pip install python-docx python-pptx)。缺库时提示装或交给
report-writer / ppt-master / markdown-exporter 技能。
"""
import io, json, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

def main():
    args = sys.argv[1:]
    json_path = None
    out_dir = None
    i = 0
    while i < len(args):
        if args[i] == "--json" and i + 1 < len(args):
            json_path = args[i + 1]; i += 2
        elif args[i] == "--out" and i + 1 < len(args):
            out_dir = os.path.dirname(args[i + 1]); i += 2
        else:
            i += 1
    if not json_path:
        print("用法: build_science_report.py --json <science-data.json> [--out <路径>]"); sys.exit(2)
    data = json.load(io.open(json_path, encoding="utf-8-sig"))

    OK = []
    try:
        import docx  # noqa
        from docx import Document
        OK.append("docx")
    except Exception:
        OK.append("!docx")
    try:
        import pptx  # noqa
        from pptx import Presentation
        OK.append("pptx")
    except Exception:
        OK.append("!pptx")

    base = out_dir or "."
    title = data.get("title", "科学讲解")
    print(f"== 科学报告生成 == [{', '.join(OK)}]  -> {base}")

    # docx
    lines = []
    lines.append(f"# {title}\n")
    if data.get("oneLiner"): lines.append(f"**一句话定位**：{data['oneLiner']}\n")
    if data.get("keyPoints"): lines.append("## 重点\n" + "\n".join(f"- {x}" for x in data["keyPoints"]) + "\n")
    if data.get("timeline"): lines.append("## 时间线\n" + "\n".join(f"- {x}" for x in data["timeline"]) + "\n")
    if data.get("productPrinciple"): lines.append(f"## 产品原理\n{data['productPrinciple']}\n")
    if data.get("sellingPoints"): lines.append("## 产品卖点\n" + "\n".join(f"- {x}" for x in data["sellingPoints"]) + "\n")
    if data.get("science"): lines.append(f"## 科学原理\n{data['science']}\n")
    if data.get("data"): lines.append("## 关键数据\n" + "\n".join(f"- {d.get('value')}（{d.get('baseline','')}，{d.get('plain','')}，出处 {d.get('cite','')}）" for d in data["data"]) + "\n")
    if data.get("pending"): lines.append("## 待确认\n" + "\n".join(f"- {x}" for x in data["pending"]) + "\n")
    if data.get("depth"): lines.append(f"**深度自评**：{data['depth']}\n")

    docx_path = os.path.join(base, "scientist-报告.docx")
    if "docx" in OK:
        doc = Document()
        doc.add_heading(title, 0)
        for seg in lines:
            doc.add_paragraph(seg)
        doc.save(docx_path)
        print(f"  docx -> {docx_path}")

    pptx_path = os.path.join(base, "scientist-讲解.pptx")
    if "pptx" in OK:
        prs = Presentation()
        s = prs.slides.add_slide(prs.slide_layouts[1])
        s.shapes.title.text = title
        if data.get("oneLiner"):
            s.placeholders[1].text = data["oneLiner"]
        blocks = [("重点", data.get("keyPoints")), ("时间线", data.get("timeline")),
                  ("产品原理", [data.get("productPrinciple")]), ("产品卖点", data.get("sellingPoints")),
                  ("科学原理", [data.get("science")])]
        for name, items in blocks:
            if not items:
                continue
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            slide.shapes.title.text = name
            body = "\n".join("- " + str(x) for x in items if x)
            slide.placeholders[1].text = body[:2000]
        prs.save(pptx_path)
        print(f"  pptx -> {pptx_path}")

    if "!docx" in OK or "!pptx" in OK:
        missing = [k for k in ("docx", "pptx") if "!" + k in OK]
        print(f"  缺库: {missing} -> pip install python-docx python-pptx，或交给 report-writer / ppt-master / markdown-exporter 技能")

if __name__ == "__main__":
    main()
