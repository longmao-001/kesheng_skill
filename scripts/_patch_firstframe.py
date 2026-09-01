# -*- coding: utf-8 -*-
"""修正 expand_tables2.json: 首帧图+图生视频 / 单镜抽卡 的旧范式文本(参考包优先)"""
import io
import json
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

P = r"F:/AI/kesheng/packs/prompt-kg/expand_tables2.json"
g = json.load(open(P, encoding="utf-8-sig"))
for pr in g.get("processes", []):
    if pr.get("name") == "首帧图+图生视频":
        pr["desc"] = "锚定范式判断顺序: ①全能参考(Seedance2.x/即梦)→参考包(@多图/视频/音频) ②多镜原生 ③仅I2V流或无参考包平台→首帧图+图生视频; 精确结构=参考包多角度(三视图/剖视/45°)优先"
        pr["steps"] = [
            "判断锚定范式顺序(全能参考→多镜原生→首帧I2V)。",
            "参考包: 从素材库组多图, prompt写清每张取什么(@图片1外观+@图片2结构)。",
            "仅当I2V流: 文生图生成首帧静帧(GPT Image 2首选)→科学顾问验收(科研片结构必须对)→图生视频, prompt只写运动。",
            "黑白线稿首帧→视频prompt写明最终彩色风格(风格token块)。",
        ]
        pr["rules"] = [
            "全能参考平台不用单独首帧——参考包直接锚定(单张首帧是一代旧范式)",
            "仅I2V流: 图生视频只写运动、不复述画面; 首帧图必须科学正确(科学顾问逐张验收)",
            "参考素材 4-5 个为宜(Seedance 2.0 共15个/2.5 共50个); 写实真人脸参考图会被审核直接拦截",
            "负面prompt含『文字，字幕，水印，logo』(AI画面零文字)",
        ]
    if pr.get("name") == "单镜抽卡":
        pr["steps"] = [
            "按锚定范式选模式(全能参考平台→参考包模式; 多镜原生→一次成片; 仅I2V流→上传首帧图生视频; 无参考→文生视频)。",
            "粘贴该镜prompt(含风格token块)+负面。",
            "按目标平台时长档抽3-6个变体, 选中最优固定。",
            "翻车时按失败→修复表改prompt再来(抽卡6次仍翻车改路线, 不死磕)。",
        ]
json.dump(g, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("expand_tables2 corrected")
