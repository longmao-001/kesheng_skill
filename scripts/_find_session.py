# -*- coding: utf-8 -*-
"""在会话存档中检索包含 PHO-SC-4 项目对话的会话文件"""
import io
import os
import sys
from datetime import datetime

import zstandard as zstd

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

SESS = r"C:/Users/Win10/.dsh/sessions/--F-AI-DS~0020harness--"
KEYS = [b"phosc4", b"pho-sc4", b"20260830-pho", "\u73cd\u5fc3".encode("utf-8"), b"juexin"]

start = datetime(2026, 8, 29)
end = datetime(2026, 9, 3)
hits = []
for d in os.listdir(SESS):
    full = os.path.join(SESS, d)
    if not os.path.isdir(full):
        continue
    p = os.path.join(full, "session.jsonl.zstd")
    if not os.path.exists(p):
        continue
    mtime = datetime.fromtimestamp(os.path.getmtime(full))
    if not (start <= mtime <= end):
        continue
    try:
        with open(p, "rb") as f:
            data = zstd.ZstdDecompressor().decompress(f.read(), max_output_size=200 * 1024 * 1024)
    except Exception as ex:
        continue
    for k in KEYS:
        if k in data:
            hits.append((d, mtime, len(data), k.decode("utf-8", "ignore")))
            break

for h in hits:
    print("HIT:", h[0], "|", h[1], "| decompressed", h[2], "bytes | key:", h[3])
if not hits:
    print("no hits")
print("scanned dirs in window:", sum(1 for d in os.listdir(SESS) if os.path.isdir(os.path.join(SESS, d)) and start <= datetime.fromtimestamp(os.path.getmtime(os.path.join(SESS, d))) <= end))
