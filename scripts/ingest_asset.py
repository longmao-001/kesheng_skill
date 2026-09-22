#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科生·素材入库器 (ingest_asset.py) —— 「入库即标签」一条命令

一次动作 = 改名入对应目录 → 抽 prompt 全文 → 写 sidecar 标签 → 刷新全库索引 → 打印下一步校验命令。
目标：**素材进库的那一刻，出处/参考/判废/复用就已经在库了**，不再事后靠人工补台账。

用法:
  python scripts/ingest_asset.py <图或视频> --root <素材根> --kind 角色|道具|场景|字帖|故事板|成片
        --id <ID> --name <名> [--version v1|第1抽] [--prompt-file <md>] [--prompt-anchor <定位串>]
        [--prompt "全文"] [--negative "..."] [--refs "@图片1=xxx.jpg"] [--upload-order "..."]
        [--reject 原因] [--reuse "EP01:1-16"] [--tool "GPT Image 2"] [--type 模型生成]
        [--vision 构图=... 主体=... 墨阶=... 留白=... 异常=...] [--date YYYYMMDD]
        [--trace-status 逐字|重构|缺口] [--dry-run] [--force] [--no-index]

  等价写法（对接 run 目录 / 已合规文件就地登记）:
  python scripts/ingest_asset.py runs/<项目>/refs/场景/S1-青埂峰-阵末空缺-v1.png --run runs/<项目>
        （文件名已合规 → 只补 sidecar 与索引，不改名；未合规时必须给 --kind/--id/--name 才会改名入库）

命名规范（不合规即拒绝入库）:  <类型前缀><ID>-<名称>-<版本或抽次>.<ext>
  例：C11-封肃-主版-v1.jpg / S1-青埂峰-阵末空缺-v1.png
  前缀：角色 C ｜ 道具 Y ｜ 场景 S ｜ 字帖 Z ｜ 故事板 B ｜ 成片 F

