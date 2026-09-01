# 科生统一知识图谱 · Domain 设计（v2）

> 版本 2026-09。总图：`packs/kesheng-kg/kg.json`（并集 KG，2166+ 实体 / 4700+ 关系），域=图谱内一级分区，分区索引 `kb/index.md`，查询 `packs/kg_query.py --domain <域>`。

## 0. 设计原则

1. **角色对齐**：域基本 = 真实剧组建制的一个部门/岗位（导演·编剧·分镜师·美术指导·摄影指导·声音设计师·剪辑师），让每个 subagent 一查就能拿到本岗知识（角色→域映射见编排手册 §3.5）。
2. **主域唯一，双域例外**：每个实体有 `domains` 列表；绝大多数单域，只有"真正跨角色共用"的概念才双域（如 画风/风格方向 = 美术定调 + prompt 写法）。
3. **写什么 vs 怎么做分离**：`prompt` 域管"写什么"（平台×镜头×风格×画风的公式词表）；`工艺` 域管"怎么做"（流程与规则）——流程是跨角色工艺，不归任何单一岗位。
4. **知识分层**：域内实体分四层——事实层（平台能力/字体授权）、方法层（公式/流程/规则）、词表层（标签/运镜词/负面词）、风险层（翻车/禁忌/失败模式，红队域）。
5. **种子允许稀疏**：新岗（导演/声音/剪辑）先有最小种子，靠项目收尾萃取循环生长；数据不编造，空即"待积累"。

## 1. 域地图（12 域）

| # | domain | 角色/受众 | 定位 | 实体类型（主要） | 当前量级 |
|---|---|---|---|---|---|
| 1 | **科学** | 科学顾问 | 科学概念/类比/数据点/缺口/铁律 | ScientificConcept·Analogy·DataPoint·KnowledgeGap·FactRule·UnderstandingLevel·Domain·Company·Method·Milestone | 115 |
| 2 | **叙事** | 编剧 | 钩子/结构/CTA/受众模式叙事要求 | HookType·NarrativeStructure·CtaFormula·ScriptTemplate·AudienceMode·WritingRule·AdCopyLaw | 40 |
| 3 | **导演** | 导演 | 导演阐述/艺术基调/节奏曲线/定剪/裁决 | DirectorStatement·ArtBaseline·TempoCurve·FinalCut·CrossDeptConfirm·Gate | 3→10 |
| 4 | **分镜** | 分镜师 | 景别/构图/视觉隐喻/节拍/宫格 | ShotType·VisualMetaphor·Beat·Concept·GridTechnique | 34 |
| 5 | **美术** | 美术指导 | VI 色板/参考资产规范/图表层规范/字体 | ViStyle·Scenario·FontFamily·FontRule·StyleDirection*·ArtStyle* | 87 |
| 6 | **影像** | 摄影指导 | 运镜/光影/拍法/可拍性/动感 | CameraMove·MovingTechnique·FeasibilityRule·Mood | 51 |
| 7 | **声音** | 声音设计师 | BGM/音效/配音/混音/版权 | BgmDirection·SoundFx·VoiceRule·MixRule·SoundRule | 16 |
| 8 | **剪辑** | 剪辑师 | 转场/节奏/字幕/调色/图表层执行 | Transition | 7 |
| 9 | **prompt** | prompt 工程师 | 平台×镜头×风格×画风 公式与词表（写什么） | Platform·PromptFormula·PromptStyleFormula·ArtStyleFormula*·ShotType·GenerateRoute·MoveTerm·Tag·NegativeRule·FailFix·ConsistencyTool·StyleTokenRule·ReferenceRule·ImageGenTool | 1779 |
| 10 | **工艺** | 全角色（制片人/导演/剪辑…） | 制作流程与规则（怎么做）+ **角色专属工作流程** | ProcessRule·ArtStyleRule·RoleWorkflow | 32 |
| 11 | **受众** | 观众代言人 | 受众模式/参数/痛点链/证据 | AudienceMode·AudienceParam·ValueChain·EvidenceType·RetentionRule·MisalignmentPattern | 30 |
| 12 | **红队** | 红队 | 失败模式/禁忌/检查维度/攻击视角/闸点 | FailureMode·Taboo·CheckDimension·AttackAngle·GateCheckpoint·RebuttalRule | 53 |
| 13 | **产业** | 科学顾问/制片人/观众代言人 | 行业信息（半导体/量测检测等）：概念·公司·市场数据·小红书工业品创意 | IndustryConcept·MarketData·Company·RednotePattern\*·RednoteRule\* | 47 |

