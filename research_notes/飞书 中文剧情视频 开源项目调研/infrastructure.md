# 飞书视频机器人与持久项目基础设施调研

研究日期：2026-11-17。范围：公开 GitHub、作者 README/源码/许可证及官方文档；未安装、未部署、未调用付费生成 API。下列“验证”指来源/代码存在，不等于生产测试通过。web_search 仍返回 401；改用公开 GitHub repository search API、repos API、raw.githubusercontent.com 和 GitHub 网页。API 后期触发未认证限额 403，停止 API 扩搜。活动日期取公开 `pushed_at`，并非版本质量或所有功能维护的保证。

## 哪些现成项目最值得复用，哪些是真正的飞书视频集成？

### Takeaway

确实找到两个公开的“飞书＋AI 视频生成/投递”集成：MuseBot 和 Veo/OpenClaw video-gen；后者已读到实际生成、轮询、上传和发送源码。但本次没有验证到完整满足“PPAPI MiniMax-H3、多镜头 60 秒中文角色对话剧情、长期云任务、版本化可编辑项目、对话定点重做”的成品。推荐将这些视为接入参考，而非完整竞品。

### Cited Findings

以下 11 项按集成层级筛选；同一项中的 SDK 或宿主是明确的配套依赖，不冒充独立端到端产品。

