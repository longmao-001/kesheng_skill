# 自建素材库 → 参考图使用（Asset Library Flow）

> **功能**：把客户/网上的素材，**分析 → 拆解 → 重命名 → 保存建库 → 参考图使用**，一步到位。产物 = **全库唯一索引 `assets_index.json`（机器）＋ `assets_index.md`（人读清单）**，选片直接用。
> **铁则**：**入库即标签（Ingest-and-Label，硬规则 #41）**——素材入库这个动作**本身** = 规范命名 ＋ 写 sidecar ＋ 入唯一索引，三件事**一次做完**；没做完＝**这件素材没入库**（不因"先收进来以后再整理"而放行）。**标签不是事后文档，是入库动作。**
> **工具**：`scripts/ingest_asset.py`（**入库即标签执行器**：命名校验＋写 sidecar＋vision 块落盘）· `scripts/asset_index.py`（**唯一索引读写**）· `scripts/check_asset_labels.py`（**标签门控**：盘上↔索引双向核对，缺口＝FAIL）· `scripts/asset_schema.md`（**字段字典**：sidecar/索引字段定义与 trace_status 判据）· `scripts/extract_docs.py`（PDF/PPTX/DOCX 批量抠图+抽文+台账骨架）· `scripts/classify_assets.py`（历史命名分类，迁入时用）· `scripts/annotate_assets.py`（智能入库脚手架，被 ingest_asset 取代）· `templates/assets-inventory.md`（历史台账形态）· `templates/reference-selection.md`（选片）。
> **按文件类型的固定处理动作（视频/图片/矢量/PPT/PDF/Word/CAD/SolidWorks/SU/3D/字体/表格/音频）见 `docs/ASSET-TYPES.md`**——提取方式因类型而异，提取完统一汇入本流程后端（**且必须走"入库即标签"三步，不得只落盘不落标签**）。
> **流程图**：`docs/SOP-FLOW.md` 图二（素材处理流程）。

---

## ★ 入库即标签（Ingest-and-Label）· 核心章节

> **来源＝红楼梦EP01·用户裁定 20260917（硬规则 #41）**。本项目实证：**51 件在库素材，仅 11 件有完整 prompt 记录，39 件的 prompt 只活在对话里**——台账建完即过时，索引散在五处（对话/台账/refs/分镜表/prompt 文件）。**结论：靠人工事后补标签，永远滞后于生产**；标签必须成为**流程关卡（入库动作的一部分）**，由脚本门控兜底。

### 一句话

**素材入库 = 三件事一次做完：①命名规范 ②写 sidecar ③入唯一索引。** 三者缺一，该素材**视为未入库**（不得用于参考/交付，不得计入选片候选）。

### 三步动作（入库那一刻，逐件执行，不可后补）

| 步 | 动作 | 判据（不合规怎么办） |
|---|---|---|
| **① 命名即规范** | 文件名固定格式 **`<类型>-<ID>-<名称>-<版本>.<ext>`**（如 `IMG-A007-散热鳍片-场景锚-v3.png`） | **不合规不入库**：`ingest_asset.py` 命名校验不过 → **拒绝落库**（先改名再入库；禁"先入库回头改名"） |
| **② 入库即写 sidecar** | 同目录同名 sidecar（`<同文件名>.label.json`，字段见 `scripts/asset_schema.md`）：**采纳版 prompt 全文**（含【负面】）＋**参考组**（@图片N=实际文件名（取哪→放哪））＋**上传顺序**＋**trace_status**＋**vision 块** | sidecar 缺字段 = `label_gap` → **门控 FAIL**；prompt 无原文者**不得留空**，须按 trace_status 三档如实标注 |
| **③ 入库即入索引** | 一件素材一条记录写入**全库唯一索引** `assets_index.json`（机器）＋同源生成 `assets_index.md`（人读清单） | 索引里没有 = **orphan**（盘上有、索引无）→ **门控 FAIL**；**禁"先落盘、索引回头批量补"**（回头补＝永远滞后＝F-59） |

**字段口径要点**

- `<类型>`：`IMG`（图片）/`VID`（视频）/`VEC`（矢量）/`PPT`/`DOC`/`CAD`/`3D`/`AUD`/`FONT`…（对齐 `docs/ASSET-TYPES.md` 的类型表）。
- `<ID>`：项目内**唯一且不复用**的序号/编号（**入库即分配，禁事后重排**——重排＝引用全断）。
- `<版本>`：单调递增 `v1 → v2 → v3`；**`final`/`最终`/`定稿` 不作为版本词**（承 F-29 与硬规则 #40③"每集只有一个「定稿」版本"），旧版归 `_archive/`。
- **历史命名**（`<用途>_<类型>_<主体>_<视角>_<序号>`，`classify_assets.py` 一代）**迁入时一次性改名为新格式**，旧名**原文保留在 sidecar 的 `legacy_name` 字段**留痕（**禁两边并存两套命名**）。

