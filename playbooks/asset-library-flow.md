# 自建素材库 → 参考图使用（Asset Library Flow）

> **功能**：把客户/网上的素材，**分析 → 拆解 → 重命名 → 保存建库 → 参考图使用**，一步到位。产物 = `assets-inventory.md`（你自建的素材库），选片直接用。
> **工具**：`scripts/extract_docs.py`（**PDF/PPTX/DOCX 批量抠图+抽文+台账骨架**）· `scripts/classify_assets.py`（分类+命名）· `scripts/annotate_assets.py`（智能入库脚手架）· `templates/assets-inventory.md`（库）· `templates/reference-selection.md`（选片）。
> **按文件类型的固定处理动作（视频/图片/矢量/PPT/PDF/Word/CAD/SolidWorks/SU/3D/字体/表格/音频）见 `docs/ASSET-TYPES.md`**——提取方式因类型而异，提取完统一汇入本流程后端。
> **流程图**：`docs/SOP-FLOW.md` 图二（素材处理流程）。

## 一步流程（五步闭环）

```
① 收集      素材目录（官方渲染/实拍/结构图/PDF-PPT抠图/网图/CAD-3D导出件/矢量）
      │        ★ 按类型处理：见 docs/ASSET-TYPES.md（各类型提取动作+红线不同）
      │        ⚙ PDF/PPTX/DOCX 一键抠图+抽文：python scripts/extract_docs.py <输入> --out runs/<slug>/ --subject <主体>
      │
② 分类+重命名  python scripts/classify_assets.py <目录> --subject <主体> [--apply]
     （按 用途分级×内容类型 命名：<用途>_<类型>_<主体>_<视角>_<序号>，文件名=条目ID）
      │
③ 智能入库     按 templates/assets-inventory.md 三件套：read_image 多模态拆解
     （物品/任务/场景/结构/质感/数据/品牌/实拍）+ 反推AI合成提示词 + 质量分★
     脚手架：python scripts/annotate_assets.py <目录> --subject <主体> --out assets-inventory-annotate.md
      │
④ 建库台账     assets-inventory.md（条目ID/用途分级/内容类型/主体/视角/内容标签/AI合成反推prompt/质量分/来源·授权）
      │
⑤ 参考图使用    按 内容标签/AI合成反推prompt 命中该镜对位需求 + 高分优先 → 挑≤3张 → 标角色+部位+位置 → @图进prompt
     → check_reference_selection.py 校验 → 图文对位检察官
```

## 关键点

- **按类型处理**：不同类型文件的"提取动作+红线"不同（视频抽帧+竖屏重构图+勿叠logo／矢量光栅化+保留矢量源+官方取色／PPT-PDF-Word 全量抠图+抽文标出处／**CAD·3D 须客户导出或外部渲染，不能直喂 AI**）——见 `docs/ASSET-TYPES.md`。
- **文件名=条目ID**：`<用途>_<类型>_<主体>_<视角>_<序号>`，引用一律用文件名，禁凭记忆翻文件夹。
- **拆解=文字检索键**：每张必须 read_image 拆解 + 反推AI合成提示词（你读文字，文字标签就是最快找图的方式）＋ 质量分（★≥4 优先，★<3 除非无替代）。
- **选片**：候选 = 从台账按 内容标签/反推prompt 命中需求；**高分优先**。
- **只用自建库**：参考图/首帧/图表层 prompt 一律从 `assets-inventory.md` 选，不凭空 AI 生成（零意外、自包含）。
- **合规**：禁用红线（水印/竞品/未授权）+ `ad_forbidden_words.py`（绝对化/疗效词）。
