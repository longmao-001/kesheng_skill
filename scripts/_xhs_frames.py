# -*- coding: utf-8 -*-
"""用 cv2 抽取小红书视频关键帧(均匀12帧, 宽720) 供视觉审阅"""
import io
import os
import sys

import cv2

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

MEDIA = r"F:/AI/kesheng/_media"
OUTD = os.path.join(MEDIA, "frames")
os.makedirs(OUTD, exist_ok=True)

for tag in ("gongye-pai", "jingcheng-gaobang"):
    vp = os.path.join(MEDIA, tag + "-v0.mp4")
    if not os.path.exists(vp):
        print("skip", tag)
        continue
    cap = cv2.VideoCapture(vp)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    dur = n / fps if fps else 0
    print(f"{tag}: frames={n} fps={fps:.2f} dur={dur:.1f}s")
    idxs = [int(i * (n - 1) / 11) for i in range(12)]
    for j, fi in enumerate(idxs):
        cap.set(cv2.CAP_PROP_POS_FRAMES, fi)
        ok, fr = cap.read()
        if not ok:
            continue
        h, w = fr.shape[:2]
        nw = 720
        nh = int(h * nw / w)
        fr = cv2.resize(fr, (nw, nh))
        outp = os.path.join(OUTD, f"{tag}-f{j:02d}.jpg")
        cv2.imwrite(outp, fr, [cv2.IMWRITE_JPEG_QUALITY, 80])
    cap.release()
    print("frames saved:", len(idxs))
print("done")
