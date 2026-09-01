# -*- coding: utf-8 -*-
"""DSH session.jsonl → 分离: 真人用户消息 / 助手文本 / 子agent通知"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

P = r"F:/AI/kesheng/runs/_tmp-session-774f5b97/session.jsonl"
DIR = r"F:/AI/kesheng/runs/_tmp-session-774f5b97"


def text_of(content):
    if isinstance(content, str):
        return content
    parts = []
    if isinstance(content, list):
        for b in content:
            if isinstance(b, dict):
                t = b.get("type")
                if t == "text":
                    parts.append(b.get("text", ""))
                elif t == "tool_use":
                    parts.append(f"[tool:{b.get('name')}]")
    return "\n".join(x for x in parts if x)


NOISE = ("Background subagent", "Current runtime context", "<system-reminder", "<available_skills",
         "The approval policy changed", "Background subagent ")

hum, ast, sub = [], [], []
with open(P, encoding="utf-8") as f:
    for ln in f:
        ln = ln.strip()
        if not ln:
            continue
        try:
            o = json.loads(ln)
        except Exception:
            continue
        t = o.get("type")
        if t == "user/message":
            d = o.get("data") or {}
            txt = text_of(d.get("content")).strip()
            if not txt:
                continue
            if txt.startswith(NOISE) or any(txt.startswith(n) for n in ("Current runtime", "<system")):
                sub.append(txt)
            else:
                hum.append(txt)
        elif t == "assistant/message":
            d = o.get("data") or {}
            txt = text_of(d.get("content")).strip()
            if txt and "[tool:" not in txt:
                ast.append(txt)

def dump(path, rows, title):
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {title} · {len(rows)} 条\n\n")
        for i, t in enumerate(rows):
            f.write(f"\n--- [{i}] ---\n{t}\n")

dump(DIR + "/USER.md", hum, "真人用户消息")
dump(DIR + "/ASSISTANT.md", ast, "助手文本消息")
dump(DIR + "/NOTICES.md", sub, "子agent/系统通知")
print("human:", len(hum), "| assistant:", len(ast), "| notices:", len(sub))
print("human 消息前 200 字预览:")
for i, h in enumerate(hum[:20]):
    print(f"  [{i}] {h[:80].replace(chr(10),' ')}")
