# kesheng_skill — 科生：科研视频制作团队 Skill

> 多 agent 编排驱动的**科研/高精尖技术 AI 视频制作团队**。不直接生成视频；交付专业团队水平的东西：
> 制作方案、口播脚本、分镜表、逐镜 AI 视频 prompt（可灵/即梦/Vidu/海螺/Runway/万相/Seedance/LibTV/cgprism）、
> 手把手制作流程、Word 适配的科学报告 + 讲解 PPT。
>
> **用户定位**：用户是冲着 **AI 视频生成**来的——主玩法是在各平台画布/节点上自己动手。所以交付物是
> **「多平台上手素材包」**（每镜：平台对照 prompt + 参考图包 + 口播 + 抽卡建议 + 画布步骤），
> 所有后期环节都给 **AI 原生路径**（自动字幕/一键调色/曲库配乐/模板数据卡）；专业后期=可选增强，永不是前提。

---

## 一、核心机制（四件事）

1. **真多 agent 协作**：制片人（主 agent）编排；导演/编剧/分镜师/美术指导/摄影指导/声音设计师/剪辑师/科学顾问/prompt 工程师/观众代言人/红队/检察官 以**独立上下文 subagent** 并行作业、黑板（`runs/<项目slug>/`）交接、制品门控。
2. **KSP 状态机流程**（KSP-01~07 + KSP-C 变更控制）：立项定档 → 简报+预注册 → **科学理解（报告=中间交付件，等用户「继续」）** → 主题共识+内容重点 → 概念先行 → 口播稿 → 九宫格风格 → 执行（分镜/声音/prompt/剪辑）→ 出口 → 萃取归档。
3. **拍板卡 + 证据先行**：每关必用 `ask_user_question` 选项卡（≥2 选项、推荐置顶、留"自定义"兜底）；基于文件拍板**必须先展示依据**再给选项，禁盲选。全部 **19 个拍板点**见 `templates/user-gate.md`。
4. **机器门控（考勤式）**：不信任"代理人觉得做了"，以**产物 + 校验脚本**为准。`scripts/check_all.py` 一键跑 8 项门控。

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
| **`docs/SOP-FLOW.md`** | **完整 SOP 流程图**：图一 KSP 主流程 + 图二 素材处理 + 图三 PPT/Deck；含**全部 19 拍板点**、**8 项门控对照**、**检察官五层**、**硬规则 15 条**。**同名 PNG/PDF 为图示成品**（`SOP-FLOW-KSP主流程` · `SOP-FLOW-素材处理` · `SOP-FLOW-PPT流程`），用 `python -X utf8 scripts/render_sop_flow.py` 重新出图 |
| **`docs/USER_SOP.md`** | KSP-01~07 + KSP-C 逐关规范（**流程权威**） |
| **`docs/ASSET-TYPES.md`** | **按文件类型的固定处理方案**（视频/图片/矢量/PPT/PDF/Word/CAD/SolidWorks/SketchUp/3D/字体/表格/音频：提取动作+归类+红线） |
| **`SKILL.md`** | 入口：人设、铁律、里程碑工作流、团队编制、执行模式、启动必读清单 |
| **`orchestration/ORCHESTRATION.md`** | 编排手册：工具映射、派活 prompt 模板、里程碑派活清单、**§5 硬规则 1-41**（含 #27 字卡口径、#31 逐镜文学闸、#32 文字参考图（字帖）、#33 OP文字白名单、#34 禁亮词、**#35–#40 剧集六条：全季规划先行/风格圣经先行/跨集资产复用/跨集一致性门控/集尾钩子与追更/剧集目录与版本规范**） |
| **`protocols/quality-gate.md`** | 七维评分 + 禁区 + **检察官五层** |
| **`templates/user-gate.md`** | 19 个拍板点预置选项速查 |

