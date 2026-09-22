#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科生·素材索引器 (asset_index.py) —— 「入库即标签」的索引与溯源核心

一句话：扫一遍素材根目录 → 给每个媒体文件生成/更新 sidecar 标签 `<file>.label.json`
        → 汇总成全库索引 `assets_index.json`（机器）+ `assets_index.md`（人读）
        → 从项目 prompt 文件里把「采纳版 prompt 全文」按 素材ID/文件名/关键词 对上
        → 对不上的标 `trace_status=缺口` 并写 `asset_gaps.md`（待补清单）
        → 与磁盘双向核对：盘上有而索引无＝未登记；索引有而盘上无＝断链。

用法:
  python scripts/asset_index.py --root <素材根> [--out <索引输出目录>]
        [--prompt-source a.md b.md ...] [--include "*.png,*.jpg"] [--exclude-dir _废片,_旧版归档]
        [--ep-tag EP01] [--config asset_index.config.json] [--check] [--no-sidecar] [--quiet]

匹配策略（三级＋全局占用，宁可报缺口也不乱配）:
  ① 强档：块上下文里出现**完整文件名**（含扩展名，或仅扩展名不符）→ high
  ② 中档：块上下文里出现**素材ID**（如 C11/C1a）且该块标题未指向同族另一件 → high
  ③ 弱档：块上下文里**分词命中 ≥2 个**且覆盖率 ≥50%（如 巨石+三视图）→ low（须人工确认）
  同一代码块只能被一件素材占用（先强后弱），避免"参考字段提到别人名字"被误当来源。

设计约束:
  - 纯标准库（hashlib/json/argparse/os/re）；读图尺寸优先 Pillow，无 Pillow 则 dims 留空并注明。
  - 通用：不写死任何项目名/角色名/目录名——目录映射、命名前缀、排除目录全部可配置。
  - sidecar 是「素材自己的标签」，索引是「全库汇总」；索引可随时重建，sidecar 里 agent 填的
    vision 块与人工写过的 prompt 不会被空值覆盖（见 merge_record）；**merge 不清空未知键**——
    schema 外的自定义键（如视频类备注 `vision_note`）在刷新 sidecar 时原样保留。

