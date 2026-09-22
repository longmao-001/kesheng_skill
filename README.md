# 科生（Kesheng）—— 科学的方法生产视频

> 多 agent 编排驱动的**多形态 AI 视频制作团队（三形态 × 三驱动源）**。不直接生成视频；交付专业团队水平的东西：
> 制作方案、口播脚本／文学剧本、分镜表、逐镜 AI 视频 prompt（可灵/即梦/Vidu/海螺/Runway/万相/Seedance/LibTV/cgprism）、
> 手把手制作流程、Word 适配的科学报告 + 讲解 PPT。
>
> **三种产物形态 ↔ 三种驱动源 ↔ 三条能力线**（硬规则 #43）：
> **口播稿＝文案／信息驱动 → 通道 A**（广告／科普／科研视频）·
> **剧本＝戏剧动作驱动 → 通道 B**（剧集／叙事：KSP-E1~E5 全季前置 ＋ 逐集循环）·
> **卡点表＝音乐驱动 → 通道 C**（MV／OP·ED／插入歌／品牌音乐片：**横向能力，与 A、B 均相交**，不新增关卡）。
>
> **用户定位**：用户是冲着 **AI 视频生成**来的——主玩法是在各平台画布/节点上自己动手。所以交付物是
> **「多平台上手素材包」**（每镜：平台对照 prompt + 参考图包 + 口播 + 抽卡建议 + 画布步骤），
> 所有后期环节都给 **AI 原生路径**（自动字幕/一键调色/曲库配乐/模板数据卡）；专业后期=可选增强，永不是前提。

---

## 一、核心机制（六件事）

1. **立项第一步 ＝ 判型两遍**（硬规则 #42④／#43①／#44②）：**① 纵向判通道**——A（广告/科普/科研）还是 B（剧集）；**"是不是剧集"是项目属性、不是档位**（与 S/M/L 无关）。**② 横向判音乐驱动**——本片／本段**是否 C**；是则判 **C∩A／C∩B／纯 C**，并**标出哪几段属 C 段（时间码）**。**两遍都写进 `brief.md`**；**模棱两可默认走 A**；**A→B ／ A/B 混用 ／ 引入 C 段 → 走 KSP-C 记录**（禁静默切换通道）。
2. **真多 agent 协作**：制片人（主 agent）编排；导演/编剧/分镜师/美术指导/摄影指导/声音设计师/剪辑师/科学顾问/prompt 工程师/观众代言人/红队/检察官 以**独立上下文 subagent** 并行作业、黑板（`runs/<项目slug>/`）交接、制品门控。
3. **三形态 × 三驱动源：两条纵向通道 ＋ 一条横向能力**：**通道 A**（KSP-01~07 原链路·**保留资产永不降级**）／**通道 B 剧集**（**KSP-E1~E5 前置** ＋ KSP-02~07 每集循环：全季分集大纲 → 风格圣经 → 逐集循环 → 跨集一致性闸 → 发布追更）／**通道 C 音乐驱动**（**横向**，与 A、B 相交，**不新增关卡**：C∩A 挂 A 的 KSP-01~07＋广告法合规/品牌 VI；C∩B 挂 KSP-E2 圣经 ＋ KSP-E1 时长预算）。判型卡与关卡映射见 `docs/USER_SOP.md` KSP-01＋§2.6；**规则适用通道审计见 `docs/DUAL-CHANNEL-AUDIT.md`**。
4. **KSP 状态机流程**（KSP-01~07 ＋ KSP-E ＋ KSP-C 变更控制）：立项定档+判型 → 简报+预注册 → **科学理解（报告=中间交付件，等用户「继续」）** → 主题共识+内容重点 → 概念先行 → 口播稿 → 九宫格风格 → 执行（分镜/声音/prompt/剪辑）→ 出口 → 萃取归档。
5. **拍板卡 + 证据先行**：每关必用 `ask_user_question` 选项卡（≥2 选项、推荐置顶、留"自定义"兜底）；基于文件拍板**必须先展示依据**再给选项，禁盲选。全部 **19 个拍板点**见 `templates/user-gate.md`（**剧集项目另加全季层三次拍板**：全季大纲／风格圣经／每集验收）。
6. **机器门控（考勤式）**：不信任"代理人觉得做了"，以**产物 + 校验脚本**为准。`scripts/check_all.py` 一键跑 **16 项**门控（**满配**）＝ **通用常跑 13 项**；**素材类项目 +1**（`check_asset_labels`，判定＝有 `refs/`／`assets/`／`素材/`／`素材库/` 目录，或有 `assets_index.json`）；**剧集项目 +2**（`check_series_consistency`／`check_bible_pin`，判定＝有 `series-config.json` 或 `EPnn/` 集目录）。不满足判定条件的项由 `check_all.py` 打印 **`[跳过]`**——**跳过 ≠ 通过，空跑不算数**。

