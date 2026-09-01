# -*- coding: utf-8 -*-
"""抓取小红书笔记视频+封面: 解析__INITIAL_STATE__中的视频流URL并下载(封面+视频)"""
import io
import json
import os
import re
import sys
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://www.xiaohongshu.com/",
}

URLS = [
    ("gongye-pai", "https://www.xiaohongshu.com/discovery/item/69153230000000000d03c141?source=webshare&xhsshare=pc_web&xsec_token=CBm6c268M7k7qsfxBSGcnneyEzFfSfOkMKd7T2lyCSoys="),
    ("jingcheng-gaobang", "https://www.xiaohongshu.com/discovery/item/6a0efb520000000007021ae9?source=webshare&xhsshare=pc_web&xsec_token=CBCsPewXJVTHIowIfY7zwA6DCvpt4WC79_1HNhtf3NfgI="),
]

OUT = r"F:/AI/kesheng/_media"
os.makedirs(OUT, exist_ok=True)


def extract_state(html):
    i = html.rfind("window.__INITIAL_STATE__")
    if i < 0:
        return None
    j = html.find("{", i)
    depth = 0
    in_str = False
    esc = False
    k = j
    while k < len(html):
        c = html[k]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return html[j:k + 1]
        k += 1
    return None


def find_video_urls(note):
    """从 note.video.media.stream 收集候选 mp4 URL"""
    cands = []
    vid = note.get("video", {})
    md = vid.get("media", {})
    stream = md.get("stream", {})
    for codec in ("h264", "h265", "av1"):
        items = stream.get(codec) or []
        if isinstance(items, dict):
            items = [items]
        for it in items:
            if isinstance(it, dict):
                u = it.get("masterUrl") or it.get("masterUrlList") or it.get("url")
                if isinstance(u, str):
                    cands.append(u)
                for bu in it.get("backupUrls", []) or []:
                    if isinstance(bu, str):
                        cands.append(bu)
    consumer = vid.get("consumer", {})
    for k in ("originVideoKey", "originVideoUrl", "originVideoId"):
        v = consumer.get(k)
        if isinstance(v, str) and v.startswith("http"):
            cands.append(v)
    return cands


def find_cover(note):
    imgs = note.get("imageList") or []
    if not imgs:
        return None
    return imgs[0].get("urlDefault") or imgs[0].get("url") or imgs[0].get("urlPre")


def download(url, path):
    try:
        req = urllib.request.Request(url, headers=UA)
        data = urllib.request.urlopen(req, timeout=60).read()
        with open(path, "wb") as f:
            f.write(data)
        return len(data)
    except Exception as ex:
        print("  dl err:", repr(ex)[:120])
        return 0


def main():
    for tag, u in URLS:
        try:
            req = urllib.request.Request(u, headers=UA)
            html = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "ignore")
            raw = extract_state(html)
            st = json.loads(raw.replace("undefined", "null"))
            ndm = st.get("note", {}).get("noteDetailMap", {})
            for _k, v in ndm.items():
                n = v.get("note", {})
                cov = find_cover(n)
                print("=====", tag, "=====")
                print("videoType:", n.get("type"), "| duration0:", n.get("video", {}).get("media", {}).get("duration"))
                if cov:
                    p = os.path.join(OUT, tag + "-cover.jpg")
                    size = download(cov, p)
                    print("cover:", p, size)
                cands = find_video_urls(n)
                print("video candidates:", cands[:3])
                for i, cu in enumerate(cands[:2]):
                    p = os.path.join(OUT, tag + f"-v{i}.mp4")
                    size = download(cu, p)
                    if size > 4096:
                        print("video saved:", p, size)
                        break
        except Exception as ex:
            print(tag, "ERR", repr(ex)[:160])


if __name__ == "__main__":
    main()
