# -*- coding: utf-8 -*-
"""图谱补: 图文对位硬检查项 + 五层检查体系关系"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

P = r"F:/AI/kesheng/packs/sop-seed/kg.json"
g = json.load(open(P, encoding="utf-8-sig"))
ids = {e["id"] for e in g["entities"]}
if "Rule:图文对位" not in ids:
    g["entities"].append({
        "id": "Rule:图文对位", "type": "Rule", "name": "图文对位(重点检查项)",
        "props": {"铁则": "每镜: 口播内容 ↔ 画面描述 ↔ 参考图/首帧 三者必须对位——口播讲的对象/动作/状态必须在参考图中体现或可靠衍生",
                  "反例": "口播讲'光带扫过控制器→灯室', 参考图只有控制器; 口播讲'风冷散热', 画面是封装外观",
                  "检查": "check_prompt_sheet R12(机器粗检: 口播↔画面共现词, 提示不阻断) + L2检察官人工硬查(逐镜对位, 违者打回分镜师/prompt工程师)",
                  "打回": "图文脱节=打回(再好看的画面对不上旁白没用)"},
        "sources": ["templates/storyboard.md", "agents/inspector.md"]})
KEYS = {(r["source"], r["target"], r["type"]) for r in g["relations"]}
for s, t, ty in [
    ("Rule:图文对位", "Rule:五层检查体系", "check-in-L2"),
    ("Rule:图文对位", "ProcessRule:参考包组装", "rule-governs"),
    ("Rule:图文对位", "KspStep:KSP-05分镜执行", "rule-governs"),
]:
    if (s, t, ty) not in KEYS:
        g["relations"].append({"source": s, "target": t, "type": ty, "props": {}})
        KEYS.add((s, t, ty))
json.dump(g, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("图文对位 rule added")
