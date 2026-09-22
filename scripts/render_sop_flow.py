#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科生 SOP 流程图 · 出图脚本 (render_sop_flow.py)

用 matplotlib 出图（PNG 位图 + PDF 矢量），不依赖 graphviz / mermaid-cli / 浏览器。

**排版两条要点（都是踩坑后改的）**
1. **测量驱动**：盒高不由"行数×固定行高"估算（会溢出），先用 renderer 实测该段文字的真实
   窗口尺寸再定盒高；并对每个盒做**溢出自检**，越界即报警 + 自动收紧字号。
2. **两轴同尺度（都是磅）**：xlim = 图宽(pt)、ylim = 图高(pt)，1 单位 = 1pt。
   若两轴尺度不同，盒子会被拉成扁条、菱形会被压成箭头（实测过）；同尺度后形状不失真。
   闸门用**扁平六边形**（宽扁比例下菱形会畸变）。

用法: python -X utf8 scripts/render_sop_flow.py [--out docs/SOP-FLOW]
产出: <out>-KSP主流程.png/.pdf · <out>-素材处理.png/.pdf · <out>-PPT流程.png/.pdf
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

DPI = 132
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
PAD, GAP, LS = 8.0, 16.0, 1.5      # 盒内留白 / 盒间距 / 行距（磅）
INDENT = 150.0                     # 页边距

OVERFLOW = []


def make_measure(ax, fig):
    renderer = fig.canvas.get_renderer()
    inv = ax.transData.inverted()
    cx = ax.get_xlim()[1] / 2

    def measure(text, fs):
        t = ax.text(cx, 60, text, fontsize=fs, linespacing=LS, ha="center", va="center")
        bb = t.get_window_extent(renderer=renderer)
        t.remove()
        (x0, y0), (x1, y1) = inv.transform([(bb.x0, bb.y0), (bb.x1, bb.y1)])
        return abs(x1 - x0), abs(y1 - y0)

    return measure


def _fits(ax, fig, text, x, y, w, h, fs, tag):
    renderer = fig.canvas.get_renderer()
    inv = ax.transData.inverted()
    t = ax.text(x, y, text, fontsize=fs, linespacing=LS, ha="center", va="center", zorder=99)
    bb = t.get_window_extent(renderer=renderer)
    t.remove()
    (bx0, by0), (bx1, by1) = inv.transform([(bb.x0, bb.y0), (bb.x1, bb.y1)])
    tw, th = abs(bx1 - bx0), abs(by1 - by0)
    if not ((tw <= w - 3.0) and (th <= h - 2.0)):
        OVERFLOW.append((tag, round(tw), round(w), round(th), round(h)))


def shrink(measure, text, fs, w, floor=6.3):
    for _ in range(10):
        tw, _t = measure(text, fs)
        if tw <= w - 4.0 or fs <= floor:
            break
        fs -= 0.2
    return fs


