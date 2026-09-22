# 素材标签规范（asset_schema）—— 「入库即标签」的字段与动作

> **适用**：任何会产生素材（锚图/首帧/参考图/字帖/故事板/成片/抽帧）的项目。
> **配套工具**：`scripts/asset_index.py`（索引器）· `scripts/ingest_asset.py`（入库器）· `scripts/check_asset_labels.py`（门控）；
> 三者与 `scripts/check_all.py` 的关系见 §八。
> **要解决的问题**（红楼梦 EP01 暴露）：素材在库 51 件，只有 11 件能凭落盘文件复现出处——**素材在库、出处不在库**，
> 换人执行/换会话就不可重出，跨镜一致性无据可依。本规范把「出处」变成**入库时必填的机器可读字段**。

---

## 一、命名规范（硬约束）

```
<类型前缀><ID>-<名称>-<版本或抽次>.<ext>
```

| 类别 | 前缀 | 示例 |
|---|---|---|
| 角色 | `C` | `C11-封肃-主版-v1.jpg` |
| 道具 | `Y` | `Y1-焦墨点锚-首帧-v1.png` |
| 场景 | `S` | `S1-青埂峰-阵末空缺-v1.png` |
| 字帖 | `Z` | `Z1-片名讖-魏碑-v1.png` |
| 故事板 | `B` | `B1-九宫格-第1抽.png` |
| 成片 | `F` | `F1-裂缝坠石-成片-v1.mp4` |

规则细则（`asset_index.check_naming` 机器判定，`ingest_asset.py` 不合规即拒绝入库）：

1. **首段 = 前缀＋ID**：前缀 1–2 个字母（上表），ID 为 1–3 位数字、可带一位小写字母（`C1a`、`S9`、`C11`）。
2. **名称段**：至少 1 段，不得含空格、点号、`、，/ \` 等标点（用 `-` 分段）。
3. **版本/抽次段（末段）**：`v1` / `v1.2` / `第1抽` / `第3版` / `第2稿` / `抽2`。
   项目若有惯用词（如 `主版`/`基础版`）把它写进 `asset_index.config.json` 的 `version_words` 白名单，不要私自放宽脚本。
4. **扩展名必须小写**。
5. **盘上已有存量件不合规**：门控 ③ 会报 FAIL；过渡期可用 `check_asset_labels.py --naming-warn` 降级为 WARN 并排期改名。

> 为什么卡这么死：`@图片N=文件名` 的挂载、跨集复用统计、`--ep EPnn` 复核全靠文件名当主键。
> 名字不规范＝引用解析不到＝下游上传报缺文件（红楼梦 EP01 就出现过 `S4-灵河岸-露珠修正版.png` 库内根本不存在却挂了 5 处）。

---

## 二、目录规范

```
<素材根>/                      # 默认 refs/（也认 assets/、素材/）
├── 角色/                       # 类别目录名 = 类别（可被 config.kind_dirs 改）
├── 道具/
├── 场景/
├── 字帖/
├── 故事板/
├── 成片/
│   └── <段号或镜头组>/           # 成片允许再分一层（如 成片/A-01/xxx.mp4）
├── _废片/    _旧版归档/    _作废归档/    _frames/     # 设计性排除目录：不计件、不计 orphan、不进索引（口径见下）
└── assets_index.json  assets_index.md  asset_gaps.md  asset_index.config.json
    <每个媒体文件>.label.json                            # sidecar 标签，与文件同目录同名
