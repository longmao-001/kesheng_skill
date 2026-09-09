# -*- coding: utf-8 -*-
"""KSP-07 知识萃取（第二轮）：向 workflow-seed（工艺域）追加本轮新增认知。
本轮条目：①LuStage 4D高斯光场重建(4DGS) ②影视术语补充关系(道具/角色/场景/分镜+三视图锚/九段)
③成片文件组织规范+参考图分类规范 ④多agent辩论门控成功案例 ⑤锂电高危工序认知(调研背景,非已实现)。
来源=官方公开页/项目文件/补充调研；不确定项一律标『待确认』。只进图谱，不新建概念卡。"""
import json

PATH = r"F:/AI/kesheng/packs/workflow-seed/kg.json"

NEW_ENTITIES = [
 {"id": "ScientificConcept:4D高斯光场重建", "type": "ScientificConcept",
  "name": "4D高斯光场重建(4DGS/4D Gaussian Splatting)",
  "props": {
    "定义": "多视点相机阵列360°同步采集→以三维高斯椭球表达场景(3D空间+时间=4D)→高精度重建动态人体/动作, 可任意视点回放",
    "原理": "高斯泼溅(Gaussian Splatting)向时间维度扩展: 用一组高斯椭球(位置/旋转/尺度/不透明度/球谐)逐帧或时序表达场景→新视角实时合成; 演进链 NeRF→3DGS(实时高质量)→4DGS(动态), 见 Gaussian Splatting 综述",
    "输出": "体积视频/动态三维重建: 360°实时光场采集; 支撑新视角合成、数字人/数字孪生复现",
    "应用": "光场重建系统(商用例: 元客视界 LuStage S4D, 官方公开页); 已入成片口播『LuStage 多视点4D高斯光场重建』——用途=动作/人体采集与数字孪生建模",
    "口径注意": "『光场重建』≠普通多相机视频: 是三维高斯椭球(3D+时间)表达; 术语错误=把光场重建当『3D扫描/普通拍摄』",
    "待确认": "4DGS 具体时序建模方式(逐帧建模 vs 时序插值)取决于产品实现, 未见官方技术白皮书——待确认"},
  "sources": [
    "https://ymate3d.com/product/202401051327290075.html",
    "https://www.lusterinc.com/solution/lu-stage-s4d/",
    "runs/20260905-embodied-industrial/m2/scientist-补充调研-具身智能进工业.md",
    "runs/20260905-embodied-industrial/storyboard-分镜表.md",
    "https://arxiv.org/abs/2405.03417"]},

 {"id": "ScientificConcept:锂电工序高危点", "type": "ScientificConcept",
  "name": "锂电产线高危工序(调研背景)",
  "props": {
    "说明": "锂电电芯产线典型『高危+重体力+高节拍』工序, 是具身智能『替人』(用工缺口×高危岗位)的典型场景与调研背景; 仅作背景认知, 不作『已实现』声明",
    "注液": "液态电解液(碳酸酯类有机溶剂+锂盐)有毒、易燃→注液工位需防毒防爆",
    "焊接化成": "焊接/化成工段高温(化成过充产热)→高温+火源与化学品风险",
    "涂布辊压分切": "涂布高温溶剂(烘干+溶剂挥发)→易燃/有毒蒸汽; 辊压分切高精度机械",
    "搬运": "电芯/模组搬运=重体力高负荷",
    "模组装配": "多部件装配, 重体力+精密对位",
    "口径注意": "行业共性问题(高危×用工缺口)用定性表述, 不报市场具体数字; 与『数据是总命门』并列作行业背景",
    "待确认": "各工序危害细节为行业通识+项目调研背景, 未逐条附一手文献——待确认"},
  "sources": [
    "runs/20260905-embodied-industrial/m2/scientist-补充调研-具身智能进工业.md",
    "runs/20260905-embodied-industrial/brief.md",
    "runs/20260905-embodied-industrial/refs/核心技术方案与旁白_抽取稿.md"]},

 {"id": "ProcessRule:多agent辩论门控", "type": "ProcessRule",
  "name": "多agent辩论门控(子代理优先+红队三态)",
  "props": {
    "说明": "同一镜头/内容的创意分歧: 各角色(导演/分镜师+摄影指导/编剧等)以独立上下文并行给方案, 红队(未参与创作)三态裁决(PASS/CONDITIONAL/BLOCK), 制片人整合『后改法』再落地; 子代理优先=制片人不包办",
    "成功案例": "20260905-embodied-industrial 开场镜头(镜00, 数据灯海→巨机挺立): 导演=灯海→巨机挺立『数据成骨 具身成峰』; 分镜/摄影=45°俯冲急停; 红队=CONDITIONAL后改法: ①f6961d真素材打底(不纯AI硬造) ②线框≤30% ③新口播句入文案白名单 ④镜06压至8s——机制=独立争议→三态裁决→整合改法→白名单收口",
    "案例来源": "m4-prompts/prompts-cgprism.md 镜头00/镜头06(8s); m4-gate-red-recheck.md(红队CONDITIONAL); editor-剪辑预计划.md(文案白名单)",
    "待确认": "『数据成骨 具身成峰』方案语未在项目文件中命中, 为项目纪要/讨论口径——待确认"},
  "sources": [
    "runs/20260905-embodied-industrial/m4-prompts/prompts-cgprism.md",
    "runs/20260905-embodied-industrial/m4-gate-red-recheck.md",
    "runs/20260905-embodied-industrial/editor-剪辑预计划.md",
    "orchestration/ORCHESTRATION.md",
    "knowledge/FAILURE-LIBRARY.md"]},

 {"id": "ProcessRule:成片文件组织规范", "type": "ProcessRule",
  "name": "成片文件组织规范(delivery/视频 按镜号命名)",
  "props": {
    "说明": "成片归档到 delivery/视频/ 并按镜号命名; 一镜多版本=同镜号同名后缀(版本/长版); 无镜号特殊件按『主题-描述』命名",
    "命名格式": "镜NN-主体-描述.mp4 (例: 镜00-开场-数据灯海.mp4 / 镜05c-第一人称检查电芯-手部骨架.mp4)",
    "特殊件": "无镜号: 主题-描述.mp4 (例: 注液工位-工人高危-电解液.mp4 / 全身遥操作-人形机器人-动捕.mp4)",
    "项目实例": "本项目 delivery/视频/ 共15条成片(镜00/02/03/05b/05c×2/06/07×3/10×2 + 注液工位高危 + 全身遥操作 + 续写片段重拍)"},
  "sources": [
    "runs/20260905-embodied-industrial/delivery/README.md",
    "runs/20260905-embodied-industrial/delivery/assets-inventory.md",
    "playbooks/production-workflow.md"]},

 {"id": "Rule:参考图分类规范", "type": "Rule",
  "name": "参考图分类规范(项目验证码)",
  "props": {
    "说明": "参考图按 用途前缀+类型码 分类(文件名=条目ID): 三视图锚=RF_MAIN_*_三视图(主体/道具/角色锚); 场景=RF_SCENE_*; 数据卡=RF_CARD_*_数据卡(人工锁值); 第一人称=RF_POV_*; 部件=RF_PART_*; 结构=RF_STR_*; 品牌=*_BRAND_*; 实拍=IN_RAW_*",
    "派生": "自 素材库分类两轴(IN/RF×MAIN/PART/SCENE/STR/TEXT/DATA/BRAND/RAW); 本项目扩展 RF_CARD(数据卡)/RF_POV(第一人称)",
    "挂载": "每镜 prompt 参考图挂载清单=文件+取哪部分→放哪; 主体一致性优先复用三视图锚图(跨镜)"},
  "sources": [
    "runs/20260905-embodied-industrial/assets-inventory.md",
    "runs/20260905-embodied-industrial/delivery/场景道具-先生成清单.md",
    "templates/assets-inventory.md",
    "playbooks/production-workflow.md"]},
]

