# audience-kg 知识索引（观众代言人）

> Pack：audience-kg · 角色：观众代言人 · Schema：`../schema.yaml`
> 权威正文来自科生团队沉淀（playbooks/agents/knowledge），本索引只存要点+原文路径，防改飘。
> 本领域无外部 API 可富集，内容来自团队沉淀；新知识由项目收尾萃取循环补充。

## 受众模式 AudienceMode

| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| 专家评审版 | AudienceMode | 技术驱动数据说话，直接切入科学问题，8-10min看细节。 | knowledge/templates/C-multi-audience-guide.md |
| 政府领导版 | AudienceMode | 国家战略高度切入，选最震撼3-5个数据，3-5min突出战略与效益。 | knowledge/templates/C-multi-audience-guide.md |
| 公众科普版 | AudienceMode | 反常识钩子/悬念起头，全术语翻译+大量类比，1-3min情感升华。 | knowledge/templates/C-multi-audience-guide.md |
| 学生青年版 | AudienceMode | 启发式展示前沿，激励性降低门槛，结尾招生态+展望。 | knowledge/templates/C-multi-audience-guide.md |
| 产业合作版 | AudienceMode | 痛点直击市场机会，商业指标+商务类比，结尾合作邀请。 | knowledge/templates/C-multi-audience-guide.md |

## 受众参数 AudienceParam

| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| 叙事策略 | AudienceParam | 同一份技术内容的整体讲法骨架（EXP技术驱动/PUB故事驱动/GOV成果导向）。 | knowledge/templates/C-multi-audience-guide.md |
| 开头钩子 | AudienceParam | 按模式选钩子：EXP切科学问题、PUB悬疑钩子、IND痛点直击。 | knowledge/templates/C-multi-audience-guide.md |
| 术语处理 | AudienceParam | 该保留/该翻译/该删除；PUB全翻口语+类比，GOV首现加3-6字注解。 | knowledge/templates/C-multi-audience-guide.md、agents/audience-advocate.md |
| 数据密度 | AudienceParam | EXP高每30秒≥2点、PUB低留1-2个；B2B只关心解决什么问题。 | knowledge/templates/C-multi-audience-guide.md |
| 类比用量 | AudienceParam | EXP极少、GOV适中、PUB大量每概念必配、STD较多。 | knowledge/templates/C-multi-audience-guide.md |
| 语气 | AudienceParam | EXP客观精炼、GOV大气有格局、PUB有趣温暖、STD激励低门槛。 | knowledge/templates/C-multi-audience-guide.md |
| 时长 | AudienceParam | EXP 8-10min、GOV 3-5min、PUB 1-3min、STD 3-5min、IND 2-4min。 | knowledge/templates/C-multi-audience-guide.md |
| 结尾策略 | AudienceParam | EXP指向后续研究、GOV强调效益就业、PUB情感升华、STD招生态、IND合作邀请。 | knowledge/templates/C-multi-audience-guide.md |

## 痛点链 ValueChain

| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| 痛点链结构 | ValueChain | 每个亮点串成任务→需求→亮点→证据，串不上就删。 | knowledge/痛点链.md、agents/audience-advocate.md |
| B2B问题停留 | ValueChain | B2B只为"能解决我什么问题"停留，参数堆砌被跳过。 | knowledge/痛点链.md、agents/audience-advocate.md |
| 套刻误差案例 | ValueChain | 套刻误差每小一纳米对光苛刻一分，所以必须又宽又稳（170–2500nm ±0.2%）。 | knowledge/痛点链.md |

## 证据类型与优先级 EvidenceType

| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| 真实测试曲线 | EvidenceType | 可直接入镜，信任度最高，工程师先看实测曲线与测试条件。 | knowledge/素材分级.md、playbooks/production-workflow.md、agents/audience-advocate.md |
| 实测光斑 | EvidenceType | 可直接入镜的真实实测证据。 | knowledge/素材分级.md、agents/audience-advocate.md |
| 真实装机场景 | EvidenceType | 可直接入镜，决策者看案例，信任度高。 | knowledge/素材分级.md、agents/audience-advocate.md |
| 概念CG | EvidenceType | 只作参考/延伸，信任度低于真实素材，AI只做延伸不替代。 | knowledge/素材分级.md、agents/audience-advocate.md |
| 真实素材优先 | EvidenceType | 真实素材优先；素材分可直接入镜/参考图/内容参考三级。 | knowledge/素材分级.md、playbooks/production-workflow.md、agents/audience-advocate.md |

## 留存监控规则 RetentionRule

| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| 第五秒钩子兑现 | RetentionRule | 第5秒开头钩子要兑现，不只靠开头留人。 | agents/audience-advocate.md |
| 中段尿点检查 | RetentionRule | 中段有没有尿点/注水段，前后密度要均衡。 | agents/audience-advocate.md |
| 结尾记忆点 | RetentionRule | 结尾观众记住什么，要有明确记忆点。 | agents/audience-advocate.md |
| 术语塌方检查 | RetentionRule | 陌生概念别超受众上限，公众版别叠生词、领导版别讲机制细节。 | agents/audience-advocate.md、knowledge/templates/C-multi-audience-guide.md |
| 一次看懂率 | RetentionRule | 第一遍不停下来重听能懂吗、不读字幕能看懂吗。 | agents/audience-advocate.md |

## 错位模式 MisalignmentPattern

| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| 自嗨 | MisalignmentPattern | 团队欣赏自己聪明，观众第10秒划走。 | agents/audience-advocate.md |
| 学生版申报腔 | MisalignmentPattern | 给学生版用申报腔，门槛高不激励；改激励性低门槛。 | agents/audience-advocate.md、knowledge/templates/C-multi-audience-guide.md |
| 专家版网络梗 | MisalignmentPattern | 给专家版用网络梗，专业度受损；改客观精炼数据说话。 | agents/audience-advocate.md、knowledge/templates/C-multi-audience-guide.md |
| 前30秒塞干货 | MisalignmentPattern | 前30秒塞完全部干货，后段时间注水密度失衡。 | agents/audience-advocate.md |
