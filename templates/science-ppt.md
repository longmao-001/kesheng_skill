# 科学讲解 PPT（可上图）

> **用途**：把 `science-report.md` 正文转成一份**能直接讲/给用户看**的 PPT。每页 `标题 + ≤3 条要点 + 配图（可选）+ 出处`。配图优先来自**素材库**（`assets-inventory.md` 条目），没有就用**文生图 prompt**（套 `image-gen-formulas.md`），禁用水印/竞品/未授权图。
> 产出：`runs/<slug>/scientist-讲解-大纲.md`（页序大纲）+ 最终 deck（`scientist-讲解.pptx` 或 HTML deck）——**用 `ppt-master` / `huashu-design` 生成**（见 §生成方式 + `playbooks/ppt-deck-flow.md`）；`scripts/build_science_report.py` 直出的 pptx 仅兜底。

## 页序（建议 10-13 页）

| # | 页 | 内容 | 配图 |
|---|---|---|---|
| 1 | 封面 | 主题 + 一句话定位 + 出品方/日期 | 主体封面图（产品/场景） |
| 2 | 一句话定位 | 20 字内让外行懂 | — |
| 3 | 重点速览 | 核心看点 3 条（是什么+为什么） | — |
| 4 | 时间线 | 关键里程碑（年份+事件） | 时间轴图（可后期） |
| 5 | 产品是什么 | 构成/模块/材质（上上下下讲透） | 产品图/结构图/爆炸图 |
| 6 | 工作原理 | 输入→操作→输出，关键创新 | 原理示意图 / 过程演示 |
| 7 | 关键部件/细节 | 部件名+作用（出光窗/鳍片/接口…） | 部件特写（`RF_PART_*`） |
| 8 | 产品卖点① | 任务→需求→卖点→证据 | 实测/对比图（`IN_*`） |
| 9 | 产品卖点② | 同上（第二/三条） | 应用场景图（`RF_SCENE_*`） |
| 10 | 科学原理 | 背后机理/因果链 | 原理示意图 / 数据曲线 |
| 11 | 关键数据 | Top 5 数据带基准+来源 | 曲线/参数表（`CT_DATA_*`） |
| 12 | 待确认 + 深度自评 | 不确定项 + L 级 | — |
| 13 | 谢谢 / 展望 | — | 主体收尾图 |

## 每页格式
```
## 页N · <标题>
- 要点1（≤20字）
- 要点2
- 要点3
配图: assets-inventory 条目号 或 文生图prompt（简述如何取/放哪）
出处: <数据/图片来源，标引用>
```

## 生成方式

> **完整流程见 `playbooks/ppt-deck-flow.md`**（含技能选型 / 输入契约 / 外部技能门控 / 与科生拍板机制的衔接 / 自检）。

- **产出大纲**：`python -X utf8 scripts/build_science_report.py --json <science-data.json> --out runs/<slug>/` → 自动生成 `scientist-讲解-大纲.md`（本模板页序）+ `scientist-报告.docx`（Word 适配）+ `.pptx` 兜底。
- **技能赋能（优先，别从零拼）**：
  - **`ppt-master`** —— **原生可编辑 PPTX**；按它的 `workflows/routing.md` 选**恰好一条**路由（generate-pptx / Quick / image-to-pptx / beautify / create-template / fill-native / enhance）；**⛔BLOCKING 门必须停下等用户**；**Image-first：新任务必须先搜真实图，禁"无图也行"**。→ 要"能改稿/交客户"选它。
  - **`huashu-design`** —— **高保真 HTML deck**（可导 PDF / 可编辑 PPTX）；🔴 **三方向硬门**：任何新视觉设计必须先出 **3 个差异化方向真实初稿**（多页 deck = 每方向 2 页代表页）让用户选，**指定风格也不豁免**；Gate 文件 `brand-spec.md` + `direction-approved.md` 必须落档；反 AI slop 禁区（紫渐变/emoji 图标/圆角卡片+左 border/SVG 画人脸）。→ 要"好看/路演级"选它。
  - `markdown-exporter`（MD→PPTX）· `pipitmk`（Deck DSL→可编辑 PPTX）· `report-writer`（docx + 质检）—— 轻量转档备选。
- **两条铁律**：① 外部技能的门 = 科生拍板点，**用 `ask_user_question` 选项卡执行**（huashu 三方向的选择原话记进 `direction-approved.md`）② 科生**先出大纲+资产**（内容正确）→ 技能出视觉 → 科生按 `quality-gate.md` 验收（科学准确/禁区/图文对位/数据人工锁值）。
- `science-data.json` 结构：`{title, oneLiner, keyPoints[], timeline[], productPrinciple, sellingPoints[], science, data[{value,baseline,plain,cite}], pending[], depth}`。
