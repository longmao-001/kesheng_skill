# -*- coding: utf-8 -*-
"""图谱补: Prompt严格统一格式规则(含口播分离字段 R11)"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

P = r"F:/AI/kesheng/packs/sop-seed/kg.json"
g = json.load(open(P, encoding="utf-8-sig"))
ids = {e["id"] for e in g["entities"]}
if "Rule:Prompt严格统一格式" not in ids:
    g["entities"].append({
        "id": "Rule:Prompt严格统一格式", "type": "Rule", "name": "Prompt严格统一格式",
        "props": {"范围": "交付给用户的所有prompt文件, 模板=templates/prompt-sheet.md",
                  "字段序": "标题/参考/风格/时间轴/口播/声音/负面/参数",
                  "口播分离": "口播单独成字段, 绝不整合进画面prompt正文(画面prompt给画面模型, 口播给配音/字幕, 两路分离)",
                  "文件命名": "每平台一个 prompts-<固定词表平台>.md + README.md",
                  "一致性": "风格token全片逐字一致(九宫格基线); 口播文本与口播稿一致",
                  "强制校验": "交付前必须 python scripts/check_prompt_sheet.py <runs/<项目>> 通过(R1-R11), FAIL不得交付"},
        "sources": ["templates/prompt-sheet.md", "scripts/check_prompt_sheet.py"]})
KEYS = {(r["source"], r["target"], r["type"]) for r in g["relations"]}
for s, t, ty in [
    ("Rule:Prompt严格统一格式", "KspStep:KSP-05分镜执行", "rule-governs"),
    ("Rule:Prompt严格统一格式", "Rule:AI原生交付原则", "rule-serves"),
]:
    if (s, t, ty) not in KEYS:
        g["relations"].append({"source": s, "target": t, "type": ty, "props": {}})
json.dump(g, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("Prompt严格统一格式 rule added")