# 既有实体 props 增补（合并进原 props）
PROPS_PATCH = {
 "FilmProp:道具": {
   "素材路线": "道具=物体: 全用真素材/官方图作锚(实拍/官方产品图), 不AI再造; 先生成三视图锚——product-prompt-formula §〇.5; 参考图分类=RF_MAIN_*_三视图"},
 "FilmCharacter:角色": {
   "素材路线": "角色=人·形象(AI三视图): 概念角色用文生图生成三视图作全片角色锚(以实物/官方图为参考), 有实拍可用真素材; 参考图分类=RF_MAIN_*_三视图"},
 "FilmScene:场景": {
   "背景素材路线": "场景=环境背景: 有真素材(实拍/官方图)剪入/作背景, 无真素材才AI生成场景背景; 角色分层放入场景; 场景≠道具≠角色"},
 "StoryboardShot:分镜": {
   "视频prompt公式": "分镜视频prompt=video-prompt-formula 九段(参数/参考/风格/镜头/时间轴/主体/声音/口播/负面+强制约束); 道具/角色/场景锚图prompt=product-prompt-formula 八段(三视图=§〇.5)"},
}

# 既有实体 sources 增补（去重）
SOURCES_PATCH = {
 "FilmProp:道具": ["runs/20260905-embodied-industrial/delivery/场景道具-先生成清单.md"],
 "FilmCharacter:角色": ["runs/20260905-embodied-industrial/delivery/场景道具-先生成清单.md"],
 "FilmScene:场景": ["runs/20260905-embodied-industrial/delivery/场景道具-先生成清单.md"],
 "StoryboardShot:分镜": ["runs/20260905-embodied-industrial/delivery/场景道具-先生成清单.md",
                          "templates/video-prompt-formula.md"],
}

