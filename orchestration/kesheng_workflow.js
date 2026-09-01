// 科生 · 科研视频制作 全自动多 agent fan-out (DeepSeek Harness workflow 脚本体)
// 用法: DSH workflow 工具 — script=本文件内容, meta=同目录 kesheng_workflow.meta.json, args 见下。
//
// args = {
//   topic:        "基因编辑",                 // 必填: 项目主题/一句需求
//   runDir:       "f:/AI/kesheng/runs/20260901-基因编辑",  // 必填: 预建工坊目录(黑板)
//   platform:     "可灵",                    // 可选: 目标AI视频工作台 (默认 可灵)
//   audienceMode: "PUB",                     // 可选: EXP/GOV/PUB/STD/IND (默认 PUB)
//   withCouncil:  true                       // 可选: M3 是否开全面质询+红队 (默认 true)
// }
//
// 注意: 本脚本只跑"并行干活+串行交接", 不做最终裁决; 制片人(主agent)读返回摘要后
// 执行: ① 复核 m3-proposal.md 并与用户走关卡 ② 出口闸打回循环(≤2) ③ 导演定剪意见
// ④ 交付后按 kb/入库规则.md 做知识萃取。

const T   = args.topic;
const R   = args.runDir;
const PL  = args.platform || "可灵";
const AM  = args.audienceMode || "PUB";
const CL  = args.withCouncil !== false;

if (!T || !R) throw new Error("args 必须含 topic 和 runDir");

const KES = "f:/AI/kesheng";
const ROLE_DOMAIN = {
  "科学顾问": "科学", "观众代言人": "受众", "导演": "导演", "编剧": "叙事",
  "分镜师": "分镜", "摄影指导": "影像", "声音设计师": "声音",
  "剪辑师": "剪辑", "prompt 工程师": "prompt", "红队": "红队"
};
const dom = (role) => ROLE_DOMAIN[role.replace(/\(.*\)/, "").trim()] || "";
const head = (role, card, upstream) =>
  `你被指派为「科生」团队的${role}。你是独立上下文的 subagent，看不到主会话，只以黑板文件和本提示为事实来源。` +
  `开工三步: ① read 读 ${KES}/agents/${card} 作为角色卡并遵循其全部指令, 再运行 python ${KES}/packs/kg_query.py --domain ${dom(role)} <关键词> 查知识图谱, 按需 read 它引用的资源文件(playbooks/knowledge/kb), 不要一次性全读 ` +
  `② read 读 ${R}/brief.md (项目简报+预注册标准+档位) ③ 读上游📤: ${upstream} ` +
  `任务:`;
const tail = (role, fname, note) =>
  `\n输出要求: 完整产出写入 ${R}/${fname}; 末尾必须有「## 📤 传递给下游 (@制片人)」块(templates/handoff.md 格式); 分段落盘(每节完成即写盘); ` +
  `科学准确铁律: 数据有出处/不确定标"待确认"/绝不编造。${note || ""}`;

phase("A. M2 并行调研: 科学理解 + 受众语境 + 导演艺术基调");
const resA = (await parallel([
  () => agent(
    head("科学顾问", "scientist.md", `${R}/brief.md`) +
    `\n对「${T}」执行 7 步深度理解法(先查 ${KES}/kb 知识图谱), 输出理解报告+深度等级自评(L2为底线)+待确认清单。` +
    tail("科学顾问", "scientist-理解报告.md", "域: 科学"),
    { label: "🔬科学顾问", phase: "A. M2 并行调研" }
  ),
  () => agent(
    head("观众代言人", "audience-advocate.md", `${R}/brief.md`) +
    `\n按受众模式 ${AM} 输出受众语境与证据映射: 受众消费场景/最先看的指标/证据可视化优先清单/痛点链初稿。` +
    tail("观众代言人", "audience-受众模型.md", "域: 受众"),
    { label: "👁观众代言人", phase: "A. M2 并行调研" }
  ),
  () => agent(
    head("导演", "director.md", `${R}/brief.md`) +
    `\n做艺术基调与可拍性调研: 导演阐述雏形(主题一句话/风格关键词/全片节奏曲线/镜头语汇候选)+需要首帧图的结构清单。` +
    tail("导演", "director-艺术基调调研.md", "域: 导演"),
    { label: "🎬导演", phase: "A. M2 并行调研" }
  )
])).filter(Boolean);
log(`阶段A完成: ${resA.length} 路产出`);

