#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨集一致性门控 (check_series_consistency.py) —— KSP-E4 / 手册 §6.2 的机器层

依据：playbooks/series-production.md
  · §6.1 跨集校验清单（11 维）+ §6.2「机器门控思路（落地形态）」判据 **D-S1–D-S8**
  · §6.2 项目专属词表只进 `runs/<series-slug>/series-config.json`，**不写进脚本**
    （仿 prompt-delivery-config.json 的做法：项目专属词只进 run 内）

判据（逐条对应手册 §6.2 表，写入注释以便回指）：
  D-S1 时长结构  OP/ED 秒数逐集相等（固定资产·浮动＝0）；正片在容差内（默认 ≤10%） → FAIL
  D-S2 锚复用    角色镜挂载的 `C*` 属本集允许集，且与首用集同版本（跨集版本漂移即 FAIL）  → FAIL
  D-S3 字帖一致  同文本跨集帖号一致；字系分档一致（同文本两帖号/同帖号两文本＝口径事故）  → FAIL
  D-S4 母题唯一  母题 ID 全局唯一；复现未声明（缺 `【复现·回环】`/`recurrence`）即 FAIL       → FAIL
  D-S5 钩子账本  每集有集尾钩且回收责任人有集号（空钩/钩到未登记集/未回填＝FAIL）           → FAIL
  D-S6 专名一致  naming_terms 内的词跨集写法逐字一致（近似误写即 WARN；★红线词缺失＝FAIL） → FAIL/WARN
  D-S7 新增入册  本集出现的锚/帖/母题 ID 均已在圣经登记（未登记/无首用集＝先斩后奏）         → FAIL
  D-S8 红线继承  全季红线（red_lines）在每集 prompt 负面中在位（跨集继承，不得单集开口）     → FAIL

与单集出口闸的关系（**两层并列、互不替代**，见手册 §6.2 与 §6.3）：
  ① 单集层：check_prompt_sheet / check_prompt_sop / check_prompt_delivery / check_delivery / check_asset_pack
     —— 逐集跑，**不得因"上一集绿了"豁免**；
  ② 剧集层：本脚本 —— 只在"集与集之间"判同一性（单集视角下天然不可见）。

用法：
  python -X utf8 scripts/check_series_consistency.py <runs/<季slug>> [--season] [--ep EPnn] [--json]
    <runs/<季slug>>  季项目目录（内含 series-config.json；集目录 EPnn/ 或 <slug>-EPnn/）
    --season         全季检查（默认行为；显式给出以便 scripts/check_all.py 直呼）
    --ep EPnn        只查某一集（配置/登记类问题仍全季校验，保证基准可信）
    --json           机器可读输出（CI / check_all）

退出码（沿用 prompt 门控的"空跑不算通过"原则）：
  0  PASS（或仅 WARN）      1  存在 FAIL
  2  不可判定：缺 series-config.json / 配置非法 / 配置 0 集 / 全季 0 个 prompt 文件 / 指定 --ep 不在配置内

