#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
check_prompt_delivery.py —— 科生 prompt 交付门控（通用版 · D1–D10[＋D11 可选]＋D12/D13）

来源：20260915《红楼梦》动漫 EP01 项目实战脚本
（runs/20260915-红楼梦动漫EP01/tools/check_prompt_delivery.py，四轮把基线 313 FAIL 清到 0）。
本脚本是它的**通用化**版本：不写死任何项目文件名/锚名；项目相关词表（专属空间标记、色彩语义、
角色锚名、字卡镜号、校勘红线句等）全部改为**可选配置**注入，缺省即用通用词表。
已纳入科生技能本体 scripts/，作为**所有项目交付前必跑**项（SOP 三层门控中的"机器门控"层）。

用法：
  python -X utf8 scripts/check_prompt_delivery.py <run目录> [文件...] [选项]

  首参必须是 **run 目录**（runs/<项目slug>）；[文件...] 是可选的白名单。
  首参若误传成**文件**，脚本会自动解析：run目录取其所属 runs/<项目slug>，该文件本身作为
  显式文件参与检查，并在输出首行说明解析结果（不静默、不空跑）。
  **空跑一律不算通过**：首参既非目录也非文件、显式文件不存在、扫描到 0 个文件、
  匹配到 0 个镜头条目 → 一律输出 `FAIL: …` 并 exit 2（"FAIL 0 / WARN 0" 只可能来自真扫过的文件）。

选项：
  --animation-baseline  D10 基线模式：动画性检查仍逐条列出清单，但不计入总 FAIL、不改退出码
                        （20260915 用户裁定：动画类项目全库初期大面积 FAIL 属预期——这是待办清单，
                          不是立刻可清零项）
  --animation-only      只跑 D10（动画性专项体检）
  --no-animation        跳过 D10（等价于动画性裁定之前的旧口径）
  --json                机器可读输出（JSON，供 check_all.py / CI 消费）
  --config PATH         指定配置文件；默认读 <run目录>/prompt-delivery-config.json
  --dump-config         打印合并后的生效配置（项目作者据此写自己的 config）
  --zika-shots "1-04,1-05"       显式指定字卡镜号（等价配置 text_card_shots）
  --correction-red "未校句1,未校句2"  显式指定校勘红线句（等价配置 correction_red_terms）
无文件参数时按 file_globs 扫描 run 目录（跳过 exclude_dirs）；显式给文件则只查这些文件。

通道档（**用户裁定 20260921 · 双通道并存 · 硬规则 #42 · 范围升级含通道 C**；依据 `docs/DUAL-CHANNEL-AUDIT.md`）：
  配置项 `"channel": "A" | "B" | "C" | "A+B" | "A+C" | "B+C" | "A+B+C"`——**严格优先：留空/未声明 ⇒ 全套严格**
  （防"没写 channel 就静默关闸"，那会让 D12/D13/D10 对既有项目整体失效）：
  · **channel=A（通道 A · 广告/科普/科研视频）**：**显式声明**才跳过剧集专属 **D10**
    （动画性 · #28 仅 AI 原生动画路径）＋ **D12**（OP 段禁浮空字卡 · #33 仅剧集 OP/ED），
    输出注明「通道A档（显式声明）：已跳过 …」——防"浮空字卡/动画性"对广告线**误报**。
  · **channel=C（通道 C · 音乐驱动 MV）**：只跳 **D12**；**D10 保留**（MV 也可能是动画路径）。
  · **channel=A+C**：跳 D10＋D12。**channel=B / A+B / B+C / A+B+C**：D1–D13 全套严格
    （限 D10 受基线模式控制）——**含 B 的组合保留全部字母**（T4-a：A+B+C 不得丢 C 信息）。
  · **D13 禁亮词（#34）不由通道名决定**：由 `light_terms` 是否为空决定——通道 A 默认档置空 ⇒ 不评估；
    项目显式给了词表（如水墨/无光源项目）⇒ **即便通道名写 A 也照跑**（避免"写个通道名就整体关闸"）。
  · 通道 A/C 档**不放松**通用项：D1/D2/D3/D4/D5/D6/D7/D8/D9（＋可选 D11）与广告法合规照旧。
  模板：`templates/prompt-delivery-config-channelA.json`（通道 A 默认档）。
  配置 `channel` 值非法（非 A/B/C/A+B/A+C/B+C/A+B+C）⇒ `exit 2`（不可判定，绝不静默按 B 跑）；
  配置文件 `prompt-delivery-config.json` **JSON 语法错/读不出** ⇒ 同样 `exit 2`（T3：**不静默回退默认词表**）。

检查项（D1–D10 全部保留自实战版，逐条对应 20260915 用户裁定）：
  D1 SOP 字段完整：视频条目须含 参考/风格/时间轴/口播/声音/负面/参数（允许等价写法，见
     field_aliases，如"声音"可由 音效/配乐/BGM 满足）；图片条目须在同一 prompt 块内**内嵌负面**
  D2 @标记贯穿：素材指代段出现"图片N"时，正文须同步出现 "@图片N"（禁"正文另写取自图片2"的脱节写法）
  D3 负面与正文同块：条目内有代码块时，"负面"字段不得写在代码块外
  D4 废止表述禁词：后期配音/后期叠/后期合成/急停悬停/定格卡 等（变更/废止/禁止/作废行豁免）
     ＋ D4-EXT 专属空间标记越界（exclusive_space_terms，可选配置注入）
  D5 故事板纪律：**只查代码块内的 prompt 正文**——须含「线稿」、须要求「景别/运镜」、
     负面须钉死线稿禁项（默认 水墨/印章，可配 7 词钉死集与最低数量）
  D6 字卡口径：禁「字卡后期上屏」等旧口径（已改为模型原生生成，除非明确标注为变更记录）
  D7 校勘红线：不得出现未校勘原文（correction_red_terms / m5-校勘红线.txt，**默认空**）
  D8 后期表述归一：字/印/字卡族、剪辑工序族、声音工序族（normalize_terms 可扩展）
  D9 字卡镜负面分档：字卡镜禁 text 类，改钉字形类（字卡镜由 text_card_shots /
     text_card_shots_pattern 指定；未配置时按条目文字自动判定，仅出 NOTE，避免项目词表缺失时误伤）
  D10 动画性检查（用户裁定：这是动画，不是动态PPT）
     a) 【时间轴】动作曲线词 ≥2（预备→发力→跟随→回收）
     b) 【时间轴】主体表演动词 ≥2（只写运镜/氛围不算）
     c) 【负面】动画性禁项 ≥2 ＋ 叙事相关性禁项 2 项（空洞特效/风吹草动）
     d) 含字卡文字的条目：【时间轴】须写「逐字书写/笔迹生长/写出」类书写性表述（禁 弹出/叠加/上屏）
     e) 动作动机：须含「动作动机＝…」标注，且动机句须出现语义判据词
        （含义/说的是/象征/对位/意味着/谶/执/梦/命 类）之一——动作不是装饰，是台词
  D11 交付格式（**可选，默认关**，配置 check_second_prompt=true 才启用）：一镜只允许一条可复制
     prompt——同一镜条目下出现【平台prompt】/【视频prompt】/【对照】等第二版本 = FAIL
     （两套写法=用户困惑源）
  D12 OP 段禁浮空字卡（20260915 甲方裁定A）：OP 段条目（镜号 1-01~1-16，或段块标题匹配
     op_scope_pattern 如「段A-01~A-05」）的【时间轴】不得含「字卡／逐字书写／字位书写／字卡位／
     叠角字卡／字幕」等浮空字卡字样；含则 FAIL。**例外白名单**（op_text_whitelist_terms）：
     片头标题字（片名／注音／印章／落印）与物件上的字（玉面镌字／石面刻字／镌字）——
     同句含白名单词即豁免；「变更/废止/禁止/作废」留痕句豁免。
     （谶语·诗词的逐字上屏移至正片 C5 段等，不在 OP 画面内出现）
  D13 禁亮词（20260915 甲方裁定B）：水墨风格无光源（无光之戏），全库 prompt 正文不得出现
     「一亮／发亮／闪光／高光／辉光／反光／发光」（含繁体外字形）——**禁项枚举豁免**：
     写在「负面」字段或禁项串行里（作为禁项列出）不算违规；**否定式豁免**：命中处前
     light_negation_window 字内出现 不/无/禁/非/勿/绝 等（如「只色不发光」「无瞳孔高光」）豁免；
     **方法性字段豁免**：参数／失败改法／判废标准／判废要点／废片判据／台账等 QC 行整行豁免。
     表达变化只能用墨的语言：渐浓、渐沉、洇开、褪淡、沉深一分、退回原色。
   D4/D13 承载型豁免（20260917 甲方要求）：**清单·台账类文件引用禁词是正确做法**，不得判 FAIL。
     ① 行级：命中行以 负面/负面词/判废/禁/D4/D13 等标签开头，或处于同一「负面词…」标签段落内
        （负面词串行即在此），或该行是纯枚举（逗号分隔 ≥N 项、无句读、无正文动词）= 词表列举；
     ② 文件级：文件名匹配 标签总表/台账/清单/自检卡/门控回执 → 该文件 D4/D13 一律降为 NOTE；
        prompt 执行件（prompts-*／segments-*／storyboard-*／m4-prompts/／m4-分镜表）**维持严格**（strict 优先）。
     降级只改档位不改检查：命中行仍逐条打印为 NOTE（可审计）；prompt 执行件里写「画面微微一亮」
     或「后期配音」照旧判 FAIL。

退出码：0 = 无 FAIL（含基线模式恒 0）；1 = 有 FAIL；2 = 用法错误或**无法判定**（路径非法/文件不存在/0 文件/0 镜头）。

