#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科生·素材标签门控 (check_asset_labels.py) —— 「素材在库、出处也在库」的机器闸

五查一闸:
  ① 双向核对：盘上有而索引无＝未登记；索引有而盘上无＝断链
  ② 每件必须有非空 prompt，或显式 trace_status=重构（重构＝WARN）；**缺口件计入 FAIL 并列出**
  ③ 命名规范校验（<类型前缀><ID>-<名称>-<版本>；存量件可 --naming-warn 降级为 WARN）
  ④ sidecar 与主索引一致（条目齐、sha256/size/prompt/trace_status 不打架）
  ⑤ --ep EPnn 只查该集复用件
  ⑥ 空跑（0 文件且 0 索引）＝ exit 2 —— 空跑不算通过
退出码：FAIL>0 → 1；全过 → 0；空跑 → 2。

用法:
  python scripts/check_asset_labels.py <素材根 或 runs/<项目>> [--root <素材根>]
        [--index <assets_index.json>] [--ep EP01] [--naming-warn] [--require-vision] [--json]

配套: scripts/asset_schema.md（规范）· scripts/asset_index.py（索引）· scripts/ingest_asset.py（入库）
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asset_index as ai  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass


def locate(run_or_root: str, index_arg=None):
    """返回 (素材根, 索引路径)。

    优先级：① --index 指定 → 用它记的 root；② <目标>/assets_index.json 或上一级同名文件 → 用它记的 root；
    ③ 目标下的 refs/assets/素材/素材库 子目录；④ 目标自身。
    """
    p = os.path.abspath(run_or_root)
    cands = ([os.path.abspath(index_arg)] if index_arg else []) + [
        os.path.join(p, ai.INDEX_JSON),
        os.path.join(os.path.dirname(p), ai.INDEX_JSON),
    ]
    for ip in cands:
        if ip and os.path.exists(ip):
            root = None
            try:
                with io.open(ip, "r", encoding="utf-8-sig", errors="ignore") as fh:
                    root = (json.load(fh) or {}).get("root")
            except Exception:  # noqa: BLE001
                root = None
            if root and os.path.isdir(root):
                return os.path.abspath(root), ip
            return p, ip
    for cand in ("refs", "assets", "素材", "素材库"):
        q = os.path.join(p, cand)
        if os.path.isdir(q) and ai.iter_media(q, ai.DEFAULT_INCLUDE, ai.DEFAULT_EXCLUDE_DIRS)[0]:
            return q, os.path.join(p, ai.INDEX_JSON)
    return p, os.path.join(p, ai.INDEX_JSON)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="check_asset_labels.py",
        description="科生·素材标签门控：双向核对 / prompt 缺口 / 命名规范 / sidecar-索引一致",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例:\n"
               "  python scripts/check_asset_labels.py runs/20260915-红楼梦动漫EP01\n"
               "  python scripts/check_asset_labels.py runs/EP01/refs --ep EP01 --naming-warn\n")
    ap.add_argument("target", nargs="?", help="素材根目录 或 runs/<项目>")
    ap.add_argument("--root", help="素材根目录（显式指定）")
    ap.add_argument("--index", help="assets_index.json 路径")
    ap.add_argument("--ep", help="只查某集复用件（如 EP01；读 sidecar.reuse）")
    ap.add_argument("--naming-warn", action="store_true", help="命名不合规只报 WARN（存量库过渡期用）")
    ap.add_argument("--require-vision", action="store_true", help="vision 块未填也算 FAIL")
    ap.add_argument("--json", action="store_true", dest="as_json", help="输出机器可读 JSON")
    args = ap.parse_args(argv)

    target = args.root or args.target
    if not target:
        ap.print_help()
        return 2
    if not os.path.isdir(target):
        print(f"[FAIL] 目录不存在：{target}")
        return 2
    root, index_path = locate(target, args.index)

    fails, warns, notes = [], [], []
    include = ai.DEFAULT_INCLUDE
    exclude = ai.DEFAULT_EXCLUDE_DIRS
    files, dropped = ai.iter_media(root, include, exclude)
    disk = {ai.norm_rel(p, root): p for p in files}

    index = None
    if os.path.exists(index_path):
        try:
            with io.open(index_path, "r", encoding="utf-8-sig", errors="ignore") as fh:
                index = json.load(fh)
        except Exception as e:  # noqa: BLE001
            fails.append(("索引", f"assets_index.json 解析失败：{e}"))
    idx_assets = {a.get("rel", ""): a for a in (index or {}).get("assets", [])}
    idx_conf = {a.get("rel", ""): a.get("match_confidence") for a in (index or {}).get("assets", [])}

    # ⑥ 空跑：0 文件且 0 索引 → exit 2
    if not disk and not idx_assets:
        print(f"== 素材标签门控：{os.path.basename(os.path.abspath(root))} ==")
        print(f"   素材根：{root}")
        print("[空跑] 0 个在册媒体文件、0 条索引记录 —— 无素材可查，空跑不算通过（exit 2）")
        print("       提示：确认 --root 是否指到素材根；或先用 asset_index.py 生成索引。")
        return 2

    if index is None:
        fails.append(("索引", f"缺 {ai.INDEX_JSON}（{index_path}）—— 先跑 asset_index.py 生成索引，门控才能核对"))

    # ⑤ --ep 过滤：只查该集复用件
    ep = (args.ep or "").strip()
    if ep:
        scope = {r: a for r, a in idx_assets.items()
                 if ep.lower() in (a.get("reuse") or "").lower()}
        if not scope:
            print(f"== 素材标签门控（--ep {ep}）==")
            print(f"[空跑] 没有任何素材登记复用集「{ep}」——空跑不算通过（exit 2）")
            print("       提示：入库时用 ingest_asset.py --reuse \"EP01:1-16\" 写复用，"
                  "或确认 asset_index.py --ep-tag 是否正确。")
            return 2
        target_rel = set(scope)
    else:
        target_rel = set(disk) | set(idx_assets)

    # ① 双向核对（orphan＝未登记；ghost＝断链）
    unregistered = sorted(set(disk) - set(idx_assets)) if index is not None else sorted(disk)
    broken = sorted(set(idx_assets) - set(disk))
    for r in unregistered:
        if not ep or r in target_rel:
            fails.append(("未登记", f"{r}（orphan：盘上有、索引无）→ 跑 asset_index.py 重建索引，或 ingest_asset.py 补入库"))
    for r in broken:
        if not ep or r in target_rel:
            fails.append(("断链", f"{r}（ghost：索引有、盘上无）→ 索引过时或文件被移走，跑 asset_index.py --check 定位"))

    # 按目录分组统计
    groups = {}
    examined = 0
    for rel in sorted(target_rel):
        d = os.path.dirname(rel) or "."
        g = groups.setdefault(d, {"ok": 0, "fail": 0, "warn": 0, "lines": []})
        a = idx_assets.get(rel)
        if a is None:
            g["fail"] += 1
            g["lines"].append(f"❌ {rel}：未登记（orphan：盘上有、索引无）")
            continue
        examined += 1
        row_fail, row_warn = [], []

        # ② prompt / trace_status
        if ai.is_gap(a):
            why = "无 prompt" if not (a.get("prompt") or "").strip() else "显式 trace_status=缺口"
            row_fail.append(f"⛔缺口（{why}）→ 补 prompt 后重跑 asset_index.py")
        elif a.get("trace_status") == "重构":
            row_warn.append("⚠️重构（候选全文，出图前须过目）")

        # ③ 命名规范
        if not a.get("naming", {}).get("ok"):
            sug = (a.get("naming") or {}).get("suggest") or ""
            msg = f"命名不合规：{(a.get('naming') or {}).get('error', '')}" + (f" → 建议 {sug}" if sug else "")
            (row_warn if args.naming_warn else row_fail).append("🏷 " + msg)

        # ④ sidecar 与主索引一致
        side = ai.load_sidecar(disk[rel]) if rel in disk else {}
        if rel in disk:
            if not side:
                row_fail.append(f"缺 sidecar（{a.get('sidecar_path', rel + ai.SIDECAR_SUFFIX)}）→ 重跑 asset_index.py")
            elif side.get("_parse_error"):
                row_fail.append("sidecar JSON 解析失败 → 删除该 .label.json 后重建索引")
            else:
                for k in ("sha256", "size"):
                    if side.get(k) != a.get(k):
                        row_fail.append(f"sidecar.{k} 与主索引不一致 → 重跑 asset_index.py")
                        break
                if (side.get("prompt") or "") != (a.get("prompt") or ""):
                    row_fail.append("sidecar.prompt 与主索引不一致 → 重跑 asset_index.py（以 sidecar 为准请先确认）")
                if (side.get("trace_status") or "") != (a.get("trace_status") or ""):
                    row_warn.append("sidecar.trace_status 与主索引不一致 → 重跑 asset_index.py")

        # vision（agent 入库必须 read_image 后填）
        if not any((a.get("vision") or {}).values()):
            (row_fail if args.require_vision else row_warn).append("👁 vision 未填（构图/主体/墨阶/留白/异常）")

        if a.get("match_confidence") == "low":
            row_warn.append("🔎 低置信匹配（来源须人工确认）")

        if row_fail:
            g["fail"] += 1
            fails.append((d, f"{rel}：" + "；".join(row_fail)))
        if row_warn:
            g["warn"] += 1
            warns.append((d, f"{rel}：" + "；".join(row_warn)))
        g["lines"].append(("❌ " if row_fail else ("⚠️ " if row_warn else "✅ "))
                          + "；".join(row_fail + row_warn) if (row_fail or row_warn) else "✅")
        if not row_fail:
            g["ok"] += 1

    counts = (index or {}).get("counts", {})
    n_fail = sum(1 for _d, _m in fails if _d not in ("索引",))
    result = {
        "root": root,
        "index": index_path,
        "ep": ep,
        "examined": examined,
        "disk": len(disk),
        "indexed": len(idx_assets),
        "excluded": len(dropped),
        "fails": len(fails),
        "warns": len(warns),
        "unregistered": len(unregistered),
        "broken": len(broken),
        "gaps": counts.get("缺口"),
        "exit": None,
    }
    if args.as_json:
        result["exit"] = 1 if fails else 0
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return result["exit"]

    print(f"== 素材标签门控：{os.path.basename(os.path.abspath(root))} ==")
    print(f"   素材根：{root}")
    print(f"   索引：{index_path}" + ("（存在）" if index is not None else "（缺失）"))
    print(f"   在册：盘上 {len(disk)} 件 / 索引 {len(idx_assets)} 件 / 排除 {len(dropped)} 件"
          + (f"；本闸范围（--ep {ep}）{len(target_rel)} 件" if ep else ""))
    if dropped:
        print(f"   （已排除目录：{'、'.join(sorted({d['reason'].replace('排除目录 ', '') for d in dropped}))}）")
    print("")
    for d in sorted(groups):
        g = groups[d]
        print(f"[{d}]  ✅{g['ok']}  ❌{g['fail']}  ⚠️{g['warn']}")
        for ln in g["lines"]:
            print(f"    {ln}")
    print("")
    if warns:
        print(f"-- WARN {len(warns)} 条（不阻断，但请排期处理）--")
        for d, m in warns[:20]:
            print(f"  ⚠️ [{d}] {m}")
        if len(warns) > 20:
            print(f"  … 另 {len(warns) - 20} 条")
        print("")
    if fails:
        print(f"-- FAIL {len(fails)} 条 --")
        for d, m in fails[:40]:
            print(f"  ❌ [{d}] {m}")
        if len(fails) > 40:
            print(f"  … 另 {len(fails) - 40} 条")
        print("")
    gaps = [r for r, a in idx_assets.items() if ai.is_gap(a) and (not ep or r in target_rel)]
    if gaps:
        print(f"-- 缺口件（{len(gaps)}，必须补 prompt 或明确授权，不得沉默通过）--")
        for r in sorted(gaps)[:40]:
            print(f"  ⛔ {r}")
        print("")
    print(f"汇总：检查 {examined} 件 ｜ FAIL {len(fails)} ｜ WARN {len(warns)} ｜ "
          f"未登记 {len(unregistered)} ｜ 断链 {len(broken)} ｜ 缺口 {len(gaps)}"
          + (f" ｜ --ep {ep}" if ep else ""))
    if fails:
        print("结论：FAIL —— 素材标签门控未过（缺口件计入 FAIL；修复后重跑 asset_index.py 再本命令）")
        return 1
    print("结论：PASS —— 每件都有出处，索引与磁盘一致 ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