⚠️ 空跑绝不等于通过：0 文件、0 集、0 判定项一律 exit 2。
⚠️ 门控与真实格式对齐（F-30）：误报＝脚本过时，不是制品不过关——修脚本，不迁就脚本。
"""
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ---------------------------------------------------------------- 常量与正则

# 集目录：EP01 / ep1 / EP1；旧形态一集一 run：<slug>-EP01
EP_DIR_RE = re.compile(r"^EP(\d{1,2})$", re.I)
EP_SUFFIX_RE = re.compile(r"-EP(\d{1,2})$", re.I)
EP_ANY_RE = re.compile(r"\bEP(\d{1,2})\b", re.I)

# prompt 文件：新规范 EPnn-prompts-<平台>.md；未分集时退化为 prompts-*.md
PROMPT_GLOBS = ("prompts-", "segments-", "EP")

# 时长标签（先 OP/ED，再正片——顺序影响 ADJ 的贪婪程度）
OP_LABEL = r"(?:OP|片头|片头曲)"
ED_LABEL = r"(?:ED|片尾|片尾曲)"
FEATURE_LABEL = r"(?:正片|净时长|正片时长|本体)"

# 时长量词：90s / 90秒 / 1分30秒 / 17分 / 17:00
DUR_TOKEN = r"(?:\d{1,2}\s*[:：]\s*\d{2}|\d+(?:\.\d+)?\s*(?:分|分钟|min|m)?\s*\d*(?:\.\d+)?\s*(?:秒|s|sec)?)"
# 标签与数值之间最多 12 字符（允许 `**`、`｜`、`：`、空格、`=` 等排版噪声）
ADJ = r"(?:\*\*|[\s｜|：:=＝〔〕\[\]（）()·—\-→]){0,12}"

NEG_FIELD = re.compile(r"(?:【负面】|\*\*\s*负面\s*\*\*\s*[：:]?|负面(?:词|块|串|prompt)?\s*[：:])")

# 「复现声明」——母题复用必须显式声明（手册 §6.1-6：复现须 `【复现·回环】`＋依据）
RECURRENCE_MARK = re.compile(r"【复现·回环】|【复现】|复现[·・]回环|复现声明")

# 「未登记/待补」信号——出现即视为"先斩后奏"（手册 §4.5：新设定必须先入册，后开抽）
PENDING_MARK = re.compile(r"未登记|待登记|待入册|未入册|先入册|待补锚|待产|⏳|❌")

# 近似专名（D-S6 WARN 用）：中文词只差一个同音/形近字不算"逐字一致"
CJK = r"\u4e00-\u9fa5"
VERSION_RE = re.compile(r"(v\d+(?:\.\d+)?)", re.I)

# 最小配置示例（缺配置时打印；与 templates/series-config.json 同构，此处刻意精简）
MINIMAL_CONFIG = {
    "_comment": "最小可用剧集配置（完整字段见 templates/series-config.json / scripts/README-check_series_consistency.md）",
    "series_slug": "YYYYMMDD-<主题>S0N",
    "episodes": ["EP01", "EP02"],
    "op_seconds": 90,
    "ed_seconds": 90,
    "feature_min_seconds": 1020,
    "feature_tolerance": 0.10,
}


# ---------------------------------------------------------------- 工具函数

def die(msg, code=2):
    """不可判定（exit 2）——绝不静默通过。"""
    print(msg)
    sys.exit(code)


def read_text(path):
    try:
        return io.open(path, encoding="utf-8-sig", errors="ignore").read()
    except Exception:  # noqa: BLE001
        return ""


def scan_text(path, limit=3_000_000):
    """大文件只读头部 limit 字节（时长契约/风格 token 都在头部），避免全量读 100MB。"""
    try:
        with io.open(path, encoding="utf-8-sig", errors="ignore") as fh:
            return fh.read(limit)
    except Exception:  # noqa: BLE001
        return ""


def norm_dur(label, raw):
    """把时长字符串转成秒；无法解析 → None。"""
    s = (raw or "").strip()
    m = re.match(r"^(\d{1,2})\s*[:：]\s*(\d{2})$", s)
    if m:                                   # 17:00 → 1020s
        return int(m.group(1)) * 60 + int(m.group(2))
    total = 0.0
    hit = False
    for num, unit in re.findall(r"(\d+(?:\.\d+)?)\s*(分|分钟|min|m|秒|s|sec)?", s):
        unit = unit or (("分",) if label == "feature" else ("秒",))[0]
        v = float(num)
        if unit in ("分", "分钟", "min", "m"):
            total += v * 60
        else:
            total += v
        hit = True
    return int(round(total)) if hit else None


def _strip_op_ed_spec(txt):
    """把 `OP90s / __分 / ED90s` 这类三段结构行里的 OP/ED 片段抹掉。

    目的：算正片时长时，`OP90s / 17分 / ED90s` 的 90/90 不得被当成正片。
    """
    txt = re.sub(OP_LABEL + ADJ + DUR_TOKEN, " ", txt)
    txt = re.sub(ED_LABEL + ADJ + DUR_TOKEN, " ", txt)
    return txt


def extract_dur(txt, kind):
    """从文本抽时长（秒）。

    kind: "op" / "ed" / "feature"。返回 (seconds|None, evidence_line)。
    只认「标签＋邻近数值」——避免把正文里的任意数字当时长（F-30：误报＝脚本过时）。
    """
    if not txt:
        return None, ""
    label = {"op": OP_LABEL, "ed": ED_LABEL, "feature": FEATURE_LABEL}[kind]
    for line in txt.splitlines():
        probe = _strip_op_ed_spec(line) if kind == "feature" else line
        m = re.search(label + ADJ + r"(" + DUR_TOKEN + r")", probe)
        if not m:
            continue
        sec = norm_dur(kind, m.group(1))
        if sec:
            return sec, line.strip()[:120]
    return None, ""


def near_miss_terms(word):
    """生成"近似误写"探针（用于 D-S6 WARN）：同形近字替换，不做通配删除（F-47：禁叠字归并）。"""
    pairs = {
        "蘆": "芦", "芦": "蘆", "廟": "庙", "庙": "廟", "茫": "芒", "芒": "茫",
        "淨": "净", "净": "淨", "後": "后", "后": "後", "係": "系", "系": "係",
        "裏": "里", "裡": "里", "里": "裡", "鑑": "鉴", "鉴": "鑑", "讖": "谶", "谶": "讖",
    }
    out = set()
    for i, ch in enumerate(word):
        if ch in pairs and pairs[ch] != ch:
            out.add(word[:i] + pairs[ch] + word[i + 1:])
    return sorted(out)


# ---------------------------------------------------------------- 集定位与制品读取

class Episode:
    """一集的定位信息与制品文本缓存。"""

    def __init__(self, ep, ep_dir, root, cfg):
        self.ep = ep                      # 'EP01'
        self.dir = ep_dir                 # 集目录（可能等于季目录 = 未分集）
        self.root = root
        self.cfg = cfg
        self._cache = {}

    # ---- 制品文件 -------------------------------------------------
    def find(self, *patterns):
        """在集目录 + 集目录/m4-prompts + 季目录 内按文件名前缀/正则找文件（不递归进 _shared）。"""
        pats = [re.compile(p) for p in patterns]
        search_dirs = [self.dir]
        if os.path.basename(os.path.normpath(self.dir)) != os.path.basename(os.path.normpath(self.root)):
            search_dirs.append(self.root)
        md = os.path.join(self.dir, "m4-prompts")
        if os.path.isdir(md):
            search_dirs.insert(0, md)
        hits = []
        for d in search_dirs:
            if not os.path.isdir(d):
                continue
            for f in sorted(os.listdir(d)):
                p = os.path.join(d, f)
                if not os.path.isfile(p):
                    continue
                if any(x.search(f) for x in pats):
                    hits.append(p)
        return hits

    def prompt_files(self):
        """本集 prompt 制品（一平台一文件；新规范 EPnn-prompts-*.md）。"""
        if "prompt_files" in self._cache:
            return self._cache["prompt_files"]
        ep_pat = rf"^{self.ep}-prompts-.*\.md$"
        hits = self.find(ep_pat, r"^prompts-.*\.md$", r"^segments-.*\.md$")
        # 季目录下的 prompts-* 只在"未分集"（单集形态）时归本集，避免多集共用时重复计数
        if len(self.episodes_of_root()) > 1:
            hits = [h for h in hits if os.path.dirname(h) != os.path.normpath(self.root)
                    or re.match(ep_pat, os.path.basename(h))]
        self._cache["prompt_files"] = hits
        return hits

    def episodes_of_root(self):
        return self.cfg.get("_episodes_of_root") or []

    def header_text(self, limit=120_000):
        """头部文本：时长契约 / 风格 token 多在文件头或简报头部。"""
        if "header" in self._cache:
            return self._cache["header"]
        parts = []
        for p in self.prompt_files()[:4]:
            parts.append(scan_text(p, limit))
        for p in self.find(rf"^{self.ep}-brief\.md$", rf"^{self.ep}-.*出口闸.*\.md$",
                           rf"^{self.ep}-分镜表\.md$"):
            parts.append(read_text(p)[:40_000])
        txt = "\n".join(parts)
        self._cache["header"] = txt
        return txt

    def prompt_text(self):
        """本集全部 prompt 正文（D-S2/D-S3/D-S4/D-S8 在正文里找引用）。"""
        if "prompt_text" in self._cache:
            return self._cache["prompt_text"]
        txt = "\n".join(read_text(p) for p in self.prompt_files())
        self._cache["prompt_text"] = txt
        return txt

    # ---- 时长契约（D-S1）------------------------------------------
    def duration(self, kind):
        """返回 (seconds, source)：source ∈ {measured, config, missing}。"""
        key = f"dur_{kind}"
        if key in self._cache:
            return self._cache[key]
        sec, line = extract_dur(self.header_text(), kind)
        if sec:
            res = (sec, "measured", line)
        else:
            conf_key = {"op": "op_seconds", "ed": "ed_seconds", "feature": "feature_min_seconds"}[kind]
            val = self.cfg.get(conf_key)
            res = (val, "config", "") if isinstance(val, (int, float)) else (None, "missing", "")
        self._cache[key] = res
        return res

    def negative_text(self):
        """本集【负面】字段文本合集（D-S8 红线在位于此判）。"""
        if "neg" in self._cache:
            return self._cache["neg"]
        txt = self.prompt_text()
        chunks = []
        for line in txt.splitlines():
            if NEG_FIELD.search(line):
                chunks.append(line)
        self._cache["neg"] = "\n".join(chunks)
        return self._cache["neg"]


# ---------------------------------------------------------------- 配置加载

def load_config(root):
    path = os.path.join(root, "series-config.json")
    if not os.path.isfile(path):
        print(f"FAIL: 未找到剧集配置 `series-config.json`（{path}）")
        print("      —— 跨集一致性门控不可判定：**无配置＝不通过**（空跑不算通过）。")
        print("      最小配置示例（写入 runs/<季slug>/series-config.json 后重跑）：")
        print(json.dumps(MINIMAL_CONFIG, ensure_ascii=False, indent=2))
        print("      完整字段与写法见 templates/series-config.json / scripts/README-check_series_consistency.md")
        sys.exit(2)
    try:
        cfg = json.loads(read_text(path))
    except Exception as e:  # noqa: BLE001
        print(f"FAIL: `{path}` 不是合法 JSON：{e}")
        sys.exit(2)
    if not isinstance(cfg, dict):
        print(f"FAIL: `{path}` 顶层必须是对象（JSON object）")
        sys.exit(2)
    cfg["_path"] = path

    # episodes：字符串数组 或 对象数组（{id|ep, dir, prompts[]}）
    eps, seen = [], set()
    for item in cfg.get("episodes") or []:
        if isinstance(item, str):
            eid, edir = item.strip(), None
        elif isinstance(item, dict):
            eid = str(item.get("id") or item.get("ep") or "").strip()
            edir = item.get("dir")
        else:
            continue
        if not eid:
            continue
        m = EP_ANY_RE.search(eid) or re.search(r"^(\d{1,2})$", eid)
        eid = f"EP{int(m.group(1)):02d}" if m else eid
        if eid in seen:
            continue
        seen.add(eid)
        eps.append((eid, edir))
    cfg["_episodes"] = eps

    if not cfg["_episodes"]:
        print(f"FAIL: `{path}` 的 `episodes` 为空——**配置 0 集＝不可判定**（空跑不算通过）。")
        print("      至少写一集，例如：\"episodes\": [\"EP01\", \"EP02\"]")
        sys.exit(2)
    return cfg


def locate_episodes(root, cfg):
    """把配置里的集号映射到实际目录：EPnn/ → 季目录 → <季目录名>-EPnn/。"""
    season_base = os.path.basename(os.path.normpath(root))
    episodes, missing = [], []
    dirs_found = []
    for eid, edir in cfg["_episodes"]:
        cands = []
        if edir:
            cands.append(os.path.join(root, edir) if not os.path.isabs(edir) else edir)
        cands.append(os.path.join(root, eid))                       # A 形态：季目录下 EPnn/
        cands.append(os.path.join(os.path.dirname(root), f"{season_base}-{eid}"))  # B 形态：一集一 run
        if len(cfg["_episodes"]) == 1:
            cands.append(root)                                      # 单集形态：季目录本体（仅单集时兜底）
        hit = next((c for c in cands if os.path.isdir(c)), None)
        if hit is None:
            missing.append(eid)
            continue
        dirs_found.append(hit)
        episodes.append(Episode(eid, hit, root, cfg))
    cfg["_episodes_of_root"] = [e.ep for e in episodes]
    return episodes, missing


# ---------------------------------------------------------------- 判据实现（D-S1–D-S8）

class Result:
    def __init__(self):
        self.fails, self.warns, self.notes = [], [], []

    def fail(self, ep, code, msg):
        self.fails.append({"ep": ep, "code": code, "msg": msg})

    def warn(self, ep, code, msg):
        self.warns.append({"ep": ep, "code": code, "msg": msg})

    def note(self, ep, code, msg):
        self.notes.append({"ep": ep, "code": code, "msg": msg})


def check_ds1_duration(episodes, cfg, res, only_ep=None):
    """D-S1 时长结构：逐集 OP/ED 秒数相等（浮动＝0），正片在容差内。"""
    tol = cfg.get("feature_tolerance", 0.10)
    base = {}
    for kind, key in (("op", "op_seconds"), ("ed", "ed_seconds"), ("feature", "feature_min_seconds")):
        v = cfg.get(key)
        if isinstance(v, (int, float)):
            base[kind] = float(v)
        else:
            meas = [e.duration(kind)[0] for e in episodes if e.duration(kind)[0]]
            base[kind] = None
            if meas:
                base[kind] = float(meas[0])
    for e in episodes:
        if only_ep and e.ep != only_ep:
            continue
        for kind, cn in (("op", "OP"), ("ed", "ED"), ("feature", "正片")):
            sec, src, line = e.duration(kind)
            if sec is None:
                if kind == "feature" and base.get("feature") is None:
                    res.note(e.ep, "D-S1", f"{cn}时长未声明（配置无基准、制品无声明）——请先写进圣经/大纲时长结构")
                else:
                    res.warn(e.ep, "D-S1", f"{cn}时长本集未声明，按契约基准 {base.get(kind)}s 判定（建议在集内制品写明）")
                continue
            b = base.get(kind)
            if b is None:
                continue
            if src == "config" and kind != "feature":
                continue                       # 本集未声明、用配置基准 → 不算漂移，仅上面的 WARN 提示
            if kind in ("op", "ed"):
                if abs(sec - b) >= 1:          # OP/ED 是固定资产：逐秒相等，浮动＝0
                    res.fail(e.ep, "D-S1",
                             f"{cn}时长 {sec}s ≠ 契约 {int(b)}s（OP/ED 为固定资产，逐集逐秒相等；浮动＝0）"
                             + (f"　证据：{line}" if line else ""))
            else:
                lo = b * (1 - tol)
                hi = b * (1 + tol)
                if not (lo <= sec <= hi):
                    res.fail(e.ep, "D-S1",
                             f"正片时长 {sec}s 超出容差（基准 {int(b)}s ±{int(tol * 100)}%）"
                             + (f"　证据：{line}" if line else ""))
                elif abs(sec - b) >= 1:
                    res.warn(e.ep, "D-S1", f"正片时长 {sec}s ≠ 基准 {int(b)}s（容差内，属正常浮动）")


def _anchor_registry(cfg):
    """锚登记表 → {ID: 条目}；兼容 dict / list 两种写法。"""
    reg = cfg.get("anchor_registry") or {}
    out = {}
    if isinstance(reg, dict):
        for k, v in reg.items():
            item = dict(v) if isinstance(v, dict) else {"file": str(v)}
            item.setdefault("id", k)
            out[k] = item
    elif isinstance(reg, list):
        for v in reg:
            if isinstance(v, dict) and (v.get("id") or v.get("anchor")):
                out[str(v.get("id") or v.get("anchor"))] = v
    return out


def _allowed(item, ep):
    scope = item.get("allowed_episodes") or item.get("reuse_scope") or item.get("episodes")
    if scope in (None, "", [], "全季", "season", "*"):
        return True
    if isinstance(scope, str):
        scope = [x.strip() for x in re.split(r"[,，、/\s]+", scope) if x.strip()]
    return ep in scope or "全季" in scope


def check_ds2_anchors(episodes, cfg, res, only_ep=None):
    """D-S2 锚复用：角色镜挂载的 `C*` 属本集允许集，且与首用集同版本（跨集版本漂移＝FAIL）。"""
    reg = _anchor_registry(cfg)
    if not reg:
        res.note("SEASON", "D-S2", "配置未登记 `anchor_registry`——锚复用无基准可判（跨集人物漂移=最高风险项，建议补齐）")
        return
    ver_seen = {}                                     # 锚ID -> {版本: [集号…]}
    for e in episodes:
        if only_ep and e.ep != only_ep:
            continue
        txt = e.prompt_text() or ""
        for aid, item in reg.items():
            if not re.search(rf"(?<![A-Za-z0-9]){re.escape(aid)}(?![A-Za-z0-9])", txt):
                continue
            # 允许集（§6.1-1 未挂＝FAIL；此处判"挂了但不该在本集出现"）
            if not _allowed(item, e.ep):
                res.fail(e.ep, "D-S2",
                         f"锚 `{aid}` 出现在本集 prompt，但登记允许集为 {item.get('allowed_episodes') or item.get('reuse_scope')}"
                         f"（跨集漂移：复用锚不得越界）")
            # 未登记（D-S7 亦判，此处只提示"用了未入册的锚"）
            if PENDING_MARK.search(f"{item.get('state','')}{item.get('file','')}"):
                res.warn(e.ep, "D-S2", f"锚 `{aid}` 登记状态为待产/待补（{item.get('state') or item.get('file')}）——开抽前须转 ✅")
            # 版本一致性（同 ID 跨集同版本）：两种证据都查——
            #   ① 登记项内声明 version；② prompt 内**同一文件名 token** 的版本号
            #      （`C1a-士隐-主锚-v1.jpeg` → v1；**只在 ID 之后同一 token 内找**，
            #        否则会误抓同行下一个文件名/全角字符的版本 = 假阳性，F-30 教训）
            vs = set()
            if item.get("version"):
                vs.add(str(item["version"]).lower())
            tok_pat = re.compile(rf"(?<![A-Za-z0-9]){re.escape(aid)}([A-Za-z0-9\u4e00-\u9fa5_.\-]{{0,60}})")
            for vm in tok_pat.finditer(txt):
                mv = VERSION_RE.search(vm.group(1)) or VERSION_RE.search(aid + vm.group(1))
                if mv:
                    vs.add(mv.group(1).lower())
            for v in vs:
                ver_seen.setdefault(aid, {}).setdefault(v, []).append(e.ep)
    for aid, vs in ver_seen.items():
        if len(vs) > 1:
            detail = "；".join(f"{k}→{','.join(sorted(set(v_)))}" for k, v_ in sorted(vs.items()))
            res.fail("SEASON", "D-S2", f"锚 `{aid}` 跨集版本漂移（同 ID 必须同版本）：{detail}")


def _threads(cfg):
    """字帖线（threads）→ [(帖号, 文本, 允许集, 字系)]；兼容 dict/list。"""
    raw = cfg.get("text_card_threads") or []
    out = []
    items = raw.items() if isinstance(raw, dict) else enumerate(raw)
    for k, v in items:
        if isinstance(v, dict):
            out.append({"thread": str(v.get("thread") or v.get("id") or k),
                        "text": str(v.get("text") or ""),
                        "allowed": v.get("allowed_episodes") or v.get("episodes"),
                        "script": v.get("script") or v.get("字形") or ""})
        else:
            out.append({"thread": str(k), "text": str(v), "allowed": None, "script": ""})
    return out


def check_ds3_text_cards(episodes, cfg, res, only_ep=None):
    """D-S3 字帖一致：同文本跨集帖号一致；字系分档一致（同文本两帖号＝口径事故）。"""
    threads = _threads(cfg)
    if not threads:
        res.note("SEASON", "D-S3", "配置未登记 `text_card_threads`——同文本同帖无基准可判（字帖铁律 #32 的跨集层）")
        return
    text2thread, thread2text = {}, {}
    for t in threads:
        if t["text"]:
            text2thread.setdefault(t["text"], set()).add(t["thread"])
        thread2text.setdefault(t["thread"], set()).add(t["text"])
    for txt, ts in text2thread.items():
        if len(ts) > 1:
            res.fail("SEASON", "D-S3", f"同一文本对应多个帖号（同文本必须同帖）：`{txt[:24]}…` → {sorted(ts)}")
    for th, txts in thread2text.items():
        if len(txts) > 1 and "" not in txts:
            res.fail("SEASON", "D-S3", f"同一帖号对应多个文本（帖号跨集唯一）：`{th}` → {sorted(x[:16] for x in txts)}")
    # 集内实际引用核对
    for e in episodes:
        if only_ep and e.ep != only_ep:
            continue
        txt = e.prompt_text() or ""
        for t in threads:
            if not t["text"] or t["text"] not in txt:
                continue
            if not _allowed({"allowed_episodes": t["allowed"]}, e.ep):
                res.fail(e.ep, "D-S3", f"字帖 `{t['thread']}`（文本「{t['text'][:16]}…」）出现在本集，但登记允许集为 {t['allowed']}")
            if t["script"] and re.search(r"简体|繁体|碑刻|魏碑|馆阁|篆", t["script"]):
                other = "简体" if "繁体" in t["script"] else ("繁体" if "简体" in t["script"] else "")
                if other and re.search(rf"(?:字系|字形)[^\n]{{0,20}}{other}", txt):
                    res.warn(e.ep, "D-S3", f"字帖 `{t['thread']}` 登记字系为「{t['script']}」，但本集出现「{other}」字样——核对字系分体例")


def _motifs(cfg):
    raw = cfg.get("motif_registry") or []
    out = []
    items = raw.items() if isinstance(raw, dict) else enumerate(raw)
    for k, v in items:
        if isinstance(v, dict):
            out.append({"id": str(v.get("id") or v.get("motif") or k),
                        "first": str(v.get("first_episode") or v.get("first") or ""),
                        "allowed": v.get("allowed_episodes") or v.get("reuse_scope") or v.get("episodes"),
                        "limit": v.get("max_recurrence") or v.get("limit"),
                        "recurrence": v.get("recurrence") or v.get("declared")})
        else:
            out.append({"id": str(v), "first": "", "allowed": None, "limit": None, "recurrence": None})
    return out


def check_ds4_motifs(episodes, cfg, res, only_ep=None):
    """D-S4 母题唯一：ID 全局唯一；复现未声明（缺【复现·回环】）即 FAIL。"""
    motifs = _motifs(cfg)
    if not motifs:
        res.note("SEASON", "D-S4", "配置未登记 `motif_registry`——母题唯一性/复现声明无基准可判")
        return
    seen = {}
    for m in motifs:
        if m["id"] in seen:
            res.fail("SEASON", "D-S4", f"母题 ID 重复登记：`{m['id']}`（母题 ID 全局唯一）")
        seen[m["id"]] = m
    for e in episodes:
        if only_ep and e.ep != only_ep:
            continue
        txt = e.prompt_text() or ""
        for m in motifs:
            if not re.search(rf"(?<![A-Za-z0-9]){re.escape(m['id'])}(?![A-Za-z0-9])", txt):
                continue
            first = m["first"]
            is_reuse = bool(first) and first != e.ep
            declared = bool(m["recurrence"]) or bool(RECURRENCE_MARK.search(txt))
            if not first:
                res.fail(e.ep, "D-S4", f"母题 `{m['id']}` 未登记「首次出现集」——无法判定是本集首用还是复现（先入册后开抽）")
            elif is_reuse and not declared:
                res.fail(e.ep, "D-S4",
                         f"母题 `{m['id']}` 首用集为 {first}，本集为复现，但未见复现声明（须标 `【复现·回环】`＋依据）")
            if not _allowed(m, e.ep):
                res.fail(e.ep, "D-S4", f"母题 `{m['id']}` 出现在本集，但登记允许集为 {m['allowed']}")


def check_ds5_hooks(episodes, cfg, res, only_ep=None):
    """D-S5 钩子账本：每集有集尾钩且回收责任人有集号（空钩/钩到未登记集＝FAIL）。"""
    ledger = cfg.get("hook_ledger")
    if not ledger:
        res.fail("SEASON", "D-S5", "配置缺 `hook_ledger`（钩子账本）——**每集集尾钩必须有回收责任人**，账本为空＝不可判定")
        return
    rows = ledger if isinstance(ledger, list) else [dict(v, ep=k) if isinstance(v, dict) else {"ep": k, "hook": v}
                                                    for k, v in ledger.items()]
    # 本季"已登记集目"：配置集目 ∪ 盘上已定位的集（未做的集不算已知，但钩子可指向它）
    known = {e.ep for e in episodes}
    for k in (cfg.get("episodes") or []):
        s = str(k.get("id") if isinstance(k, dict) else k)
        m = EP_ANY_RE.search(s) or re.search(r"^(\d{1,2})$", s)
        if m:
            known.add(f"EP{int(m.group(1)):02d}")
    season_n = cfg.get("season_episode_count") or cfg.get("season_episodes") or cfg.get("集数")
    by_ep = {}
    for r in rows:
        raw_ep = str(r.get("ep") or r.get("episode") or r.get("集号") or "")
        m = EP_ANY_RE.search(raw_ep)
        ep = f"EP{int(m.group(1)):02d}" if m else raw_ep
        by_ep.setdefault(ep, []).append(r)
    for e in episodes:
        if only_ep and e.ep != only_ep:
            continue
        rs = by_ep.get(e.ep) or []
        if not rs:
            res.fail(e.ep, "D-S5", "钩子账本无本集条目——本集无集尾钩（剧集收尾＝给问题、接下一集；空钩即 FAIL）")
            continue
        for r in rs:
            hook = str(r.get("hook") or r.get("tail_hook") or r.get("集尾钩") or "").strip()
            if not hook or hook in ("无", "—", "-"):
                res.fail(e.ep, "D-S5", "集尾钩为空——空钩＝FAIL（一集一主钩，且必须写清钩的是什么）")
            owner = str(r.get("owner") or r.get("payoff") or r.get("payoff_ep") or r.get("兑现") or "").strip()
            if not owner:
                res.fail(e.ep, "D-S5", f"集尾钩「{hook[:20]}」无回收责任人（写不出「哪一集哪一拍兑现」＝空钩）")
                continue
            om = EP_ANY_RE.search(owner)
            if not om:
                res.fail(e.ep, "D-S5", f"集尾钩「{hook[:20]}」的兑现责任人未带集号（'{owner[:24]}'）——必须写 `EPnn`")
                continue
            target = f"EP{int(om.group(1)):02d}"
            if isinstance(season_n, int) and int(om.group(1)) > season_n:
                res.fail(e.ep, "D-S5",
                         f"集尾钩兑现集 `{target}` 超出全季集数 {season_n}（钩到季外＝断钩）")
            elif target not in known:
                res.warn(e.ep, "D-S5", f"集尾钩兑现集 `{target}` 尚未在本季集目/盘上出现——该集产出时须回填核对")
            if target == e.ep:
                res.warn(e.ep, "D-S5", "集尾钩兑现集与自身同集——确认不是「本集内回收」的写法误用")


def check_ds6_naming(episodes, cfg, res, only_ep=None):
    """D-S6 专名一致：naming_terms 逐字一致；近似误写 WARN，★红线词缺失 FAIL。"""
    terms = cfg.get("naming_terms")
    if not terms:
        res.note("SEASON", "D-S6", "配置未登记 `naming_terms`（专名/称谓白名单）——同词两写无基准可判（配 F-47 三禁令）")
        return
    if isinstance(terms, dict):
        items = [{"term": k, "episodes": v if not isinstance(v, dict) else v.get("episodes")}
                 for k, v in terms.items()]
        red = [k for k, v in terms.items() if isinstance(v, dict) and v.get("red_line")]
    else:
        items = [{"term": t, "episodes": None} if isinstance(t, str) else dict(t) for t in terms]
        red = [str(t) for t in terms if isinstance(t, dict) and t.get("red_line")]
    for e in episodes:
        if only_ep and e.ep != only_ep:
            continue
        txt = e.prompt_text() or ""
        for it in items:
            term = str(it.get("term") or "")
            if not term:
                continue
            if _allowed({"allowed_episodes": it.get("episodes")}, e.ep) and term not in txt:
                if term in red:
                    res.fail(e.ep, "D-S6", f"★红线专名 `{term}` 未在本集出现（白名单红线词缺失＝口径断裂）")
                continue
            for bad in near_miss_terms(term):
                if re.search(rf"(?<![\u4e00-\u9fa5]){re.escape(bad)}(?![\u4e00-\u9fa5])", txt) and term not in txt:
                    res.warn(e.ep, "D-S6", f"疑似专名误写：应为 `{term}`，本集只见 `{bad}`（同词两写＝FAIL；请逐点 diff 取证，F-47）")


def check_ds7_registry(episodes, cfg, res, only_ep=None):
    """D-S7 新增入册：本集出现的锚/帖/母题 ID 均已在圣经登记（未登记/无首用集＝先斩后奏）。"""
    anchors = _anchor_registry(cfg)
    threads = {t["thread"]: t for t in _threads(cfg)}
    motifs = {m["id"]: m for m in _motifs(cfg)}
    if not (anchors or threads or motifs):
        res.note("SEASON", "D-S7", "配置未登记任何注册表（anchor_registry/text_card_threads/motif_registry）——入册判定无基准")
        return
    unreg = 0                                        # 未登记引用累计（只留前 20 条，避免刷屏）
    for e in episodes:
        if only_ep and e.ep != only_ep:
            continue
        if not e.prompt_files():
            res.fail(e.ep, "D-S7", "本集无 prompt 文件——交付件缺失（入册引用无从核对，空跑不算通过）")
            continue
        txt = e.prompt_text() or ""
        # 未登记却被引用的 ID 形态（C*/S*/Y*/#*/M-*）
        for m in re.finditer(r"(?<![A-Za-z0-9#])([CSY]\d+[a-z]?|#\d{1,3}|M-[A-Za-z\u4e00-\u9fa5]{1,6}\d{0,2})(?![A-Za-z0-9])", txt):
            tok = m.group(1)
            hit = False
            if tok.startswith("#"):
                hit = tok in threads or tok.lstrip("#") in threads
                what = f"引用字帖 `{tok}` 未在本季 `text_card_threads` 登记（先入册后开抽）"
            elif tok.startswith("M-"):
                hit = tok in motifs
                what = f"引用母题 `{tok}` 未在本季 `motif_registry` 登记"
            else:
                hit = tok in anchors
                what = f"引用锚 `{tok}` 未在本季 `anchor_registry` 登记（新设定必须先入册）"
            if not hit:
                unreg += 1
                if unreg <= 20:
                    res.warn(e.ep, "D-S7", what)
        # 已登记的：首用集必须写死
        for aid, item in anchors.items():
            if item.get("first_episode") or item.get("first"):
                continue
            if re.search(rf"(?<![A-Za-z0-9]){re.escape(aid)}(?![A-Za-z0-9])", txt):
                res.fail(e.ep, "D-S7", f"锚 `{aid}` 被本集引用，但圣经登记项缺「首用集」——形态锚/新增锚必须先入册")
        for mid, item in motifs.items():
            if not item.get("first") and re.search(rf"(?<![A-Za-z0-9]){re.escape(mid)}(?![A-Za-z0-9])", txt):
                res.fail(e.ep, "D-S7", f"母题 `{mid}` 被本集引用，但登记项缺「首次出现集」")
    if unreg > 20:
        res.note("SEASON", "D-S7", f"另有 {unreg - 20} 条未登记 ID 引用未逐条列出（登记表补齐后重跑）")


def check_ds8_redlines(episodes, cfg, res, only_ep=None):
    """D-S8 红线继承：全季红线在每集 prompt 负面中在位（不得单集开口）。"""
    reds = cfg.get("red_lines") or []
    if not reds:
        res.note("SEASON", "D-S8", "配置未登记 `red_lines`（全季红线）——红线继承无基准可判（跨集继承，不得单集开口）")
        return
    items = [{"term": r} if isinstance(r, str) else dict(r) for r in reds]
    for e in episodes:
        if only_ep and e.ep != only_ep:
            continue
        neg = e.negative_text()
        full = e.prompt_text() or ""
        if not e.prompt_files():
            res.fail(e.ep, "D-S8", "本集无 prompt 文件——红线在位无从核对（空跑不算通过）")
            continue
        if not neg:
            res.fail(e.ep, "D-S8", "本集 prompt 未识别到任何【负面】字段——全季红线无法在位（负面字段是红线的唯一载体）")
            continue
        for it in items:
            term = str(it.get("term") or it.get("red_line") or "")
            if not term:
                continue
            allow_missing = it.get("episodes") or it.get("allowed_episodes")
            if allow_missing and not _allowed({"allowed_episodes": allow_missing}, e.ep):
                continue
            if term not in neg:
                where = "正文出现但负面未钉" if term in full else "本集完全未见"
                res.fail(e.ep, "D-S8", f"全季红线 `{term}` 未在本集【负面】在位（{where}）——跨集继承，不得单集开口")


# ---------------------------------------------------------------- 输出

CHECK_NAMES = [
    ("D-S1", "时长结构", "OP/ED 逐集逐秒相等；正片在容差内"),
    ("D-S2", "锚复用", "角色锚属本集允许集、且与首用集同版本"),
    ("D-S3", "字帖一致", "同文本同帖号；字系分档一致"),
    ("D-S4", "母题唯一", "母题 ID 唯一；复现须声明"),
    ("D-S5", "钩子账本", "每集有集尾钩且回收责任人有集号"),
    ("D-S6", "专名一致", "naming_terms 逐字一致"),
    ("D-S7", "新增入册", "锚/帖/母题 ID 均已登记（先入册后开抽）"),
    ("D-S8", "红线继承", "全季红线在每集负面在位"),
]


def emit_text(root, episodes, cfg, res, scope_label, counts):
    print(f"== 跨集一致性门控（KSP-E4 · 手册 §6.2 D-S1–D-S8）==")
    print(f"   季目录: {root}")
    print(f"   配置  : {cfg.get('_path')}")
    print(f"   范围  : {scope_label}　集数: {len(episodes)}　有 prompt 的集: {counts['with_prompts']}"
          f"　prompt 文件: {counts['files']}")
    print("   判据  : " + " · ".join(f"{c} {n}" for c, n, _ in CHECK_NAMES))
    print()
    by_ep = {}
    for x in res.fails:
        by_ep.setdefault(x["ep"], {"FAIL": [], "WARN": [], "NOTE": []})["FAIL"].append(x)
    for x in res.warns:
        by_ep.setdefault(x["ep"], {"FAIL": [], "WARN": [], "NOTE": []})["WARN"].append(x)
    for x in res.notes:
        by_ep.setdefault(x["ep"], {"FAIL": [], "WARN": [], "NOTE": []})["NOTE"].append(x)
    order = [e.ep for e in episodes] + ["SEASON"]
    for ep in [x for x in order if x in by_ep] + [x for x in by_ep if x not in order]:
        blk = by_ep[ep]
        head = "【全季】" if ep == "SEASON" else f"【{ep}】"
        print(f"{head} FAIL {len(blk['FAIL'])} / WARN {len(blk['WARN'])} / NOTE {len(blk['NOTE'])}")
        for x in blk["FAIL"]:
            print(f"   ✗ {x['code']} {x['msg']}")
        for x in blk["WARN"]:
            print(f"   ! {x['code']} {x['msg']}")
        for x in blk["NOTE"]:
            print(f"   · {x['code']} {x['msg']}")
        print()
    n_f, n_w = len(res.fails), len(res.warns)
    if n_f:
        summary = "FAIL"
    elif n_w:
        summary = "WARN"
    else:
        summary = "PASS"
    print(f"—— {summary}：FAIL {n_f} / WARN {n_w}"
          f"（FAIL>0 不得交付；过闸记录落 runs/<slug>/EPnn/ep-consistency-check.md，"
          f"并由独立上下文检察官出《全季一致性裁决书》）")


def main():
    argv = sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        sys.exit(0 if argv else 2)
    root = argv[0]
    as_json = "--json" in argv
    only_ep = None
    if "--ep" in argv:
        i = argv.index("--ep")
        if i + 1 >= len(argv):
            die("用法错误：--ep 需要一个集号，如 --ep EP02", 2)
        only_ep = argv[i + 1].strip()
        m = EP_ANY_RE.search(only_ep) or re.search(r"^(\d{1,2})$", only_ep)
        only_ep = f"EP{int(m.group(1)):02d}" if m else only_ep
    if not os.path.isdir(root):
        die(f"用法错误：`{root}` 不是目录。用法: check_series_consistency.py <runs/<季slug>> [--season] [--ep EPnn] [--json]", 2)

    cfg = load_config(root)
    episodes, missing = locate_episodes(root, cfg)
    if not episodes:
        print(f"FAIL: 配置声明了 {len(cfg['_episodes'])} 集，但在 `{root}` 下一个集目录也没找到"
              f"（找过 EPnn/ 与 <季目录名>-EPnn/）——**0 集＝不可判定，绝不静默通过**。")
        sys.exit(2)
    if only_ep and only_ep not in [e.ep for e in episodes]:
        die(f"FAIL: --ep {only_ep} 不在配置集目内（配置：{', '.join(e.ep for e in episodes)}）", 2)

    counts = {"files": sum(len(e.prompt_files()) for e in episodes),
              "with_prompts": sum(1 for e in episodes if e.prompt_files())}
    if counts["files"] == 0:
        print(f"FAIL: {len(episodes)} 集目录内 **0 个 prompt 文件**（期望 `EPnn-prompts-<平台>.md` 或 `prompts-*.md`）"
              f"——无可检查制品＝不可判定（空跑不算通过）。")
        print("      先落盘逐集 prompt 制品（`EPnn/prompts/` 一平台一文件，见手册 §9.2），再跑本门控。")
        sys.exit(2)

    res = Result()
    if missing:
        for ep in missing:
            res.fail(ep, "D-S7", "配置声明的集在盘上找不到目录（集号 ↔ 目录对不上，跨集索引不可信）")
    check_ds1_duration(episodes, cfg, res, only_ep)
    check_ds2_anchors(episodes, cfg, res, only_ep)
    check_ds3_text_cards(episodes, cfg, res, only_ep)
    check_ds4_motifs(episodes, cfg, res, only_ep)
    check_ds5_hooks(episodes, cfg, res, only_ep)
    check_ds6_naming(episodes, cfg, res, only_ep)
    check_ds7_registry(episodes, cfg, res, only_ep)
    check_ds8_redlines(episodes, cfg, res, only_ep)

    scope = f"单集 {only_ep}" if only_ep else "全季 --season"
    if as_json:
        payload = {
            "scope": scope,
            "root": root,
            "config": cfg.get("_path"),
            "series_slug": cfg.get("series_slug"),
            "episodes": [e.ep for e in episodes],
            "missing_episodes": missing,
            "counts": counts,
            "fail": res.fails,
            "warn": res.warns,
            "note": res.notes,
            "summary": "FAIL" if res.fails else ("WARN" if res.warns else "PASS"),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        emit_text(root, episodes, cfg, res, scope, counts)

    if res.fails:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