配置文件 <run目录>/prompt-delivery-config.json（可选，所有键可缺省）——
详见 scripts/README-check_prompt_delivery.md。
"""
import argparse
import glob as _glob
import json
import os
import re
import sys

try:  # Windows 控制台中文输出保险
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

# ============================================================================
# 一、默认配置（通用词表）—— 项目可用 <run目录>/prompt-delivery-config.json 覆盖
#    约定：词表项按**正则片段**处理（普通词可直写；含正则元字符时即按正则解释）
#    凡标 ★ 的键 = 实战项目里曾写死的项目词，通用版一律改由配置注入
# ============================================================================
DEFAULT_CONFIG = {
    # ---------- 扫描范围 ----------
    "file_globs": ["prompts-*.md", "segments-*.md", "m5-*.md", "shotlist-*.md",
                   "storyboard-*.md", "*prompt*.md"],
    "exclude_dirs": ["_旧版归档", "旧版", "archive", "归档", "node_modules", ".git"],

    # ---------- 条目锚（不写死项目锚名，可配置） ----------
    #  默认只认"### 镜头 …"（科生 SOP 规范锚）；项目若用「### 镜 1-01」等锚，改这个正则
    "shot_heading_pattern": r"镜头|\bShot\b|\bshot\s*\d",
    "shot_id_pattern": r"([0-9A-Za-z]+[-–][0-9A-Za-z]+|T\d+[A-Za-z]?|S\d+[A-Za-z]?|G\d+[A-Za-z]?)",

    # ---------- D1 SOP 字段（字段名或其等价写法命中即算） ----------
    "required_video_fields": ["参考", "风格", "时间轴", "口播", "声音", "负面", "参数"],
    "field_aliases": {
        "参考": [r"参考", r"@图片\s*\d", r"@图\s*\d", "挂载", "参考图"],
        "风格": [r"风格", r"\bstyle\b", "风格token"],
        "时间轴": [r"时间轴", r"\d+\s*[-–~]\s*\d+\s*秒", r"第\s*\d+\s*秒", r"\d+:\d\d"],
        "口播": [r"口播", "旁白", "台词", r"V\.?\s*O\.?", "画外音", "解说词"],
        "声音": [r"声音", "音效", "配乐", r"\bBGM\b", "音频", "静音", "拟音", r"\bSFX\b"],
        "负面": [r"负面", r"\bnegative\b", "禁项"],
        "参数": [r"参数", "时长档", "画幅"],
    },
    "video_entry_pattern": r"时间轴|运镜|镜头运动|I2V|T2V|图生视频|文生视频|视频|\d+\s*s\b|秒",
    "image_entry_pattern": r"出图|静帧|图片条目|九宫格|首帧图|Image2|IMAGE|图像生成|文生图|T2I",

    # ---------- 通用豁免（规则自述行/变更记录行不算违规） ----------
    "allow_line_terms": ["变更", "废止", "禁止", "作废", "旧口径", "已废", "不得"],

    # ---------- D2 @标记贯穿 ----------
    "image_ref_pattern": r"图片\s*\d",
    "image_at_pattern": r"@图片\s*\d",

    # ---------- D3/D9/D10 用的「负面」字段识别 ----------
    "negative_field_pattern": r"^\s*-?\s*\*\*(?:负面|负面词)\*\*|^\s*【?负面",

    # ---------- D4 废止表述禁词（★ 项目可追加色彩语义/角色锚等专属禁词） ----------
    "forbidden_terms": ["后期配音", "后期叠", "后期合成", "急停悬停", "定格卡"],

    # ---------- D4-EXT 专属空间标记（★ 项目词：如「墨浪/S9墨浪」仅限 OP 段） ----------
    #  结构：[{"term": "墨浪", "allowed_shots": ["1-01","1-02"],
    #         "allowed_scope_pattern": "OP段|序幕|A-0[1-5]", "note": "OP段专属空间标记"}]
    #  判定：该词出现在「允许镜号」或「允许作用域标题」之外 → FAIL；
    #        出现在负面字段行内 = 列为禁项（正确用法，豁免）；无法定位上下文 → WARN。
    "exclusive_space_terms": [],
    "exclusive_space_negative_exempt": True,

    # ---------- D5 故事板纪律（仅代码块内） ----------
    "storyboard_markers": ["故事板"],
    "storyboard_trigger_terms": ["生成", "黑白", "线稿", "出图", "storyboard"],
    "storyboard_required_terms": ["线稿"],
    "storyboard_shot_terms": ["景别", "运镜"],
    "storyboard_negative_terms": ["水墨", "印章"],
    "storyboard_negative_min": 1,

    # ---------- D6 字卡旧口径 ----------
    "text_card_markers": ["字卡", "回目", "谶文", "定场诗", "片名", "印文"],
    "text_card_legacy_terms": ["字卡后期上屏", "字卡后期", "字后期上屏", "后期上屏", "后期字卡上屏"],

    # ---------- D7 校勘红线（★ 默认空 = 不做项目专属校勘检查） ----------
    "correction_red_terms": [],
    "correction_red_file": "m5-校勘红线.txt",   # 备选注入源（每行一句）
    "correction_exempt_terms": ["校勘", "变更", "废止", "禁止", "作废"],

    # ---------- D8 后期表述归一（★ 项目可按需扩展 normalize_terms） ----------
    "normalize_terms": [
        # 字/印/字卡族 → 「字卡（印文）含于prompt由模型原生生成」
        "字后期", "后期板", "后期贴回", "后期压印", "后期字卡", "字卡后期", "后期贴字", "印文后期",
        "后期白字板", "后期黑底白字卡", "字卡必为后期", "留待后期", "全后期",
        # 剪辑工序族 → 「剪辑X」
        "后期贴片", "后期遮罩", "后期字幕", "后期转场", "后期做", "后期插入", "后期裁掉", "后期跳接",
        "后期弱化", "后期加速", "后期洇染", "后期层", "后期框", "后期LUT", "后期调淡", "后期可叠",
        "后期统一", "后期动效", "后期挂载", "后期手绘", "后期同步",
        # 声音工序族 → 「＋X（声音工序处理）」
        "后期贴尾腔", "后期变形",
    ],
    "normalize_pattern": "",            # 追加一条自定义正则（如 r"后期(?!期)"）

    # ---------- D9 字卡镜负面分档 ----------
    "text_card_shots": [],              # ★ 项目词：显式字卡镜号清单（硬门控 FAIL）
    "text_card_shots_pattern": "",      # ★ 或正则，如 ^(?:1-0[4-7]|2-01)$
    "text_card_auto_note": True,        # 未登记字卡镜时的自动 NOTE（项目已显式枚举时可关）
    "text_card_negative_required_terms": ["简体字", "字形残缺"],
    "text_card_negative_banned_pattern":
        r"(?<![不])文字|题字|calligraphy|\bcharacters\b|\btext\b|可辨字形|对联文字|玉面刻字",
    # 未配置字卡镜号时，用来自动判定的字卡文字标记（只出 NOTE，不判 FAIL）
    "text_card_auto_markers":
        r"字卡|回目|谶文|谶语|定场诗|片名|印文|镌字|玉面四字|篆书刻痕|落版字",

    # ---------- D10 动画性检查 ----------
    # a) 动作曲线词（≥2）—— 用户 20260915 指定 13 词 + 同义补形
    "animation_curve_terms": [
        "预备", "蓄势", "发力", "跟随", "回收", "余摆", "余动", "渐慢", "骤起",
        "由缓到疾", "由急转缓", "回稳",
        "由急到缓", "由缓转疾", "由疾到缓", "先慢后快", "先快后慢", "渐快", "余势", "余韵",
    ],
    # 负向豁免：这些短语里的"匀速/渐变"不构成动作曲线（防误判）
    "animation_curve_exempt_terms": [
        "匀速", "不回缩", "不减速", "不加速", "保持匀速", "连续运动", "恒定速度",
        "无变化", "不变", "均匀", "等速",
    ],
    # b) 主体表演动词（≥2，须出现在【时间轴】内，且不得只在运镜句里）
    "animation_perf_terms": [
        "升起", "沉没", "爬", "翻滚", "摆动", "掀", "颤", "顿", "站稳", "钻出", "扩散", "垂落", "写", "生长",
        "垂下", "低头", "抬头", "回头", "转身", "抬臂", "抬手", "摊掌", "合掌", "拱手", "跪", "躬身", "起身",
        "坐下", "站起", "退步", "踉跄", "点头", "摇头", "睁眼", "闭眼", "垂泪", "落泪", "坠落",
        "飞出", "飞过", "扑", "攀", "爬升", "爬出", "挣", "挤出", "挣脱", "抖", "抖动", "颤动", "震动", "摇晃",
        "摇曳", "飘", "飘落", "飘散", "散开", "聚拢", "收拢", "卷起", "翻卷", "涌动", "荡开", "涟漪",
        "砸落", "触及", "滑落", "掠过", "抽", "拽", "抓", "握", "捧", "举起", "抬起", "落笔", "书写", "写下",
        "勾勒", "描", "蘸", "泼", "洒", "溅", "喷", "腾起", "升腾", "倾斜", "倒下", "塌落", "崩裂", "裂开",
        "绽开", "蔓延", "渗出", "洇开", "晕开", "晕染", "褪色", "褪去", "吹动", "拂", "飘荡", "打转", "旋转",
        "盘旋", "喘", "呼吸", "起伏", "绷", "松开", "扯", "撕", "捻", "翻动", "交叠", "合上", "摊开", "推门",
        "迈", "跨", "奔跑", "行进", "追赶", "逃", "俯身", "弯腰", "蜷缩", "伸展", "伸出", "探出", "缩回",
        "收敛", "凝固", "点亮", "亮起", "暗下", "沉向",
    ],
    # c) 动画性负面禁项（≥2）；c-2) 叙事相关性负面禁项（用户 20260915 追加裁定，须齐备）
    "animation_ban_terms": ["静止帧", "幻灯片式切换", "元素瞬间闪现", "匀速无变化", "画面定格"],
    "narrative_ban_terms": ["与叙事无关的空洞特效", "无意义的风吹草动"],
    "animation_min_curve": 2,
    "animation_min_perf": 2,
    "animation_min_ban": 2,
    # d) 字卡书写性表述（须出现其一）/ 非书写性表述（出现即 FAIL）
    "text_card_write_terms": [
        "逐字书写", "笔迹生长", "写出", "逐字生成", "逐字写出", "笔锋下行", "笔画生长", "书写而出",
        "逐字浮现成字", "逐字落位成字", "一笔一画写出", "逐字由笔尖带出", "笔迹延展", "逐字落墨",
    ],
    "text_card_nonwrite_terms": ["弹出", "叠加", "上屏", "瞬现", "闪现即定", "直接出现", "整体浮现"],
    # e) 动作动机（用户 20260915 追加裁定：动作不是装饰，是台词）
    "motive_key": "动作动机",
    "motive_window": 90,                # 从「动作动机」向后取多少字符找语义词
    "motive_semantic_terms": [
        "含义", "说的是", "象征", "对位", "意味着", "谶", "执", "梦", "命",
        "之义", "隐喻", "呼应", "写照", "句义", "寓",
    ],

    # ---------- D11 交付格式（可选，默认关） ----------
    "check_second_prompt": False,
    "second_prompt_pattern":
        r"【\s*(?:平台\s*prompt|视频\s*prompt|prompt|对照)\s*】"
        r"|^\s*[-*\s>]*\**(?:平台\s*prompt|视频\s*prompt|对照)\**\s*[：:]",

    # ---------- D12 OP 段禁浮空字卡（20260915 甲方裁定A） ----------
    #   判定范围：①条目镜号匹配 op_shot_pattern（或显式列在 op_shot_ids）
    #             ②段块标题匹配 op_scope_pattern（如 segments-*.md 的「段A-02 · …」）
    "op_shot_pattern": r"^1-(?:0[1-9]|1[0-6])$",       # ★ 项目词：OP 镜号 1-01~1-16
    "op_shot_ids": [],                                  # ★ 或显式列镜号
    "op_scope_pattern": r"A-0[1-5](?!\d)|序幕|OP《|OP段|OP 段",   # ★ 项目词：OP 段块（A-01~A-05）
    "op_text_card_terms": ["字卡", "逐字书写", "字位书写", "字卡位", "字卡区",
                           "叠角字卡", "字卡叠角", "逐字上屏", "上屏", "字幕"],
    "op_text_whitelist_terms": ["片名", "注音", "印章", "落印", "玉面", "玉背",
                                "镌字", "鐫字", "印文", "石面刻字"],
    "op_text_negation_terms": ["不", "无", "無", "沒", "没", "禁", "非", "勿", "免", "莫", "绝"],
    "op_text_negation_window": 8,

    # ---------- D13 禁亮词（20260915 甲方裁定B） ----------
    "light_terms": ["一亮", "发亮", "發亮", "闪光", "閃光", "高光", "辉光",
                    "輝光", "反光", "发光", "發光"],
    "light_warn_terms": [],                             # 可选：亮起/点亮 等邻类词，只出 WARN
    "light_negation_terms": ["不", "无", "無", "沒", "没", "禁", "非", "勿",
                             "免", "莫", "别", "戒", "绝"],
    "light_negation_window": 8,
    "light_context_exempt_terms": ["负面", "禁项", "即废", "专属", "不得", "严禁", "禁用", "禁止",
                                   "回避", "不出现", "裁定", "词表", "替换", "纪律", "铁律",
                                   "门控", "豁免", "基线"],
    "light_context_window": 40,
    "light_enum_min": 2,
    "light_qc_line_pattern":
        r"\*\*(?:参数|验收|失败改法|判废标准|判废要点|判废经历|判废记录|判废|看什么|废片判据|"
        r"测试目的|测试条目|降级路径|读法|口播零改写|负面分档|抽卡建议|动镜参考组纪律|"
        r"文学闸口径注)\*\*|【(?:参数|验收)】|废片判据|失败改法|判废标准|判废要点|判废经历|"
        r"判过|台账|溯源",
    "light_negative_enum_sentinels": ["3D渲染", "厚涂", "赛璐璐"],
    "light_negative_block_pattern":
        r"(?:\*\*)?(?:负面词?|负面\s*prompt|负面（内嵌同块）|统一负面整串|负面块|负面串|禁项)",
    "light_storyboard_pattern": r"故事板|分镜故事板|线稿|草图生成prompt",

    # ---------- 承载型行豁免（20260917 甲方要求：清单/台账类文件**引用禁词**是正确做法，不得判 FAIL） ----------
    #   ① 行级：命中行本身以 负面/负面词/判废/禁/D4/D13 等标签开头 → 承载型行；
    #      或处于同一「负面词…」标签段落内（至空行/标题/围栏/新字段行为止）；
    #      或该行是纯枚举（逗号/顿号分隔 ≥N 项、无句读、无正文动词）= 词表列举。
    #   ② 文件级：文件名匹配 carrier_files_pattern（清单/台账类）→ 该文件 D4/D13 一律降为 NOTE；
    #      文件名匹配 strict_files_pattern（prompt 执行件）→ 维持严格（**strict 优先**）。
    "carrier_check_codes": ["D4", "D13"],
    "carrier_open_labels": ["负面词", "负面", "禁项", "禁用", "禁止", "判废", "废片", "失败改法",
                            "词表", "例外", "回避", "不进", "D4", "D8", "D13"],
    "carrier_files_pattern": r"标签总表|台账|清单|自检卡|门控回执",
    "strict_files_pattern": r"(?:^|/)prompts-|(?:^|/)segments-|(?:^|/)storyboard-|/m4-prompts/|m4-分镜表",
    "carrier_enum_min_tokens": 3,
    "carrier_enum_max_token_len": 12,
    "carrier_prose_pattern": r"画面|镜头|生成|绘制|呈现|改为|替换|不得|即废|无光之戏|音乐|旁白",
    # 行内 QC/方法性标签（判废要点/废片判据/失败改法/参数…，可出现在「- **备注**：判废要点：…」等句中）
    # → 该行同样按承载型处理（这类行引用禁词＝陈述判废标准，不是违规）
    "carrier_inline_label_pattern":
        r"(?:^|[\s\-*|｜>（(【\[、:：])[\*_]{0,2}"
        r"(?:判废|废片|失败改法|验收|方法|词表|禁项|禁用|禁止|豁免|例外|回写|D4|D8|D13)"
        r"(?:要点|标准|判据|记录|经历|清单|原则|口径)?[\*_]{0,2}\s*[:：＝=|]",

    # ---------- 通道档（用户裁定 20260921 · 双通道并存 · 硬规则 #42） ----------
    #   channel=A → 通道 A（广告/科普/科研视频）：**自动跳过剧集专属检查** D12/D13/D10
    #     （依据 docs/DUAL-CHANNEL-AUDIT.md：#33 OP 文字白名单仅剧集 OP/ED；#34 禁亮词仅
    #      AI 原生水墨无光源风格、通道 A 的 light_terms 默认置空；#28 动画性纪律仅 AI 原生动画路径，
    #      真人实拍/产品摄影/纯图表/专业后期成片不适用）——防"浮空字卡/亮词"对广告线**误报**。
    #   channel=B → 剧集（或留空）：D1–D13 全套严格（D10 仍受 --animation-baseline 控制）。
    #   通道 A 档另可按 #26 限定语放行「后期/剪辑」表述（forbidden_terms/normalize_terms 置空）；
    #   并可按 #24 限定语另附「专业交接单」（不计第二版本 prompt，check_second_prompt 保持 false）。
    #   模板：templates/prompt-delivery-config-channelA.json（A 档默认档）
    #   ⚠️ 通道 A 的**全通道通用**门控不放松：D1/D2/D3/D9/D7/D11/广告法合规照旧。
    "channel": "",

    # ---------- 门控自述行（NOTE）—— 通道档等运行时说明写这里 ----------
    "notes": [],
}


def deep_merge(base, over):
    """递归合并配置：dict 逐键合并，其余（含列表）整体覆盖。"""
    out = dict(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


class ConfigError(Exception):
    """配置文件不可用（JSON 语法错 / 读取失败 / 显式指定的文件不存在）。

    属**无法判定**：调用方必须 `exit 2`。**不得静默回退默认词表继续跑**——
    实测静默回退会丢光项目词表与 exclude_dirs（34 文件被扫成 119 文件、D10 假 FAIL 翻倍）。
    """


def load_config(run_dir, cfg_path=None):
    """读 <run目录>/prompt-delivery-config.json（可选）；返回 (生效配置, 实际配置文件或 None)。

    T3（20260921）：配置存在但**不可解析** ⇒ 抛 ConfigError（调用方 exit 2，绝不静默回退）。
    """
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))          # 深拷贝默认值
    path = cfg_path or os.path.join(run_dir, "prompt-delivery-config.json")
    used = None
    if cfg_path and not os.path.isfile(path):
        raise ConfigError(f"显式指定的配置文件不存在 —— {path}"
                          "（`--config` 路径写错；不指定则默认读 <run目录>/prompt-delivery-config.json）")
    if os.path.isfile(path):
        try:
            with open(path, encoding="utf-8-sig") as fh:
                raw = fh.read()
        except Exception as e:  # noqa: BLE001
            raise ConfigError(f"配置文件读取失败：{path} —— {e}")
        try:
            user = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ConfigError(
                f"配置文件 JSON 解析失败：{path} 第 {e.lineno} 行第 {e.colno} 列 —— {e.msg}。"
                "修复指引：①按行:列定位补/删逗号、引号、括号；②自检命令 "
                "python -X utf8 -c \"import json,io;json.load(io.open(r'" + path + "',encoding='utf-8-sig'))\"；"
                "③确不使用则改名或删除该文件以回退通用词表——"
                "**脚本不会静默回退默认词表**（带病继续跑会产出假 FAIL/假 PASS）")
        if not isinstance(user, dict):
            raise ConfigError(f"配置文件顶层必须是 JSON 对象 {{...}}：{path} —— 实际为 {type(user).__name__}")
        cfg = deep_merge(cfg, user)
        used = path
    return cfg, used


# ============================================================================
# 一·二、通道档（用户裁定 20260921 · 双通道并存 · 硬规则 #42 · 范围升级含通道 C）
#   ⚠️ **严格优先**：只有**显式声明**通道才缩小检查范围；**留空/未声明 ⇒ 全套严格**
#      （防"没写 channel 就静默关闸"——那会让 D12/D13/D10 对既有项目整体失效）。
#      · A（通道 A 广告/科普/科研视频）  ⇒ 跳过剧集专属 **D10＋D12**（#28／#33）
#      · A+C（广告·音乐混用）            ⇒ 跳过剧集专属 **D10＋D12**
#      · C（通道 C 音乐驱动·横向）        ⇒ **只跳 D12**（无 OP 文字白名单）；**D10 保留**
#                                          （MV 也能是动画路径）；D13 不由通道决定（见下）
#      · B（剧集）/ A+B（混用）           ⇒ 全套严格
#      · 留空 / 未声明                    ⇒ 全套严格（既有行为不变）
#   D13 禁亮词（#34）**不由通道名决定**：只由 config 的 `light_terms` 是否为空决定——
#      通道 A 默认档把词表置空（`templates/prompt-delivery-config-channelA.json`）⇒ 天然不误报；
#      项目显式声明了亮词表（如红楼梦）⇒ 即便通道名写 A 也照跑（避免"写个通道名就整体关闸"）。
#   依据：docs/DUAL-CHANNEL-AUDIT.md（#28 仅 AI 原生动画；#33 仅剧集 OP/ED；#34 仅 AI 原生「无光源」风格）。
# ============================================================================
#: 剧集专属检查（标注依据见 DUAL-CHANNEL-AUDIT；跳过时必须在输出写明依据）
CHANNEL_SERIES_ONLY_CHECKS = {
    "D10": "动画性纪律（硬规则 #28）—— 仅 AI 原生动画路径；真人实拍/产品摄影/纯图表/专业后期不适用",
    "D12": "OP 段禁浮空字卡（硬规则 #33）—— 仅剧集 OP/ED 段；通道 A/C 片头允许 slogan 卡/落版/参数卡",
    "D13": "禁亮词（硬规则 #34）—— 仅 AI 原生「无光源」风格；词表空（通道 A 默认档）即不评估",
}


def _norm_channel(v):
    """归一通道值：'' / 'A' / 'B' / 'C' / 'A+B' / 'A+C' / 'B+C' / 'A+B+C'（大小写、全角、+／、/ 分隔容错）。

    通道 A＝广告/科普/科研视频；通道 B＝剧集/叙事；通道 C＝音乐驱动（横向·与 A/B 均交集）。
    T4-a（20260921）：**含 B 的组合保留全部字母**（A+B+C 不得丢 C 信息，B+C 不得退化成 B）；
    **空 = 未声明**（调用方须按"全套严格"处理，不得当作 A 档）。
    """
    s = ("" if v is None else str(v)).strip().upper().translate(str.maketrans("ＡＢＣ＋／", "ABC+/"))
    if not s:
        return ""
    has_a, has_b, has_c = ("A" in s), ("B" in s), ("C" in s)
    if has_b:                                    # 含 B ⇒ 保留全部字母（严格档，不丢 C）
        return "+".join(x for x, on in (("A", has_a), ("B", has_b), ("C", has_c)) if on)
    if has_a and has_c:
        return "A+C"
    if has_a:
        return "A"
    if has_c:
        return "C"
    return ""


def _channel_scope(cfg):
    """通道口径**唯一事实源**（scan() 与 main() 共用，防两处判定分叉——20260921 曾因此出过
    "scan 判 A、main 判严格"的静默漏跑）。

    返回 (ch, skip_d10_d12, skip_d12_only)，口径 = **严格优先**：
      · 空/未声明                     ⇒ 不跳过（全套严格）
      · 含 B 的组合（B／A+B／B+C／A+B+C）⇒ 不跳过（全套严格；A/C 信息仅用于自述）
      · 仅 A（含 A+C）                 ⇒ 跳 D10＋D12（#28／#33 剧集专属）
      · C 单通道                       ⇒ 只跳 D12（MV 也能是动画路径 ⇒ D10 保留）
      · D13 不由通道名决定（只由 light_terms 是否为空决定，见 scan()）
    """
    ch = _norm_channel(cfg.get("channel"))
    has_a, has_b, has_c = ("A" in ch), ("B" in ch), ("C" in ch)
    skip_d10_d12 = (has_a and not has_b)
    skip_d12_only = (has_c and not has_a and not has_b)
    return ch, skip_d10_d12, skip_d12_only


def _channel_note(cfg):
    """通道档自述（供横幅打印；通道A档跳过声明在 scan() 内**逐文件**出 NOTE）。"""
    ch = _norm_channel(cfg.get("channel"))
    return ch


# ============================================================================
# 二、通用工具
# ============================================================================
def _rx_search(text, patterns):
    """任一正则片段命中即真（词表项按正则片段处理；写坏了退化为字面量匹配，不崩）。"""
    for p in patterns or []:
        try:
            if re.search(p, text, re.I):
                return True
        except re.error:
            if p in text:
                return True
    return False


def _field(body, name):
    """取条目内某字段的整段文本（到下一个字段或条目尾为止）。兼容 **字段**： 与 【字段】："""
    pat = (r"(?m)^\s*-?\s*(?:\*\*" + re.escape(name) + r"\*\*|【" + re.escape(name) + r"】)\s*[：:](.*?)"
           r"(?=^\s*-?\s*(?:\*\*[^*]+\*\*|【[^】]+】)|\Z)")
    m = re.search(pat, body, re.S)
    return m.group(1).strip() if m else ""


def _field_line(body, name):
    """取单行字段（负面/参数等通常一整行）。"""
    pat = (r"(?m)^\s*-?\s*(?:\*\*" + re.escape(name) + r"\*\*|【" + re.escape(name) + r"】)\s*[：:](.*)$")
    m = re.search(pat, body)
    return m.group(1).strip() if m else ""


def shot_entries(txt, cfg):
    """按 ### 标题切条目，只保留**锚名匹配**的镜头条目（锚名由 shot_heading_pattern 配置）。"""
    lines = txt.splitlines()
    starts = [i for i, l in enumerate(lines) if l.startswith("### ") or l.startswith("###\t")]
    out = []
    for k, s in enumerate(starts):
        e = starts[k + 1] if k + 1 < len(starts) else len(lines)
        head = lines[s][3:].strip()
        if not re.search(cfg["shot_heading_pattern"], head, re.I):
            continue
        m = re.search(cfg["shot_id_pattern"], head)
        out.append({
            "head": head,
            "sid": m.group(1) if m else head[:24],
            "line": s + 1,
            "body": "\n".join(lines[s + 1:e]),
        })
    return out


