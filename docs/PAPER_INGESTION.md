# 论文拆解方案（Paper Ingestion Schema）

> 目的：把各专业的学术文献**有质量地**拆进科生知识图谱，而非只做"文献清单叶子节点"。
> 参考的知识图谱构建范式：**通用 KG 构建流水线**（本体 Schema → 命名实体识别 NER → 关系抽取 RE → 知识融合 → 质量评估）、**学术知识图谱**（Microsoft Academic Graph / Open Academic Graph / DBLP / AMiner 的"论文-作者-概念-引用"多层拆解）、**来源分层与置信度**（论文 > 行业手册 > 网络）。

## 1. 拆解模型（本体）

每批专业文献拆成 5 类节点 + 6 类关系（不允许只存 Paper 叶子）：

| 节点类型 | 含义 | 例子（广告专业） |
|---|---|---|
| `Paper` | 单篇文献（仅元数据：专业/年份/被引/DOI，**不写正文摘要**） | Central and Peripheral Routes…(ELM) |
| `Concept` | 该专业**核心概念/术语**（可复用、可被科生引用） | 精细加工可能性模型 ELM / 品牌态度 / 广告效果层级 |
| `Method` | 方法流派/研究范式 | 内容分析法 / 受众实验 / 眼动追踪 / 元分析 |
| `Finding` | **可操作实证发现**（一条结论=一个节点，能被科生规则引用为证据） | 高卷入产品走中心路径更有效 |
| `Theory` | 理论框架/经典学说 | 说服理论(ELM) / 使用与满足 / 叙事传输 / 作者论 / 装置理论 |

| 关系类型 | 方向 | 含义 |
|---|---|---|
| `paper-about` | Paper → Concept | 论文讨论某概念 |
| `paper-proposes` | Paper → Method | 论文提出/采用某方法 |
| `paper-finds` | Paper → Finding | 论文的实证发现 |
| `paper-uses` | Paper → Theory | 论文依据某理论 |
| `method-supports-rule` | Method → 科生规则 | 方法支撑科生某规则 |
| `finding-evidence-for-rule` | Finding → 科生规则 | 实证发现作为科生规则证据 |
| `concept-related-to` | Concept → Concept | 概念间关联 |

## 2. 拆解规则（质量纪律）

1. **论文元数据只登记，不杜撰正文**：Paper 节点只有 title/专业/年份/被引/DOI；拿不到摘要就不写摘要——宁缺勿造
2. **概念/方法/理论要"真在文献里"**：从 50 篇标题+该专业的通识理论中提取，每条 Concept/Method/Finding/Theory 的 `sources` 指向对应 Paper 的 DOI（来源可溯源）
3. **Finding 必须可操作**：写成"某条件下某效应"句式，能被科生规则直接当证据（如"短视频跳切频率↑ → 留存↑"）
4. **与科生规则接线**：Method/Finding 必须连到科生已有规则（`Rule:概念先行`、`Rule:图文对位`、`NarrationRule:语速档位`、`ProcessRule:剪辑合成（配音对齐·图表层·文案层·字幕·调色·片头片尾）`、`NarrationType:直白规格型`、`NarrationType:科普短视频`、`Rule:五层检查体系`、`Rule:AI原生交付原则`、`Rule:Prompt严格统一格式`、`ProcessRule:单镜抽卡` 等——跨片段引用这些 id）
5. **每专业规模**：Paper 50 + Concept 8-15 + Method 3-6 + Finding 6-12 + Theory 3-6；关系 ≥ 1.3×实体
6. **剔无关**：标题明显跑题（光电子材料/化学软件/纯医学）直接跳过不建 Paper，用质量换数量不足 50 也行
7. 片段文件：`packs/papers-<专业slug>-kg/kg.json`，`{"schema_version":"1.0","pack":"...","entities":[...],"relations":[...]}`；Paper 用 id `Paper:OA-<专业>-<i>`（与清单一致），Concept/Method/Finding/Theory 用 `Concept:<名>` 等

## 3. 来源分层（置信度）

- `DB_REFERENCE`：DOI 可验证的论文
- `LLM_INFERRED`：由标题+专业通识归纳的概念/发现（必须溯源到 Paper 的 sources）
- 写入 props 的 `置信度` 字段；不写无法溯源的"结论"