## 二、四条铁则（贯穿全流程）

| # | 铁则 | 说明 |
|---|---|---|
| 1 | **用户是甲方** | 每关拍板才推进；未经拍板不得进入下一阶段 |
| 2 | **拍板必须选项卡** | 一律 `ask_user_question`；禁止用纯文本列 A/B/C |
| 3 | **证据先行** | 拍板前先展示文件内容（全文/要点/图片路径+描述/数据来源） |
| 4 | **知识只进图谱** | 调研知识 → 域片段 → 重建图谱（`scripts/build_union_kg.py`）；**不新建 markdown 概念卡** |

---

## 三、流程图与权威文档（先读这些）

| 文件 | 内容 |
|---|---|
| **`docs/SOP-FLOW.md`** | **完整 SOP 流程图**：图一 KSP 主流程（**两通道 A/B ＋ 一横向能力 C**，含 **KSP-01 同卡判型框**）＋ 图一·补 **通道 C 交集流程** ＋ 图二 素材处理 ＋ 图三 PPT/Deck；含**全部 19 拍板点**、**一键 16 项门控脚本对照表**（通用 13 ＋ 素材类 1 ＋ 剧集类 2）、**检察官五层**、**顺序铁则与硬规则速查**。**同名 PNG/PDF 为图示成品**（`SOP-FLOW-KSP主流程` · `SOP-FLOW-素材处理` · `SOP-FLOW-PPT流程`），用 `python -X utf8 scripts/render_sop_flow.py` 重新出图 |
| **`docs/USER_SOP.md`** | KSP-01~07 ＋ **剧集通道 KSP-E1~E5** ＋ KSP-C 逐关规范（**流程权威**；含 §2.5 剧集通道 ／ §2.6 通道判定卡与通道 A 保留资产清单） |
| **`docs/DUAL-CHANNEL-AUDIT.md`** | **双通道规则审计表**：逐条给出**适用通道 ＋ 冲突判定 ＋ 限定语**（11 条需加限定语／7 条无需）＋ Top 5 高危误伤点 ＋ 通道 A 保留资产留痕（**判型／切换／混用／加新规则前先查本表**·硬规则 #42①） |
| **`docs/ASSET-TYPES.md`** | **按文件类型的固定处理方案**（视频/图片/矢量/PPT/PDF/Word/CAD/SolidWorks/SketchUp/3D/字体/表格/音频：提取动作+归类+红线） |
| **`SKILL.md`** | 入口：人设、铁律、里程碑工作流、团队编制、执行模式、启动必读清单、资源索引 |
| **`orchestration/ORCHESTRATION.md`** | 编排手册：工具映射、派活 prompt 模板、里程碑派活清单、**§5 硬规则 1-44**（含 #27 字卡口径、#31 逐镜文学闸、#32 文字参考图（字帖）、#33 OP 文字白名单、#34 禁亮词、**#35–#40 剧集六条**：全季规划先行/风格圣经先行/跨集资产复用/跨集一致性门控/集尾钩子与追更/剧集目录与版本规范、**#41 素材入库即标签**、**#42 双通道并存**、**#43 形态—驱动源对应**、**#44 MV 为横向能力**） |
| **`protocols/quality-gate.md`** | 七维评分 + 禁区 + **检察官五层** |
| **`templates/user-gate.md`** | 19 个拍板点预置选项速查 |

### 能力线专属文档（按判型结果按需读）