def _neg_field(line, cfg):
    """单行是否为「负面」字段行。"""
    try:
        return bool(re.search(cfg["negative_field_pattern"], line))
    except re.error:
        return line.strip().startswith("负面")


def neg_lines(body, cfg):
    """条目的「负面」字段行列表。"""
    return [ln for ln in body.splitlines() if _neg_field(ln, cfg)]


def _exempt(line, cfg):
    """规则自述行/变更记录行豁免（不得据以判 FAIL）。"""
    return any(t in line for t in cfg["allow_line_terms"])


def list_files(run_dir, patterns, exclude_dirs, explicit):
    """收集待检文件：显式文件优先，否则按 file_globs 扫描（跳过 exclude_dirs）。

    返回 (files, missing)。显式给出但不存在的路径进 missing —— 调用方必须据此 exit 2，
    **绝不静默跳过**（"扫了 0 个文件却报 PASS"比报错更危险）。
    """
    if explicit:
        out, missing = [], []
        for f in explicit:
            p = f if os.path.isabs(f) else os.path.join(run_dir, f)
            (out if os.path.isfile(p) else missing).append(p)
        return sorted(out), missing
    found = set()
    for pat in patterns:
        for p in _glob.glob(os.path.join(run_dir, "**", pat), recursive=True):
            found.add(os.path.normpath(p))
    if not found:   # 兜底：一个都没命中时扫全部 .md，避免"扫了 0 个文件却报 PASS"
        for p in _glob.glob(os.path.join(run_dir, "**", "*.md"), recursive=True):
            found.add(os.path.normpath(p))
    keep = []
    for p in sorted(found):
        parts = set(os.path.normpath(p).split(os.sep))
        if any(d in parts for d in exclude_dirs):
            continue
        if os.path.isfile(p):
            keep.append(p)
    return keep, []


