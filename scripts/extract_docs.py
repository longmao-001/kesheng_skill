#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
素材文档批量提取 (extract_docs.py) —— PDF / PPTX / DOCX → 抠图 + 抽文 + 台账骨架

配套 SOP: docs/ASSET-TYPES.md（按文件类型的固定处理方案）+ playbooks/asset-library-flow.md
作用: 把客户给的 PDF/PPT/Word 里的**图片一次性抠出来**、**正文抽成带出处的抽取稿**、
      并生成 **assets-inventory 台账骨架**（待用 read_image 填三件套）。

用法:
  python -X utf8 scripts/extract_docs.py <输入文件或目录> --out <输出目录> [选项]

选项:
  --out DIR        输出目录（必填；建议 = runs/<项目slug>/）
  --subject NAME   主体名（用于台账"主体"列预填；默认取源文件名）
  --min-size N     最小边长(px)，小于此的图跳过（去图标/装饰线）；默认 120；0=不过滤
  --no-text        只抠图，不抽文
  --dry-run        只扫描报告，不写文件

产物（全部落在 <out>/ 下）:
  extracted-images/<源文件名>/p<页或slide>_<序号>.<ext>   抠出的图（按内容哈希去重）
  doc-extracts/<源文件名>.md                              抽文（按页/slide 分节，标出处）
  assets-inventory-抽图候选.md                            台账骨架（照 templates/assets-inventory.md §四）
  extract-report.md                                       本次提取报告（数量/跳过原因/异常）