| 能力线 | 手册 | 模板 | 门控脚本 |
|---|---|---|---|
| **通道 B · 剧集** | `playbooks/series-production.md`（剧集必读） | `templates/season-outline.md`（全季分集大纲）· `templates/show-bible.md`（风格圣经）· `templates/episode-brief.md`（单集简报）· `templates/series-config.json`（跨集一致性门控词表） | `scripts/check_series_consistency.py`（KSP-E4·D-S1–D-S8）· `scripts/check_bible_pin.py`（圣经引用版本 pin·#36③） |
| **通道 C · 音乐驱动（横向）** | `playbooks/mv-production.md`（通用手册·必读）· `playbooks/op-ed-mv.md`（**C∩B 应用实例**：OP/ED） | `templates/mv-beat-sheet.md`（**唯一**卡点表模板：卡点表＋镜头表＋素材复用清单）· `templates/op-ed-mv-sheet.md`（OP/ED 填法说明·**不重复字段**） | **不新增关卡**——C∩A 挂 A 的 KSP-01~07（＋广告法/品牌 VI）／C∩B 挂 KSP-E2 圣经 ＋ KSP-E1 时长预算 |
| **动画类（A 或 B）** | `playbooks/animation-motion-design.md`（动画性纪律·动画类必读） | — | `scripts/check_prompt_delivery.py` **D10 动画性**（`--animation-baseline` 日常／`--animation-only` 专项体检） |
| **通道 A · 广告/科普/科研** | `playbooks/production-workflow.md` · `playbooks/platform-prompts.md` | `templates/product-prompt-formula.md` · `templates/narration-formula.md`（口播句公式 F01-F14） | `scripts/ad_forbidden_words.py`（广告法）· `scripts/check_channel_assets.py`（**保留资产守护**·#42③） |
| **素材库（三通道共用）** | `playbooks/asset-library-flow.md`（入库即标签·#41） | `scripts/asset_schema.md`（**sidecar／索引字段字典与 trace_status 判据**） | `scripts/asset_index.py`（唯一索引读写）· `scripts/ingest_asset.py`（入库即标签执行器）· `scripts/check_asset_labels.py`（双向核对门控） |
| **判型与通道纪律（技能级）** | `docs/USER_SOP.md` §2.6 · `docs/DUAL-CHANNEL-AUDIT.md` | — | `scripts/check_channel_conformance.py`（判型×磁盘形态交叉校验·#42④）· `scripts/check_rule_channels.py`（新增规则须标适用通道·#42①）· `scripts/check_channel_assets.py`（通道 A 保留资产·#42③）· `scripts/check_readme_counts.py`（**文档计数不漂移**） |

> **启动必读（每次使用先读全，读全前禁止派活/建文件）**：`docs/USER_SOP.md` · `orchestration/ORCHESTRATION.md` · `protocols/quality-gate.md` · `playbooks/production-workflow.md` · `templates/user-gate.md` ＋ `knowledge/FAILURE-LIBRARY.md`（失败图书馆，防重复踩坑）；**判为剧集加读 `playbooks/series-production.md`；含音乐驱动段加读 `playbooks/mv-production.md`**（C∩B 再读 `playbooks/op-ed-mv.md`）。

---

## 四、目录结构

> 下面括号里的数字＝**实测件数**（由 `scripts/check_readme_counts.py` 机器守护——漂移即 FAIL，禁凭记忆改）。

