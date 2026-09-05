#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
广告禁用词/极限词 检查器 (ad_forbidden_words.py)

依据《广告法》绝对化用语/极限词 + 医疗保健疗效承诺 + 平台(电商/短视频)禁语，扫描文本，返回命中。
用法:
  python scripts/ad_forbidden_words.py <文件或文本串>      # 扫描
  python scripts/ad_forbidden_words.py --list --ad          # 列出广告段
供 红队(广告合规禁用词) / 检察官 / check_residual.py 复用。

科生特别提醒(科技/科研产品): 别用 最/第一/绝对/100%/顶级/根治 等；用可核实的规格+数据(手册原文)，卖点=可验证参数。
"""
import io, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 《广告法》绝对化用语 / 极限词
ABS = ["最好","最佳","最优","最强","最先进","最科学","最优秀","最专业","最实惠","最低价","最高级",
       "最具","最大规模","销量第一","全国第一","全球第一","世界第一","行业第一","第一名","排名第一",
       "首选","唯一","独一无二","独家","首家","首位","领先","领导者","领导品牌","顶级","极致","至尊",
       "顶尖","一流","全覆盖","全网最低","史上最低","全球领先","世界领先","国家级","世界级","最高级",
       "万能","绝对","百分百","百分之百","100%","零风险","万无一失","永久","永久有效","绝无仅有",
       "史无前例","前所未有","不二之选","天下第一","无双","国家免检","质量免检","中国驰名商标",
       "100%纯天然","100%无添加","绝对安全","绝对有效","无任何副作用","无任何风险","轻松达到","一劳永逸"]
# 疗效/功效承诺 (医疗/保健/食品禁区)
EFF = ["治愈","根治","包治","疗效","有效率","治愈率","抗癌","防癌","抗肿瘤","降三高","降血压","降血脂",
       "降血糖","治疗糖尿病","治疗高血压","治疗癌症","防癌抗癌","提高免疫力(限保健食品)","增强免疫力(限保健食品)",
       "生发","壮阳","丰胸","排毒","消炎","杀菌","修复受损","激活细胞","改善睡眠(限保健)","促进生长发育",
       "增高","药到病除","一次治愈","神奇疗效","断根","没有任何副作用","百分百有效","永久不反弹"]
# 虚假/不可证实
FAKE = ["毫无副作用","百分百有效","永久不反弹","绝对根治","全网最低价","销量第一","突破性","革命性",
        "史无前例","将颠覆", "完美配方","绝佳","出类拔萃"]
# 平台通用禁语(电商/短视频)
PLAT = ["抢爆","仅此一天","最后一波","限时抢购(未如实)","假一赔十(未兑现)","史上最低","全网最低","颠覆行业"]

ALL = ABS + EFF + FAKE + PLAT

def scan(text):
    hits = []
    for w in ABS:
        if w in text:
            hits.append(("绝对化/极限词", w))
    for w in EFF:
        if w in text:
            hits.append(("疗效/功效承诺", w))
    for w in FAKE:
        if w in text:
            hits.append(("虚假/不可证实", w))
    for w in PLAT:
        if w in text:
            hits.append(("平台禁语", w))
    # 去重(若同一词多列)
    seen=set(); res=[]
    for cat,w in hits:
        if (cat,w) in seen: continue
        seen.add((cat,w)); res.append((cat,w))
    return res

def main():
    args=sys.argv[1:]
    if args and args[0]=="--list":
        print("== 绝对化/极限词 =="); print("、".join(ABS))
        print("\n== 疗效/功效承诺 =="); print("、".join(EFF))
        print("\n== 虚假/不可证实 =="); print("、".join(FAKE))
        print("\n== 平台禁语 =="); print("、".join(PLAT))
        return
    if not args:
        print("用法: ad_forbidden_words.py <文件或文本> | --list"); sys.exit(2)
    src=args[0]
    import os
    text = io.open(src,encoding="utf-8-sig").read() if os.path.isfile(src) else src
    hits=scan(text)
    if hits:
        print(f"== 广告禁用词命中 {len(hits)} ==")
        for cat,w in hits:
            print(f"  [{cat}] {w}")
        sys.exit(1)
    print("== 通过: 未命中广告禁用词 ==")

if __name__=="__main__":
    main()