phase("B. M3 盲独立提案 (并行×4, 上下文隔离)");
const blind = (role, card, angle) =>
  head(role, card, `${R}/brief.md + ${R}/scientist-理解报告.md(如存在)`) +
  `\n【盲提案】不要读任何其他提案文件, 以 ${angle} 视角独立产出一份完整制作方案提案(结构用 ${KES}/templates/proposal.md): 定位/受众/文案要点/分镜概览/执行计划。` +
  tail(role, `proposals/${role}-盲提案.md`, `若无法确定科学数据出处, 标"待确认", 绝不编造。`);

const resB = (await parallel([
  () => agent(blind("编剧", "screenwriter.md", "叙事与口播稿角度"),
    { label: "✍️编剧", phase: "B. M3 盲提案" }),
  () => agent(blind("分镜师", "storyboard-artist.md", "分镜画面序列角度"),
    { label: "📽️分镜师", phase: "B. M3 盲提案" }),
  () => agent(blind("摄影指导", "dop.md", "影像质感/运镜/拍法角度"),
    { label: "🎥摄影指导", phase: "B. M3 盲提案" }),
  () => agent(blind("导演", "director.md", "全片艺术基调与节奏角度"),
    { label: "🎬导演", phase: "B. M3 盲提案" })
])).filter(Boolean);
log(`阶段B完成: ${resB.length} 份盲提案`);

let critArr = [];
if (CL) {
  phase("C. M3 交叉质询 (并行×4) + 红队");
  const others = (me) =>
    ["编剧", "分镜师", "摄影指导", "导演"]
      .filter(r => r !== me)
      .map(r => `proposals/${r}-盲提案.md`);
  cond = null; // noop
  const critiqueFor = (me) =>
    `你是独立质询 agent。只读 ${R}/brief.md 与其他三份提案(${others(me).join(" + ")}), 按预注册标准逐条打分析议: ` +
    `每份: ①最强可采纳点 ②按标准编号的反驳 ③与你的整合建议。写入 ${R}/m3-critiques/${me}-质询.md。` +
    `\n规则: 有原则的针锋相对, 禁止每点必杠; 反对必须给推翻条件。`;
  critArr = (await parallel([
    () => agent(critiqueFor("编剧"), { label: "✍️质询", phase: "C. M3 交叉质询" }),
    () => agent(critiqueFor("分镜师"), { label: "📽️质询", phase: "C. M3 交叉质询" }),
    () => agent(critiqueFor("摄影指导"), { label: "🎥质询", phase: "C. M3 交叉质询" }),
    () => agent(critiqueFor("导演"), { label: "🎬质询", phase: "C. M3 交叉质询" }),
    () => agent(
      `你是「科生」红队(角色卡 ${KES}/agents/red-team.md)。只读 ${R}/brief.md + proposals/ 下四份提案 + m3-critiques/ 下质询(如存在)。` +
      `输出 1-3 条最致命反对(每条: 攻击点/依据的标准编号/推翻条件), 写入 ${R}/m3-critiques/red-team-致命反对.md。` +
      tail("红队", "m3-critiques/red-team-致命反对.md", "域: 红队"),
      { label: "🔴红队", phase: "C. M3 交叉质询" }
    )
  ])).filter(Boolean);
  log(`阶段C完成: 质询+红队 ${critArr.length} 路`);
}

phase("D. M3 导演整合 (总方案 v1)");
const proposal = await agent(
  head("导演(整合)", "director.md", `${R}/brief.md + proposals/ 下全部提案${CL ? " + m3-critiques/" : ""}`) +
  `\n以导演视角按预注册标准逐条打分, 整合四份盲提案出执行方案 v1(合并/取舍写明理由与艺术基调依据), 写入 ${R}/m3-proposal.md; 同时输出会议纪要要素(决议/被否方案/异议/未决风险)到 ${R}/decision-log-m3.md。` +
  tail("导演(整合)", "m3-proposal.md", `事实争议不许折中: 标"待确认"并列为升级项。`),
  { label: "🎬导演整合", phase: "D. M3 导演整合" }
);