# ============================================================================
# 三、逐项检查（D1–D13）
# ============================================================================
def check_d1(entry, cfg, issues):
    """D1 SOP 字段完整：视频条目须含 参考/风格/时间轴/口播/声音/负面/参数；图片条目须负面内嵌。"""
    b, tag = entry["body"], f"[镜头 {entry['sid']} L{entry['line']}]"
    is_image = (re.search(cfg["image_entry_pattern"], b, re.I)
                and not re.search(cfg["video_entry_pattern"], b, re.I))
    if is_image:
        if not _rx_search(b, cfg["field_aliases"].get("负面", [])):
            issues.append(f"D1 FAIL {tag}: 图片条目须在同一 prompt 块内内嵌「负面」")
        return
    for f in cfg["required_video_fields"]:
        pats = cfg["field_aliases"].get(f) or [re.escape(f)]
        if not _rx_search(b, pats):
            issues.append(f"D1 FAIL {tag}: 视频条目缺 SOP 字段「{f}」"
                          f"（可写字段名或等价写法：{'/'.join(pats[:6])}）")


def check_d2(entry, cfg, issues):
    """D2 @标记贯穿：提到"图片N"就必须同步写 "@图片N"（素材指代不得与正文脱节）。"""
    b = entry["body"]
    if re.search(cfg["image_ref_pattern"], b) and not re.search(cfg["image_at_pattern"], b):
        issues.append(f"D2 FAIL [镜头 {entry['sid']} L{entry['line']}]: 提到图片N但全文无 @图片N 标记"
                      "（指代与正文脱节写法）")


def check_d3(entry, cfg, warns):
    """D3 负面与 prompt 正文同代码块：条目内有代码块时，负面不得写在块外。"""
    b = entry["body"]
    if "```" not in b:
        return
    fences = re.findall(r"```(.*?)```", b, re.S)
    outer = [l for l in b.splitlines() if _neg_field(l, cfg) and not any(l in f for f in fences)]
    if outer:
        warns.append(f"D3 WARN [镜头 {entry['sid']} L{entry['line']}]: "
                     f"{len(outer)} 处「负面」写在代码块外（用户要求负面与 prompt 正文同块）")


def check_d4_lines(lines, cfg, issues, warns, notes=None, tier_info=None):
    """D4 废止表述禁词（变更/废止/禁止/作废 记录行豁免；
    承载型行与清单·台账类文件降为 NOTE——引用禁词是正确做法）。"""
    for w in cfg["forbidden_terms"]:
        for i, ln in enumerate(lines, 1):
            if w not in ln or _exempt(ln, cfg):
                continue
            msg = f"出现已废止表述「{w}」"
            down, why = _downgrade("D4", i, cfg, tier_info)
            if down:
                (notes if notes is not None else warns).append(
                    f"D4 NOTE L{i}: 承载型引用（{why}）{msg}——不计 FAIL（引用禁词=正确做法）")
            else:
                issues.append(f"D4 FAIL L{i}: {msg}")


def check_d4_exclusive(lines, cfg, issues, warns):
    """D4-EXT 专属空间标记越界（★ 项目词由 exclusive_space_terms 注入；未配置则不检查）。"""
    if not cfg["exclusive_space_terms"]:
        return
    cur_shot, cur_scope = None, None
    heading_re = re.compile(r"^#{1,6}\s*(.*)$")
    for i, ln in enumerate(lines, 1):
        m = heading_re.match(ln)
        if m:
            title = m.group(1).strip()
            if re.search(cfg["shot_heading_pattern"], title, re.I):
                sid = re.search(cfg["shot_id_pattern"], title)
                cur_shot = sid.group(1) if sid else title[:24]
            else:
                cur_scope = title                 # 非镜头标题 = 作用域标题（如"一、序幕 OP"）
            continue
        for item in cfg["exclusive_space_terms"]:
            term = item.get("term", "")
            if not term or term not in ln or _exempt(ln, cfg):
                continue
            if cfg.get("exclusive_space_negative_exempt", True) and _neg_field(ln, cfg):
                continue                          # 写在负面字段里 = 列为禁项（正确用法）
            allowed_shots = set(item.get("allowed_shots") or [])
            scope_pat = item.get("allowed_scope_pattern") or ""
            note = item.get("note") or ""
            if cur_shot and cur_shot in allowed_shots:
                continue
            if scope_pat and (re.search(scope_pat, cur_scope or "", re.I)
                              or re.search(scope_pat, cur_shot or "", re.I)):
                continue
            where = ((f"仅限镜号 {'/'.join(sorted(allowed_shots))}" if allowed_shots else "")
                     + (f" 或作用域「{scope_pat}」" if scope_pat else "")).strip()
            tail = f"· {note}" if note else ""
            if not cur_shot and not cur_scope:
                warns.append(f"D4 WARN L{i}: 专属空间标记「{term}」出现但无法定位镜头/作用域"
                             f"（应{where or '限定作用域'}）{tail}")
            else:
                issues.append(f"D4 FAIL L{i}: 专属空间标记「{term}」越界出现"
                              f"（当前：镜 {cur_shot or '-'} / 作用域 {cur_scope or '-'}；"
                              f"应{where or '限定作用域'}）{tail}")