配套: scripts/asset_schema.md（规范）· scripts/asset_index.py（索引）· scripts/check_asset_labels.py（门控）
"""
from __future__ import annotations

import argparse
import datetime
import io
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_index as ai  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass


def extract_prompt(prompt_file: str, anchor: str):
    """从项目 prompt 文件里按定位串抽一条 prompt 全文。

    返回 dict(prompt, negative, trace_status, source={file,anchor,line,match})；抽不到返回 None。
    """
    if not prompt_file or not os.path.exists(prompt_file):
        return None
    corpus = ai.PromptCorpus([prompt_file])
    # ① 定位串命中章节（标题或正文）→ 取该节最像 prompt 的块
    for s in corpus.sections:
        if anchor and (anchor in s.heading or anchor in s.text):
            blk = s.best_block()
            if blk:
                return _pack(corpus, s, blk, anchor or s.heading)
    # ② 定位串命中某个块的局部上下文
    for s in corpus.sections:
        for blk in s.candidates():
            if anchor and ai.key_hit(blk.context, anchor):
                return _pack(corpus, s, blk, anchor)
    # ③ 没给定位串 → 全文最大的一块
    if not anchor:
        best = None
        for s in corpus.sections:
            for blk in s.candidates():
                if best is None or len(blk.body) > len(best[1].body):
                    best = (s, blk)
        if best:
            return _pack(corpus, best[0], best[1], "")
    return None


def _pack(corpus, section, blk, anchor):
    prompt, negative = ai.split_negative(blk.body)
    return {
        "prompt": prompt,
        "negative": negative,
        "trace_status": ai.guess_trace(section.text),
        "refs": ai.extract_refs(blk.context + "\n" + blk.body),
        "upload_order": ai.extract_upload_order(blk.context + "\n" + blk.body),
        "rejects": ai.extract_rejects(section.text),
        "tool": ai.guess_tool(section.text),
        "source": {"file": os.path.basename(blk.doc), "path": blk.doc,
                   "anchor": section.heading or anchor, "line": blk.open_line,
                   "match": f"anchor:{anchor or section.heading}", "confidence": "high"},
    }


def parse_refs(items):
    """`@图片1=xxx.jpg` → [{'index':1,'file':...,'order':N}]；items 支持嵌套列表。"""
    flat = []
    for it in items or []:
        flat += it if isinstance(it, (list, tuple)) else [it]
    refs = []
    for it in flat:
        s = str(it).strip().lstrip("@")
        if "=" not in s and "＝" not in s:
            print(f"[warn] --refs 参数「{it}」不是 @图片N=文件名 形式，已忽略")
            continue
        idx, fn = re.split(r"[=＝]", s, maxsplit=1)
        num = "".join(ch for ch in idx if ch.isdigit())
        refs.append({"index": int(num) if num else len(refs) + 1,
                     "file": fn.strip(), "order": len(refs) + 1})
    return sorted(refs, key=lambda r: r["index"])


def parse_vision(items, vision):
    """`构图=… 主体=…` → 填进 vision 字典；返回 (vision, 是否填了任何字段)。"""
    flat = []
    for it in items or []:
        flat += it if isinstance(it, (list, tuple)) else [it]
    for it in flat:
        if "=" in str(it):
            k, v = str(it).split("=", 1)
            if k.strip() in vision:
                vision[k.strip()] = v.strip()
    return vision, any(vision.values())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="ingest_asset.py",
        description="科生·素材入库器：改名入库 + sidecar 标签 + 刷新索引（入库即标签）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例:\n"
               "  python scripts/ingest_asset.py 新图.png --root runs/EP01/refs --kind 角色 --id 11 --name 封肃-主版 \\\n"
               "      --version v1 --prompt-file runs/EP01/m5-OP前置件出图包.md --prompt-anchor \"件 ①-A\" \\\n"
               "      --refs \"@图片1=C1a-士隐-主锚-第1抽.jpeg\" --reuse \"EP01:1-16\" --reject \"\"\n")
    ap.add_argument("src", help="待入库的图/视频文件")
    ap.add_argument("--root", help="素材根目录")
    ap.add_argument("--run", help="runs/<项目> 目录（等价 --root，自动识别其下 refs/assets/素材）")
    ap.add_argument("--kind", choices=list(ai.KIND_PREFIX), help="素材类别（缺省按源文件所在目录/前缀推断）")
    ap.add_argument("--id", dest="aid", help="素材 ID（如 11 / 1a / 9；缺省从源文件名推断）")
    ap.add_argument("--name", help="名称（如 封肃-主版；不得含点号/空格；缺省从源文件名推断）")
    ap.add_argument("--version", help="版本或抽次（如 v1 / 第1抽；缺省 v1）")
    ap.add_argument("--trace-status", dest="trace_status",
                    help="溯源三档：逐字|重构|缺口（也接受 verbatim|reconstructed|missing）")
    ap.add_argument("--verbatim-source", dest="verbatim_source", default="",
                    help="逐字来源凭证（如「m5-素材prompt回贴.md §3 L42 祖本逐字」）。"
                         "**升 trace_status=逐字 必须给本项**：禁伪造逐字红线（见 asset_schema.md §四）")
    ap.add_argument("--prompt-file", help="prompt 来源 md")
    ap.add_argument("--prompt-anchor", default="", help="prompt 定位串（章节标题或正文关键词）")
    ap.add_argument("--prompt", help="直接给 prompt 全文（与 --prompt-file 二选一）")
    ap.add_argument("--negative", help="负面词整串")
    ap.add_argument("--refs", action="append", nargs="+",
                    help="参考挂载，可重复/可并列：--refs \"@图片1=文件名\" 或 --refs \"@图片1=a.jpg\" \"@图片2=b.jpg\"")
    ap.add_argument("--upload-order", default="", help="上传顺序原文")
    ap.add_argument("--reject", default="", help="判废原因（判废件必填）")
    ap.add_argument("--reuse", default="", help="复用记录，如 \"EP01:1-16\"")
    ap.add_argument("--tool", default="", help="出图/生成工具")
    ap.add_argument("--type", default="", help="素材类型：用户输入/模型生成/图生图派生/剪辑产物")
    ap.add_argument("--vision", action="append", nargs="+", default=[],
                    help="视觉标签 k=v（放命令末尾）：--vision 构图=… 主体=… 墨阶=… 留白=… 异常=…")
    ap.add_argument("--date", default="", help="日期 YYYYMMDD（缺省取文件 mtime）")
    ap.add_argument("--ep-tag", default="", help="EP 标记（刷新索引时用）")
    ap.add_argument("--config", help="asset_index.config.json 路径")
    ap.add_argument("--dry-run", action="store_true", help="只打印计划，不落盘")
    ap.add_argument("--force", action="store_true", help="目标已存在时覆盖")
    ap.add_argument("--no-index", action="store_true", help="不刷新全库索引（只写 sidecar）")
    ap.add_argument("--write-sidecars", action="store_true",
                    help="刷新索引时**连全库 sidecar 一起回写**（危险：默认关闭；就地登记只写本件 sidecar）")
    args = ap.parse_args(argv)

    root_arg = args.root or args.run
    if not root_arg:
        print("[FAIL] 缺素材根：给 --root <素材根> 或 --run runs/<项目>")
        return 2
    root, _note = ai.resolve_root(root_arg)
    if not os.path.isdir(root):
        print(f"[FAIL] 素材根不存在：{root}")
        return 2
    if not os.path.isfile(args.src):
        print(f"[FAIL] 源文件不存在：{args.src}")
        return 2

    cfg, _used = ai.load_config(root, args.config)
    src_stem, src_ext = os.path.splitext(os.path.basename(args.src))
    src_ext = src_ext.lower()
    if src_ext not in ai.MEDIA_EXT:
        print(f"[FAIL] 不支持的扩展名「{src_ext}」（图片/视频/音频见 asset_schema.md §2）")
        return 1

    # ---- 参数缺省：已合规文件名可「就地登记」（只补标签不改名）----
    parsed, perr = ai.parse_name(src_stem, cfg.get("version_words") or [])
    in_place = False
    if args.kind is None or args.name is None or args.aid is None:
        if parsed and not args.kind and not args.name and not args.aid and not args.version:
            in_place = True                       # 符合规范 → 就地入库
            args.kind, args.aid = parsed["kind"], parsed["id"]
            args.name, args.version = parsed["name"], parsed["version"]
        elif parsed:
            args.kind = args.kind or parsed["kind"]
            args.aid = args.aid or parsed["id"]
            args.name = args.name or parsed["name"]
            args.version = args.version or parsed["version"]
        else:
            print(f"[拒绝入库] 源文件名「{os.path.basename(args.src)}」不合规（{perr}），"
                  f"且未给 --kind/--id/--name 无法改名")
            print("   规范示例：C11-封肃-主版-v1.jpg / S1-青埂峰-阵末空缺-v1.png")
            return 1
    version = args.version
    if not version:
        tail = src_stem.split("-")[-1]
        version = tail if ai.VERSION_RE.match(tail) else "v1"
    if args.kind not in ai.KIND_PREFIX:
        print(f"[FAIL] 类别「{args.kind}」不在 {list(ai.KIND_PREFIX)}")
        return 1

    kind_dirs = cfg.get("kind_dirs") or ai.KIND_DIR
    subdir = kind_dirs.get(args.kind, args.kind)
    if in_place:
        src_dir_rel = ai.norm_rel(os.path.dirname(os.path.abspath(args.src)), root)
        if src_dir_rel != ".":
            subdir = src_dir_rel
        target_name = os.path.basename(args.src)
    else:
        target_name = f"{ai.KIND_PREFIX[args.kind]}{args.aid}-{args.name}-{version}{src_ext}"
    rel = (subdir.replace("\\", "/").strip("/") + "/" + target_name).lstrip("/")
    naming = ai.check_naming(rel, cfg.get("version_words") or [])

    print("== 素材入库器 ==")
    print(f"   源文件：{args.src}")
    print(f"   类别：{args.kind} → 目录 {subdir}/")
    print(f"   目标名：{target_name}" + ("（已合规，就地登记不改名）" if in_place else ""))
    if not naming["ok"]:
        print(f"\n[拒绝入库] 命名不合规：{naming['error']}")
        print(f"   规范：<类型前缀><ID>-<名称>-<版本或抽次>.<ext>，如 C11-封肃-主版-v1.jpg")
        print(f"   建议：{naming['suggest']}")
        return 1

    # ---- 抽 prompt ----
    info = None
    source_note = ""
    if args.prompt:
        prompt, negative = ai.split_negative(args.prompt)
        info = {"prompt": prompt, "negative": args.negative or negative, "trace_status": "逐字",
                "trace_source": "human",
                "refs": parse_refs(args.refs), "upload_order": args.upload_order, "rejects": args.reject,
                "tool": args.tool,
                "source": {"file": "(--prompt 命令行)", "anchor": "", "line": 0,
                           "match": "inline", "confidence": "high"}}
        source_note = "命令行 --prompt"
    else:
        if not args.prompt_file:
            print("\n[拒绝入库] 缺 prompt 出处：请给 --prompt-file + --prompt-anchor，或直接 --prompt 全文")
            print("   （「入库即标签」不接受无出处的素材；确需占位请显式 --prompt \"⛔缺口：待补\"）")
            return 1
        info = extract_prompt(args.prompt_file, args.prompt_anchor)
        if not info:
            print(f"\n[拒绝入库] 在《{os.path.basename(args.prompt_file)}》里按定位串"
                  f"「{args.prompt_anchor}」找不到 prompt 块")
            print("   排查：① 定位串是否与章节标题/正文一致；② 该处是否有 ``` 围栏块；"
                  "③ 或改直接给 --prompt 全文")
            return 1
        source_note = f"{os.path.basename(args.prompt_file)} L{info['source']['line']}"

    if args.negative:
        info["negative"] = args.negative
    if args.trace_status:
        info["trace_status"] = ai.norm_trace(args.trace_status)
        info["trace_source"] = "human"      # 人写值：合并时以它为准（升逐字另需 verbatim_source）
        # 红线：升「逐字」必须显式给逐字来源凭证，否则拒绝（不得伪造逐字）
        if info["trace_status"] == "逐字" and not args.verbatim_source.strip():
            print("[拒绝入库] trace_status=逐字 必须同时给 --verbatim-source（逐字来源凭证，如"
                  "「m5-素材prompt回贴.md §3 L42 祖本」）——禁伪造逐字红线（见 asset_schema.md §四）。")
            return 1
    if args.refs:
        info["refs"] = parse_refs(args.refs)
    if args.upload_order:
        info["upload_order"] = args.upload_order
    if args.reject:
        info["rejects"] = args.reject
        if not info.get("scrapped"):
            info["scrapped"] = bool(ai.SCRAP_RES and any(p.search(args.reject) for p, _d in ai.SCRAP_RES))
    if not info.get("tool") and args.tool:
        info["tool"] = args.tool

    # ---- 视觉标签 ----
    vision, vision_filled = parse_vision(args.vision, ai.empty_vision())

    dst = os.path.join(root, rel.replace("/", os.sep))
    acts = [f"复制 {os.path.basename(args.src)} → {rel}" if os.path.abspath(dst) != os.path.abspath(args.src)
            else f"就地登记 {rel}（已在位，只补标签）"]
    if not vision_filled:
        acts.append("⚠️ vision 块为空：agent 入库时必须先 read_image 看真图，再补 构图/主体/墨阶/留白/异常")
    if os.path.exists(dst) and os.path.abspath(dst) != os.path.abspath(args.src) and not args.force:
        print(f"\n[拒绝入库] 目标已存在：{rel}（要覆盖请加 --force；要并列请改 --version）")
        return 1
    for a in acts:
        print("   · " + a)
    print(f"   · prompt 来源：{source_note}（{info['trace_status']}，{len(info['prompt'])} 字）")

    if args.dry_run:
        print("\n（--dry-run：未落盘）")
        return 0

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.abspath(dst) != os.path.abspath(args.src):
        shutil.copy2(args.src, dst)
    dims, dims_note = ai.read_dims(dst)
    mtime = os.path.getmtime(dst)
    rec = {
        "file": target_name,
        "rel": rel,
        "dir": subdir.replace("\\", "/").strip("/") or ".",
        "kind": args.kind,
        "media": ai.media_kind_of(src_ext),
        "ext": src_ext,
        "type": args.type or ai.guess_type(rel, target_name, info["prompt"], ai.media_kind_of(src_ext),
                                           cfg.get("type_default", "模型生成")),
        "tool": args.tool or info.get("tool") or cfg.get("tool_default", ""),
        "prompt": info["prompt"],
        "negative": info["negative"],
        "refs": info["refs"] or [],
        "upload_order": info["upload_order"] or "",
        "date": args.date or datetime.datetime.fromtimestamp(mtime).strftime("%Y%m%d"),
        "rejects": info.get("rejects") or "",
        "rejects_source": ("human" if args.reject else
                           ("source" if (info.get("rejects") or "").strip() else "")),
        "scrapped": bool(info.get("scrapped")),
        "reuse": args.reuse or "",
        "trace_status": info["trace_status"],
        "trace_source": info.get("trace_source") or "",
        "vision": vision,
        "vision_filled": vision_filled,
        "sha256": ai.sha256_file(dst),
        "size": os.path.getsize(dst),
        "dims": dims,
        "dims_note": dims_note,
        "prompt_source": info["source"],
        "naming": naming,
        "match_confidence": (info["source"] or {}).get("confidence", "high"),
        "sidecar_path": rel + ai.SIDECAR_SUFFIX,
        "updated_at": ai.now_str(),
    }
    if args.verbatim_source.strip():
        rec["verbatim_source"] = args.verbatim_source.strip()
    old = ai.load_sidecar(dst)
    rec = ai.merge_record(rec, old)
    ai.write_json(ai.sidecar_path(dst), rec)
    print(f"   · 已写入 sidecar：{rel}{ai.SIDECAR_SUFFIX}")

    if not args.no_index:
        base = os.path.dirname(root) if os.path.basename(root) in ("refs", "assets", "素材", "素材库") else root
        argv2 = ["--root", root, "--out", base, "--quiet"]
        # 就地登记只写本件 sidecar；刷新索引**默认不碰其余 sidecar**（禁全量回写覆写 rejects/trace_status）
        if not args.write_sidecars:
            argv2.append("--no-sidecar")
        if args.ep_tag:
            argv2 += ["--ep-tag", args.ep_tag]
        if args.config:
            argv2 += ["--config", args.config]
        print("\n-- 刷新全库索引 --"
              + ("（--no-sidecar：只刷索引，不动其余 sidecar）" if not args.write_sidecars
                 else "（⚠️ --write-sidecars：连全库 sidecar 一起回写）"))
        ai.main(argv2)

    me = os.path.abspath(__file__)
    py = os.path.basename(sys.executable)
    chk = me.replace("ingest_asset.py", "check_asset_labels.py")
    aidx = me.replace("ingest_asset.py", "asset_index.py")
    print("\n== 下一步校验命令 ==")
    print(f"  1) 标签门控：{py} -X utf8 \"{chk}\" \"{root}\"")
    print(f"  2) 双向核对：{py} -X utf8 \"{aidx}\" --root \"{root}\" --check   # 只读，报未登记/断链")
    if args.reuse:
        ep = args.reuse.split(":")[0].strip()
        if ep:
            print(f"  3) 该集复用件复核：{py} -X utf8 \"{chk}\" \"{root}\" --ep {ep}")
    if not vision_filled:
        print(f"  4) 视觉标签未填：先 read_image 看真图，再补 "
              f"--vision 构图=… --vision 主体=… --vision 墨阶=… --vision 留白=… --vision 异常=… 重跑本命令")
    return 0


if __name__ == "__main__":
    sys.exit(main())
