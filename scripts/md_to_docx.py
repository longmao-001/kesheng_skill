# -*- coding: utf-8 -*-
"""md -> docx 报告 转档工具（科生 M2 交付用）。
用法: python md_to_docx.py <report.md> <out.docx>
生成带标题/分节的 docx 报告。中文用思源黑体回退到系统中文字体名。
"""
import sys, re
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def load_blocks(path):
    with open(path, encoding='utf-8') as f:
        lines = f.read().split('\n')
    return lines

def build(lines, out):
    doc = Document()
    # 设置默认字体（中文）
    style = doc.styles['Normal']
    style.font.name = 'Microsoft YaHei'
    style._element.rPr.rFonts.set(
        '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia',
        'Microsoft YaHei')
    style.font.size = Pt(11)

    para_type = 'para'
    for ln in lines:
        s = ln.rstrip()
        if not s.strip():
            continue
        if s.startswith('# '):
            doc.add_heading(s[2:].strip(), level=0)
            continue
        if s.startswith('## '):
            doc.add_heading(s[3:].strip(), level=1)
            continue
        if s.startswith('### '):
            doc.add_heading(s[4:].strip(), level=2)
            continue
        m = re.match(r'^[-*]\s+(.*)$', s)
        if m:
            p = doc.add_paragraph(style='List Bullet')
            p.add_run(m.group(1).strip())
            continue
        m = re.match(r'^\d+[.)]\s+(.*)$', s)
        if m:
            p = doc.add_paragraph(style='List Number')
            p.add_run(m.group(1).strip())
            continue
        doc.add_paragraph(s)
    doc.save(out)
    print('saved:', out)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: python md_to_docx.py <report.md> <out.docx>')
        sys.exit(1)
    build(load_blocks(sys.argv[1]), sys.argv[2])
