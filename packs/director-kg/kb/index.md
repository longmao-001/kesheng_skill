# 视觉导演 领域知识图谱索引（director-kg）

> 按实体类型分组。`原文路径` 与 `kg.json` 的 `sources` 一致（相对 `F:/AI/kesheng/`）。
> 权威正文永远在原文件，本表只做概念化索引 + 出处链接，两处不走样。

## ShotType 景别
| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| 远景 | ShotType | 16-24mm，交代环境/空间关系/格局，推进式叙事起点 | knowledge/camera-language.md、agents/director.md |
| 全景 | ShotType | 35mm，人物全身动作/场景全貌，建立场景 | knowledge/camera-language.md、agents/director.md |
| 中景 | ShotType | 50mm，人物上半身/产品与人交互，带货演示主力景别 | knowledge/camera-language.md、knowledge/tvc-ad-templates.md |
| 近景 | ShotType | 50mm，面部表情/情绪反馈，情绪景别 | knowledge/camera-language.md、knowledge/tvc-ad-templates.md |
| 特写 | ShotType | 85mm，产品细节/关键动作，卖点演示主力景别 | knowledge/camera-language.md、knowledge/tvc-ad-templates.md |
| 大特写 | ShotType | 135mm，水珠/气泡/纹理/膏体等微观细节 | knowledge/camera-language.md、knowledge/tvc-ad-templates.md |

## CameraMove 运镜
| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| 推 | CameraMove | dolly-in，建立紧张/聚焦/情感逼近，戏剧性揭示/开场 | knowledge/camera-language.md |
| 拉 | CameraMove | dolly-out，释然/孤独/交代全貌，收尾/揭示环境规模 | knowledge/camera-language.md |
| 摇 | CameraMove | pan/tilt，扫视信息/跟视线，展现场景宽度高度 | knowledge/camera-language.md |
| 移 | CameraMove | truck，平行观察/展示深度，跟随角色侧移/空间关系 | knowledge/camera-language.md |
| 跟 | CameraMove | tracking，陪伴感/行动感，角色行进/低机位跟拍显步伐 | knowledge/camera-language.md |
| 环绕 | CameraMove | orbit，英雄时刻/全方位审视，产品展示/人物高光 | knowledge/camera-language.md |
| 升降 | CameraMove | crane/jib，史诗感/规模揭示，建立全景/格局拉开 | knowledge/camera-language.md |
| 变焦 | CameraMove | zoom，突然强调/快速转向，强调关键元素（比推更硬） | knowledge/camera-language.md |
| 希区柯克变焦 | CameraMove | dolly-zoom，眩晕/心理冲击/世界塌陷感，震惊/转折揭示 | knowledge/camera-language.md |
| 手持 | CameraMove | handheld，纪实/紧迫/亲密，纪录片感/UGC 真实感/追逐 | knowledge/camera-language.md |
| FPV穿越 | CameraMove | fpv，沉浸/速度/探索，第一人称穿空间/开箱/跑酷 | knowledge/camera-language.md、knowledge/tvc-ad-templates.md |
| 甩 | CameraMove | whip-pan，节奏/转场冲击，快速切场景保持视觉连贯 | knowledge/camera-language.md |
| 固定 | CameraMove | locked-off，稳定/客观/仪式感，对话/产品细节/落版 | knowledge/camera-language.md、knowledge/tvc-ad-templates.md |
| 探针微距穿梭 | CameraMove | macro-probe，奢侈/解压/微观奇观，首饰滑行/穿缝隙 | knowledge/camera-language.md、knowledge/tvc-ad-templates.md |
| 低角度环绕 | CameraMove | low-angle-orbit，力量感/时尚感，潮流服饰/产品英雄化 | knowledge/camera-language.md |
| 鱼眼贴脸 | CameraMove | fisheye，畸变张力/街头感，潮流/重音卡点片头 | knowledge/camera-language.md |
| 无人机升镜 | CameraMove | drone-rise，史诗感/上帝视角规模揭示，航拍/设施俯瞰 | playbooks/storyboard-grid.md、knowledge/camera-language.md |