> **启动必读（每次使用先读全，读全前禁止派活/建文件）**：`docs/USER_SOP.md` · `orchestration/ORCHESTRATION.md` · `protocols/quality-gate.md` · `playbooks/production-workflow.md` · `templates/user-gate.md` ＋ `knowledge/FAILURE-LIBRARY.md`（失败图书馆，防重复踩坑）。

---

## 四、目录结构

```
SKILL.md              入口：人设/铁律/里程碑/团队编制/执行模式/启动必读
README.md             本文件
docs/     (7)         USER_SOP(KSP流程权威) · SOP-FLOW(完整流程图) · ASSET-TYPES(按类型处理方案)
                      ROLE_WORKFLOWS(角色SOP) · DESIGN(架构设计) · KG_DOMAIN_DESIGN · PAPER_INGESTION
agents/   (13)        制片人 · 导演 · 编剧 · 分镜师 · 美术指导 · 摄影指导 · 声音设计师 · 剪辑师
                      科学顾问 · prompt工程师 · 观众代言人 · 红队 · 检察官
orchestration/        ORCHESTRATION.md(编排手册·硬规则1-41) · kesheng_workflow.js+.meta.json(全自动 fan-out)
protocols/            meeting.md(会议协作协议) · quality-gate.md(三态门控+检察官五层)
playbooks/ (9)        production-workflow(端到端) · asset-library-flow(素材库→参考图) ·
                      ppt-deck-flow(PPT交 ppt-master/huashu-design) · science-report-flow(M2→M3交接闸) ·
                      platform-prompts(各平台公式·含Seedance2.0/2.5核实版) · storyboard-grid(宫格技法) ·
                      consistency(跨镜一致性) · animation-motion-design(动画性纪律) ·
                      **series-production(剧集制作·KSP-E1~E5 必读)**
templates/ (24)       brief · proposal · storyboard · decision-log · breakdown · handoff ·
                      prompt-sheet(格式规范) · prompt-sop(写prompt十步) · prompt-file ·
                      product/video-prompt-formula ·
                      prompt-formulas(可复制公式库) · narration-formula(口播句公式F01-F14) ·
                      science-report · science-ppt · visual-baseline · reference-selection ·
                      assets-inventory(智能入库) · user-gate · l3-fact-inspector-report ·
                      **season-outline(全季分集大纲) · show-bible(风格圣经) · episode-brief(单集简报) ·
                      series-config.json(剧集门控词表)**
knowledge/            工艺知识库(历史权威正文)：hooks/ · ad-copy · tvc-ad-templates · camera-language ·
                      image-gen-formulas · prompt-reverse · seedance-template-library · vi_styles/ ·
                      痛点链/文案层/动感三来源/首帧锚定/素材分级/图表层/全能参考三用法 · index.md ·
                      **FAILURE-LIBRARY.md**(失败图书馆·跨项目·开工先读)
kb/                   科学知识图谱(Obsidian vault)：按领域分文件夹 + 入库规则.md + 隐私红线.md
packs/    (27片段)    统一知识图谱：kesheng-kg/(并集大图 3634实体 · 13 domain 分区) + kg_query.py 查询
                      域片段：scientist/screenwriter/director/creative/narration/prompt/audience/
                      audio/redteam/lessons/workflow-seed/sop-seed/gate-seed + papers-*(10个论文片段)
                      + rednote-industry-kg(产业) + xhs-cases-kg
scripts/  (76)        门控/工具脚本（见下节）
runs/                 项目工坊（黑板）：每项目一个 runs/<项目slug>/（只放项目，临时目录交付前删）
```

---

## 五、机器门控（`scripts/check_all.py` 一键 8 项）

