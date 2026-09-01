# -*- coding: utf-8 -*-
"""图谱补: 调研图料三件套规则(科学道理+网图+素材图, 好好用上)"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

P = r"F:/AI/kesheng/packs/sop-seed/kg.json"
g = json.load(open(P, encoding="utf-8-sig"))
ids = {e["id"] for e in g["entities"]}
if "Rule:调研图料三件套" not in ids:
    g["entities"].append({
        "id": "Rule:调研图料三件套", "type": "Rule", "name": "调研图料三件套",
        "props": {"三件": "①科学道理(原理/公式/示意→理解报告+图谱) ②网图(公开示意图/结构/场景→入库refs/标来源版权, 无授权仅参考不入镜) ③素材图(客户全量收集→分级: 直接入镜/参考图/内容参考)",
                  "图库": "runs/<slug>/refs/ + assets-inventory.md(每张: 来源/版权/用途等级)",
                  "使用纪律": "分镜/参考包/九宫格/首帧必须先由图库挑(逐镜问: 图库有没有能用的); 有素材镜头不靠AI凭空生成",
                  "红线": "无授权网图绝不入镜(只作构图/结构/演示参考); 客户敏感页不入库"},
        "sources": ["docs/USER_SOP.md", "playbooks/production-workflow.md"]})
KEYS = {(r["source"], r["target"], r["type"]) for r in g["relations"]}
for s, t, ty in [
    ("Rule:调研图料三件套", "KspStep:KSP-03科学理解", "rule-governs"),
    ("Rule:调研图料三件套", "ProcessRule:素材库建库（PDF-PPT抠图）", "rule-serves"),
    ("Rule:调研图料三件套", "ProcessRule:参考包组装", "rule-serves"),
]:
    if (s, t, ty) not in KEYS:
        g["relations"].append({"source": s, "target": t, "type": ty, "props": {}})
json.dump(g, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("调研图料三件套 rule added")
