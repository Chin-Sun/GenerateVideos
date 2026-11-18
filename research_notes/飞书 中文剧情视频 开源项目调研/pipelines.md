# 调研中文剧情视频生成流水线

本文供主报告作者及飞书个人机器人项目开发者选型，目标是约 60 秒中文剧情、角色亲自说话且口型同步、项目可保存、通过对话修改、云端长期运行。检索日期为 2026 年 11 月 17 日。实际使用公开 GitHub 搜索 API、仓库元数据 API、README、少量源代码与许可证全文；没有安装、运行生成、调用付费模型或部署。**这是有边界的广泛检索，不是穷尽清单；仓库存在和文档功能已核实，不等于成片质量或生产可靠性已经实测。**

目录：[比较项目](#比较哪些项目值得复用) · [选择架构](#判断怎样满足当前项目) · [记录证据边界](#记录维护与证据缺口)

## 比较哪些项目值得复用

### Takeaway

最值得优先比较的是 **LocalMiniDrama 的可编辑工程和剧内助手**、**Jellyfish 的实体与异步任务模型**，以及 **comfyui-AICG3D 的 H3 对白与分段控制思路**。火宝短剧覆盖完整工作台但有非商业许可；NarratoAI、MoneyPrinterTurbo、Director 对编排有价值，却不能把“有配音”“能生成影片”直接解释为角色对白口型同步。[LocalMiniDrama](https://github.com/xuanyustudio/LocalMiniDrama)；[Jellyfish](https://github.com/Forget-C/Jellyfish)；[AICG3D](https://github.com/JGRFW/comfyui-AICG3D)

### Cited Findings

下列“证据”明确区分文档声明与源码核实。“未证明”仅表示本次证据不足，不表示项目绝对不具备此能力。

#### １．LocalMiniDrama——最贴近可保存、可对话编辑的工程

- **真实仓库**：[xuanyustudio/LocalMiniDrama](https://github.com/xuanyustudio/LocalMiniDrama)。README 的 v1.2.9 更新声明：剧集、制作、画布页中的剧内助手可以对话操作剧本、角色、场景、分镜和出图，删除需要确认。**本次核实的是 README 声明，未审计助手工具权限和修改实现**。[README](https://github.com/xuanyustudio/LocalMiniDrama/blob/main/README.md)
- **分镜与一致性**：从故事到多集剧本、角色／场景／道具、含台词的分镜、逐镜图片与视频、最后合成；支持多图参考、尾帧衔接、提示词编辑、手动参考图。角色一致性是引用资产的工作流能力，不是质量保证。[README](https://github.com/xuanyustudio/LocalMiniDrama/blob/main/README.md)
- **保存与版本**：SQLite 与本地文件；工程 ZIP 导入导出；画布与列表使用同源数据；历史功能明确列出视频历史版本；工作流组可选择图片／视频／配音重跑。[README](https://github.com/xuanyustudio/LocalMiniDrama/blob/main/README.md)
- **部署**：Vue 3、Express、SQLite、Electron；有 Node.js 源码启动和 Windows 包。详细开发文档说明配置与数据目录，不能仅凭桌面可用认定云端多用户或持久队列已具备。[开发指南](https://github.com/xuanyustudio/LocalMiniDrama/blob/main/docs/quickstart.md)
- **许可**：已读取实际许可证，MIT，版权为 2026 xuanyustudio；API 模型、音色与素材权利不包含在 MIT 授权内。[LICENSE](https://raw.githubusercontent.com/xuanyustudio/LocalMiniDrama/main/LICENSE)
- **可复用**：剧集／分镜实体、单镜重生、历史版本、工程导入导出、受限助手工具。**缺口**：没有核实 PPAPI H3 适配；README 的旁白配音不能证明对白口型；云端鉴权、队列恢复、幂等与版本不可变性均需验证。README 同时写“数据不出本机”和接入第三方 AI API，前者只能按本地存储理解，不能当作推理完全离线的证明。[README](https://github.com/xuanyustudio/LocalMiniDrama/blob/main/README.md)

#### ２．Jellyfish——适合复用后台制作状态机

- **真实仓库**：[Forget-C/Jellyfish](https://github.com/Forget-C/Jellyfish)。React／Vite 与 FastAPI 工作台，按项目、章节、镜头组织；脚本提取角色、场景、道具、服装和对白。[README](https://github.com/Forget-C/Jellyfish/blob/main/README.md)
- **一致性与编辑**：共享实体资产；候选资产与对白可接受、忽略或关联已有对象；镜头准备状态与生成状态分开；关键帧、参考图、提示词、单镜和批量生成，结果回写镜头／媒体系统。[README](https://github.com/Forget-C/Jellyfish/blob/main/README.md)
- **持久任务**：README 声称统一异步文本、图像、视频任务，跟踪进度、结果、耗时、取消和恢复。**恢复是文档声明，未源码验证进程崩溃后恢复语义**。[README](https://github.com/Forget-C/Jellyfish/blob/main/README.md)
- **部署**：仓库说明 Compose 包含前端、后端、MySQL、Redis、RustFS；OpenAPI 生成前端客户端。是更接近常驻服务器的结构，但不等于已经做过负载、安全或故障演练。[README](https://github.com/Forget-C/Jellyfish/blob/main/README.md)
- **许可**：已读取实际 Apache-2.0 许可证全文；许可证末尾仍为标准模板版权占位符，不改变应继续检查 NOTICE 与第三方依赖义务的必要性。[LICENSE](https://raw.githubusercontent.com/Forget-C/Jellyfish/main/LICENSE)
- **可复用**：分镜准备／确认／生成分离、资产复用、OpenAPI、异步任务中心。**缺口**：对白字段不是音视频同步实现；未验证 H3、飞书或聊天修改；没有不可变工程版本／回滚实现证据。[README](https://github.com/Forget-C/Jellyfish/blob/main/README.md)

#### ３．Huobao Drama——全流程工作台，但要看当前架构与许可

- **真实仓库**：[chatfire-AI/huobao-drama](https://github.com/chatfire-AI/huobao-drama)。当前 README 已是 TypeScript、Hono、Drizzle、Mastra、better-sqlite3；不要沿用旧资料中的 Go／MySQL 栈。[README](https://github.com/chatfire-AI/huobao-drama/blob/master/README.md)
- **能力**：小说改写拍摄剧本，提取角色／场景／道具，生成参考资产；分镜中 `@角色名` 映射参考图；批量视频、失败重试、选择镜头后 FFmpeg 拼接。[README](https://github.com/chatfire-AI/huobao-drama/blob/master/README.md)
- **保存与部署**：SQLite WAL、生成媒体本地保存；桌面包、服务器指南、Docker 和 Compose；当前 Compose 持久卷覆盖 SQLite、图片／视频及 workspace。README 同时含旧版本“移除 Docker／MySQL”历史记录，不能将历史变更误判为当前无 Docker。[README](https://github.com/chatfire-AI/huobao-drama/blob/master/README.md)
- **许可**：README 明示 CC BY-NC-SA 4.0，限制商业目的使用；GitHub API 为 `NOASSERTION`，不能把项目自称开源当作宽松商用许可。[许可证入口](https://github.com/chatfire-AI/huobao-drama/blob/master/LICENSE)；[README 许可段](https://github.com/chatfire-AI/huobao-drama/blob/master/README.md#-许可证--license)
- **可复用**：参考资产注入、分镜批处理、可选择合成、SQLite 单用户持久化。**缺口**：未验证对白音轨保留及中文口型；Mastra agents 不自动等于用户聊天编辑；PPAPI 与飞书需适配；版本历史与崩溃恢复待验证。[README](https://github.com/chatfire-AI/huobao-drama/blob/master/README.md)

#### ４．CineGen-ShortDrama——轻量浏览器分镜工作台

- **真实仓库**：[UllrAI/CineGen-ShortDrama](https://github.com/UllrAI/CineGen-ShortDrama)。Google Gemini 处理脚本／图像，Veo 生成视频；流程是脚本→角色／场景参考→首尾关键帧→镜头视频。[README](https://github.com/UllrAI/CineGen-ShortDrama/blob/main/README.md)
- **编辑与保存**：镜头网格、角色不同造型共享基础参考；输出语言与目标时长可选；API key 在浏览器 localStorage，工程在 IndexedDB，清站点数据会丢工程。[README](https://github.com/UllrAI/CineGen-ShortDrama/blob/main/README.md)
- **部署与许可**：Node／Vite 浏览器应用，需要 Google 模型权限；实际许可证是自定义 AniKuku Community License v1.0，含显著归属链接、商业无归属需另许可等条款。**不是 MIT，也不能简化成无限制商用**。[许可证全文](https://raw.githubusercontent.com/UllrAI/CineGen-ShortDrama/main/license.md)
- **可复用**：关键帧约束、镜头状态、角色造型参考。**缺口**：浏览器 IndexedDB 不适合作为飞书云端服务唯一工程库；未验证后台队列、对白口型、工程版本、对话编辑、H3。[README](https://github.com/UllrAI/CineGen-ShortDrama/blob/main/README.md)

#### ５．comfyui-AICG3D——与 H3 对白最直接相关的本地分段工作流

- **真实仓库**：[JGRFW/comfyui-AICG3D](https://github.com/JGRFW/comfyui-AICG3D)。README 定位是 ComfyUI 本地 MiniMax H3 工作流，包含分段解析、尾帧续写、合成、参考图／视频／音频及数字人模式；不是 PPAPI 云端调用范例。[README](https://github.com/JGRFW/comfyui-AICG3D/blob/main/README.md)
- **对白相关证据**：v1.1.23 描述六角色声线座位、跨段音色锁定、角色绑定参考图片、5～15 秒参考音频克隆，并限定只有 `<d>...</d>` 中的原文可以发声；数字人模式使用音频驱动。**这是明确对白控制设计，但未实测中文逐字准确和嘴部同步**。[README](https://github.com/JGRFW/comfyui-AICG3D/blob/main/README.md)
- **编辑与一致性**：每段独立或继承素材，逐段提示词与预览、尾帧续写、接缝曝光处理、单段抽卡修复。文档也记录旧版曾移除局部重抽入口，后续又修复，说明行为必须固定版本核查。[README](https://github.com/JGRFW/comfyui-AICG3D/blob/main/README.md)
- **部署与许可**：ComfyUI 自定义节点，FFmpeg；可选 Spark-TTS 权重另下载，部分官方工作流另需 DMAD 等节点；项目 README 声明 GPL-3.0-or-later，GitHub 元数据识别 GPL-3.0。代码许可不覆盖 H3、Spark-TTS、放大模型权重与参考声音。[README](https://github.com/JGRFW/comfyui-AICG3D/blob/main/README.md)
- **可复用**：台词标签、角色视觉／音色绑定、分段继承、只重生某段、保留原音轨。**缺口**：本地推理所需 GPU／显存未在本次核实；不应套用到 PPAPI 参数；“无限时长”是连续分段，不是单次模型无限输出；云端任务服务、工程聊天版控仍需独立开发。[README](https://github.com/JGRFW/comfyui-AICG3D/blob/main/README.md)

#### ６．Open-AI-Micro-Drama-Generator——可读的小型流水线，存在重要实现风险

- **真实仓库**：[Anil-matcha/Open-AI-Micro-Drama-Generator](https://github.com/Anil-matcha/Open-AI-Micro-Drama-Generator)。README 描述编剧、角色抽取、分镜、参考肖像、关键帧、视频、MoviePy 拼接；FastAPI 加 Next.js，SSE 报进度，MuAPI 供应商绑定。[README](https://github.com/Anil-matcha/Open-AI-Micro-Drama-Generator/blob/main/README.md)
- **源码已核实**：任务放在进程内 `jobs` 字典，FastAPI `BackgroundTasks` 执行；SSE 重连重播来自内存事件。这不是持久化队列，进程重启后任务索引与事件会丢，不能把“reconnect-safe”解释为云端断点恢复。[api.py](https://github.com/Anil-matcha/Open-AI-Micro-Drama-Generator/blob/main/server/api.py)
- **文档／代码差异**：README 流水线表仍写 Kling v2.1 Standard；实际视频代码默认 Seedance 2 VIP，失败回退 Kling Master。更严重的是两条生成路径收到 401／403 时会返回固定示例视频 `_SANDBOX_VIDEO_URL`，需要移除或明确标识，不能作为成功作品回传给用户。[视频生成代码](https://github.com/Anil-matcha/Open-AI-Micro-Drama-Generator/blob/main/server/tools/muapi_video_generator.py)
- **许可**：README 写 MIT 并链接 LICENSE，但 API license 为 null，获取到的完整仓库树未列 LICENSE；本次未拿到实际许可证文本。**应标为“README 声称 MIT、许可文件未核实”，而不是已确认 MIT**。[README](https://github.com/Anil-matcha/Open-AI-Micro-Drama-Generator/blob/main/README.md)；[仓库树 API](https://api.github.com/repos/Anil-matcha/Open-AI-Micro-Drama-Generator/git/trees/main?recursive=1)
- **可复用**：清晰 agent／provider／pipeline 分层、SSE 消息结构。**缺口**：持久工程、版控、对话修改、鉴权、中文对白同步与 H3；演示性代码不适合作为长期服务直接部署。[api.py](https://github.com/Anil-matcha/Open-AI-Micro-Drama-Generator/blob/main/server/api.py)

#### ７．AI Story——带版本与队列的叙事视频架构

- **真实仓库**：[xhongc/ai_story](https://github.com/xhongc/ai_story)。主题→文案改写→分镜→图片→运镜→视频，README 明确分镜生成“画面描述和旁白”；导演模式标为开发中。[README](https://github.com/xhongc/ai_story/blob/main/README.md)
- **编辑与版本**：文案历史版本对比、分镜顺序与时长编辑、修改提示词重生、项目暂停／恢复／重试、阶段回滚、模板与提示词版本管理，均为 README 功能声明，本次未逐项源码验收。[README](https://github.com/xhongc/ai_story/blob/main/README.md)
- **部署**：Django、Celery、Redis、Vue，Compose 中后端和 worker 共享数据与存储挂载，服务设置 `restart: unless-stopped`。[README](https://github.com/xhongc/ai_story/blob/main/README.md)
- **许可**：README 声明 CC BY-NC-SA 4.0，禁止未经授权商用；API 未识别许可证。H3 出现在赞助广告里，不能仅据此认定平台已适配 H3。[README](https://github.com/xhongc/ai_story/blob/main/README.md)
- **可复用**：Celery 长任务、分阶段重跑、历史对比。**缺口**：核心更接近旁白叙事，未证明演员对话／唇同步；没有本次核实的聊天编辑与 PPAPI 接入。[README](https://github.com/xhongc/ai_story/blob/main/README.md)

#### ８．NarratoAI——影视解说／剪辑，不是原创对白短剧生成器

- **真实仓库**：[linyqh/NarratoAI](https://github.com/linyqh/NarratoAI)。明确定位影视素材解说、LLM 文案、自动剪辑、配音、字幕；可选视频理解、转录、短剧混剪、导出剪映草稿。名称不要与 NarratorAI 混同。[README](https://github.com/linyqh/NarratoAI/blob/main/README.md)
- **对白判断**：已有素材可以含原始演员对白，工具也可加旁白；这不等于从新台词生成演员嘴部动作。README 中“主角人脸匹配”仍是未勾选计划。[README](https://github.com/linyqh/NarratoAI/blob/main/README.md)
- **部署与许可**：整合包、本地 Python 3.12／uv 和 Docker 指南；GitHub 元数据识别 MIT。TTS 克隆引擎和影视素材版权独立处理。[README](https://github.com/linyqh/NarratoAI/blob/main/README.md)；[元数据](https://api.github.com/repos/linyqh/NarratoAI)
- **可复用**：转录、字幕、素材剪辑与剪映草稿导出。**缺口**：不是原创一致角色、多镜对白生成底座；项目聊天编辑、H3 和云端队列恢复未核实。[README](https://github.com/linyqh/NarratoAI/blob/main/README.md)

#### ９．MoneyPrinterTurbo——已扩展 AI 视频素材，但主链仍是配音叙事

- **真实仓库**：[harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo)。当前 README 有 AI Agent、WebUI、API、CLI；主题→脚本→配音→素材→字幕／配乐／剪辑、批量成片、任务历史、阶段进度。[README](https://github.com/harry0703/MoneyPrinterTurbo/blob/main/README.md)
- **重要更新证据**：不能再简单称它“只拼库存素材”。当前功能表除 Pexels／Pixabay／Coverr／本地上传，明确列出秘塔 MiniMax H3 文生视频，768P／2K、4～15 秒、三种画幅，以及多个其他视频提供商。这是 README 产品功能条目，而不只是 H3 赞助广告。[README 功能表](https://github.com/harry0703/MoneyPrinterTurbo/blob/main/README.md#功能特性-)
- **对白判断**：AI 视频被描述为“原始素材”，仍进入配音、字幕和剪辑流程；支持无配音也不能推出保留原生对白、角色声线与唇同步的完整验收。因此属于**库存／生成素材＋叙事编排基线**，不是已证实对话短剧解决方案。[README](https://github.com/harry0703/MoneyPrinterTurbo/blob/main/README.md)
- **部署与许可**：Docker 预构建镜像与 Compose、本地运行、CLI／API；GitHub 元数据 MIT，第三方视频／TTS 服务和素材权利另计。[README](https://github.com/harry0703/MoneyPrinterTurbo/blob/main/README.md)；[元数据](https://api.github.com/repos/harry0703/MoneyPrinterTurbo)
- **可复用**：provider 配置、素材获取、任务进度、FFmpeg 成片、自动化入口。**缺口**：未证明一致角色的工程模型、不可变镜头版本、对白音轨保护、PPAPI H3、飞书对话编辑。[README](https://github.com/harry0703/MoneyPrinterTurbo/blob/main/README.md)

#### １０．Director——聊天视频 Agent 框架，不是现成剧情导演

- **真实仓库**：[video-db/Director](https://github.com/video-db/Director)。围绕 VideoDB 的视频搜索、剪辑、编译、生成、字幕、配音与聊天界面；支持上下文、多 agent 动态编排与实时进度。[README](https://github.com/video-db/Director/blob/main/README.md)
- **对话与保存证据**：README 的自定义 Agent 指南要求 `push_update()` 发送进度，最终 `output_message.publish()` 发布并持久会话。此处证明的是接口设计，未审计会话存储实现，也不能等同于镜头工程版控。[README](https://github.com/video-db/Director/blob/main/README.md)
- **对白判断**：“Generate full movies with voiceovers” 明确是 voiceover；没有据此确认原创中文角色对白和口型同步。[README](https://github.com/video-db/Director/blob/main/README.md)
- **部署与许可**：Python 3.9+、Node 22.8+，本地或云端，README 有 Render／Railway 入口；MIT 元数据。核心依赖 VideoDB 云基础设施，开源 agent 不代表视频存储／处理服务可免费自托管。[README](https://github.com/video-db/Director/blob/main/README.md)；[元数据](https://api.github.com/repos/video-db/Director)
- **可复用**：聊天意图分解、工具注册、状态消息、媒体结果类型。**缺口**：需自建短剧实体与版本、PPAPI、角色一致性与对白生成；更换 VideoDB 可能涉及架构改造。[README](https://github.com/video-db/Director/blob/main/README.md)

### Inferences

- **个人项目优先组合，不盲目整仓 fork**：用 LocalMiniDrama 学工程结构与受限编辑工具，用 Jellyfish 学确认状态和异步任务，用 AICG3D 学角色声线／台词／镜头边界约束。此为设计建议，不是已验证三者可直接互通。
- **许可筛选先于工程投入**：MIT／Apache 项目更便于复用；CC BY-NC-SA 与自定义 ACL 应先确认个人用途及将来商业部署范围；MicroDrama 的缺失许可文件应先向作者澄清。
- **“支持音频”的最小判据**应是镜头输出含角色自己的中文台词、对应可见说话人和同步嘴部运动，而不是后期加 TTS 或在脚本对象里存在 dialogue。

### Gaps

- 十个项目均未在本次完成端到端生成验收，因此没有一个可宣称已经满足“飞书→PPAPI MiniMax-H3→60 秒中文双人对话→修改旧工程→云端恢复”全链路。
- LocalMiniDrama 助手和 Jellyfish 恢复机制目前停留在 README 证据；GitHub API 后续返回 403 rate limit，已停止继续调用该 API，未绕过限制。许可证由公开 raw 文件独立核实，未使用认证绕过。
- H3 适配的字段、模型标识、对白能力与 PPAPI 是否同构，必须查 PPAPI 当前契约；任何其他平台的 H3 集成都不能自动证明 PPAPI 可用。

## 判断怎样满足当前项目

### Takeaway

关键不是再找一个“文生视频”按钮，而是将**工程状态、镜头版本、角色资产、音视频生成任务、对话修改命令**分开。所有对白相关输出必须单镜验收后再拼接；只改一镜时应保留其他镜头原文件和音轨。

### Cited Findings

- LocalMiniDrama 已声明工程 ZIP、视频历史与对话操作，可以参考“工程不是最终 MP4”的产品形式。[README](https://github.com/xuanyustudio/LocalMiniDrama/blob/main/README.md)
- Jellyfish 将 candidate confirmation、shot ready、generation 分开，且把对白作为可审阅候选，适合作为生成前检查点。[README](https://github.com/Forget-C/Jellyfish/blob/main/README.md)
- AICG3D 将角色参考图与声线绑定、台词限定为 `<d>` 原文，提供了避免旁白误读和声线串人的具体提示结构。[README](https://github.com/JGRFW/comfyui-AICG3D/blob/main/README.md)
- MicroDrama 的进程内字典说明“异步 API＋SSE”与“可恢复持久任务”不是同一个能力。[api.py](https://github.com/Anil-matcha/Open-AI-Micro-Drama-Generator/blob/main/server/api.py)

### Inferences

建议的自建最小结构如下，属于工程建议，未执行：

```text
飞书消息／交互卡片
  → 意图解析＋工程选择＋修改确认
  → Project／Revision／Character／Shot／Asset 数据库
  → 持久任务队列
  → PPAPI H3 provider：提交／轮询／下载／错误分类
  → 单镜音画验收
  → FFmpeg 拼接，保留原生对白音轨
  → 对象存储＋新版本预览＋飞书结果卡片
```

- **对白合同**：每镜明确 `speaker_id`、中文逐字台词、参考角色、音色参考、时长预算、画面动作和不得旁白；能否传这些字段取决于 PPAPI 实际接口，不能自造 provider 参数。
- **60 秒方案**：优先若干短镜而非强求单次 60 秒；镜头长度由供应商限制、中文台词长度和节奏决定。先验证单人近景与双人轮流说话，再决定镜头数量。
- **版本模型**：每次修改生成新 revision；保留父版本、用户修改意图、镜头引用、provider 请求摘要、输出文件和验收结果。只失效受影响镜头；“第 3 镜把最后一句改成……”不应重新生成全部。
- **长期部署**：飞书事件先落库并幂等确认，worker 独立执行；provider task id 落库；启动扫描未终态任务；重试区分未提交与已提交，避免重复计费；生成文件及时下载至自己控制的持久存储。
- **验收例**：固定两名角色和两句中文对白，要求第 1 镜甲说、第 2 镜乙说、第 3 镜甲说；检查是谁说、说了什么、嘴是否同步、音色是否延续、是否多了旁白；随后仅修改第 2 镜台词，验证其他镜头哈希不变、旧版本仍能打开。

### Gaps

- 无本次真实视频输出，不能报告中文识别准确率、唇同步分数、成本、耗时、成功率或可用性 SLA。
- 未验证任何项目对飞书事件幂等、PPAPI 回调、数据库迁移备份、密钥隔离、长任务重启恢复的完整实现。
- 角色／声音一致性取决于底层模型和接口暴露能力；单靠平台资产管理无法保证。

## 记录维护与证据缺口

### Takeaway

下表记录的是本次 GitHub API 实际返回的 `pushed_at`，统一 UTC，**不是最近功能发布日，也不能推出维护质量或社区规模**。没有使用虚构 star 数、commit 数或“成熟稳定”标签。

### Cited Findings

| 项目 | 实际观察的 `pushed_at` | 维护证据与边界 |
|---|---|---|
| LocalMiniDrama | `2026-11-17T00:46:43Z` | API 未归档；README v1.2.9 助手更新；非长期稳定性证明。[元数据](https://api.github.com/repos/xuanyustudio/LocalMiniDrama) |
| Jellyfish | `2026-07-30T02:19:18Z` | API 未归档；距调研数月，不能称近期高频维护。[元数据](https://api.github.com/repos/Forget-C/Jellyfish) |
| Huobao Drama | `2026-11-15T18:05:56Z` | API 未归档；README 有当前部署和历史迁移说明。[元数据](https://api.github.com/repos/chatfire-AI/huobao-drama) |
| CineGen-ShortDrama | `2026-09-25T12:53:16Z` | API 未归档；README 已明确浏览器存储和自定义许可。[元数据](https://api.github.com/repos/UllrAI/CineGen-ShortDrama) |
| comfyui-AICG3D | `2026-11-15T02:25:40Z` | API 未归档；README 记录至 v1.1.31 安全修复，属于作者声明而非本次审计。[元数据](https://api.github.com/repos/JGRFW/comfyui-AICG3D) |
| Open-AI-Micro-Drama-Generator | `2026-08-02T09:36:28Z` | API 未归档；源码存在演示占位回退，不应按宣传做生产保证。[元数据](https://api.github.com/repos/Anil-matcha/Open-AI-Micro-Drama-Generator) |
| AI Story | `2026-10-13T05:10:50Z` | API 未归档；README 导演模式仍写开发中。[元数据](https://api.github.com/repos/xhongc/ai_story) |
| NarratoAI | `2026-10-24T17:22:04Z` | API 未归档；README 自述 2026-07-16 发布 0.8.6，应与 pushed_at 分开。[元数据](https://api.github.com/repos/linyqh/NarratoAI) |
| MoneyPrinterTurbo | `2026-11-17T09:47:50Z` | API 未归档；本次读取功能表已列 H3 视频素材。[元数据](https://api.github.com/repos/harry0703/MoneyPrinterTurbo) |
| Director | `2026-11-14T15:25:50Z` | API 未归档；README 有部署和自定义 agent 文档。[元数据](https://api.github.com/repos/video-db/Director) |

### Inferences

- 新近项目、频繁更新、版本号高或营销模型名新，均不代表久经验证。本次未收集创建日期和维护者分布，因此不对具体项目武断标注“只成立几天”。
- 近期 pushed_at 可能只是赞助链接或 README 更新；应在实施前固定 commit、复核关键文件、运行无付费测试，再做最小付费验证。
- 源码中有占位视频回退，比没有视频生成功能更容易产生错误成功信号；需要显式禁止以示例视频冒充真实生成结果。

### Gaps

- 搜索覆盖的关键词包括 `AI short drama storyboard`、`AI video director`、`NarratoAI`、`MoneyPrinterTurbo`、`AI 短剧`；搜索遇到一次 SSL EOF，后续仓库直接读取成功；之后 GitHub API rate limit 403，停止 API 扩展。未使用失败的搜索服务，也未规避访问控制。
- 仓库默认分支内容可能改变；本次保存了原始 README 与元数据在 [pipeline_sources.json](</Users/sunqian/Desktop/Projects/Demo/GenerateVideos/research_notes/飞书 中文剧情视频 开源项目调研/pipeline_sources.json>)，阅读摘录在 [pipeline_extracts.md](</Users/sunqian/Desktop/Projects/Demo/GenerateVideos/research_notes/飞书 中文剧情视频 开源项目调研/pipeline_extracts.md>)，实际源码和 ACL／部署文件摘录在 [pipeline_code_checks.md](</Users/sunqian/Desktop/Projects/Demo/GenerateVideos/research_notes/飞书 中文剧情视频 开源项目调研/pipeline_code_checks.md>)。未固定所有源文件 commit permalink，实施前应补齐。
- 没有逐仓审计所有许可证、依赖许可证与权重授权。仅 LocalMiniDrama MIT、Jellyfish Apache-2.0、CineGen ACL 全文已读；其他按 README／API 证据明确区分，不能扩大授权解释。