def check_d5(lines, code_blocks, cfg, issues, warns):
    """D5 故事板纪律：**只查代码块内的 prompt 正文**（散文行不算）。"""
    in_block = set()
    for cb in code_blocks:
        for ln in cb.splitlines():
            in_block.add(ln.strip())
    for i, ln in enumerate(lines, 1):
        if ln.strip() not in in_block:
            continue
        if not any(mk in ln for mk in cfg["storyboard_markers"]):
            continue
        if not any(t in ln for t in cfg["storyboard_trigger_terms"]):
            continue
        ctx = "\n".join(lines[max(0, i - 1):i + 8])
        if not any(t in ctx for t in cfg["storyboard_required_terms"]):
            issues.append(f"D5 FAIL L{i}: 故事板 prompt 未写「{'/'.join(cfg['storyboard_required_terms'])}」"
                          "（总指令须前置 黑白单线线稿/明暗仅用简单排线）")
        if not any(t in ctx for t in cfg["storyboard_shot_terms"]):
            issues.append(f"D5 FAIL L{i}: 故事板 prompt 未要求逐格标注"
                          f"「{'/'.join(cfg['storyboard_shot_terms'])}」")
        nailed = [w for w in cfg["storyboard_negative_terms"] if w in ctx]
        if len(nailed) < cfg["storyboard_negative_min"]:
            warns.append(f"D5 WARN L{i}: 故事板负面线稿钉死词仅 {len(nailed)}"
                         f"/{cfg['storyboard_negative_min']}（须含 "
                         f"{', '.join(cfg['storyboard_negative_terms'])}）")


def check_d6(lines, cfg, warns):
    """D6 字卡口径：禁「字卡后期上屏」等旧口径（已改为模型原生生成）。"""
    for i, ln in enumerate(lines, 1):
        if _exempt(ln, cfg):
            continue
        for w in cfg["text_card_legacy_terms"]:
            if w in ln:
                warns.append(f"D6 WARN L{i}: 仍写「{w}」（字卡已改为含于 prompt 由模型原生生成）")
                break


def check_d7(lines, cfg, issues):
    """D7 校勘红线（★ 项目词由 correction_red_terms / m5-校勘红线.txt 注入；默认空 = 不检查）。"""
    for w in cfg["correction_red_terms"]:
        for i, ln in enumerate(lines, 1):
            if w in ln and not any(k in ln for k in cfg["correction_exempt_terms"]):
                issues.append(f"D7 FAIL L{i}: 出现未校勘句「{w}」")


def check_d8(lines, cfg, issues):
    """D8 后期表述归一（★ normalize_terms 可扩展；变更/废止/禁止/作废 记录行豁免）。"""
    pats = list(cfg["normalize_terms"])
    if cfg.get("normalize_pattern"):
        pats.append(cfg["normalize_pattern"])
    for p in pats:
        try:
            rx = re.compile(p, re.I)
        except re.error:
            rx = None
        for i, ln in enumerate(lines, 1):
            if _exempt(ln, cfg):
                continue
            if (rx.search(ln) if rx else (p in ln)):
                issues.append(
                    f"D8 FAIL L{i}: 出现已归一表述「{p}」"
                    "（字/印/字卡族→「字卡（印文）含于prompt由模型原生生成」；"
                    "剪辑工序族→「剪辑X」；声音工序族→「＋X（声音工序处理）」）")


def _is_text_card_shot(sid, cfg):
    """字卡镜判定：① 配置清单/正则（硬门控）② 未配置则返回 False（自动判定只用于 NOTE）。"""
    if sid in set(cfg["text_card_shots"]):
        return True
    if cfg.get("text_card_shots_pattern"):
        try:
            return bool(re.search(cfg["text_card_shots_pattern"], sid))
        except re.error:
            return False
    return False


def check_d9(entry, cfg, issues, warns, notes):
    """D9 字卡镜负面分档：字卡镜禁 text 类，改钉字形类。

    字卡镜来源：① 配置 text_card_shots / text_card_shots_pattern → **硬门控 FAIL**
                ② 未配置时按 text_card_auto_markers 自动判定 → 只出 NOTE（避免项目词表缺失误伤）
    """
    b, sid, tag = entry["body"], entry["sid"], f"[镜头 {entry['sid']} L{entry['line']}]"
    negtxt = "\n".join(neg_lines(b, cfg))
    if not negtxt:
        return
    req = cfg["text_card_negative_required_terms"]
    has_shape = all(t in negtxt for t in req)
    try:
        banned = re.search(cfg["text_card_negative_banned_pattern"], negtxt)
    except re.error:
        banned = None
    if _is_text_card_shot(sid, cfg):
        if not has_shape:
            issues.append(f"D9 FAIL {tag}: 字卡镜负面缺「{', '.join(req)}」字形类禁项")
        if banned:
            issues.append(f"D9 FAIL {tag}: 字卡镜负面仍含 text 类禁项「{banned.group(0)}」"
                          "（该镜该有字，须改钉字形类禁项）")
    elif has_shape and banned:
        # 自认字卡镜（负面已钉字形类）却同时保留 text 类 → 口径冲突
        warns.append(f"D9 WARN {tag}: 负面已声明「{req[0]}」却又含 text 类禁项"
                     f"「{banned.group(0)}」，口径冲突（字卡镜应改钉字形类）")
    elif not has_shape and cfg.get("text_card_auto_note", True):
        try:
            # OP 段（D12 硬门控已覆盖"画面不得出现文字"）不再出「疑似字卡」NOTE：
            # 1-04~1-07 这类**被裁定删出字卡镜清单**的 OP 镜，条目内仍会保留
            # 「无字卡／镌字之约／谶卡空版」等字样，自动判定必然误报。
            if _is_op_shot(entry["sid"], cfg):
                return
            if re.search(cfg["text_card_auto_markers"], b):
                notes.append(f"D9 NOTE {tag}: 疑似字卡条目但负面未见「{', '.join(req)}」"
                             "（该镜未登记为字卡镜：text_card_shots / text_card_shots_pattern；"
                             "仅提示，不计 FAIL）")
        except re.error:
            pass


def _tl_region(body, cfg):
    """取条目/段块内【时间轴】正文（兼容「**时间轴**：」「**时间轴prompt（…）**：」「【时间轴】」）。"""
    pat = (r"(?ms)^\s*-?\s*(?:\*\*时间轴[^*]*\*\*|【时间轴】)\s*[：:]?(.*?)"
           r"(?=^\s*-?\s*(?:\*\*[^*]+\*\*|【[^】]+】)|\Z)")
    m = re.search(pat, body)
    return m.group(1).strip() if m else ""


def _is_op_shot(sid, cfg):
    """OP 镜号判定（D12 用）：显式清单 or op_shot_pattern。"""
    if sid in set(cfg.get("op_shot_ids") or []):
        return True
    pat = cfg.get("op_shot_pattern") or ""
    if pat:
        try:
            return bool(re.search(pat, sid, re.I))
        except re.error:
            return False
    return False


def op_blocks(txt, cfg):
    """D12 待检块：①### 镜头条目（镜号匹配 OP）②## 段块（标题匹配 op_scope_pattern）。"""
    lines = txt.splitlines()
    heads = [i for i, l in enumerate(lines) if re.match(r"^#{1,6}\s", l)]
    out = []
    for k, i in enumerate(heads):
        e = heads[k + 1] if k + 1 < len(heads) else len(lines)
        title = re.sub(r"^#{1,6}\s*", "", lines[i]).strip()
        m = re.search(cfg["shot_id_pattern"], title)
        sid = m.group(1) if m else None
        is_shot = bool(re.search(cfg["shot_heading_pattern"], title, re.I))
        if is_shot and sid:
            if _is_op_shot(sid, cfg):
                out.append((f"镜{sid}", i + 1, "\n".join(lines[i + 1:e])))
        elif not is_shot:
            pat = cfg.get("op_scope_pattern") or ""
            if pat:
                try:
                    hit = bool(re.search(pat, title, re.I))
                except re.error:
                    hit = pat in title
                if hit:
                    out.append((f"段块「{title[:24]}」", i + 1, "\n".join(lines[i + 1:e])))
    return out


def check_d12(txt, cfg, issues):
    """D12 OP 段禁浮空字卡：OP 条目/段块的【时间轴】不得含字卡字样（白名单词同句豁免）。"""
    for label, line, body in op_blocks(txt, cfg):
        tl = _tl_region(body, cfg)
        if not tl:
            continue
        for seg in re.split(r"[；;。\n]", tl):
            seg = seg.strip()
            if not seg or _exempt(seg, cfg):
                continue
            hit = [t for t in cfg["op_text_card_terms"] if t in seg]
            if not hit:
                continue
            if any(w in seg for w in cfg["op_text_whitelist_terms"]):
                continue
            # 否定式豁免：如「全程无字幕无水印」「画面无字卡」——禁项表述，不是要上字卡
            neg = any(
                any(w in seg[max(0, seg.find(t) - cfg["op_text_negation_window"]):seg.find(t)]
                    for w in cfg["op_text_negation_terms"])
                for t in hit
            )
            if neg:
                continue
            issues.append(
                f"D12 FAIL [{label} L{line}]: OP 段【时间轴】出现浮空字卡/诗句字幕字样「{hit[0]}」"
                f"（20260915 甲方裁定A：OP 段画面内禁浮空字卡与诗句字幕，仅允许片头标题字"
                f"〔{'/'.join(cfg['op_text_whitelist_terms'][:4])}〕与物件上的字"
                f"〔玉面镌字/石面刻字〕；谶语·诗词逐字上屏移至正片 C5 段）"
                f" ｜ 原句：{seg[:70]}")


def _bare_neg_enum(ln, cfg):
    """裸负面串行判定：一行内命中 ≥2 个通用负面哨兵词 = 禁项枚举行（D13 整行豁免）。"""
    sents = cfg.get("light_negative_enum_sentinels") or []
    return sum(1 for s in sents if s in ln) >= 2


def _light_hits(ln, cfg):
    """该行中**未被否定、未被上下文豁免**的亮词命中：[(术语, 位置)]。"""
    out = []
    for t in cfg["light_terms"]:
        for m in re.finditer(re.escape(t), ln):
            pre_n = ln[max(0, m.start() - cfg["light_negation_window"]):m.start()]
            if any(w in pre_n for w in cfg["light_negation_terms"]):
                continue
            pre_c = ln[max(0, m.start() - cfg["light_context_window"]):m.start()]
            if any(w in pre_c for w in cfg["light_context_exempt_terms"]):
                continue
            out.append((t, m.start()))
    return out


