# check_series_consistency.py —— 跨集一致性门控（KSP-E4 · D-S1–D-S8）

**用途**：剧集项目**每集交付前必跑 ＋ 季末总检必跑**的机器门控。判据＝`playbooks/series-production.md` **§6.1 跨集校验清单** ＋ **§6.2「剧集层判据 D-S1–D-S8」**。把"这一集和别的集是不是同一部片子"（人物锚/色板/字形/母题/音效/**时长结构**/钩子/专名/红线）变成可判、可阻断的检查。

**为什么必须独立于单集出口闸**：每集出口闸只看得到本集（跨集镜头隔着数周生产），**跨集漂移在单集视角下天然不可见**。本脚本与出口闸**并列不可互替**。

---

## 一、用法

```
python -X utf8 scripts/check_series_consistency.py <runs/<季slug>> [--season] [--ep EPnn] [--json]
```

| 参数 | 作用 |
|---|---|
| `<runs/<季slug>>` | 季项目目录（内含 `series-config.json`；集目录 `EPnn/` 或 `<季slug>-EPnn/`） |
| `--season` | 全季检查（**默认行为**；显式给出便于 `check_all.py` 直呼，与"逐集跑"对照） |
| `--ep EPnn` | 只查某一集（配置/登记类全季基准仍照常校验，保证基准可信） |
| `--json` | 机器可读输出（CI / `check_all.py`）：`{summary, episodes, counts, fail[], warn[], note[], …}` |

**退出码**（沿用 prompt 门控的"**空跑不算通过**"原则）：

| 码 | 含义 |
|---|---|
| `0` | PASS（或仅 WARN） |
| `1` | 存在 FAIL（**不得交付**） |
| `2` | **不可判定**：缺 `series-config.json` / 配置非法 / 配置 **0 集** / 全季 **0 个 prompt 文件** / `--ep` 不在配置内 |

> **0 文件、0 集、0 判定项一律 exit 2**——绝不静默通过。缺配置时脚本会打印**最小配置示例**。
> **门控与真实格式对齐（F-30）**：误报＝脚本过时，不是制品不过关——**修脚本，不迁就脚本**。

---

## 二、判据（逐条对应手册 §6.2 表）

| 项 | 判据（手册原文口径） | 不达标 | 本脚本怎么判 |
|---|---|---|---|
| **D-S1 时长结构** | 逐集 OP/ED 秒数**相等**（固定资产·浮动＝0），正片在容差内 | FAIL | 集内制品头部写 `**时长结构**：OP 90s / 正片 17分 / ED 90s` → 取**实测值**逐集比对；未写明则该集回退契约基准并出 WARN |
| **D-S2 锚复用** | 角色镜挂载的 `C*` 属本集允许集，且与首用集**同版本** | FAIL | 扫 prompt 正文里的锚 ID：越界（`allowed_episodes` 不含本集）＝FAIL；同 ID 跨集版本漂移（登记 `version` 或文件名 `-v2`）＝FAIL |
| **D-S3 字帖一致** | 同文本跨集**帖号一致**；字系分档一致 | FAIL | 配置表内"一文本两帖号／一帖号两文本"＝FAIL；集内引用越界／字系分体例冲突＝FAIL/WARN |
| **D-S4 母题唯一** | 母题 ID 全局唯一；**复现未声明即 FAIL** | FAIL | 登记表内 ID 重复＝FAIL；复现集未见 `【复现·回环】`（或登记 `recurrence`）＝FAIL；越界＝FAIL |
| **D-S5 钩子账本** | 每集有集尾钩，且**回收责任人有集号** | FAIL | 账本无本集条目／钩为空／责任人无 `EPnn`／兑现集超出全季集数＝FAIL；兑现集尚未产出＝WARN（产出时回填） |
| **D-S6 专名一致** | `naming_terms` 内的词跨集**逐字一致** | FAIL/WARN | 近似误写（同形近字，逐串取证、**禁叠字归并**）＝WARN；`red_line:true` 的专名在某集缺失＝FAIL |
| **D-S7 新增入册** | 本集出现的锚/帖/母题 ID **均已在圣经登记** | FAIL | 登记项缺「首用集」却被引用＝FAIL；被引用但未登记的 ID＝WARN（先入册后开抽） |
| **D-S8 红线继承** | 全季红线在**每集 prompt 负面**中在位 | FAIL | 逐集在【负面】字段里找 `red_lines[]`：缺失＝FAIL；本集无 prompt 文件或识别不到【负面】＝FAIL |

> **在位即在负面里**：红线写在正文不算在位（正文出现＝口径混用）。

---

## 三、为项目写 `<run>/series-config.json`

配置模板：`templates/series-config.json`（**直接复制改写**）。**项目专属词只进配置**（专名/锚ID/帖号/母题ID/红线），不写进脚本——同 `prompt-delivery-config.json` 的做法。核心字段：

