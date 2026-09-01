# -*- coding: utf-8 -*-
"""图谱补: 检察官角色流程 + 与五层检查连线"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

P = r"F:/AI/kesheng/packs/workflow-seed/kg.json"
g = json.load(open(P, encoding="utf-8-sig"))
ids = {e["id"] for e in g["entities"]}
if "RoleWorkflow:检察官" not in ids:
    g["entities"].append({
        "id": "RoleWorkflow:检察官", "type": "RoleWorkflow", "name": "检察官工作流程",
        "props": {"阶段": "交付前(L1-L4.5), 闸点触发", "触发": "交付前检查",
                  "步骤": "素材检查(L1)→prompt检查(L2)→事实检查(L3)→出口评分(L4)→总汇总裁决书(L4.5)→交用户签收(L5)",
                  "纪律": "独立上下文只看证据不听辩护; 每条结论引证据; 给推翻条件; 抽查即全查; 发现问题打回对应角色不代修",
                  "产出": "L1-L4检查报告 + 检查裁决书(三态+各层评分+打回清单)"},
        "sources": ["agents/inspector.md", "docs/USER_SOP.md"]})
KEYS = {(r["source"], r["target"], r["type"]) for r in g["relations"]}
for s, t, ty in [
    ("RoleWorkflow:检察官", "Rule:五层检查体系", "rule-empowers"),
    ("RoleWorkflow:检察官", "KspStep:KSP-06制作交付", "workflow-gates"),
]:
    if (s, t, ty) not in KEYS:
        g["relations"].append({"source": s, "target": t, "type": ty, "props": {}})
        KEYS.add((s, t, ty))
json.dump(g, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("检察官 role added")