配套: scripts/asset_schema.md（规范）· scripts/ingest_asset.py（入库）· scripts/check_asset_labels.py（门控）
"""
from __future__ import annotations

import argparse
import datetime
import fnmatch
import hashlib
import io
import json
import os
import re
import sys

# 控制台按 UTF-8 输出（用 reconfigure 而非重包 buffer：被 import 时不会踩 TextIOWrapper 关闭坑）
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

# ---------------------------------------------------------------- 常量与默认值

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff", ".heic", ".avif"}
VIDEO_EXT = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".flv", ".wmv"}
AUDIO_EXT = {".wav", ".mp3", ".flac", ".aac", ".m4a", ".ogg"}
MEDIA_EXT = IMAGE_EXT | VIDEO_EXT | AUDIO_EXT

SIDECAR_SUFFIX = ".label.json"
INDEX_JSON = "assets_index.json"
INDEX_MD = "assets_index.md"
GAPS_MD = "asset_gaps.md"
CONFIG_NAME = "asset_index.config.json"

# 排除目录默认值（下划线前缀的归档目录不参与索引，但会在报告里列出「已排除 N 件」）
DEFAULT_EXCLUDE_DIRS = [
    "_废片", "_旧版归档", "_作废归档", "_归档", "_frames", "_trash", "_tmp", "_temp",
    ".git", ".svn", "__pycache__", "node_modules", ".idea", ".vscode",
]
DEFAULT_INCLUDE = [
    "*.png", "*.jpg", "*.jpeg", "*.webp", "*.gif", "*.bmp", "*.tif", "*.tiff",
    "*.mp4", "*.mov", "*.avi", "*.mkv", "*.webm", "*.m4v",
]

# 排除目录口径（写死，20260921 门控裁定）：随 assets_index.md 一起生成，可由 config.index_meta 覆盖
EXCLUDED_DIRS_POLICY = (
    "`_废片`/`_旧版归档`/`_作废归档`/`_frames` 为**设计性排除目录**："
    "不计件、不计 orphan、不进索引；判废原因记录在各目录 README 或主表 `rejects` 栏。"
    "（故归档件无 sidecar 属正常形态，不得据此补件或补计数。）"
)

# 刷新纪律（并发安全，写死）：随 assets_index.md 一起生成，可由 config.index_meta 覆盖
REFRESH_DISCIPLINE = (
    "**只刷索引一律 `asset_index.py --no-sidecar`**（不改写任何 sidecar）；"
    "`ingest_asset.py` 就地登记**默认不回写全量 sidecar**（只写本件；要连全库一起回写须显式 `--write-sidecars`）；"
    "`trace_status`／`rejects` 具**「人写值粘滞」**（`trace_source`/`rejects_source=human` 时机器不得改，"
    "禁伪造逐字、禁静默改弱）；体检字段级差异用 `asset_index.py --audit-sidecars`。"
)

# 素材类型（sidecar.type）四选一
TYPES = ["用户输入", "模型生成", "图生图派生", "剪辑产物"]
# 溯源三档（sidecar.trace_status）—— 中文为准，同时兼容英文别名（verbatim/reconstructed/missing）
# N/A ＝ 不适用（**废片/归档件不判溯源档**：废片一律 N/A＋rejects 记原因＋note 记采纳版）
TRACES = ["逐字", "重构", "缺口", "N/A"]
TRACE_ALIASES = {
    "verbatim": "逐字", "逐字": "逐字", "exact": "逐字",
    "reconstructed": "重构", "重构": "重构", "rebuild": "重构",
    "missing": "缺口", "gap": "缺口", "label_gap": "缺口", "缺口": "缺口",
    "n/a": "N/A", "na": "N/A", "n.a.": "N/A", "不适用": "N/A", "废片": "N/A",
}


def norm_trace(v) -> str:
    """把中/英两种写法都归一到三档中文值（读旧 sidecar / 索引时用）。"""
    s = (v or "").strip()
    return TRACE_ALIASES.get(s.lower(), s)

# 类型前缀 ↔ 素材类别（命名规范 <前缀>-<ID>-<名称>-<版本>）
KIND_PREFIX = {"角色": "C", "道具": "Y", "场景": "S", "字帖": "Z", "故事板": "B", "成片": "F"}
PREFIX_KIND = {v: k for k, v in KIND_PREFIX.items()}
KIND_DIR = {k: k for k in KIND_PREFIX}          # 类别 → 默认子目录（可被 config 覆盖）
KIND_DIR_ALIAS = {                              # 目录名 → 类别（从路径反推，含常见别名）
    "角色": "角色", "人物": "角色", "character": "角色", "char": "角色",
    "道具": "道具", "prop": "道具", "props": "道具",
    "场景": "场景", "scene": "场景", "scenes": "场景", "背景": "场景",
    "字帖": "字帖", "文字": "字帖", "书法": "字帖", "glyph": "字帖",
    "故事板": "故事板", "board": "故事板", "分镜": "故事板", "storyboard": "故事板",
    "成片": "成片", "final": "成片", "输出": "成片", "output": "成片",
}

VERSION_RE = re.compile(r"^(?:[vV]\d+(?:\.\d+)*|第\s*[0-9０-９]+\s*(?:抽|版|次|稿)|抽\s*[0-9０-９]+)$")
ID_RE = re.compile(r"^[0-9０-９]{1,3}[a-z]?$")

SOURCE_MARK = ("保存文件名", "资产文件名", "文件名", "保存为", "save as")
# 溯源三档判据（顺序敏感：先缺口，再重构，否则逐字）
GAP_RE = re.compile(r"⛔[^\n]{0,30}缺口|缺口\s*——|采纳版全文\s*不可复现|不可复现|无要点可复原|全文\s*未落盘")
REBUILD_RE = re.compile(r"重构|复原|候选全文|非逐字")
VERBATIM_RE = re.compile(r"祖本|逐字照录|逐字复制|逐字原文")
# 「像不像一段 prompt」——用于剔除误配的散段（判废要点/说明文字）
PROMPT_HINT_RE = re.compile(
    r"中式水墨|水墨动画|生成一张|生成一段|白底焦墨|黑白线稿|书法字帖|参考图|"
    r"【风格】|【画面】|【规格|【参考】|宣纸暖白底|2K分辨率|负面词|【负面】")
# 废片判据（可被 config.scrap_markers 追加）：(正则, 允许的最大字距)
# 判据只在「点名本件」的行里生效，且判据里若写了抽次必须与本件抽次一致。
SCRAP_RES = [
    (re.compile(r"[❌⛔🗄]\s*[^\n]{0,16}判废"), 60),
    (re.compile(r"废片留档"), 40),
    (re.compile(r"废\s*/\s*归档"), 30),
]

TOOL_HINTS = [
    ("Seedance", "Seedance（字节）"), ("即梦", "即梦 Jimeng"), ("Jimeng", "即梦 Jimeng"),
    ("可灵", "可灵 Kling"), ("Kling", "可灵 Kling"), ("Vidu", "Vidu"),
    ("海螺", "海螺 Hailuo"), ("Hailuo", "海螺 Hailuo"), ("LibTV", "LibTV 节点画布"),
    ("Runway", "Runway"), ("万相", "通义万相"),
    ("Image2", "GPT Image 2（Image2）"), ("GPT Image", "GPT Image 2（Image2）"),
    ("Midjourney", "Midjourney"), ("SDXL", "Stable Diffusion"), ("ComfyUI", "ComfyUI"),
    ("ffmpeg", "ffmpeg（剪辑合成）"), ("剪映", "剪映"),
]

SHOT_RE = re.compile(r"(?<![\d\-])(\d{1,2}-\d{2})(?![\d\-])")
SEG_RE = re.compile(r"(?<![A-Za-z0-9\-])([A-Z]-\d{2})(?![0-9])")
SCENE_RE = re.compile(r"场\s*([0-9]{1,2})")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})\s*([^\s`]*)")
HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.*)$")
REF_RE = re.compile(r"@(?:图片|图|视频|音频|素材)\s*([0-9]{1,2})\s*[=＝]\s*([^\s，,；;、）)】\]]+)")
UPLOAD_RE = re.compile(r"上传顺序\s*[：:]\s*([^\n]+)")
NEG_RE = re.compile(r"^\s*(?:【负面】|负面词|负面)\s*[（(]?[^：:）)]{0,20}[）)]?\s*[：:]?\s*(.*)$")
BORROW_RE = re.compile(r"(?:同|见|＝|=|即)\s*第\s*(\d+)\s*条")


# ---------------------------------------------------------------- 小工具

def now_str() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def read_text(path: str) -> str:
    with io.open(path, "r", encoding="utf-8-sig", errors="ignore") as fh:
        return fh.read()


def write_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def write_json(path: str, obj) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def sha256_file(path: str, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def read_dims(path: str):
    """图片尺寸：优先 Pillow；无 Pillow / 非图片 / 视频 → (None, 说明)。"""
    ext = os.path.splitext(path)[1].lower()
    if ext in VIDEO_EXT:
        return None, "视频未读尺寸（需 ffprobe；本工具只用标准库+Pillow）"
    if ext in AUDIO_EXT:
        return None, "音频无尺寸字段"
    try:
        from PIL import Image  # type: ignore
    except Exception:  # noqa: BLE001
        return None, "未安装 Pillow，dims 跳过（pip install Pillow 后自动补）"
    try:
        with Image.open(path) as im:
            w, h = im.size
            fmt = im.format or ""
        return [int(w), int(h)], f"{fmt} {w}x{h}"
    except Exception as e:  # noqa: BLE001
        return None, f"读图失败：{e}"


def norm_rel(path: str, root: str) -> str:
    return os.path.relpath(path, root).replace("\\", "/")


def media_kind_of(ext: str) -> str:
    if ext in IMAGE_EXT:
        return "image"
    if ext in VIDEO_EXT:
        return "video"
    if ext in AUDIO_EXT:
        return "audio"
    return "other"


def _cell_around(line: str, pos: int) -> str:
    """取 pos 所在的表格单元格（无 `|` 时取左右各 40 字）。"""
    if "|" not in line:
        return line[max(0, pos - 40): pos + 40]
    lo = line.rfind("|", 0, pos)
    hi = line.find("|", pos)
    lo = 0 if lo < 0 else lo + 1
    hi = len(line) if hi < 0 else hi
    return line[lo:hi]


def _looks_like_prompt(text: str) -> bool:
    """一段文字像不像出图 prompt（用于剔除判废要点/说明段落被误当 prompt）。"""
    t = (text or "").strip()
    if len(t) < 40:
        return False
    first = next((ln.strip() for ln in t.splitlines() if ln.strip()), "")
    if first.startswith((">", "- **", "* **", "**", "|")):
        return False
    return bool(PROMPT_HINT_RE.search(t))


def key_hit(text: str, key: str) -> bool:
    if not key:
        return False
    for m in re.finditer(re.escape(key), text):
        before = text[m.start() - 1] if m.start() else ""
        after = text[m.end()] if m.end() < len(text) else ""
        if before and before.isascii() and (before.isalnum() or before in "-_"):
            continue
        if after and after.isascii() and (after.isalnum() or after in "-_"):
            continue
        return True
    return False


# ---------------------------------------------------------------- 命名的解析与校验

def kind_of_rel(rel: str) -> str:
    for seg in reversed(rel.split("/")[:-1]):
        if seg in KIND_DIR_ALIAS:
            return KIND_DIR_ALIAS[seg]
    return ""


def parse_name(stem: str, version_words=()):
    """解析 `前缀+ID-名称-版本`（如 C11-封肃-主版-v1 / S1-青埂峰-阵末空缺-第2抽）。

    返回 (info, error)；error 非空＝不合规。
    """
    segs = stem.split("-")
    if len(segs) < 3:
        return None, "分段不足 3 段（须 <前缀><ID>-<名称>-<版本或抽次>，如 C11-封肃-主版-v1）"
    m = re.match(r"^([A-Za-z]{1,2})([0-9０-９]{1,3}[a-z]?)$", segs[0])
    if not m:
        return None, f"首段「{segs[0]}」不合规（须 <类型前缀><ID>，如 C11 / S1 / Y2）"
    prefix, aid = m.group(1).upper(), m.group(2)
    if prefix not in PREFIX_KIND:
        return None, f"类型前缀「{prefix}」不在规范表（{'/'.join(sorted(PREFIX_KIND))}）"
    name = "-".join(segs[1:-1])
    version = segs[-1]
    if not name.strip():
        return None, "名称段为空"
    if any(ch in name for ch in " \t.。，,、/\\"):
        return None, f"名称段「{name}」含空格/标点/点号"
    if not (VERSION_RE.match(version) or version in set(version_words)):
        extra = ("；已配置版本白名单：" + "/".join(version_words)) if version_words else ""
        return None, f"版本/抽次段「{version}」不合规（须 v1 / 第1抽 / 第3版 之类）{extra}"
    return {"prefix": prefix, "id": aid, "name": name, "version": version,
            "kind": PREFIX_KIND.get(prefix, "")}, ""


def suggest_name(stem: str, ext: str, kind: str, seq: int = 1) -> str:
    """给不合规文件名一个改名建议（不保证唯一，仅作提示）。"""
    segs = stem.split("-")
    prefix = KIND_PREFIX.get(kind, "X")
    m = re.match(r"^([A-Za-z]{1,2})([0-9０-９]{1,3}[a-z]?)$", segs[0]) if segs else None
    aid = m.group(2) if m else (segs[1] if len(segs) > 2 and ID_RE.match(segs[1]) else f"{seq:02d}")
    version = segs[-1] if segs and VERSION_RE.match(segs[-1]) else "v1"
    tail = list(segs[1:])
    if tail and tail[-1] == version:
        tail = tail[:-1]
    if not tail:
        tail = [segs[0]]
    name = "-".join(t for t in tail if not ID_RE.match(t))[:40].strip("-") or segs[0]
    return f"{prefix}{aid}-{name}-{version}{ext.lower()}"


def check_naming(rel: str, version_words=()) -> dict:
    """命名规范校验（索引器与门控共用）。"""
    base = os.path.basename(rel)
    stem, ext = os.path.splitext(base)
    out = {"ok": True, "error": "", "suggest": "", "prefix": "", "id": "", "name": "",
           "version": "", "kind": kind_of_rel(rel), "id_token": ""}
    if ext != ext.lower():
        out.update(ok=False, error=f"扩展名须小写（当前「{ext}」）")
    info, err = parse_name(stem, version_words)
    if err:
        out.update(ok=False, error=err, suggest=suggest_name(stem, ext, out["kind"] or "角色", 1))
        return out
    out.update(prefix=info["prefix"], id=info["id"], name=info["name"],
               version=info["version"], id_token=f"{info['prefix']}{info['id']}")
    if out["kind"] and info["kind"] and out["kind"] != info["kind"]:
        out.update(ok=False, error=f"前缀「{info['prefix']}」= {info['kind']}，但所在目录是 {out['kind']}",
                   suggest=f"{KIND_PREFIX[out['kind']]}{info['id']}-{info['name']}-{info['version']}{ext}")
    if not out["ok"] and not out["suggest"]:
        out["suggest"] = suggest_name(stem, ext, out["kind"] or info["kind"], 1)
    return out


# ---------------------------------------------------------------- prompt 源语料（章节 + 代码块）

class Block:
    """候选 prompt 块：章内一个 ``` 代码块 + 它自己的局部上下文（上一块之后 → 围栏）。"""

    __slots__ = ("doc", "open_line", "close_line", "body", "context", "section", "unclosed")

    def __init__(self, doc, open_line, close_line, body, context, section, unclosed=False):
        self.doc = doc
        self.open_line = open_line
        self.close_line = close_line
        self.body = body
        self.context = context            # 上一块结束（或章节标题）→ 本围栏之前 的全部行
        self.section = section            # 所属 Section
        self.unclosed = unclosed

    @property
    def key(self):
        return (self.doc, self.open_line)


class Section:
    """源文件里的一个 md 章节（按标题切分）——用于读溯源标记、判废、条目互引。"""

    __slots__ = ("doc", "num", "heading", "line", "lines", "blocks")

    def __init__(self, doc, num, heading, line):
        self.doc = doc
        self.num = num
        self.heading = heading
        self.line = line
        self.lines = []
        self.blocks = []          # 围栏块（未校验；取值时筛）

    @property
    def text(self):
        return "\n".join(self.lines)

    def _region(self):
        """无围栏/围栏残缺时的兜底：从「采纳版 prompt 全文」等标记行起，取到下一个元信息行为止。"""
        start = None
        for i, ln in enumerate(self.lines):
            if re.search(r"(?:采纳版|平台)\s*prompt\s*全文|prompt\s*全文|可直接粘贴|采纳版原文", ln):
                start = i + 1
                break
        if start is None:
            return None
        out, blanks = [], 0
        for j in range(start, len(self.lines)):
            t = self.lines[j].strip()
            if t.startswith("```") or t.startswith("~~~"):
                continue
            if not t:
                blanks += 1
                if out and blanks >= 1:
                    break
                continue
            if out and (t.startswith((">", "#", "---")) or t.startswith("- **") or t.startswith("* **")):
                break
            blanks = 0
            out.append(self.lines[j])
        txt = "\n".join(out).strip()
        if not _looks_like_prompt(txt):
            return None
        ctx = "\n".join(self.lines[:start + 1])
        return Block(self.doc, self.line + start + 1, self.line + start + len(out), txt, ctx, self)

    def candidates(self):
        """本节的候选 prompt 块（围栏块 + 兜底区域），已按「像不像 prompt」筛过。"""
        out = [b for b in self.blocks if _looks_like_prompt(b.body)]
        r = self._region()
        if r is not None:
            out.append(r)
        return out

    def best_block(self):
        cands = self.candidates()
        return max(cands, key=lambda b: len(b.body)) if cands else None


