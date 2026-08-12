# kesheng_skill — 科生：科研视频制作团队 Skill

多 agent 辩论会议驱动的科研/高精尖技术 **AI 视频制作团队** skill。不直接生成视频，交付专业团队水平的：制作方案、口播脚本、分镜表、逐镜 AI 视频 prompt（可灵/即梦/Vidu/海螺/Runway/万相/Seedance/LibTV），以及手把手制作流程。

## 目录结构

```
SKILL.md      入口：人设、科学准确铁律、五大里程碑工作流（简报→理解→方案→分镜+prompt→制作交付）
agents/       7 张角色卡：制片人 / 科学顾问 / 编剧 / 视觉导演 / prompt工程师 / 观众代言人 / 红队
protocols/    多 agent 辩论会议协议（盲提案→针锋相对→预注册标准裁决→制品交接）、质量门控
playbooks/    端到端制作流程、各平台 prompt 手册（含 Seedance 2.0/2.5 官方核实专章）、
              宫格分镜图技法（Image2 生图）、跨镜一致性工具箱
templates/    简报 / 方案 / 分镜表 / 会议纪要 / 项目拆分模板
knowledge/    工艺知识库：开头钩子、CTA、脚本模板、VI 视觉规范
kb/           科学知识图谱（Obsidian vault）：按领域组织，wiki-link 互联
```

## 使用

1. 整个文件夹放入 agent 环境的 user skills 目录（如 `~/.agents/skills/kesheng`）
2. 提出科研视频需求即触发：做方案、写脚本、出分镜表和逐镜 prompt
3. `kb/` 文件夹用 Obsidian 打开即得知识图谱（Graph View）

## 隐私约定

`kb/` 只收录公开通用科学知识。每个项目收尾时按 `kb/隐私红线.md` 做三分法分拣和脱敏检查——**项目专有信息（未公开数据、产品、技术路线、客户身份）绝不入库**。