# 关系：idA -> type -> idB
NEW_RELATIONS = [
 ("ProcessRule:多agent辩论门控", "concept-related-to", "RoleWorkflow:红队"),
 ("ProcessRule:多agent辩论门控", "concept-related-to", "RoleWorkflow:制片人"),
 ("Rule:参考图分类规范", "concept-related-to", "Rule:参考图挂载清单必写"),
 ("FilmProp:道具", "concept-related-to", "Rule:参考图分类规范"),
 ("FilmCharacter:角色", "concept-related-to", "Rule:参考图分类规范"),
 ("FilmScene:场景", "concept-related-to", "Rule:参考图分类规范"),
 ("StoryboardShot:分镜", "concept-related-to", "Rule:参考图分类规范"),
]

# 跨片段关系：端点在被合并的其它域片段(并集后存在), 直接追加(并集构建时校验去重)
CROSS_RELATIONS = [
 ("ScientificConcept:4D高斯光场重建", "concept-related-to", "ScientificConcept:数字孪生"),
 ("ScientificConcept:4D高斯光场重建", "concept-related-to", "ScientificConcept:三维视觉感知与位姿估计"),
 ("ScientificConcept:锂电工序高危点", "concept-related-to", "ScientificConcept:具身智能进工业七大技术群"),
 ("ScientificConcept:锂电工序高危点", "concept-related-to", "ScientificConcept:人机协作安全"),
 ("ProcessRule:多agent辩论门控", "concept-related-to", "ProcessRule:质量门控"),
 ("ProcessRule:成片文件组织规范", "concept-related-to", "ProcessRule:素材库命名规范"),
 ("Rule:参考图分类规范", "concept-related-to", "Concept:素材库分类两轴"),
 ("Rule:参考图分类规范", "concept-related-to", "ProcessRule:三视图锚定"),
]

def main():
    with open(PATH, encoding="utf-8") as f:
        kg = json.load(f)

    known_ids = {e["id"] for e in kg["entities"]}
    for e in NEW_ENTITIES:
        if e["id"] in known_ids:
            print(f"[skip-entity] 已存在: {e['id']}")
            continue
        kg["entities"].append(e)
        known_ids.add(e["id"])
        print(f"[add-entity] {e['id']}")

    for eid, patch in PROPS_PATCH.items():
        for e in kg["entities"]:
            if e["id"] == eid:
                e["props"] = {**e.get("props", {}), **patch}
                print(f"[patch-props] {eid}: {list(patch)}")
                break
        else:
            print(f"[warn-props] 实体不存在: {eid}")

    for eid, add_srcs in SOURCES_PATCH.items():
        for e in kg["entities"]:
            if e["id"] == eid:
                srcs = list(e.get("sources", []))
                for s in add_srcs:
                    if s not in srcs:
                        srcs.append(s)
                e["sources"] = srcs
                print(f"[patch-sources] {eid}: +{len(add_srcs)}")
                break
        else:
            print(f"[warn-sources] 实体不存在: {eid}")

    exist_rel = {(r["source"], r["type"], r["target"]) for r in kg["relations"]}
    for src, t, dst in NEW_RELATIONS:
        if src not in known_ids or dst not in known_ids:
            print(f"[warn-rel] 端点缺失，跳过: {src} ->{t}-> {dst}")
            continue
        if (src, t, dst) in exist_rel:
            print(f"[skip-rel] 已存在: {src} ->{t}-> {dst}")
            continue
        kg["relations"].append({"source": src, "target": dst, "type": t, "props": {}})
        print(f"[add-rel] {src} ->{t}-> {dst}")
    for src, t, dst in CROSS_RELATIONS:
        if (src, t, dst) in exist_rel:
            print(f"[skip-rel] 已存在: {src} ->{t}-> {dst}")
            continue
        kg["relations"].append({"source": src, "target": dst, "type": t, "props": {}})
        print(f"[add-cross-rel] {src} ->{t}-> {dst}")

    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(kg, f, ensure_ascii=False, indent=1)
        f.write("\n")

    with open(PATH, encoding="utf-8") as f:
        kg2 = json.load(f)
    print(f"[OK] entities={len(kg2['entities'])} relations={len(kg2['relations'])}")

if __name__ == "__main__":
    main()
