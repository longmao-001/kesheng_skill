#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科生 SOP 流程图 · 出图脚本 (render_sop_flow.py)

用 matplotlib 把 docs/SOP-FLOW.md 的流程画成**图片**（PNG 位图 + PDF 矢量）。
不依赖 graphviz / mermaid-cli / 浏览器。

用法: python -X utf8 scripts/render_sop_flow.py [--out docs/SOP-FLOW]
产出: <out>-KSP主流程.png/.pdf · <out>-素材处理.png/.pdf · <out>-PPT流程.png/.pdf

设计：单栅格坐标（0-100 x，y 向下）；主列居中偏左、注释/拍板列靠右互不重叠；
      盒高按文本行数自动计算；y 轴范围按最终布局动态收缩（不留大片空白）。
"""
import argparse
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                    # noqa: E402
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch  # noqa: E402

matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "SimSun", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

C = {
    "start": ("#E8F0FE", "#1A73E8"),
    "ksp":   ("#FFFFFF", "#1F3864"),
    "know":  ("#FFF4E5", "#E8710A"),
    "halt":  ("#FDECEA", "#C5221F"),
    "idea":  ("#F3E8FD", "#7B1FA2"),
    "exec":  ("#E6F4EA", "#137333"),
    "gate":  ("#FFF8E1", "#B7791F"),
    "insp":  ("#E8EAED", "#3C4043"),
    "close": ("#E0F2F1", "#00695C"),
    "fix":   ("#FCE8E6", "#B3261E"),
    "note":  ("#F1F3F4", "#5F6368"),
    "plate": ("#EDE7F6", "#4527A0"),
}
LINE_H = 2.62          # 每行文本占用的 y 单位
PAD = 2.3              # 盒内上下留白
GAP = 4.6              # 盒间距


class Flow:
    """顺序排版器：自动算高、画盒、连箭头、记录节点。"""

    def __init__(self, ax, xm, w, y0):
        self.ax, self.xm, self.w, self.y = ax, xm, w, y0
        self.nodes = []          # [(cy, h)]

    def h(self, text, minh=5.5):
        n = text.count("\n") + 1
        return max(minh, PAD * 2 + n * LINE_H)

    def _border(self, text, kind, h, cy, fs, bold, radius, lw, ls):
        fc, ec = C[kind]
        self.ax.add_patch(FancyBboxPatch((self.xm - self.w / 2, cy - h / 2), self.w, h,
                                        boxstyle=f"round,pad=0.3,rounding_size={radius}",
                                        linewidth=lw, edgecolor=ec, facecolor=fc,
                                        linestyle=ls, zorder=2))
        self.ax.text(self.xm, cy, text, ha="center", va="center", fontsize=fs,
                     color="#202124", fontweight="bold" if bold else "normal",
                     zorder=3, linespacing=1.52)

    def box(self, text, kind="ksp", fs=8.9, minh=5.5, bold=False, ls="-", lw=1.6):
        h = self.h(text, minh)
        cy = self.y + h / 2
        self._border(text, kind, h, cy, fs, bold, 1.1, lw, ls)
        self.nodes.append((cy, h))
        self.y += h + GAP
        return cy, h

    def gate(self, text, fs=8.7, pad=3.4):
        h = self.h(text) + pad
        cy = self.y + h / 2
        w = self.w * 0.80
        pts = [(self.xm, cy - h / 2), (self.xm + w / 2, cy), (self.xm, cy + h / 2), (self.xm - w / 2, cy)]
        fc, ec = C["gate"]
        self.ax.add_patch(Polygon(pts, closed=True, lw=1.8, edgecolor=ec, facecolor=fc, zorder=2))
        self.ax.text(self.xm, cy, text, ha="center", va="center", fontsize=fs,
                     color="#202124", fontweight="bold", zorder=3, linespacing=1.45)
        self.nodes.append((cy, h))
        self.y += h + GAP
        return cy, h, w

    def arrows(self, skip=()):
        """相邻节点之间画竖直箭头。skip=跳过的节点序号。"""
        for i in range(len(self.nodes) - 1):
            if i in skip:
                continue
            (cy1, h1), (cy2, h2) = self.nodes[i], self.nodes[i + 1]
            self.ax.add_patch(FancyArrowPatch(
                (self.xm, cy1 + h1 / 2), (self.xm, cy2 - h2 / 2), arrowstyle="-|>",
                mutation_scale=15, linewidth=1.7, color="#5F6368", zorder=1,
                shrinkA=0, shrinkB=0))

    def label_on_arrow(self, i, text, color="#137333"):
        """在第 i 与 i+1 个节点之间的竖直箭头上加旁注（如 PASS/CONDITIONAL）。"""
        (cy1, h1), (cy2, h2) = self.nodes[i], self.nodes[i + 1]
        mid = (cy1 + h1 / 2 + cy2 - h2 / 2) / 2
        self.ax.text(self.xm + 1.8, mid, text, ha="left", va="center",
                     fontsize=8.0, color=color, zorder=4)


def new_canvas(w, h):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 100)
    ax.set_ylim(h * 6.5, 0)
    ax.axis("off")
    return fig, ax


def title(ax, main, sub):
    ax.text(50, 5.5, main, ha="center", va="center", fontsize=19.5,
            fontweight="bold", color="#1F3864")
    ax.text(50, 10.8, sub, ha="center", va="center", fontsize=9.8, color="#5F6368", linespacing=1.6)


def plate(ax, cy, text, x=82.0, w=32.0, spine_right=63.0):
    fc, ec = C["plate"]
    h = max(6.0, PAD * 1.6 + (text.count("\n") + 1) * LINE_H)
    ax.add_patch(FancyBboxPatch((x - w / 2, cy - h / 2), w, h,
                                boxstyle="round,pad=0.3,rounding_size=1.0",
                                linewidth=1.2, edgecolor=ec, facecolor=fc, zorder=2))
    ax.text(x, cy, "▲ " + text, ha="center", va="center", fontsize=8.3,
            color="#311B92", zorder=3, linespacing=1.5)
    ax.plot([spine_right, x - w / 2], [cy, cy], color=ec, lw=1.0, ls=(0, (3, 2)), zorder=1)
    return h


def note(ax, cy, text, x=82.0, w=32.0, fs=8.3, spine_right=63.0, link=True):
    fc, ec = C["note"]
    h = max(6.0, PAD * 1.6 + (text.count("\n") + 1) * LINE_H)
    ax.add_patch(FancyBboxPatch((x - w / 2, cy - h / 2), w, h,
                                boxstyle="round,pad=0.3,rounding_size=0.9",
                                linewidth=1.0, edgecolor=ec, facecolor=fc,
                                linestyle="--", zorder=2))
    ax.text(x, cy, text, ha="center", va="center", fontsize=fs, color="#3C4043",
            zorder=3, linespacing=1.55)
    if link:
        ax.plot([spine_right, x - w / 2], [cy, cy], color="#9AA0A6", lw=0.9,
                ls=(0, (2, 3)), zorder=1)
    return h


def branch(ax, cy, x_from, label, kind="fix", w=18.0, x_left=65.0):
    """右侧打回支路盒（起始 x 从闸门右顶点，盒体不压主列）。"""
    fc, ec = C[kind]
    x = x_left + w / 2
    h = 7.0
    ax.add_patch(FancyArrowPatch((x_from, cy), (x_left, cy), arrowstyle="-|>",
                                 mutation_scale=14, lw=1.7, color=ec, zorder=1))
    ax.add_patch(FancyBboxPatch((x - w / 2, cy - h / 2), w, h,
                                boxstyle="round,pad=0.3,rounding_size=0.9",
                                linewidth=1.5, edgecolor=ec, facecolor=fc, zorder=2))
    ax.text(x, cy, label, ha="center", va="center", fontsize=8.1, color=ec,
            zorder=3, linespacing=1.45)
    return h


def legend_bar(ax, y, names, max_x=94.0):
    """横排图例（超出画布自动换行）。"""
    x, yy = 4.0, y
    ax.text(x, yy, "图例", fontsize=8.8, fontweight="bold", color="#3C4043", va="center")
    x += 5.0
    for name, k in names:
        w = 12.0 + len(name) * 2.1
        if x + w > max_x:
            x, yy = 4.0, yy + 4.2
        fc, ec = C[k]
        ax.add_patch(FancyBboxPatch((x, yy - 1.4), 5.4, 2.8,
                                    boxstyle="round,pad=0.1,rounding_size=0.5",
                                    linewidth=1.2, edgecolor=ec, facecolor=fc, zorder=2))
        ax.text(x + 6.4, yy, name, fontsize=7.8, va="center", color="#3C4043")
        x += w + 1.6
    return yy


def finish(fig, ax, out, bottom):
    """bottom = 内容底部 y（含图例）。据此收缩 y 轴，不留空白也不越界。"""
    ax.set_ylim(bottom + 4.0, 0)
    fig.savefig(out + ".png", dpi=132, bbox_inches="tight", facecolor="white", pad_inches=0.4)
    fig.savefig(out + ".pdf", bbox_inches="tight", facecolor="white", pad_inches=0.4)
    plt.close(fig)


# ==================== 图一：KSP 主流程 ====================
def fig_ksp(base):
    fig, ax = new_canvas(17.0, 30.0)
    title(ax, "科生 SOP 流程图（一）· KSP 主流程  KSP-01 ~ KSP-07 + KSP-C",
          "四条铁则：① 用户是甲方（每关拍板）　② 拍板必用选项卡　③ 证据先行　④ 知识只进图谱\n"
          "依据 docs/USER_SOP.md（流程权威）+ docs/SOP-FLOW.md（本图配套）+ orchestration/ORCHESTRATION.md")

    xm, W = 32.0, 58.0
    SPINE_R = xm + W / 2
    f = Flow(ax, xm, W, 20.0)

    cy, _ = f.box("【0 启动】制片人先读全「核心流程全集」5 份 + 失败图书馆\n"
                  "docs/USER_SOP.md · orchestration/ORCHESTRATION.md · protocols/quality-gate.md ·\n"
                  "playbooks/production-workflow.md · templates/user-gate.md ＋ knowledge/FAILURE-LIBRARY.md\n"
                  "■ 读全前禁止派活 / 建文件；产物只落 runs/<项目slug>/", "start", 8.7)

    steps = [
        ("KSP-01 立项定档 ─ 制片人",
         "一句话理解 → 三问（做什么片 / 给谁看 / 多久要）→ slug ＋ STATE.md\n"
         "定档：S 档单干 ／ M 档并行+双闸（默认）／ L 档全会+全自动", "ksp",
         "拍板 #1 定档 S/M/L\n＋ #18 品牌名·用字·logo"),
        ("KSP-02 需求简报 ＋ 预注册 ─── 制片人 ＋ 并行 4 约束（科学/导演/摄影/受众）",
         "brief.md ＝ 简报 ＋ 预注册标准 3-5 条 ＋ 素材清单/缺口\n"
         "铁则：信息缺口必须问清，不许猜", "ksp",
         "拍板 #2-7 受众/平台/时长/风格/画风/素材\n＋ #19 强调色·主色·画风"),
        ("KSP-03 科学理解（知识关 · 先读后谈）─── 科学顾问 ＋ 观众代言人 ＋ 导演（并行）",
         "· 7 步深度理解法 → 理解深度 ≥L2（L1 只够新闻稿，禁止创作）\n"
         "· 调研图料三件套：① 科学道理 ② 网图（→refs/，标来源，不入镜）③ 素材图（→建库）\n"
         "· 素材智能入库（M2 同步 · 必做）：每张三件套 ＝ read_image 多模态拆解\n"
         "　 ＋ 反推 AI 合成提示词（文字检索键）＋ 质量分 ★（合规一票否决）　← 见图二\n"
         "· 两点讲明白：产品=介绍+卖点 ／ 机构=研究什么+人员 ／ 设施=能力+意义 ／ 科普=先讲人\n"
         "产物：scientist-理解报告.md（唯一事实源）＋ scientist-报告.docx（Word 适配）＋ PPT 大纲",
         "know", None),
        ("■ 硬性停顿：报告 ＝ 中间交付件",
         "① 完整报告全文写进对话（不得压缩成 3 行总结）\n"
         "② docx ＋ PPT 作为文件交用户（可打开 / 可上图 / 可直接用）\n"
         "③ 用户读完 → 明确回复「继续」（讨论 / 纠偏记 m2-纪要.md）\n"
         "④ 未收到「继续」→ 禁止推进任何后续环节 ／ 禁止抛拍板选项", "halt", None),
        ("KSP-03.5 主题共识 ＋ 内容重点对齐",
         "① 主体共识卡（一句话讲清这条片子讲什么 / 为谁讲）\n"
         "② 3-8 条候选重点（信息点 ＋ 支持证据 ＋ 对应镜头可能）\n"
         "③ 讨论 → 「内容重点协议」（重点 × 权重 P0/P1/弱化/删除 × 镜头预算）", "idea",
         "拍板 #17 内容重点圈选（多选）"),
        ("KSP-04 创意概念先行 ─── 导演 / 编剧 / 摄影 / 观众代言人",
         "Insight（已在 03.5）→ Ideation（各出 5 个创意概念 · 非完整方案）\n"
         "→ Evaluation（四维打分：预注册 / 传播力 / 科学准确 / 可执行 ＋ 红队挑战）\n"
         "→ Presentation（概念卡并列 · 证据先行）→ Refine（只深化所选）\n"
         "　　深化 ＝ 完整方案：定位 / 受众 / 口播稿定稿 / 分镜概览 / 执行计划", "idea",
         "拍板 #9 概念：选一 / 融合 / 自定义"),
        ("KSP-05 口播稿（先定内容）─── 编剧",
         "2-3 个方案竞稿（① 直白规格型 ② 价值翻译型 ③ 混合型）＋ 读法批注\n"
         "逐句对号 templates/narration-formula.md（14 个句子公式 F01-F14）", "idea",
         "拍板 #16 口播方案：选一 / 混搭\n＋ #13 术语发音疑难 → 注音"),
        ("KSP-04.5 九宫格风格预览（口播之后）─── 分镜师 ＋ 美术指导",
         "九宫格出图 → 美术批复 → 风格基线固化（风格 token / 色板 / 画风 / 构图倾向）", "idea",
         "拍板 #15 风格预览：按此基线 / 换方向 / 微调"),
    ]

    for name, detail, kind, pl in steps:
        ls = (0, (5, 2)) if kind == "halt" else "-"
        lw = 2.4 if kind == "halt" else 1.6
        cy, h = f.box(f"{name}\n{detail}", kind, 8.7, ls=ls, lw=lw)
        if pl:
            plate(ax, cy, pl, x=82.0, w=32.0, spine_right=SPINE_R)
        if kind == "halt":
            note(ax, cy, "★ 顺序铁则\n报告读完「继续」→ 才可谈\n主题共识 / 方案 / 风格 / 口播",
                 x=82.0, w=32.0, spine_right=SPINE_R)

    cy, _ = f.box("★ 顺序铁则：口播稿 → 九宫格出图 → 才做分镜（不可乱）", "note", 9.4, bold=True)

    cy, _ = f.box("KSP-06 执行关（并行 → 串行交接）\n"
                  "分镜表（分镜师）‖ 声音方案（声音设计师）\n"
                  "　　↓\n"
                  "摄影方案（摄影指导：每镜运镜 ≤2 ＋ 变速 / 光影 / 拍法路线 / 参考资产）\n"
                  "　　↓\n"
                  "prompt 分段并行转写（prompt 工程师 ×N · 每段 5-8 镜）‖ 剪辑预计划（剪辑师）\n"
                  "　　↓\n"
                  "美术 VI 复核 → 科学复核（L3 事实检察官）\n"
                  "产物：storyboard-分镜表.md ／ m4-prompts/prompts-<平台>.md ／ sound ／ dop ／ editor",
                  "exec", 8.7)

    cy, _ = f.box("机器门控：python -X utf8 scripts/check_all.py runs/<slug>　（8 项）\n"
                  "① check_sop　　　　　 产物齐 ＋ 每镜 prompt 字段完整（缺 ＝ 跳 SOP → 回退）\n"
                  "② check_prompt_sheet　 prompt 格式与一致性（核心字段 / 口播≠口播稿 / 风格 / 参考 / 负面）\n"
                  "③ check_prompt_sop　　 写 prompt 十步 SOP 执行证据（参考图裸引用 / 风格不同源 / 口播不同源）\n"
                  "④ check_asset_pack　　 素材自包含（引用可解析、无「待补充 / 拍照」）\n"
                  "⑤ check_delivery　　　 交付件版本收敛（单一源 / 包自包含 / 无漂移）\n"
                  "⑥ ad_forbidden_words　 广告禁用词（绝对化 / 极限 / 疗效 / 平台禁语）\n"
                  "⑦ check_runs_clean　　 runs/ 只放项目\n"
                  "⑧ check_docs_integrity 技能级：SOP 无断链 / 无孤岛", "gate", 8.5)

    _, _, gw = f.gate("红队前置闸 m4-gate-red\n（独立上下文 · 未参与创作）")
    idx_g1 = len(f.nodes) - 1
    cy_g1 = f.nodes[idx_g1][0]
    branch(ax, cy_g1, xm + gw / 2, "BLOCK\n打回对应环节\n≤2 循环")

    _, _, gw2 = f.gate("出口评审闸 L4\n七维评分 ＋ 三态")
    idx_g2 = len(f.nodes) - 1
    cy_g2 = f.nodes[idx_g2][0]
    branch(ax, cy_g2, xm + gw2 / 2, "BLOCK / CONDITIONAL\n打回 ≤2 循环")

    cy, _ = f.box("检察官五层（每层独立上下文 · 只看证据 · 不听辩护 · 不代修）\n"
                  "L1 素材 → L2 prompt → L3 事实 → L4 出口 → L4.5 总检　→　L5 用户签收",
                  "insp", 9.2)

    cy, _ = f.box("交付（AI 原生两档）\n"
                  "A 档 · 多平台上手包（默认）：每镜【平台对照 prompt ＋ 参考图包 ＋ 口播 ＋ 抽卡建议 ＋ 画布步骤】\n"
                  "　　　配音 ＝ AI 原生（TTS / 剪映，口播带读法批注）\n"
                  "B 档 · 专业增强（可选，用户主动要求时）\n"
                  "零意外铁则：交付后用户绝不需要再拍照 / 找物 / 补素材（否则 ＝ 流程事故）", "insp", 8.7)

    cy, _ = f.box("KSP-07 知识萃取归档（闭环）\n"
                  "· 通用知识 → 域片段 → build_union_kg.py 重建图谱\n"
                  "· 失败教训 → knowledge/FAILURE-LIBRARY.md 追加（现象 / 根因 / 已固化 / 证据）\n"
                  "· 交付包归档 delivery/（视频 · 分镜 · prompts · README · 授权）\n"
                  "· 隐私：kb/隐私红线.md 三分法，项目专有信息零入库", "close", 8.7)

    cy, _ = f.box("交付闭环　──→　下次开工前先读 FAILURE-LIBRARY（防重复踩坑）", "close", 9.8, bold=True)

    cy, _ = f.box("横切 KSP-C 变更控制（随时）：变更记录 → 影响评估 → 用户拍板 → 回退最早受影响关卡\n"
                  "降级：S 档单干（明示「降级模式」）／ subagent 失败 → 重派 1 次 → 仍失败制片人接手（注明降级）",
                  "note", 8.7)

    f.arrows()
    f.label_on_arrow(idx_g1, "PASS / CONDITIONAL")
    f.label_on_arrow(idx_g2, "PASS")
    ly = legend_bar(ax, f.y + 7.0, [("启动", "start"), ("KSP 阶段", "ksp"), ("知识关", "know"),
                               ("硬性停顿", "halt"), ("创意关", "idea"), ("执行关", "exec"),
                               ("门控/闸", "gate"), ("检察官/交付", "insp"), ("归档", "close"),
                               ("打回", "fix")])
    finish(fig, ax, base + "-KSP主流程", ly)


# ==================== 图二：素材处理 ====================
def fig_asset(base):
    fig, ax = new_canvas(17.0, 21.0)
    title(ax, "科生 SOP 流程图（二）· 素材处理流程",
          "文件到手 → 参考图进 prompt　·　依据 docs/ASSET-TYPES.md（13 类文件）+ playbooks/asset-library-flow.md + templates/reference-selection.md\n"
          "★ 核心：类型差异只在「提取」一步；分类 / 命名 / 入库 / 选片 全类型统一")
    xm, W = 32.0, 58.0
    SPINE_R = xm + W / 2
    f = Flow(ax, xm, W, 20.0)

    f.box("文件到手：视频 / 图片 / 矢量 / PPT / PDF / Word / CAD / SolidWorks / SketchUp / 3D / 字体 / 表格 / 音频",
          "start", 9.0)

    f.box("① 决策树（先问「拿来干什么」）\n"
          "· 能直接入镜？　　　　　　　　　　　→ IN 直接入镜（信任主体，须真素材 ＋ 授权）\n"
          "· 给模型做锚（外观/结构/场景/质感）？→ RF 参考图\n"
          "· 只作内容依据（数据/原理/图表）？　→ CT 内容参考（原图永不出镜）\n"
          "· 只作事实 / 口径依据？　　　　　　→ 抽取稿 / 报告（带出处）\n"
          "★ 同一文件可同时多角色 → 拆开分头归类", "ksp", 8.9)

    f.box("② 按类型提取（docs/ASSET-TYPES.md 类型矩阵）\n"
          "视频　　　：读中帧 → 抽帧建 RF_SCENE → 记画幅 / 帧率\n"
          "图片　　　：read_image 看真图（不凭文件名判断）\n"
          "矢量　　　：光栅化 300dpi+ ＋ 保留矢量源 ＋ 官方取 HEX 色值（禁自造）\n"
          "PPT　　　 ：python-pptx 抠图 ＋ 抽文（含表格 / 演讲备注）\n"
          "PDF　　　 ：PyMuPDF get_images ＋ get_text（标页码出处）\n"
          "Word　　 ：python-docx 全文 ＋ inline_shapes\n"
          "CAD　　　：须导出 PDF/SVG → 光栅化（不能直喂 AI）\n"
          "SolidWorks：导三视图/等轴测 或 PhotoView 渲染（须 SW 环境 · 多在客户侧）\n"
          "SketchUp ：导场景图/等轴测（只作空间比例，不作外观锚）\n"
          "3D 中性　 ：Blender/KeyShot 渲染三视图　｜　字体/表格/音频：查授权 / 提指标 / 听辨\n"
          "⚙ 自动化：scripts/extract_docs.py（PDF/PPTX/DOCX 批量抠图 ＋ 抽文 ＋ 台账骨架）\n"
          "⚠ CAD/3D 无解析库 → 向客户要导出件，作素材缺口走拍板 #7", "exec", 8.7)

    f.box("③ 统一入库（全类型同一套）\n"
          "两轴分类：IN/RF/CT × MAIN/PART/SCENE/TEXT/STR/DATA/BRAND/RAW\n"
          "命名：<用途>_<类型>_<主体>_<视角>_<序号>　（文件名 ＝ 条目ID）\n"
          "三件套：read_image 多模态拆解（物品/任务/场景/结构/质感/数据/品牌/实拍）\n"
          "　　　　＋ 反推 AI 合成提示词（文字检索键）＋ 质量分 ★1-5\n"
          "⚙ scripts/classify_assets.py ／ scripts/annotate_assets.py", "ksp", 8.9)

    f.box("④ 建库台账 assets-inventory.md\n"
          "条目ID / 用途 / 类型 / 主体 / 视角 / 内容标签 / 反推 prompt / ★ / 来源·授权", "ksp", 8.9)

    f.box("⑤ 参考图使用（选片 · 8 维打分）\n"
          "先定「对位需求」→ 候选池（按内容标签 / 反推 prompt 文字匹配 ＋ 高分优先）\n"
          "→ 8 维打分（对位度 / 信息完整 / 角度 / 光影 / 占位 / 合规 / 唯一性 / 可溯源）\n"
          "→ 入选 ≤3 张 → 标「角色 ＋ 部位对应 ＋ 位置 ＋ 依据口播哪句」\n"
          "→ @图N 进 prompt【参考】字段", "exec", 8.9)

    cy, _ = f.box("⑥ 门控\n"
                  "check_reference_selection.py（选片要素完整）\n"
                  "check_asset_pack.py（引用可解析 / 无后补提示词 ＝ 自包含）\n"
                  "ad_forbidden_words.py（合规禁词）\n"
                  "→ L1 素材检察官 ＋ L2 prompt 检察官（图文对位硬查）", "gate", 8.9)

    note(ax, cy, "★ 三条硬红线\n"
         "① 合规一票否决（水印/竞品/团队照/未授权 → 不入库）\n"
         "② 数据图表只作 CT，永不出镜；\n　　数据一律人工锁值（AI 不生成数字）\n"
         "③ 产品/设备类：绝不改造真实造型\n　　＝「保持真实造型 ＝ @参考图不变」",
         x=82.0, w=32.0, spine_right=SPINE_R, fs=8.0)

    f.arrows()
    ly = legend_bar(ax, f.y + 7.0, [("启动/入口", "start"), ("决策/分类", "ksp"),
                               ("提取/入库/选片", "exec"), ("门控", "gate"), ("旁注", "note")])
    finish(fig, ax, base + "-素材处理", ly)


# ==================== 图三：PPT / Deck ====================
def fig_ppt(base):
    fig, ax = new_canvas(17.0, 15.0)
    title(ax, "科生 SOP 流程图（三）· PPT / Deck 制作流程",
          "配合外部技能（ppt-master / huashu-design）　·　依据 playbooks/ppt-deck-flow.md\n"
          "科生不自己拼 PPT：出「大纲 ＋ 资产」→ 交成熟技能出视觉 → 科生按质量门验收")
    xm, W = 32.0, 58.0
    SPINE_R = xm + W / 2
    f = Flow(ax, xm, W, 20.0)

    cy, _ = f.box("① 内容就绪（科生）\n"
                  "scientist-讲解-大纲.md（页序 / 要点 / 配图指向 / 出处）\n"
                  "＋ assets-inventory.md 条目（图二产物）\n"
                  "＋ 品牌资产：拍板 #18 品牌名·用字·logo ＋ #19 强调色/主色/画风（官方源取色，禁自造）",
                  "start", 8.9)
    note(ax, cy, "★ 衔接铁则\n外部技能的门 ＝ 科生的拍板点\n一律用 ask_user_question 选项卡执行",
         x=82.0, w=32.0, spine_right=SPINE_R, fs=8.0)

    cy, _ = f.box("② 选技能（拍板）\n"
                  "要「能改稿 / 交客户」　→ ppt-master（原生可编辑 .pptx）\n"
                  "要「好看 / 路演级」　　→ huashu-design（高保真 HTML deck，可导 PDF / 可编辑 PPTX）\n"
                  "（重要场合可两者都出，让用户对比选）", "idea", 8.9)

    cy, _ = f.box("③ 技能按自己的门走（科生不得替它开闸）\n"
                  "ppt-master：读 workflows/routing.md 选「恰好一条」路由\n"
                  "　（generate-pptx / Quick / image-to-pptx / beautify / create-template / fill-native / enhance）\n"
                  "　■ BLOCKING 门 → 停下等用户确认\n"
                  "　Image-first：进入规划前必须搜 ≥2 组真实图（禁「无图也行」）\n"
                  "huashu-design：● 三方向硬门 —— 任何新视觉设计先出 3 个差异化方向真实初稿\n"
                  "　（多页 deck ＝ 每方向 2 页代表页）让用户选；指定风格也不豁免\n"
                  "　Gate 文件必落档：brand-spec.md ＋ direction-approved.md（含用户选择原话）\n"
                  "　反 AI slop 禁区：紫渐变 / emoji 图标 / 圆角卡片+左 border / SVG 画人脸", "exec", 8.7)

    f.box("④ 生成\n"
          "ppt-master → .pptx（文字可在 PowerPoint 里直接改）\n"
          "huashu-design → HTML deck → 导 PDF / 可编辑 PPTX", "exec", 8.9)

    f.box("⑤ 科生验收（protocols/quality-gate.md）\n"
          "七维评分 ＋ 视觉克制/反 AI 感（科生禁区：霓虹 / 镀铬反光 / 大光球 / 激光束 / 白底紫渐变 / 海军金）\n"
          "＋ 图文对位（R12）＋ 数据页人工锁值核验 ＋ 配图授权核验", "gate", 8.9)

    cy, _ = f.box("⑥ 交付：.pptx / PDF 归档 delivery/，品牌资产与出处留档", "close", 9.2)
    note(ax, cy, "★ build_science_report.py 直出的 pptx\n只是兜底，不作交付标准",
         x=82.0, w=32.0, spine_right=SPINE_R, fs=8.0)

    f.arrows()
    ly = legend_bar(ax, f.y + 7.0, [("内容就绪", "start"), ("选技能", "idea"),
                               ("技能执行", "exec"), ("验收", "gate"), ("交付", "close")])
    finish(fig, ax, base + "-PPT流程", ly)


def main():
    ap = argparse.ArgumentParser(description="科生 SOP 流程图出图（matplotlib）")
    ap.add_argument("--out", default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "SOP-FLOW"))
    a = ap.parse_args()
    base = a.out[:-3] if a.out.endswith(".md") else a.out          # 兼容旧写法
    os.makedirs(os.path.dirname(base) or ".", exist_ok=True)
    fig_ksp(base)
    fig_asset(base)
    fig_ppt(base)
    for suf in ("-KSP主流程", "-素材处理", "-PPT流程"):
        print(f"  OK {base}{suf}.png / .pdf")
    print("完成：科生 SOP 流程图已出图（PNG 位图 + PDF 矢量）")


if __name__ == "__main__":
    main()
