# PPT / Deck 制作流程（PPT Deck Flow）—— 配合外部技能

> **用途**：科生的报告 PPT / 提案 deck / 讲解 deck，**不自己从零拼**，而是产出**规范化大纲 + 品牌资产**，交给成熟技能生成高保真成品。
> **两个主力技能（已安装，用 Skill 工具按名调用）**：
> | 技能 | 产出 | 什么时候用 |
> |---|---|---|
> | **`ppt-master`** | **原生可编辑 `.pptx`**（文字能在 PowerPoint 里直接改） | 要交客户/要能改稿/要套客户模板；走它的路由（见下） |
> | **`huashu-design`** | **高保真 HTML deck**（可导 PDF / 可编辑 PPTX） | 视觉冲击力优先；路演/发布会/汇报要"看着贵"；要设计探索 |
> | 兜底 | `scripts/build_science_report.py` 直出的 `.pptx` | 仅当无技能可用时的临时兜底——**不作为交付标准** |
>
> 一句话选型：**要"能改"选 ppt-master，要"好看"选 huashu-design，两者都可先出大纲。**

---

## 一、科生给什么（输入契约）

生成前先把这三样备齐（**缺一样不要开工**）：

| # | 输入 | 来源 | 说明 |
|---|---|---|---|
| 1 | **PPT 大纲** `scientist-讲解-大纲.md` | `scripts/build_science_report.py` 自动生成（或按 `templates/science-ppt.md` 页序手写） | 页序 + 每页要点 + 配图指向 + 出处 |
| 2 | **素材/配图** `assets-inventory.md` 条目 | 素材库（`docs/ASSET-TYPES.md` 流程建库） | 优先真实素材；禁水印/竞品/未授权 |
| 3 | **品牌资产** logo / VI 色值 / 用字 | KSP-02 拍板 #18（品牌名·用字·logo）+ #19（强调色/主色/画风） | **官方源**取（禁自造色）；huashu 要的 `brand-spec.md` 就由此而来 |

> 数据页**一律人工锁值**（AI 不生成数字）；CT 类（数据图表/原理示意）只作内容参考、**原图不出镜**，要重绘。

---

## 二、外部技能的纪律（调用时必须一起遵守，不得绕过）

调用外部技能 = **接受它的门控**。科生不得以"赶时间"替它开闸。

### `ppt-master` 的硬纪律
- **先路由**：读它的 `workflows/routing.md` 选**恰好一条**路由，不要自己拼流程。
  - Generate PPTX（普通）/ Quick / **Image to PPTX**（图→PPTX）/ **Beautify**（美化已有 PPTX）/ Create Template（建模板）/ Fill Native PPTX（填模板）/ Enhance Native PPTX（增强）
- **⛔ BLOCKING 门必须停**：到 `⛔ BLOCKING` 就停下等用户确认，不许替用户决定。
- **Image-first（新任务必做）**：进入方案规划前必须先用 `web_search` 搜 ≥2 组主题相关**真实图**；**禁止"无图也行"**——搜不到要明说"未找到合适的图"，不许留空白或编造。

### `huashu-design` 的硬纪律
- 🔴 **三方向硬门（100% 必走）**：任何会产出**新视觉设计**的任务，必须先给 **3 个差异化方向的真实初稿**（不是文字描述）让用户选；**指定了风格也不豁免**（"Apple 风格"是一个语境不是设计）。用户选完才执行。
  - 多页 deck 的三方向形态 = **每方向 2 页代表页**（兼作 showcase）。
- **Gate 文件**：`brand-spec.md`（品牌资产）、`direction-approved.md`（三方向展示 + **用户选择原话**）。项目目录里没有这些文件 = 该环节没做。
- **反 AI slop 禁区**：紫渐变 / emoji 当图标 / 圆角卡片+左彩色 border / SVG 画人脸代替真实产品图 / Inter-Roboto 当 display / "均匀深蓝底+通用霓虹 glow"。
- 幻灯片**默认架构 = 多文件 + 概览墙**（`assets/deck_index.html`），别默认单文件绕过概览墙。

---