def _light_rule_line(ln, cfg):
    """规则/词表描述行 → D13 豁免，**必须同时满足语境条件**（T2 · 20260921 修正）：
      ① 行首承载标签（负面/禁项/判废…，`_is_carrier_label`）或行内 QC/方法性标签
         （`判废要点：…`，`_inline_qc_label`）；
      ② 纯词表枚举行（逗号分隔 ≥N 项、无句读、无正文动词，`_enum_line`）；
      ③ Markdown 表首格只由亮词构成（「替换词表」行，如 `| 反光 | 映墨 |`）。

    ⛔ **仅凭"一行 ≥light_enum_min 个亮词"不得豁免**——那会把真违规句
    （如 `画面微微一亮，桌面高光反射明显`，2 个亮词）整行放过。豁免只认语境标记；
    `light_negation_window` / `light_context_window` 两套既有豁免不受影响（只加严、不放松）。
    """
    hits = _light_hits(ln, cfg)
    if not hits:
        return False
    if _is_carrier_label((ln or "").strip(), cfg) or _inline_qc_label(ln, cfg) or _enum_line(ln, cfg):
        return True
    m = re.match(r"^\s*\|\s*([^|]+?)\s*\|", ln)
    if m and any(t in m.group(1) for t, _ in hits):
        residue = m.group(1)
        for t, _ in hits:
            residue = residue.replace(t, "")
        residue = re.sub(r"[／/\s（）()、,，\-—｜|正面负面]", "", residue)
        if not residue:
            return True
    return False


# ---------- 承载型行/文件判定（清单·台账类文件**引用禁词**的正当用法，20260917 甲方要求） ----------
def _file_tier(path, cfg):
    """文件档位：strict（prompt 执行件，维持严格）/ carrier（清单·台账类，D4/D13 降为 NOTE）/ normal。"""
    rel = os.path.abspath(path).replace("\\", "/")
    try:
        if cfg.get("strict_files_pattern") and re.search(cfg["strict_files_pattern"], rel):
            return "strict"          # strict 优先：prompt 执行件不被清单规则削弱
        if cfg.get("carrier_files_pattern") and re.search(cfg["carrier_files_pattern"], os.path.basename(rel)):
            return "carrier"
    except re.error:
        pass
    return "normal"


def _is_carrier_label(s, cfg):
    """行是否以承载标签开头（负面/负面词/判废/禁…/D4/D13）；剥掉列表符·表格管·加粗符后再判。"""
    t = re.sub(r"^\s*(?:[-*+>]\s*|\d+[.、)]\s*)+", "", s or "")
    t = re.sub(r"^[\|\s]+", "", t).lstrip("*_# ").strip()
    return any(t.startswith(lb) for lb in (cfg.get("carrier_open_labels") or []))


def _inline_qc_label(ln, cfg):
    """行内 QC/方法性标签（判废要点/废片判据/失败改法/参数…）→ 该行按承载型处理。
    覆盖「判废要点」不在行首的情形（如 `- **备注**：判废要点：出现急停悬停即废。`）——
    这类行是在**陈述判废标准**、引用禁词属正确做法，不得判 FAIL。"""
    pat = cfg.get("carrier_inline_label_pattern") or ""
    if not pat:
        return False
    try:
        return bool(re.search(pat, ln or ""))
    except re.error:
        return False


def _enum_line(ln, cfg):
    """纯枚举行：逗号/顿号分隔 ≥N 项、无句读、无正文动词 → 视为「词表列举」（承载型）。"""
    s = (ln or "").strip().strip("`").strip()
    if not s or any(c in s for c in "。！？；"):
        return False
    try:
        if re.search(cfg.get("carrier_prose_pattern") or r"(?!x)x", s):
            return False
    except re.error:
        pass
    toks = [t.strip() for t in re.split(r"[,，、]", s) if t.strip()]
    if len(toks) < cfg.get("carrier_enum_min_tokens", 3):
        return False
    return all(len(t) <= cfg.get("carrier_enum_max_token_len", 12) for t in toks)


def carrier_line_flags(lines, cfg):
    """逐行标记「承载型行」：标签行本身、标签段落内的续行（负面词串行即在此）、纯枚举行。"""
    flags = [False] * len(lines)
    open_block = False
    for i, ln in enumerate(lines):
        s = (ln or "").strip()
        if s == "" or s.startswith("#") or s.startswith("```"):
            open_block = False                       # 空行/标题/围栏 = 承载段落结束
            continue
        is_label = _is_carrier_label(s, cfg)
        if re.match(r"^\s*[-*+]\s*\*\*", ln) and not is_label:
            open_block = False                       # 新字段行 = 上一段结束
        if is_label:
            flags[i] = True
            open_block = True
            continue
        if _inline_qc_label(ln, cfg):
            flags[i] = True                          # 行内 QC/方法性标签行（不开新承载段落）
            continue
        if open_block:
            flags[i] = True                          # 标签段落内的续行
            continue
        if _enum_line(ln, cfg):
            flags[i] = True
    return flags


def _downgrade(code, lineno, cfg, tier_info):
    """该行该检查项是否降级为 NOTE（承载型行 / 清单·台账类文件）。返回 (bool, 原因)。"""
    if not tier_info or code not in (cfg.get("carrier_check_codes") or []):
        return False, ""
    if tier_info.get("tier") == "carrier":
        return True, "清单/台账类承载文件"
    flags = tier_info.get("carrier") or []
    if 1 <= lineno <= len(flags) and flags[lineno - 1]:
        return True, "承载型行（负面词串/禁项枚举/清单语境）"
    return False, ""


def check_d13(lines, cfg, issues, warns, notes=None, tier_info=None):
    """D13 禁亮词：正文不得出现「一亮/发亮/闪光/高光/辉光/反光/发光」（禁项/否定/QC 行豁免；
    承载型行与清单·台账类文件降为 NOTE——引用禁词是正确做法）。"""
    terms = cfg["light_terms"]
    try:
        qc_re = re.compile(cfg["light_qc_line_pattern"])
    except re.error:
        qc_re = None
    try:
        sb_re = re.compile(cfg["light_storyboard_pattern"])
    except re.error:
        sb_re = None
    try:
        nb_re = re.compile(cfg["light_negative_block_pattern"])
    except re.error:
        nb_re = None
    for i, ln in enumerate(lines, 1):
        if _neg_field(ln, cfg) or _bare_neg_enum(ln, cfg) or _light_rule_line(ln, cfg):
            continue
        if nb_re and nb_re.search(ln):
            continue
        if qc_re and qc_re.search(ln):
            continue
        if sb_re and sb_re.search(ln) and "负面" in ln:
            continue
        hits = _light_hits(ln, cfg)
        if hits:
            body = (f"正文出现「亮」类表述「{hits[0][0]}」"
                    "（20260915 甲方裁定B：水墨风格无光源，禁 一亮/发亮/闪光/高光/辉光/反光/发光；"
                    "改用墨的语言——渐浓／渐沉／洇开／褪淡／沉深一分／退回原色）"
                    f" ｜ 原句：{ln.strip()[:80]}")
            down, why = _downgrade("D13", i, cfg, tier_info)
            if down:
                (notes if notes is not None else warns).append(
                    f"D13 NOTE L{i}: 承载型引用（{why}）{body}——不计 FAIL（引用禁词=正确做法）")
            else:
                issues.append(f"D13 FAIL L{i}: {body}")
        for t in (cfg.get("light_warn_terms") or []):
            if t in ln:
                warns.append(f"D13 WARN L{i}: 出现邻类亮词「{t}」（建议改墨的语言；非本次裁定禁项）")
                break


def check_d11(entry, cfg, issues):
    """D11 交付格式（默认关）：一镜只允许一条可复制 prompt，出现第二版本 = FAIL。"""
    b = entry["body"]
    try:
        hit = re.search(cfg["second_prompt_pattern"], b, re.M)
    except re.error:
        hit = None
    if hit and not any(k in b for k in cfg["allow_line_terms"]):
        issues.append(f"D11 FAIL [镜头 {entry['sid']} L{entry['line']}]: 同一镜出现第二版本 prompt"
                      f"（命中「{hit.group(0).strip()}」）—— 交付=单一 SOP 合并块，两套写法=用户困惑源")


def anim_check(entry, cfg):
    """D10 动画性检查：返回该条目的 FAIL 说明列表（空 = 通过）。"""
    shot = entry["sid"]
    tl = _field(entry["body"], "时间轴")
    neg = _field_line(entry["body"], "负面")
    if not tl:
        return [f"D10 FAIL [镜头 {shot}]: 缺【时间轴】字段，无法做动画性检查"]
    out = []

    # a) 动作曲线词 >= N（负向短语内的不算）
    ch = []
    for w in cfg["animation_curve_terms"]:
        idx = tl.find(w)
        while idx >= 0:
            seg = tl[max(0, idx - 6):idx + len(w) + 2]
            if not any(n in seg for n in cfg["animation_curve_exempt_terms"]):
                ch.append(w)
                break
            idx = tl.find(w, idx + 1)
    if len(ch) < cfg["animation_min_curve"]:
        out.append(f"D10 FAIL [镜头 {shot}] a: 动作曲线词 {len(ch)}/{cfg['animation_min_curve']}"
                   f"（命中：{'、'.join(ch) if ch else '无'}）—— 缺「预备→发力→跟随→回收」曲线")

    # b) 主体表演描述（>= N 个不同主体动作动词，须在【时间轴】内）
    ph = [w for w in cfg["animation_perf_terms"] if w in tl]
    if len(ph) < cfg["animation_min_perf"]:
        out.append(f"D10 FAIL [镜头 {shot}] b: 主体表演动词 {len(ph)}/{cfg['animation_min_perf']}"
                   f"（命中：{'、'.join(ph) if ph else '无'}）"
                   " —— 时间轴只写了运镜/氛围，没写主体在做什么")

    # c) 动画性负面禁项 >= N ＋ 叙事相关性禁项须齐备
    bh = [w for w in cfg["animation_ban_terms"] if w in neg]
    nb = [w for w in cfg["narrative_ban_terms"] if w in neg]
    if len(bh) < cfg["animation_min_ban"] or len(nb) < len(cfg["narrative_ban_terms"]):
        miss = [w for w in cfg["narrative_ban_terms"] if w not in neg]
        out.append(f"D10 FAIL [镜头 {shot}] c: 动画性禁项 {len(bh)}/{cfg['animation_min_ban']}＋"
                   f"叙事相关性禁项 {len(nb)}/{len(cfg['narrative_ban_terms'])}"
                   f"（动画项命中：{'、'.join(bh) if bh else '无'}；"
                   f"叙事项缺：{'、'.join(miss) if miss else '无'}）"
                   f" —— 负面须含 {'/'.join(cfg['animation_ban_terms'])} ≥{cfg['animation_min_ban']}，"
                   f"并必含「{', '.join(cfg['narrative_ban_terms'])}」")

    # d) 字卡条目的书写性表述（字卡镜 = 配置清单／自动判定，与 D9 同一事实源）
    #    OP 段例外：OP 段文字纪律由 D12 硬门控把关，1-04~1-07 被裁定A 删出字卡镜清单后
    #    条目内仍留有「无字卡／镌字之约」等字样，自动判定必然误报 → OP 段只认显式清单（1-12）。
    is_zika = _is_text_card_shot(shot, cfg)
    if not is_zika and not _is_op_shot(shot, cfg):
        try:
            is_zika = bool(re.search(cfg["text_card_auto_markers"], tl))
        except re.error:
            is_zika = False
    if is_zika:
        nw = [w for w in cfg["text_card_nonwrite_terms"] if w in tl]
        wri = [w for w in cfg["text_card_write_terms"] if w in tl]
        if nw:
            out.append(f"D10 FAIL [镜头 {shot}] d: 字卡条目时间轴出现非书写性表述「{nw[0]}」"
                       "（须写「逐字书写/笔迹生长/写出」）")
        elif not wri:
            out.append(f"D10 FAIL [镜头 {shot}] d: 含字卡文字但时间轴未写「逐字书写/笔迹生长/写出」"
                       "类书写性表述")

    # e) 动作动机（用户 20260915 追加裁定：动作不是装饰，是台词）
    key = cfg["motive_key"]
    if key not in tl:
        out.append(f"D10 FAIL [镜头 {shot}] e: 时间轴无「{key}＝…」标注"
                   " —— 每个动作须写「动作动机＝…」说明这个动作在说什么，无动机的动作=装饰")
    else:
        win = tl[tl.find(key):tl.find(key) + cfg["motive_window"]]
        sem = [w for w in cfg["motive_semantic_terms"] if w in win]
        if not sem:
            out.append(f"D10 FAIL [镜头 {shot}] e: 「{key}」后未见语义判据词"
                       f"（须出现 {'/'.join(cfg['motive_semantic_terms'][:9])} 类之一）"
                       " —— 动作不是装饰，是台词")
    return out