```
SKILL.md              入口：人设/铁律/里程碑/团队编制/执行模式/启动必读/资源索引
README.md             本文件
docs/     (8)         USER_SOP(KSP流程权威·KSP-01~07＋KSP-E1~E5＋KSP-C) · SOP-FLOW(完整流程图) ·
                      ASSET-TYPES(按类型处理方案) · ROLE_WORKFLOWS(角色SOP·含通道B/C额外职责) ·
                      DUAL-CHANNEL-AUDIT(双通道规则审计表) · DESIGN(架构设计) ·
                      KG_DOMAIN_DESIGN · PAPER_INGESTION
                      ＋图示成品 6 件（PNG/PDF：KSP主流程／素材处理／PPT流程）
agents/   (13)        制片人 · 导演 · 编剧 · 分镜师 · 美术指导 · 摄影指导 · 声音设计师 · 剪辑师
                      科学顾问 · prompt工程师 · 观众代言人 · 红队 · 检察官
orchestration/        ORCHESTRATION.md(编排手册·硬规则1-44) · kesheng_workflow.js+.meta.json(全自动 fan-out)
protocols/            meeting.md(会议协作协议) · quality-gate.md(三态门控+检察官五层)
playbooks/ (11)       production-workflow(端到端) · asset-library-flow(素材库→参考图·入库即标签) ·
                      ppt-deck-flow(PPT交 ppt-master/huashu-design) · science-report-flow(M2→M3交接闸) ·
                      platform-prompts(各平台公式·含Seedance2.0/2.5核实版) · storyboard-grid(宫格技法) ·
                      consistency(跨镜一致性) · animation-motion-design(动画性纪律·动画类必读) ·
                      series-production(剧集制作·KSP-E1~E5 必读) ·
                      mv-production(通道 C 音乐驱动·横向能力通用手册·必读) ·
                      op-ed-mv(通道 C∩B 应用实例：OP/ED·剧集做 OP/ED 必读)
templates/ (28)       brief · proposal · storyboard · decision-log · breakdown · handoff ·
                      prompt-sheet(格式规范) · prompt-sop(写prompt十步) · prompt-file ·
                      product-prompt-formula · video-prompt-formula ·
                      prompt-formulas(可复制公式库) · narration-formula(口播句公式F01-F14) ·
                      science-report · science-ppt · visual-baseline · reference-selection ·
                      assets-inventory(智能入库) · user-gate · l3-fact-inspector-report ·
                      season-outline(全季分集大纲) · show-bible(风格圣经) · episode-brief(单集简报) ·
                      series-config.json(剧集跨集一致性门控词表·KSP-E4) ·
                      mv-beat-sheet(通道 C 唯一卡点表模板) · op-ed-mv-sheet(OP/ED 填法说明) ·
                      prompt-delivery-config-channelA.json(通道 A 词表·自动跳过剧集专属 D12/D13/D10) ·
                      prompt-delivery-config-channelB.json(通道 B/剧集词表)
knowledge/            工艺知识库(历史权威正文)：hooks/ · ad-copy · tvc-ad-templates · camera-language ·
                      image-gen-formulas · prompt-reverse · seedance-template-library · vi_styles/ ·
                      痛点链/文案层/动感三来源/首帧锚定/素材分级/图表层/全能参考三用法 · index.md ·
                      FAILURE-LIBRARY.md(失败图书馆·跨项目·开工先读·编号 F-01…F-61 连续)
kb/                   科学知识图谱(Obsidian vault)：按领域分文件夹 + 入库规则.md + 隐私红线.md
packs/    (27片段)    统一知识图谱：kesheng-kg/(并集大图 3634实体 · 13 domain 分区) + kg_query.py 查询
                      域片段：scientist/screenwriter/director/creative/narration/prompt/audience/
                      audio/redteam/lessons/workflow-seed/sop-seed/gate-seed + papers-*(10个论文片段)
                      + rednote-industry-kg(产业) + xhs-cases-kg
scripts/  (90)        门控/工具脚本（门控清单与「拦什么」见下节；含 asset_schema.md 素材字段字典）
runs/                 项目工坊（黑板）：每项目一个 runs/<项目slug>/（只放项目，临时目录交付前删）
```

---

## 五、机器门控（`scripts/check_all.py` 一键 16 项）

**项数口径（实测，非承诺）**：**满配 16 项** ＝ **通用常跑 13 项**（下表 #1–#13）＋ **素材类项目 +1**（`check_asset_labels`；判定＝有 `refs/`／`assets/`／`素材/`／`素材库/` 目录，或有 `assets_index.json`）＋ **剧集项目 +2**（`check_series_consistency`／`check_bible_pin`；判定＝有 `series-config.json`，或有 `EPnn/` 集目录）。**不满足判定条件的项由 `check_all.py` 打印 `[跳过]`——跳过 ≠ 通过**；`exit 2`（不可判定/空跑）同样**不计入通过**（只有 `check_channel_conformance` 的 exit 2 视为"不臆断判型"的跳过）。