铁则（见 docs/ASSET-TYPES.md）：① 抠出的图**必须再用 read_image 看真图**做多模态拆解，
不得凭文件名/页码判断内容 ② 数据图表只作 CT 内容参考、**永不出镜** ③ 客户敏感页不入库
④ 抠出的图默认只作"候选"，合规（水印/竞品/未授权）核查后才入库。
"""
import argparse
import hashlib
import io
import os
import sys
import zipfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

IMG_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".tif", ".tiff", ".emf", ".wmf", ".svg"}
DEFAULT_MIN = 120


def _rel(p):
    try:
        return os.path.relpath(p).replace("\\", "/")
    except ValueError:  # 跨盘符（如输出在 C:，cwd 在 F:）
        return os.path.abspath(p).replace("\\", "/")


def _sha(b):
    return hashlib.sha1(b).hexdigest()[:12]


def _safe(name):
    bad = '<>:"/\\|?*'
    out = "".join("_" if c in bad else c for c in name).strip()
    return out[:60] or "unnamed"


def _base_of(path):
    """源文件基名（含扩展名以避不同格式同名互撞，如 t.docx / t.pdf → t_docx / t_pdf）。"""
    stem, ext = os.path.splitext(os.path.basename(path))
    return _safe(stem) + "_" + (ext.lstrip(".").lower() or "file")


def _img_size(data):
    """返回 (w,h)；读不出返回 (0,0)（如 EMF/WMF）。"""
    try:
        from PIL import Image
        with Image.open(io.BytesIO(data)) as im:
            return im.size
    except Exception:  # noqa: BLE001
        return (0, 0)


def _save_image(blob, ext, out_dir, stem, seen, min_size, notes):
    """内容去重 + 尺寸过滤后落盘；返回落盘文件名 or None。"""
    h = _sha(blob)
    if h in seen:
        notes.append(("dup", stem, "内容重复，跳过"))
        return None
    w, hh = _img_size(blob)
    if min_size and w and hh and (w < min_size or hh < min_size):
        notes.append(("small", stem, f"{w}x{hh} < {min_size}，跳过"))
        return None
    seen.add(h)
    if not ext:
        ext = ".bin"
    ext = ext if ext.startswith(".") else "." + ext
    fn = f"{stem}_{h}{ext}"
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, fn), "wb") as f:
        f.write(blob)
    notes.append(("ok", stem, f"{w}x{hh}" if w else "尺寸未知"))
    return fn


# ---------------- PDF ----------------
def extract_pdf(path, out_root, min_size, want_text, notes, rows):
    try:
        import pymupdf as fitz  # 新版
    except Exception:  # noqa: BLE001
        try:
            import fitz  # 旧版
        except Exception as e:  # noqa: BLE001
            notes.append(("error", os.path.basename(path), f"PyMuPDF 不可用: {e}"))
            return 0, 0
    base = _base_of(path)
    img_dir = os.path.join(out_root, "extracted-images", base)
    n_img = 0
    seen = set()
    texts = []
    doc = fitz.open(path)
    for pno in range(len(doc)):
        page = doc[pno]
        # 图
        try:
            for i, info in enumerate(page.get_images(full=True), 1):
                xref = info[0]
                try:
                    d = doc.extract_image(xref)
                except Exception:  # noqa: BLE001
                    continue
                fn = _save_image(d.get("image") or b"", d.get("ext") or "", img_dir,
                                 f"p{pno + 1:03d}_{i:02d}", seen, min_size, notes)
                if fn:
                    n_img += 1
                    rows.append({
                        "file": f"extracted-images/{base}/{fn}",
                        "src": f"{os.path.basename(path)} p{pno + 1}",
                        "w": "", "subject": base,
                    })
        except Exception as e:  # noqa: BLE001
            notes.append(("warn", f"{base} p{pno + 1}", f"取图失败: {e}"))
        # 文
        if want_text:
            try:
                t = page.get_text() or ""
                if t.strip():
                    texts.append(f"\n### p{pno + 1}\n\n{t.strip()}\n")
            except Exception:  # noqa: BLE001
                pass
    if want_text and texts:
        d = os.path.join(out_root, "doc-extracts")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, f"{base}.md"), "w", encoding="utf-8") as f:
            f.write(f"# 抽取稿 · {os.path.basename(path)}\n\n> 来源: `{_rel(path)}`（PyMuPDF 抽取；页码=出处）\n")
            f.write("".join(texts))
    doc.close()
    return n_img, len(texts)


# ---------------- PPTX ----------------
def extract_pptx(path, out_root, min_size, want_text, notes, rows):
    try:
        from pptx import Presentation
        from pptx.enum.shapes import MSO_SHAPE_TYPE
    except Exception as e:  # noqa: BLE001
        notes.append(("error", os.path.basename(path), f"python-pptx 不可用: {e}"))
        return 0, 0
    base = _base_of(path)
    img_dir = os.path.join(out_root, "extracted-images", base)
    n_img = 0
    seen = set()
    texts = []
    prs = Presentation(path)

    def walk(shapes, sn):
        nonlocal n_img
        for sh in shapes:
            try:
                if sh.shape_type == MSO_SHAPE_TYPE.GROUP:
                    walk(sh.shapes, sn)
                    continue
            except Exception:  # noqa: BLE001
                pass
            # 图片
            try:
                if sh.shape_type == MSO_SHAPE_TYPE.PICTURE:
                    img = sh.image
                    fn = _save_image(img.blob, os.path.splitext(img.filename or "")[1],
                                     img_dir, f"s{sn:03d}_{len(seen) + 1:02d}", seen, min_size, notes)
                    if fn:
                        n_img += 1
                        rows.append({"file": f"extracted-images/{base}/{fn}",
                                     "src": f"{os.path.basename(path)} slide{sn}",
                                     "w": "", "subject": base})
                    continue
            except Exception:  # noqa: BLE001
                pass
            # 表格
            try:
                if getattr(sh, "has_table", False) and sh.has_table:
                    tb = []
                    for r in sh.table.rows:
                        tb.append(" | ".join(c.text.strip() for c in r.cells))
                    if tb:
                        texts.append(f"\n[表格 slide{sn}]\n" + "\n".join(tb) + "\n")
                    continue
            except Exception:  # noqa: BLE001
                pass
            # 文本
            try:
                if sh.has_text_frame and sh.text_frame.text.strip():
                    texts.append(sh.text_frame.text.strip())
            except Exception:  # noqa: BLE001
                pass

    for sn, slide in enumerate(prs.slides, 1):
        before = len(texts)
        walk(slide.shapes, sn)
        # 备注（演讲者备注常含事实/口径）
        try:
            if slide.has_notes_slide and slide.notes_slide.notes_text_frame.text.strip():
                texts.append(f"[备注 slide{sn}] " + slide.notes_slide.notes_text_frame.text.strip())
        except Exception:  # noqa: BLE001
            pass
        if want_text and len(texts) > before:
            pass
    if want_text and texts:
        d = os.path.join(out_root, "doc-extracts")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, f"{base}.md"), "w", encoding="utf-8") as f:
            f.write(f"# 抽取稿 · {os.path.basename(path)}\n\n> 来源: `{_rel(path)}`（python-pptx 抽取；slide 号=出处）\n")
            f.write("\n\n".join(texts) + "\n")
    return n_img, len(texts)


# ---------------- DOCX ----------------
def extract_docx(path, out_root, min_size, want_text, notes, rows):
    try:
        import docx
    except Exception as e:  # noqa: BLE001
        notes.append(("error", os.path.basename(path), f"python-docx 不可用: {e}"))
        return 0, 0
    base = _base_of(path)
    img_dir = os.path.join(out_root, "extracted-images", base)
    n_img = 0
    seen = set()
    texts = []
    d = docx.Document(path)
    # 内嵌图：走关系部件（最稳，避免 graphicData 私有 API）
    try:
        for rid, rel in d.part.rels.items():
            try:
                if "image" not in rel.reltype:
                    continue
                blob = rel.target_part.blob
                ext = os.path.splitext(rel.target_ref or "")[1]
                fn = _save_image(blob, ext, img_dir, f"img_{n_img + 1:02d}", seen, min_size, notes)
                if fn:
                    n_img += 1
                    rows.append({"file": f"extracted-images/{base}/{fn}",
                                 "src": f"{os.path.basename(path)} (内嵌图)",
                                 "w": "", "subject": base})
            except Exception:  # noqa: BLE001
                continue
    except Exception as e:  # noqa: BLE001
        notes.append(("warn", base, f"取内嵌图失败: {e}"))
    # 文 + 表
    if want_text:
        try:
            for p in d.paragraphs:
                if p.text.strip():
                    texts.append(p.text.strip())
            for ti, tb in enumerate(d.tables, 1):
                rows_t = [" | ".join(c.text.strip() for c in r.cells) for r in tb.rows]
                if rows_t:
                    texts.append(f"\n[表格 {ti}]\n" + "\n".join(rows_t) + "\n")
        except Exception as e:  # noqa: BLE001
            notes.append(("warn", base, f"抽文失败: {e}"))
    if texts:
        dd = os.path.join(out_root, "doc-extracts")
        os.makedirs(dd, exist_ok=True)
        with open(os.path.join(dd, f"{base}.md"), "w", encoding="utf-8") as f:
            f.write(f"# 抽取稿 · {os.path.basename(path)}\n\n> 来源: `{_rel(path)}`（python-docx 抽取）\n\n")
            f.write("\n".join(texts) + "\n")
    return n_img, len(texts)


def write_inventory_skeleton(out_root, subject, rows):
    """生成台账骨架（照 templates/assets-inventory.md §四 列）。"""
    p = os.path.join(out_root, "assets-inventory-抽图候选.md")
    with open(p, "w", encoding="utf-8") as f:
        f.write("# 素材库 · 抽图候选台账（骨架）\n\n")
        f.write("> ⚠️ 由 `scripts/extract_docs.py` 自动生成：**只有图 + 出处**；"
                "必须逐张 `read_image` 看真图填「用途分级/内容类型/内容标签/反推AI提示词/质量分」，"
                "合规核查（水印/竞品/未授权）后才入正式 `assets-inventory.md`（见 `docs/ASSET-TYPES.md`）。\n")
        f.write("> 决策树：能入镜=IN／做锚=RF／只作内容依据=CT（数据图表永不出镜）。\n\n")
        f.write("| 抽图文件 | 来源·出处 | 用途分级 | 内容类型 | 主体 | 视角·部位 | 内容标签(物品/任务/场景/结构/质感/数据/品牌/实拍) | AI合成反推prompt | 质量分(★) | 备注 |\n")
        f.write("|---|---|---|---|---|---|---|---|---|---|\n")
        for r in rows:
            f.write(f"| `{r['file']}` | {r['src']} | 待填 | 待填 | {subject} | 待填 | 待填 | 待填 | 待填 | 待填 |\n")
    return p


def main():
    ap = argparse.ArgumentParser(description="PDF/PPTX/DOCX → 抠图 + 抽文 + 台账骨架")
    ap.add_argument("input", help="输入文件或目录")
    ap.add_argument("--out", required=True, help="输出目录（建议 runs/<项目slug>/）")
    ap.add_argument("--subject", default="", help="主体名（台账预填；默认取源文件名）")
    ap.add_argument("--min-size", type=int, default=DEFAULT_MIN, help=f"最小边长px，默认 {DEFAULT_MIN}；0=不过滤")
    ap.add_argument("--no-text", action="store_true", help="只抠图不抽文")
    ap.add_argument("--dry-run", action="store_true", help="只扫描不写文件")
    a = ap.parse_args()

    src = a.input
    if not os.path.exists(src):
        print(f"输入不存在: {src}"); sys.exit(2)
    files = []
    if os.path.isfile(src):
        files = [src]
    else:
        for root, _d, fs in os.walk(src):
            for f in fs:
                if os.path.splitext(f)[1].lower() in (".pdf", ".pptx", ".docx"):
                    files.append(os.path.join(root, f))
    files.sort()
    if not files:
        print("未找到 .pdf / .pptx / .docx 文件"); sys.exit(0)

    out_root = a.out
    if not a.dry_run:
        os.makedirs(out_root, exist_ok=True)
    notes, rows = [], []
    tot_img = 0
    print(f"== extract_docs: {len(files)} 个文件 → {out_root} ==")
    for p in files:
        ext = os.path.splitext(p)[1].lower()
        base = _base_of(p)
        if a.dry_run:
            print(f"  [dry] {os.path.basename(p)} ({ext})")
            continue
        if ext == ".pdf":
            ni, nt = extract_pdf(p, out_root, a.min_size, not a.no_text, notes, rows)
        elif ext == ".pptx":
            ni, nt = extract_pptx(p, out_root, a.min_size, not a.no_text, notes, rows)
        elif ext == ".docx":
            ni, nt = extract_docx(p, out_root, a.min_size, not a.no_text, notes, rows)
        else:
            continue
        tot_img += ni
        # 主体回填：默认取源文件名（不含扩展名），--subject 给定则统一替换
        for r in rows:
            if r["subject"] == base:
                r["subject"] = a.subject or os.path.splitext(os.path.basename(p))[0]
        print(f"  {os.path.basename(p)}: 抠图 {ni} 张" + (f" / 抽文 {nt} 段" if not a.no_text else ""))

    if a.dry_run:
        print("（dry-run：未写任何文件）"); return

    inv = write_inventory_skeleton(out_root, a.subject or "（待填）", rows) if rows else None
    # 报告
    rp = os.path.join(out_root, "extract-report.md")
    with open(rp, "w", encoding="utf-8") as f:
        f.write("# 提取报告（extract_docs.py）\n\n")
        f.write(f"- 输入: `{_rel(src)}`\n- 文件数: {len(files)}\n- 抠图总数: {tot_img}\n")
        f.write(f"- 最小边长过滤: {a.min_size}px\n- 输出: `extracted-images/` + `doc-extracts/`"
                + (f" + `{os.path.basename(inv)}`" if inv else "") + "\n\n")
        f.write("## 明细\n\n")
        for kind, stem, msg in notes:
            f.write(f"- [{kind}] {stem}: {msg}\n")
        f.write("\n> 下一步（见 `docs/ASSET-TYPES.md`）：逐张 `read_image` 看真图 → 填三件套 → 合规核查 → 入 `assets-inventory.md`。\n")
    print(f"\n完成：抠图 {tot_img} 张")
    if inv:
        print(f"  台账骨架: {_rel(inv)}")
    print(f"  报告: {_rel(rp)}")
    print("  ⚠️ 下一步必须逐张 read_image 看真图填三件套（不凭文件名判断）")


if __name__ == "__main__":
    main()
