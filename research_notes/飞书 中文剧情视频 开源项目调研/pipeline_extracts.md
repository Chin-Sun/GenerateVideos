
## chatfire-AI/huobao-drama
{"repo": "chatfire-AI/huobao-drama", "default_branch": "master", "pushed_at": "2026-11-15T18:05:56Z", "archived": false, "license": {"key": "other", "name": "Other", "spdx_id": "NOASSERTION", "url": null, "node_id": "MDc6TGljZW5zZTA="}, "description": "🎬 火宝短剧 - 基于AI的一站式短剧生成平台 《一句话生成完整短剧，从剧本到成片全自动化》  Huobao Drama - An AI-Powered End-to-End Short Drama Generator \"One Sentence to Complete Drama: Fully Automated from Script to Final Video\""}
10: [![License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
40: Huobao Drama 是一个基于 AI 的短剧自动化生产平台，实现从剧本生成、角色设计、分镜制作到视频合成的全流程自动化。<br>
45: - **🤖 AI 驱动**：使用大语言模型解析剧本，提取角色、场景和分镜信息<br>
48: - **🎨 智能创作**：AI 绘图生成角色形象和场景背景<br>
52:   **📹 Video Generation**: Text-to-video and image-to-video models automatically produce storyboard clips
54: - **🔄 工作流**：完整的短剧制作工作流，从创意到成片一站式完成<br>
61: backend/    — Hono + Drizzle ORM + Mastra AI Agents + better-sqlite3
69: ## ✨ 功能特性 / Features
71: ### 🎭 角色管理 / Character Management
73: - ✅ AI 生成角色形象<br>
76: - ✅ 批量角色生成<br>
79: - ✅ 角色图片上传和管理<br>
82: ### 🎬 视频任务 / Video Tasks
84: - ✅ AI 自动生成视频任务<br>
90: - ✅ 按任务批量生成视频<br>
109: - ✅ 本地存储支持<br>
112: - ✅ 任务进度追踪<br>
123: | `extractor` |角色 / 场景 / 道具智能提取与去重<br>Intelligent extraction and dedup of characters / scenes / props|
125: | `prompt_generator` |角色/场景/道具图片提示词 + 分镜视频提示词生成<br>Image prompts for characters/scenes/props + storyboard video prompts|
146: |软件<br>Software|版本要求<br>Version|说明<br>Notes|
164: | `SQLITE_PATH` |`<仓库根>/data/huobao.sqlite3`<br>`<repo>/data/huobao.sqlite3`|SQLite 数据库文件位置<br>SQLite database file location|
166: | `STORAGE_PATH` |`<仓库根>/data/static`<br>`<repo>/data/static`|生成文件存储目录<br>Generated-file storage directory|
171: | `PUBLIC_BASE_URL` | — |Seedance 引用本地参考资源时所需的公网地址（服务器部署用）<br>Public URL Seedance needs to reference local assets (server deployments)|
239: 内置 SQLite（`better-sqlite3` + WAL 模式），数据库表在首次启动时自动创建（幂等重放 DDL 与种子数据），默认文件位于 `data/huobao.sqlite3`，可通过 `SQLITE_PATH` 重定向。桌面版数据存放在用户数据目录（`~/Library/Application Support/HuobaoDrama/data/`）。<br>
240: Bundled SQLite (`better-sqlite3` + WAL mode). Tables are created automatically on first launch (idempotent DDL replay + seed data). Default file: `data/huobao.sqlite3`, overridable via `SQLITE_PATH`. The desktop app stores data in the user-data directory (`~/Library/Application Support/HuobaoDrama/data/`).
250: cd backend && npx tsx scripts/import-mysql-to-sqlite.ts
253: > 迁移只覆盖数据库行；旧部署 `data/static/` 下的图片/视频等媒体文件需手动拷贝，否则历史素材无法访问。<br>
258: 启动后所有 AI 功能（文本/生图/视频）都需要先配置模型服务，未配置时页面顶部会有横幅引导：<br>
306: 进入剧集工作台，先粘贴**原始内容**（小说文本），再点「AI 改写」生成拍摄剧本——按集拆分、标注场景与角色，改写时可换文本模型、调语气。满意后「保存并进入制作」。<br>
315: 对剧本执行**提取**，自动获得角色 / 场景 / 道具清单；逐个点「生成形象」产出一致性参考图（也可批量）。生成的资产图会在后续生视频时作为参考素材注入。<br>
330: - 右侧检查 / 微调每个分镜的提示词（`@角色名` 自动映射参考图）<br>
333: - 点「批量生成视频」发起任务，失败任务可一键「重试失败」<br>
347: Select shots (hover to preview each clip), click "Start Merging" and FFmpeg assembles the full episode — play online or download. Click "Mark Done" when finished to light up the progress rail.
362: ## 📦 部署指南 / Deployment
378: **命令行安装（推荐，免修复）**：用 curl 下载不会触发 macOS 隔离属性，安装后双击即开，不会遇到「已损坏」提示（Apple Silicon 把 `arm64` 文件名换成对应版本，Intel 用无后缀 dmg）：<br>
400: # desktop/release/HuobaoDrama-<版本>-arm64.dmg        (Apple Silicon) / desktop/release/HuobaoDrama-<version>-arm64.dmg     (Apple Silicon)
401: # desktop/release/HuobaoDrama-<版本>.dmg              (Intel) / desktop/release/HuobaoDrama-<version>.dmg           (Intel)
402: # desktop/release/HuobaoDrama Setup <版本>.exe        (Windows) / desktop/release/HuobaoDrama Setup <version>.exe     (Windows)
429: - Electron 锁定 37.x：better-sqlite3 的 win32 预编译最高覆盖到该版本的 ABI（交叉打包免编译的关键）<br>
430:   Electron is pinned to 37.x: better-sqlite3's win32 prebuilds max out at that ABI (the key to compilation-free cross-packaging)
445: # 2. 生成版本清单 release/latest.json（含各平台产物 sha256） / 2. Generate the release manifest release/latest.json (with per-platform sha256)
467: ### 🏭 服务器部署方式 / Server Deployment
525: ### 🐳 Docker 部署（含应用内更新） / Docker Deployment (with in-app updates)
531: docker pull huobao/huobao-drama:4.0.6
533: docker run -d \
541: **方式二：docker compose（源码构建 + Watchtower 应用内更新）**：根目录提供一体化 `Dockerfile`（前端 generate + 后端依赖/运行时三阶段，后端与服务器部署一致走 tsx）与 `docker-compose.yml`（应用 + Watchtower）：<br>
542: **Option B — docker compose (source build + Watchtower in-app updates):** the repo root provides an all-in-one `Dockerfile` (three stages: frontend generate + backend dependencies + runtime; the backend runs via tsx just like server deployment) and `docker-compose.yml` (app + Watchtower):
545: # 1. 配置环境（Watchtower 令牌，app 与 watchtower 两侧必须一致） / 1. Configure the environment (Watchtower token — must match on the app and watchtower sides)
548: # 2. 构建并启动（发布时注入版本号，供「关于更新」比对） / 2. Build and start (inject a version at publish time for "About & Updates" comparison)
549: HUOBAO_VERSION=4.0.5 docker compose up -d --build
554: - **数据持久化**：命名卷 `huobao-data` 挂载 `/app/data`（SQLite + 生成的图片/视频 + workspace/skills，更新镜像不丢数据）<br>
557: - **应用内更新**：compose 自带 [Watchtower](https://containrrr.dev/watchtower/) sidecar（`--label-enable` 只更新标记容器，`--cleanup` 清旧镜像，每天自检一次）。设置页「关于更新」可检查新版本并「立即更新」——后端经 Watchtower HTTP API 触发，拉新镜像重建容器，几分钟后刷新页面即可<br>
560: - **手动模式**：`docker-compose.yml` 中删除 app 的 `HUOBAO_WATCHTOWER_*` 两个环境变量（或整个 watchtower 服务）后，「关于更新」退化为新版本提示 + 手动命令 `docker compose pull && docker compose up -d`<br>
561:   **Manual mode**: remove the app's two `HUOBAO_WATCHTOWER_*` env vars (or the whole watchtower service) from `docker-compose.yml` — "About & Updates" then degrades to a new-version notice + manual `docker compose pull && docker compose up -d`
563: - **发布镜像**：`docker buildx build --platform linux/amd64,linux/arm64 --build-arg HUOBAO_VERSION=x.y.z -t huobao/huobao-drama:x.y.z -t huobao/huobao-drama:latest --push .`，版本清单与桌面版共用 GitHub Releases 的 `latest.json`（可用 `HUOBAO_UPDATE_FEED` 覆盖）<br>
564:   **Publishing images**: `docker buildx build --platform linux/amd64,linux/arm64 --build-arg HUOBAO_VERSION=x.y.z -t huobao/huobao-drama:x.y.z -t huobao/huobao-drama:latest --push .` — the version manifest is shared with the desktop app via `latest.json` on GitHub Releases (overridable with `HUOBAO_UPDATE_FEED`)
568: ## 🎨 技术栈 / Tech Stack
578: - **ORM**: Drizzle ORM + better-sqlite3（WAL 模式）<br>
579:   **ORM**: Drizzle ORM + better-sqlite3 (WAL mode)
629: A: 保持 MySQL 可连接（环境变量或 `backend/.env`），执行 `cd backend && npx tsx scripts/import-mysql-to-sqlite.ts`，脚本会自动建表、逐表导入并校验行数（目标库非空需加 `--force`，写入前自动备份）。<br>
630: A: Keep MySQL reachable (environment variables or `backend/.env`), then run `cd backend && npx tsx scripts/import-mysql-to-sqlite.ts`. The script creates tables automatically, imports table-by-table, and validates row counts (non-empty targets require `--force`; a backup is made before writing).
639: A: 这是正常的首次部署引导。前往「设置」页，用「火宝快捷配置」粘贴 API Key 一键写入，或通过「手动模板」按厂商添加。文本、图片、视频三类均有启用中的配置后横幅自动消失。<br>
672: - 数据库从 MySQL 完全迁移到 SQLite（better-sqlite3 + WAL）<br>
673:   Database fully migrated from MySQL to SQLite (better-sqlite3 + WAL)
678:   - 新增一次性导入脚本 `import-mysql-to-sqlite.ts`（逐表行数校验 + 自动备份）<br>
679:     New one-shot import script `import-mysql-to-sqlite.ts` (per-table row-count validation + automatic backup)
681: - 后端 esbuild 单文件打包（externals：sharp/better-sqlite3/ffmpeg 二进制包）<br>
682:   Backend bundled to a single file with esbuild (externals: sharp/better-sqlite3/ffmpeg binary packages)
684: - 移除 Docker/MySQL 部署方式（git 历史可找回）<br>
685:   Removed Docker/MySQL deployment (recoverable from git history)
701: - 批量视频：选择模式 + 生成前确认（镜头数/总时长/模型/分辨率），失败任务一键重试<br>
712: #### 🚀 部署与体验优化 / Deployment & Experience Improvements
714: - Docker 部署就绪改造<br>
715:   Docker deployment readiness
720:   - 数据库初始化增加重试，容器编排下首次部署零人工干预<br>
726:   - Agent skills 目录 volume 持久化（设置页在线编辑不丢失）<br>
729:   - 新增 `docker/init.sql` 及导出脚本（DBA 审核 / 预建表）<br>
730:     New `docker/init.sql` and export scripts (DBA review / pre-created tables)
750: - 工作台：任务列表抽屉、流水线大环节状态、选择性拼接（拼接前校验视频文件存在）<br>
760: - 项目全面迁移至 TypeScript 技术栈<br>
784: - 新增 Docker 部署支持，前后端合并为单镜像<br>
785:   Docker deployment support — frontend and backend merged into a single image
804: - 引入本地存储策略，规避外部资源链接失效<br>
821: - Docker 跨平台支持 host.docker.internal<br>
822:   Docker cross-platform support for host.docker.internal
837: ## 📄 许可证 / License
840: This project is licensed under **[CC BY-NC-SA 4.0](LICENSE)** (Attribution-NonCommercial-ShareAlike 4.0 International).
846:   ✅ Modifications and redistribution allowed under the same license with attribution
848: - ❌ **禁止商用**——未经作者书面许可，不得将本项目整体或部分用于任何商业目的（包括付费服务、商业部署、转售等）<br>
852: Full license text: see [LICENSE](LICENSE).

## UllrAI/CineGen-ShortDrama
{"repo": "UllrAI/CineGen-ShortDrama", "default_branch": "main", "pushed_at": "2026-09-25T12:53:16Z", "archived": false, "license": {"key": "other", "name": "Other", "spdx_id": "NOASSERTION", "url": null, "node_id": "MDc6TGljZW5zZTA="}, "description": "AI Director - AI Manga, Anime, Animation, storyboard, Generation System. 开源 AI 漫剧、动漫、短剧，解说漫、动态漫，生成系统。"}
# CineGen AI Director — AI Manga, Motion Comics & Short Drama Production

[English](./README.md) · [简体中文](./README_ZH.md) · [日本語](./README_JA.md) · [한국어](./README_KO.md)

**CineGen AI Director** is a browser-based production workbench for **AI manga videos, motion comics, animated comics, animatics, and short dramas**. Its **script → assets → keyframes → video** workflow connects story planning, character and scene references, shot design, and video generation in one place. It uses Google Gemini for script and image generation and Veo for video clips.

## Screenshots

![CineGen AI Director AI manga production interface](https://github.com/user-attachments/assets/4d224a09-5752-4ab5-b4ff-a7ba2cc7a666)

![CineGen AI Director motion comic workflow interface](https://github.com/user-attachments/assets/f21eb8ca-913d-4485-8be7-d70911505c79)

![CineGen AI Director shot grid and start/end keyframe editor](./UI.png)

## AI manga and short drama workflow

### 1. Script and storyboard

Enter a story outline or script. Choose the output language and target duration, then use Gemini to structure scenes, characters, and shots with visual prompts and camera directions.

### 2. Characters and scenes

Generate reference images for characters and locations. Create multiple character looks while retaining a base reference for later shots.

### 3. Director workbench

Manage shots in a visual grid. Generate a start frame and, when needed, an end frame for each shot. Scene and character images provide visual context for image generation. Use Veo to generate a video clip from the start frame or from both keyframes.

### 4. Preview and production status

Preview generated clips and review the sequence and shot completion status in the production workspace.

**Why keyframes?** Defining the beginning and optional ending image of a shot gives creators more direct control over composition and transitions than a text prompt alone. Generated results still require review and iteration.

## Run CineGen locally

You need Node.js, npm, and a Google Gemini API key with access to the Gemini and Veo models used by the project. Model availability and billing depend on your Google account and region.

```bash
git clone https://github.com/UllrAI/CineGen-ShortDrama.git
cd CineGen-ShortDrama
npm install
npm run dev
```

Open the local URL printed by Vite (the configured development port is `3000`), enter your Gemini API key, and create a project in **Phase 01**. The application interface is primarily in Chinese; you can choose the generated script's output language in the project settings.

The API key is stored in browser `localStorage`, and projects are stored in browser `IndexedDB`. Clearing site data removes locally saved projects.

## License, AniKuku, and contact

The source is available under the [AniKuku Community License (ACL) v1.0](./license.md). This custom license includes attribution requirements and commercial-use conditions. Read it before using, modifying, distributing, or deploying the project.

[AniKuku](https://anikuku.com/?github) offers a hosted AI manga and motion comic production platform, as well as commercial and private deployment options. For a first purchase, use `CINEGEN50OFF` at checkout for 50% off, subject to AniKuku's current terms.

For collaboration, deployment, or licensing inquiries, contact [visoar@ullrai.com](mailto:visoar@ullrai.com).

## Star History

<a href="https://www.star-history.com/?repos=ullrai%2Fcinegen-shortdrama&type=date&legend=top-left">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=ullrai/cinegen-shortdrama&type=date&theme=dark&legend=top-left" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=ullrai/cinegen-shortdrama&type=date&legend=top-left" />
    <img alt="CineGen-ShortDrama GitHub star history chart" src="https://api.star-history.com/chart?repos=ullrai/cinegen-shortdrama&type=date&legend=top-left" />
  </picture>
</a>


## Forget-C/Jellyfish
{"repo": "Forget-C/Jellyfish", "default_branch": "main", "pushed_at": "2026-07-30T02:19:18Z", "archived": false, "license": {"key": "apache-2.0", "name": "Apache License 2.0", "spdx_id": "Apache-2.0", "url": "https://api.github.com/licenses/apache-2.0", "node_id": "MDc6TGljZW5zZTI="}, "description": "An end-to-end production workspace for AI-generated short dramas. From script input to structured storyboarding, consistency management, shot preparation, video generation, and export."}
# Jellyfish — AI Short Drama Studio

<p align="center">
  <img src="./docs/img/logo.svg" alt="Jellyfish Logo" width="160" />
</p>

<p align="center">
  <a href="https://www.apache.org/licenses/LICENSE-2.0">
    <img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License" />
  </a>
  <a href="https://img.shields.io/badge/frontend-React%20%2B%20Vite-61DAFB">
    <img src="https://img.shields.io/badge/frontend-React%20%2B%20Vite-61DAFB" alt="Frontend" />
  </a>
  <a href="https://img.shields.io/badge/backend-FastAPI-009688">
    <img src="https://img.shields.io/badge/backend-FastAPI-009688" alt="Backend" />
  </a>
  <a href="https://github.com/Forget-C/Jellyfish/actions/workflows/deploy-site.yml">
    <img src="https://github.com/Forget-C/Jellyfish/actions/workflows/deploy-site.yml/badge.svg" alt="Deploy Site" />
  </a>
  <a href="https://github.com/Forget-C/Jellyfish/actions/workflows/ghcr-images.yml">
    <img src="https://github.com/Forget-C/Jellyfish/actions/workflows/ghcr-images.yml/badge.svg" alt="Build and push images" />
  </a>
</p>

<p align="center">
  <a href="./README.md">English</a> ·
  <a href="./docs/README.ja.md">日本語</a>
</p>

An end-to-end production workspace for AI-generated short dramas.  
From script input to structured storyboarding, consistency management,
shot preparation, video generation, and export.

## 📷 Screenshots

| Project overview | Asset management |
| --- | --- |
| <img src="./docs/img/project.png" alt="Project overview" width="420" /> | <img src="./docs/img/%E8%B5%84%E4%BA%A7%E7%AE%A1%E7%90%86.png" alt="Asset management" width="420" /> |

## ✨ Core Value

- **Connect the full production flow**: Move from script input to storyboard preparation, image/video generation, and task tracking in one place.
- **Turn AI output into reusable production assets**: Shots, candidate assets, dialogue, prompts, and generation tasks can all be reviewed and reused.
- **Treat consistency as a first-class problem**: Centralized character, scene, prop, and costume management reduces drift across shots.
- **Handle long-running generation as trackable tasks**: Text, image, and video jobs all go through one async task system with status, cancel, and recovery.
- **Build AI capability as infrastructure**: Model management, prompt templates, files, and OpenAPI-based collaboration make the system extensible.

## ✨ Core Capabilities

Jellyfish is not just a single “AI image/video” utility. It is a
production workspace built around:

- script understanding
- shot preparation
- asset consistency
- generation execution
- task tracking

### 1. AI script understanding and storyboard breakdown

- Split chapter scripts into shots
- Extract characters, scenes, props, costumes, and dialogue
- Run script optimization, simplification, and consistency checks
- Support targeted analysis such as character portraits or scene details

### 2. Shot preparation and confirmation workflow

The main workflow is:

`script breakdown → shot preparation → candidate confirmation → shot ready → generation workspace`

Preparation currently supports:

- extracting and refreshing shot candidates
- accepting or ignoring asset candidates
- accepting or ignoring dialogue candidates
- linking existing characters, scenes, props, and costumes
- correcting shot-level basic information
- using a unified readiness state to decide whether a shot is prepared

### 3. Asset consistency and reuse

The system maintains a shared entity model across:

- characters / actors
- scenes
- props
- costumes

This supports asset reuse across shots and helps stabilize style and identity.

### 4. Shot-level image and video orchestration

Once a shot is `ready`, the generation workspace supports:

- keyframe and reference image management
- shot-level video prompt preview
- image and video generation tasks
- single-shot and batch pre-checks
- writing generation outputs back into the shot/media system

### 5. Unified async task center

Current task infrastructure supports:

- async text-processing tasks
- async image and video generation tasks
- unified task status, result, and elapsed-time tracking
- task cancellation
- a global task center with context-aware navigation back to project/chapter/shot

### 6. Model, prompt, and generation infrastructure

Supporting capabilities include:

- multi-provider / multi-model management
- default model settings by category
- prompt template management
- file and generated media management
- OpenAPI-driven frontend/backend contracts

## 🚀 Feature Overview

### Project and chapter management

- Create and manage projects and chapters
- Use chapters as the unit for scripts, shots, and generation
- Provide dashboard-style entry points and aggregated stats

### AI script processing

- Break chapter scripts into shots
- Extract characters, scenes, props, costumes, and dialogue
- Support optimization, simplification, and consistency checks
- Support focused analysis such as character portraits or scene information

### Shot preparation workflow

- Edit shot title, summary, and basic information
- Refresh extracted asset and dialogue candidates
- Confirm, ignore, or link candidate items
- Use preparation state to determine shot readiness
- Keep “prepared” distinct from “currently generating”

### Asset and entity management

- Manage characters, actors, scenes, props, and costumes
- Link and reuse them at shot level
- Manage entity images
- Check name existence to encourage reuse of existing assets

### Shot generation workspace

- Manage keyframes, reference images, and video prompts
- Check video readiness before generation
- Launch image/video generation tasks
- Support both single-shot and batch generation workflows

### Task center

- View active and recently finished tasks
- Track status, progress, elapsed time, and results
- Cancel tasks
- Jump back to the related project, chapter, or shot

### Model and prompt infrastructure

- Manage providers, models, and default settings
- Manage prompt templates for images, video, and shots
- Generate frontend request helpers and types from OpenAPI
- Provide a stable base for future AI workflow expansion

### File and media management

- Manage uploads and generated outputs
- Preview, link, and reuse image/video assets
- Preserve shot and entity context around generated media

## 🎯 Use Cases

- Short / micro-drama creators
- AI studios producing video content in batches
- Solo creators exploring vertical drama production
- Education and training teams making lesson videos
- Brands and e-commerce teams producing story-driven promos

## 🔁 Frontend OpenAPI client and type generation

Frontend request helpers and types are generated from the backend
OpenAPI spec. Output directory:

- `front/src/services/generated/`

Cached spec file:

- `front/openapi.json`

With the backend dev server running at `http://127.0.0.1:8000`, run:

```bash
cd front
pnpm run openapi:update
```

## 🐳 Docker Compose

The repository includes a ready-to-run compose setup under
`deploy/compose/`.

### Ports

- Frontend: `http://localhost:7788`
- Backend: `http://localhost:8000` (`/docs` for Swagger)
- MySQL: `localhost:${MYSQL_PORT:-3306}`
- Redis: `localhost:${REDIS_PORT:-6379}`
- RustFS: `http://localhost:${RUSTFS_PORT:-9000}`

### Start

```bash
cp deploy/compose/.env.example deploy/compose/.env
docker compose --env-file deploy/compose/.env -f deploy/compose/docker-compose.yml up --build
```

## 🧑‍💻 Local Development

### Backend

```bash
cd backend
cp .env.example .env
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd front
pnpm install
pnpm dev
```

## 📄 License

This project is licensed under [Apache-2.0](./LICENSE).

## 💬 Community & Feedback

- [GitHub Issues](https://github.com/Forget-C/Jellyfish/issues)



## xuanyustudio/LocalMiniDrama
{"repo": "xuanyustudio/LocalMiniDrama", "default_branch": "main", "pushed_at": "2026-11-17T00:46:43Z", "archived": false, "license": {"key": "mit", "name": "MIT License", "spdx_id": "MIT", "url": "https://api.github.com/licenses/mit", "node_id": "MDc6TGljZW5zZTEz"}, "description": "🎬 seedance2接入  开源本地 AI 短剧 & 漫剧生成工具 —— 从故事到成片一站式完成，数据不出本机，短剧工作流管理平台，高灵活度，AI真人剧，AI漫剧本地搞定。 Open-source local AI short drama maker: story → storyboard → video, fully offline, your data stays yours. 纳米流水线"}
<div align="center">

# 🎬 本地短剧助手

**本地 AI 短剧 & 漫剧生成工具 —— 下载即用，完全开源，数据不出本机**

*LocalMiniDrama · AI-powered short drama creator*

[![version](https://img.shields.io/badge/version-1.2.9-blue?style=flat-square)](https://github.com/xuanyustudio/LocalMiniDrama/releases)
[![license](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![platform](https://img.shields.io/badge/platform-Windows-lightgrey?style=flat-square)](#-快速开始)
[![stack](https://img.shields.io/badge/Vue3%20%2B%20Node.js%20%2B%20Electron-informational?style=flat-square)](#-项目架构)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](https://github.com/xuanyustudio/LocalMiniDrama/pulls)

**[English](docs/en.md) · 简体中文 · [作者故事](docs/story.md)**

[![GitHub](https://img.shields.io/badge/GitHub-xuanyustudio%2FLocalMiniDrama-181717?logo=github&style=flat-square)](https://github.com/xuanyustudio/LocalMiniDrama)
[![Gitee](https://img.shields.io/badge/Gitee-bi__shang__a%2Flocalminidrama-C71D23?logo=gitee&style=flat-square)](https://gitee.com/bi_shang_a/localminidrama)
[![AtomGit](https://img.shields.io/badge/AtomGit-xuanyustudio%2FLocalMiniDrama-0052D9?style=flat-square)](https://atomgit.com/xuanyustudio/LocalMiniDrama)

[**⬇️ 下载 Release**](https://github.com/xuanyustudio/LocalMiniDrama/releases) · [**🚀 快速开始**](#-快速开始) · [**📖 配置 AI**](docs/configuration.md) · [**🗺 画布文档**](docs/plans/2026-06-15-drama-canvas-workflow-plan.md)

</div>

---

<table>
<tr>
<td width="25%" align="center"><b>🔒 本地优先</b><br/>SQLite + 本地文件，素材不上云</td>
<td width="25%" align="center"><b>🎬 全流程</b><br/>剧本 → 角色/场景 → 分镜 → 视频合成</td>
<td width="25%" align="center"><b>🤖 多模型</b><br/>通义 / 火山 / 可灵 / Gemini 等</td>
<td width="25%" align="center"><b>🗺 双视图</b><br/>列表精细编辑 + 画布批量编排</td>
</tr>
</table>

市面上 AI 短剧工具不少，但真正能**本地离线运行、开箱即用、素材不上云**的几乎没有。  
本项目用纯 JavaScript 从零搭建，接入你自己的 AI API，打开即可生成完整 AI 短剧。

> ✅ 无订阅费 · ✅ 数据本地存储 · ✅ 支持多家 AI 服务商 · ✅ 完全开源可二次开发

---

## 📌 最新动态（v1.2.9）

- 🆕 **剧内助手**：剧集页、制作页、画布页可对话操作当前短剧（剧本、角色、场景、分镜、出图）；删除需确认
- 🔧 **文本模型**：配置里存了多个模型时，助手使用默认的那一个，不再把整段名单当作模型名
- 🔧 **桌面运行时**：Electron 升到 44，以便在安装包内运行助手

完整记录 → **[CHANGELOG.md](CHANGELOG.md)**

---

## 目录

- [界面预览](#-界面预览)
- [核心功能](#-核心功能)
- [快速开始](#-快速开始)
- [AI 服务商](#-ai-服务商支持)
- [项目架构](#-项目架构)
- [后续计划](#-后续计划-roadmap)
- [参与贡献](#-参与贡献)
- [联系社区](#-联系--社区)

---

## 📸 界面预览

<div align="center">
  <img src="项目截图/首页截图.png" alt="首页 · 项目列表" width="960"/><br/>
  <sub>首页 · 项目卡片一览，亮色模式</sub>
</div>

<br/>

<div align="center">
  <img src="项目截图/画布模式.png" alt="画布工作流 · 分镜流水线" width="960"/><br/>
  <sub>🆕 画布模式 · 分镜流水线可视化 · 节点内编辑/生成 · 工作流整组重跑</sub>
</div>

<br/>

<table>
  <tr>
    <td align="center"><img src="项目截图/武侠.png" alt="剧集管理页" width="480"/><br/><sub>剧集管理 · 分集 + 资源库</sub></td>
    <td align="center"><img src="项目截图/武侠分镜.png" alt="分镜编辑页" width="480"/><br/><sub>分镜制作 · 图片 + 视频一键生成</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="项目截图/新版本4宫格分镜.png" alt="角色管理页" width="480"/><br/><sub>角色生成 · AI 自动提取并生成角色形象图</sub></td>
    <td align="center"><img src="项目截图/专业分镜.png" alt="专业分镜参数" width="480"/><br/><sub>分镜制作 · 专业视频参数（景别 / 运镜 / 灯光 / 景深）</sub></td>
  </tr>
  <tr>
    <td align="center" colspan="2"><img src="项目截图/本剧场景库.png" alt="本剧场景库" width="720"/><br/><sub>场景库 · 一键「加入本集」，复用已有场景素材</sub></td>
  </tr>
</table>

---

## 🎬 AI 生成实拍效果

> 以下 3 段视频由**本软件自动工作流选择即梦 1.0**生成，展示连续分镜下角色外貌一致性。

<table>
  <tr>
    <td align="center">
      <video src="项目截图/1.mp4" controls width="300"></video><br/>
      <sub>分镜 1 · 即梦 1.0</sub>
    </td>
    <td align="center">
      <video src="项目截图/2.mp4" controls width="300"></video><br/>
      <sub>分镜 2 · 服装一致</sub>
    </td>
    <td align="center">
      <video src="项目截图/3.mp4" controls width="300"></video><br/>
      <sub>分镜 3 · 人物统一</sub>
    </td>
  </tr>
</table>

> 💡 同时支持火山 **Seedance 2.0**、通义万相、Vidu、可灵 Kling（含 Omni）等，模型越新效果通常越好。

---

## ✨ 核心功能

<details open>
<summary><b>🔄 完整创作流程（点击展开/收起）</b></summary>

| 步骤 | 功能 | 说明 |
|:----:|------|------|
| 1 | **故事生成** | 输入梗概 + 风格，AI 自动生成多集剧本 |
| 2 | **剧本编辑** | 分集管理，剧本文本可自由编辑 |
| 3 | **角色生成** | AI 提取角色列表，逐个生成角色形象图 |
| 4 | **场景生成** | 从剧本自动提取场景，生成场景背景图 |
| 5 | **道具生成** | 从剧本提取/手动添加道具，生成道具图 |
| 6 | **分镜生成** | 按集自动生成分镜脚本（含景别/运镜/台词） |
| 7 | **图片/视频生成** | 逐镜生成静帧图与视频片段 |
| 8 | **合成视频** | 所有分镜视频自动合成为完整剧集文件 |

</details>

<details>
<summary><b>⚡ 一键流水线 · 项目管理 · 分镜编辑</b></summary>

- **一键生成 / 补全并生成**：从角色到合成视频全自动；智能跳过已有内容
- **失败自动重试**：每步最多 3 次，应对限流；实时进度与错误日志
- **工程 ZIP 导出/导入** · **全局素材库** · **16:9 / 9:16 / 1:1 画幅**
- **经典 / 全能分镜** · **`@图片N` 多图参考** · **尾帧衔接** · **导出分镜表 HTML**
- **图片/视频提示词**全文编辑 · 手动上传/拖拽替换参考图

</details>

### 🗺 画布工作流（LibTV 式）

制作页 / 剧集详情 → **画布模式**（`/film/:id/canvas`），与列表模式**同源数据**：

| 能力 | 说明 |
|------|------|
| 竖排流水线 | 每镜一行：经典「文本→首帧/尾帧→视频」；全能「全能分镜词→视频」 |
| 剧本节点 | 画布起点直接编辑剧本、AI 生成故事、提取角色/场景/道具 |
| 节点操作面板 | 单击节点下方编辑/生成，无需频繁切列表 |
| 右键 / 工具栏 | 新建分镜、集、角色、场景、道具；框选创建工作流 |
| 工作流组 | 框选分镜 → 创建工作流 → **整组重跑**（生图/视频/配音可勾选） |
| 布局持久化 | 拖动保存坐标；曲线连线；左键框选、中键/右键平移 |

界面预览见 [上方截图](#-界面预览) · 📖 [画布工作流完整文档](docs/plans/2026-06-15-drama-canvas-workflow-plan.md)

### 🤖 AI 配置 · 🌓 亮/暗主题 · 自定义提示词

三类模型独立配置（图/视频/文本）；一键配置通义/火山；9 类提示词可自定义覆盖。

---

## 🚀 快速开始

### 方式一：下载 exe（推荐）

前往 **[Releases 下载页](https://github.com/xuanyustudio/LocalMiniDrama/releases)**：

| 版本 | 说明 | 适合 |
|------|------|------|
| `本地短剧助手 x.x.x.exe` | 标准版，**含示例项目** | 新手入门 |
| `本地短剧助手-Lite-x.x.x.exe` | Lite 版，体积更小 | 熟悉流程后 |

双击运行 → 「AI 配置」填入 API Key → 开始创作。

> 首次运行配置：`%APPDATA%\LocalMiniDrama\backend\configs\config.yaml`

### 方式二：源码开发

> Node.js ≥ 18

```bash
git clone https://github.com/xuanyustudio/LocalMiniDrama.git
cd LocalMiniDrama

# 后端（端口 5679）
cd backend-node && npm install
cp configs/config.example.yaml configs/config.yaml   # 填入 API Key
npm run migrate && npm start

# 前端（端口 3013，新终端）
cd frontweb && npm install && npm run dev
```

浏览器打开 `http://localhost:3013`，或双击根目录 **`run_dev.bat`** 一键启动。

📖 [详细开发/打包/Docker 指南](docs/quickstart.md) · [AI 配置指南](docs/configuration.md)

---

## 🤖 AI 服务商支持

| 服务商 | 文本 | 图片 | 视频 |
|--------|:----:|:----:|:----:|
| 阿里云 DashScope（通义） | ✅ | ✅ | ✅ |
| 火山引擎 Volcengine（豆包 / Seedance 2.0） | ✅ | ✅ | ✅ |
| 可灵 Kling AI（含 Omni） | — | ✅ | ✅ |
| Agnes AI | ✅ | ✅ | ✅ |
| Google Gemini（Imagen / Veo） | — | ✅ | ✅ |
| Vidu 生数科技 | — | — | ✅ |
| NanoBanana（含代理） | — | ✅ | — |
| 本地 Ollama 等 OpenAI 兼容 | ✅ | — | — |
| 其他 OpenAI 兼容接口 | ✅ | ✅ | — |

---

## 🏗 项目架构

```
LocalMiniDrama/
├── backend-node/     # Express + SQLite，生成/合成/导入导出
├── frontweb/         # Vue 3 + Element Plus + @vue-flow/core
│   └── views/        # FilmList · DramaDetail · FilmCreate · DramaCanvas
├── desktop/          # Electron 打包 exe
└── docs/             # 文档与计划
```

| 层 | 技术 |
|----|------|
| 前端 | Vue 3 · Vite · Element Plus · Pinia · @vue-flow/core |
| 后端 | Node.js · Express · SQLite (better-sqlite3) |
| 桌面 | Electron 28 · electron-builder |

---

## 🗺 后续计划 Roadmap

| 状态 | 计划 | 说明 |
|:----:|------|------|
| ✅ | Seedance 2.0 + 全能模式 | 多图 `@图片N` · `universal_segment_text` |
| ✅ | 画布工作流 | 列表/画布双视图 · 整组重跑 · 节点面板 |
| 📋 | **场景图 → 全景图** | 由场景参考图 AI 扩展超宽/360° 全景，供大景别运镜与场景库 |
| 📋 | 分镜参考图自由上传 | 任意图片作为分镜参考 |
| 📋 | 参考图自由选择 | 生图时手动指定角色/场景参考 |
| 📋 | 宫格图生成视频 | 多帧合图作为视频输入（部分模型已支持） |

> 认领功能或提建议 → [New Issue](https://github.com/xuanyustudio/LocalMiniDrama/issues/new)

<details>
<summary><b>📋 更多历史版本亮点（v1.2.3 及更早）</b></summary>

- **v1.2.3** 分镜解说旁白 · 导出解说 SRT
- **v1.2.2** 连贯帧模式 · 小说/长文导入 · ffmpeg 自动解压
- **v1.2.1** 可灵 Kling · 视频历史版本 · 场景/道具「加入本集」
- **v1.1.x** 多集剧本 · AI 并发 · 四宫格 · 批量生图/视频 …

详见 **[CHANGELOG.md](CHANGELOG.md)**

</details>

---

## 🎯 适合谁

| 用户 | 场景 |
|------|------|
| 📹 内容创作者 | 批量生产 AI 短剧 / 漫剧 |
| 🔒 隐私敏感 | 素材与剧本完全留在本机 |
| 🛠 开发者 | 二次开发、接入新 AI 服务商 |
| 🌱 入门探索 | 低成本体验 AI 视频全流程 |

---

## 🤝 参与贡献

- 🐛 [报告 Bug](https://github.com/xuanyustudio/LocalMiniDrama/issues/new)
- 💡 [功能建议](https://github.com/xuanyustudio/LocalMiniDrama/issues/new)
- 🔧 Fork → PR
- ⭐ **Star** 帮助更多人发现本项目

**GitHub 仓库建议 Topics**（在仓库 Settings → Topics 添加，便于搜索）：  
`ai-video` `short-drama` `storyboard` `vue3` `electron` `local-first` `seedance` `comic-drama`

---

<details>
<summary><b>☕ 一杯咖啡的鼓励</b></summary>

项目完全开源、无订阅。若对你有帮助，欢迎随缘打赏（自愿，不影响 Issue/PR 处理）：

<table>
  <tr>
    <td align="center"><img src="项目截图/weixinpay.jpg" alt="微信赞赏码" width="200"/><br/><sub>微信支付</sub></td>
    <td align="center"><img src="项目截图/ali.jpg" alt="支付宝收款码" width="200"/><br/><sub>支付宝</sub></td>
  </tr>
</table>

</details>

---

## 💬 联系 & 社区

[作者故事 & 碎碎念](docs/story.md) · 微信交流 / 用户群（二维码见仓库 `项目截图/` 目录）

> 群二维码约 7 天有效，过期请加作者微信拉群。

---

## 📄 License

[MIT](LICENSE)

---

<div align="center">

**如果这个项目对你有帮助，请点 ⭐ Star —— 这是对作者最大的鼓励！**

[⬇️ 立即下载](https://github.com/xuanyustudio/LocalMiniDrama/releases) · [📖 快速开始文档](docs/quickstart.md) · [🗺 画布文档](docs/plans/2026-06-15-drama-canvas-workflow-plan.md)

</div>


## Anil-matcha/Open-AI-Micro-Drama-Generator
{"repo": "Anil-matcha/Open-AI-Micro-Drama-Generator", "default_branch": "main", "pushed_at": "2026-08-02T09:36:28Z", "archived": false, "license": null, "description": "AI short drama & micro-drama video generator — turns any idea into a complete short-form drama using multi-agent AI pipeline (screenwriter → storyboard → frames → video). Seedance 2 VIP, Kling 3.0 Pro, Veo 3.1, Sora 2."}
<div align="center">

<h1 align="center">MicroDrama AI</h1>
<h3 align="center">Agentic AI Micro-Drama Video Generator</h3>

<p align="center">
  <img src="https://img.shields.io/badge/🐍Python-3.10+-00d9ff?style=for-the-badge&logo=python&logoColor=white&labelColor=1a1a2e">
  <img src="https://img.shields.io/badge/⚡Next.js-14-ff6b6b?style=for-the-badge&logo=next.js&logoColor=white&labelColor=1a1a2e">
  <img src="https://img.shields.io/badge/License-MIT-4ecdc4?style=for-the-badge&logo=opensourceinitiative&logoColor=white&labelColor=1a1a2e">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/MuAPI-Powered-7c3aed?style=for-the-badge&logoColor=white&labelColor=1a1a2e">
  <img src="https://img.shields.io/badge/One_Key-Setup-FFC107?style=for-the-badge&logoColor=white&labelColor=1a1a2e">
</p>

</div>

---

### 🚨 The problem with AI video today:
- ❌ **Manual, fragmented workflow** — Separate tools needed for scripting, image gen, and video gen
- ❌ **No narrative structure** — Raw T2V models don't understand story arcs or scene continuity
- ❌ **Character inconsistency** — Characters look different in every shot
- ❌ **Visual-only** — Missing scripts, narrative depth, and cinematic storytelling

### 💡 MicroDrama AI Solution:
🎬 **Screenwriter**, **Storyboard Artist**, **Frame Generator**, and **Video Producer** — all in one automated pipeline.

Type an idea. MicroDrama AI autonomously handles everything: story development, character design, shot-by-shot storyboarding, frame generation, and video clip production — then stitches it all into a complete cinematic micro-drama. Powered entirely by a single MuAPI key.

---

<p align="center">
  <a href="https://github.com/Anil-matcha/awesome-generative-ai-apps">
    <img src="https://img.shields.io/badge/Part%20of-Awesome%20Generative%20AI%20Apps-FFD700?style=for-the-badge&logo=github&logoColor=black" alt="Awesome Generative AI Apps">
  </a>
</p>

> 🎨 **[Explore 50+ more open-source AI apps →](https://github.com/Anil-matcha/awesome-generative-ai-apps)**

## Related Projects

- [Seedance 2.5 on MuAPI](https://muapi.ai/seedance-2.5) — Model landing page for the cinematic video workflow.
- [Seedance 2.5 text-to-video playground](https://muapi.ai/playground/seedance-2.5-text-to-video) — Try the model used for short-form scenes.
- [AI-Youtube-Shorts-Generator](https://github.com/SamurAIGPT/AI-Youtube-Shorts-Generator) — Auto-clip and crop your AI dramas into viral YouTube Shorts
- [Clip-Anything](https://github.com/SamurAIGPT/Clip-Anything) — Clip any moment from your AI drama with text prompts
- [AI-Faceless-Video-Generator](https://github.com/SamurAIGPT/AI-Faceless-Video-Generator) — Generate faceless AI videos for your drama channel
- [awesome-ai-video-models](https://github.com/Anil-matcha/awesome-ai-video-models) — compare AI video models by API, price & speed
- [ai-creator-academy](https://github.com/Anil-matcha/ai-creator-academy) — free curriculum teaching creators how to monetize AI micro-dramas and video content

## 🎥 Demo Video

https://github.com/user-attachments/assets/f8b5d09c-8c58-40c1-b171-e3f42b0d71a8

Watch MicroDrama AI transform ideas into fully cinematic micro-drama videos using autonomous AI agents, character-consistent image generation, storyboarding, and MuAPI-powered video creation.

---



## 📑 Table of Contents

- [💡 Key Features](#-key-features)
- [🏗️ Architecture](#%EF%B8%8F-architecture)
- [🔄 Pipeline Stages](#-pipeline-stages)
- [🚀 Quick Start](#-quick-start)
- [🛠️ Project Structure](#%EF%B8%8F-project-structure)
- [🌐 API Reference](#-api-reference)
- [⚙️ Configuration](#%EF%B8%8F-configuration)
- [🖥️ UI Overview](#%EF%B8%8F-ui-overview)

---

## 💡 Key Features

<table align="center" width="100%">
<tr>
<td width="25%" align="center" valign="top" style="padding: 20px;">

### 🎭 Idea to Video
**From Spark to Screen**

Transform a raw idea into a complete micro-drama. The AI develops the story, writes scene scripts, designs the storyboard, and generates the full video — zero manual steps.

</td>
<td width="25%" align="center" valign="top" style="padding: 20px;">

### 📝 Script to Video
**Bring Your Script to Life**

Already have a scene script? Skip the writing phase and let MicroDrama AI handle storyboarding, character portraits, frame generation, and video production.

</td>
<td width="25%" align="center" valign="top" style="padding: 20px;">

### 🎨 Character Consistency
**Coherent Visual Identity**

Characters are extracted with detailed static and dynamic features. Reference portraits are generated and used to keep characters visually consistent across every shot.

</td>
<td width="25%" align="center" valign="top" style="padding: 20px;">

### 📡 Real-time Progress
**Live Pipeline Visibility**

Watch every stage of the pipeline in real time via SSE streaming — from story development through to the final concatenated video, with a live animated stage timeline.

</td>
</tr>
</table>

---

## 🏗️ Architecture

```
                   ┌──────────────────────────────────────────────────────────┐
                   │                MicroDrama AI Server                      │
  Idea / Script ─► │                                                          │
                   │  ┌────────────────────────────────────────────────────┐  │
                   │  │              Screenwriter Agent                     │  │
                   │  │  develop_story()  → write_script_based_on_story()  │  │
                   │  └──────────────────────────┬─────────────────────────┘  │
                   │                             │ story + scene scripts       │
                   │  ┌──────────────────────────▼─────────────────────────┐  │
                   │  │           Character Extractor Agent                 │  │
                   │  │      extract_characters(script) → List[char]       │  │
                   │  └──────────────────────────┬─────────────────────────┘  │
                   │                             │ characters[]               │
                   │  ┌──────────────────────────▼─────────────────────────┐  │
                   │  │           Storyboard Artist Agent                   │  │
                   │  │  design_storyboard() → List[ShotBriefDescription]  │  │
                   │  └──────────────────────────┬─────────────────────────┘  │
                   │                             │ shots[]                    │
                   │  ┌──────────────────────────▼─────────────────────────┐  │
                   │  │                  MuAPI Tools                        │  │
                   │  │  ① Portrait Gen  →  flux-dev-image  (T2I)          │  │
                   │  │  ② Frame Gen     →  flux-kontext-dev-i2i  (I2I)    │  │
                   │  │  ③ Video Gen     →  kling-v2.1-standard-i2v  (I2V) │  │
                   │  └──────────────────────────┬─────────────────────────┘  │
                   │                             │ video clips                │
                   │  ┌──────────────────────────▼─────────────────────────┐  │
                   │  │                moviepy Concat                       │  │
                   │  └──────────────────────────┬─────────────────────────┘  │
                   └────────────────────────────-┼──────────────────────────--┘
                                                 │
                                        final_video.mp4
```

All LLM calls (story, characters, storyboard) go through MuAPI's `/claude-sonnet-4-6` endpoint.
**Only one API key is required for the entire pipeline.**

---

## 🔄 Pipeline Stages

### Idea to Video — Full Pipeline

| # | Stage | Agent / Tool | Output |
|---|-------|-------------|--------|
| 1 | **Story Development** | Screenwriter (MuAPI LLM) | Story outline in prose |
| 2 | **Character Extraction** | CharacterExtractor (MuAPI LLM) | Characters with static + dynamic visual features |
| 3 | **Scene Scripting** | Screenwriter (MuAPI LLM) | 2–4 individual scene scripts |
| 4 | **Character Portraits** | MuAPI `flux-dev-image` (T2I) | Reference portrait per character — runs in parallel |
| 5 | **Storyboard Design** | StoryboardArtist (MuAPI LLM) | 3–5 shots per scene: visual + motion + audio desc |
| 6 | **Frame Generation** | MuAPI `flux-kontext-dev-i2i` (I2I) | First frame per shot using character reference images |
| 7 | **Video Generation** | MuAPI `kling-v2.1-standard-i2v` (I2V) | 5-second video clip per shot — runs in parallel |
| 8 | **Concatenation** | moviepy | All clips joined into `final_video.mp4` |

### Script to Video — Short Pipeline

Skips stages 1–3. Starts directly from your provided script.

| # | Stage | Agent / Tool | Output |
|---|-------|-------------|--------|
| 1 | **Character Extraction** | CharacterExtractor (MuAPI LLM) | Characters with visual descriptions |
| 2 | **Character Portraits** | MuAPI `flux-dev-image` (T2I) | Reference portrait per character |
| 3 | **Storyboard Design** | StoryboardArtist (MuAPI LLM) | Shots from your script |
| 4 | **Frame Generation** | MuAPI `flux-kontext-dev-i2i` (I2I) | First frame per shot |
| 5 | **Video Generation** | MuAPI `kling-v2.1-standard-i2v` (I2V) | 5-second video per shot |
| 6 | **Concatenation** | moviepy | Final scene video |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- A [MuAPI](https://muapi.ai?utm_source=github&utm_medium=readme&utm_campaign=open-ai-micro-drama-generator) API key

### 1. Clone the repo

```bash
git clone https://github.com/Anil-matcha/Open-AI-Micro-Drama-Generator.git
cd Open-AI-Micro-Drama-Generator
```

### 2. Set up the server

```bash
cd server
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Open .env and set MUAPI_KEY=your_key_here
```

### 3. Start the server

```bash
uvicorn api:app --reload --port 8000
```

API available at `http://localhost:8000`. Health check: `GET /api/health`.

### 4. Set up and start the client

```bash
cd client
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### 5. Generate your first micro-drama

1. Enter an idea — e.g. *"A detective chases a shadow through a neon-lit cyberpunk city"*
2. Optionally add requirements — e.g. *"Keep it under 3 scenes, suitable for all ages"*
3. Pick a visual style: **Cinematic**, Realistic, Anime, Fantasy, or Documentary
4. Click **Generate Video** and watch the pipeline run in real time
5. Download your finished micro-drama when it completes

---

## 🛠️ Project Structure

```
Open-AI-Micro-Drama-Generator/
│
├── server/                           # FastAPI backend
│   ├── api.py                        # App entry point, endpoints, SSE job runner
│   ├── requirements.txt
│   ├── .env.example
│   │
│   ├── agents/                       # LLM-powered AI agents (all via MuAPI)
│   │   ├── screenwriter.py           # develop_story() + write_script_based_on_story()
│   │   ├── character_extractor.py    # extract_characters() → List[CharacterInScene]
│   │   └── storyboard_artist.py      # design_storyboard() → List[ShotBriefDescription]
│   │
│   ├── interfaces/                   # Pydantic data models
│   │   ├── character.py              # CharacterInScene (idx, name, static/dynamic features)
│   │   └── shot.py                   # ShotBriefDescription, ShotDescription
│   │
│   ├── tools/                        # MuAPI integration layer
│   │   ├── muapi_llm.py              # MuAPILLM — submit + poll LLM completions
│   │   ├── muapi_image_generator.py  # T2I (flux-dev) + I2I (flux-kontext) image gen
│   │   ├── muapi_video_generator.py  # I2V (kling-v2.1) video gen with polling
│   │   └── muapi_uploader.py         # Upload local images to MuAPI for URL references
│   │
│   ├── pipelines/                    # Orchestration logic
│   │   ├── idea2video.py             # Full end-to-end pipeline
│   │   └── script2video.py           # Scene-level pipeline (portraits → storyboard → video)
│   │
│   └── utils/
│       └── video.py                  # moviepy concatenation helper
│
└── client/                           # Next.js 14 frontend
    ├── next.config.js                # Rewrites /api/* and /outputs/* → FastAPI server
    ├── package.json
    ├── tailwind.config.js
    │
    ├── app/
    │   ├── layout.js                 # Root layout + metadata
    │   ├── globals.css               # Global styles + gradient utilities
    │   ├── page.js                   # Landing page: hero + generation form
    │   └── generate/[jobId]/
    │       └── page.js               # SSE consumer: pipeline progress + result viewer
    │
    └── components/
        ├── IdeaForm.js               # Idea/script input, style picker, mode toggle
        ├── PipelineProgress.js       # Animated 7-stage timeline + live scrolling log
        └── VideoResult.js            # Video player with download + open controls
```

---

## 🌐 API Reference

### `POST /api/generate` — Start a generation job

**Request body:**

```json
{
  "idea": "A lone astronaut discovers alien ruins on Europa",
  "user_requirement": "Keep it under 3 scenes, suitable for all ages",
  "style": "Cinematic",
  "mode": "idea2video"
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `idea` | string | required | The creative idea or concept |
| `user_requirement` | string | `""` | Optional constraints (audience, length, tone) |
| `style` | string | `"Cinematic"` | Visual style: Cinematic, Realistic, Anime, Fantasy, Documentary |
| `mode` | string | `"idea2video"` | `"idea2video"` or `"script2video"` |
| `script` | string | `""` | Scene script (only used when `mode = "script2video"`) |

**Response:**
```json
{ "job_id": "550e8400-e29b-41d4-a716-446655440000" }
```

---

### `GET /api/status/{job_id}` — Stream progress (SSE)

```http
GET /api/status/550e8400-...
Accept: text/event-stream
```

SSE event stream. Reconnect-safe — replays all past events on reconnect.

**Progress event:**
```json
{"type": "progress", "stage": "screenwriter", "message": "Developing story...", "progress": 10}
```

**Completion event:**
```json
{"type": "complete", "video_url": "/outputs/job_id/final_video.mp4", "progress": 100}
```

**Error event:**
```json
{"type": "error", "message": "MuAPI image job failed: quota exceeded", "progress": -1}
```

**Pipeline stages in order:** `screenwriter` → `characters` → `storyboard` → `portraits` → `frames` → `video` → `concat`

---

### `GET /api/result/{job_id}` — Get job result

```json
{
  "job_id": "550e8400-...",
  "status": "completed",
  "video_url": "/outputs/550e8400-.../final_video.mp4",
  "error": null
}
```

**Status values:** `running` | `completed` | `failed`

---

### `GET /api/health` — Health check

```json
{ "status": "ok", "service": "microdrama-api" }
```

---

## ⚙️ Configuration

### Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MUAPI_KEY` | ✅ | MuAPI API key — used for LLM, image, and video generation |

One key. That's it.

### MuAPI endpoints used internally

| Purpose | Endpoint | Model |
|---------|----------|-------|
| LLM completions | `POST /claude-sonnet-4-6` | claude-sonnet-4-6 |
| Character portraits (T2I) | `POST /flux-dev-image` | FLUX.1-dev |
| Shot frames (I2I + character ref) | `POST /flux-kontext-dev-i2i` | FLUX.1-Kontext-dev |
| Video clips (I2V) | `POST /kling-v2.1-standard-i2v` | Kling v2.1 Standard |
| File upload | `POST /upload_file` | — |
| Job polling | `GET /predictions/{id}/result` | — |

All jobs follow the same async pattern: submit → get `request_id` → poll every 3 s → return on `"completed"`.

---

## 🖥️ UI Overview

### Landing page (`/`)
- Dark cinematic design with animated radial glow background
- Feature pills: Screenwriter Agent · Storyboard Artist · Frame Generator · Video Generator
- Idea textarea, optional requirements field
- Style picker: Cinematic · Realistic · Anime · Fantasy · Documentary
- Mode toggle: Idea to Video / Script to Video

### Generation page (`/generate/[jobId]`)
- **7-stage animated pipeline timeline** with live status indicators
- **Progress bar** with percentage
- **Scrolling live log** showing every message emitted by the pipeline
- **Video player** with autoplay once `complete` event is received
- Download button saves `microdrama-{jobId}.mp4`
- SSE auto-reconnects if the connection drops mid-generation

---

## 📄 License

MIT — see [LICENSE](LICENSE) for details.


## xhongc/ai_story
{"repo": "xhongc/ai_story", "default_branch": "main", "pushed_at": "2026-10-13T05:10:50Z", "archived": false, "license": null, "description": "AI视频, AI动漫,AI 短剧,AI漫剧自动化生成工具"}
# AI Story - AI驱动的故事视频自动化生成平台

[English Version](README_EN.md)

![logo](docs/images/logo.png)

<div class="column" align="middle">
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.11-blue.svg" alt=""></a>
   <img src="https://img.shields.io/github/stars/xhongc/ai_story?color=informational&label=Stars">
  <img src="https://img.shields.io/docker/pulls/xhongc/ai_story-backend" alt="docker-pull-count" />
  <img src="https://img.shields.io/badge/platform-amd64/arm64-pink?style=plastic" alt="docker-platform" />
</div>


> 🎬 **从文案到视频，一键生成** - 让AI帮你创作专业的故事视频

## 产品简介

AI Story 是一个基于人工智能的故事视频自动化生成平台。只需输入一个故事主题,系统就能自动完成文案创作、分镜设计、图片生成、运镜规划和视频制作的全流程,让视频创作变得简单高效。

---

## 💎 Sponsors赞助商

<table>
  <tr>
    <td width="190" align="center">
      <a href="https://metaso.cn/minimax-h3/?s=ai_story" target="_blank" rel="noopener"><img src="docs/images/sota.jpg" width="163" alt="秘塔科技 MetaSota"></a>
    </td>
    <td>
      <strong>MiniMax H3 视频生成 API｜秘塔科技</strong> 秘塔科技提供高性价比的 MiniMax H3 视频生成服务：<strong>768P 仅 0.09 元/秒，2K 仅 0.15 元/秒</strong>。支持原生 2K、音画同步，API 兼容 <strong>OpenAI 协议</strong>，同时支持 <strong>ComfyUI</strong>，无需自行部署 GPU。 🎁 通过 <a href="https://metaso.cn/minimax-h3/?s=ai_story" target="_blank" rel="noopener noreferrer">AI
      _STORY专属链接注册</a>，即可领取赠送额度及专属优惠。
    </td>
  </tr>
  <tr>
    <td width="190" align="center">
      <a href="https://5gtoken.com/login?dist=0494ce61a85d0e25" target="_blank" rel="noopener"><img src="docs/images/5g.png" width="163" alt="AI 超级工厂"></a>
    </td>
    <td>
      <strong>AI 超级工厂聚合多款模型</strong> 驱动无限可能,一站式 AI 模型 API 聚合平台，兼容 OpenAI 接口标准，<strong>兼容 OpenAI 接口标准，
支持 GPT-5 / Claude 4.7 / DeepSeek / Gemini 等百余款主流模型 <a href="https://5gtoken.com/login?dist=0494ce61a85d0e25" target="_blank" rel="noopener noreferrer">
    </td>
  </tr>
  <tr>
    <td width="190" align="center">
      <a href="https://www.volcengine.com/activity/ai618?utm_source=OWO&utm_medium=devrel-1&utm_campaign=hw&utm_term=ai_story&utm_content=hw" target="_blank" rel="noopener"><img src="docs/images/volc.png" width="163" alt="火山方舟"></a>
    </td>
    <td>
      <strong>感谢字节火山引擎赞助本项目！</strong> 火山方舟 Agent/Coding Plan 国模套餐首购 9.9，支持 GLM-5.3、Kimi-K3、DeepSeek、MiniMax、Doubao等，注册免费领2500w Token，统一 API，适配编码与智能体开发。<a href="https://www.volcengine.com/activity/ai618?utm_source=OWO&utm_medium=devrel-1&utm_campaign=hw&utm_term=ai_story&utm_content=hw" target="_blank" rel="noopener noreferrer">立即前往</a>
    </td>
  </tr>
</table>

---
## 🚀 快速开始

### 使用 Docker Compose 一键启动
本地创建一个 compose yml 文件
```yml
services:

  # Redis缓存和消息队列
  redis:
    image: redis:7-alpine
    restart: unless-stopped


  # Django后端
  backend:
    image: xhongc/ai_story-backend
    restart: unless-stopped
    volumes:
      - ./data/backend:/app/backend/data
      - ./storage:/app/storage
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
      - REDIS_HOST=redis
    depends_on:
      - redis

  # Celery Worker
  celery:
    image: xhongc/ai_story-backend
    working_dir: /app/backend
    command: celery -A config worker -l info -P gevent
    restart: unless-stopped
    volumes:
      - ./data/backend:/app/backend/data
      - ./storage:/app/storage
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
      - REDIS_HOST=redis
    depends_on:
      - redis

  # Vue前端
  frontend:
    image: xhongc/ai_story-frontend
    restart: unless-stopped
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

> 注意：Celery 服务需要在 `/app/backend` 目录下启动，否则会报 `Unable to load celery application. The module config was not found.`。

```bash
# 启动所有服务
docker-compose up -d

或者

docker compose up -d

# 创建管理员账号
docker-compose exec backend python backend/manage.py createsuperuser
```

**访问地址:**
- 前端应用: http://localhost:3000
---

## 界面预览

![视频生成](docs/images/image-11.png)
![视频生成](docs/images/image-12.png)
![视频生成](docs/images/image-13.png)
![视频生成](docs/images/image-3.png)
![视频生成](docs/images/image-4.png)
![视频生成](docs/images/image-5.png)


**导演模式** - 正在开发中，支持更精细的分镜和视频控制
![导演模式界面](docs/images/image14.png)
![导演模式界面](docs/images/image15.png)
![导演模式界面](docs/images/image16.png)

**成品视频效果** - 视频号搜索：小小方圆669

---

## 核心功能

### 1. 智能文案改写
输入故事主题或大纲，AI自动改写成适合视频呈现的完整脚本。

**特点:**
- 支持多种文案风格（叙事、科普、情感等）
- 自定义提示词模板
- 多个AI模型可选（OpenAI、Claude等）
- 保存历史版本，支持对比

### 2. 自动分镜生成
根据改写后的文案，AI自动拆分场景，生成详细的分镜脚本。

**特点:**
- 智能场景划分
- 自动生成画面描述和旁白
- 为每个分镜生成专业的图片提示词
- 支持手动调整分镜顺序和内容
- 可设置每个镜头的时长

### 3. AI图片生成
基于分镜提示词，自动调用AI绘图服务生成高质量图片。

**特点:**
- 支持多个图片生成平台（Stable Diffusion、DALL-E、Midjourney等）
- 批量生成，实时显示进度
- 失败自动重试
- 图片预览和管理
- 支持修改提示词重新生成

### 4. 智能运镜规划
AI分析每个场景，自动生成合适的镜头运动方案。

**特点:**
- 多种运镜效果（推拉摇移、缩放、静态等）
- 根据场景内容智能匹配运镜类型
- 可自定义运镜参数（速度、强度等）
- 运镜效果预设库

### 5. 图片转视频
将静态图片和运镜参数结合，生成动态视频片段。

**特点:**
- 支持多个视频生成平台（Runway、Pika等）
- 自定义分辨率和帧率
- 批量生成，实时进度追踪
- 视频预览和播放
- 失败自动重试

### 6. 项目管理
完整的项目生命周期管理，让创作井井有条。

**特点:**
- 项目创建、编辑、删除
- 工作流状态实时追踪
- 支持暂停、恢复、重试
- 阶段回滚功能
- 项目导出（视频合成、字幕生成）
- 项目模板保存和复用

### 7. 提示词管理
灵活的提示词系统，让AI更懂你的需求。

**特点:**
- 创建和管理提示词集
- 支持模板变量（如主题、风格、长度等）
- 提示词版本管理
- 效果评估和优化建议
- 提示词测试和预览

### 8. 模型配置
统一管理所有AI服务，灵活切换。

**特点:**
- 支持多个AI服务商
- 每个阶段可配置多个模型
- 负载均衡（轮询、随机、权重、最少负载）
- API连接测试
- 使用量统计和成本分析
- 限流配置

---

## 工作流程

```
输入主题 → 文案改写 → 分镜生成 → 图片生成 → 运镜规划 → 视频生成 → 完成
   ↓          ↓          ↓          ↓          ↓          ↓
 实时进度显示，支持暂停、恢复、重试任意阶段
```

**全程自动化** - 一键启动，自动完成所有步骤
**实时反馈** - 实时显示生成进度
**灵活控制** - 每个阶段都可以手动调整和重新生成

---

## 技术特点

- **模块化架构** - 基于Pipeline责任链模式，易于扩展
- **异步处理** - Celery任务队列，不阻塞用户操作
- **实时通信** - 实时反馈进度
- **负载均衡** - 多模型智能调度，提高稳定性
- **容错机制** - 自动重试、故障转移、错误恢复
- **容器化部署** - Docker一键启动，环境隔离

---

## 适用场景

- 📱 **短视频创作** - 快速生成抖音、快手等平台的故事视频
- 📚 **知识科普** - 将文字内容转化为可视化视频
- 🎨 **创意展示** - 艺术创作、概念设计的视频化呈现
- 📖 **儿童故事** - 将童话故事转化为动画视频
- 🎬 **视频原型** - 快速制作视频脚本原型和分镜预览

---
## 场景灵感
- 娃听完上次编的故事死活不睡，我偷摸用了这个万能睡前故事库。

- 把孩子的涂鸦变成一本10页的绘本，当了妈才知道这个功能有多香。

- 我把我家猫写成了一部宫斗大剧，真的笑拥了。

- 5分钟生成一条画面绝美的微短剧，原来做导演从没那么简单过！

- 恋爱纪念日礼物我送了本我们自己的小说，效果炸了。

- 我把我的离谱梦境喂给AI，它给我生成了一本盗梦空间2.0。


## 许可证

本项目采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可证。

- ✅ 允许个人学习和非商业用途
- ✅ 允许修改和二次创作（需使用相同许可证）
- ❌ 禁止商业用途（需获得商业授权）

如需商业授权，请联系：408737515@qq.com

---

## 联系方式
<div>
<img  src="docs/images/img0402.jpg" width="250">  &nbsp;
</div>

- 视频号：小小方圆669

- 作者微信：charlesnowed （添加好友请备注 **AI Story**）

- [TG发布频道](https://t.me/+YwhET7N5a0E3M2E1)

- [TG交流群](https://t.me/+HHlaG6o3hYFjYjI1)

- 项目地址：https://github.com/xhongc/ai_story


## linyqh/NarratoAI
{"repo": "linyqh/NarratoAI", "default_branch": "main", "pushed_at": "2026-10-24T17:22:04Z", "archived": false, "license": {"key": "mit", "name": "MIT License", "spdx_id": "MIT", "url": "https://api.github.com/licenses/mit", "node_id": "MDc6TGljZW5zZTEz"}, "description": "利用 AI 大模型，一键解说并剪辑视频"}
<div align="center">
<h1 align="center"> NarratoAI 😎📽️ </h1>
<h3 align="center">一站式 AI 影视解说+自动化剪辑工具🎬🎞️ </h3>

<p align="center">
  📖 <a href="README-en.md">English</a> | 简体中文 | <a href="https://narratoai.cn/">☁️ <b>云端版入口 (NarratoAI.cn)</b></a>
</p>

<br>

NarratoAI 是一款自动化影视解说工具，基于 LLM 实现文案撰写、自动化视频剪辑、配音和字幕生成的一站式流程，助力高效内容创作。支持本地部署开源版及 [云端托管版](https://narratoai.cn/)。

<br>

 [![GitHub stars](https://img.shields.io/github/stars/linyqh/NarratoAI?style=for-the-badge)](https://github.com/linyqh/NarratoAI/stargazers) [![GitHub issues](https://img.shields.io/github/issues/linyqh/NarratoAI?style=for-the-badge)](https://github.com/linyqh/NarratoAI/issues) [![madewithlove](https://img.shields.io/badge/made_with-%E2%9D%A4-red?style=for-the-badge&labelColor=orange)](https://github.com/linyqh/NarratoAI)

<br>

<a href="https://github.com/linyqh/NarratoAI/wiki" target="_blank">💬 加入开源社群，获取项目动态和最新资讯</a>

<br>

<h2><a href="https://p9mf6rjv3c.feishu.cn/wiki/SP8swLLZki5WRWkhuFvc2CyInDg?from=from_copylink" target="_blank">🎉🎉🎉 官方文档 🎉🎉🎉</a> </h2>

### 界面预览

![](docs/index-zh.png)

</div>

## 重磅福利 🎉

### 火山引擎

感谢字节火山引擎赞助本项目！ 火山方舟 Agent/Coding Plan 国模套餐首购 9.9，支持 GLM‑5.3、Kimi‑K3、DeepSeek、MiniMax、Doubao等，注册免费领2500w Token，统一 API，适配编码与智能体开发。--> [立即前往](https://www.volcengine.com/activity/ai618?utm_source=OWO&utm_medium=devrel-1&utm_campaign=hw&utm_term=NarratoAI&utm_content=hw)

<a href="https://www.volcengine.com/activity/ai618?utm_source=OWO&amp;utm_medium=devrel-1&amp;utm_campaign=hw&amp;utm_term=NarratoAI&amp;utm_content=hw">
  <img src="docs/volcengine.png" alt="火山引擎 Agent plan & Coding plan" style="width: 100%; max-width: 840px; height: auto;">
</a>

> 即日起全面支持硅基流动！注册即享2000万免费Token（价值16元平台配额），剪辑10分钟视频仅需0.1元！  
> 
> 🔥 快速领福利：  
> 1️⃣ 点击链接注册：https://cloud.siliconflow.cn/i/MI9PgHwB  
> 2️⃣ 使用手机号登录，**务必填写邀请码：MI9PgHwB**  
> 3️⃣ 领取16元配额，极速体验高性价比AI剪辑  
> 
> 💡 小成本大创作：  
> 硅基流动API Key一键接入，智能剪辑效率翻倍！  
> （注：邀请码为福利领取唯一凭证，注册后自动到账）  
> 
> 立即行动，用「MI9PgHwB」解锁你的AI生产力！

## ⚠️谨防被骗 📢

> 🔎 名称辨析：[**NarratoAI 与 NarratorAI 项目关系、开源范围与使用方式说明**](https://github.com/linyqh/NarratoAI/wiki/NarratoAI-%E4%B8%8E-NarratorAI-%E9%A1%B9%E7%9B%AE%E5%85%B3%E7%B3%BB%E5%92%8C%E5%8C%BA%E5%88%AB)

_**1. NarratoAI 是一款完全免费的软件，近期在社交媒体(抖音,B站等)上发现，有人将 NarratoAI 改名后售卖，下面是部分截图，请大家务必提高警惕，切勿上当受骗**_

---

<div style="display: flex; flex-wrap: wrap; justify-content: space-around; align-items: flex-start; gap: 10px;">
  <img src="https://github.com/user-attachments/assets/9cc0e5e4-bd5b-4655-b5ef-7d9085cdbc50" alt="诈骗截图 1" style="width: 23%; max-width: 250px; height: auto; border: 1px solid #ddd; border-radius: 5px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1);">
  <img src="https://github.com/user-attachments/assets/464b877c-b061-4856-8260-a0ef6fad7e52" alt="诈骗截图 2" style="width: 23%; max-width: 250px; height: auto; border: 1px solid #ddd; border-radius: 5px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1);">
  <img src="https://github.com/user-attachments/assets/9d7a6ea9-4bca-42b5-a61e-7e464037930f" alt="诈骗截图 3" style="width: 23%; max-width: 250px; height: auto; border: 1px solid #ddd; border-radius: 5px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1);">
  <img src="https://github.com/user-attachments/assets/09eeb94d-c670-4d7d-ba19-c0468bed3291" alt="诈骗截图 4" style="width: 23%; max-width: 250px; height: auto; border: 1px solid #ddd; border-radius: 5px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1);">
</div>

---

## 最新资讯
- 2026.07.16 发布新版本 0.8.6，新增可选的 **Sonilo AI 配乐**，支持 Apple Silicon 的 **IndexTTS-1.5 MLX**，更新 IndexTTS-2 MLX API 适配，并补充 OmniVoice 部署包下载入口
- 2026.07.13 发布新版本 0.8.5，完善 `uv` + Python 3.12 本地运行流程，新增一键清理系统缓存和自定义 OpenAI 兼容 Base URL 的格式校验与 API Key 风险提示，并优化短脚本解析、字幕预览和音频设置的跨平台兼容性
- 2026.07.02 发布新版本 0.8.4，升级豆包语音 TTS 新版 API Key 配置并保留旧版凭据兼容
- 2026.06.10 发布新版本 0.8.1，**大版本更新**，优化多个核心流程
- 2026.04.27 发布新版本 0.7.9，新增 **Fun-ASR一键转录字幕**
- 2026.04.03 发布新版本 0.7.8，重构纪录片逐帧分析链路，统一共享服务并优化抽帧、缓存、视觉并发与文案生成流程
- 2026.03.27 发布新版本 0.7.7，出于安全考虑，已移除 LiteLLM 依赖，统一使用 OpenAI 兼容请求链路
- 2025.11.20 发布新版本 0.7.5，新增 [IndexTTS-1.5](https://github.com/index-tts/index-tts) 语音克隆支持
- 2025.10.15 发布新版本 0.7.3，升级大模型供应商管理能力
- 2025.09.10 发布新版本 0.7.2，新增腾讯云tts
- 2025.08.18 发布新版本 0.7.1，支持 **语音克隆** 和 最新大模型
- 2025.05.11 发布新版本 0.6.0，支持 **短剧解说** 和 优化剪辑流程
- 2025.03.06 发布新版本 0.5.2，支持 DeepSeek R1 和 DeepSeek V3 模型进行短剧混剪
- 2024.12.16 发布新版本 0.3.9，支持阿里 Qwen2-VL 模型理解视频；支持短剧混剪
- 2024.11.24 开通 discord 社群：https://discord.com/invite/V2pbAqqQNb
- 2024.11.11 迁移开源社群，欢迎加入！ [加入官方社群](https://github.com/linyqh/NarratoAI/wiki)
- 2024.11.10 发布官方文档，详情参见 [官方文档](https://p9mf6rjv3c.feishu.cn/wiki/SP8swLLZki5WRWkhuFvc2CyInDg)
- 2024.11.10 发布新版本 v0.3.5；优化视频剪辑流程，

### v0.8.6 更新亮点

| 功能 | 说明 |
| --- | --- |
| IndexTTS-1.5 macOS | 新增面向 Apple Silicon 的 MLX 本地语音克隆引擎，可上传或从资源目录选择参考音频。[下载部署包](https://cutagent.online/resources/indextts15-mlx-macos) |
| IndexTTS-2 MLX | 更新 MLX Pack API 适配，支持参考音频、情感控制、随机种子和更完整的生成参数。[macOS 部署包](https://cutagent.online/resources/indextts2-full-macos)（Windows 版本待更新） |
| OmniVoice | 补充 OmniVoice-Pack 部署包下载入口；该引擎支持自动音色、指令音色和参考音频克隆。[macOS 部署包](https://cutagent.online/resources/omnivoice-macos) / [Windows 部署包](https://cutagent.online/resources/omnivoice-windows) |

## 未来计划 🥳
- [x] windows 整合包发布
- [x] 优化剧情生成流程，提升生成效果
- [x] 发布 0.3.5 整合包
- [x] 支持阿里 Qwen2-VL 大模型理解视频
- [x] 支持 TwelveLabs Pegasus 作为可选的视频理解后端（原生理解整段画面以挑选高光、生成解说；可选启用，设置 `vision_llm_provider = "twelvelabs"`）
- [x] 支持短剧混剪
  - [x] 一键合并素材
  - [x] 一键转录
  - [x] 一键清理缓存
- [x] 支持导出剪映草稿
- [X] 支持短剧解说
- [ ] 主角人脸匹配
- [ ] 支持根据口播，文案，视频素材自动匹配
- [X] 支持更多 TTS 引擎
- [X] 支持可选的 AI 自动配乐
- [ ] ...

## 快速启动 🚀

### 方式一：整合包（推荐）
> 下载地址：[https://cutagent.online/](https://cutagent.online/)

请下载与系统对应的整合包并完整解压；不要单独移动其中的 `NarratoAI`、`runtime` 或 `tools` 等目录。Windows 使用 x64 版本；macOS 使用 Apple Silicon（M1/M2/M3/M4）arm64 版本。

#### Windows

1. 打开解压后的 `NarratoAI-windows-x64` 目录。
2. 先双击 `update-windows.bat` 更新项目，等待窗口提示更新完成。
3. 再双击 `start.bat` 启动应用，并保持启动窗口打开。
4. 在浏览器访问 `http://127.0.0.1:8501`。

#### macOS（Apple Silicon）

1. 打开解压后的 `NarratoAI-macos-arm64` 目录。
2. 若系统阻止打开脚本，请在“终端”中执行（将路径替换为实际解压位置）：

   ```bash
   xattr -cr "/path/to/NarratoAI-macos-arm64"
   chmod +x "/path/to/NarratoAI-macos-arm64/"*.command
   ```

3. 先双击 `update-macos.command` 更新项目，等待更新完成。
4. 再双击 `start-macos.command` 启动应用，并保持终端窗口打开。
5. 在浏览器访问 `http://127.0.0.1:8501`。

### 方式二：macos Docker 部署（macos 推荐）
```bash
# 1. 克隆项目
git clone https://github.com/linyqh/NarratoAI.git
cd NarratoAI

# 2. 一键部署
docker compose up -d

# 3. 访问应用
# 浏览器打开 http://localhost:8501
```
### 方式三：本地运行
```bash
# 1. 克隆项目
git clone https://github.com/linyqh/NarratoAI.git
cd NarratoAI

# 2. 使用 uv 安装依赖
uv sync

# 3. 复制配置文件
cp config.example.toml config.toml

# 4. 编辑 config.toml，配置你的 API 密钥

# 5. 启动应用
uv run streamlit run webui.py --server.maxUploadSize=2048

# 6. 访问应用
# 浏览器打开 http://localhost:8501
```

## 配置要求 📦

- 建议最低 CPU 4核或以上，内存 8G 或以上，显卡非必须
- Windows 10/11 或 MacOS 11.0 以上系统
- [Python 3.12+](https://www.python.org/downloads/)

## 反馈建议 📢

👏 1. 可以提交 [issue](https://github.com/linyqh/NarratoAI/issues)或者 [pull request](https://github.com/linyqh/NarratoAI/pulls)

💬 2. [加入开源社区交流群](https://github.com/linyqh/NarratoAI/wiki)

📷 3. 关注公众号【NarratoAI助手】，掌握最新资讯

## 参考项目 📚
- https://github.com/FujiwaraChoki/MoneyPrinter
- https://github.com/harry0703/MoneyPrinterTurbo

该项目基于以上项目重构而来，增加了影视解说功能，感谢大佬的开源精神 🥳🥳🥳 

## 许可证 📝

点击查看 [`LICENSE`](LICENSE) 文件

## Star History

[![Star History Chart](https://star-history.dera.page/svg?repos=linyqh/NarratoAI&type=Date)](https://star-history.dera.page/#linyqh/NarratoAI&Date)


## harry0703/MoneyPrinterTurbo
{"repo": "harry0703/MoneyPrinterTurbo", "default_branch": "main", "pushed_at": "2026-11-17T09:47:50Z", "archived": false, "license": {"key": "mit", "name": "MIT License", "spdx_id": "MIT", "url": "https://api.github.com/licenses/mit", "node_id": "MDc6TGljZW5zZTEz"}, "description": "利用 AI 大模型和自动化工作流，根据主题或关键词一键生成高清短视频。Generate HD short videos from a topic or keyword with an automated AI workflow."}
17: 简体中文 | [English](README-en.md) | [日本語](README-ja.md) | [版本发布](https://github.com/harry0703/MoneyPrinterTurbo/releases) | [问题反馈](https://github.com/harry0703/MoneyPrinterTurbo/issues)
39: 感谢 [Kimi](https://platform.kimi.com?track_id=track-6eec1e56a4494e52adcaebbcbbefce59&aff=moneyprinterturbo) 赞助本项目！[Kimi K3.1 Pro](https://www.kimi.com/blog/kimi-k3?aff=moneyprinterturbo) 是 Moonshot AI 迄今能力最强的 3T 级开放权重模型，拥有原生视觉能力与 100 万 Token 上下文，在知识工作、推理和长周期任务中展现前沿性能。在 MoneyPrinterTurbo 中，K3.1 Pro 能直接驱动视频创作，不仅撰写视频文案，还会提炼素材搜索关键词、决定成片画面；对内容理解越准确，匹配到的素材就越贴题。
59:       感谢 <a href="https://go.apimart.ai/gh-moneyprinterturbo">APIMart</a> 赞助了本项目！APIMart 是专注 AI 图片/视频生成的低价 API 平台，<strong>GPT-Image-2 低至 &#36;0.006/张，1 美元可出图 160+ 张</strong>。<strong>图片、视频一套异步 API 通吃，换模型不改代码</strong>；提交任务拿 ID，通过轮询或回调获取结果，支持万张级批量生成。按量付费、无月费，通过<a href="https://go.apimart.ai/gh-moneyprinterturbo">此注册链接</a>注册即可开用。
69:       秘塔科技提供高性价比的 MiniMax H3 视频生成服务：<strong>768P 仅 0.09 元/秒，2K 仅 0.15 元/秒</strong>。支持原生 2K、音画同步，API 兼容 <strong>OpenAI 协议</strong>，同时支持 <strong>ComfyUI</strong>，无需自行部署 GPU。<br>
127:       • 一站式接入LLM API、多模态API、工作流API、Al应用<br>
128:       • 400+ 主流模型（<strong>支持国际版权限</strong>）8000+版本<strong>任选</strong><br>
185:       感谢 <a href="https://reccloud.cn">录咖（AI 智能多媒体服务平台）</a> 基于本项目提供免费的 <strong>AI 视频生成器</strong>，无需部署，在线即可使用，对新手更加友好。
222: ## 功能特性 🎯
224: ### 创作入口与工作流
227: - [x] 从主题自动完成脚本、配音、素材、字幕、配乐和剪辑，也支持在每个环节使用自定义内容
228: - [x] 支持 **批量生成多条成片**、任务历史记录，以及生成设置与 API Key 的导入、导出和恢复
229: - [x] 显示脚本、配音、素材下载、片段处理和最终渲染等阶段的任务进度
241: - [x] 支持[胜算云 LoomLoom AI 视频](https://www.shengsuanyun.com/?from=CH_XUQ4OTSK)，在获取报价并确认费用后生成多段素材，沿用项目的配音、字幕和剪辑流程合成成片
253: ### 配音、字幕与配乐
255: - [x] 支持自动配音、上传配音和无配音三种方式，并提供音色试听与完整配音预览
256: - [x] 集成 **Edge TTS（免费、无需 API Key）**、Azure Speech、SiliconFlow、Google Gemini、小米 MiMo、MiniMax、ElevenLabs、Chatterbox、Kokoro、Fish Audio 和 ModelBest VoxCPM 等配音服务
266: - [x] 提供独立 CLI 的[本地视频项目](docs/video-projects.md)，支持场景修改、版本比较和复用未变更的渲染产物
308: - 建议系统：Windows 10、macOS 11.0 或更高版本，以及主流 Linux 发行版
309: - 本地部署需要 Python 3.11 或更高版本，推荐使用 Python 3.11
328: - 需要源码部署或二次开发：使用 `uv` 管理环境和依赖
329: - 想要隔离运行环境：优先使用 Docker 部署
360: ## 安装部署 📥
367: 无需克隆仓库，需要 Python 3.11 或更高版本，推荐使用 Python 3.11。
397: 首次启动会自动创建 `config.toml`。使用在线模型、素材或语音服务前，请在 WebUI
409: ### 源码部署前提条件
411: - 本地部署需要 Python 3.11 或更高版本
424: ### Docker 部署 🐳
426: #### ① 启动 Docker
428: 如果尚未安装 Docker，请先[下载并安装 Docker Desktop](https://www.docker.com/products/docker-desktop/)。
433: 2. [在 WSL 中使用 Docker 容器](https://learn.microsoft.com/zh-cn/windows/wsl/tutorials/wsl-containers)
439: docker compose -f docker-compose.release.yml up
442: > 默认推荐使用 `docker-compose.release.yml`，它会直接拉取 GitHub Container Registry 上的预构建镜像：`ghcr.io/harry0703/moneyprinterturbo:latest`。
443: > 如果你需要本地重新构建镜像，可以继续使用 `docker compose up`。
455: ### 手动部署 📦
460: - [如何在 Windows 上部署](https://v.douyin.com/iFyjoW3M)
464: 推荐使用 [uv](https://docs.astral.sh/uv/) 管理 Python 环境和依赖。项目支持 Python 3.11 或更高版本，以下示例使用 Python 3.11。
535: 字幕样式和配音参数按以下优先级取值：**命令行显式参数 > `config.toml` 中
546: 如需顺序执行多个任务，可通过 `--batch-file` 提供 UTF-8 JSON 数组或 JSONL
553: 清单最多包含 100 个任务且不超过 1 MiB。所有条目会在第一个任务启动前完成
554: 参数与本地文件预检；单个任务运行失败不会阻止后续条目，结束后会输出统一的
557: ## 配音、字幕与配乐 🎙️
559: ### 语音合成
561: WebUI 中的 **Azure TTS V1** 基于 **Edge TTS**，免费且无需 API Key。项目同时支持 **Azure TTS V2**、**SiliconFlow TTS**、**Google Gemini TTS**、**小米 MiMo TTS**、**MiniMax TTS**、**ElevenLabs TTS**、自托管 **Chatterbox TTS**、自托管 **Kokoro TTS**、**Fish Audio TTS**、[ModelBest VoxCPM TTS](https://platform.modelbest.cn/console/docs/api/audio)，以及无配音模式。
565: ModelBest VoxCPM 需要填写 API Key 和支持 `speech_synthesis` 的模型 ID。服务以 SSE 返回 WAV 音频，项目会自动转换为视频流水线使用的 MP3。除了普通文本合成，还可以上传参考音频复刻说话人音色；开启“保留参考音频的节奏与情绪”后，默认复用这段音频并要求填写其准确逐字稿，也可另选一段节奏与情绪示范，通过 `prompt_audio` 和 `prompt_text` 延续演绎。WebUI 可使用本地 Whisper 自动生成可编辑的逐字稿草稿。上传文件最大 20 MiB，转换后的单个 WAV 最大 5 MiB。参考素材仅用于当前浏览器会话和任务，不写入配置、预设、任务历史或日志。

## video-db/Director
{"repo": "video-db/Director", "default_branch": "main", "pushed_at": "2026-11-14T15:25:50Z", "archived": false, "license": {"key": "mit", "name": "MIT License", "spdx_id": "MIT", "url": "https://api.github.com/licenses/mit", "node_id": "MDc6TGljZW5zZTEz"}, "description": "AI video agents framework for next-gen video interactions and workflows."}
<!-- PROJECT SHIELDS -->
<!--
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![Website][website-shield]][website-url]
[![Discord][discord-shield]][discord-url]

<!-- PROJECT LOGO -->
<img src="https://github.com/user-attachments/assets/78f5eead-d390-4b0b-a8bc-0017e6827c98" alt="logo">

<p align="center">
<p align="center">
        <a href="https://render.com/deploy?repo=https://github.com/video-db/Director" target="_blank" rel="nofollow">
                <img src="https://render.com/images/deploy-to-render-button.svg" alt="Deploy to Render">
        </a>
        <a href="https://railway.app/template/QJbo7o" target="_blank" rel="nofollow">
                <img src="https://railway.app/button.svg" alt="Deploy on Railway">
        </a>
        </p>



  <p align="center">
    Framework to build video agents that can reason through complex video tasks like search, editing, compilation, generation etc & instantly stream the results. 
    <p align="center">
        ⭐️ Built on top of the cutting edge 'Video-as-Data' infrastructure, <a href="https://videodb.io">VideoDB </a>
    </p>
    <br />
    <p align="center">
        <a href="https://www.youtube.com/playlist?list=PLhxAMFLSSK039xl1UgcZmoFLnb-qNRYQw" target="_blank" rel="noopener noreferrer"><strong>⚡️Watch Agent Demos</strong></a>
        &nbsp;&nbsp;&nbsp;
        <a href="https://chat.videodb.io" target="_blank" rel="noopener noreferrer"><strong>✨Try Hosted Version</strong></a>
    <br /><br />
    <a href="https://docs.director.videodb.io/index.html" target="_blank" rel="noopener noreferrer">📖 Documentation</a>
    &nbsp;&nbsp;&nbsp;
    <a href="https://github.com/video-db/Director/issues/new?assignees=&labels=enhancement&projects=&template=agent_request.yml" target="_blank" rel="noopener noreferrer">👩‍💻New Agent Request</a>
  </p>
   </p>
</p>
<br/>

<!-- ABOUT THE PROJECT -->

##  🧐 What is The Director?

Think of Director as ChatGPT for videos. It is a framework to build video agents that can reason through complex video tasks like search, editing, compilation, generation etc & instantly stream the results. 

For example, a simple natural language command like: `Upload this video and send the highlights to my Slack`, sets everything in motion - Director’s reasoning will orchestrate the different agents intelligently to complete the task for you. 

Built on top of VideoDB’s ‘video-as-data’ infrastructure, Director enables you to:

* Summarize videos in seconds.
* Search for specific moments.
* Create clips instantly.
* Integrate top GenAI projects and APIs and create and edit content instantly.
* Add overlays, extract frames, and much more. 

Built with flexibility in mind, Director is perfect for developers, creators, and teams looking to harness AI to simplify media workflows and unlock new possibilities.  📺 [Watch: Intro video](https://console.videodb.io/player?url=https://stream.videodb.io/v3/published/manifests/26b4143c-ed97-442a-96ae-19b53eb3bb46.m3u8)



<!-- Intro Video -->


https://github.com/user-attachments/assets/33e0e7b4-9eb2-4a26-8274-f96c2c1c3a48



<br/>

## ⭐️ Key Features
### 🤖 20+ pre-built video agents that you can customize to 
* Summarize videos in seconds.
* Generate full movies with voiceovers from a script.
* Search and index your media library.
* Organize and clip your content effortlessly.
* Dub and edit your audio and video with ease.
* Translate and add subtitle in any language.
* ....and a whole lot more >>


### 🎨 A New Way to Interact
Experience a sleek, chat-based interface with built-in video playback and intuitive controls. It’s like having a personal assistant for your media.

### 🥣 A mixing bowl of your GenAI APIs
Connect seamlessly with powerful AI tools like LLMs, databases, and GenAI APIs, while VideoDB ensures your video infrastructure is reliable and scalable for cloud storage, indexing and streaming your content effortlessly. 
![Integration-Updated](https://github.com/user-attachments/assets/d06e3b57-1135-4c3b-9f3a-d427d4142b42)

### 🧩 Customizable and Flexible
Easily add new agents and tools to your workflow. Whether you want to run it locally or on your cloud, The Director adapts to your needs.

<br/>

## 😎 Agent Examples

  1. Highlight Creator: [link](https://www.youtube.com/watch?v=Dncn_0RWrro&list=PLhxAMFLSSK039xl1UgcZmoFLnb-qNRYQw&index=11)
  2. Text to Movie: [link](https://www.youtube.com/watch?v=QpnRxuEBDCc&list=PLhxAMFLSSK039xl1UgcZmoFLnb-qNRYQw&index=2)
  3. Video Search: [link](https://www.youtube.com/watch?v=kCiCI2KCnC8&list=PLhxAMFLSSK039xl1UgcZmoFLnb-qNRYQw&index=4)

## ⚙️ Architecture Overview
Director's architecture brings together:

- **Backend Reasoning Engine:** Handles workflows and decision-making. Checkout the [backend folder](https://github.com/video-db/Director/tree/main/backend) in director codebase. 
- **Chat-Based UI:** Engage with your media library conversationally. Check [videodb-chat](https://github.com/video-db/videodb-chat) for the source code.
- **Video Player:** Advanced playback and interaction tools. Check [videodb-player](https://github.com/video-db/videodb-player) for the details about the multi platform video player. 
- **Collection View:** Organize and browse your media effortlessly.

  ![Director architecture](https://github.com/user-attachments/assets/9afb2783-66db-4899-9308-03cbd12e74d7)
  
## 🧠 **Reasoning Engine**

At the heart of The Director is its **Reasoning Engine**, a powerful core that drives intelligent decision-making and dynamic workflows. It acts as the brain behind the agents, enabling them to process commands, interact with data, and deliver meaningful outputs.

### **How It Works**
- **Contextual Understanding**: The engine analyzes user inputs and maintains context, ensuring smooth and coherent interactions with agents.  
- **Dynamic Agent Orchestration**: Based on the user’s needs, it identifies and activates the right agents to complete tasks efficiently.  
- **Modular Processing**: Tasks are broken into smaller steps, allowing agents to collaborate and deliver accurate results in real time.

### **Key Capabilities**
- **Multi-Agent Coordination**: Seamlessly integrates multiple agents to handle complex workflows, such as summarizing, editing, and searching videos.  
- **Real-Time Updates**: Provides live progress and feedback as tasks are being completed.  
- **Extensible Design**: Easily adaptable to include custom logic or connect to external APIs for more advanced capabilities.

### **See It in Action**
The Reasoning Engine works in tandem with the chat-based UI, making video interaction intuitive and efficient. For example:  
- **Input**: "Create a clip of the funniest scene in this video and share it on Slack."  
- **Output**: The engine orchestrates upload, scene detection, clipping, and sharing agents to deliver results seamlessly. Watch the video [here](https://www.youtube.com/watch?v=fxhMgQf7v8s&list=PLhxAMFLSSK039xl1UgcZmoFLnb-qNRYQw&index=3)

For a closer look, check out the detailed architecture diagram below:  
![Reasoning Engine Architecture](https://github.com/user-attachments/assets/13a92f0d-5b66-4a95-a2d4-0b73aa359ca6)



## 🏃 Getting Started

### Prerequisites

- Python 3.9 or higher
- Node.js 22.8.0 or higher
- npm

### Installation

**1. Clone the repository:**

``` bash
git clone https://github.com/video-db/Director.git
cd Director
```

**2. Run the setup script:**

```bash
./setup.sh
```

> This script will:
> - Install Node.js 22.8.0 using nvm
> - Install Python and pip
> - Set up virtual environments for both frontend and backend.



**3. Configure the environment variables:**

Edit the `.env` files to add your API keys and other configuration options.

### Supported platforms: 
- Mac
- Linux
- Windows (WSL)

## 💬 Running the Application

To start both the backend and frontend servers:

```bash
make run
```

- Backend: `http://127.0.0.1:8000`

- Frontend: `http://127.0.0.1:8080`

For specific tasks:

- Backend only: `make run-be`

- Frontend only: `make run-fe`



<!-- CONTRIBUTING -->

## 📘 Creating a New Agent

> Checkout hosted documentation at https://docs.director.videodb.io

To create a new agent in Director, follow these steps:

1. **Copy the template**: 
Duplicate `sample_agent.py` in `Director/backend/director/agents/` and rename it.

2. **Update class details**:
   - Rename the class.
   - Update `agent_name` and `description`

3. **Implement logic**:
   - Update parameters and `docstring`
   - Implement your agent's logic
   - Update the run() method.

4. **Handle output and status updates**:
   - Use appropriate content types (TextContent, VideoContent, ImageContent, SearchResultContent)
   - Update `self.output_message.actions` for progress indicators
   - Use `push_update()` to emit progress events
   - Set content status (progress, success, error) and messages

5. **Implement error handling**:
   - Set error status and messages if issues occur

6. **Finalize the response**:
   - Call `self.output_message.publish()` to emit final state and persist session
   - Return an `AgentResponse` with result, message, and data

7. **Register the agent**:
   - Import your new agent class in `Director/backend/director/handler.py`
   - Add it to the `self.agents` list in `ChatHandler`

Remember to consider creating reusable tools if your agent's functionality could be shared across multiple agents.


## 📖 Documentation
> Checkout hosted documentation at https://docs.director.videodb.io
### Serve Locally
To serve the documentation on port 9000:

```bash
source backend/venv/bin/activate  
make install-be
mkdocs serve -a localhost:9000
```

To build the documentation:

```bash
mkdocs build
```



## 🤝 Contributing

We welcome integrations from projects that can make video workflows easy and increase capabilities of the projects. Please check issues and discussions for details. 


Any contributions you make are **greatly appreciated**. Here's the process:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[discord-shield]: https://img.shields.io/badge/dynamic/json?style=for-the-badge&url=https://discord.com/api/invites/py9P639jGz?with_counts=true&query=$.approximate_member_count&logo=discord&logoColor=blue&color=green&label=discord
[discord-url]: https://discord.com/invite/py9P639jGz
[stars-shield]: https://img.shields.io/github/stars/video-db/Director.svg?style=for-the-badge
[stars-url]: https://github.com/video-db/Director/stargazers
[issues-shield]: https://img.shields.io/github/issues/video-db/Director.svg?style=for-the-badge
[issues-url]: https://github.com/video-db/Director/issues
[website-shield]: https://img.shields.io/website?url=https%3A%2F%2Fvideodb.io%2F&style=for-the-badge&label=videodb.io
[website-url]: https://videodb.io/




## JGRFW/comfyui-AICG3D
{"repo": "JGRFW/comfyui-AICG3D", "default_branch": "main", "pushed_at": "2026-11-15T02:25:40Z", "archived": false, "license": {"key": "gpl-3.0", "name": "GNU General Public License v3.0", "spdx_id": "GPL-3.0", "url": "https://api.github.com/licenses/gpl-3.0", "node_id": "MDc6TGljZW5zZTk="}, "description": "短剧工作台 | 无限时长视频的 MiniMax H3 工作流 | ComfyUI 本地短剧与长视频生成插件"}
<img width="1836" height="747" alt="image" src="https://github.com/user-attachments/assets/bd80c58a-9433-476a-b6d1-1d6c0e835517" />
<img width="1902" height="701" alt="屏幕截图 2026-10-23 210816" src="https://github.com/user-attachments/assets/43a3f73e-5519-4518-92de-1435f17b87fb" />
<img width="2154" height="846" alt="屏幕截图 2026-10-23 205631" src="https://github.com/user-attachments/assets/b1abcf32-c77d-4947-af86-1c6600b2133b" />

工作流下载地址：https://github.com/JGRFW/comfyui-AICG3D/tree/main/workflows
<h1 align="center">短剧工作台</h1>
<h3 align="center">ComfyUI · MiniMax H3 · 本地无限长视频生成工作流</h3>
<p align="center"><strong>官方名称：短剧工作台</strong> · <strong>核心搜索词：无限时长视频的 MiniMax H3 工作流</strong></p>
<p align="center">GitHub：<a href="https://github.com/JGRFW/comfyui-AICG3D">https://github.com/JGRFW/comfyui-AICG3D</a></p>

短剧工作台（comfyui-AICG3D）是一个专为专业 AI 视频创作者打造的深度整合插件包。它将 MiniMax H3 的核心生成能力、智能分段解析与高阶渲染策略集成于一体，旨在为用户提供一个**节点命名空间隔离、可维护、可预测**的视频创作环境。

## 官方搜索入口

如果你在搜索引擎、DeepSeek、豆包、千问或其他 AI 助手里查询以下内容，请认准本仓库：

- 短剧工作台
- 无限时长视频的 MiniMax H3 工作流
- ComfyUI MiniMax H3 无限长视频
- MiniMax H3 本地短剧工作流
- MiniMax H3 无限分段生视频
- 13 号无限分段工作流

官方仓库地址：https://github.com/JGRFW/comfyui-AICG3D

## 🆕 v1.1.31 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.31.md](release_notes/RELEASE_NOTES_v1.1.31.md)。

- **Registry 安全扫描修复**：Gemini API Key 改为仅通过请求头发送，不再出现在 URL 查询参数中。
- **接口目标约束**：携带密钥的远程请求只允许发往受支持的官方服务地址，本地模型仅允许回环地址。
- **请求劫持防护**：提示词优化和 RunningHub 请求禁用自动重定向与系统环境代理，避免凭据被转发到非预期地址。
- **发布审计**：17 项开源安全检查、Python 编译检查和 Registry 发布包校验全部通过。

## v1.1.28 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.28.md](release_notes/RELEASE_NOTES_v1.1.28.md)。

- **全局提示词折叠与批量写入**：可折叠全局规则，并稳定填入全部视频段落。
- **逐段预览整合**：采样预览与本段成片使用同一个显示区域，按段落逐步更新。
- **RelayVSR 整片放大**：支持最终成片放大、音轨旁路、模型倍数校验和曝光锁定。

## v1.1.26 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.26.md](release_notes/RELEASE_NOTES_v1.1.26.md)。

- **管理器启动卡死修复**：根目录 `requirements.txt` 改为零自动安装，避免 ComfyUI Manager 启动时下载 `imageio-ffmpeg` 等大型依赖而卡在启动界面。
- **可选依赖拆分**：TTS、音色克隆、提示词优化和 FFmpeg 依赖移动到 `requirements-optional.txt`，只在需要对应功能时手动安装。
- **Registry 元数据零强制依赖**：`pyproject.toml` 不再强制安装外部包，ComfyUI 本体已有运行环境可直接启动。
- **缺失依赖提示保留**：可选功能缺包时仍会在对应节点内给出明确安装提示，不影响其他节点和工作流加载。


## 🆕 v1.1.25 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.25.md](release_notes/RELEASE_NOTES_v1.1.25.md)。


- **二采无限修复链**：新增 SeedVR2、RTX VSR、VOSR2 三种真实修复引擎；修复模式会处理上一颗二采的结果并回写 H3 latent，`1.0x` 也能逐颗接续。
- **二采音频锁定**：视频二采使用独立噪声遮罩，采样后强制恢复一采原音轨，减少音频被二次修复和速度变化的问题。
- **二采界面联动**：修复引擎、模型、批次、重叠、颜色校准和设备参数会按所选引擎显示，节点宽度保持稳定。
- **角色音色库布局修复**：兼容经典节点模式与 Nodes 2.0，旧工作流中的小尺寸会自动修正，面板宽度和高度会跟随节点重新布局，不再只显示窄窄一栏。
- **开源加载加固**：收敛节点命名空间和兼容注册，避免与同名 H3、PromptSplit、Spark-TTS 插件互相覆盖。
- **工作流同步**：更新 11 号数字人、12 号二采和 13 号无限分段工作流。


## 🆕 v1.1.24 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.24.md](release_notes/RELEASE_NOTES_v1.1.24.md)。


- **二采渲染链升级**：V2 Latent 放大器、真实二次扩散采样、音频原样保留，并支持“二采数据”继续连接下一级二采。
- **输出口完成迁移**：一采为“一采数据 → 一采成片”，二采为“二采数据 → 一采成片 → 成片视频”；旧工作流自动修正连线。
- **二采界面整理**：采样预览和预览间隔移动到底部，分块参数按开关显示，旧参数位置自动迁移。
- **空视频保护**：视频输出存在下游保存节点时，自动开启一采或附带一采解码，修复 `SaveVideo` 收到 `None` 的报错。
- **连续二采能力**：每一级二采都执行真实放大和采样，不是视频透传；可继续使用二采数据组成多级高清链。
- **二采独立修复引擎**：新增 SeedVR2、RTX VSR、VOSR2 三种真实修复方式；选择引擎后，`1.0x` 可按“后一颗处理前一颗”的方式无限接续，音频保持原样。详见 [二采无限修复](docs/二采无限修复.md)。

## 🆕 v1.1.23 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.23.md](release_notes/RELEASE_NOTES_v1.1.23.md)。

- **固定六角色音色库**：女孩、男孩、女主角、男主角、老太太、老爷子各有独立声线座位；支持描述音色和 5～15 秒参考音频克隆。
- **跨段音色锁定**：`(S1)`～`(S6)` 或 `@角色1`～`@角色6` 会启用对应座位；同一角色激活后，后续段落自动沿用声线与克隆参考，明确切换座位时才换声。角色显示名可自由修改。
- **角色音色库完全可选**：不添加该节点时，工作流会自动清除失效音色链接并跳过音色处理，主 H3 节点和所有视频段落按普通模式正常生成，不会因为缺少音色库报错。
- **单段抽卡继承最新音色**：提交时给每个段落显式注入音色库连接，避免抽卡目标从上一段缓存继承旧音色。
- **角色名精确匹配与安全报错**：改名后不会因前缀相同误触发；克隆音色缺少人物画面参考时会给出清楚的中文提示。
- **避免音色说明被朗读**：音色参数以静默制作元数据提交，并锁定只有 `<d>...</d>` 内的原文可以作为台词发声。
- **音色试听与 11 号工作流**：克隆音色可直接试听截取片段；描述音色使用插件内置 Spark-TTS 生成试听，并把听到的同一个 WAV 自动固定为 H3 克隆参考；11 号工作流已加入同一个角色音色库。
- **节点内完整音色操作**：每个角色可直接生成 Spark 音色、重新生成、试听/停止试听、清除生成音色，并把 `@角色N` 一键应用到 11 号主节点或 13 号视频段落提示词；重新生成始终读取当前语言和声线描述。
- **多人物图像音色绑定**：角色可绑定图像1～图像9，插入时自动写成 `@角色N <Picture X>`；H3 元数据会锁定该图像人物只能使用对应声线，并在素材过滤后同步重编号。
- **儿童/老年声线年龄优先**：儿童角色自动切换 Spark 最高音高并启用内部 `Child` 年龄 token；描述里出现“3岁、幼儿、奶声”等词也会触发，避免生成成年人声线。
- **全年龄男女声线映射**：覆盖儿童、少年、青年、成年、中年、老年六档；描述中的具体年龄数字和关键词会自动识别男女与年龄，并映射到 Spark 年龄 token 和对应男/女声线。重新生成时会直接朗读“固定声线描述”原文。
- **12 套声线模板与关键词标签**：固定声线描述旁可直接选择儿童、少年、青年、成年、中年、老年的男女模板，自动同步年龄、性别、音高和语速；18 个声音关键词可一键追加。
- **一键清除全部提示词**：分段提示词解析节点可清空解析文本和所有视频段落提示词，同时保留段落连线、秒数、种子、模型和最终合成设置。

## 🆕 v1.1.21 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.21.md](release_notes/RELEASE_NOTES_v1.1.21.md)。

- **Registry 安装包修复**：关闭 Git 中文路径转义并启用 UTF-8，管理器下载包现在会包含全部工作流和中文技能资源。
- **发布包自动验收**：Registry Action 会下载刚发布的 zip，关键入口、后端节点、至少 9 个工作流或许可证缺失时直接失败。
- **保留 1.1.20 功能**：旧节点兼容、资源库上传、PromptSplit 新旧 ID、Nodes 2.0 布局和真正单段抽卡全部保留。

## 🆕 v1.1.19 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.19.md](release_notes/RELEASE_NOTES_v1.1.19.md)。

- **开源安全与兼容性审计**：修复集成节点 ID 冲突并为旧工作流自动迁移，隔离 API Key、阻止素材路径穿越、移除 KJNodes 私有模块注入，并修复本地视觉模型图像载荷。
- **UI 与注册稳定性**：修复资源库恢复时的重复尺寸回调、补齐节点分类、减少全局补丁层级，并确保后端失败时不会启动半套前端。

## v1.1.18 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.18.md](release_notes/RELEASE_NOTES_v1.1.18.md)。

- **旧版数字人工作流兼容**：自动修复其他电脑加载旧工作流时 RIFE 模型、插帧倍率和清缓存值错位的问题，避免出现“输入超出范围 / 无效输入”。

## v1.1.17 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.17.md](release_notes/RELEASE_NOTES_v1.1.17.md)。

- **全能参考采样预览恢复**：修复“高级·加速”渲染器解码了预览帧却未回传原生预览通道的问题，全能参考、图生视频和数字人模式均可实时显示采样预览。
- **未引用音频不再误用**：`Ref2VA 全能参考` 只有提示词明确写入有效的 `<Audio N>` 时才读取资源库音频；没有音频标签时自动忽略音频，图片与视频参考保持不变。
- **数字人音频驱动保持兼容**：数字人（锁定音频）仍会直接把资源库音频作为驱动音轨，不要求额外填写 `<Audio N>`。

## v1.1.16 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.16.md](release_notes/RELEASE_NOTES_v1.1.16.md)。

- **资源库音频/视频直接引用**：点击音频、视频卡片会按当前光标位置插入 `<Audio N>` / `<Video N>`，播放按钮独立操作，不再抢占卡片点击。
- **截取时长与选段窗口**：音频/视频裁剪支持输入 `5`、`5 秒`、`5s` 或 `0:05`；新增“选段位置”滑块可整体移动固定时长片段。
- **视频段落布局修复**：提示词编辑区占满可用空间，参数和按钮固定行高，展开资源库后不再出现大块空白。
- **旧工作流引导帧迁移**：自动修复素材 JSON 错位到“引导帧位置”的旧数据，恢复为数字 `0` 并保留素材引用。

## 🆕 v1.1.15 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.15.md](release_notes/RELEASE_NOTES_v1.1.15.md)。

- **目录结构唯一命名空间加固**：`h3easy/`、`h3goohai/` 迁移至 `aicg3d_h3easy/`、`aicg3d_h3goohai/`，进一步降低与同源插件的加载冲突。
- **新增 3D 人物白模与分段采样器**：`MiniMax H3 Aicg 3D人物白模`（视频→动作骨架）与 `分段采样器` 节点。
- **新增 11 号多参考·首尾帧·数字人、15 号分段人物场景动作迁移替换工作流**。
- **数字人长音频自动分段**：超长音频自动切段顺序生成，配合 SelfLift 潜空间放大提速。
- **修复数字人模式渲染报错**：修复 `NameError: name 'self' is not defined`。

## 🆕 v1.1.14 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.14.md](release_notes/RELEASE_NOTES_v1.1.14.md)。

- **Registry 搜索修复**：修复安全扫描标记的 PyTorch 不安全反序列化。
- **安全加载权重**：非 SafeTensors 的 latent 放大模型改用 `weights_only=True` 加载。
- **公开管理器可检索**：新版本通过自动扫描后，其他电脑可直接在自定义节点管理器搜索安装。
- **开源兼容性加固**：内部 Python 包、HTTP 路由和前端扩展名全部改为 AICG3D 唯一命名空间，降低与同源插件的加载冲突。
- **分段解析正式节点 ID**：改为 `AICG3D_H3PromptSegmentSplit`；未安装旧 PromptSplit 插件时仍保留旧 ID 兼容别名，新工作流不会争用通用节点名。
- **API Key 不回传浏览器**：提示词优化设置只返回“是否已保存”，留空保存会保留原密钥，并支持显式清除。

## v1.1.13 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.13.md](release_notes/RELEASE_NOTES_v1.1.13.md)。

- **模型目录树**：加载器下拉按 `MiniMax`、`Krea2`、`Qwen`、`LTX2.5` 等文件夹分组显示。
- **LoRA 多级目录**：支持 `Krea2/Krea2-风格` 这类多层文件夹展开选择。
- **搜索与最近使用保留**：可直接跨目录搜索文件名，也可从最近使用快速选择。
- **经典界面兼容**：关闭 Nodes 2.0 后同样使用文件夹式选择。

## v1.1.12 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.12.md](release_notes/RELEASE_NOTES_v1.1.12.md)。

- **缺失素材自动检查**：打开工作流后批量检查图片、音频和视频是否存在。
- **精确段落提示**：提示缺失文件属于哪一个视频段落，资源卡片同步显示红色“素材缺失”。
- **一键清理**：确认缺失清单后可自动移除所有失效素材引用，也可保留后手动替换。
- **运行错误更明确**：段落内嵌素材缺失时，报错会直接指出“视频段落 N”。

## v1.1.11 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.11.md](release_notes/RELEASE_NOTES_v1.1.11.md)。

- **接入 Comfy Registry**：补齐官方节点管理器要求的项目名称、Publisher、显示名称、图标、关键词、仓库和问题反馈地址。
- **官方管理器可检索**：发布后可搜索 `AICG3D`、`短剧工作台` 或 `MiniMax H3` 找到本插件。
- **自动发布流程**：配置 Registry API Key 后，更新 `pyproject.toml` 版本即可通过 GitHub Actions 自动发布新版本。

## v1.1.10 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.10.md](release_notes/RELEASE_NOTES_v1.1.10.md)。

- **彻底取消上游 Easy 依赖**：单独安装本插件即可使用资源库，不需要另外安装 `ComfyUI-MiniMaxH3-Easy`。
- **修复干净环境启动失败**：移除启动日志中的 Emoji 输出，避免 Windows GBK 控制台无法编码导致整个插件被误判为加载失败。
- **资源库面板内置注册**：只加载 `comfyui-AICG3D` 时，`MiniMax H3 Aicg资源库` 也会正常显示上传区、图片、音频和视频面板。

## v1.1.9 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.9.md](release_notes/RELEASE_NOTES_v1.1.9.md)。

- **修复资源库白板**：`mediaLoaderResize` 测量后不再恢复旧的隐藏状态，面板会稳定保持可见。
- **同步可见状态**：同时修复 `hidden`、`type`、`options.hidden`、`options.canvasOnly` 与 `_state`，避免工作流重载后只恢复一半。
- **强制刷新前端**：入口提升为 `minimax_h3_easy_ui_v4.js`，避免浏览器继续加载旧模块。

## 🆕 v1.1.8 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.8.md](release_notes/RELEASE_NOTES_v1.1.8.md)。

- 为 13 号无限长视频工作流最终合成补齐 `imageio-ffmpeg` 运行依赖。
- 缺少 FFmpeg 时给出中文安装提示和 ComfyUI Python 安装命令。

## 🆕 v1.1.7 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.7.md](release_notes/RELEASE_NOTES_v1.1.7.md)。

- **资源库点击引用严格跟随光标**：图片、视频和音频标签现在插入到用户最后操作的位置，不再追加到提示词末尾。
- **兼容隐藏与可见 textarea**：优先使用用户实际点击的编辑框，同时保留原提示词编辑器的选区恢复。
- **前端入口版本化**：`minimax_h3_easy_ui_v3.js` 强制浏览器重新加载修复后的脚本，避免旧模块缓存。

## 🆕 v1.1.6 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.6.md](release_notes/RELEASE_NOTES_v1.1.6.md)。

- **五种 H3 任务模式已接入执行链**：`Ref2VA 全能参考（推荐）`、`T2VA 纯文本`、`I2VA 首帧参考`、`FL2VA 首尾帧参考`、`L2VA 尾帧参考`。
- **模式会真实改变生成行为**：素材数量校验、首尾帧条件、模型角色和提示词优化规则都会随模式切换。
- **本地模型扩展**：增加 Gemma3 / Gemma4 GGUF 视觉处理器支持，并自动过滤 MTP、draft、assistant 等辅助模型。
- **本地设置面板重排**：输出语言移到右侧，新增 llama.cpp 依赖提示和协助联系方式。
- **资源库点击引用**：图片、音频、视频可直接写入 `comfyui-AICG3D-SKILLS` 的“创意描述”提示词框。
- **提示词优化修复**：支持停止优化、本地模型真正中断，并强化英文输出锁定。

## 🆕 v1.1.5 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.5.md](release_notes/RELEASE_NOTES_v1.1.5.md)。

- **三个渲染器支持外部采样**：高级·加速、一采、二采放大均新增“外部采样器”和“外部调度器（Sigmas）”可选输入。
- **二采全路径支持**：二采整幅采样与分块采样都能使用外部采样器和 Sigmas。
- **经典画布修复**：“打开提示词优化设置”在关闭 Nodes 2.0 后恢复为按钮，可正常进入并选择本地模型。
- **工作流同步**：11、12、13 号工作流已同步最新插件版本与界面状态。
- **原采样方式兼容**：不连接外部输入时，继续使用原来的采样器、调度器、步数和 denoise 行为。

## v1.1.4 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.4.md](release_notes/RELEASE_NOTES_v1.1.4.md)。

- **外部采样器接口**：无限段落顺序生成（全局设置）新增“外部采样器”和“外部调度器（Sigmas）”输入，连接后自动覆盖内置采样器、调度器、步数和 denoise 截断。
- **DMAD 官方四步加速**：支持 `DMAD Sampler (re-noise)` + `DMAD Sigmas`，官方推荐参数为 LoRA 强度 1.0、步数 4、shift 12。
- **音频偏移修正**：工作流加入 `MiniMaxH3SigmaShift`，推荐 `shift_video=12`、`shift_audio=2`。
- **13 号 1.2 工作流已接线**：DMAD Sampler、DMAD Sigmas、MiniMaxH3SigmaShift 已连接到全局设置，打开即可使用。
- **兼容原采样方式**：不连接外部采样器和 Sigmas 时，继续使用原来的 sampler_name、scheduler、steps 和 denoise。

## v1.1.3 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.3.md](release_notes/RELEASE_NOTES_v1.1.3.md)。

- **视频段落编辑区重排**：提示词框自动占据节点的主要伸缩空间，底部操作按钮固定为 32px，不再出现大面积空白。
- **资源库展开更稳定**：资源库打开时最高 320px，内容过多时内部滚动；提示词仍保留可编辑空间，节点可自由拖高且不会回弹。
- **资源库开关修复**：展开、收起、再次展开可以正常循环，修掉收起后无法重新打开、节点空白区和按钮失效问题。
- **移除抽卡与锁定入口**：多段拼接工作流不再提供容易破坏接缝一致性的局部重抽功能，保留添加下一段、打开下一段和删除这一段。
- **13 号 1.2 工作流同步**：节点布局、按钮文案和操作说明已与 v1.1.3 插件同步。


## v1.1.2 更新摘要

> **重要**：分段提示词解析已经完整内置在本插件中。请不要再同时安装独立的 `ComfyUI-AICG3D-PromptSplit`，两个同名节点会互相覆盖前端逻辑。
>
> 宣传视频分镜见 [docs/AICG3D_无限分段_6分钟宣传片分镜与剧本.md](docs/AICG3D_无限分段_6分钟宣传片分镜与剧本.md)。

- **资源库贯穿段落链**：外部 AICG3D 资源库接到第一段后，素材状态会自动同步到后续每个视频段落节点，后续段落提示词里的 `@图片N`、`@视频N`、`@音频N` 可以正确生效。
- **继承与覆盖并存**：没有单独设置素材的段落自动继承上游资源；某一段打开资源库并增删素材后，会转为该段独立资源，并继续向下游同步。
- **13 号工作流 1.2 同步更新**：工作流中的三个视频段落都已写入继承资源状态，直接运行也能拿到同一套外部素材。
- **下载最新 13 号工作流**：[13.AICG3D_MiniMax H3 无限长视频短剧工作流.json](workflows/13.AICG3D_MiniMax%20H3%20%E6%97%A0%E9%99%90%E9%95%BF%E8%A7%86%E9%A2%91%E7%9F%AD%E5%89%A7%E5%B7%A5%E4%BD%9C%E6%B5%81.json)。
- **接缝运动桥**：仅对同一镜头的一帧姿态跳变做轻微桥接，保留正常动作，避免把硬切误处理成叠化。
- **曝光过渡收敛**：接缝加性亮度窗口缩短为 12 帧，整段亮度校正上限降到 0.04，减少拼接处的曝光波动。
- **本地 MiniMax H3 无限分段**：延续现有的 `FL2VA + REF2VA` 混合模型路线，支持本地连续分段、尾帧续写和最终合成。

## v1.1.1 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.1.md](release_notes/RELEASE_NOTES_v1.1.1.md)。

- **跨段接缝曝光锁定**：匹配上一段尾帧的低频色光，使用有上限的全局亮度对齐，解决分段拼接处明暗跳变。
- **拼接模糊修复**：修正接缝亮度过渡的运算顺序，避免为平滑曝光而把整段画面模糊。
- **每段独立资源库**：`MiniMax H3 Aicg 视频段落` 节点可直接展开独立图片 / 音频 / 视频资源区，点选素材即写入 `@引用`。
- **段落链自动操作**：新增“添加下一段”“删除这一段”，自动维护 `上一分段 → 下一分段` 与最终合成视频连接。
- **提示词批量填入更稳定**：一键填入后保持节点尺寸，第一段连着解析线时仍可手动输入；开始输入会自动断开该段提示词连线。
- **节点尺寸锁定**：视频段落节点不再因点击、填词、开关资源库而自动放大或缩小，只响应手动拖拽。
- **无限视频提示词模板 V2（沿用 V1 文件名）**：融合通用版剧情导演方法，强化单核心事件、单主要动作、单主要运镜、段间曝光连续和对白时长控制；最终输出固定为一个 `text` 代码块，可直接使用界面右上角“一键复制”。

## 🌟 核心价值 (Core Value)

### 🛡️ 工业级稳定性：零冲突命名空间
针对 ComfyUI 生态中常见的节点同名冲突（Node Collision）问题，本插件采用了 **Forced Unique Namespace (强制唯一命名空间)** 架构。
- **唯一标识**：所有核心节点均采用 AICG3D_H3_ 专属前缀。
- **独立运行**：无论你的环境中安装了多少个 MiniMax 相关分支，AICG3D 均能独立运行，彻底杜绝节点被覆盖、工作流失效或界面崩溃的情况。

### ⚙️ 全链路功能集成 (Integrated Pipeline)
无需安装碎片化的插件，一个包即可覆盖从创意到成片的完整流程：

- **智能剧本分段 (PromptSplit)**：支持将长剧本/提示词自动拆分为逻辑段落 -> 一键映射至视频时间轴 -> 自动优化随机种子。
- **高精度渲染采样 (Advanced Sampler)**：集成高度优化的采样策略，确保视频在动态一致性与视觉质量之间达到最佳平衡。
- **Latent 深度放大 (HD Upscaler)**：内置专为 H3 设计的潜空间放大算法，在提升分辨率的同时，有效保留细节并减少伪影。
- **SelfLift 策略增强**：支持高级的自提升采样方案，极大增强画面细节的丰富度。

## 🛠️ 安装与部署

1.  **快速安装**：将 `comfyui-AICG3D` 文件夹复制到 ComfyUI 的 `custom_nodes/` 目录下。
2.  **启动服务**：重启 ComfyUI。
3.  **定位节点**：在右键菜单中找到 **AICG3D** 分类即可开始创作。

推荐直接在 **ComfyUI Manager / Comfy Registry** 搜索 `AICG3D`、`短剧工作台` 或 `MiniMax H3` 安装。核心包保持零强制依赖；角色音色、试听、提示词远程优化和 FFmpeg 合成等扩展功能需要在当前 ComfyUI 的 Python 环境手动安装 `requirements-optional.txt`。安装完成后重启 ComfyUI，并在浏览器执行 `Ctrl+F5`。

本插件已内置资源库、分段提示词解析和 H3 核心节点，**不需要另外安装 `ComfyUI-MiniMaxH3-Easy` 或独立的 `ComfyUI-AICG3D-PromptSplit`**。同时安装上游 Easy 插件时，本插件会保留自己的 `AICG3D_H3*` 节点，避免同名节点互相覆盖。

### FFmpeg 运行依赖（13 号工作流最后合成必需）

13 号无限长视频工作流的「最终合成视频」需要 FFmpeg。插件会优先使用 `imageio-ffmpeg`，其次查找系统 `PATH` 中的 `ffmpeg.exe`，也可通过 `VHS_FORCE_FFMPEG_PATH` 指定路径。

如果安装后仍提示缺少 FFmpeg，请在当前 ComfyUI 使用的 Python 环境执行：

```powershell
python.exe -m pip install imageio-ffmpeg
```

也可以一次安装全部扩展功能依赖：

```powershell
python.exe -m pip install -r requirements-optional.txt
```

然后重启 ComfyUI。请勿安装到系统 Python 或其他虚拟环境，否则节点仍可能找不到。

### Spark-TTS 模型（角色音色库必需，模型本体不随插件分发）

插件已经内置 Spark-TTS 推理源码、节点注册和 5 个 `Step-Audio-speakers` 参考音频，**不需要再安装 `ComfyUI_SparkTTS`**。只有大模型权重需要单独下载：

```text
ComfyUI/
└─ models/
   └─ tts/                         # Windows 下 models\TTS 也兼容
      └─ Spark-TTS-0.5B/
         ├─ config.yaml
         ├─ BiCodec/
         ├─ LLM/
         └─ wav2vec2-large-xlsr-53/
```

下载地址：https://huggingface.co/SparkAudio/Spark-TTS-0.5B

角色音色库会显示模型状态；缺少模型时，鼠标移到提示条或点击“生成 Spark 音色”会给出缺失目录、缺失文件和下载地址。也可用环境变量 `AICG3D_SPARK_TTS_MODEL` 指向模型目录。

### 官方工作流的附加节点



- 13 号 1.2 工作流使用 `DMADSampler` / `DMADSigmas`，需安装 [ComfyUI-DMAD](https://github.com/Yzmblog/DMAD)。
- 11 号数字人工作流中的 `MiniMaxH3DMADSampler` 来自 `Spark-H3`；没有该节点时请改用工作流内可用的 AICG3D 采样器，或安装对应节点包。
- 角色音色库的描述音色试听使用本插件内置的 `AICG3D Spark-TTS 固定声线生成`，无需另装 `ComfyUI_SparkTTS`；只要求单独下载 `Spark-TTS-0.5B` 模型，缺少时节点会明确提示目录和下载地址。
- 12、13 号工作流里的 `Label (rgthree)` 只是画布注释；缺少 [rgthree-comfy](https://github.com/rgthree/rgthree-comfy) 时不影响后端生成，但建议安装以正常显示标签。



> **💡 迁移说明**：新工作流使用 `AICG3D_H3*` 命名空间。旧工作流常用到的 `MiniMaxH3EasyMediaLoader`、`MiniMaxH3EasySequenceGlobal`、`MiniMaxH3EasySequenceSegment` 和 `MiniMaxH3EasySequenceCombine` 已提供自动兼容注册；只有遇到未覆盖的旧节点时，才需要手动替换为对应的 `AICG3D_H3*` 节点。

## 🤝 核心贡献者与致谢 (Core Contributors & Acknowledgements)

本项目是通过整合社区顶顶成果并进行工程化重构而成的，其稳定性与功能的实现离不开以下核心作者的贡献：

- **主架构师与整合者 (Integration & Maintenance)**: 
  - **AICG3D** - 负责整体架构设计、强制命名空间重构、稳定性优化以及插件的日常维护。
- **核心模块贡献者 (Core Engine Developers)**: 
    - **@goohai** - 提供了 Goohai-MiniMax-H3_Integration 的核心实现，包括强大的提示词优化能力与集成框架。
    - **@nkxx188** - 提供了 ComfyUI-MiniMaxH3-Easy 的核心节点实现，包括高效的采样策略与渲染流程。
- **社区支持**: 感谢所有在 MiniMax H3 生态中提供反馈、测试并贡献灵感的 ComfyUI 创作者。

## 📜 开源协议

本项目遵循 GNU GPL v3.0 或更高版本（GPL-3.0-or-later）协议开源。
## 🆕 v1.1.20 更新摘要

完整说明见 [RELEASE_NOTES_v1.1.20.md](release_notes/RELEASE_NOTES_v1.1.20.md)。

- **管理器安装兼容修复**：补齐旧版 `MiniMaxH3Easy*` 资源库和段落节点 ID，旧工作流不再因为缺少节点而显示白板。
- **分段提示词解析恢复**：新旧节点 ID 都安装“一键填入全部视频段落”和“✦ 优化提示词”按钮，并在工作流加载后兜底初始化。
- **资源库上传恢复**：修复 Nodes 2.0 资源面板的父容器尺寸和前端归属判断，上传、图片/音频/视频列表和清空按钮保持可用。
- **Nodes 2.0 布局修复**：资源库面板固定在节点内部 320px 区域滚动，不再溢出节点或盖住其他节点。
- **单段抽卡修复**：点击任意“抽卡时段”只采样当前段，上一段从本进程缓存读取；右上角运行只做最终合成。
- **干净安装验证**：已实测媒体上传、旧/新分段解析节点、三段自动填入、第一段文本编辑和提示词框尺寸保持。
- **注册与发布审计**：Python 全量编译、前端全量语法检查、Registry 发布校验和 10 项开源安全与兼容回归测试通过。
