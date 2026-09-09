#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
素材包完整性校验 (check_asset_pack.py) —— "零意外"机器强制

用法: python -X utf8 scripts/check_asset_pack.py <runs/<项目>>
目的：交付件自包含 —— prompts 里引用的每个参考图/视频都在 assets-inventory.md 中登记，
     且无"待补充/补拍/自己找"等后补提示词。兼容新旧两代参考图语法：
  A) 旧：@图片N/@视频N/@音频N（位置编号）
  B) 新：@图NN=<文件名> 或 @图NN=文件名主体（命名对应；prompt 头「> 参考资产：」建映射）

判定：
  SELF FAIL = 交付文档出现后补提示词（待补充/补拍/自己找…）
  REF  FAIL = prompts 中某个 @图NN/@图片N 引用，无法解析到 inventory 登记的文件名主体
  (来源/授权列由人工 + 授权清单把关；此处只保"引用可解析 + 自包含"。)
"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

FORBID = ["待补充", "补拍", "需要你", "自己找", "找一下", "拍一张", "拍个照", "后期补素材",
          "未准备素材", "你提供一下", "待提供素材", "缺素材", "还需提供", "你来提供"]
REF = re.compile(r"@(?:图|图片|视频|音频)(\d+)")


def _root(seg):
    """取文件名主体：去'=别名'、'（用途）'、扩展名、尾随空白/分隔。"""
    seg = seg.split("=", 1)[-1]
    seg = re.split(r"[（(]", seg, maxsplit=1)[0].strip()
    seg = re.split(r"[\s，。/]", seg, maxsplit=1)[0].strip()
    if seg.lower().endswith((".png", ".jpg", ".jpeg", ".mp4", ".gif", ".webp")):
        seg = seg.rsplit(".", 1)[0]
    return seg


def main():
    run_dir = sys.argv[1] if len(sys.argv) > 1 else None
    if not run_dir or not os.path.isdir(run_dir):
        print("用法: check_asset_pack.py <runs/<项目>>")
        sys.exit(2)
    issues = []

    # SELF. 后补提示词（排除 gate/check 评审件自身——他们评的是别的文件，允许提"建议补"）
    for root, _d, files in os.walk(run_dir):
        for f in files:
            if not (f.endswith(".md") or f.endswith(".txt")):
                continue
            if "check" in f.lower():
                continue
            low = f.lower()
            if "gate-red" in low or "评审单" in f or "recheck" in low or "红队" in f:
                continue
            txt = open(os.path.join(root, f), encoding="utf-8-sig", errors="ignore").read()
            for kw in FORBID:
                if kw in txt:
                    issues.append(f"SELF FAIL [{f}]: 交付件出现后补提示词「{kw}」——必须自包含")

    # inventory 登记文件名主体集合（兼容：反引号文件名 + 裸 ID 首列）
    inv_path = os.path.join(run_dir, "assets-inventory.md")
    inv_txt = open(inv_path, encoding="utf-8-sig", errors="ignore").read() if os.path.exists(inv_path) else ""
    inv_roots = set()
    for m in re.finditer(r"`([^`|]+)`", inv_txt):
        r = _root(m.group(1))
        if r:
            inv_roots.add(r)
    for m in re.finditer(r"(?:^|\||\s|,)((?:IN|RF|REF|CT|OUT|AO|POV|SCENE|MAIN|PART|STR|DATA|BRAND|RAW)_[A-Za-z0-9_\u4e00-\u9fa5]+)", inv_txt):
        inv_roots.add(m.group(1))
    old_ids = {a + b for a, b in re.findall(r"@(?:图片|视频|音频)(\d+)", inv_txt)}

    # 通用文件名探测：从某行引用之后提取文件名 token（=后 / 反引号 / 相邻 裸ID）
    def fn_after(line, ref_tok):
        idx = line.find(ref_tok)
        seg = line[idx + len(ref_tok):]
        for pat in (r"=\s*([A-Za-z0-9_\u4e00-\u9fa5./\-]+)", r"`([^`]+)`",
                    r"(IN|RF|REF|CT|OUT|AO|POV|SCENE|MAIN|PART|STR|DATA|BRAND|RAW)_[A-Za-z0-9_\u4e00-\u9fa5]+"):
            m = re.search(pat, seg)
            if m:
                return _root(m.group(1))
        return None

    # 别名是否为"生成规格"（结构可视化首帧/图表层重建/科学顾问出图/无实拍）——自包含，不作缺失判定
    GEN_SPEC = re.compile(r"首帧|结构可视化|图表层|图表|生成|无实拍|科学顾问|示意图|示意|再生成|重建")

    REF = re.compile(r"@(?:图片|图|视频|音频)(\d+)")
    md = os.path.join(run_dir, "m4-prompts")
    if os.path.isdir(md):
        for f in sorted(os.listdir(md)):
            if not f.startswith("prompts-") or not f.endswith(".md"):
                continue
            full = open(os.path.join(md, f), encoding="utf-8-sig", errors="ignore").read()
            # 全文件别名表（键归一为去前导0）；同名列=材料名
            alias_map = {}
            for line in full.splitlines():
                for m in re.finditer(r"@(?:图片|图|视频|音频)(\d+)", line):
                    found = fn_after(line, m.group(0))
                    if found:
                        alias_map[str(int(m.group(1)))] = found
            for m in REF.finditer(full):
                key = str(int(m.group(1)))
                if key in old_ids:
                    continue
                ref_tok = m.group(0)
                _line = next((ln for ln in full.splitlines() if ref_tok in ln), None)
                # 别名宣告行为"生成规格"（结构可视化首帧/图表层重建/示意/无实拍）→ 自包含(科学顾问出图)，不作缺失判定
                if _line and GEN_SPEC.search(_line):
                    continue
                found = fn_after(_line, ref_tok) if _line else None
                if not found:
                    found = alias_map.get(key)
                if found and (found in inv_roots or any(found in r or r in found for r in inv_roots)):
                    continue
                issues.append(f"REF FAIL [{f}]: {ref_tok} 引用未在 inventory 登记(缺素材/未入库)")

    if issues:
        print(f"== 素材包校验 FAIL ({len(issues)} 条) ==")
        for x in issues[:40]:
            print(" -", x)
        if len(issues) > 40:
            print(f"   ... 共 {len(issues)} 条")
        sys.exit(1)
    print(f"== 素材包校验 PASS: 自包含确认, 引用全部可解析(新旧语法兼容), 无后补提示 ==")


if __name__ == "__main__":
    main()