# ============================================================================
# 四、单文件扫描
# ============================================================================
def scan(path, cfg, anim_only=False, no_anim=False, baseline=False):
    """扫一个文件，返回 {issues, warns, notes, anim_issues, shots, anim_shots}。

    通道门（用户裁定 20260921 · 硬规则 #42 · **严格优先**）——**只有显式声明通道才缩小范围**：
      · 留空/未声明            ⇒ **全套严格**（D1–D13 全跑；不因"没写 channel"静默关闸）
      · channel=A / A+C        ⇒ 跳过**剧集专属** D10（#28）＋ D12（#33）——D13 见下
      · channel=C（MV 单通道） ⇒ **只跳 D12**；D10 保留（MV 也能是动画路径）
      · channel=B / A+B        ⇒ 全套严格
      · **D13 禁亮词（#34）不由通道名决定**：由 `light_terms` 是否为空决定（通道 A 默认档置空 ⇒
        不评估；项目显式给了词表 ⇒ 照跑）。避免"写个通道名就整体关闸"。
    **不跳过**通道 A/C 同样适用的通用项：D1/D2/D3/D4/D5/D6/D7/D8/D9/D11（含 D4/D8 后期表述门，
    承载型行豁免照常生效）。baseline=True ⇒ D10 只列清单不计 FAIL（--animation-baseline 语义）。
    """
    try:
        with open(path, encoding="utf-8-sig", errors="ignore") as fh:
            txt = fh.read()
    except Exception as e:  # noqa: BLE001
        return {"file": path, "issues": [f"无法读取: {e}"], "warns": [], "notes": [],
                "anim_issues": [], "shots": set(), "anim_shots": set()}
    lines = txt.splitlines()
    issues, warns, notes, anim_issues = [], [], [], []
    anim_shots = set()
    # 承载型判定：清单/台账类文件 + 负面词串/禁项枚举行（D4/D13 降 NOTE，prompt 执行件维持严格）
    tier_info = {"tier": _file_tier(path, cfg), "carrier": carrier_line_flags(lines, cfg)}
    # ---- 通道档（严格优先 · 唯一事实源 _channel_scope）：空/未声明、含 B 的组合一律全套严格 ----
    ch, skip_d10_d12, skip_d12_only = _channel_scope(cfg)
    skip_d10 = skip_d10_d12               # #28 动画性：仅 AI 原生动画路径 ⇒ 广告/MV 通道不适用
    skip_d12 = skip_d10_d12 or skip_d12_only   # #33 OP 文字白名单：仅剧集 OP/ED
    no_light = not [t for t in (cfg.get("light_terms") or []) if str(t).strip()]
    skip_d13 = no_light                    # #34 禁亮词：词表空（通道 A 默认档）⇒ 不评估；与通道名无关
    skipped = []
    if skip_d10:
        skipped.append(f"D10 {CHANNEL_SERIES_ONLY_CHECKS['D10']}")
    if skip_d12:
        skipped.append(f"D12 {CHANNEL_SERIES_ONLY_CHECKS['D12']}")
    if skip_d13:
        skipped.append("D13 禁亮词：本档 `light_terms` 为空（#34 仅 AI 原生「无光源」风格；"
                       "通道 A 默认档置空）⇒ 不评估")
    if skipped:
        notes.append(f"通道={ch}（**显式声明**，非「未声明」）：已跳过 —— " + "；".join(skipped))
    elif ch:
        notes.append(f"通道={ch}：全套严格（未跳过任何检查）")

    if not anim_only:
        check_d4_lines(lines, cfg, issues, warns, notes, tier_info)   # D4 禁词（承载型降 NOTE）
        check_d4_exclusive(lines, cfg, issues, warns)      # D4-EXT 专属空间标记
        check_d7(lines, cfg, issues)                       # D7 校勘红线
        if not skip_d13:
            check_d13(lines, cfg, issues, warns, notes, tier_info)    # D13 禁亮词（承载型降 NOTE）
        if not skip_d12:
            check_d12(txt, cfg, issues)                    # D12 OP 段禁浮空字卡

    entries = shot_entries(txt, cfg)                       # 条目锚由配置决定
    for e in entries:
        if not anim_only:
            check_d1(e, cfg, issues)                       # D1 SOP 字段
            check_d2(e, cfg, issues)                       # D2 @标记贯穿
            check_d3(e, cfg, warns)                        # D3 负面同块
            check_d9(e, cfg, issues, warns, notes)         # D9 字卡镜负面分档
            if cfg.get("check_second_prompt"):
                check_d11(e, cfg, issues)                  # D11 第二版本 prompt（可选）
        if not no_anim and not skip_d10:
            ai = anim_check(e, cfg)                        # D10 动画性（仅非动画通道跳过）
            if ai:
                anim_issues.extend(ai)
                anim_shots.add(e["sid"])

    if not anim_only:
        code_blocks = re.findall(r"```(.*?)```", txt, re.S)
        check_d5(lines, code_blocks, cfg, issues, warns)   # D5 故事板纪律（仅代码块内）
        check_d6(lines, cfg, warns)                        # D6 字卡口径
        check_d8(lines, cfg, issues)                       # D8 后期表述归一（通用项·照跑）

    return {"file": path, "issues": issues, "warns": warns, "notes": notes,
            "anim_issues": anim_issues,
            "shots": {e["sid"] for e in entries}, "anim_shots": anim_shots}


# ============================================================================
# 五、CLI
# ============================================================================
def _code(msg):
    m = re.match(r"(D\d+)", msg)
    return m.group(1) if m else "??"


def _split_shots(s):
    return [x.strip() for x in re.split(r"[,，;；\s]+", s or "") if x.strip()]


def _resolve_run_dir_for_file(path):
    """首参是文件时向上定位 run 目录：以「父目录名为 runs/」的那一层为准
    （runs/<slug>/m4-prompts/x.md → runs/<slug>）；找不到则退回该文件所在目录。"""
    start = os.path.dirname(os.path.abspath(path))
    cur = start
    while True:
        parent = os.path.dirname(cur)
        if not parent or parent == cur:
            return start
        if os.path.basename(parent).lower() == "runs":
            return cur
        cur = parent


def _gate_error(msg, cfg_used=None, run_dir=None, as_json=False, arg_note=None):
    """门控无法判定（0 文件 / 0 镜头 / 路径非法）时的统一出口：exit 2，绝不静默通过。"""
    if as_json:
        print(json.dumps({
            "run_dir": os.path.abspath(run_dir) if run_dir else None,
            "config_file": cfg_used, "arg_resolution": arg_note,
            "gate_error": msg, "summary": {"fail": None, "warn": None}, "exit_code": 2,
        }, ensure_ascii=False, indent=2))
    else:
        print(f"FAIL: {msg}")
    return 2