| # | 脚本 | 拦什么 |
|---|---|---|
| 1 | `check_channel_conformance.py` | **判型 × 磁盘形态交叉校验**（硬规则 #42④）：判 B／A+B 却缺 `series-config.json` 或 `EPnn/` 集结构 ＝ **FAIL**（防"判了 B 却不产 E1 配置 ⇒ 跨集闸被静默跳过"）；判 A 却有剧集形态 ＝ WARN；无 `brief.md`／缺通道字段 ＝ exit 2 → 总检打印 `[跳过]` |
| 2 | `check_sop.py` | 跳 SOP / 缺产物 + 每镜 prompt 字段不全 |
| 3 | `check_prompt_sheet.py` | prompt **格式与一致性**：核心字段 / 口播并入画面 / 口播≠口播稿 / 风格 token 不一致 / 参考漏挂 / 负面空（兼容 `**字段**：` 与 `【字段】` 两代格式） |
| 4 | `check_prompt_sop.py` | **写 prompt 十步 SOP 的执行证据**：参考图裸引用 / 风格不同源 / 口播≠口播稿 / 时间轴无分段 / 缺 README = FAIL；缺"部位对应·放哪位置"/产品镜缺"保真实造型"/参数缺项 = WARN |
| 5 | `check_prompt_delivery.py` | **prompt 交付门控·通用版 D1–D10**：SOP 字段 / @标记贯穿 / 负面同块 / 禁后期表述 / 故事板纪律 / 字卡口径 / 校勘红线 / 字卡镜负面分档 / **D10 动画性**（动作曲线·主体表演·负面·字卡书写性·动作动机）。**读 run 内 `prompt-delivery-config.json` 的 `channel`：`channel=A` 自动跳过剧集专属 D12/D13/D10**（模板 `templates/prompt-delivery-config-channelA.json`／`channelB.json`） |
| 6 | `check_asset_pack.py` | 素材自包含（@引用可解析、无"待补充/拍照"后补提示词） |
| 7 | `check_delivery.py` | **交付件版本收敛**：多源并存 / 交付包死链 / 口播稿多版本漂移 |
| 8 | `ad_forbidden_words.py` | 广告禁用词（绝对化·极限词 / 疗效承诺 / 平台禁语） |
| 9 | `check_runs_clean.py` | `runs/` 混入非项目散落物 |
| 10 | `check_docs_integrity.py` | **技能级**：SOP 断链 / 孤岛（写了没人读）/ 启动必读与门控脚本不一致 |
| 11 | `check_rule_channels.py` | **技能级**·**规则通道标注**（硬规则 #42①）：扫 §5 硬规则区，**新增规则（#≥43）缺适用通道标注 ＝ FAIL**；历史条目按审计表覆盖/默认通用仅 WARN |
| 12 | `check_channel_assets.py` | **技能级**·**通道 A 保留资产守护**（硬规则 #42③）：保留资产逐件断言存在 ＋ `.py` `py_compile`；缺件/空件/编译不过 ＝ FAIL（防剧集化改造误伤广告线） |
| 13 | `check_readme_counts.py` | **技能级**·**文档计数不漂移**：实测 playbooks/templates/scripts/agents/docs 件数、§5 硬规则条数、`check_all` 满配项数、拍板点数、FAILURE-LIBRARY 编号上限，与 `README.md`／`knowledge/index.md`／`docs/SOP-FLOW.md` 的**声明数字**逐项比对——**漂移 ＝ FAIL（列出"写 X / 实际 Y"）**；**文件缺失或声明缺失 ＝ exit 2**（不可判定，不当通过） |
| +1 | `check_asset_labels.py` | **素材类项目专属**·**素材标签门控**（硬规则 #41）：盘上↔索引**双向核对**——`orphan`／`ghost`／`label_gap` 任一命中即 FAIL；`trace_status: missing` 计入门控 FAIL；0 通过／1 有 FAIL／2 不可判定；**非素材类项目自动 `[跳过]`** |
| +2 | `check_series_consistency.py` | **剧集项目专属**·**跨集一致性**（KSP-E4 · D-S1–D-S8）：OP/ED 时长固定资产逐集相等 / 锚复用与版本漂移 / 同文本同帖 / 母题唯一与复现声明 / 钩子账本兑现责任人 / 专名逐字一致 / 新增入册 / 全季红线继承；**0 集 / 0 prompt 文件 / 缺配置 ＝ exit 2，空跑不算通过**；**非剧集项目自动 `[跳过]`** |
| +3 | `check_bible_pin.py` | **剧集项目专属**·**圣经引用版本 pin**（硬规则 #36③）：圣经 §⓪ 版本行非空（版本号＋生效日期/生效集号）＋ 各集 `EPnn-brief.md`「引用圣经版本」＝圣经当前版本；缺圣经/版本行空/引用过期/简报缺字段 ＝ FAIL；**非剧集项目自动 `[跳过]`** |

