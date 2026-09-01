# -*- coding: utf-8 -*-
"""失败图书馆 → 图谱教训实体(FailureLesson) + 三条新规则(读法批注/品牌官方源/数据目检)"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

P = r"F:/AI/kesheng/packs/lessons-kg/kg.json"
os.makedirs(os.path.dirname(P), exist_ok=True)

SRC = ["runs/_lessons/FAILURE-LIBRARY.md", "F:/AI/DS harness/runs/20260830-pho-sc4/red-team-M4关闭确认.md"]

LESSONS = [
    ("FailureLesson:数据口径分层", "数据口径分层", {"现象": "s27_18长周期漂移图与手册10000h衰减混用并线性换算(F-01)", "根因": "来源/口径/量纲未分层", "规则": "不同口径数据不同屏不并列、禁线性换算; 数据来源三层=本机实测/官方手册/教科书, 上屏只认前两层"}),
    ("FailureLesson:数据目检", "原始文档目检确认", {"现象": "0.01nm课本精度当本机实测(F-02); 关键数值靠'大概率'", "根因": "验证用概率语言而非目检", "规则": "关键数据必须原始文档(PDF/手册/官网)目检确认+截图入库; '大概率/待确认'=L3检察官FAIL项"}),
    ("FailureLesson:品牌官方源", "品牌资产官方源", {"现象": "落版电光青自造色(C1); 青绿logo实为'玦芯生物'(C2)", "根因": "品牌色/字体/logo未从官方VI取", "规则": "品牌色/logo/字体一律官方源(官网矢量/VI/手册); 禁止自造色值; 品牌用字属用户拍板项#10"}),
    ("FailureLesson:旧表述残留", "全局残留一致性", {"现象": "主文本改完, 自评/待确认/下游建议/制作清单仍留旧表述(S1-S4)——M5按旧指令=问题回归", "根因": "只改面向读者的主文本, 未做全项目关键词扫描", "规则": "每轮修订后跑 check_residual.py 禁词残留扫描(执行文件); 修改必须全局同步清除旧表述"}),
    ("FailureLesson:型号数字撞车", "型号-参数数字规避", {"现象": "PHO-SC-4 的'4'与输出功率8W/4W字面易误读", "根因": "型号含数字与相近参数撞车", "规则": "型号含数字时, 与其相近的参数一律规避呈现(改'高功率输出'), 不出现8W/4W"}),
    ("FailureLesson:读法批注", "口播读法批注", {"现象": "口播稿缺读法, 配音/字幕各读各的(数字/单位/型号读法不一)", "根因": "口播稿无配音层规范", "规则": "口播稿必带读法批注: 数字读法/单位不念/型号逐字母/停连重音/语速档——AI配音或外部配音直接照读"}),
    ("FailureLesson:AI原生配音", "配音零找人", {"现象": "素材包'待你提供=外部配音'——唯一遗留动作", "根因": "未把配音纳入AI原生", "规则": "A档上手包默认AI原生配音(TTS/剪映智能配音/克隆音色+读法批注), 用户零找人零配音"}),
    ("FailureLesson:文案白名单", "零自创文案", {"现象": "用户删CTA/slogan/痛点段, 口播=定位语原文直读, 字幕=口播逐句", "根因": "团队默认做'广告创意'式文案层", "规则": "CTA/slogan/文案层=用户拍板项(默认不做); 字幕=口播逐句; 文案白名单无一字自创"}),
    ("FailureLesson:素材红线前置", "禁用素材清单前置", {"现象": "竞品曲线/水印素材进提案后被红队拦截", "根因": "版权/水印/竞品排查晚于方案", "规则": "brief阶段建立禁用清单(水印/竞品/未授权/AI味), 检查器全程扫描; 素材包出包=零待办"}),
]
for eid, name, props in LESSONS:
    props["证据"] = "F:/AI/DS harness/runs/20260830-pho-sc4/ (red-team-M4关闭确认.md / decision-log-m3.md / deliverables/00-素材包说明.md)"
    pass  # placeholder

RULES = [
    {"id": "Rule:读法批注", "type": "Rule", "name": "口播读法批注", "props": {"要求": "口播稿必带: 数字读法(±0.2%→误差不超过百分之零点二)/单位不念/型号逐字母(PHO-SC-4)/停连重音/语速档", "用途": "AI配音或外部配音直接照读, 杜绝各读各的"}, "sources": SRC},
    {"id": "Rule:品牌资产官方源", "type": "Rule", "name": "品牌资产官方源", "props": {"要求": "品牌色/logo/字体一律官方源(官网矢量/VI/手册), 禁止自造色值; 品牌用字属用户拍板项#10"}, "sources": SRC},
    {"id": "Rule:数据目检确认", "type": "Rule", "name": "数据目检确认", "props": {"要求": "关键数据必须原始文档目检(截图入库); '大概率/待确认'=L3检察官FAIL项; 教科书参数不上屏不绑机"}, "sources": SRC},
]
g = {"schema_version": "1.0", "pack": "lessons-kg", "role": "全角色",
     "entities": [], "relations": []}
for eid, name, props in LESSONS:
    g["entities"].append({"id": eid, "type": "FailureLesson", "name": name, "props": props,
                          "sources": ["runs/_lessons/FAILURE-LIBRARY.md"], "domains": ["工艺"]})
for r in RULES:
    g["entities"].append({**r, "sources": SRC, "domains": ["工艺"]})

KEYS = set()
for eid, name, props in LESSONS:
    g["relations"].append({"source": eid, "target": "Rule:五层检查体系", "type": "lesson-enables-check", "props": {}})
    g["relations"].append({"source": eid, "target": "KspStep:KSP-04创意概念", "type": "lesson-feeds", "props": {}})
for r in RULES:
    g["relations"].append({"source": r["id"], "target": "KspStep:KSP-05分镜执行", "type": "rule-governs", "props": {}})
g["relations"].append({"source": "FailureLesson:旧表述残留", "target": "Rule:图文对位", "type": "lesson-reinforces", "props": {}})
json.dump(g, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("lessons-kg:", len(g["entities"]), "entities /", len(g["relations"]), "relations")
