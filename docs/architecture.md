# 定义中文对白剧情机器人契约

本文面向 core、media 和集成开发者，目标是在不付费、不云部署的条件下，实现可恢复、可追溯且不伪造对白质量的本地 MVP。

导航：[划分职责](#划分职责) · [保存数据](#保存数据) · [恢复任务](#恢复任务) · [约定接口](#约定接口) · [验收能力](#验收能力)。

## 划分职责

本节产出是文件独占表，模块间仅通过共享契约连接。

```text
飞书官方 SDK → core 事件验权与去重 → PostgreSQL／SQLite
                                   ↓
                              core 租约 worker
                                   ↓
              media PPAPI → 下载资产 → FFmpeg → core outbox
                                                      ↓
                                               media 飞书发送
```

| 所有者 | 独占路径 | 职责 |
|---|---|---|
| architect 初始创建，随后 captain 管理 | `pyproject.toml`、`uv.lock`、`src/drama_bot/contracts.py`、`src/drama_bot/config.py`、`src/drama_bot/app.py`、`tests/test_skeleton.py`、本文及根说明 | 契约、配置、依赖与装配。core、media 只能读取，需变更时发消息请求 captain 协调 |
| core | `src/drama_bot/core/**`、`tests/core/**` | SQLAlchemy 模型、迁移、版本编辑、鉴权、API 路由、持久 worker、outbox 状态及事务 |
| media | `src/drama_bot/media/**`、`tests/media/**` | PPAPI、下载、FFmpeg、官方飞书 SDK transport、未实现的 TTS／口型接口 |
| captain／集成 | `tests/integration/**`、`scripts/**`、其他文档 | 组合注入、端到端离线演练与使用说明 |

core 不导入具体 media 模块，构造服务时注入共享 `Protocol`。media 不读写业务数据库，不维护任务状态，不启动后台轮询。同步方法便于事务前后明确划界，耗时操作在独立 worker 执行，不阻塞飞书事件入口。任何成员不得修改另一成员的文件。

最小栈采用 Python、FastAPI、SQLAlchemy 2、PostgreSQL、SQLite、FFmpeg 和官方 `lark-oapi`，不引入 Redis、Celery、MoviePy、GPU 模型或第三方机器人框架。实际环境为 Python 3.14.6、FFmpeg 8.1.2，依赖精确版本由 `uv.lock` 固定；支持范围为 Python 3.13～3.14，但本次只实测 3.14。生产 PostgreSQL 兼容设计不等于已经运行生产库。

## 保存数据

本节产出是数据库最小约束。JSON 用于不可变语义快照，关系字段用于权限、调度及唯一性。

| 实体 | 必备字段 | 约束 |
|---|---|---|
| `Project` | `id`、`tenant_id`、`owner_user_id`、`head_version_id`、`created_at` | 只能由固定租户和白名单所有者访问 |
| `Version` | `id`、`project_id`、`parent_id`、`number`、`request_text`、`patch_json`、`settings_json`、`created_at` | 项目内版本号唯一，创建后禁止覆盖语义快照 |
| `Shot` | `version_id`、`shot_id`、`position`、`spec_json` | 联合主键，稳定 `shot_id` 跨版本保留；台词含 `speaker_id`、逐字文本、`zh-CN` |
| `Asset` | `id`、`sha256`、`path`、`mime`、`duration_seconds`、`has_audio`、`provenance`、`provider_task_id`、`quality_json`、`license_json` | 原始输出持久保存；哈希校验；临时供应商 URL 不作永久地址 |
| `Job` | `id`、`project_id`、`version_id`、`shot_id`、`kind`、`state`、`identity_json`、`provider_task_id`、`submission_intent`、`lease_owner`、`lease_token`、`lease_expires_at`、`attempts`、`next_run_at`、`error_json`、`result_json` | 创建时固定会话；资产选择写入结果关联而非覆盖版本语义 |
| `Delivery` | `id`、`version_id`、`asset_id`、`identity_json`、`state`、`file_key`、`message_id`、`attempts`、租约字段 | 版本、目标会话和用途唯一；上传与发送分阶段恢复 |
| `EventReceipt` | `tenant_id`、`event_id`、`job_id` | 联合唯一，重复事件返回已有业务任务 |

版本如同已封存的配方，任务结果是另附的制作记录。`Version`、`Shot` 不可变；生成完成只新增 `Asset` 和任务结果映射。渲染固定版本、镜头顺序及已选资产哈希，不能读取“最新版本”替代目标版本。导出包含语义清单、全部引用素材和哈希，不只导出 MP4。

例如基于 v1 修改 s2 台词，应事务创建 v2，复制其余镜头快照及已有资产引用，只将 s2 资产选择置空。使用 `expected_head_version_id` 做 compare-and-swap，旧 head 不匹配返回 `409`。v1 的镜头、资产和渲染结果均保留。资产缺失返回明确错误，不伪称可无损重做。

画幅默认 `9:16`，可配置为 `16:9` 或 `1:1`，只是工程暂定值，**不是用户已确认偏好**。目标 60 秒，初始容差 5 秒也仅为本地验收参数，真实成片容差须确认。建议 6 个 10 秒镜头，但每镜支持 4～15 秒，不拉伸台词凑时长。

## 恢复任务

本节产出是外部副作用的恢复规则。

```text
queued → submitting → generating → downloading → assets_ready
       → rendering → delivering → succeeded
异常：retry_wait／failed／unknown_submission／cancel_requested
```

- 以数据库事务条件更新领取任务，只有租约已过期且 `next_run_at` 到期的可执行状态允许领取。PostgreSQL 可用 `FOR UPDATE SKIP LOCKED`；SQLite 使用原子条件更新，不假设支持行锁。
- 每次领取生成新的 `lease_token`，心跳、完成、错误保存均要求 token 相等，防止过期 worker 回写。长下载和渲染需要续租，重启不依赖内存队列。
- 调用 `submit` 前提交 `submitting` 和提交意图。拿到供应商 ID 后持久化再轮询。过期 `submitting` 没有 ID 时进入 `unknown_submission`，不得自动重发。
- `UnknownSubmission` 表示可能已被供应商受理；超时、连接中断、解析成功响应失败等无法排除受理的情况均需保守处理。不得自造 PPAPI 幂等参数或查询能力。
- 已有 ID 的任务恢复 `poll`；下载采用受控目标路径、临时文件和原子完成，校验后登记资产。失败阶段重试不重新生成已完成镜头。
- `Delivery` 是独立 outbox，和渲染完成记录在同一事务建立。上传得到 `file_key` 后落库；发送失败只继续投递。发送超时转 `unknown_delivery`，未经平台去重契约验证，不盲目重发或承诺 exactly-once。
- outbox 的收件人只来自创建时持久化的 `Identity`，严禁使用最近聊天或全局 `chat_id`。同一用户两个会话交错完成也不得串聊。

默认 `paid_calls_enabled=false`、授权 ID 为空、次数上限为零。真实提交必须同时满足开关、显式授权、有效凭据和原子预算次数预留；本次禁止打开。失败且受理不确定的提交仍占次数，不能借重试绕过额度。空白名单拒绝所有用户与租户，不表示全部允许。

## 约定接口

本节产出是 core 与 media 可独立实现的集成边界。准确字段见共享 [契约文件](<../src/drama_bot/contracts.py>)。

| 接口 | 输入 | 返回与异常 |
|---|---|---|
| `VideoProvider.submit` | `GenerationRequest`，含固定任务、版本和 `ShotSpec` | `Submission.provider_task_id`；禁用时 `PaidCallsDisabled`；受理不确定时 `UnknownSubmission` |
| `VideoProvider.poll` | 已保存的任务 ID | `PollResult`，状态为 `pending`、`succeeded` 或 `failed` |
| `VideoProvider.download` | 经验证 URL、目标路径 | `AssetResult`，实际时长、音轨、哈希及来源 |
| `Renderer.render` | `RenderRequest`，有序资产、版本和目标路径 | `AssetResult`，保留原始对白音轨，缺音轨明确拒绝 |
| `DeliveryTransport.upload` | 已验收资产 | 飞书 `file_key` |
| `DeliveryTransport.send` | 固定 `Identity`、`file_key`、稳定 `delivery_id` | 飞书消息 ID；不确定异常由 core 暂停对账 |
| `SpeechProvider.synthesize` | 中文台词、目标路径 | 未配置实现时抛 `UnsupportedCapability`，不返回伪音频 |
| `LipSyncProvider.synchronize` | 视频、锁定音轨、目标路径 | 未配置实现时抛 `UnsupportedCapability`，不得伪造通过 |

PPAPI 使用 `MiniMax-H3` 与 `POST /v2/video_generation`，结果读取 `task.status`、`task.content.url`。media 必须读取当前官方文档核实轮询路径、认证及精确请求结构，再将内部 `references` 转成供应商字段。首尾帧与 `reference_*` 模式互斥。内部 speaker、台词或 `<d>` 标签不是供应商独立字段，不得擅自声称其具有强制对齐能力。base URL 默认空值，等待显式配置，不猜测生产入口。

建议 core 提供以下受保护 HTTP 路由，最终路由如调整须同步集成说明：

| 方法与路径 | 必备输入 | 成功与错误 |
|---|---|---|
| `GET /healthz` | 无 | `200`，只证明进程存活，质量为 `unverified` |
| `POST /projects` | 鉴权身份、名称、分镜 | `201`，返回项目、版本和任务 ID |
| `GET /projects/{id}` | 鉴权身份 | `200`，项目及版本；越权不泄露数据 |
| `POST /projects/{id}/versions` | `expected_head_version_id`、`shot_id`、允许字段 patch | `201` 新版本；冲突 `409`；非法字段 `422` |
| `GET /jobs/{id}` | 鉴权身份 | `200`，持久状态、失败分类与质量状态 |
| `GET /projects/{id}/export` | 鉴权身份、版本 ID | 工程清单及素材包；缺素材明确失败 |

开发 HTTP 入口仅绑定 loopback，使用本地 Bearer token 并校验用户／租户白名单；不得把任意请求体中的身份当作已认证飞书用户。飞书正式事件由官方 SDK 验证签名／verification token，随后检查白名单与事件去重。密钥不出现在响应、日志、提示词及工程包中。

示例修订请求：

```json
{
  "expected_head_version_id": "v1",
  "shot_id": "s2",
  "patch": {"dialogue": [{"speaker_id": "乙", "text": "明天上午九点见。", "language": "zh-CN"}]}
}
```

预期创建 v2，仅 s2 失效，旧 v1 不变。鉴权缺失返回 `401`，非白名单返回 `403`，版本不匹配返回 `409`。HTTP 请求成功不代表允许付费，付费禁用应保留明确的阻塞状态或 `403` 错误，不回退示例视频。

## 验收能力

本节产出是分层验证清单，而非真实模型验收成绩。

| 测什么 | 为什么 | 怎么做 | 看什么 |
|---|---|---|---|
| 安装与骨架 | 保证锁文件可复现 | `UV_CACHE_DIR="$PWD/.uv-cache" uv sync --frozen`，然后 `.venv/bin/python -m pytest tests/test_skeleton.py -q` | 全部通过，无网络生成 |
| core 持久性 | 防重启丢任务和重复收费 | `.venv/bin/python -m pytest tests/core -q` | 事件去重、租约 fencing、重启轮询、不确定提交阻断、权限隔离 |
| media 契约 | 防字段漂移和丢音轨 | `.venv/bin/python -m pytest tests/media -q` | HTTP 假服务、请求验证、音轨保留、下载边界及付费禁用 |
| 离线集成 | 验证多镜头与版本闭环 | `.venv/bin/python -m pytest tests/integration -q` | 合成测试素材约 60 秒、v2 仅变更单镜、outbox 固定目标 |
| 真实中文质量 | 不能以测试素材冒充人物发声 | 经单独授权生成三个真实短镜，人工复核并保存证据 | 逐字台词、人物对应、可见嘴形、静默角色与跨镜身份均合格 |

后三类测试目录由各责任人创建，不表示骨架阶段已具备全部测试。`QualityEvidence` 默认全部 `unverified`；任一 `passed` 必须有非合成来源、评审者和证据 URI。结构校验不能证明评审真实有效，业务层必须防止未授权外部输入自报通过。未验证视频只能作为显式草稿预览，不能按“已完成中文对白短剧”投递。合成夹具永久标注 `synthetic`，不进入真实质量验收。

参考依据为 [研究报告](<../reports/飞书 中文剧情视频 开源项目调研.md>) 与 [基础设施笔记](<../research_notes/飞书 中文剧情视频 开源项目调研/infrastructure.md>)。本项目仅借设计，不复制候选项目代码；未来复用先核指定 commit 的许可证、依赖及权重。FFmpeg 当前构建启用了 GPL，分发前另审构建许可。用户已有暂存文件、报告和研究资料保持原样，不替用户提交。