class PromptCorpus:
    """把若干项目 md 读成「章节 + 代码块」，供按 文件名/ID/分词 三级匹配（含全局占用）。"""

    def __init__(self, paths):
        self.paths = [p for p in paths if p and os.path.exists(p)]
        self.sections = []
        self.lines = []                 # [(basename, lineno, line)]：用于复用/判废线索抽取
        for p in self.paths:
            text = read_text(p)
            lines = text.splitlines()
            self.lines.extend((os.path.basename(p), i + 1, ln) for i, ln in enumerate(lines))
            self.sections.extend(self._scan(p, lines))
        self.by_num = {}
        for s in self.sections:
            if s.num is not None and s.num not in self.by_num:
                self.by_num[s.num] = s
        self.line_occ = None            # [(stem,start,end)] 与 self.lines 平行，resolve() 时建

    # ---------- 解析 ----------
    @staticmethod
    def _scan(path, lines):
        sections, cur = [], None
        for i, ln in enumerate(lines):
            h = HEADING_RE.match(ln)
            if h:
                title = h.group(2).strip()
                m = re.match(r"^(\d+)\s*[·.、]", title) or re.match(r"^新增-(\d+)", title)
                num = int(m.group(1)) if m else None
                cur = Section(path, num, title, i)
                sections.append(cur)
            elif cur is None:
                cur = Section(path, None, "", 0)
                sections.append(cur)
            cur.lines.append(ln)
        # 章内配对围栏（未闭合的块＝到章末）
        for s in sections:
            open_idx = None
            body = []
            for i, ln in enumerate(s.lines):
                if FENCE_RE.match(ln):
                    if open_idx is None:
                        open_idx, body = i, []
                    else:
                        if len("\n".join(body).strip()) >= 20:
                            b = Block(path, s.line + open_idx + 1, s.line + i + 1,
                                      "\n".join(body), "", s)
                            s.blocks.append(b)
                        open_idx, body = None, []
                elif open_idx is not None:
                    body.append(ln)
            if open_idx is not None and len("\n".join(body).strip()) >= 20:
                s.blocks.append(Block(path, s.line + open_idx + 1, s.line + len(s.lines),
                                      "\n".join(body), "", s, unclosed=True))
        # 回填每个块的局部上下文（章节标题 + 上一块之后 → 本围栏）
        for s in sections:
            head_txt = s.lines[0] if s.lines else ""
            prev_end = 0
            for b in s.blocks:
                start = prev_end
                rel_open = b.open_line - s.line - 1
                b.context = head_txt + "\n" + "\n".join(s.lines[start:rel_open + 1])
                b.section = s
                prev_end = b.close_line - s.line
        return sections

    # ---------- 位置权重 ----------
    @staticmethod
    def _weight(context: str, key: str):
        """8=标题行；5=「保存文件名/资产文件名」行；3=其它上下文行；None=未命中。"""
        if not key:
            return None
        best = None
        for ln in context.splitlines():
            if not key_hit(ln, key):
                continue
            stripped = ln.lstrip()
            if stripped.startswith("#"):
                w = 8
            elif any(k in ln for k in SOURCE_MARK):
                w = 5
            else:
                w = 3
            if best is None or w > best:
                best = w
        return best

    @staticmethod
    def _heading_has_other_family(heading: str, id_token: str, own_stem: str, all_stems) -> bool:
        """标题里出现「同 ID 家族但本库确有另一件」的文件名 → 该块不属本件（防 C5-睫部 vs C5-主锚 串档）。"""
        if not id_token:
            return False
        for m in re.finditer(re.escape(id_token) + r"-[^\s（()），,、/|`*]+", heading):
            stem = os.path.splitext(m.group(0).strip("`*"))[0]
            if stem == own_stem:
                continue
            if stem in all_stems:          # 是本库真实存在的同族另一件
                return True
        return False

    # ---------- 全局匹配 ----------
    def _build_line_index(self, assets):
        """为每行预计算「本库素材名」的出现位置，供判废归属消歧（只用本库真名，防误挂）。"""
        stems = sorted({a["stem"] for a in assets}, key=len, reverse=True)
        idx = []
        for _doc, _n, ln in self.lines:
            occ = []
            for st in stems:
                for m in re.finditer(re.escape(st), ln):
                    b = ln[m.start() - 1] if m.start() else ""
                    a2 = ln[m.end()] if m.end() < len(ln) else ""
                    if b and b.isascii() and (b.isalnum() or b in "-_"):
                        continue
                    if a2 and a2.isascii() and (a2.isalnum() or a2 in "-_"):
                        continue
                    occ.append((st, m.start(), m.end()))
            idx.append(occ)
        self.line_occ = idx

    def resolve(self, assets, scrap_res=()):
        """assets: [{'rel','file','stem','id_token','tokens','keys','own_stems'}] → {rel: match_dict}

        分两轮占用代码块：先强档（标题/文件名行命中 文件名 或 ID），再弱档（分词命中）。
        一个块只能被一件素材占用——避免「参考字段提到别人名字」被当成来源。
        """
        claimed = {}          # (doc, open_line) → rel
        out = {}
        strong, weak = [], []
        self._build_line_index(assets)
        for a in assets:
            for s in self.sections:
                for blk in s.candidates():
                    for key, method, bonus in a["keys"]:
                        w = self._weight(blk.context, key)
                        if w is None:
                            continue
                        if method == "id":
                            if w < 5:
                                continue
                            if self._heading_has_other_family(s.heading, a["id_token"], a["stem"], a["own_stems"]):
                                continue
                        score = len(key) * 10 + bonus + w + (50 if key == a["file"] else 0) \
                            + (100 if w == 8 else 0)
                        cand = {"score": score, "rel": a["rel"], "sec": s, "blk": blk,
                                "key": key, "method": method, "w": w, "a": a}
                        # 强档要求命中位置是标题行(8)或「保存文件名/资产文件名」行(5)；
                        # 只在正文里被提一句(w=3)的降级到弱档，避免抢走别人真正的块
                        (strong if w >= 5 else weak).append(cand)
            tokens = a["tokens"]
            if len(tokens) >= 2:
                for s in self.sections:
                    for blk in s.candidates():
                        lines = blk.context.splitlines()
                        hit = [t for t in tokens if key_hit(blk.context, t)]
                        longest = max((len(t) for t in hit), default=0)
                        ok = (len(hit) >= 2 or longest >= 4) and len(hit) / len(tokens) >= 0.5
                        if ok and hit:
                            # 命中词离围栏越近越可信（防「章节导语里提了一句」被当成该块的标题）
                            last = max((i for i, l in enumerate(lines)
                                        if any(key_hit(l, t) for t in hit)), default=0)
                            gap = max(0, len(lines) - 1 - last)
                            weak.append({"score": sum(len(t) for t in hit) * 10 + len(hit) - gap * 5,
                                         "rel": a["rel"], "sec": s, "blk": blk,
                                         "key": "+".join(hit), "method": "token", "w": 3, "a": a})

        def assign(pool):
            for c in sorted(pool, key=lambda x: -x["score"]):
                if c["rel"] in out or c["blk"].key in claimed:
                    continue
                claimed[c["blk"].key] = c["rel"]
                out[c["rel"]] = self._materialize(c, scrap_res)

        assign(strong)
        self._assign_borrow(assets, out, scrap_res)
        assign(weak)
        return out

    def _assign_borrow(self, assets, out, scrap_res=()):
        """无 prompt 块的章节（正文写「同第 N 条」）→ 借用那一条的 prompt（标 重构）。"""
        for a in assets:
            if a["rel"] in out:
                continue
            for s in self.sections:
                if s.candidates():
                    continue
                for key, method, bonus in a["keys"]:
                    w = self._weight("\n".join(s.lines), key)
                    if w is None or (method == "id" and w < 5):
                        continue
                    if self._heading_has_other_family(s.heading, a["id_token"], a["stem"], a["own_stems"]):
                        continue
                    m = BORROW_RE.search(s.text)
                    if not m:
                        continue
                    src = self.by_num.get(int(m.group(1)))
                    sblk = src.best_block() if src else None
                    if sblk is None:
                        continue
                    c = {"score": 0, "rel": a["rel"], "sec": s, "blk": sblk, "key": key,
                         "method": method, "w": w, "a": a, "borrow": f"同第{m.group(1)}条"}
                    out[a["rel"]] = self._materialize(c, scrap_res, borrowed=True)
                    break
                if a["rel"] in out:
                    break

    def _materialize(self, c, scrap_res=(), borrowed=False):
        a, s, blk = c["a"], c["sec"], c["blk"]
        prompt, negative = split_negative(blk.body)
        sec_text = s.text
        trace = guess_trace(sec_text)
        if borrowed:
            trace = "缺口" if trace == "缺口" else "重构"
        rejects = extract_rejects(sec_text)
        scrap_line, scrapped = self.scrap_from_lines([k for k, _m, _b in a["keys"]], scrap_res)
        if scrapped:
            rejects = scrap_line or rejects
        refs_text = blk.context + "\n" + blk.body + "\n" + sec_text
        conf = "high" if c["method"] in ("stem_ext", "stem", "id") else "low"
        return {
            "matched": True,
            "prompt": prompt,
            "negative": negative,
            "trace_status": trace,
            "prompt_source": {
                "file": os.path.basename(c["blk"].doc),
                "path": c["blk"].doc,
                "anchor": s.heading,
                "line": c["blk"].open_line,
                "match": f"{c['method']}:{c['key']}",
                "confidence": conf,
                "borrow": c.get("borrow", ""),
            },
            "refs": extract_refs(refs_text),
            "upload_order": extract_upload_order(refs_text),
            "rejects": rejects,
            "scrapped": scrapped,
            "tool": guess_tool(sec_text),
        }

    # ---------- 复用 / 判废线索 ----------
    def reuse_for(self, keys, ep_tag: str) -> str:
        shots, segs, scenes = [], [], []
        for _doc, _n, ln in self.lines:
            if not any(key_hit(ln, k) for k in keys if k):
                continue
            if any(x in ln for x in ("用途镜号", "复用", "挂载", "下游", "被挂", "镜号")):
                shots += SHOT_RE.findall(ln)
                segs += SEG_RE.findall(ln)
                scenes += SCENE_RE.findall(ln)
        out, seen = [], set()
        for v in shots + segs + ["场" + x for x in scenes]:
            if v not in seen:
                seen.add(v)
                out.append(v)
        out = out[:12]
        if not out:
            return ""
        return "; ".join(f"{ep_tag}:{v}" if ep_tag else v for v in out)

    def scrap_from_lines(self, keys, scrap_res=()):
        """找「点名本件」的判废证据（判据必须真正归属本件）。

        三条归属规则，缺一不可：
          ① 判据与文件名的距离 ≤60 字（同一表行/同一段落内）；
          ② 判据里若写了抽次（第N抽/vN），必须与本件抽次一致；本件无抽次则判据也不得带抽次；
          ③ 判据归属 = 「离判据最近的素材名」（左侧优先），必须是本件。
        这样「采纳版条目里提到另两抽判废」「挂载表里点名别的件废片留档」都不会误伤本件。
        """
        pats = list(SCRAP_RES) + [(re.compile(p), 40) for p in scrap_res]
        mykeys = set(keys)
        if self.line_occ is None:
            return "", False
        for i, (_doc, _n, ln) in enumerate(self.lines):
            occ = self.line_occ[i]
            mine = [o for o in occ if o[0] in mykeys]
            if not mine:
                continue
            for p, maxd in pats:
                for pm in p.finditer(ln):
                    near_mine = [o for o in mine
                                 if min(abs(o[1] - pm.end()), abs(pm.start() - o[2])) <= maxd]
                    if not near_mine:
                        continue
                    # ② 抽次一致性：只看「本件文件名 → 判据」之间那段文字里的抽次，
                    #    避免把文件名自带的「第2抽」当成判据的抽次
                    o = min(near_mine, key=lambda x: min(abs(x[1] - pm.end()), abs(pm.start() - x[2])))
                    seg = ln[o[2]:pm.end() + 12] if pm.start() >= o[2] else ln[pm.end():o[1]]
                    mk = re.search(r"第\s*([0-9０-９]+)\s*抽|[vV]\s*([0-9]+)", seg)
                    my_ver = ""
                    mv = re.search(r"第\s*([0-9０-９]+)\s*抽|[vV]\s*([0-9]+)", o[0])
                    if mv:
                        my_ver = mv.group(0).replace(" ", "")
                    if mk:
                        mk_ver = mk.group(0).replace(" ", "")
                        if not my_ver or mk_ver != my_ver:
                            continue
                    # ③ 归属：离判据最近的素材名必须是本件
                    if not occ:
                        continue
                    nearest = min(occ, key=lambda o: (0 if o[2] <= pm.start() else 1,
                                                      min(abs(o[1] - pm.end()), abs(pm.start() - o[2]))))
                    if nearest[0] not in mykeys:
                        continue
                    return ln.strip().strip("|").strip()[:400], True
        return "", False


