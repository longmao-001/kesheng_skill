# 红队知识图谱索引（redteam-kg）

> 科生科研视频制作团队 **红队** 领域知识图谱 Pack 的分组索引。
> 实体 | 类型 | 一句话 | 原文路径（与 `kg.json` 的 sources 一致）。
> 角色=红队；定位=制度性反对者与质量守门；内容来自团队沉淀，无外部 API 可富集，新知识由项目收尾萃取循环补充。

## 失败模式（FailureMode）

| 实体 | 类型 | 一句话 | 原文路径 |
| --- | --- | --- | --- |
| 科学错误 | FailureMode | 定量/因果表述错误、结论超出原论文主张 | agents/scientist.md |
| 数据无出处 | FailureMode | 定量数据须有出处，并带对比基准/样本量/显著性 | agents/scientist.md；protocols/quality-gate.md |
| 编造伪造数据 | FailureMode | 绝不留编造；不确定标待确认 | agents/scientist.md；protocols/quality-gate.md |
| PPT式视频 | FailureMode | 只写『缓慢推近』的匀速单运镜=不合格 | knowledge/动感三来源.md；playbooks/platform-prompts.md；agents/director.md |
| 超载prompt | FailureMode | 一个prompt里多主体/多动作/三个以上运镜 | agents/prompt-engineer.md；playbooks/platform-prompts.md |
| 标题党 | FailureMode | 钩子和正文脱节=欺骗红线 | agents/screenwriter.md；protocols/quality-gate.md |
| 图文脱节 | FailureMode | 旁白讲A画面演B；视觉噱头冲掉科学信息 | agents/director.md |
| 术语塌方 | FailureMode | 公众版连续两个未解释的术语；领导版讲机制细节 | agents/audience-advocate.md；agents/screenwriter.md |
| 自嗨 | FailureMode | 团队在欣赏自己的聪明，观众却在第10秒划走 | agents/audience-advocate.md |
| 密度失衡 | FailureMode | 前30秒塞完全部干货，后2分钟注水 | agents/audience-advocate.md；protocols/quality-gate.md |
| 节奏事故 | FailureMode | 单镜头>10秒；连续3个同景别；没有远景锚定就切特写 | agents/director.md；protocols/quality-gate.md |
| 抽象词 | FailureMode | 『电影感』『高级感』『震撼』等抽象词 | agents/prompt-engineer.md；playbooks/platform-prompts.md |
| 平台错配 | FailureMode | 把Runway英文句式丢进即梦；运镜指令没放开头 | agents/prompt-engineer.md；playbooks/platform-prompts.md |
| 图生视频复述画面 | FailureMode | I2V的prompt复述画面内容 | agents/prompt-engineer.md；playbooks/platform-prompts.md |
| 不可制作 | FailureMode | 精确结构走纯文生视频路线；单镜塞3个动作 | agents/director.md |
| 陈词滥调 | FailureMode | 『蓝色粒子汇聚成DNA』『科学家低头看显微镜』假笑 | agents/director.md |
| 无聊 | FailureMode | 开头平淡、段落没有推进感、结尾没有记忆点 | agents/screenwriter.md |
| 混乱 | FailureMode | 主线不清、信息堆砌、类比之间打架 | agents/screenwriter.md |
| 错位 | FailureMode | 给学生版用申报腔；给专家版用网络梗 | agents/audience-advocate.md |
| 需求错位 | FailureMode | 用户真正要的和正在做的不是同一件事 | agents/red-team.md；agents/audience-advocate.md；protocols/quality-gate.md |
| 开头无钩子 | FailureMode | 前5秒无钩子 | protocols/quality-gate.md |
| 配音歧义读音 | FailureMode | 术语发音错误、无歧义读音 | protocols/quality-gate.md |
| 品牌不一致 | FailureMode | 不符合选定VI规范 | protocols/quality-gate.md |
| 总时长超限 | FailureMode | 不符合模板/简报要求 | protocols/quality-gate.md |
| 错误因果 | FailureMode | 因果链不成立；类比暗示了错误的因果 | agents/scientist.md；agents/red-team.md |

## 禁忌与红线（Taboo）

