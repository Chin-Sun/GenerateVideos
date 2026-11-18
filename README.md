# 构建飞书中文对白剧情机器人

为个人飞书会话保存可恢复的多镜头工程，以 PPAPI MiniMax-H3、FFmpeg 与官方飞书 SDK 实现生成、局部修订和投递。

**当前为开发中的本地 MVP，真实中文逐字台词与口型尚未验收。默认禁止付费调用，不部署云服务。**

## 了解能力

- 持久任务与固定收件人，避免进程重启丢任务和异步串聊。
- 不可变项目版本与镜头资产复用，避免修改一句话覆盖旧工程。
- 原始音轨与质量状态分离，避免将旁白、合成测试片或 API 成功冒充真人物中文对白。
- 官方 SDK 薄接入与本地 FFmpeg 合成，避免为个人使用部署多套平台。

## 启动开发

本节帮助开发者安装锁定环境并验证骨架。需要 Python 3.13～3.14、uv、FFmpeg 和 ffprobe；本机已验证 Python 3.14.6 与 FFmpeg 8.1.2。

```bash
UV_CACHE_DIR="$PWD/.uv-cache" uv sync --frozen
.venv/bin/python -m pytest tests/test_skeleton.py -q
.venv/bin/uvicorn drama_bot.app:app --host 127.0.0.1 --port 8000
```

预期测试通过；访问 `http://127.0.0.1:8000/healthz` 返回以下内容。健康检查不代表生成、投递或质量已通过。

```json
{"status":"ok","generation_quality":"unverified"}
```

本地数据库和资产默认写入 `var` 目录。生产存储选 PostgreSQL，配置 `DRAMA_DATABASE_URL` 为 `postgresql+psycopg://...`，不要将连接凭据提交。空租户与用户白名单拒绝访问，`DRAMA_PAID_CALLS_ENABLED` 默认关闭。画幅暂用 `9:16`，可通过 `DRAMA_DEFAULT_ASPECT_RATIO` 修改，不视作用户已确认。

## 阅读工程

| 位置 | 用途 |
|---|---|
| [架构契约](<docs/architecture.md>) | 数据结构、租约、版本、权限、质量门与成员路径所有权 |
| [共享接口](<src/drama_bot/contracts.py>) | core 与 media 的输入、输出和异常协议 |
| [安全配置](<src/drama_bot/config.py>) | 白名单、付费禁用和服务凭据配置 |
| [应用入口](<src/drama_bot/app.py>) | FastAPI 装配与健康检查 |
| [骨架测试](<tests/test_skeleton.py>) | 默认安全状态与质量证据约束 |
| [锁定依赖](<uv.lock>) | 全部直接及传递依赖精确版本 |

核心实现见 [core 服务](<src/drama_bot/core/service.py>)，媒体实现见 [H3 适配器](<src/drama_bot/media/provider.py>)，装配见 [runtime](<src/drama_bot/runtime.py>)。完整配置、飞书应用权限、能力缺口、备份恢复与真实三镜验收见 [操作说明](<docs/operations.md>)。容器配置见 [Compose](<compose.yaml>) 与 [Dockerfile](<Dockerfile>)，本次未启动容器或云部署。

离线完整演示使用真实 FFmpeg，但供应商与投递均为明确标注的测试夹具：

```bash
.venv/bin/python -m drama_bot.demo --output var/demo-first
```

预期生成两个约 60 秒测试片及报告，完成六镜创建、去重、恢复、s2 修订、其余五镜复用和假投递。输出目录必须不存在。彩色图案与正弦音不是真实中文对白，禁止上传冒充成片。

## 区分验收

运行 `.venv/bin/python -m pytest -q` 检查当前已存在的全部离线测试。离线通过只证明代码和合成流程，不证明模型中文发音或口型。真实验收必须另行授权、设定预算，保存原始输出与人工逐镜评审证据；TTS 和口型仅保留扩展接口，没有伪造实现。

常见问题：为什么付费生成被拒绝？默认关闭且预算为零是设计要求，不能为了跑通演示而取消保护。为什么测试片不算成片？测试素材不包含真实演员对白证据。

术语：outbox 是持久投递记录；租约是限时任务执行权；`unknown_submission` 表示供应商可能已受理，需要对账而非盲目重试。
