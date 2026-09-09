# -*- coding: utf-8 -*-
"""知识萃取（20260905-embodied-industrial 复盘·门控校准）：向 workflow-seed（工艺域）追加两条
产品级门控认知。触发：该片已完成、出口评审 CONDITIONAL，主因不是内容而是「交付件版本漂移/多源并存」
与「机器门控与真实格式错位(假阴性)」。这两条是团队级可复用方法论，只进图谱，不新建概念卡。
隐私：不带任何客户/产品/合作方专有信息；来源=项目文件路径 + scripts/*。"""
import json

PATH = r"F:/AI/kesheng/packs/workflow-seed/kg.json"

NEW_ENTITIES = [
 {"id": "ProcessRule:交付件单一执行源版本收敛", "type": "ProcessRule",
  "name": "交付件单一执行源 + 版本收敛(出口前)",
  "props": {
    "说明": "最终交付件必须是单一自洽版本组合(口播定稿×分镜×执行prompt×风格基线)，同一制品只留一个定稿，版本漂移(多v并存/75s与90s同存/分镜标题版本与正文矛盾)即出口前打回——版本漂移是能拿到 PASS 的成品被降级为 CONDITIONAL 的最常见非内容原因",
    "规则": "①口播稿只保留一个『定稿』版本(vN)，其余版务归档/删除，禁止 v9 与 v10 并存；②执行prompt以 m4-prompts/prompts-*.md 为单一源，run 根/delivery 不放旁路同题文件；③delivery/README 索引自包含，引用的文件必须在 delivery/ 内(或标明外部资源)，引用 m2/ 等 run 根件=死链；④分镜表/口播/prompt 三者的时长与分段(0-15/15-55/...)必须一致",
    "检查": "出口前跑 scripts/check_delivery.py <runs/<项目>>：(A)多源并存 (B)delivery/README自包含死链 (C)口播稿多版本/分镜标题与正文版本矛盾——任一 FAIL 打回收敛后再交",
    "反模式": "『先记旧版再补新版』『同题文件复制到多个目录』『README 引用未打进包的文件』『标题写90s正文写75s』",
    "来源": "runs/20260905-embodied-industrial/m5-出口-评审单.md(§〇 交付件多版本分裂)"},
  "sources": [
    "runs/20260905-embodied-industrial/m5-出口-评审单.md",
    "runs/20260905-embodied-industrial/delivery/README.md",
    "scripts/check_delivery.py"]},

 {"id": "ProcessRule:门控与真实格式对齐", "type": "ProcessRule",
  "name": "机器门控须与实际生产格式对齐(避免假阴性)",
  "props": {
    "说明": "门控脚本是『考勤式门控』的底座，但它假设的格式如果已不是团队现在实际用的格式，就会对一份完成度高的制品整片误报(假阴性)，导致(a)制片人要么被迫绕开门控(b)要么门控失掉可信度。本片三条门控(check_sop/check_prompt_sheet/check_asset_pack)都因『只认**字段**：/只认@图片N/只认某列』而对一份基本合规的交付件满屏 FAIL",
    "规则": "①字段标记兼容两代(**字段**：与【字段】，核心字段同名)；②参考图语法兼容新旧(@图片N 与 @图NN=<文件名>/@图NN 空格文件名)，按 prompt 头『参考资产』映射解析；③路线白名单允许括注(参考生视频(产品·九段) → 主名=参考生视频)；④只要核心字段(参考/风格/时间轴/口播/声音/负面/参数)齐且非空即过，不因新增镜头/主体/强制约束等合法字段而报『字段顺序错』；⑤交付维度由 check_delivery.py 单独承担",
    "校验": "跑 check_sop / check_prompt_sheet / check_asset_pack 时，先看是否只报『格式别名』而非『真缺』；把误报理解为脚本过时而不是制品不过关；修复脚本(兼容)而非改动制品迎合脚本",
    "正例": "本片 check_sop/check_asset_pack 兼容后 PASS，只余镜00 真实缺陷(v9口播/风格token缺『真实产线为底』)被正确捕获",
    "来源": "scripts/check_sop.py / check_prompt_sheet.py / check_asset_pack.py"},
  "sources": [
    "scripts/check_sop.py",
    "scripts/check_prompt_sheet.py",
    "scripts/check_asset_pack.py",
    "templates/prompt-sheet.md"]},
]

NEW_RELATIONS = [
 ("ProcessRule:交付件单一执行源版本收敛", "concept-related-to", "ProcessRule:成片文件组织规范"),
 ("ProcessRule:门控与真实格式对齐", "concept-related-to", "ProcessRule:成片文件组织规范"),
]

# 跨片段关系：端点在被合并的其它域片段(并集后存在)，直接追加(并集构建时校验去重)
CROSS_RELATIONS = [
 ("ProcessRule:交付件单一执行源版本收敛", "concept-related-to", "ProcessRule:质量门控"),
 ("ProcessRule:交付件单一执行源版本收敛", "concept-related-to", "Gate:M4出口门控"),
 ("ProcessRule:门控与真实格式对齐", "concept-related-to", "ProcessRule:质量门控"),
 ("ProcessRule:门控与真实格式对齐", "concept-related-to", "ProcessRule:多agent辩论门控"),
]

def main():
    with open(PATH, encoding="utf-8") as f:
        kg = json.load(f)
    known_ids = {e["id"] for e in kg["entities"]}
    for e in NEW_ENTITIES:
        if e["id"] in known_ids:
            print(f"[skip-entity] 已存在: {e['id']}"); continue
        kg["entities"].append(e); known_ids.add(e["id"])
        print(f"[add-entity] {e['id']}")
    exist_rel = {(r["source"], r["type"], r["target"]) for r in kg["relations"]}
    for src, t, dst in NEW_RELATIONS:
        if src not in known_ids or dst not in known_ids:
            print(f"[warn-rel] 端点缺失: {src} ->{t}-> {dst}"); continue
        if (src, t, dst) in exist_rel:
            print(f"[skip-rel] 已存在: {src} ->{t}-> {dst}"); continue
        kg["relations"].append({"source": src, "target": dst, "type": t, "props": {}})
        print(f"[add-rel] {src} ->{t}-> {dst}")
    for src, t, dst in CROSS_RELATIONS:
        if (src, t, dst) in exist_rel:
            print(f"[skip-rel] 已存在: {src} ->{t}-> {dst}"); continue
        kg["relations"].append({"source": src, "target": dst, "type": t, "props": {}})
        print(f"[add-cross-rel] {src} ->{t}-> {dst}")
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(kg, f, ensure_ascii=False, indent=1); f.write("\n")
    with open(PATH, encoding="utf-8") as f:
        kg2 = json.load(f)
    print(f"[OK] entities={len(kg2['entities'])} relations={len(kg2['relations'])}")

if __name__ == "__main__":
    main()
