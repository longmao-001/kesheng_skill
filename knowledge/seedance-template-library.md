# Seedance 2.0 分镜模板库（外部调研汇编）

> 来源：GitHub 调研（2026-08）。[liangdabiao/make-prompt-seedance2](https://github.com/liangdabiao/make-prompt-seedance2)（结构化模板体系，已改编）、[YouMind-OpenLab/awesome-seedance-2-prompts](https://github.com/YouMind-OpenLab/awesome-seedance-2-prompts)（2000+ 案例库）、[luozhilzh/video-prompt-reverse](https://github.com/luozhilzh/video-prompt-reverse)（反推提示词工程师）、[beshuaxian/higgsfield-seedance2-jineng](https://github.com/beshuaxian/higgsfield-seedance2-jineng)（15 个行业 skill，含摄像机百科）。
> 用法：多镜一次成片时按模板套时间轴结构；单镜图生视频仍用 `playbooks/platform-prompts.md` 的公式。运镜词表在 platform-prompts.md，不重复收录。

## 一、时间轴分镜公式（多镜成片用）

```
【风格】_____风格，_____秒，_____比例，_____氛围

【时间轴】
0-X秒：[镜头] + [画面] + [动作] + [特效]
X-Y秒：[镜头] + [画面] + [动作] + [特效]
...

【声音】_____配乐 + _____音效 + _____对白
【参考】@图片1 _____，@视频1 _____
```

15 秒叙事节奏参考：0-3 建立场景 → 3-7 发展 → 7-11 高潮 → 11-13 转折 → 13-15 落版。

## 二、产品展示类模板（B2B/产品片直接套）

```
【风格】商业广告/极简/高端/科技感，15秒，16:9

0-2秒：开场抓眼球，产品特写或悬念设置
2-5秒：产品全景展示，运镜环绕/推拉
5-8秒：产品细节特写，材质/工艺展示
8-12秒：使用场景，产品在实际环境中的应用
12-15秒：品牌落版，slogan展示

【声音】科技感/大气配乐
【参考】@图片1 产品外观，@图片2 材质参考
```

与科生工艺对接：slogan/大字文案按 `knowledge/ad-copy.md`，数据字卡按 [[图表层]]，一致性按 [[首帧锚定]]。

## 三、产品动效展示类（UI/多图宣传片）

```
将@图片N...@图片1这几张展示图，变成多分镜多角度的宣传片，搭配合适的口播介绍，增加丰富的转场效果和细节展示，每个分镜的转换需要连贯顺畅。
产品介绍为：[产品名称]是[产品类型]，让[核心价值]，提供[功能1]、[功能2]、[功能3]。
制作思路：[设计理念描述]
```

## 四、视频延长模板

```
将@视频1延长X秒（生成长度选择X秒）
延续前视频的风格和主体：
0-X秒：[新内容描述]，与前视频无缝衔接
【要求】保持主体一致性，动作连贯流畅
```

## 五、视频编辑模板（改局部不改全片）

```
基于@视频1进行编辑：
【保留】原视频的运镜/场景
【修改】[具体修改点]
【要求】保持镜头连贯，只在指定位置修改
```

## 六、@引用语法速查

```
@图片1 作为首帧 / @图片2 作为尾帧 / @图片3 作为主体形象参考
@图片4-6 作为场景参考 / @视频1 参考运镜方式 / @视频2 参考动作节奏
@音频1 用于配乐 / @音频2 用于对白参考
```
限制：写实真人脸素材会被审核拦截；参考素材 4-5 个为宜。

## 七、氛围关键词库

- 光影：逆光、侧光、顶光、伦勃朗光、剪影、轮廓光、体积光、丁达尔效应
- 色调：暖色调、冷色调、高饱和、低饱和、黑白、赛博朋克、复古胶片
- 质感：电影级、纪录片风格、广告质感、MV风格、油画感、水墨感
- 情绪：温馨、紧张、悬疑、欢快、忧伤、史诗、治愈、惊悚

## 八、优质提示词特征清单（自检）

时间轴清晰 ✅ 镜头语言明确 ✅ 动作描述具体 ✅ 多模态引用规范 ✅ 声音设计完整 ✅ 参考素材标注清楚 ✅（再加科生两条：无抽象词 ✅ 有变速/复合运镜 ✅——见 [[动感三来源]]）

## 九、案例模式精选（awesome-seedance-2-prompts 提炼）

> 来源：[YouMind-OpenLab/awesome-seedance-2-prompts](https://github.com/YouMind-OpenLab/awesome-seedance-2-prompts)（2026-08-12 调研）。该库宣称总量 5000+ 条，GitHub README 为平面案例流（逐条标题即类型标签：Cinematic / UGC / Advertisement / Vlog / MV / Anime / Wuxia…），精细分类（cinematic/anime/UGC/ads/meme）在其配套的 YouMind 画廊侧。以下是从广告类/产品类/cinematic 类代表案例中**总结的结构模式**，非逐条搬运。

### 广告类模式 A：多场景产品广告（首尾产品夹心结构）

香水准奢广告范式：5 场景 × 3 秒，**产品开场 → 人物生活方式中段 → 产品落版收口**（SC1 产品特写 → SC2 人物登场 → SC3 使用瞬间 → SC4 人物行动 → SC5 产品居中落版）。每场景独立一段 prompt，文末必附**一致性块**（"Same woman throughout all scenes, identical face/hairstyle/outfit；Same bottle design in every shot；No extra people, no distorted hands, no unwanted text"）。要点：人物只在中间段出现，产品和人物不同时挤一个镜头。对应我们的 TVC 骨架，见 `knowledge/tvc-ad-templates.md`。

### 广告类模式 B：UGC 证言广告（对镜口播 + 强产品锁定）

手机壳类范式：总起段定人设定场（人物外貌+场景+"向朋友推荐"语感）→ 一段完整口播台词 → Storyboard 5 场（特写展示→上手演示→日常使用→自拍场景→hero shot 收尾+一句收口台词）→ 双重锁定块：**物理一致**（"case geometry/color/material/buttons/proportions remain unchanged"）+ **质感一致**（"realistic smartphone camera quality, natural handheld movement, subtle autofocus"）。要点：UGC 感的来源是"手机实拍缺陷"（手持微晃、自动对焦抽动），不是精美。

### 广告类模式 C：场景变换商业片（安静→高能变身）

Red Bull 范式：日常压抑场景（办公室疲惫）→ 产品介入瞬间 → **气氛戏剧化转换**（同一人变身另一身份的高能场景）→ 第一人称沉浸镜头收口，品牌露出压最后。要点：变身的"同一人"必须写死（same man, now as…），转换段是全片高潮，运镜/动感全堆在这里。

### 产品/生活类模式：手机实拍 montage（快切记忆流）

尾牙派对类范式：总起声明"raw smartphone home video, no cinematic polish"→ 每 1-2.5s 一个快切段（shake/jump cut/quick flash 交替）→ 人物锁定用强措辞（"reference photo as the strict ONLY visual reference, zero deviation"）→ 负向反着写（"no pro stabilization or effects"）。要点：真实感=刻意保留抖动和跳切，和我们 [[动感三来源]] 的③剪辑节奏同构。

### Cinematic 模式 A：微表情情感短片（总-分-收三段式）

日式纯爱范式：**总起段**（时长+风格+场景+光影+一致性总约束"面部/服装/发型全程一致，无变形漂移"）→ **时间轴分段**（每段写死微表情+呼吸同步细节：瞳孔放大、喉结滚动、耳垂泛红、停顿 0.3-0.4 秒）→ **专项收口段**（口型同步要求→音效层→一致性重申）。要点：情感戏的张力来自"微表情+精确到 0.1 秒的停顿"，不是大动作。

### Cinematic 模式 B：CUT 编号独白片（头部参数块 + 逐镜台词）

对镜独白范式：开头参数块（`MODE / MOTION / DURATION / REF`）→ 人物外观锁定段（细到指甲颜色、肤质"visible pores"）→ `CUT 1..N` 每镜一行`景别+角度`+一个微动作+一句台词 → 负向用 `--no` 列表（no robotic movement, no puppet face, no uncanny valley, no inconsistent face）。要点：台词驱动结构，每镜只配一句词，负向列表专攻"AI 感"。

### 共性规律（2000+ 案例的收敛点）

- 长 prompt 都走**总起约束 → 分段 → 收口重申**三段式，一致性要求开头说一遍、结尾再说一遍（与我们 [[首帧锚定]] 和反推方法论的"双锚定"互证，见 `knowledge/prompt-reverse.md`）
- 凡有人物，必写"identical face/hairstyle/outfit, no identity drift"
- 凡产品，必写物理属性锁定（几何/颜色/材质/比例 unchanged）
- 负向约束不再是可选项，是结构的一部分