## Transition 转场/衔接
| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| 硬切 | Transition | 干脆/节奏，对话、快节奏带货 | knowledge/camera-language.md |
| 匹配剪辑 | Transition | 高级/流畅穿越，主体轴向一致换场景（产品不变背景变） | knowledge/camera-language.md、knowledge/tvc-ad-templates.md |
| 鞭甩转场 | Transition | 速度/张力，潮流/运动片场景切换 | knowledge/camera-language.md |
| 溶解 | Transition | 柔和/时光流逝，礼盒揭示/回忆/情绪过渡 | knowledge/camera-language.md |
| 遮挡转场 | Transition | 无缝/一镜到底错觉，前景物体掠过换场景 | knowledge/camera-language.md |
| 粒子消散重组 | Transition | 科技感/变装，极速变装/材质转换 | knowledge/camera-language.md |
| 冻结帧爆发 | Transition | 节奏中断再炸开，钩子段/卡点片头 | knowledge/camera-language.md |

## VisualMetaphor 视觉隐喻与招牌镜头
| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| 微观穿越 | VisualMetaphor | 进细胞/沿 DNA 飞行，把微观世界做成奇观招牌镜头 | agents/director.md、knowledge/camera-language.md |
| 宏观俯瞰 | VisualMetaphor | 设施航拍感/尺度揭示，交代工程规模与时空尺度 | agents/director.md、knowledge/camera-language.md |
| 数据动起来 | VisualMetaphor | 图表动起来/数据可视化，数据后期重绘不许加字 | agents/director.md、knowledge/图表层.md |
| 过程演示 | VisualMetaphor | 反应/组装/编辑过程可视化，把机理讲成过程 | agents/director.md |
| 工程隐喻 | VisualMetaphor | 用工程结构/装置比喻抽象概念，精确结构走首帧图 | agents/director.md |
| 生长效果可视化 | VisualMetaphor | 首帧初始→尾帧理想，时间压缩生长，效果难可视化品类 | knowledge/tvc-ad-templates.md |
| 探针微观视角 | VisualMetaphor | 微距拍膏体微观变化，解压治愈感，美妆个护 | knowledge/tvc-ad-templates.md、knowledge/camera-language.md |

## ViStyle 视觉风格规范
| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| 科技蓝生物绿VI模板 | ViStyle | 高校/科研院所风，深蓝背景+粒子流转场 | knowledge/vi_styles/vi-style-templates.md |
| 医疗洁净风VI模板 | ViStyle | 医疗蓝/生命粉/纯净白，柔和模糊转场+ECG 片头 | knowledge/vi_styles/vi-style-templates.md |
| 自然暖色调VI模板 | ViStyle | 科普向暖橙天空蓝，浅色背景禁止纯黑，圆润字体 | knowledge/vi_styles/vi-style-templates.md |
| VI适配速查表 | ViStyle | 申报答辩/公众科普/产业商业三版速配 | knowledge/vi_styles/vi-style-templates.md |
| 风格token块 | ViStyle | 全片写死一句风格描述逐字复用每镜，换平台保留 | playbooks/consistency.md |

## FeasibilityRule 可拍性约束
| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| 精确结构首帧图加图生视频 | FeasibilityRule | 蛋白折叠/设备构造/实验装置必须首帧图+图生视频 | agents/director.md、playbooks/consistency.md |
| 单镜时长上限10秒 | FeasibilityRule | 单镜 3-10 秒，≤10s 为质量门控硬指标 | agents/director.md |
| 单镜不超两种运镜 | FeasibilityRule | 单镜 ≤2 种运镜，要动感靠变速和复合 | knowledge/camera-language.md、knowledge/动感三来源.md |
| 单镜单动作单重点 | FeasibilityRule | 1 主体+1 动作+1 运镜，塞 3 动作=不可制作 | agents/director.md、knowledge/tvc-ad-templates.md |
| 匀速单运镜不合格 | FeasibilityRule | 匀速单运镜=PPT 式视频，不合格 | knowledge/动感三来源.md、knowledge/camera-language.md |
| 角色表演需参考图方案 | FeasibilityRule | 需角色表演但没参考图方案=不可制作 | agents/director.md、playbooks/consistency.md |
| 连续三同景别为节奏事故 | FeasibilityRule | 连续 3 同景别/无远景锚定切特写=节奏事故 | agents/director.md |
| 强制约束收口 | FeasibilityRule | 每片末尾加约束词：无穿模/无偏色/无模糊/人脸自然 | knowledge/tvc-ad-templates.md |
| AI画面零文字 | FeasibilityRule | AI 画面不出现文字/数据，图表全部后期做（M4 强检） | knowledge/图表层.md、agents/director.md |
| Slogan不捏造 | FeasibilityRule | Slogan 必须用户输入，AI 绝不捏造 | knowledge/tvc-ad-templates.md |
| 容器场景符合常识 | FeasibilityRule | 容器/场景必须符合生活常识，AI 不替你把关 | knowledge/tvc-ad-templates.md |
| 避免纯黑背景 | FeasibilityRule | 科普向避免纯黑背景（太严肃吓跑路人） | knowledge/vi_styles/vi-style-templates.md |
| 黑白线稿规避真人审核 | FeasibilityRule | 分镜用黑白线稿规避平台真人参考拦截 | playbooks/storyboard-grid.md |