```

- **设计性排除目录（口径写死，20260921 门控裁定）**：`_废片`/`_旧版归档`/`_作废归档`/`_frames`
  为**设计性排除目录**：**不计件、不计 orphan、不进索引**；判废原因记录在各目录 README 或主表 `rejects` 栏。
  （同上口径含 `_trash`/`_归档`/`_tmp`/`_temp` 等 `_` 前缀目录。）
  - 机器行为：`asset_index.iter_media()` 直接跳过，索引只把它们列进 `excluded`（写「已排除 N 件」，**不静默丢弃**）；
    `check_asset_labels.py` 的双向核对同样只比对**非排除目录**，所以归档件**既不报未登记（orphan）、也不报断链**，
    **更不需要 sidecar**——归档件没有 sidecar 属正常形态，不是缺陷、不得据此补件或补计数。
  - 对应动作：判废件移入归档目录即视为「已留档」，其判废原因写在该目录 `README.md`（或主台账/主表 `rejects` 栏），
    不在索引里重复计一次废片。
- **中间产物**（视频抽帧联系表、缩略图）一律进 `_frames/`，不要与交付素材混放。
- 索引三件套与配置文件放**素材根的上一级**（即 `runs/<项目>/`），不要塞进素材目录里当素材。

---

## 三、sidecar 字段表（`<文件名>.label.json`）

sidecar 是**素材自己的标签**，跟着素材走；换目录/换机器都不丢。

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | str | ✅ | 文件名（含扩展名，改名后须同步） |
| `rel` | str | ✅ | 相对素材根的路径（机器主键） |
| `kind` | str | ✅ | 类别：角色/道具/场景/字帖/故事板/成片（由目录反推） |
| `type` | str | ✅ | 素材类型：`用户输入` / `模型生成` / `图生图派生` / `剪辑产物` |
| `tool` | str | ✅ | 出图/生成工具（Image2 / Seedance / 可灵 / 即梦 / LibTV…）；未知写「未知（待补）」 |
| `prompt` | str | ✅ | **采纳版 prompt 正文全文**（可整块复制重出）；缺口件留空并在 `trace_status` 标缺口 |
| `negative` | str | ✅ | 负面词整串（与正文同源，不得另起版本） |
| `refs` | list | ○ | `[{index, file, order}]`＝`@图片N=文件名`＋上传顺序 |
| `upload_order` | str | ○ | 「上传顺序：@图片1=…；@图片2=…」原文 |
| `date` | str | ✅ | `YYYYMMDD`（取文件 mtime 或显式给） |
| `rejects` | str | ○ | 判废原因/判废经历原文（判废件必填，采纳版可留空）；**旧值非空时索引重推不得覆盖** |
| `rejects_source` | str | ○ | 该 `rejects` 是谁写的：`human`（`--reject` 显式给，可改写）／`source`（来源 md 抽取）／`index`（索引重推）／`sidecar` |
| `scrapped` | bool | ○ | 是否废片（不得用于下游）；由「点名本件的判废证据」机器判定，可在入库时显式给 |
| `reuse` | str | ✅ | 复用记录，如 `EP01:1-16; EP01:28-01`（跨集复用的唯一依据） |
| `trace_status` | str | ✅ | **三档：`逐字` / `重构` / `缺口`**（定义见 §四）；**以 sidecar 为准，机器刷新不得自动改**（禁伪造逐字） |
| `trace_source` | str | ○ | 该 `trace_status` 是谁定的：`human`（人/回贴显式给，**机器此后不得改**）／`index`（索引重推）／空（历史件） |
| `verbatim_source` | str | ○ | **逐字来源凭证**（如 `m5-素材prompt回贴.md §3 L42 祖本逐字`）：**升 `逐字` 必须带它**，否则机器拒绝升档 |
| `vision` | obj | ✅ | 视觉标签：`构图`/`主体`/`墨阶`/`留白`/`异常`（agent 必须 `read_image` 后填，见 §七） |
| `sha256` | str | ✅ | 文件指纹（机器算，用于「同一件」判定与索引一致性核对） |
| `size` | int | ✅ | 字节数（机器算） |
| `dims` | list/null | ✅ | `[宽,高]`；无 Pillow 或视频 → `null` 并在 `dims_note` 注明 |
| `prompt_source` | obj | ✅ | `{file, anchor, line, match, confidence, borrow}`：出处文件名/章节/L 行/匹配方式/置信度 |
| `naming` | obj | ✅ | 命名校验结果：`{ok, prefix, id, name, version, error, suggest}` |
| `note` | str | ○ | 扩展备注（用户裁定/调色待办/展开件说明等）；schema 外扩展键，受「merge 不清空未知键」保证 |
| `vision_note` | str | ○ | **视频类备注（扩展键，agent 写）**：成片/视频件的动效·运镜·音画关系·时长口径等文字备注，与 `vision` 五键（图片视觉标签）并列；图片件也可用作补充说明。由 agent 直接写进 sidecar，`asset_index.py` 刷新时原样保留（见下方「未知键保证」） |

> `○` ＝按需；其余字段由 `asset_index.py` 生成、`ingest_asset.py` 写入；**agent/人工手写的 `vision` 与已填 `prompt` 不会被空值覆盖**（`merge_record` 只做「非空覆盖」）。

> **未知键保证（merge 不清空未知键）**：`merge_record(new, old)` 会把旧 sidecar 里**schema 之外的
> 自定义键原样沿用**——索引刷新重写 sidecar 时，agent/人工自行追加的扩展键（如视频类备注 `vision_note`、
> 项目自定义字段）**不会被丢弃、也不会被空值清空**；新值非空才覆盖。唯一例外是内部哨兵键（`_` 开头，
> 如解析失败的 `_parse_error`）不落盘。因此**给 sidecar 加字段是安全的**：加完不必改脚本，
> `asset_index.py` 重跑后仍在（机器判定：`assets_index.json` 的逐件记录同样带出该键）。

---

## 四、trace_status 分档（唯一判定口径）

| 档 | 含义 | 门控处置 |
|---|---|---|
| **逐字** | 采纳版 prompt 全文可从落盘文件**逐字复制**（含风格 token＋正文＋负面整串） | PASS |
| **重构** | 采纳版原文未落盘，但有结构要点可**复原候选全文**（`⚠️重构（非逐字原文）`） | **WARN**：出图前须制片人/导演过目 |
| **缺口** | 采纳版全文**不可复现**（无要点可复原，或来源明确标注缺口） | **FAIL**：必须回贴原文或授权以落盘基线重定稿 |
| **N/A（不适用）** | **废片/归档件不判溯源档**（`scrapped=true`） | 不计入逐字/重构统计；判废原因在 `rejects`、采纳版在 `note`；**不得当在用品** |

- **分档语义（裁定制片人 20260921）**：`trace_status` **只对「在用品」判定**——**废片一律 `N/A`**
  （`scrapped: true` ＋ `rejects` 记原因 ＋ `note` 记采纳版），归档件排除不计件（见 §二）。
  据此本项目在用品中 `重构` 仅 `C3c-僧人-托玉手部.jpg`（机械展开件，见 §四之二末）。
- 机器判据：来源章节里出现 `⛔…缺口` / `不可复现` / `无要点可复原` → 缺口；出现 `重构`/`复原`/`候选全文`/`非逐字` → 重构；否则按逐字；`scrapped=true` → `N/A`（机器硬判）。
- **缺口件不得沉默通过**：门控把它们逐件列出并计入 FAIL；索引侧同时写进 `asset_gaps.md`（待补清单）。
- 派生件（图生图/同机位派生）的 prompt 一样要按这三档登记——**底图不可重出＝派生链全部悬空**。

### 四之二、红线：禁伪造逐字（机器不得改 trace_status）

> 起因（红楼梦 EP01 实测）：`ingest_asset.py` 就地登记会顺带跑一次全量索引刷新，而旧版刷新**回写全部 sidecar**，
> 把 `trace_status` 换成索引重推值（4 件 `重构`→`逐字` 的静默升档、2 件 `逐字`→`重构` 的静默降档），
> `rejects` 也被索引抽取文本换掉。**这是「素材在库、出处不可信」的根源，不是小事。**

机器合并规则（`asset_index.merge_trace`，机器判定口径唯一）：

| 情形 | 处置 |
|---|---|
| sidecar 旧值为空（新件） | 用新值 |
| 人显式给（`trace_source=human`，如 `ingest_asset.py --trace-status`） | 以新值为准；**升 `逐字` 必须带 `verbatim_source`**，否则拒绝 |
| 旧值已是人写（`old.trace_source=human`） | **机器不得改**（既不能升也不能降） |
| 机器重推想升档（`重构`/`缺口`→`逐字`） | **一律拦截**（除非 sidecar 已带 `verbatim_source` 凭证） |
| 机器重推想降档（`逐字`→`重构`/`缺口`） | **不自动落盘**（机器不得静默把权威值改弱）；差异进 `--audit-sidecars` 交人确认 |
| 机器判 `N/A`（`scrapped=true`） | 允许（状态语义，不是溯源主张）：废片一律 `N/A` |
| 合并后仍无 prompt | 强制 `缺口`（唯一保留的机器硬判） |

- 升 `逐字` 的唯一合法路径：**人/回贴显式提供**（`--trace-status 逐字 --verbatim-source "<出处>"`，或在 sidecar 里写
  `trace_source:"human"` + `verbatim_source:"…"`），且 `prompt` 字段里确实是那段可整块复制的原文。
- **`rejects` 同理**：旧值非空时索引重推不覆盖；只有 `rejects_source=human`（`--reject`）才允许改写。
- **展开件**（由上游条目机械展开为自包含 prompt，如 `C3c-僧人-托玉手部.jpg`＝依 C3a＋D2＋C1c 展开）：
  **保持 `重构`**，`note` 写明展开依据，**不升 `逐字`**。

### 四之三、并发纪律（只刷索引不改事实源）

> **只刷索引一律 `asset_index.py --no-sidecar`**——它只重建 `assets_index.json/md`＋`asset_gaps.md`，**不改写任何 sidecar**。
> `ingest_asset.py` 就地登记**默认只写本件 sidecar ＋ 以 `--no-sidecar` 刷新索引**（要连全库一起回写须显式 `--write-sidecars`）。
> `trace_status`／`rejects` 具**「人写值粘滞」**：`trace_source: human` / `rejects_source: human` 的记录，机器此后**不得改**
> （禁伪造逐字、禁静默改弱）。**多会话并行时尤其重要**：任何「顺手重跑」都不得回写别人的 sidecar。
> **门控通道纪律（20260921 裁定 · 硬规则 #42）**：`prompt-delivery-config.json` 的 `channel` **留空（未声明）＝全套严格**
> （D1–D13 照跑）；只有**显式** `"channel": "A"` 才跳过剧集专属 D10/D12（`"C"` 只跳 D12）；**D13 禁亮词由 `light_terms`
> 是否为空决定，不看通道名**。剧集项目请显式声明 `"channel": "B"`，避免默认可读性歧义（漏跑＝闸没跑，不算通过）。

- 体检命令：`asset_index.py --root <素材根> --audit-sidecars` → 逐件列出「sidecar 现值 vs 索引重推值 vs 合并后写入值」，
  写 `sidecar_audit.md/.json`，**自身不改任何文件**。
- 只用索引、不动 sidecar 的三条命令（项目日常）：
  ```bash
  python scripts/asset_index.py --root runs/<项目>/refs --no-sidecar          # 只刷索引（安全档）
  python scripts/asset_index.py --root runs/<项目>/refs --audit-sidecars     # 只读体检
  python scripts/check_asset_labels.py runs/<项目> --naming-warn             # 门控
  ```

---

## 五、索引字段表（`assets_index.json` / `assets_index.md`）

`assets_index.json` 顶层：

| 字段 | 说明 |
|---|---|
| `generated_at` / `root` / `root_label` / `ep_tag` | 生成时间、素材根、EP 标记 |
| `prompt_sources` / `prompt_source_paths` | 本次匹配用的 prompt 来源文件 |
| `counts` | `{total, 逐字, 重构, 缺口, 不适用, 废片, 命名不合规, vision未填, 低置信匹配, 排除}` |
| `assets` | 逐件记录（＝每条 sidecar 的汇总，字段同 §三） |
| `excluded` | 被排除的归档/中间产物 `[{rel, reason}]` |

`assets_index.md`（人读，可直接给用户看）：总账表 → 逐件台账（按目录分组）→ 缺口清单 → 低置信匹配 → 废片留档 → 已排除。
`asset_gaps.md`（待补清单）：逐件写「现状 + 建议动作 + 补录口径」。

> **索引可随时重建**（`asset_index.py` 幂等）；**sidecar 是权威**——重建时以 sidecar 里非空的人工/agent 字段优先；
> **merge 不清空未知键**：sidecar 里 schema 外的扩展键（如视频类备注 `vision_note`）重建后原样保留（见 §三「未知键保证」）。

---

## 六、「入库即标签」三步动作（唯一入库姿势）

```bash
# ① 入库（一条命令：改名入目录 + 抽 prompt 全文 + 写 sidecar + 以 --no-sidecar 刷新索引，不碰别人的 sidecar）
python scripts/ingest_asset.py <新图.png> --root runs/<项目>/refs --kind 场景 --id 1 --name 青埂峰-阵末空缺 \
    --version v1 \
    --prompt-file runs/<项目>/m5-XX出图包.md --prompt-anchor "件 ③" \
    --refs "@图片1=S1-青埂峰石阵-第2抽.jpg" --upload-order "@图片1=S1-青埂峰石阵-第2抽.jpg" \
    --reuse "EP01:1-02; EP01:1-07" --tool "GPT Image 2"
