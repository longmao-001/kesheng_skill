#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
写 Prompt 十步 SOP · 执行证据门控 (check_prompt_sop.py)

与 check_prompt_sheet.py 的分工：
  · check_prompt_sheet.py = **格式与一致性**（字段完整/口播单独且与口播稿一致/风格token一致/参考@/负面非空）
  · 本脚本            = **「有没有真的按 templates/prompt-sop.md 十步走」的执行证据**
    它不重复判格式，而是逐镜核对十步各自留下的**产物证据**（缺证据=该步没走）。

用法: python -X utf8 scripts/check_prompt_sop.py <runs/<项目>>

十步 → 证据 → 判定：
  1 取输入   → 镜标题含时长 + 有口播字段                  （缺→WARN）
  2 定路线   → 路线 ∈ 词表                                （缺/不在词表→FAIL）
  3 选参考图 → 参考字段有 @ ＋「挂载说明」(角色/取放/部位→位置)（裸引用→FAIL；缺部位对应/位置→WARN）
              参考明写"无(人工排版)"视为已决策 → 通过
  4 定主体   → 有【主体】(九段) 或正文含主体描述；（产品/设备类须"保真实造型=@参考图不变"→WARN）
  5 写风格   → 【风格】存在且全片逐字一致                  （缺/不一致→FAIL）
  6 写时间轴 → 时间轴有按秒分段                            （无→FAIL）
  7 写口播   → 口播为独立字段（≠"无"时须在口播稿中）        （缺/不一致→FAIL）
  8 写负面   → 负面非空（建议含红线词：霓虹/渐变/镀铬/大光球→WARN）
  9 写参数   → 参数含 时长档；（真镜头/人工排版可免抽卡；其余须含 抽卡+失败改法→WARN）
 10 自检交付 → m4-prompts/README.md 存在（全片索引）        （缺→FAIL）