### agent 侧强制动作（每件入库必做·vision 块）

- **每件素材入库时，agent 必须 `read_image` 至少一次，并写 vision 块**（**构图 / 主体 / 墨阶（明暗层次·色彩层次）/ 留白 / 异常**五栏）——这是**入库动作的一部分**，不是"另外抽空看图"。
- **由脚本落进 sidecar**：vision 块经 `scripts/ingest_asset.py` 写入 sidecar 的 `vision` 字段（**写进对话不算数**——只在对话里的判据＝未落盘，承 F-42）。
- **异常栏非空即须处置**：水印/竞品/未授权/糊/裁切错误等，写入 `vision.anomalies` 并给 `usage_block: true`（该件**不得入镜、不得作参考喂模型**）。
- 媒体类型不适用（音频/字体/表格）时，vision 块按 `scripts/asset_schema.md` 的类型特化字段填写（禁留空、禁写"不适用"了事）。

### trace_status 三档（**禁止伪造"逐字"**）

| 档 | 判据 | 后果 |
|---|---|---|
| **逐字** `verbatim` | **有原始 prompt 原文**（含负面）可逐字复制，出处落盘（文件+条目号） | 可复用、可跨集交付、可作交付件 |
| **重构** `reconstructed` | 只有要点/纪要，按要点**复原**；**须显式标注**（`trace_status: reconstructed` ＋ `reconstructed_from: <出处>` ＋ 复原不确定项标"待确认"） | 可作参考与二次生成依据，但**交付前须复核**；**不得冒充原文** |
| **缺口** `missing` | **无任何记录**（prompt 只活在对话里/已不可考） | **计入门控 FAIL**：不得作交付件、不得作跨集复用依据；处置＝**补录（找原始出处）或重抽**，并在索引内标 ❌ |

- **禁令（红线）**：`verbatim` **只能**用于"确有原文"的件。把 `reconstructed`/`missing` 标成 `verbatim` ＝ **伪造"逐字"＝流程事故**（与"数据必须=手册原文""事实不折中"同级）。
- **判据唯一事实源＝sidecar＋索引**；对话记录、记忆、口头说明**一律不作为 trace_status 依据**。

### 双向核对（盘上 ↔ 索引，缺一即 FAIL）

```
python -X utf8 scripts/check_asset_labels.py runs/<项目slug>/     # 标签门控
```

三条判据（任一命中即 FAIL，逐条列文件名，不许"总体通过"）：

1. **orphan**：盘上有、索引无（＝漏登记，最常见）；
2. **ghost**：索引有、盘上无（＝索引虚记/文件被移走，引用必断）；
3. **label_gap**：sidecar 缺字段（prompt 全文/参考组/上传顺序/trace_status/vision 任一缺）或 `trace_status: missing`。

**工具分工**：`scripts/asset_index.py`＝唯一索引的读/写/重建（**索引只能由它生成**，禁手改 `assets_index.json`，禁手改 `assets_index.md`）；`scripts/ingest_asset.py`＝单件入库（命名校验＋sidecar＋vision 落盘＋追加索引一条）；`scripts/check_asset_labels.py`＝门控（退出码沿用本 skill 门控约定：**0 通过 / 1 有 FAIL / 2 不可判定**，以脚本 `--help` 实际输出为准；**空跑不算通过**）。字段与判据全部以 `scripts/asset_schema.md` 为准。

### 单一索引原则（全库只有一份索引）

- **全库唯一索引**：`assets_index.json`（机器可读、门控读它）＋ `assets_index.md`（**同源生成**的人读清单，交付给用户看的就是它）——两者**由 `asset_index.py` 从 sidecar 生成，禁手写、禁并行维护**。
- **历史台账仅作留痕**：`assets-inventory.md`、`m5-素材prompt溯源台账.md`、`m5-参考挂载对照表.md` 等**转为历史留痕**（保留可查，**不再作为选片/复用依据**）；**禁止多份台账并行**——多份台账＝**同一素材多个"事实"**＝漂移源（与硬规则 #40④"单一事实源"同源）。
- **迁移一次性收敛**：历史台账里的条目经 `ingest_asset.py` **逐件迁入 sidecar＋索引**（trace_status 如实标注），迁完旧台账封存；**禁"新索引建着、旧台账改着"**。

