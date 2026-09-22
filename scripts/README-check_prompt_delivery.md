# check_prompt_delivery.py —— prompt 交付门控（通用版 D1–D13）

**用途**：交付前必跑的机器门控（FAIL>0 不得交付）。把《红楼梦》EP01 四轮纠错固化的 prompt 纪律（SOP字段完整/@标记贯穿/负面同块/废止表述/故事板纪律/字卡口径/校勘红线/字卡镜负面分档/动画性 D10/**D12 OP 禁浮空字卡**/**D13 禁亮词**）变成可执行检查。

**D12／D13 摘要（红楼梦EP01·甲方裁定A/B 20260915）**：
- **D12 OP 段禁浮空字卡**：OP 段条目（镜号匹配 `op_shot_pattern`，默认 `^1-(?:0[1-9]|1[0-6])$`）或段块（标题匹配 `op_scope_pattern`，默认 `A-0[1-5](?!\d)|序幕|OP《|OP段|OP 段`）的**【时间轴】**不得含 `op_text_card_terms`（字卡／逐字书写／字位书写／字卡位／字卡区／叠角字卡／逐字上屏／上屏／字幕）；**同句**含 `op_text_whitelist_terms`（片名／注音／印章／落印／玉面／玉背／镌字／印文／石面刻字）→ 豁免；否定式（前 8 字内有 不/无/禁/非/勿/绝）→ 豁免；「变更/废止/禁止/作废」留痕句豁免。
- **D13 禁亮词（无光之戏）**：全库 prompt 正文不得出现 `light_terms`（一亮／发亮／闪光／高光／辉光／反光／发光；含繁体字形）。**豁免**：①负面字段与禁项串行（`light_negative_block_pattern`／`light_negative_enum_sentinels`）②否定式（命中处前 `light_negation_window` 字含 不/无/禁/非/勿/绝，如「只色不发光」「无瞳孔高光」）③方法性/QC 行（参数／失败改法／判废标准／判废要点／废片判据／看什么／台账／溯源，见 `light_qc_line_pattern`）——这些行里的「出辉光即废」是**正确**写法。可选 `light_warn_terms`（如 亮起/点亮）只出 WARN、不阻断。
- 替换词表（写作用）：一亮/发亮→**沉深一分**／**墨色渐浓**；闪光→**洇开一瞬**；高光/辉光→**焦墨凝住**；反光→**映墨**；发光（正面）→渐浓／褪淡／洇开。细则见 `playbooks/animation-motion-design.md` §4.3.2、`playbooks/platform-prompts.md` §0.6.1/§0.6.2、`orchestration/ORCHESTRATION.md` 硬规则 **#33/#34**、`knowledge/FAILURE-LIBRARY.md` **F-45/F-46**。
- **D9／D10-d 的 OP 例外**：`text_card_auto_note`（默认 true）与 D10-d 的"自动判定字卡镜"对 **OP 段自动跳过**（OP 文字纪律由 D12 硬门控把关；被裁定删出字卡镜清单的 OP 镜条目内仍留有「无字卡／镌字之约」等字样，自动判定必然误报），OP 段只认显式 `text_card_shots`（如片名镜）。

**用法**（`<run>` = `runs/<项目slug>`）：
`python -X utf8 scripts/check_prompt_delivery.py <run> [文件...] [--animation-baseline|--animation-only|--no-animation] [--json] [--dump-config]`
`--animation-baseline`＝动画类项目日常口径（D10 只出待办清单、不阻断、exit 0）；`--json`＝机器可读（CI/check_all）；无文件参数时按 `file_globs` 扫描（默认 `prompts-*`/`segments-*`/`m5-*.md`，跳过 `_旧版归档`）。

**⚠️ 用法红线**：正确用法是 `check_prompt_delivery.py <run目录> [文件…]`。首参若误传成单个文件，脚本自动解析其所属 `runs/<项目slug>`、把该文件作为显式文件检查、并在输出首行打印解析结果；首参既非目录也非文件、显式文件不存在、扫到 **0 个文件**、匹配到 **0 个镜头条目** → 一律 `FAIL: …` 并 **exit 2**（**空跑绝不算通过**："FAIL 0 / WARN 0" 只可能来自真扫过的文件）。

**为项目写 `<run>/prompt-delivery-config.json`**（可选；不写＝通用词表）。项目专属词**只进配置**——专属空间标记、字卡镜号、校勘红线、额外禁词、故事板钉死词、动画阈值均可覆盖：

```json
{
  "exclusive_space_terms": [
    {"term": "墨浪", "allowed_shots": ["1-01", "1-02"], "allowed_scope_pattern": "序幕|OP段",
     "note": "OP段专属空间标记；写在负面字段里=列为禁项，豁免"}
  ],
  "text_card_shots": ["1-12", "2-01", "7-01"],
  "text_card_shots_pattern": "^(?:13-01|15-0[12])$",
  "text_card_auto_note": true,
  "op_shot_pattern": "^1-(?:0[1-9]|1[0-6])$",
  "op_scope_pattern": "A-0[1-5](?!\\d)|序幕|OP《|OP段|OP 段",
  "op_text_whitelist_terms": ["片名", "注音", "印章", "落印", "玉面", "玉背", "镌字", "印文", "石面刻字"],
  "light_terms": ["一亮", "发亮", "發亮", "闪光", "閃光", "高光", "辉光", "輝光", "反光", "发光", "發光"],
  "light_warn_terms": [],
  "correction_red_terms": ["飞觥限挚", "大旨谈论"],
  "forbidden_terms": ["后期配音", "后期叠", "后期合成", "急停悬停", "定格卡"],
  "storyboard_negative_terms": ["水墨", "晕染", "泼墨", "飞白", "灰阶渲染", "彩色", "黑色块"],
  "storyboard_negative_min": 3
}
```

**与 SOP 三层门控的关系**：① **文字条款**（`templates/prompt-sop.md` 等规范文本，人写人读）→ ② **机器门控**（本脚本：条条可判、FAIL 即阻断；已纳入 `check_all.py`）→ ③ **人工闸**（红队前置闸 / 出口评审 / 用户拍板，判"好不好"）。顺序不可颠倒：机器门控过不了就不必浪费人工闸；机器门控只保证"不犯已知错"，不替代人工判断。

**口径来源**：红楼梦EP01·用户裁定 20260915（`playbooks/platform-prompts.md` §〇、`playbooks/animation-motion-design.md`）。D10 基线是待办清单，不是立刻清零项——日常用 `--animation-baseline`，成片前专项清零。**D12／D13 为硬门控**（甲方裁定A/B），默认计入 FAIL、不可基线豁免。