| 字段 | 用途 | 对应判据 |
|---|---|---|
| `series_slug` / `episodes[]` / `season_episode_count` | 剧集标识与集目清单（门控据此遍历） | 遍历基准 / D-S5 |
| `op_seconds` / `ed_seconds` / `feature_min_seconds` / `feature_tolerance` | **时长结构契约**（§3.1 固定资产） | D-S1 |
| `anchor_registry` | 锚 ID ↔ 文件 ↔ **首用集** ↔ 允许集 ↔ 版本 ↔ 不可变属性 | D-S2 / D-S7 |
| `text_card_threads` | 帖号 ↔ 文本（逐字照录）↔ 允许集 ↔ 字系分档 | D-S3 |
| `motif_registry` | 母题 ID ↔ 首次出现集 ↔ 允许复现集/限次/复现声明 | D-S4 / D-S7 |
| `naming_terms` | 专名/称谓白名单（`red_line:true`＝跨集红线词） | D-S6 |
| `hook_ledger` | 每集集尾钩 ↔ 兑现责任人（哪一集哪一拍） | D-S5 |
| `red_lines[]` | 全季红线（**跨集继承，不得单集开口**） | D-S8 |
| `shared_assets_dir` / `shared_asset_subdirs` / `*_file` | 跨集共享资产与单一事实源文件（**_shared/ 真实文件唯一存放处**） | 目录纪律（§5/§9.2） |
| `exclude_dirs` | 扫描时跳过（`_shared`/`tools`/旧版归档——不排除会导致计数虚高） | 全域 |

**最小可用配置**（缺配置时脚本也会打印这份）：

```json
{
  "series_slug": "YYYYMMDD-<主题>S0N",
  "episodes": ["EP01", "EP02"],
  "op_seconds": 90, "ed_seconds": 90,
  "feature_min_seconds": 1020, "feature_tolerance": 0.10
}
```

> 字段缺省**≠放行**：缺 `anchor_registry`/`text_card_threads`/`motif_registry`/`naming_terms`/`red_lines` 时，该判据出 **NOTE（无基准可判）**，不静默通过——把这些表补进圣经/配置才是"过闸"。

**集目录形态**（二选一，手册 §9.1）：**A** `runs/<季slug>/EP01/`（推荐）；**B** `runs/<季slug>-EP01/`（一集一 run，须额外维护 `_shared`）。列型配置 `episodes` 也支持对象写法 `{"id":"EP01","dir":"EP01"}`。

---

## 四、与单集出口闸的关系（两层并列，互不替代）

```
# ① 单集层（既有通用门控，逐集跑；不得因"上一集绿了"豁免）
python -X utf8 scripts/check_prompt_delivery.py <runs/<slug>/EPnn> --animation-baseline   # D1–D13
python -X utf8 scripts/check_prompt_sheet.py      <runs/<slug>/EPnn>
python -X utf8 scripts/check_prompt_sop.py        <runs/<slug>/EPnn>
python -X utf8 scripts/check_delivery.py          <runs/<slug>/EPnn>                      # 版本收敛
python -X utf8 scripts/check_asset_pack.py        <runs/<slug>/EPnn>                      # 零意外自包含

# ② 剧集层（本脚本：只判"集与集之间"的同一性）
python -X utf8 scripts/check_series_consistency.py <runs/<slug>> --season
```

- **出口闸查"这一集好不好"；本门控查"这一集与别的集是不是同一部片子"**——两者都要过，缺一不可。
- **机器门控 ≠ 人工闸**：本脚本只保证"不犯已知错"，**不替代**手册 §6.3 的**跨集一致性检察官**（独立上下文、只看证据不听辩护）。闸序：**文学闸 → 红队前置闸 → 单集检察官（L1–L4.5）→ 跨集一致性检察官（KSP-E4，本脚本是其机器层）→ 用户签收**。
- **过闸记录**：`runs/<slug>/EPnn/ep-consistency-check.md`（判据｜实际｜比对基准｜结论）；季末另出《全季一致性裁决书》。

---

## 五、口径来源与纪律

- **判据来源**：`playbooks/series-production.md` §6.1/§6.2（来源＝红楼梦 EP01 暂停复盘·用户裁定 20260917）。
- **失败条目**：`knowledge/FAILURE-LIBRARY.md` **F-51–F-58**（剧集化复盘八条）。
- **硬规则**：`orchestration/ORCHESTRATION.md` **#35–#40**（全季规划先行／风格圣经先行／跨集资产复用／跨集一致性门控／集尾钩子与追更／剧集目录与版本规范）。
- **流程关卡**：`docs/USER_SOP.md` §2.5 **KSP-E1~E5**（E1 全季立项 → E2 风格圣经 → E3 逐集循环 → **E4 跨集一致性闸＝本脚本** → E5 发布节奏与追更）。
- **自查自测**：两集 TEMP fixture（OP 时长不一致＋钩子缺失＋红线缺失）已实测抓出 D-S1/D-S5/D-S8 三类 FAIL；0 集 / 0 prompt 文件 / 缺配置均 exit 2。
