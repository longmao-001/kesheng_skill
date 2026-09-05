# -*- coding: utf-8 -*-
"""Add 广告禁用词 knowledge (Taboo/NegativeRule) to redteam-kg (红队), wire, rebuild."""
import io, json
P = r"F:/AI/kesheng/packs/redteam-kg/kg.json"
d = json.load(io.open(P, encoding="utf-8-sig"))
ents = d.setdefault("entities", []); rels = d.setdefault("relations", [])
new_ents = [
 {"id":"Taboo:广告绝对化用语","type":"Taboo","name":"广告绝对化用语(极限词)",
  "props":{"说明":"《广告法》绝对化/极限词禁用：最/最佳/第一/唯一/绝对/100%/顶级/国家级/世界级/全网最低/史无前例 等。检查器 `scripts/ad_forbidden_words.py`。","出处":"广告法+平台禁语"},
  "sources":["scripts/ad_forbidden_words.py","knowledge/ad-copy.md"],"domains":["红队"]},
 {"id":"Taboo:广告疗效功效承诺","type":"Taboo","name":"广告疗效/功效承诺禁用",
  "props":{"说明":"医疗/保健/食品类禁疗效承诺：治愈/根治/疗效/有效率/抗癌/降三高/生发/壮阳/排毒/消炎 等夸大功能。检查器 ad_forbidden_words.py。","出处":"广告法+食药监"},
  "sources":["scripts/ad_forbidden_words.py"],"domains":["红队"]},
 {"id":"NegativeRule:广告禁用词","type":"NegativeRule","name":"广告禁用词(极限词+疗效+平台禁语)",
  "props":{"说明":"广告词/文案/口播 交付前必扫禁用词(绝对化/疗效承诺/平台禁语)，`python scripts/ad_forbidden_words.py <文件>`；科技/科研产品用**可核实规格+数据(手册原文)**，不用 最/第一/绝对/100%/根治 等；有证据才说'领先/第一'(销量/数据)。","出处":"广告法+平台红线"},
  "sources":["scripts/ad_forbidden_words.py","knowledge/FAILURE-LIBRARY.md"],"domains":["红队"]},
]
have={e["id"] for e in ents}; ae=0
for e in new_ents:
    if e["id"] not in have: ents.append(e); have.add(e["id"]); ae+=1
new_rels = [
 ("Taboo:广告绝对化用语","Taboo:平台审核红线","concept-related-to"),
 ("Taboo:广告疗效功效承诺","Taboo:平台审核红线","concept-related-to"),
 ("NegativeRule:广告禁用词","Rule:五层检查体系","concept-related-to"),
 ("NegativeRule:广告禁用词","FailureLesson:文案白名单","concept-related-to"),
 ("NegativeRule:广告禁用词","Taboo:平台审核红线","concept-related-to"),
]
have2={(r.get("source"),r.get("target"),r.get("type")) for r in rels}; ar=0
for s,t,ty in new_rels:
    if (s,t,ty) not in have2: rels.append({"source":s,"target":t,"type":ty,"props":{}}); ar+=1
json.dump(d, io.open(P,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"added {ae} ents, {ar} rels to redteam-kg")