"""
import io
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

CORE7 = ["参考", "风格", "时间轴", "口播", "声音", "负面", "参数"]
# 九段额外字段（合法）
EXTRA9 = {"镜头", "主体", "强制约束", "参数"}
ROUTES = {"T2V", "I2V", "参考生视频", "首尾帧", "多镜原生", "人工数据卡"}
TITLE = re.compile(r"^###\s+镜头\s+(\S+)\s*·\s*(\d+(?:\.\d+)?)s\s*·\s*(.+)$")
FIELD = re.compile(r"^(?:【([^】]+)】|(?:[*-]\s*)?\*\*([^*]+)\*\*[:：]?)\s*(.*)$")
# 挂载说明要素
ROLE_WORD = re.compile(r"主体|部件|场景|质感|参考|锚|POV|道具|角色")
TAKE_PUT = re.compile(r"取[^。；\n]{0,40}?(?:→|->|放|作|充当|用于)|取哪|放哪|用于背景|作背景|作主体")
PAIR = re.compile(r"[＝=＝]|部位|图中|位置")
# 产品/设备类关键词（决定是否要求"保真实造型"）
# 20260915修订：剔除「镜头/阵列」——影视分镜用语与石阵/灯阵构图会大面积误命中（L2检察官逐条证实全为误报）
PRODUCT = re.compile(r"产品|设备|仪器|机台|机型|机器人|电芯|器件|装置|相机|头戴")
KEEP_SHAPE = re.compile(r"保持真实造型|真实造型|参考图不变|@参考图不变|禁改形|不改形|禁新增部件|禁增删部件|保持外形")
NEG_RED = re.compile(r"霓虹|渐变|镀铬|大光球|激光束|彩虹|水印|logo|文字")
NONALNUM = re.compile(r"[，。；、：\s·《》「」“”（）()\[\]【】_\-:/|]")


def norm(s):
    return NONALNUM.sub("", s or "")


def parse_shots(md_dir):
    """返回 [(file, 镜id, 路线, 字段dict)]"""
    shots = []
    for f in sorted(os.listdir(md_dir)):
        if not (f.startswith("prompts-") and f.endswith(".md")):
            continue
        lines = io.open(os.path.join(md_dir, f), encoding="utf-8-sig", errors="ignore").read().splitlines()
        i = 0
        while i < len(lines):
            s = lines[i].strip()
            if s.startswith("### 镜头"):
                m = TITLE.match(s)
                sid, route, fields = (m.group(1), m.group(3).strip(), {}) if m else (s[:20], "", {})
                j = i + 1
                cur = None
                while j < len(lines):
                    ln = lines[j].strip()
                    if ln.startswith("### "):
                        break
                    fm = FIELD.match(ln)
                    if fm:
                        nm = (fm.group(1) or fm.group(2) or "").strip().lstrip("*")
                        if nm:
                            fields.setdefault(nm, "")
                            cur = nm
                            if fm.group(3):
                                fields[nm] = fm.group(3).strip()
                    elif ln and cur:
                        fields[cur] = (fields.get(cur) or "") + ln + "\n"
                    j += 1
                shots.append((f, sid, route, fields))
                i = j
                continue
            i += 1
    return shots


def main():
    run = sys.argv[1] if len(sys.argv) > 1 else None
    if not run or not os.path.isdir(run):
        print("用法: check_prompt_sop.py <runs/<项目>>"); sys.exit(2)
    md = os.path.join(run, "m4-prompts")
    if not os.path.isdir(md):
        print(f"FAIL: 缺少 m4-prompts 目录 ({md})"); sys.exit(1)

    shots = parse_shots(md)
    if not shots:
        print("FAIL: m4-prompts/ 下未找到 prompts-*.md 或其中无 '### 镜头' 块"); sys.exit(1)

    # 口播基准源（用于第7步核对）
    # 20260915修订：无 screenwriter-口播稿 时不再空转放行（空转=门控漏洞），
    # 逐级回退：m4-剧本-EP01.md（定稿）→ m4-剧本-EP01-v*.md（最高版）→ 全部缺失 = FAIL
    scripts = [g for g in os.listdir(run) if g.startswith("screenwriter-口播稿") and g.endswith(".md")]
    script_src = "screenwriter-口播稿"
    if not scripts:
        if os.path.exists(os.path.join(run, "m4-剧本-EP01.md")):
            scripts = ["m4-剧本-EP01.md"]
            script_src = "m4-剧本-EP01.md"
        else:
            vs = sorted(g for g in os.listdir(run)
                        if re.match(r"m4-剧本-EP01-v\d+.*\.md$", g))
            if vs:
                scripts = [vs[-1]]
                script_src = vs[-1]
    if not scripts:
        fails.append("S0: run目录既无 screenwriter-口播稿 也无 m4-剧本-EP01.md——第7步无口播基准源，门控不可空转")
        script_txt = ""
    else:
        script_txt = ""
        for g in scripts:
            script_txt += io.open(os.path.join(run, g), encoding="utf-8-sig", errors="ignore").read()
    script_norm = norm(script_txt)

    VOICE_PREFIX = re.compile(r"^[^：:]{0,16}(?:旁白|V\.O\.|VO|独白|画外|念|唱|叠诵|说书)[^：:]*[：:]")
    PAREN = re.compile(r"[（(][^）)]*[)）]")

    def voice_core(vb):
        """从口播字段提取可核对的白话正文（去角色/读法括注、去反引号、拆分镜内多段）。"""
        s = vb.replace("`", "").strip()
        s = PAREN.sub("", s)                      # 先去括注（含时间码/读法）
        s = VOICE_PREFIX.sub("", s)               # 再去段首角色/旁白前缀
        segs = []
        for seg in re.split(r"[／/|｜│。！？!?\n：:；;．，,　]+", s):
            seg = re.sub(r"^\s*[0-9:：\-–—.\s]+", "", seg).strip()   # 去时间码
            seg = re.sub(r"^(?:旁白|V\.O\.|VO|独白|画外|念回目|念|唱|叠诵)", "", seg).strip()
            seg = norm(seg)
            if seg:
                segs.append(seg)
        return segs

    def in_script(sent):
        """句同源判定：全句或去1–3字角色前缀（僧/道人/士隐等说话人标记）后命中基准源。"""
        if sent in script_norm:
            return True
        for k in (1, 2, 3):
            tail = sent[k:]
            if len(tail) >= 4 and tail in script_norm:
                return True
        return False

    # 全片风格 token 基准
    style_vals = [f.get("风格", "").strip() for _f, _i, _r, f in shots if f.get("风格", "").strip()]
    style_base = style_vals[0] if style_vals else None

    fails, warns = [], []
    step_ok = {n: 0 for n in range(1, 11)}

    for f, sid, route, fl in shots:
        tag = f"[{f}] 镜{sid}"
        ref = (fl.get("参考") or "").strip()
        # 1 取输入
        if fl.get("口播") is None:
            warns.append(f"S1 {tag}: 无口播字段（该镜输入/口播步无证据）")
        else:
            step_ok[1] += 1
        # 2 定路线
        r_main = re.sub(r"[（(].*?[)）]", "", route).strip()
        if not route or r_main not in ROUTES:
            fails.append(f"S2 {tag}: 路线缺失或不在词表（'{route}'）——第2步未走")
        else:
            step_ok[2] += 1
        # 3 选参考图
        if not ref:
            fails.append(f"S3 {tag}: 缺【参考】字段——第3步（选参考图）无证据")
        elif norm(ref) == "无" or ref.startswith("无"):
            step_ok[3] += 1                      # 明写"无(人工排版)"=已决策
        else:
            if "@" not in ref:
                fails.append(f"S3 {tag}: 参考字段无 @ 引用——第3步未走")
            else:
                has_role = bool(ROLE_WORD.search(ref))
                has_take = bool(TAKE_PUT.search(ref))
                if not (has_role or has_take):
                    fails.append(f"S3 {tag}: 参考图是**裸引用**（只写 @图N，无角色/取哪→放哪）——违反挂载清单硬规则")
                else:
                    step_ok[3] += 1
                    if not PAIR.search(ref):
                        warns.append(f"S3 {tag}: 挂载清单缺「部位对应/放哪位置」（§5-16③）")
        # 4 定主体（+产品类保真实造型）
        body = fl.get("主体", "") + fl.get("强制约束", "") + fl.get("时间轴", "")
        if fl.get("主体") or body.strip():
            step_ok[4] += 1
        else:
            warns.append(f"S4 {tag}: 无【主体】字段——第4步（定主体）无证据")
        # 仅当该镜**生成产品画面**（用参考图 且 非真镜头剪入/人工排版）才要求"保真实造型"
        prm_txt = fl.get("参数", "")
        is_real_shot = bool(re.search(r"真镜头|真素材|剪入|人工排版|人工锁值", prm_txt))
        if (not is_real_shot) and PRODUCT.search(body) and ref and not ref.startswith("无"):
            # "保持真实造型"可能写在 主体 / 强制约束 / 负面 / **参考**（与挂载清单同段）——四处都搜
            scope = (fl.get("主体", "") + fl.get("强制约束", "") + fl.get("负面", "") + fl.get("参考", ""))
            if not KEEP_SHAPE.search(scope):
                warns.append(f"S4 {tag}: 生成产品/设备画面但未写「保持真实造型=@参考图不变」——违反 §5-16②")
        # 5 写风格
        sv = (fl.get("风格") or "").strip()
        if not sv:
            fails.append(f"S5 {tag}: 缺【风格】——第5步未走")
        elif style_base and sv != style_base:
            fails.append(f"S5 {tag}: 风格 token 与全片不一致——第5步违规（须逐字复用）")
        else:
            step_ok[5] += 1
        # 6 写时间轴
        tz = fl.get("时间轴", "")
        if not re.search(r"\d+\s*[-–]\s*\d+\s*(?:秒|s)", tz):
            fails.append(f"S6 {tag}: 时间轴无按秒分段——第6步未走")
        else:
            step_ok[6] += 1
        # 7 写口播
        vb = (fl.get("口播") or "").strip()
        if not vb:
            fails.append(f"S7 {tag}: 口播字段为空——第7步未走")
        elif norm(vb) == "无":
            step_ok[7] += 1
        elif not script_norm:
            fails.append(f"S7 {tag}: 无口播基准源可核对——第7步门控不可空转")
        else:
            segs = voice_core(vb)
            if not segs:
                step_ok[7] += 1          # 去括注后无可核正文（如纯字卡镜），视为已决策
            else:
                miss = [x for x in segs if len(x) >= 4 and not in_script(x)]
                if not miss:
                    step_ok[7] += 1
                else:
                    fails.append(f"S7 {tag}: 口播与口播基准源({script_src})不一致（须逐句同源）——第7步违规 -> {' / '.join(miss[:2])}")
        # 8 写负面
        neg = (fl.get("负面") or "").strip()
        if not neg:
            fails.append(f"S8 {tag}: 【负面】为空——第8步未走")
        else:
            step_ok[8] += 1
            if not NEG_RED.search(neg):
                warns.append(f"S8 {tag}: 负面未含红线反模式词（霓虹/渐变/镀铬/大光球/文字）——建议前置写全（§5-22③）")
        # 9 写参数
        prm = fl.get("参数", "")
        if not prm:
            warns.append(f"S9 {tag}: 缺【参数】——第9步无证据")
        else:
            step_ok[9] += 1
            real = is_real_shot
            miss = []
            if not re.search(r"档|时长|\d+\s*s", prm):
                miss.append("时长档")
            if not real:
                if not re.search(r"抽卡|变体|试|重抽", prm):
                    miss.append("抽卡")
                if not re.search(r"失败|改法|回退|备选|重做", prm):
                    miss.append("失败改法")
            if miss:
                warns.append(f"S9 {tag}: 参数缺 {'/'.join(miss)}（真镜头/人工排版免抽卡与失败改法）")
        # 10 自检交付
        if os.path.exists(os.path.join(md, "README.md")):
            step_ok[10] += 1

    if not os.path.exists(os.path.join(md, "README.md")):
        fails.append("S10: 缺 m4-prompts/README.md（全片索引）——第10步（自检交付）未走")

    n = len(shots)
    print(f"== Prompt 十步 SOP 执行证据 · {n} 镜 ==")
    print("   步1取输入 步2路线 步3参考挂载 步4主体 步5风格 步6时间轴 步7口播 步8负面 步9参数 步10交付")
    print("   证据命中：" + "  ".join(f"S{k}={step_ok[k]}" for k in range(1, 11)))
    if fails:
        print(f"\nFAIL（{len(fails)}，=该步没走/走错）：")
        for x in sorted(set(fails))[:30]:
            print("  -", x)
    if warns:
        print(f"\nWARN（{len(set(warns))}，建议项，交红队/检察官人工核）：")
        for x in sorted(set(warns))[:20]:
            print("  -", x)
    if fails:
        print("\n=> 按 templates/prompt-sop.md 回对应步补齐；十步不可跳（跳=缺要素）。")
        sys.exit(1)
    print("\nPASS: 十步 SOP 均有执行证据")


if __name__ == "__main__":
    main()