### 为什么（本项目实证 · 为什么会滞后）

- **实证数据**：51 件在库素材 → **仅 11 件有完整 prompt 记录** → **39 件 prompt 只活在对话里**（换个会话/换个人即不可复现）。
- **滞后机制**：标签**没有关卡**（收素材的入口不管标签）→ 标签只能靠人工"事后补" → **生产速度 > 补录速度** → **台账建完即过时**（补完 A 段，B 段又新增了）。
- **修正**：把标签从"事后动作"改成"**入库动作本身**"（本文件三步）＋ 脚本门控 `check_asset_labels.py`（缺口＝FAIL）＋ 硬规则 #41（**不是建议，是关卡**）。

---

## 一步流程（五步闭环 · 与「入库即标签」的对应关系）

```
① 收集      素材目录（官方渲染/实拍/结构图/PDF-PPT抠图/网图/CAD-3D导出件/矢量）
      │        ★ 按类型处理：见 docs/ASSET-TYPES.md（各类型提取动作+红线不同）
      │        ⚙ PDF/PPTX/DOCX 一键抠图+抽文：python scripts/extract_docs.py <输入> --out runs/<slug>/ --subject <主体>
      │
② 分类+重命名  → 【标签动作① 命名即规范】<类型>-<ID>-<名称>-<版本>.<ext>
      （历史命名迁移用 scripts/classify_assets.py <目录> --subject <主体> [--apply]；不合规不入库）
      │
③ 智能入库     → 【标签动作②③ 写 sidecar ＋ 入索引】逐件：read_image → vision 块（构图/主体/墨阶/留白/异常）
      （＋采纳版 prompt 全文/负面/参考组/上传顺序/trace_status）→ 由脚本落 sidecar 并追加索引一条
      执行：python -X utf8 scripts/ingest_asset.py <素材文件> --run runs/<slug>/ --id <ID> [--trace-status verbatim|reconstructed|missing]
      │
④ 唯一索引     assets_index.json（机器）＋ assets_index.md（人读清单，同源生成）
      （历史台账 assets-inventory.md / m5-素材prompt溯源台账.md 仅作留痕，不再作选片依据）
      │
⑤ 参考图使用    按 sidecar 标签/采纳版 prompt 命中该镜对位需求 + 高分优先 → 挑≤3张 → 标角色+部位+位置 → @图进prompt
     → check_asset_labels.py（FAIL 即回退补标签后重跑）→ check_reference_selection.py → 图文对位检察官
```

## 关键点

- **入库即标签（硬规则 #41）**：命名 / sidecar / 索引三件事**在入库那一刻**完成；**"先收后整"一律视为未入库**（这是本流程第一铁则，其余各点都在它之下）。
- **按类型处理**：不同类型文件的"提取动作+红线"不同（视频抽帧+竖屏重构图+勿叠logo／矢量光栅化+保留矢量源+官方取色／PPT-PDF-Word 全量抠图+抽文标出处／**CAD·3D 须客户导出或外部渲染，不能直喂 AI**）——见 `docs/ASSET-TYPES.md`。
- **文件名=条目ID**：引用一律用文件名（**新格式 `<类型>-<ID>-<名称>-<版本>.<ext>`**），禁凭记忆翻文件夹；改文件名＝改 ID，须走 KSP-C 并同步索引（承硬规则 #40③ 版本收敛）。
- **拆解=文字检索键**：每张必须 `read_image` 拆解（**vision 块五栏**）＋采纳版 prompt（**trace_status 如实标注**）＋ 质量分（★≥4 优先，★<3 除非无替代）——**标签就是最快找图的方式**。
- **选片**：候选 = **从唯一索引**按标签/prompt 命中需求（**不从对话、不从旧台账翻**）；**高分优先**；`trace_status: missing` 的件**不得作交付件**。
- **只用自建库**：参考图/首帧/图表层 prompt 一律从**唯一索引**选，不凭空 AI 生成（零意外、自包含；承硬规则 #14）。
- **合规**：禁用红线（水印/竞品/未授权）+ `ad_forbidden_words.py`（绝对化/疗效词）；`vision.anomalies` 命中的件一律 `usage_block: true`。
- **联动**：硬规则 **#30**（asset 溯源：素材↔采纳版 prompt↔参考组）、**#37**（跨集资产复用：复用索引随圣经维护，**索引可查才谈得上复用**）、**F-42**（素材在库、出处不在库）、**F-54**（资产未登记复用→重复抽卡）、**F-59**（素材标签事后补＝永远滞后）。