class Flow:
    def __init__(self, ax, fig, xm, w, y0, measure):
        self.ax, self.fig, self.xm, self.w, self.y = ax, fig, xm, w, y0
        self.measure, self.nodes = measure, []

    def box(self, text, kind="ksp", fs=8.9, minh=36.0, bold=False, ls="-", lw=1.6, tag=""):
        fs = shrink(self.measure, text, fs, self.w)
        _t, th = self.measure(text, fs)
        h = max(minh, th + 2 * PAD)
        cy = self.y + h / 2
        fc, ec = C[kind]
        self.ax.add_patch(FancyBboxPatch((self.xm - self.w / 2, cy - h / 2), self.w, h,
                                        boxstyle="round,pad=0.3,rounding_size=6",
                                        linewidth=lw, edgecolor=ec, facecolor=fc,
                                        linestyle=ls, zorder=2))
        self.ax.text(self.xm, cy, text, ha="center", va="center", fontsize=fs,
                     color="#202124", fontweight="bold" if bold else "normal",
                     zorder=3, linespacing=LS)
        _fits(self.ax, self.fig, text, self.xm, cy, self.w, h, fs, tag or text[:14])
        self.nodes.append((cy, h))
        self.y += h + GAP
        return cy, h

    def gate(self, text, fs=8.7, extra=26.0, tag=""):
        """扁平六边形闸门（宽扁比例下菱形会畸变）。"""
        fs = shrink(self.measure, text, fs, self.w * 0.78)
        _t, th = self.measure(text, fs)
        h = th + extra
        w = self.w * 0.86
        cy = self.y + h / 2
        ind = min(70.0, w * 0.09)
        pts = [(self.xm - w / 2, cy), (self.xm - w / 2 + ind, cy - h / 2),
               (self.xm + w / 2 - ind, cy - h / 2), (self.xm + w / 2, cy),
               (self.xm + w / 2 - ind, cy + h / 2), (self.xm - w / 2 + ind, cy + h / 2)]
        fc, ec = C["gate"]
        self.ax.add_patch(Polygon(pts, closed=True, lw=1.9, edgecolor=ec, facecolor=fc, zorder=2))
        self.ax.text(self.xm, cy, text, ha="center", va="center", fontsize=fs,
                     color="#202124", fontweight="bold", zorder=3, linespacing=LS)
        _fits(self.ax, self.fig, text, self.xm, cy, w - 2 * ind, h, fs, tag or text[:10])
        self.nodes.append((cy, h))
        self.y += h + GAP
        return cy, h, w

    def arrows(self):
        for i in range(len(self.nodes) - 1):
            (cy1, h1), (cy2, h2) = self.nodes[i], self.nodes[i + 1]
            self.ax.add_patch(FancyArrowPatch(
                (self.xm, cy1 + h1 / 2), (self.xm, cy2 - h2 / 2), arrowstyle="-|>",
                mutation_scale=16, linewidth=1.8, color="#5F6368", zorder=1,
                shrinkA=0, shrinkB=0))

    def label_on_arrow(self, i, text, color="#137333", fs=8.2):
        (cy1, h1), (cy2, h2) = self.nodes[i], self.nodes[i + 1]
        mid = (cy1 + h1 / 2 + cy2 - h2 / 2) / 2
        self.ax.text(self.xm + 12, mid, text, ha="left", va="center", fontsize=fs,
                     color=color, zorder=4)


def side_box(ax, fig, measure, cy, text, PTS, kind="plate", x_frac=0.82, w_frac=0.30,
             spine_right=0.0, link=True, fs=8.3, prefix="", tag=""):
    x, w = PTS * x_frac, PTS * w_frac
    full = prefix + text
    fs = shrink(measure, full, fs, w, 6.2)
    _t, th = measure(full, fs)
    h = max(28.0, th + 2 * PAD)
    fc, ec = C[kind]
    ax.add_patch(FancyBboxPatch((x - w / 2, cy - h / 2), w, h,
                                boxstyle="round,pad=0.3,rounding_size=5",
                                linewidth=1.2, edgecolor=ec, facecolor=fc,
                                linestyle="--" if kind == "note" else "-", zorder=2))
    ax.text(x, cy, full, ha="center", va="center", fontsize=fs,
            color="#311B92" if kind == "plate" else "#3C4043", zorder=3, linespacing=LS)
    _fits(ax, fig, full, x, cy, w, h, fs, tag or full[:12])
    if link and spine_right:
        ax.plot([spine_right, x - w / 2], [cy, cy], color=ec, lw=1.0, ls=(0, (4, 3)), zorder=1)
    return h