# ①b 若要显式把某件定为「逐字」，必须同时给逐字来源凭证（否则拒绝入库）：
python scripts/ingest_asset.py <文件> ... --trace-status 逐字 --verbatim-source "m5-素材prompt回贴.md §3 L42 祖本"
# ② 看真图补视觉标签（agent 必做，见 §七）
python scripts/ingest_asset.py <同一个文件> ... --vision 构图=… --vision 主体=… --vision 墨阶=… --vision 留白=… --vision 异常=…
# ③ 门控
python scripts/check_asset_labels.py runs/<项目> --naming-warn   # FAIL>0 → exit 1；空跑 → exit 2
```

**若出处只能靠补录**（历史素材）：把采纳版全文按下面格式落进项目 md，再让索引器自动对上（`asset_index.py --prompt-source <md>`）：

```markdown
## 27 · S1-青埂峰-阵末空缺-v1.png          ← 标题里写文件名（或写「**保存文件名**：`xxx.png`」一行）
- **采纳版 prompt 全文**（**＝祖本** / **⚠️重构（非逐字原文）** / **⛔缺口——采纳版全文未落盘**）：
```
【风格】…＋【画面】…＋【留白】…
负面词：…
```
> 判废要点：…
```

匹配方式（自动，先强后弱，**宁可报缺口也不乱配**）：
① 块上下文里出现**完整文件名**（含扩展名，或仅扩展名不符）→ 高置信；
② 出现**素材 ID**（`C11`/`C1a`）且该块标题未指向同族另一件 → 高置信；
③ **分词命中 ≥2 个**（或 1 个 ≥4 字的特征词）且覆盖率 ≥50% → **低置信**，写进「低置信匹配（须人工确认）」。
一个代码块只能被一件素材占用；`同第 N 条` 的条目会自动借用第 N 条的 prompt（标 `重构`）。

---

## 七、给 agent 的视觉标签填写要求（硬规则）

1. **入库前必须 `read_image` 看真图**——没看图的入库＝猜标签，等于没标签。
2. 看完必须写 `vision` 五键，缺一不可（门控 `--require-vision` 会判 FAIL）：
   - `构图`：景别/构图法/主体落位/留白方位（如「甲级天地留白，主体左下黄金分割，右上 60% 留白」）
   - `主体`：画面是什么（人/物/场景＋数量＋姿态/状态），**只写看见的**
   - `墨阶`：焦/浓/重/淡/清 的分布与点睛色（朱砂·泥金·赭石/花青）及其面积占比
   - `留白`：留白级别（甲/乙/丙/特级）与合计占比
   - `异常`：与判废要点不符处、可疑元素（现代物件/文字/发光/蓝色调/格不等大…），无则写「无」
3. 与判废要点有出入 → 写进 `异常` 并同步 `rejects`，**不要悄悄放过**（红楼梦 EP01 的 `Y2 第1抽` 就是"与判废要点不符"却差一点被当采纳版用）。
4. 低置信匹配件（`match_confidence=low`）入库后必须人工/主管确认来源，确认后重写 `prompt` 与 `prompt_source`。
5. **视频/成片件（`media=video`）**：除 `vision` 五键外，可另写扩展键 `vision_note`（动效·运镜·音画关系·时长口径等等），
   与图片件的 `vision` 并列；`vision_note` 属 schema 外扩展键，受「merge 不清空未知键」保证（见 §三），
   agent 写完不会被 `asset_index.py` 刷新清掉。

---

## 八、与 check_all 的关系

- `scripts/check_all.py` 已接入本门控：**有素材根（`refs/`、`assets/` 或 `assets_index.json`）的项目自动跑 `check_asset_labels.py`，非素材类项目自动跳过**（跳过＝不跑也不假装 PASS）。
- 接入后的通过条件（与全量门控一致）：**缺口 0 件、未登记 0、断链 0、命名全合规**；
  `vision 未填` / `重构` / `低置信匹配` 只报 WARN（不阻断），但必须出现在索引报告里排期处理。
- 空跑（0 文件且 0 索引）→ **exit 2**，`check_all` 视为未通过：空跑不是通过。
- 与既有门控的分工：
  - `check_asset_pack.py`＝**交付期**看 prompt 里的 `@图N` 引用能不能在 inventory 里解析（引用级）；
  - `check_asset_labels.py`＝**入库期**看每件素材自己有没有出处（**件级**）。
  两者互补，不重复：前者防「引用悬空」，后者防「素材无源」。

---

## 九、配置 `asset_index.config.json`（可选，放素材根或上一级）

```json
{
  "index_dir": "",
  "include_globs": ["*.png", "*.jpg", "*.jpeg", "*.mp4"],
  "exclude_dirs": ["_废片", "_旧版归档", "_作废归档", "_frames"],
  "kind_dirs": {"角色": "锚图/角色", "道具": "锚图/道具", "场景": "锚图/场景", "字帖": "锚图/字帖", "故事板": "故事板", "成片": "成片"},
  "prefix_by_kind": {"角色": "C", "道具": "Y", "场景": "S", "字帖": "Z", "故事板": "B", "成片": "F"},
  "version_words": ["主版", "剪影版", "基础版", "备用"],
  "ep_tag": "EP01",
  "prompt_sources": ["m5-素材prompt补录.md", "m5-OP前置件出图包.md", "m5-Image2出图清单.md"],
  "tool_default": "GPT Image 2（Image2）",
  "type_default": "模型生成",
  "scrap_markers": []
}
```

- `kind_dirs` 支持「锚图/角色」这种两级目录（红楼梦 EP01 的库形态）；不带斜杠就是一层目录。
- `prompt_sources` 让重跑变成一条命令：`asset_index.py --root runs/<项目>/refs`（不必每次拼一长串 `--prompt-source`）。
- `version_words` 只放宽**版本段**用词，不放宽前缀/ID/名称规则。
- `scrap_markers` 追加项目自定义废片判据正则（默认判据：`❌/⛔/🗄…判废`、`废片留档`、`废/归档`）。