## 三、与科生自身机制的衔接（关键）

外部技能的门 = 科生的拍板点，**用同一套机制执行**，不另起一套：

| 外部技能要的 | 科生怎么给 |
|---|---|
| huashu 的「三方向选择」 | **用 `ask_user_question` 拍板选项卡**（≥2 选项、推荐置顶、留"自定义"兜底）；用户选择**原话**记进 `direction-approved.md` |
| huashu 的 `brand-spec.md` | 由 KSP-02 拍板 **#18 品牌名·用字·logo** + **#19 强调色/主色/画风** 的结论直接转写（官方取色，禁自造） |
| ppt-master 的 `⛔ BLOCKING` | 同科生拍板点——**停下等用户**，不得代拍 |
| ppt-master 的 Image-first 搜图 | 与科生「素材库优先」一致：先查 `assets-inventory.md`，**库里有就用库里的**；库里没有才 web_search 补（注明来源，只作参考不入镜） |
| 两个技能的反 slop 禁区 | 与科生 `protocols/quality-gate.md`「视觉克制 / 反 AI 感」同一套禁区（霓虹/镀铬反光/大光球/激光束/白底紫渐变/海军金）——**把科生禁区直接喂给技能** |
| 证据先行 | 三方向初稿/成品**必须先贴给用户看**（截图/路径+描述）再给选项卡，禁盲选 |

> **顺序**：科生先出**大纲 + 资产**（内容正确）→ 技能出**视觉**（好看）→ 科生按 `quality-gate.md` **验收**（科学准确 + 禁区 + 图文对位）。

---

## 四、一步流程

```
① 内容就绪（科生）   scientist-讲解-大纲.md（页序/要点/配图/出处）
        │            + assets-inventory 条目 + 品牌资产(#18/#19)
        ▼
② 选技能（拍板）     要"能改"→ ppt-master ／ 要"好看"→ huashu-design
        │            （大型/重要场合可两者都出，让用户对比选）
        ▼
③ 技能按自己的门走   ppt-master: 路由 → ⛔BLOCKING 停等
        │            huashu-design: 🔴三方向初稿 → 停等用户选（记 direction-approved.md）
        ▼
④ 生成              ppt-master → .pptx（可编辑）
        │            huashu-design → HTML deck → 导 PDF / 可编辑 PPTX
        ▼
⑤ 科生验收           quality-gate.md 七维 + 视觉克制/反AI感 + 图文对位(R12)
        │            数据页人工锁值核验；配图授权核验
        ▼
⑥ 交付              .pptx / PDF 归档进 delivery/；品牌资产与出处留档
```

---

## 五、自检

- [ ] 大纲齐全（页序/要点/配图指向/出处），不是空壳
- [ ] 品牌资产来自**官方源**（logo/色值/用字），未自造色
- [ ] 技能是**按名调用**的成熟技能，不是自己写 HTML/PPTX 硬拼
- [ ] 外部技能的**门都走了**：ppt-master 的 ⛔BLOCKING 停等；huashu 的三方向 + `direction-approved.md` 落档
- [ ] 三方向/成品**证据先行**贴给用户看过再让其选
- [ ] 反 slop 禁区与科生 quality-gate 禁区**两套都过**
- [ ] 数据页**人工锁值**（AI 未生成数字）；CT 类原图未出镜
- [ ] 配图**授权核验**（无水印/竞品/未授权）
- [ ] 成品归档 `delivery/`，出处留档

---

## 六、关联文件

- 大纲模板：`templates/science-ppt.md`（页序建议 10-13 页）
- 内容源：`templates/science-report.md` · `scripts/build_science_report.py`
- 报告转档（Word 适配）：`scripts/md_to_docx.py`
- 素材/配图：`docs/ASSET-TYPES.md` · `playbooks/asset-library-flow.md` · `templates/assets-inventory.md`
- 验收标准：`protocols/quality-gate.md`（七维 + 视觉克制/反 AI 感）
- 品牌资产拍板：`templates/user-gate.md` #18 / #19
- M2→M3 交接：`playbooks/science-report-flow.md`