def branch(ax, fig, measure, cy, x_from, label, PTS, kind="fix", w_frac=0.17):
    x_left = PTS * 0.655
    w = PTS * w_frac
    fs = shrink(measure, label, fs=8.2, w=w, floor=6.0)
    _t, th = measure(label, fs)
    h = max(30.0, th + 2 * PAD)
    fc, ec = C[kind]
    ax.add_patch(FancyArrowPatch((x_from, cy), (x_left, cy), arrowstyle="-|>",
                                 mutation_scale=15, lw=1.7, color=ec, zorder=1))
    ax.add_patch(FancyBboxPatch((x_left, cy - h / 2), w, h,
                                boxstyle="round,pad=0.3,rounding_size=5",
                                linewidth=1.5, edgecolor=ec, facecolor=fc, zorder=2))
    ax.text(x_left + w / 2, cy, label, ha="center", va="center", fontsize=fs, color=ec,
            zorder=3, linespacing=LS)
    _fits(ax, fig, label, x_left + w / 2, cy, w, h, fs, label[:8])
    return h


def legend_bar(ax, fig, measure, y, names, PTS):
    x, yy = INDENT, y
    ax.text(x, yy, "图例", fontsize=9.0, fontweight="bold", color="#3C4043", va="center")
    x += 40.0
    for name, k in names:
        w = 78.0 + len(name) * 17.0
        if x + w > PTS - INDENT:
            x, yy = INDENT, yy + 26.0
        fc, ec = C[k]
        ax.add_patch(FancyBboxPatch((x, yy - 8.0), 34.0, 16.0,
                                    boxstyle="round,pad=0.1,rounding_size=4",
                                    linewidth=1.2, edgecolor=ec, facecolor=fc, zorder=2))
        ax.text(x + 42.0, yy, name, fontsize=8.0, va="center", color="#3C4043")
        x += w + 12.0
    return yy


def title(ax, PTS, main, sub):
    ax.text(PTS / 2, 48, main, ha="center", va="center", fontsize=19.5,
            fontweight="bold", color="#1F3864")
    ax.text(PTS / 2, 92, sub, ha="center", va="center", fontsize=9.7,
            color="#5F6368", linespacing=LS + 0.2)


def render(builder, w_in, out, title_args, legend_items):
    """迭代收敛画布高度（测量依赖缩放 → 定点迭代）。"""
    PTS, S = w_in * 72.0, 2600.0
    for it in range(10):
        OVERFLOW.clear()
        fig = plt.figure(figsize=(w_in, S / 72.0), dpi=DPI)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, PTS)
        ax.set_ylim(S, 0)
        ax.axis("off")
        measure = make_measure(ax, fig)
        title(ax, PTS, *title_args)
        f = Flow(ax, fig, PTS * 0.33, PTS * 0.60, 145.0, measure)
        builder(f, ax, fig, measure, PTS)
        ly = legend_bar(ax, fig, measure, f.y + 30.0, legend_items, PTS)
        needed = ly + 26.0
        if abs(needed - S) < 8.0:
            break
        S = needed
    fig.set_size_inches(w_in, S / 72.0)
    fig.savefig(out + ".png", dpi=DPI, facecolor="white")
    fig.savefig(out + ".pdf", facecolor="white")
    plt.close(fig)
    if OVERFLOW:
        print(f"  ! 溢出 {len(OVERFLOW)} 处（{os.path.basename(out)}）:")
        for tag, tw, bw, th, bh in OVERFLOW[:12]:
            print(f"     [{tag}] 文字 {tw}x{th}pt vs 盒 {bw}x{bh}pt")
    return it + 1, len(OVERFLOW), S