def split_negative(body: str):
    """把代码块拆成 正文块 + 负面词串：负面行及其续行归入 negative。"""
    lines = body.splitlines()
    start = next((i for i, ln in enumerate(lines) if NEG_RE.match(ln.strip())), None)
    if start is None:
        return body.strip(), ""
    head = NEG_RE.match(lines[start].strip())
    parts = [head.group(1).strip()] if head and head.group(1).strip() else []
    j = start + 1
    while j < len(lines):
        s = lines[j].strip()
        if not s or s.startswith(("【", "（上传顺序", ">", "#", "```")):
            break
        parts.append(s)
        j += 1
    prompt = "\n".join(lines[:start] + lines[j:]).strip()
    negative = " ".join(p for p in parts if p).strip()
    negative = re.sub(r"^[（(]?[^：:]{0,24}[）)]?\s*[：:]\s*", "", negative)
    return prompt, negative


def guess_trace(text: str) -> str:
    if GAP_RE.search(text):
        return "缺口"
    if REBUILD_RE.search(text):
        return "重构"
    return "逐字"


def guess_tool(text: str) -> str:
    for k, v in TOOL_HINTS:
        if k in text:
            return v
    return ""


def extract_rejects(section_text: str):
    """判废经历/归因/要点 → rejects 文本（信息用；是否废片由 scrap_from_lines 按「点名本件」判定）。"""
    prio = [("判废归因", 0), ("判废经历", 1), ("判废要点", 2)]
    found = []
    for ln in section_text.splitlines():
        s = ln.strip().lstrip(">").strip()
        if not s:
            continue
        for kw, rank in prio:
            if kw in s:
                found.append((rank, re.sub(r"^[-*\s|]*", "", s)))
                break
    found.sort(key=lambda x: x[0])
    return " ｜ ".join(t for _r, t in found[:2])[:600]


def extract_refs(text: str):
    refs, seen = [], set()
    for m in REF_RE.finditer(text):
        idx = int(m.group(1))
        if idx in seen:
            continue
        seen.add(idx)
        fn = m.group(2).strip().strip("`*()（）")
        fn = re.split(r"[（(、，,；;）)】\]\s*]", fn)[0].strip().strip("`*")
        refs.append({"index": idx, "file": fn, "order": len(refs) + 1})
    return sorted(refs, key=lambda r: r["index"])


def extract_upload_order(text: str) -> str:
    m = UPLOAD_RE.search(text)
    if not m:
        return ""
    return re.split(r"[）)]\s*$", m.group(1).strip())[0].strip()


# ---------------------------------------------------------------- 类型/工具 推断

def guess_type(rel: str, name: str, text: str, media: str, default="模型生成") -> str:
    if media == "video":
        return "剪辑产物"
    if any(k in text for k in ("图生图", "参考图中", "同机位派生", "派生底图", "禁重新文生")):
        return "图生图派生"
    if re.search(r"(背面版|袖口|派生|改衣|首帧|变体|阵末空缺)", name):
        return "图生图派生"
    low = rel.lower()
    if any(k in low for k in ("用户", "upload", "上传", "实拍", "raw", "input", "客户")):
        return "用户输入"
    return default


def infer_tool(name: str, rel: str, text: str, default="") -> str:
    return guess_tool(text) or guess_tool(name + rel) or default


# ---------------------------------------------------------------- sidecar 读写与合并

def sidecar_path(media_path: str) -> str:
    return media_path + SIDECAR_SUFFIX


def load_sidecar(media_path: str):
    p = sidecar_path(media_path)
    if not os.path.exists(p):
        return {}
    try:
        with io.open(p, "r", encoding="utf-8-sig", errors="ignore") as fh:
            return json.load(fh)
    except Exception:  # noqa: BLE001
        return {"_parse_error": True}


VISION_KEYS = ["构图", "主体", "墨阶", "留白", "异常"]


