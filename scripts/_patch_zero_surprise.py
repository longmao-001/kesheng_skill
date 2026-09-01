# -*- coding: utf-8 -*-
"""图谱补: 零意外·素材自包含 + 五层检查体系"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

P = r"F:/AI/kesheng/packs/sop-seed/kg.json"
g = json.load(open(P, encoding="utf-8-sig"))
ids = {e["id"] for e in g["entities"]}
if "Rule:零意外素材自包含" not in ids:
    g["entities"].append({
        "id": "Rule:零意外素材自包含", "type": "Rule", "name": "零意外素材自包含",
        "props": {"铁则": "交付件自包含: 所有画面素材要么①已下载入包(含来源/授权) ②附文生图/图生视频生成prompt ③取自已收集客户素材",
                  "禁止": "交付后用户再拍照/找物/补素材=流程事故(严禁)", "逐镜自问": "出包时: 这镜所有素材用户手里都有了吗"},
        "sources": ["docs/USER_SOP.md", "orchestration/ORCHESTRATION.md"]})
if "Rule:五层检查体系" not in ids:
    g["entities"].append({
        "id": "Rule:五层检查体系", "type": "Rule", "name": "五层检查体系(co-scientist风格)",
        "props": {"L1": "素材完整性 check_asset_pack.py(@引用全登记/无待补提示)", "L2": "prompt格式 check_prompt_sheet.py(R1-R11)",
                  "L3": "事实审计(科学顾问终核: 数据出处+待确认有去向)", "L4": "红队出口闸(评分单+三态)", "L5": "用户签收(上手包+工艺文件)",
                  "原则": "每层独立检查、不互相复用结论——全部通过才交付"},
        "sources": ["docs/USER_SOP.md", "orchestration/ORCHESTRATION.md"]})

KEYS = {(r["source"], r["target"], r["type"]) for r in g["relations"]}
for s, t, ty in [
    ("Rule:零意外素材自包含", "Rule:五层检查体系", "rule-enforced-by"),
    ("Rule:五层检查体系", "KspStep:KSP-06制作交付", "rule-governs"),
    ("Rule:五层检查体系", "KspStep:KSP-05分镜执行", "rule-governs"),
]:
    if (s, t, ty) not in KEYS:
        g["relations"].append({"source": s, "target": t, "type": ty, "props": {}})
        KEYS.add((s, t, ty))

json.dump(g, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("零意外+五层检查 rules added")