# ==================== 图一：KSP 主流程 ====================
def build_ksp(f, ax, fig, measure, PTS):
    SPINE_R = f.xm + f.w / 2
    f.box("【0 启动】制片人先读全「核心流程全集」5 份 + 失败图书馆\n"
          "docs/USER_SOP.md · orchestration/ORCHESTRATION.md · protocols/quality-gate.md ·\n"
          "playbooks/production-workflow.md · templates/user-gate.md ＋ knowledge/FAILURE-LIBRARY.md\n"
          "■ 读全前禁止派活 / 建文件；产物只落 runs/<项目slug>/", "start", 8.8, tag="0启动")

    steps = [
        ("KSP-01 立项定档 ─ 制片人",
         "一句话理解 → 三问（做什么片 / 给谁看 / 多久要）→ slug ＋ STATE.md\n"
         "定档：S 档单干 ／ M 档并行+双闸（默认）／ L 档全会+全自动", "ksp",
         "拍板 #1 定档 S/M/L\n＋ #18 品牌名·用字·logo"),
        ("★ KSP-01 同卡判型：两通道（A/B）＋ 一横向能力（C）　硬规则 #42 / #43 / #44",
         "纵向：A 文案驱动（广告/科普/科研）／ B 戏剧驱动（剧集）\n"
         "横向（第二遍）：本片/本段是否音乐驱动＝是否 C\n"
         "　C∩A 广告侧 ／ C∩B 剧集侧 ／ 纯 C ／ 无 C 段（默认）\n"
         "写进 brief.md：通道（A/B/A+B）＋ 音乐驱动段（无/C∩A/C∩B＋C 段\n"
         "　时间码范围）；判型两遍不可省 —— 硬规则 #42④ / #43① / #44②", "note",
         None),
        ("KSP-02 需求简报 ＋ 预注册 ─ 制片人 ＋ 并行 4 约束（科学/导演/摄影/受众）",
         "brief.md ＝ 简报 ＋ 预注册标准 3-5 条 ＋ 素材清单/缺口\n"
         "铁则：信息缺口必须问清，不许猜", "ksp",
         "拍板 #2-7 受众/平台/时长/风格/画风/素材\n＋ #19 强调色·主色·画风"),
        ("KSP-03 科学理解（知识关 · 先读后谈）─ 科学顾问 ＋ 观众代言人 ＋ 导演（并行）",
         "· 7 步深度理解法 → 理解深度 ≥L2（L1 只够新闻稿，禁止创作）\n"
         "· 调研图料三件套：① 科学道理 ② 网图（→refs/，标来源，不入镜）③ 素材图（→建库）\n"
         "· 素材智能入库（M2 同步 · 必做）：每张三件套 ＝ read_image 多模态拆解\n"
         "　＋ 反推 AI 合成提示词（文字检索键）＋ 质量分 ★（合规一票否决）　← 见图二\n"
         "· 两点讲明白：产品=介绍+卖点 ／ 机构=研究什么+人员 ／ 设施=能力+意义\n"
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
        ("KSP-04 创意概念先行 ─ 导演 / 编剧 / 摄影 / 观众代言人",
         "Insight（已在 03.5）→ Ideation（各出 5 个创意概念 · 非完整方案）\n"
         "→ Evaluation（四维打分：预注册 / 传播力 / 科学准确 / 可执行 ＋ 红队挑战）\n"
         "→ Presentation（概念卡并列 · 证据先行）→ Refine（只深化所选）\n"
         "　深化 ＝ 完整方案：定位 / 受众 / 口播稿定稿 / 分镜概览 / 执行计划", "idea",
         "拍板 #9 概念：选一 / 融合 / 自定义"),
        ("KSP-05 口播稿（先定内容）─ 编剧",
         "2-3 个方案竞稿（① 直白规格型 ② 价值翻译型 ③ 混合型）＋ 读法批注\n"
         "逐句对号 templates/narration-formula.md（14 个句子公式 F01-F14）", "idea",
         "拍板 #16 口播方案：选一 / 混搭\n＋ #13 术语发音疑难 → 注音"),
        ("KSP-04.5 九宫格风格预览（口播之后）─ 分镜师 ＋ 美术指导",
         "九宫格出图 → 美术批复 → 风格基线固化（风格 token / 色板 / 画风 / 构图倾向）", "idea",
         "拍板 #15 风格预览：按此基线 / 换方向 / 微调"),
    ]
    for name, detail, kind, pl in steps:
        cy, _h = f.box(f"{name}\n{detail}", kind, 8.7,
                       ls=(0, (6, 3)) if kind == "halt" else "-",
                       lw=2.6 if kind == "halt" else 1.6, tag=name[:12])
        if pl:
            side_box(ax, fig, measure, cy, pl, PTS, "plate", spine_right=SPINE_R)
        if kind == "halt":
            side_box(ax, fig, measure, cy,
                     "★ 顺序铁则\n报告读完「继续」→ 才可谈\n主题共识 / 方案 / 风格 / 口播",
                     PTS, "note", spine_right=SPINE_R)

    f.box("★ 顺序铁则：口播稿 → 九宫格出图 → 才做分镜（不可乱）", "note", 9.6, bold=True)

    f.box("KSP-06 执行关（并行 → 串行交接）\n"
          "分镜表（分镜师）‖ 声音方案（声音设计师）　　　　↓\n"
          "摄影方案（摄影指导：每镜运镜 ≤2 ＋ 变速 / 光影 / 拍法路线 / 参考资产）　　↓\n"
          "prompt 分段并行转写（prompt 工程师 ×N · 每段 5-8 镜）‖ 剪辑预计划（剪辑师）　　↓\n"
          "美术 VI 复核 → 科学复核（L3 事实检察官）\n"
          "产物：storyboard-分镜表.md ／ m4-prompts/prompts-<平台>.md ／ sound ／ dop ／ editor",
          "exec", 8.7, tag="KSP-06")

    f.box("机器门控：python -X utf8 scripts/check_all.py runs/<slug>　（8 项）\n"
          "① check_sop　　　　　 产物齐 ＋ 每镜 prompt 字段完整（缺 ＝ 跳 SOP → 回退）\n"
          "② check_prompt_sheet　 格式与一致性（核心字段 / 口播≠口播稿 / 风格 / 参考 / 负面）\n"
          "③ check_prompt_sop　　 写 prompt 十步 SOP 执行证据（参考图裸引用 / 风格不同源）\n"
          "④ check_asset_pack　　 素材自包含（引用可解析、无「待补充 / 拍照」）\n"
          "⑤ check_delivery　　　 交付件版本收敛（单一源 / 包自包含 / 无漂移）\n"
          "⑥ ad_forbidden_words　 广告禁用词（绝对化 / 极限 / 疗效 / 平台禁语）\n"
          "⑦ check_runs_clean　　 runs/ 只放项目\n"
          "⑧ check_docs_integrity 技能级：SOP 无断链 / 无孤岛", "gate", 8.5, tag="门控")

    _cy, _h, gw = f.gate("红队前置闸 m4-gate-red　（独立上下文 · 未参与创作）")
    i1 = len(f.nodes) - 1
    branch(ax, fig, measure, f.nodes[i1][0], f.xm + gw / 2,
           "BLOCK\n打回对应环节\n≤2 循环", PTS)

    _cy, _h, gw2 = f.gate("出口评审闸 L4　七维评分 ＋ 三态")
    i2 = len(f.nodes) - 1
    branch(ax, fig, measure, f.nodes[i2][0], f.xm + gw2 / 2,
           "BLOCK / CONDITIONAL\n打回 ≤2 循环", PTS)

    f.box("检察官五层（每层独立上下文 · 只看证据 · 不听辩护 · 不代修）\n"
          "L1 素材 → L2 prompt → L3 事实 → L4 出口 → L4.5 总检　→　L5 用户签收", "insp", 9.3,
          tag="检察官五层")

    f.box("交付（AI 原生两档）\n"
          "A 档 · 多平台上手包（默认）：每镜【平台对照 prompt ＋ 参考图包 ＋ 口播 ＋ 抽卡建议 ＋ 画布步骤】\n"
          "　配音 ＝ AI 原生（TTS / 剪映，口播带读法批注）　｜　B 档 · 专业增强（可选，用户主动要求时）\n"
          "零意外铁则：交付后用户绝不需要再拍照 / 找物 / 补素材（否则 ＝ 流程事故）", "insp", 8.7,
          tag="交付")

    f.box("KSP-07 知识萃取归档（闭环）\n"
          "· 通用知识 → 域片段 → build_union_kg.py 重建图谱\n"
          "· 失败教训 → knowledge/FAILURE-LIBRARY.md 追加（现象 / 根因 / 已固化 / 证据）\n"
          "· 交付包归档 delivery/（视频 · 分镜 · prompts · README · 授权）\n"
          "· 隐私：kb/隐私红线.md 三分法，项目专有信息零入库", "close", 8.7, tag="KSP-07")

    f.box("交付闭环　──→　下次开工前先读 FAILURE-LIBRARY（防重复踩坑）", "close", 10.0, bold=True)

    f.box("横切 两通道 ＋ 一横向能力（硬规则 #42/#43/#44）\n"
          "· 通道 A 文案驱动 ＝ KSP-01~07（不加剧集前置）\n"
          "· 通道 B 戏剧驱动 ＝ KSP-E1~E5 前置 ＋ KSP-02~07 每集循环\n"
          "· 通道 C 音乐驱动·横向：不新增关卡 —— C∩A 挂 A 的 KSP-01~07\n"
          "　（＋广告法合规/品牌 VI）／ C∩B 挂 KSP-E2 圣经 ＋ KSP-E1 时长\n"
          "　预算之下（OP/ED 属固定资产）；主产物＝卡点表（mv-beat-sheet）\n"
          "· C 规则（卡点/文字白名单/无对白）只对 C 段生效，不得外溢到 A 口播片\n"
          "　与 B 正片；也不得为 OP/ED 编四场脊椎/剧透结构（#43③）\n"
          "· 判型两遍在 KSP-01 同卡完成；引入 C 段 / 切通道 / 混用 → 走 KSP-C", "note", 8.7,
          tag="两通道+一横向能力")

    f.box("横切 KSP-C 变更控制（随时）：变更记录 → 影响评估 → 用户拍板 → 回退最早受影响关卡\n"
          "降级：S 档单干（明示「降级模式」）／ subagent 失败 → 重派 1 次 → 仍失败制片人接手", "note", 8.7,
          tag="KSP-C")

    f.arrows()
    f.label_on_arrow(i1, "PASS / CONDITIONAL")
    f.label_on_arrow(i2, "PASS")


# ==================== 图二：素材处理 ====================
def build_asset(f, ax, fig, measure, PTS):
    SPINE_R = f.xm + f.w / 2
    f.box("文件到手：视频 / 图片 / 矢量 / PPT / PDF / Word / CAD / SolidWorks / SketchUp / 3D / 字体 / 表格 / 音频",
          "start", 9.1, tag="入口")
    f.box("① 决策树（先问「拿来干什么」）\n"
          "· 能直接入镜？　　　　　　　　　　　→ IN 直接入镜（信任主体，须真素材 ＋ 授权）\n"
          "· 给模型做锚（外观/结构/场景/质感）？→ RF 参考图\n"
          "· 只作内容依据（数据/原理/图表）？　→ CT 内容参考（原图永不出镜）\n"
          "· 只作事实 / 口径依据？　　　　　　→ 抽取稿 / 报告（带出处）\n"
          "★ 同一文件可同时多角色 → 拆开分头归类", "ksp", 8.9, tag="决策树")
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
          "⚠ CAD/3D 无解析库 → 向客户要导出件，作素材缺口走拍板 #7", "exec", 8.7, tag="按类型提取")
    f.box("③ 统一入库（全类型同一套）\n"
          "两轴分类：IN/RF/CT × MAIN/PART/SCENE/TEXT/STR/DATA/BRAND/RAW\n"
          "命名：<用途>_<类型>_<主体>_<视角>_<序号>　（文件名 ＝ 条目ID）\n"
          "三件套：read_image 多模态拆解（物品/任务/场景/结构/质感/数据/品牌/实拍）\n"
          "　　＋ 反推 AI 合成提示词（文字检索键）＋ 质量分 ★1-5\n"
          "⚙ scripts/classify_assets.py ／ scripts/annotate_assets.py", "ksp", 8.9, tag="统一入库")
    f.box("④ 建库台账 assets-inventory.md\n"
          "条目ID / 用途 / 类型 / 主体 / 视角 / 内容标签 / 反推 prompt / ★ / 来源·授权", "ksp", 8.9,
          tag="台账")
    f.box("⑤ 参考图使用（选片 · 8 维打分）\n"
          "先定「对位需求」→ 候选池（按内容标签 / 反推 prompt 文字匹配 ＋ 高分优先）\n"
          "→ 8 维打分（对位度 / 信息完整 / 角度 / 光影 / 占位 / 合规 / 唯一性 / 可溯源）\n"
          "→ 入选 ≤3 张 → 标「角色 ＋ 部位对应 ＋ 位置 ＋ 依据口播哪句」\n"
          "→ @图N 进 prompt【参考】字段", "exec", 8.9, tag="选片")
    cy, _h = f.box("⑥ 门控\n"
                   "check_reference_selection.py（选片要素完整）\n"
                   "check_asset_pack.py（引用可解析 / 无后补提示词 ＝ 自包含）\n"
                   "ad_forbidden_words.py（合规禁词）\n"
                   "→ L1 素材检察官 ＋ L2 prompt 检察官（图文对位硬查）", "gate", 8.9, tag="门控")
    f.arrows()
    side_box(ax, fig, measure, cy,
             "★ 三条硬红线\n"
             "① 合规一票否决（水印/竞品/团队照/未授权 → 不入库）\n"
             "② 数据图表只作 CT，永不出镜；\n　　数据一律人工锁值（AI 不生成数字）\n"
             "③ 产品/设备类：绝不改造真实造型\n　　＝「保持真实造型 ＝ @参考图不变」",
             PTS, "note", fs=8.1, tag="硬红线")


