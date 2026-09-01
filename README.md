# kesheng_skill — 科生：科研视频制作团队 Skill（多 agent 协作版 v2）

多 agent 编排驱动的科研/高精尖技术 **AI 视频制作团队** skill。不直接生成视频，交付专业团队水平的：制作方案、口播脚本、分镜表、逐镜 AI 视频 prompt（可灵/即梦/Vidu/海螺/Runway/万相/Seedance/LibTV），以及手把手制作流程。

**v2 变化**：从"单 agent 扮演全部角色"重构为**按真实影视剧组建制的真多 agent 协作**——制片人（主 agent）编排，导演/编剧/分镜师/美术指导/摄影指导/声音设计师/剪辑师/科学顾问/prompt 工程师/观众代言人/红队以独立 subagent 并行作业、黑板式制品交接、红队双闸门控；并配**统一知识图谱**（并集 KG + 11 个 domain 分区 + `kg_query.py` 查询接口）。设计依据见 `docs/DESIGN.md`（含 8 种多 agent 方法对比与选型）。

## 目录结构

```
SKILL.md       入口：人设、科学准确铁律、五大里程碑工作流、团队编制、执行模式 v2（默认真多 agent 编排）
agents/        7 张角色卡（带独立 agent 工作规范头，可直接作为 subagent prompt 主体）
protocols/     meeting.md v3（多 agent 会议与协作协议）、quality-gate.md（三态门控协议）
playbooks/     端到端制作流程、各平台 prompt 手册（含 Seedance 2.0/2.5 官方核实专章）、
               宫格分镜图技法（Image2 生图）、跨镜一致性工具箱
templates/     简报 / 方案 / 分镜表 / 会议纪要 / 项目拆分 / handoff📤交接块规范
knowledge/     工艺知识库：开头钩子、CTA、脚本模板、VI 视觉规范
kb/            科学知识图谱（Obsidian vault）：按领域组织，wiki-link 互联
orchestration/ v2 新增：ORCHESTRATION.md 编排手册（工具映射/派活模板/降级规则）、
               kesheng_workflow.js + .meta.json 全自动多 agent fan-out 脚本
docs/          v2 新增：DESIGN.md 多方法调研与架构设计
packs/         v2 新增：统一知识图谱（并集KG+分区domain）——kesheng-kg/kg.json +
               kg_query.py 查询接口 + 6 个域片段目录（科学/叙事/视觉/prompt/受众/红队）
scripts/       v2 新增：build_union_kg.py 域片段→总图合并脚本
runs/          v2 新增：项目工坊（黑板）目录约定，每项目一文件夹
```

## 使用（多 agent 模式）

1. 整个文件夹已装入 agent 环境的 user skills 目录（`~/.dsh/skills/kesheng`）。
2. 提出科研视频需求即触发：制片人先定档（S/M/L）→ 简报卡+预注册标准 → 按 `orchestration/ORCHESTRATION.md` 派活。
3. **默认关卡式**：每里程碑派 parallel subagent（M2 调研 3-5 路 / M3 盲提案+质询 / M4 prompt 分段转写），关键处停下请用户确认。
4. **全自动模式**：用户说"全自动跑完"时，用 DSH `workflow` 工具跑 `orchestration/kesheng_workflow.js`（args: topic/runDir/platform/audienceMode/withCouncil）。
5. `kb/` 文件夹用 Obsidian 打开即得知识图谱（Graph View）。

### 快速上手（制片人节奏）

```
开工 → todo_write 清单 → 定档 → 简报卡+预注册标准 → 用户确认
→ M2 并行3路调研 → L2检查 → M3 盲提案3路 → 质询3路(+红队) → 裁决+纪要 → 用户确认
→ M4 口播→分镜→prompt分段并行 → 科学复核 → 红队前置闸 → 用户确认
→ M5 陪跑出片 → 红队出口闸(≤2循环) → 用户签收 → kb萃取
```

## 隐私约定

`kb/` 只收录公开通用科学知识。每个项目收尾时按 `kb/入库规则.md`（收录门槛与流程，唯一权威版）和 `kb/隐私红线.md`（三分法分拣与脱敏检查）执行——**项目专有信息（未公开数据、产品、技术路线、客户身份）绝不入库**。
