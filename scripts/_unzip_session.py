# -*- coding: utf-8 -*-
"""解压 DSH session 导出 zip, 找主会话 + 子agent会话文件"""
import io
import os
import sys
import zipfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ZIP = r"C:/Users/Win10/Downloads/dsh-session-session-774f5b97-bb33-42f1-8e3e-22cf2062e702.zip"
DST = r"F:/AI/kesheng/runs/_tmp-session-774f5b97"

z = zipfile.ZipFile(ZIP)
print("zip entries:", len(z.namelist()))
for n in z.namelist()[:60]:
    print(" ", n, "|", z.getinfo(n).file_size)
print("--- 提取主会话/全部 jsonl(.zstd) ---")
for n in z.namelist():
    if n.endswith(".jsonl") or n.endswith(".zstd") or n.endswith(".json"):
        out = os.path.join(DST, n.replace("../", "").replace("\\", "/"))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "wb") as f:
            f.write(z.read(n))
        print("extracted:", out, os.path.getsize(out))