| 实体 | 类型 | 一句话 | 原文路径 |
| --- | --- | --- | --- |
| 品牌禁区 | Taboo | 不符合选定VI规范=硬性违规 | protocols/quality-gate.md |
| 平台审核红线 | Taboo | 真人脸参考图会被审核直接拦截 | playbooks/platform-prompts.md；protocols/quality-gate.md |
| 数据与文字水印交给AI生成 | Taboo | 参数/曲线/表格/logo/字幕绝不交给AI生成 | agents/prompt-engineer.md；agents/director.md；protocols/quality-gate.md |
| 夸大疗效 | Taboo | 夸大疗效、夸大能力、误导公众的表述 | agents/red-team.md；protocols/quality-gate.md |
| 误导性类比 | Taboo | 类比有误导性；翻译牺牲准确性 | agents/scientist.md；protocols/quality-gate.md |

## 检查维度（CheckDimension）

| 实体 | 类型 | 一句话 | 原文路径 |
| --- | --- | --- | --- |
| 画面相关性 | CheckDimension | 分镜画面与文稿≥80%匹配 | protocols/quality-gate.md |
| 配音准确度 | CheckDimension | 术语发音正确、无歧义读音 | protocols/quality-gate.md |
| 节奏感 | CheckDimension | 单镜头≤10秒 | protocols/quality-gate.md |
| 镜头动感 | CheckDimension | 无PPT式视频：每镜有变速/复合运镜或画面内部运动 | protocols/quality-gate.md；agents/director.md |
| 信息密度 | CheckDimension | ≥3个信息点/分钟 | protocols/quality-gate.md |
| 开头吸引力 | CheckDimension | 前5秒有钩子 | protocols/quality-gate.md |
| 品牌一致性 | CheckDimension | 符合选定VI规范 | protocols/quality-gate.md |
| 总时长 | CheckDimension | 符合模板/简报要求 | protocols/quality-gate.md |

## 攻击视角（AttackAngle）

| 实体 | 类型 | 一句话 | 原文路径 |
| --- | --- | --- | --- |
| 科学风险 | AttackAngle | 如果审稿专家看到这条视频，哪个表述会被挂？ | agents/red-team.md |
| 传播风险 | AttackAngle | 如果这条视频没火，最可能死在哪一秒？ | agents/red-team.md |
| 制作风险 | AttackAngle | 哪个镜头最可能生成翻车？翻车了整个方案受多大影响？ | agents/red-team.md |
| 甲方风险 | AttackAngle | 用户真正要的和我们正在做的，是不是同一件事？ | agents/red-team.md |
| 伦理合规 | AttackAngle | 有没有夸大疗效、夸大能力、误导公众的表述？ | agents/red-team.md |

## 闸点（GateCheckpoint）

| 实体 | 类型 | 一句话 | 原文路径 |
| --- | --- | --- | --- |
| M4前置拦截闸 | GateCheckpoint | 硬性违规：科学错误/伪造数据/无出处/品牌禁区/平台审核红线/数据画面交给AI生成 | protocols/quality-gate.md；agents/red-team.md |
| M5出口评审闸 | GateCheckpoint | 七维检查表+里程碑验收清单+预注册标准 | protocols/quality-gate.md |

## 反对纪律（RebuttalRule）

| 实体 | 类型 | 一句话 | 原文路径 |
| --- | --- | --- | --- |
| 引用预注册标准 | RebuttalRule | 每个反对引用Phase 0预注册的评审标准（『按钩子强度标准，这个方案……』） | agents/red-team.md；protocols/quality-gate.md |
| 禁止每点必杠 | RebuttalRule | 只打要害，一场会议提出1-3个最致命的反对 | agents/red-team.md |
| 给出推翻条件 | RebuttalRule | 每条反对必须给出推翻条件（『如果……我就撤回这条反对』） | agents/red-team.md；protocols/quality-gate.md |
| 只评制品不评人 | RebuttalRule | 攻击方案不攻击角色；只谈制品不谈动机；只评制品不评人 | agents/red-team.md；protocols/quality-gate.md |
| 少数派报告必须留档 | RebuttalRule | 即使被裁决否决，反对意见也必须原样记录在案，不许被和稀泥抹掉 | agents/red-team.md；protocols/quality-gate.md |
| 事实性争议不折中 | RebuttalRule | 事实性争议不折中，查证或升级 | protocols/quality-gate.md |
| 辩论最后发言 | RebuttalRule | 辩论中永远最后发言，听完所有人再开火 | agents/red-team.md |
| 逐场轮换视角 | RebuttalRule | 逐场轮换：科学风险/传播风险/制作风险/甲方风险/伦理合规 | agents/red-team.md |