phase("E. M4 口播稿");
const script = await agent(
  head("编剧", "screenwriter.md", `${R}/m3-proposal.md + ${R}/brief.md`) +
  `\n按定稿方案产出完整口播稿 v2: 钩子(前5秒)/意义建立/核心内容/情感收尾/CTA; 每段≤10秒约40字; 术语首次出现必须解释(受众模式 ${AM} 例外规则见角色卡)。写入 ${R}/screenwriter-口播稿.md。` +
  tail("编剧", "screenwriter-口播稿.md", "域: 叙事"),
  { label: "✍️口播稿", phase: "E. M4 口播稿" }
);

phase("F. M4 分镜表 ‖ 声音方案 (并行)");
const board = (await parallel([
  () => agent(
    head("分镜师", "storyboard-artist.md", `${R}/screenwriter-口播稿.md + ${R}/brief.md`) +
    `\n把口播稿转成分镜表(${KES}/templates/storyboard.md 格式): 单镜3-10s/景别构图/镜头间动势衔接(运镜列待摄影指导合议, 你填镜头内容与构图)/需要首帧图的结构镜头标注/视觉隐喻设计。写入 ${R}/storyboard-分镜表.md。` +
    `\n同时把全片按 2-6 个自然段切分返回 JSON: {"sections":[{"id":"sec-01","shotRange":"镜头1-5"}]}` +
    tail("分镜师", "storyboard-分镜表.md", "域: 分镜"),
    {
      label: "📽️分镜表", phase: "F. M4 分镜表",
      schema: {
        type: "object",
        properties: {
          sections: {
            type: "array",
            items: { type: "object", properties: { id: { type: "string" }, shotRange: { type: "string" } }, required: ["id", "shotRange"], additionalProperties: false }
          }
        },
        required: ["sections"], additionalProperties: true
      }
    }
  ),
  () => agent(
    head("声音设计师", "sound-designer.md", `${R}/screenwriter-口播稿.md + ${R}/brief.md`) +
    `\n产出声音方案: BGM 情绪曲线(起/落/留白)+曲风关键词与商用素材库方向/音效清单(环境/拟音/转场/UI)/配音建议(音色/语速/术语发音检查)+卡点建议。写入 ${R}/sound-声音方案.md。` +
    tail("声音设计师", "sound-声音方案.md", "域: 声音"),
    { label: "🔊声音设计师", phase: "F. M4 分镜表" }
  )
])).filter(Boolean);
const storyboard = board[0];
log(`阶段F完成: 分镜表+声音方案 ${board.length} 路`);

const sections = (storyboard && Array.isArray(storyboard.sections) ? storyboard.sections : []).slice(0, 6);
log(`分镜完成: ${sections.length} 个分段`);

phase("G. M4 摄影方案");
const dopRes = await agent(
  head("摄影指导", "dop.md", `${R}/storyboard-分镜表.md + ${R}/brief.md`) +
  `\n产出摄影方案: 每镜运镜设计(≤2运镜必带变速/复合)+光影氛围+拍法路线(T2V/I2V/首尾帧/参考)+参考资产需求+首尾帧衔接链; 与分镜师合议运镜列, 把方案写入 ${R}/dop-摄影方案.md。` +
  tail("摄影指导", "dop-摄影方案.md", "域: 影像"),
  { label: "🎥摄影方案", phase: "G. M4 摄影方案" }
);