| 项目/精确仓库 | 类别与确认能力 | 部署/复用价值 | 许可证与活动证据 |
|---|---|---|---|
| [Feishu Python SDK](https://github.com/larksuite/oapi-sdk-python)；TypeScript 备选 [node-sdk](https://github.com/larksuite/node-sdk) | 官方基础设施；token、签名、事件 dispatch、卡片和媒体 API。Node README 明确含 MP4 上传、流式下载、WebSocket 和机器人示例 | Python/Node 常驻云进程；适合自建最薄接入层。Node 文档示例链接到官方 [lark-samples robot](https://github.com/larksuite/lark-samples/tree/main/react_and_nodejs/robot)；示例不是视频系统 | 均 MIT；[Python API 元数据](https://api.github.com/repos/larksuite/oapi-sdk-python) push 2026-11-16；[Node API](https://api.github.com/repos/larksuite/node-sdk) 2026-10-16。功能依据 [Node README](https://github.com/larksuite/node-sdk/blob/main/README.md) |
| [MuseBot](https://github.com/yincongcyincong/MuseBot) | 已有飞书多模态机器人；飞书专页明确 `/video`；源码 `sendVideo → generateMedia`，上传文件，构造 `MessagePostMedia` 发送 | Go 二进制/容器、云服务器；优先借鉴平台路由、provider 抽象和媒体投递，而非重写机器人。已有多轮聊天不等于版本化视频项目 | MIT；[元数据](https://api.github.com/repos/yincongcyincong/MuseBot) push 2026-11-17；[飞书说明](https://github.com/yincongcyincong/MuseBot/blob/main/static/doc/lark.md)、[实际飞书代码](https://github.com/yincongcyincong/MuseBot/blob/main/robot/lark.go)、[视频配置](https://github.com/yincongcyincong/MuseBot/blob/main/static/doc/videoconf.md) |
| [skill-veo3-video-gen-feishu](https://github.com/ASauler/skill-veo3-video-gen-feishu) | 直接匹配的 OpenClaw 插件/skill：Veo `predictLongRunning` → 每 10 秒轮询 → MP4 下载 → 飞书文件上传 → `msg_type: media`；源码确实存在，不只有营销 README | 需要 OpenClaw、Gemini key、飞书应用配置。最适合读代码理解端到端“短片投递”，不建议原样当生产任务层 | README 声称 MIT，但 GitHub license 字段为 null，根目录 `LICENSE` 请求 404；授权文本不完整，复用前确认。push 2026-03-01；[元数据](https://api.github.com/repos/ASauler/skill-veo3-video-gen-feishu)、[README](https://github.com/ASauler/skill-veo3-video-gen-feishu/blob/main/README.md)、[实际 index.ts](https://github.com/ASauler/skill-veo3-video-gen-feishu/blob/main/index.ts) |
| [LangBot](https://github.com/langbot-app/LangBot) | 多平台机器人平台；README 确认 Lark、Dify、n8n、插件、多轮工具调用 | Docker Compose、自托管、云服务；已有 IM 管理界面和权限控制，适合希望少写接入代码的人；未验证本需求视频工作流 | Apache-2.0；[元数据](https://api.github.com/repos/langbot-app/LangBot) push 2026-11-17；[README](https://github.com/langbot-app/LangBot/blob/master/README.md) |
| [dify-on-lark](https://github.com/duhongming1990/dify-on-lark) | 真实 Dify↔飞书桥接；群/私聊、AI 卡片流式输出、点赞反馈、card action | Java 21/Spring Boot；README 给出 Docker 和 K8s 配置，长连接事件；适合已有 Dify 的用户。不是视频编辑系统 | GitHub license=null，未核得明确授权，不能当成可自由商业复用；push 2026-02-03；[元数据](https://api.github.com/repos/duhongming1990/dify-on-lark)、[README](https://github.com/duhongming1990/dify-on-lark/blob/main/README.md) |
| [n8n-nodes-feishu-lark](https://github.com/zhgqthomas/n8n-nodes-feishu-lark) ＋ [n8n](https://github.com/n8n-io/n8n) | 真实社区节点：LarkTrigger/WebSocket、Webhook parse、Send and Wait、流式消息；附可导入 workflow JSON。作者教程是“AI 生图”，不是已验证 AI 视频剧情 | 自托管 n8n＋社区节点；可承接接收→调用自有 job API→进度卡→人工批准。不能把 workflow execution 历史当完整项目版本库 | 节点 MIT，push 2026-07-24；n8n Sustainable Use License，非无条件 OSI 开源：允许个人/非商业/内部业务，收费托管/分发等不能按 MIT 理解，`.ee` 另需企业许可。n8n push 2026-11-17。[节点 README](https://github.com/zhgqthomas/n8n-nodes-feishu-lark/blob/main/README.md)、[节点元数据](https://api.github.com/repos/zhgqthomas/n8n-nodes-feishu-lark)、[n8n LICENSE](https://github.com/n8n-io/n8n/blob/master/LICENSE.md)、[n8n 元数据](https://api.github.com/repos/n8n-io/n8n) |
| [Remotion](https://github.com/remotion-dev/remotion) | React/TypeScript 编程视频、字幕/转场/合成、交互式预览/编辑基础；不是生成人物动作或口型模型 | Node 渲染服务；保存 composition＋props＋素材引用可再渲染。Web 编辑 UI 仍要做，不是拿到任意 MP4 自动还原工程 | 自定义 Remotion License：个人、最多 3 员工盈利组织等可免费含商业视频制作；较大盈利组织需 Company License；禁止为售卖/出租/再许可自己的 Remotion 衍生物而复制修改代码。许可证注明未来 5.0 变化，应锁版本核验。[LICENSE](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md)；[元数据](https://api.github.com/repos/remotion-dev/remotion) push 2026-11-17；[README](https://github.com/remotion-dev/remotion/blob/main/README.md) |
| [MoviePy](https://github.com/Zulko/moviepy) | Python 剪切、拼接、字幕、叠加、音频混合/编码 | Python＋FFmpeg 云 worker；最简单的 60 秒多片段合成方案。作者说明逐帧数组处理比直接 FFmpeg 慢；v2 有 breaking changes，v1 不再维护 | MIT；[元数据](https://api.github.com/repos/Zulko/moviepy) push 2026-08-26；[README](https://github.com/Zulko/moviepy/blob/master/README.md)。FFmpeg 构建、字体、配乐和模型输出另有权利边界 |
| [OpenTimelineIO](https://github.com/AcademySoftwareFoundation/OpenTimelineIO) | 剪辑时间线交换格式/API；记录片段顺序、长度和外部素材引用；明确不是媒体容器，也不是渲染器 | Python/C++ 库；适合保存可编辑时间线、导出 NLE；0.16 后适配器大多拆为独立包/仓库。应另存剧情、提示词、角色设定、生成依赖 | Apache-2.0；[元数据](https://api.github.com/repos/AcademySoftwareFoundation/OpenTimelineIO) push 2026-11-10；[README](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/README.md) |
| [Pixelle-Video](https://github.com/ATH-MaaS/Pixelle-Video)（旧 AIDC-AI 地址重定向） | 相邻 AI 视频引擎：主题→文案→图片/视频→TTS→BGM→合成；README 更新含数字人口播、图生视频、历史任务和直连视频 API | Python、uv、FFmpeg、WebUI；ComfyUI/RunningHub 或外部模型 API。最值得借鉴的多阶段内容生产流水线，但不能把“解说/数字人口播”当成多人物中文剧情对话保证 | Apache-2.0；[元数据](https://api.github.com/repos/ATH-MaaS/Pixelle-Video) push 2026-06-14；README 2026-06-01 更新直连模型配置；[README](https://github.com/ATH-MaaS/Pixelle-Video/blob/main/README.md) |
| [Temporal](https://github.com/temporalio/temporal) | 持久工作流基础设施；Activity 重试、Workflow 恢复、任务队列、heartbeat checkpoint | Temporal 服务/Cloud＋Python/TS/Go worker；适合跨多镜头、人工确认、多小时重试。个人用自托管成本较高，不必为了一个 bot 首先引入完整集群 | MIT 服务端；Cloud 付费服务另计。push 2026-11-17；[元数据](https://api.github.com/repos/temporalio/temporal)、[README](https://github.com/temporalio/temporal/blob/main/README.md)、[官方 Activity 文档](https://docs.temporal.io/activities) |

**Dify 的独立商业 caveat（桥接项目的依赖，不额外算短名单）：** [langgenius/dify](https://github.com/langgenius/dify) 许可证是修改版 Apache-2.0；多租户 workspace 服务需书面授权，不得移除前端 logo/copyright；不用前端时该前端限制不适用。不能简写成“Apache-2.0，可任意 SaaS 化”。[完整 LICENSE](https://github.com/langgenius/dify/blob/main/LICENSE)

**直接集成的代码级差距：**

- Veo skill 的 `operationName` 仅是 execute 函数局部变量；轮询是内存 `setTimeout`，最多 300 秒；未见提交/轮询状态持久化，成功投递后删除临时 MP4；这份实现不能作为崩溃恢复或长期项目资产保留的证明。[index.ts](https://github.com/ASauler/skill-veo3-video-gen-feishu/blob/main/index.ts)
- 同一代码用模块级 `currentChatId` 记录最近收到的消息，生成完成时读取它发送；异步期间另一聊天可能覆盖目标。即使主要个人使用，也应将 tenant/user/chat/message_id 固定存入每个任务，不能照抄全局目标变量。[index.ts](https://github.com/ASauler/skill-veo3-video-gen-feishu/blob/main/index.ts)
- README/SKILL 文案有“file message”与“media”混用、`duration` 5–8 秒参数但实际生成请求不发送该参数；实际源码调用 `veo-3.0-generate-001` 和 `media`，README 说明固定 8 秒。本次只确认短片生成/投递，不将其模型细节当成当前 Google API 通用约束。[SKILL.md](https://github.com/ASauler/skill-veo3-video-gen-feishu/blob/main/SKILL.md)、[index.ts](https://github.com/ASauler/skill-veo3-video-gen-feishu/blob/main/index.ts)
- MuseBot 飞书 handler 有后台 goroutine、`sendVideo` 和视频上传/媒体发送，足以验证平台集成真实；本次未审完整 `taskflow`/DB/所有 provider 路径，因此不能断言它没有持久能力，也不能认定它已经持久恢复每个视频生成任务。[lark.go](https://github.com/yincongcyincong/MuseBot/blob/main/robot/lark.go)

### Inferences

- 最优先试读/借鉴顺序：**官方 SDK → MuseBot 的飞书视频路径 → MoviePy 或 Remotion → 自有 project/job DB；需要可靠复杂编排时再上 Temporal**。用户主要 Python/快速合成偏 MoviePy；需要浏览器可视化预览和 UI 编辑偏 Remotion。
- LangBot/n8n/Dify-on-lark 是可替代的接入/编排选择，不应全装；个人自用已经确定飞书、单生成 API 时，薄 SDK 方案更小。
- Pixelle 值得拆解其脚本和素材流水线，但人物一致性、中文口型、60 秒剧情节奏是另外的模型/导演问题，不由机器人平台解决。

### Gaps

- 未验证任一项目原生支持 PPAPI MiniMax-H3、60 秒多镜头中文角色演戏、局部镜头重做、非破坏式版本回退的完整组合。不能从“video support”外推。
- Veo skill README 的 MIT 声称缺少独立许可正文；dify-on-lark license=null。商用复制前应找作者确认，不能把公开 GitHub 自动等同开源许可。
- 搜索覆盖不是全网穷尽；另检出 Seedance 飞书字段捷径和 Bitable 视频插件，但未做源码/许可证验证，故不进入主短名单。
- 本次未执行任何 E2E：没有验证飞书 tenant 权限、个人能否开通目标应用、视频大小/编码上限、最终视觉/中文音画质量、API 费用或服务 SLA。

## 哪些模式能真正解决异步恢复、幂等、长期云部署？

### Takeaway

飞书回调是控制入口，不能承载整个视频生成生命周期；长连接也不意味着任务持久。需要把“接收”“生成”“素材保存”“渲染”“投递”拆开，并且单独处理外部付费请求的不确定结果。

### Cited Findings

- 官方 Node SDK 长连接章节说明：收到消息后需 3 秒内完成处理，否则超时重推；多客户端是集群模式，只有一个随机客户端收到事件，不是广播；无需公网 IP/域名但需运行环境可访问公网。[官方 README](https://github.com/larksuite/node-sdk/blob/main/README.md)
- 同一官方 README 旧章节说长连接仅支持 event 而不支持 callback，新 Channel 章节又包含 card interactions；dify-on-lark README 展示长连接卡片 callback。存在文档/版本差异，不能简单承诺所有版本都支持卡片长连接回调，实际部署应固定 SDK 版本并验证目标回调。[Node README](https://github.com/larksuite/node-sdk/blob/main/README.md)、[dify-on-lark README](https://github.com/duhongming1990/dify-on-lark/blob/main/README.md)
- 官方 SDK 提供 MP4 上传、下载流封装；流只能消费一次，用过 writeFile 后再取 stream 会为空/报错。[文件上传下载示例](https://github.com/larksuite/node-sdk/blob/main/README.md)
- Temporal 文档明确 Activity 可以执行服务调用、媒体转码；建议幂等；失败自动按 Retry Policy 重试，单次尝试默认从头开始，只有显式 heartbeat detail 才提供 checkpoint 恢复。它不神奇地令付费供应商提交 exactly-once。[官方 Activities](https://docs.temporal.io/activities)
- n8n 社区节点实际提供 Send and Wait 可暂停等待用户确认，以及 Webhook/流式 demo；这是真实人工确认模式，但 README 未提供本需求视频任务持久化证明。[节点 README](https://github.com/zhgqthomas/n8n-nodes-feishu-lark/blob/main/README.md)

### Inferences

建议最小云架构（工程建议，不是某仓库已实现能力）：

1. **飞书入口**：白名单用户/tenant；接收事件→以 `tenant_id + message_id/event_id` 唯一约束落库→创建 job/outbox→快速返回；后续卡片显示 `project_id/version_id/job_id`。
2. **独立 worker**：提交 PPAPI；先记录提交意图与幂等 key，成功后记录 provider_task_id；轮询以 `next_poll_at` 调度，而非把请求一直挂在回调里。重启扫描未完成 job；provider 提交超时但可能已扣费时，进入 reconciliation/人工确认，不能盲重发。
3. **状态机**：queued → submitting → generating → downloading → assets_ready → rendering → delivering → succeeded；另有 retry_wait、failed、cancel_requested、unknown_submission。每步保存错误分类/尝试次数/心跳/租约。
4. **媒体存储**：临时生成 URL 立即下载到对象存储；保存 checksum、MIME、尺寸、时长、供应商 id 和版权来源；消息只发链接/资源 key，不把 MP4 bytes 塞进工作流历史或 DB JSON。云容器本地盘不是唯一资产库。
5. **投递 outbox**：保存固定 chat_id、目标 user、project version、uploaded file_key 和 sent message_id；上传成功但发送失败时只重投递，不重生成。为发送请求使用稳定业务幂等标识；平台是否支持原生 uuid 去重及有效期需另查官方当前 API。
6. **云运行**：一个轻量 WebSocket bot＋PostgreSQL＋对象存储＋独立 CPU render worker 起步；健康检查/自动重启/备份，生成 API 在远端时本地不需要 GPU。多 worker 用 DB lease/队列锁避免同镜头重复执行。复杂长链或可靠性升级才加 Temporal。
7. **会话不是项目**：聊天记忆仅解析用户意图；项目数据库是事实源。明确指令“把 v3 第 4 镜头对白改为……”必须绑定版本、镜头 ID；同一版本上的并发修订用 optimistic concurrency 防覆盖。

### Gaps

- PPAPI 是否提供 idempotency key、按 client_request_id 查询已提交任务、callback、取消、结果 URL 保留期和 SLA，未在本基础设施调研中确认；以上恢复策略必须根据其真实 API 契约调整。
- 飞书当前单视频大小、格式与 duration 限制及消息 uuid 去重窗口未核验，不提供未经来源支持的数值。
- n8n queue mode 官方网页可访问但正文提取不足，raw 文档旧路径 404；此处不声称已核实其当前 Redis/DB/二进制存储所有配置细节。

## 如何让结果成为可编辑、可版本化的剧情项目而不只是 MP4？

### Takeaway

要同时保存生成语义工程和剪辑时间线；OTIO/Remotion/MoviePy 都不是“把成片反解成可任意改对白的项目”。局部对话修订常常意味着重新生成某个镜头，再合成新版本。

### Cited Findings

- OTIO 明确保存 cut 顺序、长度及外部媒体引用，不包含媒体本体；有 Python/C++ 数据模型、序列化和适配器，可交换多种剪辑格式。[OTIO README](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/README.md)
- Remotion 宣称视频即代码、可程序化/交互式制作，支持 batch rendering 与搭建视频编辑应用；这提供渲染/前端基础，而非默认项目存储服务。[README](https://github.com/remotion-dev/remotion/blob/main/README.md)
- MoviePy 提供切片、拼接、文本、合成、音量调整，适合重跑确定性合成；其 README 明确像素转换处理的性能代价。[README](https://github.com/Zulko/moviepy/blob/master/README.md)
- Pixelle-Video 确认脚本→素材→音声→合成模块化、历史任务与批量生成，但 README 未证明 Git 式版本、镜头依赖追踪或持久恢复的语义。[README](https://github.com/ATH-MaaS/Pixelle-Video/blob/main/README.md)

### Inferences

建议项目数据结构：

- `Project`：owner、角色 bible/参考图、风格、语言、比例、目标 60 秒、权限。
- `ProjectVersion`：不可变 version id、parent version、用户修订原文、解析后的 patch、script/storyboard、模型及参数快照。
- `Shot`：稳定 shot_id、角色、对白原文、说话人、景别/动作/镜头运动、目标/实际时长、reference hashes、generation settings、seed（若支持）、selected take。
- `Asset/Take`：原始 API 输出、音频、字幕、封面、校验和、存储 URI、provider_task_id；生成 URL 不作为永久唯一地址。
- `Timeline`：shot/take 引用、in/out、转场、字幕、音轨、音量；用自有 JSON 作为语义事实源，按需 OTIO 导出；Remotion composition/props 或 MoviePy recipe 是可重复渲染描述。
- `Render`：精确 source version、渲染器版本、字体资源、参数、输出 hash、投递记录。

修订分类：纯字幕/片头/配乐/顺序改动只重渲染；对白文本、角色表演、口型、镜头内容改动一般重生对应 shot；角色外观或场景连续性改动可能影响后续镜头，应显示影响范围/预计费用并确认。v2 使用未改镜头原始 asset，不能覆盖 v1，完成后发“v2 已完成，修改镜头 4；查看 v1/v2”卡片。

对于 60 秒，多镜头长度由模型真实限制和剧情节奏决定，不能把 Veo 插件固定 8 秒或 MuseBot 配置 5/10 秒当作 MiniMax-H3 的限制。严格 60 秒应最终按帧率和实际素材长度校验、剪辑/补足；对白不宜仅靠拉伸速度凑时长。

### Gaps

- 未验证任何候选对“同一角色跨镜头一致、中文声线稳定、多人物轮流说话、口型同步”有目标模型级质量保证。
- 没有执行 timeline 往返导出测试；OTIO 到具体 NLE 的转场、字幕、特效保真度依赖适配器及目标软件，不能承诺全保留。
- 开源代码许可不覆盖模型服务条款、人物肖像/声音授权、字体/配乐素材、生成内容商业使用权；需独立审查。