def empty_vision():
    return {k: "" for k in VISION_KEYS}


# trace_status 强弱序（数字越大＝越强）：缺口 < 重构 < 逐字
TRACE_RANK = {"缺口": 0, "重构": 1, "逐字": 2}


def merge_trace(new_trace, old_trace, new_rec=None, old_rec=None) -> str:
    """trace_status 合并规则（红线：禁伪造逐字）—— **以 sidecar 旧值为准**。

    - 旧值为空 → 用新值（新件首次登记）；
    - 新值由人显式提供（`trace_source=human`，如 `ingest_asset.py --trace-status`）→ 以新值为准；
      但**升「逐字」必须带非空 `verbatim_source`**（逐字来源凭证），否则保持旧值；
    - 旧值已是人写/回贴落定（`old.trace_source=human`）→ **机器不得改**（粘滞）；
    - 其余＝机器重推（索引侧按来源 md 重算）：
      · 升档（重构→逐字）一律**拦截**（除非 sidecar 已有 `verbatim_source` 凭证）；
      · 降档（逐字→重构/缺口）也**不自动落盘**（机器不得静默把权威值改弱）——
        想降档的差异由 `asset_index.py --audit-sidecars` 逐字段列出，交人/门控确认后显式改。
      机器仍保留唯一硬判：**没有 prompt → 强制 `缺口`**（合并后由 build_index 兜底，见下）。
    """
    nt, ot = norm_trace(new_trace), norm_trace(old_trace)
    if not ot:
        return nt
    if nt == "N/A":
        return nt          # 废片＝不判溯源档（状态语义，不是"更强/更弱"的溯源主张）
    new_src = str((new_rec or {}).get("trace_source") or "").strip()
    old_src = str((old_rec or {}).get("trace_source") or "").strip()
    vs = str((new_rec or {}).get("verbatim_source")
             or (old_rec or {}).get("verbatim_source") or "").strip()
    if new_src == "human":
        if nt == "逐字" and TRACE_RANK.get(nt, -1) > TRACE_RANK.get(ot, -1) and not vs:
            return ot
        return nt
    if old_src == "human":
        return ot
    if TRACE_RANK.get(nt, -1) > TRACE_RANK.get(ot, -1):
        return nt if vs else ot
    return ot


def merge_record(new: dict, old: dict) -> dict:
    """合并：新值非空则覆盖；旧值非空而新值为空则保留（保护 agent/人工手写的标签）。

    未知键保证（**merge 不清空未知键**）：旧 sidecar 里 schema 之外的自定义键（如视频类备注
    `vision_note`）原样沿用，索引刷新重写 sidecar 时不被丢弃、也不被空值清空；仅内部哨兵键
    （`_` 开头，如 load_sidecar 的 `_parse_error`）不落盘。

    溯源红线（**禁伪造逐字**）：`trace_status` 以 sidecar 旧值为准——机器重推的值只能「降级或持平」，
    **不得自动升级到 `逐字`**；要升 `逐字` 必须由人/回贴显式提供且带非空 `verbatim_source`
    （见 merge_trace）。`rejects` 同理：旧值非空时，**索引重推值一律不覆盖**，只有显式人写
    （`rejects_source=human`）才允许改写；覆盖与否由 `rejects_source` 标记区分。
    """
    out = dict(new)
    out["trace_status"] = norm_trace(out.get("trace_status"))
    if not old or not isinstance(old, dict):
        return out
    for k in ("type", "tool", "date", "reuse", "upload_order", "negative", "prompt", "scrapped"):
        if out.get(k) in (None, "", False) and old.get(k) not in (None, ""):
            out[k] = old[k]
            if k == "prompt":
                out["prompt_source"] = old.get("prompt_source", {})
    if not out.get("refs") and old.get("refs"):
        out["refs"] = old["refs"]
    # ---- trace_status：sidecar 旧值优先，禁自动升「逐字」 ----
    out["trace_status"] = merge_trace(out.get("trace_status"), old.get("trace_status"), out, old)
    if out.get("trace_status") == norm_trace(old.get("trace_status")) and (old.get("trace_source") or ""):
        out["trace_source"] = old["trace_source"]      # 值取自 sidecar → 来源标记随 sidecar（含人写粘滞标记）
    # ---- rejects：旧值非空时，索引重推不覆盖（只有 rejects_source=human 才改写） ----
    old_rej = (old.get("rejects") or "").strip()
    new_rej = (out.get("rejects") or "").strip()
    if old_rej and new_rej and (out.get("rejects_source") or "").strip() != "human":
        out["rejects"] = old["rejects"]
        out["rejects_source"] = old.get("rejects_source") or "sidecar"
    elif old_rej and not new_rej:
        out["rejects"] = old["rejects"]
        out["rejects_source"] = old.get("rejects_source") or "sidecar"
    # schema 外的自定义键（agent/人工手写，如 vision_note）一律沿用旧 sidecar 值 —— 见上方「未知键保证」；
    # 已知键同样遵守「非空覆盖」：新值为空而旧值非空时保留旧值，绝不用空值清空。
    for k, v in old.items():
        if isinstance(k, str) and k.startswith("_"):
            continue
        if k not in out:
            out[k] = v
        elif out.get(k) in (None, "", False) and v not in (None, ""):
            out[k] = v
    vision = empty_vision()
    for k in VISION_KEYS:
        vision[k] = (out.get("vision") or {}).get(k, "") or (old.get("vision") or {}).get(k, "")
    out["vision"] = vision
    out["vision_filled"] = bool(old.get("vision_filled")) or any(vision.values())
    # 本件 prompt 来自 sidecar（索引侧没匹配到来源）→ 溯源档/出处/置信度一律以 sidecar 为准
    if not (new.get("prompt") or "").strip() and (old.get("prompt") or "").strip():
        out["trace_status"] = norm_trace(old.get("trace_status")) or out.get("trace_status")
        out["prompt_source"] = old.get("prompt_source", out.get("prompt_source", {}))
        out["match_confidence"] = "sidecar"
    return out


def is_gap(rec: dict) -> bool:
    """缺口判定：无 prompt，或显式 trace_status=缺口（兼容英文别名 missing/label_gap）。"""
    return (not (rec.get("prompt") or "").strip()) or norm_trace(rec.get("trace_status")) == "缺口"


# ---------------------------------------------------------------- 配置

def default_config():
    return {
        "include_globs": list(DEFAULT_INCLUDE),
        "exclude_dirs": list(DEFAULT_EXCLUDE_DIRS),
        "kind_dirs": dict(KIND_DIR),
        "prefix_by_kind": dict(KIND_PREFIX),
        "version_words": [],
        "ep_tag": "",
        "prompt_sources": [],
        "tool_default": "",
        "type_default": "模型生成",
        "scrap_markers": [],
        "index_dir": "",
    }


def load_config(root: str, explicit):
    cfg = default_config()
    cands = ([explicit] if explicit else []) + [
        os.path.join(root, CONFIG_NAME),
        os.path.join(os.path.dirname(os.path.abspath(root)), CONFIG_NAME),
    ]
    used = ""
    for p in cands:
        if p and os.path.exists(p):
            try:
                with io.open(p, "r", encoding="utf-8-sig", errors="ignore") as fh:
                    user = json.load(fh)
                cfg.update({k: v for k, v in user.items() if v not in (None, "", [], {})})
                used = p
                break
            except Exception as e:  # noqa: BLE001
                print(f"[warn] 配置文件读取失败 {p}: {e}")
    return cfg, used


# ---------------------------------------------------------------- 扫描

def iter_media(root: str, include_globs, exclude_dirs):
    """枚举媒体文件，返回 (在册文件, 被排除文件)；均按相对路径排序。"""
    keep, dropped = [], []
    ex = set(exclude_dirs)
    for dirpath, _dirnames, filenames in os.walk(root):
        for f in sorted(filenames):
            full = os.path.join(dirpath, f)
            if f.endswith(SIDECAR_SUFFIX) or f.endswith(".json") or f.startswith("."):
                continue
            if not any(fnmatch.fnmatch(f.lower(), g.lower()) for g in include_globs):
                continue
            rel = norm_rel(full, root)
            parts = rel.split("/")
            drop = next((d for d in ex if d in parts), None)
            if drop:
                dropped.append({"rel": rel, "reason": f"排除目录 {drop}"})
            else:
                keep.append(full)
    keep.sort(key=lambda p: norm_rel(p, root))
    dropped.sort(key=lambda d: d["rel"])
    return keep, dropped


# ---------------------------------------------------------------- 索引构建