**其他脚本**：`check_reference_selection.py`（选片要素）· `check_residual.py`（旧表述残留回归）· `asset_index.py`（**全库唯一索引读写**：生成 `assets_index.json`〔机器〕＋ `assets_index.md`〔人读〕；**禁手改、禁并行台账**）· `ingest_asset.py`（**入库即标签执行器·硬规则 #41**：命名校验〔不合规不入库〕→ 写 sidecar → 追加唯一索引一条）· `scripts/asset_schema.md`（**素材 sidecar／索引字段字典与 `trace_status` 判据**——逐字/重构/缺口三档，禁伪造"逐字"）· `annotate_assets.py`／`classify_assets.py`（素材智能入库脚手架／分类命名）· `extract_docs.py`（PDF/PPTX/DOCX → 抠图+抽文+台账骨架）· `md_to_docx.py`（Markdown → **适配 Word** 的 docx）· `build_science_report.py`（科学报告 → 结构化 md + Word适配 docx + PPT 大纲）· `render_sop_flow.py`（SOP 流程图出图：PNG 位图 + PDF 矢量）· `build_union_kg.py`（图谱并集重建）· `packs/kg_query.py`（图谱查询）。

> **门控哲学**：SOP 条目必须同时有 **①文字条文 ②机器门控 ③人工闸（红队/检察官）三层**，缺一层就等于没写（ORCHESTRATION §5-23）。
> **计数也是条文**——件数/条数/项数写进文档即受 `check_readme_counts.py` 守护。
> 门控报错先分"真缺"还是"格式别名误报"——**误报=修脚本，不迁就脚本改制品**（F-30）。

---

## 六、快速上手（制片人节奏）