## MovingTechnique 动感技法
| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| 运镜变速 | MovingTechnique | 由快到缓收稳/骤然放缓/急停悬停，快慢即情绪 | knowledge/动感三来源.md、agents/director.md |
| 复合运镜 | MovingTechnique | 环绕+上升、推近+旋转，两镜内制造动感层次 | knowledge/动感三来源.md、agents/director.md |
| 画面内部运动 | MovingTechnique | 光扫/粒子/前景遮挡掠过/元素展开，每镜至少一个 | knowledge/动感三来源.md、agents/director.md |
| 剪辑节奏 | MovingTechnique | 动作匹配剪辑、快慢相间，剪辑端制造动感落差 | knowledge/动感三来源.md、agents/director.md |
| 相邻镜动势衔接 | MovingTechnique | 环绕接推近，首尾帧无缝，分镜阶段标注 | knowledge/动感三来源.md、agents/director.md、playbooks/consistency.md |
| 数据稳定镜头动感补偿 | MovingTechnique | 主体钉死不动，动感交给镜头（下移俯拍揭示/缓推） | knowledge/动感三来源.md、agents/director.md |

## GridTechnique 宫格分镜技法
| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| 九宫格分镜图 | GridTechnique | 一次 3x3 全片构图定型，整图成片或切片首帧 | playbooks/storyboard-grid.md |
| Image2五段式prompt | GridTechnique | 基础设置→风格→逐格镜头→视觉规范→底部信息栏 | playbooks/storyboard-grid.md |
| 黑白线稿分镜 | GridTechnique | 规避真人审核+只当视觉骨架，重渲成彩色 | playbooks/storyboard-grid.md |
| 整图一次成片 | GridTechnique | 宫格图喂 Seedance/Sora，须写清逐格顺序演绎 | playbooks/storyboard-grid.md |
| 切片逐格当首帧 | GridTechnique | 切开逐格进图生视频，按 I2V 公式写运动 | playbooks/storyboard-grid.md、knowledge/tvc-ad-templates.md |
| 单格重绘微调 | GridTechnique | 继续编辑只重画某格，不重抽整图 | playbooks/storyboard-grid.md |
| 宫格变体格数 | GridTechnique | 四/九/十六/二十五宫格对应时长，官方上限≤15 格 | playbooks/storyboard-grid.md、knowledge/tvc-ad-templates.md |
| 宫格时间线分镜 | GridTechnique | 时间区间/镜头动作/画面内容三列逐秒控制 | knowledge/tvc-ad-templates.md、playbooks/storyboard-grid.md |