def build_index(root: str, cfg: dict, corpus: PromptCorpus, ep_tag: str, quiet=False, pushed_out=None):
    """扫全库建索引。pushed_out（可选 list）会收到逐件的「索引重推值 vs sidecar 现值」快照（体检用）。"""
    include = cfg.get("include_globs") or DEFAULT_INCLUDE
    exclude = cfg.get("exclude_dirs") or DEFAULT_EXCLUDE_DIRS
    version_words = cfg.get("version_words") or []
    scrap_res = [re.compile(p) for p in (cfg.get("scrap_markers") or [])]
    files, dropped = iter_media(root, include, exclude)
    all_stems = [os.path.splitext(os.path.basename(p))[0] for p in files]

    prepared = []
    for full in files:
        name = os.path.basename(full)
        stem = os.path.splitext(name)[0]
        rel = norm_rel(full, root)
        naming = check_naming(rel, version_words)
        variant = re.sub(r"变体\s*([0-9])", lambda m: "变体" + "①②③④⑤⑥⑦⑧⑨"[int(m.group(1)) - 1], stem)
        tokens = [t for t in re.split(r"[-_ ]+", variant) if len(t) >= 2]
        keys = [(name, "stem_ext", 40), (stem, "stem", 20)]
        if variant != stem:
            keys.append((variant, "stem", 20))
        if naming.get("id_token"):
            keys.append((naming["id_token"], "id", 5))
        prepared.append({"full": full, "name": name, "file": name, "stem": stem, "rel": rel,
                         "naming": naming, "tokens": tokens, "keys": keys,
                         "id_token": naming.get("id_token", ""),
                         "own_stems": set(all_stems)})

    matches = corpus.resolve(prepared, scrap_res) if corpus.sections else {}

    assets = []
    seq_by_kind = {}
    for p in prepared:
        full, name, stem, rel = p["full"], p["name"], p["stem"], p["rel"]
        ext = os.path.splitext(name)[1].lower()
        media = media_kind_of(ext)
        naming = p["naming"]
        kind = naming.get("kind") or ""
        seq_by_kind[kind] = seq_by_kind.get(kind, 0) + 1
        if not naming["suggest"]:
            naming["suggest"] = suggest_name(stem, ext, kind or "角色", seq_by_kind[kind])
        m = matches.get(rel) or {}
        keys = [k for k, _t, _b in p["keys"]]
        hint = (m.get("prompt") or "") + "\n" + (m.get("negative") or "")
        old = load_sidecar(full)
        dims, dims_note = read_dims(full)
        # 工具推断：prompt/章节线索 > 文件名线索 > 项目兜底（视频不吃「出图工具」兜底）
        tool = infer_tool(name, rel, (m.get("tool") or "") + hint,
                          "" if media == "video" else cfg.get("tool_default", ""))
        if not tool:
            tool = "剪辑合成（待补确认）" if media == "video" else "未知（待补）"
        rec = {
            "file": name,
            "rel": rel,
            "dir": os.path.dirname(rel) or ".",
            "kind": kind,
            "media": media,
            "ext": ext,
            "type": guess_type(rel, name, hint, media, cfg.get("type_default", "模型生成")),
            "tool": tool,
            "prompt": m.get("prompt") or "",
            "negative": m.get("negative") or "",
            "refs": m.get("refs") or [],
            "upload_order": m.get("upload_order") or "",
            "date": datetime.datetime.fromtimestamp(os.path.getmtime(full)).strftime("%Y%m%d"),
            "rejects": m.get("rejects") or "",
            "rejects_source": "index" if (m.get("rejects") or "").strip() else "",
            "scrapped": bool(m.get("scrapped")),
            "reuse": corpus.reuse_for(keys, ep_tag),
            "trace_status": m.get("trace_status") or ("缺口" if not m.get("prompt") else "逐字"),
            "trace_source": "index",
            "vision": empty_vision(),
            "vision_filled": False,
            "sha256": sha256_file(full),
            "size": os.path.getsize(full),
            "dims": dims,
            "dims_note": dims_note,
            "prompt_source": m.get("prompt_source") or {
                "file": "", "anchor": "", "line": 0, "match": "未匹配", "confidence": "none"},
            "naming": naming,
            "match_confidence": (m.get("prompt_source") or {}).get("confidence", "none"),
            "sidecar_path": norm_rel(sidecar_path(full), root),
            "updated_at": now_str(),
        }
        if not rec["prompt"]:
            rec["trace_status"] = "缺口"
        if rec.get("scrapped"):
            rec["trace_status"] = "N/A"      # 废片一律 N/A（不判溯源档；判废原因在 rejects，采纳版在 note）
        pushed = dict(rec)          # 合并前快照＝「索引重推值」（--audit-sidecars 体检用）
        rec = merge_record(rec, old)
        # 合并后仍无 prompt → 缺口（sidecar 里人工/agent 写过的 prompt 优先，见 merge_record）
        if not (rec.get("prompt") or "").strip():
            rec["trace_status"] = "缺口"
        assets.append(rec)
        if pushed_out is not None:
            pushed_out.append({"rel": rel, "old": old, "pushed": pushed, "merged": rec})
        if not quiet:
            mark = "缺" if is_gap(rec) else ("废" if rec.get("scrapped") else "OK")
            print(f"  [{mark}] {rel}  ({rec['trace_status']}, {rec['match_confidence']})")

    counts = {
        "total": len(assets),
        "逐字": sum(1 for a in assets if a["trace_status"] == "逐字" and a.get("prompt")),
        "重构": sum(1 for a in assets if a["trace_status"] == "重构"),
        "缺口": sum(1 for a in assets if is_gap(a)),
        "不适用": sum(1 for a in assets if a["trace_status"] == "N/A"),
        "废片": sum(1 for a in assets if a.get("scrapped")),
        "命名不合规": sum(1 for a in assets if not a["naming"]["ok"]),
        "vision未填": sum(1 for a in assets if not any((a.get("vision") or {}).values())),
        "低置信匹配": sum(1 for a in assets if a.get("match_confidence") == "low"),
        "排除": len(dropped),
    }
    return assets, dropped, counts


def diff_with_disk(root: str, cfg: dict, index: dict):
    """双向核对：盘上有而索引无（未登记）/ 索引有而盘上无（断链）。"""
    include = cfg.get("include_globs") or DEFAULT_INCLUDE
    exclude = cfg.get("exclude_dirs") or DEFAULT_EXCLUDE_DIRS
    files, _d = iter_media(root, include, exclude)
    disk = {norm_rel(p, root) for p in files}
    idx = {a.get("rel", "") for a in index.get("assets", [])}
    return sorted(disk - idx), sorted(idx - disk)


# ---------------------------------------------------------------- 输出：人读表 / 缺口清单