# ==================== 图三：PPT / Deck ====================
def build_ppt(f, ax, fig, measure, PTS):
    SPINE_R = f.xm + f.w / 2
    cy, _h = f.box("① 内容就绪（科生）\n"
                   "scientist-讲解-大纲.md（页序 / 要点 / 配图指向 / 出处）\n"
                   "＋ assets-inventory.md 条目（图二产物）\n"
                   "＋ 品牌资产：拍板 #18 品牌名·用字·logo ＋ #19 强调色/主色/画风（官方源取色，禁自造）",
                   "start", 8.9, tag="内容就绪")
    side_box(ax, fig, measure, cy,
             "★ 衔接铁则\n外部技能的门 ＝ 科生的拍板点\n一律用 ask_user_question 选项卡执行",
             PTS, "note", fs=8.1, tag="衔接铁则")
    f.box("② 选技能（拍板）\n"
          "要「能改稿 / 交客户」　→ ppt-master（原生可编辑 .pptx）\n"
          "要「好看 / 路演级」　　→ huashu-design（高保真 HTML deck，可导 PDF / 可编辑 PPTX）\n"
          "（重要场合可两者都出，让用户对比选）", "idea", 8.9, tag="选技能")
    f.box("③ 技能按自己的门走（科生不得替它开闸）\n"
          "ppt-master：读 workflows/routing.md 选「恰好一条」路由\n"
          "　（generate-pptx / Quick / image-to-pptx / beautify / create-template / fill-native / enhance）\n"
          "　■ BLOCKING 门 → 停下等用户确认\n"
          "　Image-first：进入规划前必须搜 ≥2 组真实图（禁「无图也行」）\n"
          "huashu-design：● 三方向硬门 —— 任何新视觉设计先出 3 个差异化方向真实初稿\n"
          "　（多页 deck ＝ 每方向 2 页代表页）让用户选；指定风格也不豁免\n"
          "　Gate 文件必落档：brand-spec.md ＋ direction-approved.md（含用户选择原话）\n"
          "　反 AI slop 禁区：紫渐变 / emoji 图标 / 圆角卡片+左 border / SVG 画人脸", "exec", 8.7,
          tag="技能门控")
    f.box("④ 生成\n"
          "ppt-master → .pptx（文字可在 PowerPoint 里直接改）\n"
          "huashu-design → HTML deck → 导 PDF / 可编辑 PPTX", "exec", 8.9, tag="生成")
    f.box("⑤ 科生验收（protocols/quality-gate.md）\n"
          "七维评分 ＋ 视觉克制/反 AI 感（科生禁区：霓虹 / 镀铬反光 / 大光球 / 激光束 / 白底紫渐变 / 海军金）\n"
          "＋ 图文对位（R12）＋ 数据页人工锁值核验 ＋ 配图授权核验", "gate", 8.9, tag="验收")
    cy, _h = f.box("⑥ 交付：.pptx / PDF 归档 delivery/，品牌资产与出处留档", "close", 9.3, tag="交付")
    f.arrows()
    side_box(ax, fig, measure, cy,
             "★ build_science_report.py 直出的 pptx\n只是兜底，不作交付标准",
             PTS, "note", fs=8.1, tag="兜底")