def main():
    ap = argparse.ArgumentParser(add_help=True, description="科生 prompt 交付门控（通用版 D1–D13）")
    ap.add_argument("run_dir", help="runs/<项目slug> 目录")
    ap.add_argument("files", nargs="*", help="可选：只检查指定文件")
    ap.add_argument("--animation-baseline", action="store_true",
                    help="D10 基线模式：列清单但不计入 FAIL、不改退出码")
    ap.add_argument("--animation-only", action="store_true", help="只跑 D10（动画性专项体检）")
    ap.add_argument("--no-animation", action="store_true", help="跳过 D10（旧口径）")
    ap.add_argument("--json", action="store_true", help="JSON 输出（机器可读）")
    ap.add_argument("--config", default=None,
                    help="配置文件路径（默认 <run目录>/prompt-delivery-config.json）")
    ap.add_argument("--dump-config", action="store_true", help="打印合并后的生效配置")
    ap.add_argument("--zika-shots", default=None, help="显式字卡镜号，如 \"1-04,1-05\"")
    ap.add_argument("--correction-red", default=None, help="显式校勘红线句，逗号分隔")
    args, unknown = ap.parse_known_args()
    extra_files = [u for u in unknown if not u.startswith("-")]
    bad_flags = [u for u in unknown if u.startswith("-")]
    if bad_flags:
        print(f"未知选项：{' '.join(bad_flags)}（用 --help 查看）")
        return 2
    args.files.extend(extra_files)

    # ---- 首参解析（堵"空跑假通过"）：目录=run目录；文件=自动解析 run 目录＋该文件为显式文件 ----
    run_arg = args.run_dir
    arg_note = None
    if os.path.isdir(run_arg):
        run_dir = run_arg
    elif os.path.isfile(run_arg):
        run_dir = _resolve_run_dir_for_file(run_arg)
        args.files.insert(0, os.path.abspath(run_arg))
        names = ", ".join(os.path.basename(x) for x in args.files[:5])
        arg_note = (f"参数解析：首参是文件 → run目录={run_dir}；显式文件 {len(args.files)} 个"
                    f"（{names}{'…' if len(args.files) > 5 else ''}）")
        if not os.path.isdir(run_dir):
            return _gate_error(f"无法从文件定位 run 目录 —— {run_arg}",
                               as_json=args.json, arg_note=arg_note)
    else:
        return _gate_error(
            f"首参既不是 run 目录也不是文件 —— {run_arg}\n"
            "正确用法: python -X utf8 check_prompt_delivery.py <run目录> [文件...] "
            "[--animation-baseline] [--json]", as_json=args.json)
    if args.animation_only and args.no_animation:
        print("--animation-only 与 --no-animation 互斥")
        return 2

    try:
        cfg, cfg_used = load_config(run_dir, args.config)
    except ConfigError as e:
        # T3：配置不可解析 ⇒ 不可判定，exit 2（绝不静默回退默认词表继续跑）
        return _gate_error(str(e), None, run_dir, args.json, arg_note)
    # ---- 通道档门（用户裁定 20260921 · 硬规则 #42）：值非法即无法判定（exit 2），绝不静默按 B 跑 ----
    ch_raw = cfg.get("channel")
    if ch_raw not in (None, "") and not _norm_channel(ch_raw):
        return _gate_error(
            f"配置 channel 值非法 —— {ch_raw!r}"
            "（只允许 A / B / C / A+B / A+C / B+C / A+B+C 或留空；留空＝全套严格）；"
            "模板见 templates/prompt-delivery-config-channelA.json",
            cfg_used, run_dir, args.json, arg_note)
    # 命令行补充注入（等价于配置项）
    if args.zika_shots:
        cfg["text_card_shots"] = _split_shots(args.zika_shots)
    if args.correction_red:
        cfg["correction_red_terms"] = [x.strip() for x in re.split(r"[,，]+", args.correction_red) if x.strip()]
    elif not cfg["correction_red_terms"] and cfg.get("correction_red_file"):
        p = os.path.join(run_dir, cfg["correction_red_file"])
        if os.path.isfile(p):
            try:
                with open(p, encoding="utf-8-sig") as fh:
                    cfg["correction_red_terms"] = [
                        ln.strip() for ln in fh if ln.strip() and not ln.lstrip().startswith("#")]
            except Exception:  # noqa: BLE001
                pass
    if args.dump_config:
        print(json.dumps(cfg, ensure_ascii=False, indent=2))
        return 0

    files, missing = list_files(run_dir, cfg["file_globs"], cfg["exclude_dirs"], args.files)
    if missing:
        return _gate_error("显式指定的文件不存在 —— " + "；".join(missing),
                           cfg_used, run_dir, args.json, arg_note)
    if not files:
        return _gate_error("未匹配到任何待检文件（检查 file_globs/路径是否正确）："
                           f"run目录={run_dir}，file_globs={cfg['file_globs']}",
                           cfg_used, run_dir, args.json, arg_note)

    results = [scan(f, cfg, anim_only=args.animation_only, no_anim=args.no_animation,
                    baseline=args.animation_baseline)
               for f in files]

    total_fail, total_warn, total_note, total_anim = 0, 0, 0, 0
    per_d, per_d_warn = {}, {}
    uniq_shots, uniq_anim_fail_shots, anim_entries = set(), set(), 0
    for r in results:
        total_fail += len(r["issues"])
        total_warn += len(r["warns"])
        total_note += len(r["notes"])
        total_anim += len(r["anim_issues"])
        anim_entries += len(r["anim_shots"])
        uniq_shots |= r["shots"]
        uniq_anim_fail_shots |= r["anim_shots"]
        for x in r["issues"] + r["anim_issues"]:
            per_d[_code(x)] = per_d.get(_code(x), 0) + 1
        for x in r["warns"]:
            per_d_warn[_code(x)] = per_d_warn.get(_code(x), 0) + 1

    # 0 镜头号 = 无法判定（锚名/配置可能不对）：一律 exit 2，绝不输出 PASS
    if not uniq_shots:
        return _gate_error(
            "未匹配到任何镜头条目（0 个镜头号）——核对 shot_heading_pattern"
            f"（当前 {cfg['shot_heading_pattern']}）或 run 内 prompt-delivery-config.json；"
            f"已扫 {len(files)} 个文件", cfg_used, run_dir, args.json, arg_note)

    blocking_anim = 0 if (args.animation_baseline or args.no_animation) else total_anim
    final_fail = total_fail + blocking_anim
    # 通道档（用户裁定 20260921 · 硬规则 #42 · **严格优先**）：仅显式声明才缩小范围；空=全套严格；
    #   含 B 的组合（B／A+B／B+C／A+B+C）⇒ 全套严格；口径唯一事实源＝_channel_scope（与 scan() 同源）
    ch, ch_skip_series, ch_skip_d12_only = _channel_scope(cfg)
    ch_narrow = ch_skip_series or ch_skip_d12_only
    ch_label = f"通道档 {ch}" if ch else "通道未声明（按全套严格）"
    _CH_DESC = {
        "A": "通道A档（显式声明：跳过剧集专属 D10/D12）",
        "A+C": "通道A+C档（显式声明：跳过剧集专属 D10/D12）",
        "C": "通道C档（显式声明：只跳 D12；D10 动画性保留）",
        "B": "通道B档（显式声明：D1–D13 全套严格）",
        "A+B": "通道A+B档（显式声明：含 B ⇒ 全套严格）",
        "B+C": "通道B+C档（显式声明：含 B ⇒ 全套严格·C 信息保留）",
        "A+B+C": "通道A+B+C档（显式声明：含 B ⇒ 全套严格·A/C 信息保留）",
    }
    ch_desc = _CH_DESC.get(ch, "")
    mode = ("基线模式（D10 不阻断）" if args.animation_baseline
            else ("已跳过 D10" if (args.no_animation or ch_skip_series)
                  else ("仅 D10 动画性体检" if args.animation_only else "全套检查（含 D10）")))
    if ch_desc:
        mode = f"{ch_desc}｜{mode}"
    exit_code = 0 if (final_fail == 0 or args.animation_baseline) else 1

    if args.json:
        skipped_checks = ([] if not ch_narrow else
                          (["D10", "D12"] if ch_skip_series else ["D12"]))
        if not [t for t in (cfg.get("light_terms") or []) if str(t).strip()]:
            skipped_checks.append("D13")
        print(json.dumps({
            "run_dir": os.path.abspath(run_dir),
            "config_file": cfg_used,
            "mode": mode,
            "channel": ch or None,
            "channel_declared": bool(ch),
            "channel_desc": ch_desc,
            "channel_skipped_checks": skipped_checks,
            "arg_resolution": arg_note,
            "animation_baseline": bool(args.animation_baseline),
            "files": [{
                "file": os.path.relpath(r["file"], run_dir).replace("\\", "/"),
                "issues": r["issues"],
                "warns": r["warns"],
                "notes": r["notes"],
                "animation_issues": r["anim_issues"],
            } for r in results],
            "summary": {
                "fail": final_fail, "fail_d1_d9": total_fail, "warn": total_warn,
                "note": total_note, "animation_fail": total_anim,
                "animation_fail_entries": anim_entries,
                "animation_fail_shots": len(uniq_anim_fail_shots),
                "shots_scanned": len(uniq_shots), "files": len(files),
                "by_check": per_d, "by_check_warn": per_d_warn,
            },
            "exit_code": exit_code,
        }, ensure_ascii=False, indent=2))
        return exit_code

    # ---- 人类可读输出：中文、按文件分组 ----
    print(f"===== 科生 prompt 交付门控（通用版 D1–D13）: "
          f"{os.path.basename(os.path.normpath(run_dir))} =====")
    print(f"配置：{cfg_used or '（未提供 prompt-delivery-config.json，使用通用默认词表）'}")
    print(f"通道档：{ch_label}" + (f"｜{ch_desc}" if ch_desc else ""))
    if ch_desc:
        light_empty = not [t for t in (cfg.get("light_terms") or []) if str(t).strip()]
        if ch_skip_series:
            print("  > 通道A档（**显式声明**）：已跳过剧集专属检查 D10（动画性·#28 仅 AI 原生动画路径）/ "
                  "D12（OP 段禁浮空字卡·#33 仅剧集 OP/ED）—— 依据 docs/DUAL-CHANNEL-AUDIT.md")
        elif ch_skip_d12_only:
            print("  > 通道C档（**显式声明**）：只跳过 D12（OP 段禁浮空字卡·#33 仅剧集 OP/ED）；"
                  "**D10 动画性保留**（MV 也可能是动画路径）")
        if light_empty:
            print("  > D13 禁亮词：本档 `light_terms` 为空 ⇒ 不评估（#34 仅 AI 原生「无光源」风格；"
                  "通道 A 默认档置空）")
        if ch_skip_series or ch_skip_d12_only:
            print("  > 通道 A/C 仍严格：D1 SOP 字段 / D2 @标记贯穿 / D3 负面同块 / D4 后期禁词 /"
                  " D5 故事板 / D6 字卡口径 / D7 校勘红线 / D8 后期表述归一 / D9 字卡镜负面分档"
                  "（通用项与广告法合规不放松）")
    if arg_note:
        print(arg_note)
    for r in results:
        if not (r["issues"] or r["warns"] or r["notes"] or r["anim_issues"]):
            continue
        print(f"\n=== {os.path.basename(r['file'])} ===")
        for x in r["issues"]:
            print("  " + x)
        for x in r["warns"]:
            print("  " + x)
        for x in r["notes"]:
            print("  " + x)
        if r["anim_issues"]:
            print(f"  ---- D10 动画性 FAIL {len(r['anim_issues'])} 条 / "
                  f"命中条目 {len(r['anim_shots'])} 个 ----")
            for x in r["anim_issues"]:
                print("  " + x)
            if args.animation_baseline:
                print("  > [基线模式] 以上 D10 FAIL 不计入总 FAIL、不改退出码"
                      "（待办清单，非立即清零项）")

    parts = " / ".join(f"{k} {v}" for k, v in sorted(per_d.items(), key=lambda kv: (len(kv[0]), kv[0])))
    print(f"\n== 交付门控结果: FAIL {final_fail} / WARN {total_warn} / NOTE {total_note}"
          f" ｜ D10 动画性 FAIL {total_anim} 条 / 命中条目 {anim_entries} 个"
          f" / 去重镜头号 {len(uniq_anim_fail_shots)} 个（全库共查 {len(uniq_shots)} 个镜头号）"
          f"（扫描 {len(files)} 个文件 · {mode}）")
    if parts:
        print(f"   分项（含 D10）：{parts}")
    if per_d_warn:
        print("   WARN 分项：" + " / ".join(f"{k} {v}" for k, v in sorted(per_d_warn.items())))
    if args.animation_baseline:
        print("   * 基线模式：总 FAIL 不含 D10；D10 清单见上（20260915 用户裁定：动画性缺口是"
              "待办清单，不是立刻清零项）")
    if final_fail == 0:
        print("   PASS ✅ 交付前门控通过")
    else:
        print(f"   FAIL ❌ {final_fail} 项未过，FAIL>0 不得交付"
              "（修复方向见 scripts/README-check_prompt_delivery.md）")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
