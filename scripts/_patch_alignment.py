# -*- coding: utf-8 -*-
"""图谱补 KSP-03.5(主题共识+内容重点) 步骤与拍板点"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# --- sop-seed: KSP-03.5 ---
P1 = r"F:/AI/kesheng/packs/sop-seed/kg.json"
g1 = json.load(open(P1, encoding="utf-8-sig"))
ids1 = {e["id"] for e in g1["entities"]}
if "KspStep:KSP-03.5主题共识" not in ids1:
    g1["entities"].append({
        "id": "KspStep:KSP-03.5主题共识", "type": "KspStep", "name": "KSP-03.5 主题共识+内容重点对齐",
        "props": {"动作": "一句话主体共识(用户确认/纠偏)→内容重点清单3-8条逐条讨论→重点圈选(多选)→重点协议落brief(权重×证据×镜头预算)",
                  "用户角色": "讨论+重点圈选(多选), 侧重点加强", "门控": "主体共识+重点协议获确认",
                  "产出": "主体共识卡+内容重点协议", "规范": "docs/USER_SOP.md §KSP-03.5"},
        "sources": ["docs/USER_SOP.md", "templates/brief.md"]})
KEYS1 = {(r["source"], r["target"], r["type"]) for r in g1["relations"]}
for s, t, ty in [
    ("KspStep:KSP-04方案对抗", "KspStep:KSP-03.5主题共识", "ksp-after-gate"),
]:
    if (s, t, ty) not in KEYS1:
        g1["relations"].append({"source": s, "target": t, "type": ty, "props": {}})
json.dump(g1, open(P1, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# --- gate-seed: 内容重点多选拍板 ---
P2 = r"F:/AI/kesheng/packs/gate-seed/kg.json"
g2 = json.load(open(P2, encoding="utf-8-sig"))
ids2 = {e["id"] for e in g2["entities"]}
if "UserGate:内容重点对齐" not in ids2:
    g2["entities"].append({
        "id": "UserGate:内容重点对齐", "type": "UserGate", "name": "内容重点圈选(多选)",
        "props": {"里程碑": "KSP-03.5", "问题": "视频讲什么、重点讲哪几条——与用户讨论后圈选侧重点",
                  "选项": "候选重点清单多选(可追加补充条目); P0=加强/未选=弱化/指名删除", "推荐": "按用户侧重",
                  "依据": "templates/user-gate.md #17"},
        "sources": ["templates/user-gate.md", "templates/brief.md"]})
KEYS2 = {(r["source"], r["target"], r["type"]) for r in g2["relations"]}
for s, t, ty in [
    ("UserGate:内容重点对齐", "RoleWorkflow:制片人", "gate-in"),
    ("UserGate:内容重点对齐", "RoleWorkflow:导演", "gate-in"),
    ("UserGate:内容重点对齐", "ProcessRule:质量门控", "gate-checks"),
]:
    if (s, t, ty) not in KEYS2:
        g2["relations"].append({"source": s, "target": t, "type": ty, "props": {}})
json.dump(g2, open(P2, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("sop-seed/gate-seed patched")