\* = 双域实体（美术+prompt）。

## 2. 实体类型 → 域 映射（主域，节选）

| 类型 | 主域 | 说明 |
|---|---|---|
| Platform / PromptFormula / PromptStyleFormula / ArtStyleFormula | prompt | 平台能力 × 镜头/风格/画风的组合公式 |
| ShotType | prompt(公式用) + 分镜(设计用) | 双域：分镜师用"设计侧"、prompt 用"写法侧" |
| CameraMove / MovingTechnique / FeasibilityRule / Mood | 影像 | 摄影指导 |
| Tag / MoveTerm / NegativeRule / FailFix / ConsistencyTool / GenerateRoute / StyleTokenRule / ReferenceRule / ImageGenTool | prompt | 词表与工具层 |
| ProcessRule / ArtStyleRule | 工艺 | 跨角色流程与一致性规则 |
| FontFamily / FontRule | 美术 | 字库与规范（数据卡数字/字幕/落版） |
| StyleDirection / ArtStyle | 美术 + prompt | 双域 |
| Transition | 剪辑 | 转场选型 |
| BgmDirection / SoundFx / VoiceRule / MixRule / SoundRule | 声音 | 声音设计 |

## 3. 域间连线（跨域传播规则）

- **公式→平台/镜头/风格/画风**（prompt 内）：`formula-for-*`，子 agent 从公式出发可 1 跳拿到平台语法与镜头写法
- **工艺→镜头/平台/规则**：`process-for-shot` / `process-uses`，流程卡与具体镜头、平台连线
- **风格/画风→公式**：`style-formula-for-style` / `artstyle-formula-for-style`（美术定调 → prompt 写法）
- **字体→授权红线**：`governed-by`（美术内）
- **红队→质量**：FailureMode/CheckDimension 与 quality-gate/角色卡为 source，跨域引用经 sources 而非关系（后续可加 `failure-violates-rule` 线）
- 跨域实体合并规则：同 `Type:名称` 跨域重复 → 合并单节点、domains 并集（当前跨域重复 0 处待生长）

## 4. 覆盖与生长策略

| 域 | 状态 | 生长方式 |
|---|---|---|
| prompt | 🟢 种子充分（1779） | 新增平台/画风 → 改 expand_tables*.json 重建 |
| 科学 | 🟢 115 | 项目收尾萃取（kb/入库规则.md） |
| 美术/工艺/声音/剪辑 | 🟡 小种子 | 角色卡迭代 + 项目验证沉淀（每条知识带"项目验证"行） |
| 导演 | 🟡 3+种子 | 同上；下一步补导演阐述案例库 |
| 受众/红队/叙事/分镜/影像 | 🟢 充分 | 工艺概念卡持续更新（knowledge/ 映射） |

**验收口径**：域不为"小而全"而填数；宁可"待积累"，不可编造。每域可查询、可导航（孤立叶节点如标签/流程卡按名直查）。

## 5. 重建管线

```
expand_tables*.json (来源表, 4 张) → expand_prompt_seed.py → packs/prompt-kg/kg.json
                                                            ↘
director-seed / 其余片段 (kg.json) ──────────────→ build_union_kg.py → kesheng-kg/kg.json
                                                       → schema.yaml + kb/index.md
查: python packs/kg_query.py --domain <域> <关键词>
```
