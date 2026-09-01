# -*- coding: utf-8 -*-
"""全量检索: 所有 profile 会话 + Claude Code 项目记录 是否含 PHO-SC-4"""
import io
import os
import sys

import zstandard as zstd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ROOTS = [
    r"C:/Users/Win10/.dsh/sessions",
    r"C:/Users/Win10/.claude/projects",
]
KEYS = [b"phosc4", b"pho-sc4", b"20260830-pho", b"juexin", "\u73cd\u5fc3".encode("utf-8")]

def scan_file(p):
    blob = None
    if p.endswith(".zstd"):
        try:
            with open(p, "rb") as f:
                blob = zstd.ZstdDecompressor().decompress(f.read(), max_output_size=300 * 1024 * 1024)
        except Exception:
            return None
    else:
        try:
            blob = open(p, "rb").read(300 * 1024 * 1024)
        except Exception:
            return None
    for k in KEYS:
        if blob and k in blob:
            return k.decode("utf-8", "ignore")
    return None

count = 0
for root in ROOTS:
    if not os.path.isdir(root):
        print("no dir:", root)
        continue
    for dirpath, _d, files in os.walk(root):
        for fn in files:
            if fn in ("session.jsonl.zstd",) or fn.endswith(".jsonl"):
                p = os.path.join(dirpath, fn)
                count += 1
                k = scan_file(p)
                if k:
                    print("HIT:", p, "| key:", k)
print("scanned files:", count)