def render_index_md(index: dict, root_label: str) -> str:
    c = index["counts"]
    L = [f"# 素材索引（assets_index）· {root_label}", ""]
    L.append(f"> 生成时间：{index['generated_at']}　｜　素材根：`{index['root']}`　｜　EP 标记：{index.get('ep_tag') or '（未设置）'}")
    L.append(f"> prompt 来源文件：{'、'.join(index.get('prompt_sources') or []) or '（未指定）'}")
    _rd = ((index.get('meta') or {}).get('role_division') or {})
    if _rd:
        _mi = _rd.get('machine_index') or {}
        _ht = _rd.get('human_table') or {}
        L.append('> **单一索引原则（%s）**：**机器唯一索引**＝%s（%s；**%s**）；**人读详表**＝%s（%s）。'
                 '**冲突时%s。**'
                 % (_rd.get('ruling', ''),
                    '、'.join(_mi.get('files') or []), _mi.get('role', ''), _mi.get('hand_edit', ''),
                    '、'.join(_ht.get('files') or []), _ht.get('role', ''),
                    _mi.get('precedence', '')))
    L.append('> **排除目录口径**：' + ((index.get('meta') or {}).get('excluded_dirs_policy')
                                   or EXCLUDED_DIRS_POLICY))
    L.append('> **刷新纪律（并发安全）**：' + ((index.get('meta') or {}).get('refresh_discipline')
                                          or REFRESH_DISCIPLINE))
    L.append("## 一、总账")
    L.append("")
    L.append("| 指标 | 数量 |")
    L.append("|---|---|")
    for k in ("total", "逐字", "重构", "缺口", "不适用", "废片", "命名不合规", "vision未填", "低置信匹配", "排除"):
        L.append(f"| {k} | {c.get(k, 0)} |")
    L.append("")
    L.append("> 逐字＝prompt 全文可从落盘文件逐字复制；重构＝按要点复原的候选全文（出图前须过目）；"
             "缺口＝采纳版全文不可复现（**门控 FAIL**）；**不适用＝`N/A`（废片不判溯源档：判废原因在 `rejects`、"
             "采纳版在 `note`）**。")
    L.append("")
    L.append("## 二、逐件台账（按目录分组）")
    cur = None
    for a in index["assets"]:
        if a["dir"] != cur:
            cur = a["dir"]
            L += ["", f"### {cur}/", "",
                  "| 文件 | 类别 | 类型 | 溯源 | 工具 | 正文字数 | 负面 | refs | 复用 | 命名 |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        refs = "、".join(f"@{r['index']}={r['file'][:16]}" for r in (a.get("refs") or [])) or "—"
        conf = "" if a.get("match_confidence") in ("high", "none", "") else f"（{a['match_confidence']}）"
        L.append("| `{}` | {} | {} | {}{} | {} | {} | {} | {} | {} | {} |".format(
            a["file"], a.get("kind") or "—", a.get("type") or "—",
            {"逐字": "✅逐字", "重构": "⚠️重构", "缺口": "⛔缺口",
             "N/A": "🅝N/A（废片）"}.get(a["trace_status"], a["trace_status"]),
            conf, a.get("tool") or "—", len(a.get("prompt") or ""), len(a.get("negative") or ""),
            refs, (a.get("reuse") or "—")[:30], "✅" if a["naming"]["ok"] else "❌"))
    gaps = [a for a in index["assets"] if is_gap(a)]
    L += ["", "## 三、缺口清单（待补 prompt）", ""]
    if not gaps:
        L.append("（无缺口）")
    else:
        L += ["| # | 文件 | 目录 | 处置 |", "|---|---|---|---|"]
        for i, a in enumerate(gaps, 1):
            ps = a.get("prompt_source") or {}
            why = "来源标注缺口" if ps.get("confidence") != "none" else "全部来源文件均未匹配"
            L.append(f"| {i} | `{a['file']}` | {a['dir']} | {why} → 见 `{GAPS_MD}` |")
    low = [a for a in index["assets"] if a.get("match_confidence") == "low"]
    if low:
        L += ["", "## 四、低置信匹配（须人工确认来源是否对）", "",
              "| 文件 | 匹配方式 | 来源 |", "|---|---|---|"]
        for a in low:
            ps = a.get("prompt_source") or {}
            L.append(f"| `{a['file']}` | {ps.get('match', '')} | {ps.get('file', '')} L{ps.get('line', '')} |")
    scrapped = [a for a in index["assets"] if a.get("scrapped")]
    if scrapped:
        L += ["", "## 五、废片留档（不得用于下游）", ""]
        for a in scrapped:
            L.append(f"- `{a['file']}` —— {(a.get('rejects') or '')[:120]}")
    if index.get("excluded"):
        L += ["", "## 六、已排除（归档/抽帧目录，不参与索引入库）", "",
              "> 口径：" + ((index.get('meta') or {}).get('excluded_dirs_policy') or EXCLUDED_DIRS_POLICY), ""]
        for d in index["excluded"]:
            L.append(f"- `{d['rel']}` —— {d['reason']}")
    L.append("")
    return "\n".join(L)


def render_gaps_md(index: dict, root_label: str) -> str:
    gaps = [a for a in index["assets"] if is_gap(a)]
    L = [f"# 素材 prompt 缺口清单（asset_gaps）· {root_label}", "",
         f"> 生成时间：{index['generated_at']}　｜　素材根：`{index['root']}`",
         "> 判定：**索引里没有非空 prompt**（来源文件里对不上，或来源本身标了缺口）。",
         "> 这是「待补录 prompt 清单」的机器生成版：补录后重跑 `asset_index.py` 即自动消项。",
         "", f"## 待补 {len(gaps)} 件", ""]
    if not gaps:
        L.append("（无缺口）")
        return "\n".join(L) + "\n"
    cur = None
    for i, a in enumerate(gaps, 1):
        if a["dir"] != cur:
            cur = a["dir"]
            L += ["", f"### {cur}/", "", "| # | 文件 | 现状 | 建议动作 |", "|---|---|---|---|"]
        ps = a.get("prompt_source") or {}
        if ps.get("confidence") and ps.get("confidence") != "none":
            now = f"来源《{ps.get('file')}》标注为「{a['trace_status']}」（{ps.get('anchor', '')[:26]}）"
            todo = "请出图执行者回贴采纳版原文，或授权以已落盘基线重新定稿"
        else:
            now = "全部来源文件均未匹配到本件"
            todo = "先确认该件出自哪次对话/哪份清单，再补录入库（见 asset_schema.md §六）"
        L.append(f"| {i} | `{a['file']}` | {now} | {todo} |")
    L += ["", "## 补录口径（与 asset_schema.md §六 一致）", "",
          "1. 每条补录＝`风格token ＋ 正文 ＋ 负面词整串 ＋ 判废要点`，落进项目 md 的一个 ``` 围栏块；",
          "   块前写文件名，或写一行 `**保存文件名**：\\`<file>\\``（两种都能被自动对上）。",
          "2. 重跑：`python scripts/asset_index.py --root <素材根> --prompt-source <md>...`",
          "   （或写进 `asset_index.config.json` 的 `prompt_sources`，一条命令复用）。",
          "3. 门控：`python scripts/check_asset_labels.py <素材根或 runs/<项目>>` —— 缺口件计入 FAIL。", ""]
    return "\n".join(L)


# ---------------------------------------------------------------- 体检：索引重推 vs sidecar

AUDIT_FIELDS = ("trace_status", "rejects", "prompt", "negative", "scrapped", "reuse", "tool", "type", "refs")


def _short(v, n=90):
    if isinstance(v, (list, dict)):
        s = json.dumps(v, ensure_ascii=False)
    else:
        s = "" if v is None else str(v)
    s = s.replace("\n", " ")
    return s if len(s) <= n else s[:n] + "…"


def audit_rows(pushed_out):
    """逐件逐字段比对「索引重推值」与「sidecar 现值」，返回差异清单（含合并后实际写入值）。"""
    rows = []
    for item in pushed_out or []:
        old, p, merged = item.get("old") or {}, item.get("pushed") or {}, item.get("merged") or {}
        if not old:
            continue                                  # 无 sidecar（新件）→ 无「现值」可比
        diffs = []
        for f in AUDIT_FIELDS:
            ov, pv = old.get(f), p.get(f)
            if f == "rejects":
                ov, pv = (ov or "").strip(), (pv or "").strip()
            if ov == pv:
                continue
            mv = merged.get(f)
            if f == "trace_status":
                rn, ro = TRACE_RANK.get(norm_trace(pv), -1), TRACE_RANK.get(norm_trace(ov), -1)
                if rn > ro:
                    risk = "🔴 索引想升档 → 已拦截（禁伪造逐字）"
                elif rn < ro:
                    risk = "🟡 索引想降档 → 不自动落盘（机器不得静默改弱；保持 sidecar 值）"
                else:
                    risk = "持平"
            elif f == "rejects" and ov and pv:
                risk = "🔴 索引重推想覆盖非空旧值 → 已拦截"
            elif ov and not pv:
                risk = "⚪ 索引重推值为空 → 旧值被保护"
            else:
                risk = "🟡 索引重推（旧值非空时受保护／空值不覆盖）"
            diffs.append({"field": f, "sidecar": _short(ov), "pushed": _short(pv),
                          "merged": _short(mv), "risk": risk})
        vo, vm = old.get("vision") or {}, merged.get("vision") or {}
        for k in VISION_KEYS:
            if (vo.get(k) or "") != (vm.get(k) or ""):
                diffs.append({"field": "vision." + k, "sidecar": _short(vo.get(k)),
                              "pushed": "（空）", "merged": _short(vm.get(k)),
                              "risk": "⚪ 索引侧空值 → 旧值被保护"})
        if diffs:
            rows.append({"rel": item.get("rel", ""), "diffs": diffs})
    return rows


def render_audit_md(root_label: str, rows, total: int) -> str:
    L = [f"# sidecar 体检（索引重推 vs sidecar 现值）· {root_label}", "",
         f"> 生成时间：{now_str()}　｜　逐件比对 {total} 件　｜　有差异 {len(rows)} 件　｜　"
         f"字段级差异 {sum(len(r['diffs']) for r in rows)} 处", "",
         "> 用途：`asset_index.py` 每次刷新都会重推一遍字段值。本表列出**索引重推值 ≠ sidecar 现值**的字段，",
         "> 并给出合并后实际写入值。保护规则（`merge_record`）：`trace_status` 以 sidecar 为准、"
         "**机器不得自动升「逐字」**（升档须显式 `verbatim_source`）；`rejects` 旧值非空时索引重推不覆盖"
         "（仅 `rejects_source=human` 可改写）；未知键（如 `vision_note`）原样保留。", ""]
    if not rows:
        L.append("（无差异：sidecar 现值与索引重推值完全一致）")
        return "\n".join(L) + "\n"
    for r in rows:
        L += [f"## `{r['rel']}`", "",
              "| 字段 | sidecar 现值 | 索引重推值 | 合并后（将写入） | 判定 |", "|---|---|---|---|---|"]
        for d in r["diffs"]:
            L.append("| `{}` | {} | {} | {} | {} |".format(
                d["field"], d["sidecar"] or "—", d["pushed"] or "—", d["merged"] or "—", d["risk"]))
        L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------- CLI

def resolve_root(path: str):
    """把「项目目录」或「素材根」都吃进来；返回 (素材根, 说明)。

    规则：目标下若有 refs/ assets/ 素材/ 素材库/ 且其中有媒体文件 → 取该子目录为素材根（约定优先）；
    否则目标自身就是素材根。
    """
    p = os.path.abspath(path)
    if not os.path.isdir(p):
        return p, ""
    for sub in ("refs", "assets", "素材", "素材库"):
        q = os.path.join(p, sub)
        if os.path.isdir(q) and iter_media(q, DEFAULT_INCLUDE, DEFAULT_EXCLUDE_DIRS)[0]:
            return q, f"（自动识别素材根：{sub}/）"
    if iter_media(p, DEFAULT_INCLUDE, DEFAULT_EXCLUDE_DIRS)[0]:
        return p, ""
    return p, ""


def build_argparser():
    ap = argparse.ArgumentParser(
        prog="asset_index.py",
        description="科生·素材索引器：扫素材根 → 生成 sidecar 标签 + 全库索引 + prompt 溯源匹配 + 缺口清单",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例:\n"
               "  python scripts/asset_index.py --root runs/EP01/refs --prompt-source runs/EP01/m5-素材prompt补录.md runs/EP01/m5-OP前置件出图包.md\n"
               "  python scripts/asset_index.py --root runs/EP01 --check        # 只核对，不改写\n"
               "  python scripts/asset_index.py --root runs/EP01/refs --no-sidecar   # 只刷索引（安全档，推荐）\n"
               "  python scripts/asset_index.py --root runs/EP01/refs --audit-sidecars  # 只读体检：索引重推 vs sidecar 现值\n"
               "  python scripts/asset_index.py --root runs/EP01/refs --exclude-dir _frames --ep-tag EP01\n")
    ap.add_argument("root_pos", nargs="?", help="素材根目录（也可用 --root）")
    ap.add_argument("--root", help="素材根目录")
    ap.add_argument("--out", help="索引输出目录（默认：素材根为 refs/assets/素材 时取其上一级，否则取自身）")
    ap.add_argument("--prompt-source", nargs="+", action="append", default=[], dest="prompt_source",
                    metavar="MD", help="项目 prompt 来源 md（可多个；建议放命令末尾）")
    ap.add_argument("--include", help="包含 glob，逗号分隔（默认常见图片/视频扩展名）")
    ap.add_argument("--exclude-dir", help="排除目录名，逗号分隔（默认含 _废片/_旧版归档/_frames 等）")
    ap.add_argument("--version-word", help="额外认可的版本段词（逗号分隔），如 主版,剪影版,基础版")
    ap.add_argument("--scrap-marker", help="额外废片判据正则（逗号分隔）")
    ap.add_argument("--ep-tag", help="EP 标记（写进 reuse，如 EP01）")
    ap.add_argument("--config", help=f"配置文件（默认找 <root>/{CONFIG_NAME} 或上一级同名文件）")
    ap.add_argument("--tool-default", help="未推断出工具时的兜底值")
    ap.add_argument("--check", action="store_true", help="只报告双向核对，不改写任何文件")
    ap.add_argument("--no-sidecar", action="store_true",
                    help="只刷新索引，不改写任何 <file>.label.json（**推荐的安全档**：凡「只刷索引/复核」"
                         "一律用它；新件登记也走此档，见 ingest_asset.py）")
    ap.add_argument("--audit-sidecars", action="store_true", dest="audit_sidecars",
                    help="只读体检：逐件输出「索引重推值 vs sidecar 现值」的字段级差异清单"
                         "（写 sidecar_audit.md/.json，不改任何 sidecar/索引）")
    ap.add_argument("--quiet", action="store_true", help="不逐件打印")
    return ap


def main(argv=None) -> int:
    args = build_argparser().parse_args(argv)
    root_arg = args.root or args.root_pos
    if not root_arg:
        build_argparser().print_help()
        return 2
    root, note = resolve_root(root_arg)
    if not os.path.isdir(root):
        print(f"[FAIL] 素材根不存在：{root}")
        return 2
    if note:
        print(f"[提示] {note}")

    cfg, cfg_used = load_config(root, args.config)
    if args.include:
        cfg["include_globs"] = [s.strip() for s in args.include.split(",") if s.strip()]
    if args.exclude_dir:
        cfg["exclude_dirs"] = [s.strip() for s in args.exclude_dir.split(",") if s.strip()]
    if args.version_word:
        cfg["version_words"] = list(cfg.get("version_words") or []) + \
            [s.strip() for s in args.version_word.split(",") if s.strip()]
    if args.scrap_marker:
        cfg["scrap_markers"] = list(cfg.get("scrap_markers") or []) + \
            [s.strip() for s in args.scrap_marker.split(",") if s.strip()]
    if args.tool_default:
        cfg["tool_default"] = args.tool_default

    out_dir = args.out or cfg.get("index_dir") or (
        os.path.dirname(root) if os.path.basename(root) in ("refs", "assets", "素材", "素材库") else root)

    sources = []
    for grp in (args.prompt_source or []):
        sources += grp
    if not sources:
        base = os.path.dirname(os.path.abspath(root))
        sources = [s if os.path.isabs(s) else os.path.join(base, s)
                   for s in (cfg.get("prompt_sources") or [])]
    sources = [os.path.abspath(s) for s in sources]
    for s in [x for x in sources if not os.path.exists(x)]:
        print(f"[warn] prompt 来源文件不存在，已跳过：{s}")
    sources = [s for s in sources if os.path.exists(s)]

    ep_tag = args.ep_tag or cfg.get("ep_tag") or ""
    if not ep_tag:
        m = re.search(r"(?:^|[-_ ])(EP\d{1,3})", os.path.basename(os.path.abspath(out_dir)), re.I)
        ep_tag = m.group(1).upper() if m else ""

    index_path = os.path.join(out_dir, INDEX_JSON)
    corpus = PromptCorpus(sources)
    root_label = os.path.basename(os.path.abspath(root))
    blocks = sum(len(s.blocks) for s in corpus.sections)
    print("== 素材索引器 ==")
    print(f"   素材根：{root}")
    print(f"   输出目录：{out_dir}" + (f"（配置 {cfg_used}）" if cfg_used else ""))
    print(f"   prompt 来源：{len(sources)} 份 / 章节 {len(corpus.sections)} / 候选块 {blocks}"
          + "".join(f"\n     - {os.path.basename(s)}" for s in sources))
    print(f"   EP 标记：{ep_tag or '（未设置）'}")

    if args.check:
        if not os.path.exists(index_path):
            print(f"\n[FAIL] 找不到索引 {index_path}：先跑一次不带 --check 的 asset_index.py")
            return 1
        with io.open(index_path, "r", encoding="utf-8-sig", errors="ignore") as fh:
            index = json.load(fh)
        unreg, broken = diff_with_disk(root, cfg, index)
        print("\n== --check 双向核对（只读）==")
        print(f"   索引登记 {len(index.get('assets', []))} 件")
        print(f"   未登记（盘上有、索引无）：{len(unreg)}")
        for r in unreg:
            print(f"     - {r}")
        print(f"   断链（索引有、盘上无）：{len(broken)}")
        for r in broken:
            print(f"     - {r}")
        return 1 if (unreg or broken) else 0

    if args.audit_sidecars:
        # 只读体检：算一遍「索引重推值」与 sidecar 现值比差异，**不写任何 sidecar / 索引**
        pushed = []
        _a, _d, _c = build_index(root, cfg, corpus, ep_tag, quiet=args.quiet, pushed_out=pushed)
        rows = audit_rows(pushed)
        md_path = os.path.join(out_dir, "sidecar_audit.md")
        json_path = os.path.join(out_dir, "sidecar_audit.json")
        write_text(md_path, render_audit_md(root_label, rows, len(pushed)))
        write_json(json_path, {"generated_at": now_str(), "root": root, "root_label": root_label,
                               "total": len(pushed), "diff_items": len(rows),
                               "diff_fields": sum(len(r["diffs"]) for r in rows), "rows": rows})
        print("\n== sidecar 体检（--audit-sidecars，只读：不改 sidecar/索引）==")
        print(f"   逐件比对 {len(pushed)} 件｜有差异 {len(rows)} 件｜"
              f"字段级差异 {sum(len(r['diffs']) for r in rows)} 处")
        for r in rows:
            for d in r["diffs"]:
                print(f"   - {r['rel']} :: {d['field']}  sidecar[{d['sidecar'] or '—'}]"
                      f" ≠ push[{d['pushed'] or '—'}] → 写入[{d['merged'] or '—'}]  {d['risk']}")
        print(f"   → {md_path}")
        print(f"   → {json_path}")
        return 0

    assets, dropped, counts = build_index(root, cfg, corpus, ep_tag, quiet=args.quiet)
    index = {
        "generated_at": now_str(),
        "root": root,
        "root_label": root_label,
        "ep_tag": ep_tag,
        "prompt_sources": [os.path.basename(s) for s in sources],
        "prompt_source_paths": sources,
        "meta": cfg.get("index_meta") or {},
        "counts": counts,
        "assets": assets,
        "excluded": dropped,
    }
    if args.no_sidecar:
        print("   （--no-sidecar：本次不改写任何 sidecar，只刷新索引 ✅ 安全档）")
    else:
        for a in assets:
            write_json(sidecar_path(os.path.join(root, a["rel"].replace("/", os.sep))), a)
        print(f"   （已回写 {len(assets)} 个 sidecar；只刷索引请加 --no-sidecar，"
              f"体检字段级差异用 --audit-sidecars）")
    write_json(index_path, index)
    write_text(os.path.join(out_dir, INDEX_MD), render_index_md(index, root_label))
    write_text(os.path.join(out_dir, GAPS_MD), render_gaps_md(index, root_label))

    print("\n== 结果 ==")
    print(f"   在册 {counts['total']} 件｜逐字 {counts['逐字']}｜重构 {counts['重构']}｜缺口 {counts['缺口']}"
          f"｜废片 {counts['废片']}｜命名不合规 {counts['命名不合规']}｜vision 未填 {counts['vision未填']}"
          f"｜排除 {counts['排除']}")
    print(f"   → {index_path}")
    print(f"   → {os.path.join(out_dir, INDEX_MD)}")
    print(f"   → {os.path.join(out_dir, GAPS_MD)}")
    print(f"   下一步自检：python scripts/check_asset_labels.py \"{root}\"")
    return 0


if __name__ == "__main__":
    sys.exit(main())
