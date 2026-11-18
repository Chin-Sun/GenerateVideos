# 运行与验收本地剧情机器人

本文面向本地操作员，目标是运行离线闭环、配置飞书接入并理解尚未验证的能力。本文提供部署文件，但本次没有启动容器、部署云服务或调用付费生成。

导航：[运行离线演示](#运行离线演示) · [配置运行进程](#配置运行进程) · [配置飞书应用](#配置飞书应用) · [核对能力矩阵](#核对能力矩阵) · [备份与恢复](#备份与恢复) · [验收真实三镜](#验收真实三镜)。

## 运行离线演示

本节产出为 SQLite 工程、两个约 60 秒合成测试片、工程清单与演练报告。测试片是彩色图案加正弦音，不是中文剧情；不会上传到飞书。

```bash
UV_CACHE_DIR="$PWD/.uv-cache" uv sync --frozen
.venv/bin/python -m pytest -q
.venv/bin/python -m drama_bot.demo --output var/demo-first
```

预期输出报告包含 `synthetic=true`、`quality=unverified`、`paid_submissions=0`、`network_deliveries=0`、两次离线投递记录、两段约 60 秒时长及 `unchanged_shots_reused=5`。输出目录必须不存在，重复执行换新目录，不覆盖资产。演示在数据库中预置已知的夹具任务 ID，验证重启恢复路径；不伪称验证了真实模型提交。

演示步骤为创建六镜工程、重放事件验证去重、每步重建 worker、真实 FFmpeg 合成、假 transport 记录固定目标、修改 s2、复用其他五镜资产，再合成和导出清单。完整 ZIP 导出另通过 HTTP 路由测试覆盖。

## 配置运行进程

本节产出为本地 CPU 控制面。配置模板见 [.env.example](<../.env.example>)，装配见 [runtime](<../src/drama_bot/runtime.py>)。

配置统一使用 `DRAMA_` 前缀。Compose 从 `.env` 注入；直接运行 Python 时必须显式导出环境变量，程序不会自动读取 `.env`。适配器旧环境变量由装配桥接，不需要重复设置。

| 参数 | 默认值与用途 |
|---|---|
| `DRAMA_DATABASE_URL` | 本地 SQLite；Compose 覆盖为 PostgreSQL |
| `DRAMA_ASSET_ROOT` | `var/assets`；Compose 覆盖为 `/data/assets` |
| `DRAMA_ALLOWED_USER_IDS`、`DRAMA_ALLOWED_TENANT_IDS` | JSON 数组，默认空列表，拒绝全部用户 |
| `DRAMA_LOCAL_API_TOKEN` | 本地 Bearer token，不设置则所有业务 HTTP 请求拒绝 |
| `DRAMA_LOCAL_TENANT_ID`、`DRAMA_LOCAL_USER_ID`、`DRAMA_LOCAL_CHAT_ID` | 固定 HTTP 操作者，不接受请求体伪造身份 |
| `DRAMA_PPAPI_BASE_URL`、`DRAMA_PPAPI_API_KEY` | 显式 HTTPS 地址及密钥，默认空，不猜生产地址 |
| `DRAMA_DOWNLOAD_ALLOWED_HOSTS` | 结果 CDN 域名精确白名单，默认空；禁止私有 IP、重定向和代理继承 |
| `DRAMA_PAID_CALLS_ENABLED` | 默认 `false`，本次必须保持关闭 |
| `DRAMA_PAID_AUTHORIZATION_ID`、`DRAMA_MAX_PAID_SUBMISSIONS` | 独立授权标识与次数封顶，默认空和零；次数不是货币预算 |
| `DRAMA_ALLOW_UNVERIFIED_PREVIEW` | 默认 `false`，只有显式批准才允许真实但未验收素材以草稿发送 |

```bash
.venv/bin/python -m drama_bot.runtime init-db
.venv/bin/uvicorn drama_bot.app:app --host 127.0.0.1 --port 8000
# 另一个终端，使用同样环境变量
.venv/bin/python -m drama_bot.runtime worker
```

预期 `/healthz` 返回进程健康且质量未验证，`/readyz` 完成数据库 `SELECT 1`。以上是未来操作命令，不要求启动与当前 GUI 争用的服务器。worker 每次完成处理写心跳；容器允许最长 900 秒，涵盖最多 600 秒渲染。任务自身租约单独续期，健康检查不代替任务 fencing。

[Compose 文件](<../compose.yaml>) 包含 CPU app、worker、PostgreSQL、顺序初始化和可选飞书 ingress；未加入 GPU、S3 或 Redis。app 仅暴露到主机 loopback，数据库不发布端口。容器以非 root 用户运行，共享 `/data` 持久卷。`POSTGRES_PASSWORD` 使用 URL 安全随机字符，否则应另编码数据库连接 URL。

```bash
cp .env.example .env
# 手工填写本地密钥与白名单，保持 paid calls 关闭
# 仅在你明确决定本地启动容器后执行
# docker compose config --quiet
# docker compose up --build -d
```

预期初始化先完成，数据库、app 与 worker 健康。Dockerfile 和 Compose 是运行配置，不是已验证的云部署；基础镜像及系统 FFmpeg 仍需在目标平台构建测试和固定镜像摘要。当前使用 `create_all` 初始化空库，无 schema 升级迁移引擎；升级既有库前必须备份并另写迁移。

## 配置飞书应用

本节产出为受白名单限制的个人会话入口，不承诺租户审批自动通过。

1. 在 [飞书开放平台](<https://open.feishu.cn/app>) 创建企业自建应用，启用机器人能力，取得 App ID 与 App Secret。
2. 在权限管理申请发送消息及上传文件能力，核对官方控制台当前权限名称，例如 `im:message:send_as_bot`、`im:resource`；为接收单聊申请 `im:message.p2p_msg:readonly`。权限别名可能变化，以控制台对应接口要求为准，不申请无关通讯录或群消息权限。
3. 在事件与回调中选择长连接，订阅 `im.message.receive_v1`。本实现不开放未经鉴权的 HTTP webhook；官方 SDK 长连接负责入口认证。
4. 发布应用版本并由租户批准，限定可用人员。将操作者 `open_id` 和租户 `tenant_key` 填入白名单，勿混用 `user_id` 或 `union_id`。用已知测试账户核对标识，不为发现标识临时开放全部用户。
5. 注入 `DRAMA_FEISHU_APP_ID`、`DRAMA_FEISHU_APP_SECRET`，需要时注入 verification token 和 encrypt key。只保存于本地环境或部署密钥服务，不写到工程清单、代码和聊天中。
6. 显式启动 `.venv/bin/python -m drama_bot.runtime ingress`，或未来本地 Compose 使用 `--profile feishu`。同一应用避免重复运行多套 ingress。

机器人仅接受个人会话文本 `/create ` 加结构化 JSON，不支持自然语言编剧。以下最小示例可创建任务，但默认预算关闭后任务将进入 `blocked`，不会生成：

```text
/create {"name":"三镜验证","target_seconds":30,"shots":[{"shot_id":"s1","prompt":"甲正面中近景，开口说中文","duration_seconds":10,"dialogue":[{"speaker_id":"甲","text":"明天上午九点见。"}]},{"shot_id":"s2","prompt":"乙正面中近景，开口说中文","duration_seconds":10,"dialogue":[{"speaker_id":"乙","text":"好的，林先生，我会准时到。"}]},{"shot_id":"s3","prompt":"甲正面中近景，开口说中文","duration_seconds":10,"dialogue":[{"speaker_id":"甲","text":"请带上三份文件，谢谢。"}]}]}
```

入口持久化去重后快速返回，不等待模型。当前无“创建成功”聊天回执，需通过受保护 HTTP／CLI 查询工程与任务；发送成片采用 MP4 文件消息而非内联视频卡片，缺缩略图适配且飞书真实上传尚未测试。局部修改使用 HTTP 或 CLI 结构化 patch，不宣称已支持自由对话编辑。

## 核对能力矩阵

本节区分已运行代码、离线证据和未验证外部效果。

| 能力 | 当前可用性 | 缺口与诚实边界 |
|---|---|---|
| SQLAlchemy 工程、不可变版本、单镜修订、租约和 outbox | SQLite 离线测试可用 | PostgreSQL 运行及备份恢复待目标环境验证 |
| FastAPI、CLI、固定身份与白名单 | 本地可用 | 不是公开多租户 API，不提供任意身份登录 |
| H3 提交、查询、受限下载 | 官方契约适配与假 HTTP 测试可用 | 缺真实 API 凭据及付费授权，中文台词／口型未验证 |
| 参考图、视频、音频 | 集成入口明确 `capability_blocked` | 尚无对象存储与签名 URL 发布；不得把本地路径发给供应商 |
| FFmpeg 合成与资产哈希 | 真实离线约 60 秒测试通过 | 合成夹具不证明剧情质量，默认 60±5 秒与 9:16 未经用户确认 |
| 飞书长连接、上传及发送 | 官方 SDK 适配与假客户端测试可用 | 缺应用凭据、权限与真实网络验证；合成夹具禁止上传 |
| LLM 编剧／自然语言编辑 | 未配置 | 仅人工结构化分镜与 patch |
| 中文 TTS | 未实现 | `UnsupportedCapability`，没有假音频兜底 |
| 口型生成 | 未实现 | `UnsupportedCapability`，没有假通过状态 |
| S3／云对象存储 | 未实现 | 仅本地文件持久卷，不冒称已集成 S3 |
| GPU 扩展 | 仅 Protocol 边界 | 单独授权后部署独立按需 worker，核模型／权重许可与隐私；不可默认购买 GPU |

预算由 core 在事务中原子预留。media 回调读取持久 `submitting` 意图和有效租约，仅确认已预留操作，不再计费。不确定提交或发送暂停人工对账；重试命令不能绕过未知状态。

## 备份与恢复

本节目标是保存数据库与媒体的一致快照。**以下恢复命令是运维步骤，本次未执行 PostgreSQL 恢复演练，不宣称已有高可用保障。**

本地 SQLite：先停止 ingress 和 worker，使用 Python `sqlite3.Connection.backup` 备份数据库，再归档整个资产根目录。不要仅复制处于写入中的数据库主文件，不能丢掉 WAL 内容。保留数据库 URL 与资产根目录约定，备份不含 API 密钥。

Compose PostgreSQL：先停止写进程，再导出数据库和媒体卷。以实际 Compose 项目执行，备份目录应加密且不公开。

```bash
mkdir -p backups
# 停止入口与执行器，并避免 HTTP 写请求
# docker compose stop ingress worker app
# docker compose exec -T db pg_dump -U drama -d drama -Fc > backups/drama.dump
# docker compose run --rm --no-deps --user root worker tar -C /data -czf - assets > backups/assets.tar.gz
```

预期两个备份文件非空。记录 SHA256 与应用版本，保持一致的一组，不只保存 MP4。恢复到独立测试环境、空数据库和空媒体卷，保留 `/data/assets` 路径，切勿覆盖仍有价值的现有卷：

```bash
# docker compose exec -T db pg_restore -U drama -d drama --no-owner < backups/drama.dump
# docker compose run --rm --no-deps --user root -T worker tar -C /data -xzf - < backups/assets.tar.gz
```

恢复后先保持付费与投递关闭，检查项目版本数、资产哈希、可重新导出工程和重渲染，再检查已知供应商 ID 恢复查询、`unknown_submission`／`unknown_delivery` 不被重发。命名卷不是异地备份；生产需另配私有存储、加密、保留与灾难恢复策略。多机器 worker 不可直接共享各自本地盘，须先实现真正共享存储接口。

### 恢复文件发布崩溃窗口

下载与渲染输出使用 `job_id-attempts-lease_token.mp4`，每次租约领取使用新路径。文件不可覆盖的媒体层保护保持不变，旧 worker 即使晚到发布文件也不能覆盖新 worker 的输出。

| 崩溃点 | 恢复语义 |
|---|---|
| 下载文件发布后、资产登记前 | 旧文件保留为未登记孤儿；租约到期后用新 attempt 路径重新下载。已存供应商任务 ID 不重新提交生成；已存下载 URL 则直接下载 |
| 渲染文件发布后、资产登记前 | 已登记输入资产继续复用，新 attempt 路径重新渲染；旧租约资产登记与任务更新被 fencing 拒绝，事务回滚 |
| 资产登记和任务成功提交后 | `succeeded` 任务不再领取，已登记资产继续引用；render 的 outbox 与成功状态同事务提交，重启只继续投递 |
| 捕获到明确本地失败 | 保留失败阶段，操作员 retry 后领取新 attempt；不能借 retry 重提不确定供应商请求 |

孤儿文件不自动登记为可信素材，也不自动删除。可能发生额外下载和 CPU 渲染，但不会重复付费生成。磁盘容量需监控；未来清理必须暂停写进程，核查所有 `Asset.path` 引用、有效租约及保留期后单独执行，本期没有自动垃圾回收。若供应商下载 URL 过期，仍可能需要人工重新查询／恢复；新路径修复不承诺供应商无限保留结果。

回归命令：

```bash
.venv/bin/python -m pytest tests/core/test_core.py -k 'published_output or render_lease_takeover' -q
```

预期 5 项通过，覆盖下载／渲染发布后的进程死亡、明确失败重试、旧租约回写回滚及成功登记后的复用。使用本地假适配器严格拒绝覆盖已有输出，不涉及网络或真实付费服务。

## 验收真实三镜

本节产出应是用户批准后的证据包，当前不执行。

1. 先确认有限预算、最大提交次数、失败停止条件、素材授权和是否允许第三方托管。保持默认关闭直到获得独立许可。
2. 确认画幅、风格、两个人物、每句逐字台词及期望总时长。当前参考素材出口未实现，先补齐授权存储及角色参考能力，否则不能承诺跨镜头一致。
3. 生成甲说、乙说、甲再说三镜，包含数字、人名和停顿，保存请求摘要、供应商任务 ID、原始视频、哈希、模型信息。禁止用测试夹具或旁白替代。
4. 人工核对逐字准确、说话人对应、可见嘴部起止与闭唇、静默角色不乱动嘴、身份及音色一致。ASR 仅辅助，不用自动分数代替人工通过。
5. 若原生路线失败，记录失败，不默认调用 TTS 或口型。另行核许可、预算与 GPU／托管条件，再实现已有 Protocol。
6. 仅由可信操作员提交绑定资产 ID 的评审证据，三个质量维度全部通过后才能释放正式 outbox。重渲染产物必须重新评审，不自动继承输入通过状态。
7. 再扩展到约 60 秒，并演练下载、上传后发送前重启及单镜修订，核对未改镜头哈希和固定目标会话。

FAQ：为什么没有真实示范视频？本次未获得真实付费生成授权。为什么已拿到 MP4 仍不能正式发送？文件存在不代表角色按指定中文发声且嘴形对应。为什么 S3 不在 Compose 中？本期只实现本地持久卷，加入空服务名不等于完成存储适配。
