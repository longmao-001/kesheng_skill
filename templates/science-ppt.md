# 科学讲解 PPT（可上图）

> **用途**：把 `science-report.md` 正文转成一份**能直接讲/给用户看**的 PPT。每页 `标题 + ≤3 条要点 + 配图（可选）+ 出处`。配图优先来自**素材库**（`assets-inventory.md` 条目），没有就用**文生图 prompt**（套 `image-gen-formulas.md`），禁用水印/竞品/未授权图。
> 产出：`runs/<slug>/scientist-讲解.pptx`（用 `scripts/build_science_report.py` 生成，或按此结构手工做）。

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
- 用 `python scripts/build_science_report.py --json <science-data.json>`（python-docx + python-pptx 可用时自动生成 docx + pptx；缺库装 `pip install python-docx python-pptx`）。
- **技能赋能（优先，别从零拼）**：`ppt-master`（generate-pptx / image-to-pptx 路由，含搜图上图）· `markdown-exporter`（MD→PPTX，把上面的 markdown 直接转）· `pipitmk`（Deck DSL→可编辑 PPTX）；配合 `report-writer`（docx + 质检）。
- `science-data.json` 结构：`{title, oneLiner, keyPoints[], timeline[], productPrinciple, sellingPoints[], science, data[{value,baseline,plain,cite}], pending[], depth}`。
