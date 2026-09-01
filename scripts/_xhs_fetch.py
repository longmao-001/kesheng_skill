# -*- coding: utf-8 -*-
"""抓取并解析小红书笔记正文 (仅公开描述文本, 供知识入库)"""
import io
import json
import sys
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

URLS = [
    ("工业产品这么拍", "https://www.xiaohongshu.com/discovery/item/69153230000000000d03c141?source=webshare&xhsshare=pc_web&xsec_token=CBm6c268M7k7qsfxBSGcnneyEzFfSfOkMKd7T2lyCSoys="),
    ("用AI帮老爸公司产品介绍", "https://www.xiaohongshu.com/discovery/item/6a0efb520000000007021ae9?source=webshare&xhsshare=pc_web&xsec_token=CBCsPewXJVTHIowIfY7zwA6DCvpt4WC79_1HNhtf3NfgI="),
    ("三维动画报价案例", "https://xhslink.cn/o/4GPVZJ8nEdv"),
]


def extract_state(html):
    i = html.rfind("window.__INITIAL_STATE__")
    if i < 0:
        return None
    j = html.find("{", i)
    if j < 0:
        return None
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


def main():
    for name, u in URLS:
        try:
            req = urllib.request.Request(u, headers=UA)
            html = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "ignore")
            raw = extract_state(html)
            if not raw:
                print(name, "NO STATE")
                continue
            st = json.loads(raw.replace("undefined", "null"))
            ndm = st.get("note", {}).get("noteDetailMap", {})
            for _k, v in ndm.items():
                n = v.get("note", {})
                print("=====", name, "=====")
                print("title:", n.get("title"))
                print("desc:", (n.get("desc") or "")[:1200])
                print("imgs:", len(n.get("imageList", []) or []), "| type:", n.get("type"))
                print("tags:", [t.get("name") for t in (n.get("tagList") or [])][:8])
        except Exception as ex:  # noqa
            print(name, "ERR", repr(ex)[:160])


if __name__ == "__main__":
    main()
