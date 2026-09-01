# prompt-kg · 知识库索引

> 科生科研视频团队「prompt 工程师」领域知识包。按实体类型分组；「原文路径」与 `kg.json` 中 `sources` 一致。
> 全部内容沉淀自团队内部 playbooks/ knowledge/ agents/；本领域无外部API可富集，新知识由项目收尾萃取循环补充。

涉及文件（相对 F:/AI/kesheng/）：
`playbooks/platform-prompts.md`、`knowledge/seedance-template-library.md`、`knowledge/prompt-reverse.md`、`playbooks/consistency.md`、`knowledge/camera-language.md`、`agents/prompt-engineer.md`、`playbooks/storyboard-grid.md`

---

## Platform · AI视频工作台

| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| Platform:可灵 | Platform | 快手AI视频工作台，文生/图生+独立负面prompt字段，相机控制六轴[-10,10]+MotionBrush | playbooks/platform-prompts.md; knowledge/prompt-reverse.md |
| Platform:即梦 | Platform | Seedance引擎工作台，运镜公式、智能多帧≤10帧、全能参考@≤12个，Seedream4.5联动 | playbooks/platform-prompts.md; knowledge/prompt-reverse.md |
| Platform:Vidu | Platform | 招牌参考生视频，上传角色/道具参考图prompt只写新动作新场景，多图首尾帧 | playbooks/platform-prompts.md; playbooks/consistency.md |
| Platform:海螺 | Platform | MiniMax Director模型，运镜指令必须放prompt最开头方括号最多2条 | playbooks/platform-prompts.md; knowledge/prompt-reverse.md |
| Platform:Runway | Platform | Gen-3/4英文，`[camera movement]: [establishing scene]. [additional details]`，Gen-4 References | playbooks/platform-prompts.md; knowledge/prompt-reverse.md |
| Platform:通义万相 | Platform | 官方7要素词典按要素组装，首尾帧API传首尾帧图prompt只写运动 | playbooks/platform-prompts.md; knowledge/prompt-reverse.md |
| Platform:Seedance | Platform | 火山引擎(即梦Pro/LibTV后端)，2.0/2.5版本差异，@引用与多镜分镜模板 | playbooks/platform-prompts.md; knowledge/prompt-reverse.md |
| Platform:LibTV | Platform | LiblibAI节点画布工作流，剧本→分镜→视频节点，分镜图作首帧参考 | playbooks/platform-prompts.md |
| Platform:智谱清影 | Platform | 主体+场景+运动基础式可叠美学控制，结构最简单适合快速验证 | knowledge/prompt-reverse.md |
| Platform:Sora | Platform | 自然语言懂电影术语，最长60s，Sora Storyboard多镜+角色/cameo | knowledge/prompt-reverse.md; playbooks/consistency.md |
| Platform:Veo3 | Platform | 5块结构(camera/subject/action/setting/audio)，原生音频，每段迭代只改一块 | knowledge/prompt-reverse.md |

## ImageGenTool · 生图工具

| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| ImageGenTool:GPT Image 2 | ImageGenTool | 宫格分镜生图首选：指令遵循强/中文小字渲染好/出2K/单格用"继续编辑"只重画 | playbooks/storyboard-grid.md |
| ImageGenTool:Nano Banana 2 | ImageGenTool | 备选，"底图扩九宫格"玩法最流行，彩色网格直出效果好 | playbooks/storyboard-grid.md |
| ImageGenTool:Seedream 4.5 | ImageGenTool | 备选(即梦图片)，多图一致性9宫格五官近零偏差，与Seedance联动最顺 | playbooks/storyboard-grid.md |

## PromptFormula · 平台 prompt 公式

| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| PromptFormula:通用公式 | PromptFormula | 主体+动作/运动+场景+镜头语言(景别+运镜+视角)+光影+风格/氛围，一句连贯自然的话 | playbooks/platform-prompts.md; agents/prompt-engineer.md |
| PromptFormula:可灵文生视频公式 | PromptFormula | 主体(主体描述)+运动+场景(场景描述)+(镜头语言+光影+氛围) | playbooks/platform-prompts.md |
| PromptFormula:可灵图生视频公式 | PromptFormula | 主体+运动，背景+运动；只写运动，不复述画面 | playbooks/platform-prompts.md; agents/prompt-engineer.md |
| PromptFormula:即梦运镜公式 | PromptFormula | 【运镜】+【节奏/速度】+【景别/角度】+【主体/场景】+【画质/氛围】，运镜放前≤2-3个 | playbooks/platform-prompts.md |
| PromptFormula:Vidu公式 | PromptFormula | 主体+场景细节+镜头运镜+动态效果+风格氛围；参考生视频只写新动作新场景 | playbooks/platform-prompts.md |
| PromptFormula:海螺公式 | PromptFormula | 【推进，轻微上升】+画面+显微摄影质感/暗场照明/风格；运镜必须放最开头 | playbooks/platform-prompts.md |
| PromptFormula:Runway公式 | PromptFormula | `[camera movement]: [establishing scene]. [additional details]`，英文 | playbooks/platform-prompts.md |
| PromptFormula:通义万相公式 | PromptFormula | 按官方7要素(景别/视角/镜头/运镜/速率/氛围/风格)组装，首尾帧只写运动 | playbooks/platform-prompts.md |
| PromptFormula:Seedance时间轴分镜公式 | PromptFormula | 风格+时间轴逐段[镜头+画面+动作+特效]+声音+参考，多镜一次成片 | knowledge/seedance-template-library.md; playbooks/platform-prompts.md |
| PromptFormula:Seedance多镜写法 | PromptFormula | 素材指代→一句话概述→分镜逐段→贯穿性约束收口；2.0用镜头N序号、2.5用时间戳 | playbooks/platform-prompts.md |
| PromptFormula:Image2五段式生图公式 | PromptFormula | 比例/风格/逐格镜头/视觉规范/底部信息栏五段，写死3列x3行共9格 | playbooks/storyboard-grid.md |

## MoveTerm · 运镜词表

| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| MoveTerm:推(dolly-in) | MoveTerm | 推=dolly-in/push in，建立紧张聚焦，戏剧性揭示/开场建立 | playbooks/platform-prompts.md; knowledge/camera-language.md |
| MoveTerm:拉(dolly-out) | MoveTerm | 拉=dolly-out/pull out，释然交代全貌，收尾/环境规模 | playbooks/platform-prompts.md; knowledge/camera-language.md |
| MoveTerm:环绕(orbit) | MoveTerm | 环绕=orbit/360° arc，英雄时刻全方位审视，产品展示/人物高光 | playbooks/platform-prompts.md; knowledge/camera-language.md |
| MoveTerm:跟(follow/tracking) | MoveTerm | 跟=follow/tracking，陪伴感行动感，角色行进/低机位跟拍 | playbooks/platform-prompts.md; knowledge/camera-language.md |
| MoveTerm:希区柯克变焦(dolly-zoom) | MoveTerm | 希区柯克变焦=dolly-zoom，眩晕心理冲击，震惊瞬间/转折揭示 | playbooks/platform-prompts.md; knowledge/camera-language.md |
| MoveTerm:手持(handheld) | MoveTerm | 手持=handheld，纪实紧迫亲密，纪录片感/UGC真实感 | playbooks/platform-prompts.md; knowledge/camera-language.md |
| MoveTerm:FPV穿越(FPV flythrough) | MoveTerm | FPV穿越=FPV flythrough，沉浸速度探索，第一人称/穿空间 | playbooks/platform-prompts.md; knowledge/camera-language.md |
| MoveTerm:一镜到底(single take/oner) | MoveTerm | 一镜到底=single take/oner，无缝连续沉浸 | playbooks/platform-prompts.md |
| MoveTerm:变速(速度修饰) | MoveTerm | 缓慢/匀速/急速 + 由快到缓/骤然放缓/急停悬停，单镜≤2运镜但用变速+复合 | playbooks/platform-prompts.md; knowledge/camera-language.md; knowledge/prompt-reverse.md |

## GenerateRoute · 生成路线

| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| GenerateRoute:文生视频 | GenerateRoute | 从零纯文字生成，无首帧约束，需公式+风格token块+具体名词 | playbooks/platform-prompts.md; agents/prompt-engineer.md |
| GenerateRoute:图生视频I2V | GenerateRoute | 先生成正确静帧→科学顾问验收→图生视频，prompt只写运动画面交给首帧 | playbooks/consistency.md; playbooks/platform-prompts.md; agents/prompt-engineer.md |
| GenerateRoute:首尾帧 | GenerateRoute | 传首帧+尾帧图prompt只写运动，保持同场景同构图只改一个元素 | playbooks/platform-prompts.md; playbooks/consistency.md |
| GenerateRoute:参考生视频 | GenerateRoute | 上传角色/道具/场景参考图prompt只写新动作新场景，Vidu招牌/Seedance全能参考 | playbooks/platform-prompts.md; playbooks/consistency.md |
| GenerateRoute:宫格整图一次成片 | GenerateRoute | 宫格图作参考图整图演绎成一段视频，写明"按从左到右从上到下顺序演绎" | playbooks/storyboard-grid.md |
| GenerateRoute:宫格切片逐格首帧 | GenerateRoute | 宫格图切逐格当首帧进图生视频，AI提取单格重绘，线稿首帧prompt写彩色风格 | playbooks/storyboard-grid.md |

## StyleTokenRule · 风格 token 规则

| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| StyleTokenRule:风格token块 | StyleTokenRule | 全片写死一句风格描述逐字粘贴进每镜prompt，跨平台带英文版 | playbooks/consistency.md; agents/prompt-engineer.md; knowledge/prompt-reverse.md |
| StyleTokenRule:双锚定规则 | StyleTokenRule | 每镜显式重嵌[原始锁定]+[上镜承接]+[本镜新增]，开头说一遍结尾再说一遍 | knowledge/prompt-reverse.md; knowledge/seedance-template-library.md |
| StyleTokenRule:物理与身份锁定 | StyleTokenRule | 人物写identical face/hairstyle/outfit，产品写几何/颜色/材质/比例unchanged | knowledge/seedance-template-library.md; knowledge/prompt-reverse.md |

## ConsistencyTool · 一致性工具箱

| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| ConsistencyTool:角色三视图 | ConsistencyTool | 开拍前文生图生成正面/侧面/背面基准资产，各镜以三视图为参考图生成首帧 | playbooks/consistency.md |
| ConsistencyTool:首帧锚定 | ConsistencyTool | 重复出现的角色/场景/设备绝不文生视频逐镜碰运气，先静帧后图生视频 | playbooks/consistency.md; agents/prompt-engineer.md |
| ConsistencyTool:种子复用 | ConsistencyTool | UI暴露seed时同镜抽卡换seed微调，全片用同一prompt模板骨架 | playbooks/consistency.md; knowledge/prompt-reverse.md |
| ConsistencyTool:LoRA | ConsistencyTool | 跨项目复用主持人/吉祥物/品牌风格在LiblibAI训练LoRA，系列化内容用 | playbooks/consistency.md |
| ConsistencyTool:首尾帧衔接链 | ConsistencyTool | 导出镜头N尾帧→N+1首帧无缝连续，同场景同构图只改一个元素 | playbooks/consistency.md; playbooks/platform-prompts.md |
| ConsistencyTool:多镜原生模型 | ConsistencyTool | Seedance2.x/万相2.6+/Sora Storyboard/LibTV分镜节点一次生成多镜 | playbooks/consistency.md |
| ConsistencyTool:后期兜底 | ConsistencyTool | 全片统一LUT调色+同一配音音色+同一BGM风格，脑补掉小瑕疵 | playbooks/consistency.md |

## FailFix · 常见失败→修复

| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| FailFix:抽象词 | FailFix | "电影感/高级感/震撼"堆满→每个抽象词换成一个具体视觉事实 | playbooks/platform-prompts.md; agents/prompt-engineer.md |
| FailFix:超载prompt | FailFix | prompt又长又密四不像/把完整剧本当prompt→砍到1主体+1动作+1运镜 | playbooks/platform-prompts.md; agents/prompt-engineer.md |
| FailFix:堆多个运镜 | FailFix | 堆多个运镜镜头乱飞→运镜≤2个，动感靠变速+复合运镜 | playbooks/platform-prompts.md |
| FailFix:I2V复述画面 | FailFix | 图生视频复述画面→只写运动，画面交给首帧图 | playbooks/platform-prompts.md; agents/prompt-engineer.md |
| FailFix:首尾帧差异太大 | FailFix | 首尾帧差异大过渡崩坏→保持同场景同构图只改一个元素 | playbooks/platform-prompts.md; playbooks/consistency.md |
| FailFix:手部多人穿帮 | FailFix | 手部/多人互动穿帮→简化成单主体或用参考图/表演迁移 | playbooks/platform-prompts.md |
| FailFix:跨镜风格漂移 | FailFix | 跨镜色彩/光跳变→风格token块+首帧锚定，逐镜重复风格锁词 | playbooks/platform-prompts.md; knowledge/prompt-reverse.md |
| FailFix:平台错配 | FailFix | 把Runway句式丢即梦/海螺运镜没放开头→按平台语法改写 | agents/prompt-engineer.md; knowledge/prompt-reverse.md |
| FailFix:人物脸漂移身份不一致 | FailFix | 脸漂移/身份不一致/表情僵→首帧图生视频兜底+微表情+no identity drift | knowledge/prompt-reverse.md |
| FailFix:真人脸审核拦截 | FailFix | 真人脸参考图被审核拦截→用授权素材/虚拟人像/线稿分镜规避 | playbooks/platform-prompts.md; playbooks/storyboard-grid.md |
| FailFix:宫格整图变格子动画 | FailFix | 整图喂视频模型变"9格各自动"→写明按顺序演绎或改切片首帧 | playbooks/storyboard-grid.md |
| FailFix:六维定位再修改 | FailFix | 不满意不推倒，按内容/运动/音频/物理/人物/风格六维单点修 | knowledge/prompt-reverse.md |

## NegativeRule · 负面词与禁用

| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| NegativeRule:通用负面清单 | NegativeRule | 变形/扭曲/多余手指/面部扭曲/文字/字幕/水印等具体排除项，不写空泛"不要" | playbooks/platform-prompts.md; agents/prompt-engineer.md |
| NegativeRule:视频专属负向词库 | NegativeRule | no morphing/flickering/jitter/warping/extra limbs/identity drift等视频翻车词 | knowledge/prompt-reverse.md |
| NegativeRule:文字数据不交给AI | NegativeRule | 参数/曲线/表格/logo字全部后期制作，prompt里不出现，负面含文字字幕水印 | agents/prompt-engineer.md; playbooks/platform-prompts.md |
| NegativeRule:真人脸审核规避 | NegativeRule | 真人脸参考图会被审核拦截，用授权素材/虚拟人像/线稿分镜规避 | playbooks/platform-prompts.md; playbooks/storyboard-grid.md |

## ReferenceRule · 参考引用规则

| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| ReferenceRule:@引用语法速查 | ReferenceRule | @图片1首帧/@图片2尾帧/@视频1运镜/@音频1配乐等，素材4-5个为宜 | knowledge/seedance-template-library.md; playbooks/platform-prompts.md |
| ReferenceRule:Seedance参考素材语法 | ReferenceRule | 图片1/视频1/音频1按序指代；编辑须含"编辑/修改"之一且直写视频1 | playbooks/platform-prompts.md |
| ReferenceRule:全能参考三用法 | ReferenceRule | 单图主体=锚图只写运动；多图写清每张取什么；构图精确时用专用首帧 | playbooks/consistency.md; agents/prompt-engineer.md |
| ReferenceRule:音频符号语法 | ReferenceRule | {台词}(音乐)<音效>【字幕】，非中英台词标语种，对白用"角色说：…" | playbooks/platform-prompts.md; knowledge/seedance-template-library.md; knowledge/prompt-reverse.md |