| # | 脚本 | 拦什么 |
|---|---|---|
| 1 | `check_sop.py` | 跳 SOP / 缺产物 + 每镜 prompt 字段不全 |
| 2 | `check_prompt_sheet.py` | prompt **格式与一致性**：核心字段 / 口播并入画面 / 口播≠口播稿 / 风格 token 不一致 / 参考漏挂 / 负面空（兼容 `**字段**：` 与 `【字段】` 两代格式） |
| 3 | `check_prompt_sop.py` | **写 prompt 十步 SOP 的执行证据**：参考图裸引用 / 风格不同源 / 口播≠口播稿 / 时间轴无分段 / 缺 README = FAIL；缺"部位对应·放哪位置"/产品镜缺"保真实造型"/参数缺项 = WARN |
| 4 | `check_asset_pack.py` | 素材自包含（@引用可解析、无"待补充/拍照"后补提示词） |
| 5 | `check_delivery.py` | **交付件版本收敛**：多源并存 / 交付包死链 / 口播稿多版本漂移 |
| 6 | `ad_forbidden_words.py` | 广告禁用词（绝对化·极限词 / 疗效承诺 / 平台禁语） |
| 7 | `check_runs_clean.py` | `runs/` 混入非项目散落物 |
| 8 | `check_docs_integrity.py` | **技能级**：SOP 断链 / 孤岛（写了没人读）/ 启动必读与门控脚本不一致 |
| 9 | `check_series_consistency.py` | **剧集层·跨集一致性（KSP-E4 · D-S1–D-S8）**：OP/ED 时长固定资产逐集相等 / 锚复用与版本漂移 / 同文本同帖 / 母题唯一与复现声明 / 钩子账本兑现责任人 / 专名逐字一致 / 新增入册 / 全季红线继承。读 `runs/<季slug>/series-config.json`（模板 `templates/series-config.json`），支持 `--season`/`--ep EPnn`/`--json`；**0 集 / 0 prompt 文件 / 缺配置＝exit 2，空跑不算通过**；**非剧集项目由 `check_all.py` 自动跳过**（说明：`scripts/README-check_series_consistency.md`） |

**其他脚本**：`check_reference_selection.py`（选片要素）· `check_residual.py`（旧表述残留回归）· `extract_docs.py`（PDF/PPTX/DOCX → 抠图+抽文+台账骨架）· `classify_assets.py`/`annotate_assets.py`（素材分类命名/智能入库脚手架）· `md_to_docx.py`（Markdown → **适配 Word** 的 docx：封面/目录/页眉页脚页码/中文字体/首行缩进/真表格）· `build_science_report.py`（科学报告 → 结构化 md + Word适配 docx + PPT 大纲）· `build_union_kg.py`（图谱并集重建）· `packs/kg_query.py`（图谱查询）。

> **门控哲学**：SOP 条目必须同时有 **①文字条文 ②机器门控 ③人工闸（红队/检察官）三层**，缺一层就等于没写（ORCHESTRATION §5-23）。
> 门控报错先分"真缺"还是"格式别名误报"——**误报=修脚本，不迁就脚本改制品**（F-30）。

---

## 六、快速上手（制片人节奏）

```
开工 → 读全核心流程5份 + FAILURE-LIBRARY → todo_write 清单
→ KSP-01 定档(S/M/L)                         ▲拍板#1 定档 #18 品牌用字
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
      → check_all.py(单集9项) → 红队前置闸 → 出口闸L4 → 检察官五层 → 交付(两档) → L5 签收
→ KSP-07 知识萃取归档(域片段→重建图谱 + FAILURE-LIBRARY追加 + delivery/归档)
★ 剧集项目另走「剧集通道 KSP-E1~E5」(docs/USER_SOP.md §2.5 + playbooks/series-production.md)：
   E0 判型(KSP-01 卡上) → E1 全季分集大纲(拍板) → E2 风格圣经(拍板) → E3 逐集循环
   → E4 跨集一致性闸(独立上下文 + check_series_consistency.py) → E5 发布节奏与追更
```

**触发方式**：把本文件夹装入 agent 环境的 user skills 目录（`~/.dsh/skills/kesheng`），提出科研视频需求即触发。
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