FIGS = [
    (build_ksp, "KSP主流程", 24.0,
      ("科生 SOP 流程图（一）· KSP 主流程　两通道（A/B）＋ 一横向能力（C）　KSP-01 ~ KSP-07 + KSP-E + KSP-C",
       "四条铁则：① 用户是甲方（每关拍板）　② 拍板必用选项卡　③ 证据先行　④ 知识只进图谱\n"
       "通道 A 文案驱动（主产物＝口播稿）／ 通道 B 戏剧驱动（主产物＝剧本）／ 通道 C 音乐驱动·横向（主产物＝卡点表）\n"
       "依据 docs/USER_SOP.md（流程权威）+ docs/SOP-FLOW.md（本图配套）+ orchestration/ORCHESTRATION.md（硬规则 #42/#43/#44）"),
     [("启动", "start"), ("KSP 阶段", "ksp"), ("知识关", "know"), ("硬性停顿", "halt"),
      ("创意关", "idea"), ("执行关", "exec"), ("门控/闸", "gate"),
      ("检察官/交付", "insp"), ("归档", "close"), ("打回", "fix")]),
    (build_asset, "素材处理", 23.0,
     ("科生 SOP 流程图（二）· 素材处理流程",
      "文件到手 → 参考图进 prompt　·　依据 docs/ASSET-TYPES.md（13 类文件）+ playbooks/asset-library-flow.md\n"
      "★ 核心：类型差异只在「提取」一步；分类 / 命名 / 入库 / 选片 全类型统一"),
     [("启动/入口", "start"), ("决策/分类", "ksp"), ("提取/入库/选片", "exec"),
      ("门控", "gate"), ("旁注", "note")]),
    (build_ppt, "PPT流程", 22.0,
     ("科生 SOP 流程图（三）· PPT / Deck 制作流程",
      "配合外部技能（ppt-master / huashu-design）　·　依据 playbooks/ppt-deck-flow.md\n"
      "科生不自己拼 PPT：出「大纲 ＋ 资产」→ 交成熟技能出视觉 → 科生按质量门验收"),
     [("内容就绪", "start"), ("选技能", "idea"), ("技能执行", "exec"),
      ("验收", "gate"), ("交付", "close")]),
]


def main():
    ap = argparse.ArgumentParser(description="科生 SOP 流程图出图（matplotlib·测量驱动·两轴同尺度）")
    ap.add_argument("--out", default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "SOP-FLOW"))
    a = ap.parse_args()
    base = a.out[:-3] if a.out.endswith(".md") else a.out
    os.makedirs(os.path.dirname(base) or ".", exist_ok=True)
    bad = 0
    for builder, name, w_in, targs, legs in FIGS:
        iters, nbad, S = render(builder, w_in, f"{base}-{name}", targs, legs)
        bad += nbad
        print(f"  {base}-{name}.png / .pdf   （迭代 {iters} 次 · 溢出 {nbad} 处 · "
              f"画布 {w_in:.0f} × {S / 72.0:.1f} in）")
    print("完成。" + ("排版自检全部通过（无文字溢出）" if bad == 0 else f"仍有 {bad} 处溢出需修"))


if __name__ == "__main__":
    main()