## Mood 情绪效果
| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| 紧张聚焦 | Mood | 建立紧张/聚焦注意力/情感逼近（推） | knowledge/camera-language.md |
| 释然孤独 | Mood | 释然/孤独/交代全貌/情绪抽离（拉、溶解） | knowledge/camera-language.md |
| 扫视跟视 | Mood | 扫视信息/跟随视线（摇） | knowledge/camera-language.md |
| 平行观察 | Mood | 平行观察/展示场景深度（移） | knowledge/camera-language.md |
| 陪伴行动 | Mood | 陪伴感/行动感（跟） | knowledge/camera-language.md |
| 英雄力量审视 | Mood | 英雄时刻/全方位审视/力量感时尚感（环绕、低角度环绕） | knowledge/camera-language.md |
| 史诗规模 | Mood | 史诗感/规模揭示/上帝视角（升降、无人机升镜） | knowledge/camera-language.md |
| 眩晕心理冲击 | Mood | 眩晕/心理冲击/世界塌陷感（希区柯克变焦） | knowledge/camera-language.md |
| 纪实紧迫亲密 | Mood | 纪实/紧迫/亲密（手持） | knowledge/camera-language.md |
| 沉浸速度探索 | Mood | 沉浸/速度/探索（FPV、快速环绕） | knowledge/camera-language.md |
| 节奏转场冲击 | Mood | 节奏/转场冲击（甩、硬切、鞭甩、冻结帧爆发） | knowledge/camera-language.md |
| 稳定客观仪式 | Mood | 稳定/客观/仪式感（固定、匹配剪辑、遮挡转场） | knowledge/camera-language.md |
| 奢侈微观奇观 | Mood | 奢侈/解压/微观奇观（探针、慢速环绕） | knowledge/camera-language.md |
| 街头畸变张力 | Mood | 畸变张力/街头感（鱼眼贴脸） | knowledge/camera-language.md |
| 突然强调 | Mood | 突然强调/快速转向/材质转换强调（变焦、粒子消散重组） | knowledge/camera-language.md |

## Beat 叙事节拍
| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| 建立场景节拍 | Beat | 远景/全景交代环境、空间关系、场景全貌 | agents/director.md、knowledge/camera-language.md |
| 推进信息节拍 | Beat | 中景推进信息、产品与人交互 | agents/director.md、knowledge/camera-language.md |
| 情绪数据节拍 | Beat | 近景/特写给情绪反馈、卖点与数据 | agents/director.md、knowledge/camera-language.md |
| 微观细节节拍 | Beat | 大特写/特写展示水珠、气泡、纹理、膏体 | knowledge/camera-language.md、knowledge/tvc-ad-templates.md |
| 推进式叙事动线 | Beat | 远→中→近→特写，推进式叙事的景别推进 | knowledge/camera-language.md、agents/director.md |
| 悬念式揭示动线 | Beat | 特写→远，先细节后全貌的悬念揭示 | knowledge/camera-language.md、knowledge/产品开场语法.md |

## Concept 抽象表达概念
| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| 微观结构 | Concept | 细胞、DNA、生物大分子等微观世界结构 | agents/director.md、knowledge/camera-language.md |
| 宏观规模 | Concept | 设施规模、时空尺度、工程体量 | agents/director.md |
| 数据指标 | Concept | 性能、趋势、指标对比等数据 | agents/director.md、knowledge/图表层.md |
| 过程机理 | Concept | 反应、组装、编辑等工艺过程机理 | agents/director.md |
| 工程结构 | Concept | 装置、设备精确结构构造 | agents/director.md |
| 材质质感 | Concept | 表面工艺、微观质感、光泽 | knowledge/tvc-ad-templates.md、knowledge/产品开场语法.md |
| 生长变化 | Concept | 种子/预期效果的演化与生长 | knowledge/tvc-ad-templates.md |

## Gate 质量门控检查点
| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| 镜头动感门控 | Gate | 七维表“镜头动感”行，检查变速/复合/内部运动/剪辑节奏 | knowledge/动感三来源.md |
| M4出口门控 | Gate | 数据/图表是否后期做、AI 是否生成数据或文字 | knowledge/图表层.md |
| 可拍性门控 | Gate | 必攻击点：不可制作/陈词滥调/图文脱节/节奏事故 | agents/director.md |

## Scenario 应用场景
| 实体 | 类型 | 一句话 | 原文路径 |
|---|---|---|---|
| 申报答辩场景 | Scenario | 国家大设施/高校研究所/生物医药企业申报，深蓝深绿 | knowledge/vi_styles/vi-style-templates.md |
| 公众科普场景 | Scenario | 公众科普/开放日/学生/新媒体，暖橙天空蓝浅色 | knowledge/vi_styles/vi-style-templates.md |
| 产业商业场景 | Scenario | 企业品牌片/产业商业广告，企业品牌色中性灰白 | knowledge/vi_styles/vi-style-templates.md |