phase("H. M4 prompt 分段转写 (并行) ‖ 剪辑预计划");
const resH = await parallel([
  () => pipeline(sections,
    (prev, sec) => agent(
      head("prompt 工程师", "prompt-engineer.md", `${R}/storyboard-分镜表.md + ${R}/dop-摄影方案.md + ${R}/brief.md`) +
      `\n负责分段 ${sec.id} (${sec.shotRange}): 为段内每镜撰写 ${PL} 平台 prompt(公式/风格token块/负面prompt/参考图需求/时长档/抽卡建议), 对照 ${KES}/playbooks/platform-prompts.md。写入 ${R}/m4-prompts/${sec.id}.md。` +
      tail("prompt 工程师", `m4-prompts/${sec.id}.md`, "域: prompt"),
      { label: `🔤${sec.id}`, phase: "H. M4 prompt 转写" }
    )
  ),
  () => agent(
    head("剪辑师", "editor.md", `${R}/storyboard-分镜表.md + ${R}/sound-声音方案.md + ${R}/brief.md`) +
    `\n产出剪辑预计划: 节奏曲线建议/转场策略/字幕与图表层工作量/文案层压字/调色LUT建议。写入 ${R}/editor-剪辑预计划.md。` +
    tail("剪辑师", "editor-剪辑预计划.md", "域: 剪辑"),
    { label: "✂️剪辑师", phase: "H. M4 prompt 转写" }
  )
]);
log(`阶段H完成: prompt ${(resH[0] || []).length} 段 + 剪辑预计划`);

phase("I. M4 红队前置闸: 硬性违规筛查");
const preGate = await agent(
  `你是「科生」红队(角色卡 ${KES}/agents/red-team.md), 执行前置拦截闸。只读 ${R}/brief.md + storyboard-分镜表.md + dop-摄影方案.md + m4-prompts/ 下全部段, 只查硬性违规: 科学错误/伪造数据/无出处表述/品牌禁区/平台审核红线/数据画面交给AI生成。逐条列出(镜头号+问题+修改要求), 写入 ${R}/m4-gate-red.md。`,
  {
    label: "🔴前置闸", phase: "I. M4 红队前置闸",
    schema: {
      type: "object",
      properties: {
        pass: { type: "boolean" },
        blockers: { type: "array", items: { type: "string" } }
      },
      required: ["pass", "blockers"], additionalProperties: true
    }
  }
);

phase("J. M5 出口评审闸 (独立上下文 Reviewer)");
const exitGate = await agent(
  `你是未参与本片创作的独立 Reviewer 审稿人(角色卡 ${KES}/agents/red-team.md 视角, 只读黑板, 不听任何角色辩护)。` +
  `读 ${R}/brief.md + m3-proposal.md + storyboard-分镜表.md + screenwriter-口播稿.md + sound-声音方案.md + m4-prompts/ 全部段, ` +
  `按 ${KES}/protocols/quality-gate.md 的七维检查表+里程碑验收清单逐项过: 画面相关/节奏(≤10s)/动感/信息密度(≥3点每分)/钩子/品牌/总时长/科学准确。` +
  `输出评分单(每项0.0-1.0+一句理由)与 3 条最尖锐批评, 写入 ${R}/m5-gate-red.md。`,
  {
    label: "🔴出口闸", phase: "J. M5 出口评审闸",
    schema: {
      type: "object",
      properties: {
        verdict: { type: "string", enum: ["PASS", "CONDITIONAL", "BLOCK"] },
        score: { type: "number" },
        topIssues: { type: "array", items: { type: "string" } }
      },
      required: ["verdict", "score", "topIssues"], additionalProperties: true
    }
  }
);

return {
  topic: T, runDir: R, platform: PL, audienceMode: AM,
  m2: resA.length, m3_proposals: resB.length, m3_council: critArr.length,
  m3_proposal_ok: !!proposal, script_ok: !!script,
  storyboard_ok: !!storyboard, dop_ok: !!dopRes,
  sections: sections.length, prompts_ok: (resH[0] || []).length,
  editor_ok: !!resH[1], preGate: preGate || null, exitGate: exitGate || null,
  note: "制片人(主agent)下一步: ①复核m3-proposal.md并对标brief定稿 ②走用户关卡(ask_user_question) ③exitGate=BLOCK/CONDITIONAL时按m5-gate-red.md打回对应环节(≤2循环) ④导演定剪意见 ⑤交付后按kb/入库规则.md做知识萃取。"
};