```
开工 → 读全核心流程5份 + FAILURE-LIBRARY → todo_write 清单
→ KSP-01 定档(S/M/L) + ★判型两遍                        ▲拍板#1 定档 #18 品牌名/用字
      ★ ①纵向：通道 A(文案驱动)｜B(剧集·戏剧驱动)｜A+B
      ★ ②横向：是否音乐驱动＝是否 C（C∩A／C∩B／纯C／无C段·默认）
      ★ 两遍都写进 brief.md；A→B／A/B 混用／引入 C 段 → 出 KSP-C 变更记录
→ KSP-02 简报+预注册标准+素材清单              ▲拍板#2-7 受众/平台/时长/风格/画风/素材 #19 强调色
→ KSP-03 科学理解(7步法≥L2 + 图料三件套 + 素材智能入库 + 两点讲明白)
      → 报告.docx(Word适配) + PPT交用户
      → ⛔ 硬性停顿：用户读完回复「继续」（未收到禁止推进）
→ KSP-03.5 主题共识 + 内容重点协议            ▲拍板#17 重点圈选(多选)
→ KSP-04 概念先行(各出5概念→四维评分→红队挑战→只深化所选)  ▲拍板#9 概念选一/融合
→ KSP-05 口播稿(2-3方案竞稿)                  ▲拍板#16 口播方案
      ★ 顺序铁则：口播稿 → 九宫格 → 才做分镜
→ KSP-04.5 九宫格风格预览 → 风格基线固化       ▲拍板#15 风格预览
→ KSP-06 制作交付+出口闸(关内含执行：分镜‖声音 → 摄影 → prompt分段‖剪辑 → 美术VI复核 → 科学复核)
      → check_all.py(满配 16 项 · 通用常跑 13) → 红队前置闸 → 出口闸L4 → 检察官五层 → 交付(两档) → L5 签收
→ KSP-07 知识萃取归档(域片段→重建图谱 + FAILURE-LIBRARY追加 + delivery/归档)

★ 剧集项目另走「剧集通道 KSP-E1~E5」(docs/USER_SOP.md §2.5 + playbooks/series-production.md)：
   E0 判型(KSP-01 卡上，判死"是不是剧集") → E1 全季分集大纲(拍板) → E2 风格圣经(拍板) → E3 逐集循环
   → E4 跨集一致性闸(独立上下文 + check_series_consistency.py + check_bible_pin.py) → E5 发布节奏与追更
   ★ C∩B 在剧集里：OP/ED ＝ 固定资产（一次生产全季复用，只换"集别定制位"；逐集逐秒相等·D-S1）
     → playbooks/op-ed-mv.md；不新增关卡（挂 KSP-E2 圣经 ＋ KSP-E1 时长预算之下）

★ 音乐驱动段走「通道 C」(横向能力·硬规则 #44·不新增关卡·playbooks/mv-production.md)：
   挂接：C∩A 挂 A 的 KSP-01~07（＋广告法合规／品牌 VI）＝ 品牌·产品音乐片／主题曲 MV／活动 MV／音乐营销片
         C∩B 挂 KSP-E2 圣经 ＋ KSP-E1 时长预算 ＝ OP/ED／插入歌／角色曲 PV／预告 MV；纯 C ＝ 独立单曲 MV
   流程：歌先行(词曲) → 卡点表(templates/mv-beat-sheet.md 唯一模板) → 镜头表 → 素材复用 → prompt → 装配验收
   ★ C 段内无对白／无口播；C 规则（卡点／文字白名单／无对白）不外溢到 A 口播片与 B 正片（硬规则 #44③）
   ★ 不得给 C 段编"四场脊椎／剧透结构"，不得把 OP/ED 当叙事正片做（硬规则 #43③）
```

**触发方式**：把本文件夹装入 agent 环境的 user skills 目录（`~/.dsh/skills/kesheng`），**提出任意 AI 视频需求即触发**（广告片／科普／科研视频／产品品牌片／剧集动漫／MV·OP·ED 均可）。
**全自动模式**：用户说"全自动跑完"或 L 档时，用 DSH `workflow` 工具跑 `orchestration/kesheng_workflow.js`（args: `topic`/`runDir`/`platform`/`audienceMode`/`withCouncil`），跑完由制片人做裁决与用户关卡。
**`kb/`** 用 Obsidian 打开即得知识图谱（Graph View）。

---

## 七、技能协同（外部技能赋能，别从零造）

| 用途 | 用什么 |
|---|---|
| **Word 报告** | `scripts/md_to_docx.py`（内置 Word 适配）或 `report-writer`（含质检） |
| **PPT / Deck** | **`ppt-master`**（原生可编辑 PPTX；按 routing 选一条路由；⛔BLOCKING 停等用户；Image-first 必搜真图）／ **`huashu-design`**（高保真 HTML deck，可导 PDF/可编辑 PPTX；🔴三方向硬门不豁免）——见 `playbooks/ppt-deck-flow.md` |
| 图谱/报告工具 | `packs/kg_query.py` · `scripts/build_union_kg.py` · `build_science_report.py` |

> **衔接铁则**：外部技能的门 = 科生的拍板点，一律用 `ask_user_question` 选项卡执行；品牌资产取自拍板 #18/#19（官方源取色，禁自造）。

---

## 八、隐私约定

`kb/` 只收录**公开通用**科学知识。每个项目收尾按 `kb/入库规则.md`（收录门槛与流程）与 `kb/隐私红线.md`（三分法分拣与脱敏检查）执行——**项目专有信息（未公开数据/产品/技术路线/客户身份/合作方/指标数值）绝不入库**；图谱只收泛化后的通用方法学与公开论文结论。
