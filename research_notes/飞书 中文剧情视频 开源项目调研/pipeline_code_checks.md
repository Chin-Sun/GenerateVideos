
## micro-tree https://api.github.com/repos/Anil-matcha/Open-AI-Micro-Drama-Generator/git/trees/main?recursive=1
client/components/VideoResult.js
server/pipelines/idea2video.py
server/pipelines/script2video.py
server/tools/muapi_video_generator.py
server/utils/video.py
local-tree HTTP Error 403: rate limit exceeded
jelly-tree HTTP Error 403: rate limit exceeded

## micro-api https://raw.githubusercontent.com/Anil-matcha/Open-AI-Micro-Drama-Generator/main/server/api.py
import asyncio
import json
import os
import uuid
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from pipelines.idea2video import Idea2VideoPipeline
from pipelines.script2video import Script2VideoPipeline
from agents.character_extractor import CharacterExtractor


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(title="MicroDrama AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure outputs directory exists on startup
OUTPUTS_DIR = Path("outputs")
OUTPUTS_DIR.mkdir(exist_ok=True)

app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")


# ---------------------------------------------------------------------------
# In-memory job store
# ---------------------------------------------------------------------------
# job structure:
# {
#   "status": "running" | "completed" | "failed",
#   "events": [...],           # list of JSON-serialisable dicts
#   "video_url": str | None,
#   "error": str | None,
#   "queue": asyncio.Queue,    # fed by pipeline, consumed by SSE
# }
jobs: Dict[str, Dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------
class GenerateRequest(BaseModel):
    idea: str
    user_requirement: str = ""
    style: str = "Cinematic"
    mode: str = "idea2video"  # "idea2video" or "script2video"
    script: str = ""          # used when mode == "script2video"


class GenerateResponse(BaseModel):
    job_id: str


class JobResult(BaseModel):
    job_id: str
    status: str
    video_url: str | None = None
    error: str | None = None


# ---------------------------------------------------------------------------
# Background pipeline runner
# ---------------------------------------------------------------------------
async def run_pipeline(job_id: str, req: GenerateRequest) -> None:
    job = jobs[job_id]
    queue: asyncio.Queue = job["queue"]

    async def progress_callback(stage: str, message: str, progress: int) -> None:
        event = {
            "type": "progress",
            "stage": stage,
            "message": message,
            "progress": progress,
        }
        job["events"].append(event)
        await queue.put(event)

    try:
        if req.mode == "script2video":
            # Script2Video: user provides a single scene script
            pipeline = Script2VideoPipeline()
            character_extractor = CharacterExtractor()

            await progress_callback("characters", "Extracting characters...", 10)
            characters = await character_extractor.extract_characters(req.script or req.idea)

            output_dir = str(OUTPUTS_DIR / job_id / "scene_00")
            video_path = await pipeline.run(
                script=req.script or req.idea,
                characters=characters,
                user_requirement=req.user_requirement,
                style=req.style,
                working_dir=output_dir,
                progress_callback=progress_callback,
                scene_idx=0,
                base_progress=15,
                progress_range=80,
            )
        else:
            # Idea2Video: full agentic pipeline
            pipeline = Idea2VideoPipeline()
            video_path = await pipeline.run(
                idea=req.idea,
                user_requirement=req.user_requirement,
                style=req.style,
                job_id=job_id,
                progress_callback=progress_callback,
            )

        # Convert local path to URL
        rel_path = Path(video_path).relative_to(Path("."))
        video_url = f"/{rel_path}"

        job["status"] = "completed"
        job["video_url"] = video_url

        complete_event = {
            "type": "complete",
            "video_url": video_url,
            "progress": 100,
        }
        job["events"].append(complete_event)
        await queue.put(complete_event)

    except Exception as exc:
        error_msg = str(exc)
        job["status"] = "failed"
        job["error"] = error_msg

        error_event = {
            "type": "error",
            "message": error_msg,
            "progress": -1,
        }
        job["events"].append(error_event)
        await queue.put(error_event)

    finally:
        # Signal SSE consumers that the stream is done
        await queue.put(None)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "microdrama-api"}


@app.post("/api/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "running",
        "events": [],
        "video_url": None,
        "error": None,
        "queue": asyncio.Queue(),
    }
    background_tasks.add_task(run_pipeline, job_id, req)
    return GenerateResponse(job_id=job_id)


@app.get("/api/status/{job_id}")
async def status_stream(job_id: str):
    """SSE endpoint — streams progress events until job completes or fails."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    async def event_generator():
        # Replay already-emitted events first (in case client reconnects)
        for event in job["events"]:
            yield f"data: {json.dumps(event)}\n\n"

        # If job is already done, we've replayed everything — finish
        if job["status"] in ("completed", "failed"):
            return

        # Otherwise stream live events from queue
        queue: asyncio.Queue = job["queue"]
        while True:
            event = await queue.get()
            if event is None:
                # Sentinel — pipeline finished
                break
            yield f"data: {json.dumps(event)}\n\n"
            if event.get("type") in ("complete", "error"):
                break

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/result/{job_id}", response_model=JobResult)
async def get_result(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    return JobResult(
        job_id=job_id,
        status=job["status"],
        video_url=job.get("video_url"),
        error=job.get("error"),
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)


## micro-video https://raw.githubusercontent.com/Anil-matcha/Open-AI-Micro-Drama-Generator/main/server/tools/muapi_video_generator.py
import asyncio
import os
from typing import Optional

import httpx


MUAPI_BASE = "https://api.muapi.ai/api/v1"
POLL_INTERVAL = 3  # seconds

# Short royalty-free placeholder video returned in sandbox mode.
_SANDBOX_VIDEO_URL = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"


class MuAPIVideoGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ["MUAPI_KEY"]
        self.headers = {"x-api-key": self.api_key, "Content-Type": "application/json"}

    async def generate_video_from_image(
        self,
        prompt: str,
        image_url: str,
        duration: int = 5,
        aspect_ratio: str = "16:9",
    ) -> str:
        """Generate a cinematic video clip from an image + motion prompt.

        Primary: Seedance 2 VIP I2V — the highest quality Seedance model,
        with cinematic motion, strong temporal consistency, and excellent
        dramatic scene handling. Supports 4–15 second clips at 16:9.

        Fallback: Kling v2.1 Master I2V — master-tier Kling with superior
        motion quality vs Standard, used if Seedance 2 VIP fails.

        Returns URL of generated video.
        """
        # Seedance 2 VIP supports 4-15s; clamp to valid range
        sd2_duration = max(4, min(15, duration))

        skip_seedance = os.environ.get("SKIP_SEEDANCE", "").lower() in ("true", "1", "yes") or \
                        os.environ.get("USE_SEEDANCE", "").lower() in ("false", "0", "no")

        if skip_seedance:
            print("Skipping Seedance 2 VIP, using Kling directly...")
            kling_duration = 5 if duration <= 7 else 10
            return await self._kling_master(prompt, image_url, kling_duration, aspect_ratio)

        try:
            return await self._seedance2_vip(prompt, image_url, sd2_duration, aspect_ratio)
        except Exception as e:
            print(f"Seedance 2 VIP failed ({e}), falling back to Kling Master...")
            # Kling supports 5 or 10s
            kling_duration = 5 if duration <= 7 else 10
            return await self._kling_master(prompt, image_url, kling_duration, aspect_ratio)

    async def _seedance2_vip(
        self, prompt: str, image_url: str, duration: int, aspect_ratio: str
    ) -> str:
        model = os.environ.get("SEEDANCE_MODEL", "seedance-2-vip-image-to-video")
        async with httpx.AsyncClient(timeout=60) as client:
            try:
                resp = await client.post(
                    f"{MUAPI_BASE}/{model}",
                    headers=self.headers,
                    json={
                        "prompt": prompt,
                        "images_list": [image_url],
                        "duration": duration,
                        "aspect_ratio": aspect_ratio,
                    },
                )
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code in (401, 403):
                    print("[Sandbox] Video generation (Seedance 2) not available — returning placeholder.")
                    return _SANDBOX_VIDEO_URL
                raise
            data = resp.json()

        request_id = data.get("request_id") or data.get("id")
        if not request_id:
            raise ValueError(f"No request_id in Seedance 2 VIP response: {data}")

        result = await self._poll_until_done(request_id, timeout=600)
        return self._extract_url(result)

    async def _kling_master(
        self, prompt: str, image_url: str, duration: int, aspect_ratio: str
    ) -> str:
        model = os.environ.get("KLING_MODEL", "kling-v2.1-master-i2v")
        async with httpx.AsyncClient(timeout=60) as client:
            try:
                resp = await client.post(
                    f"{MUAPI_BASE}/{model}",
                    headers=self.headers,
                    json={
                        "prompt": prompt,
                        "image_url": image_url,
                        "duration": duration,
                        "aspect_ratio": aspect_ratio,
                    },
                )
                resp.raise_for_status()
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code in (401, 403):
                    print("[Sandbox] Video generation (Kling Master) not available — returning placeholder.")
                    return _SANDBOX_VIDEO_URL
                raise
            data = resp.json()

        request_id = data.get("request_id") or data.get("id")
        if not request_id:
            raise ValueError(f"No request_id in Kling Master response: {data}")

        result = await self._poll_until_done(request_id, timeout=600)
        return self._extract_url(result)

    def _extract_url(self, result: dict) -> str:
        outputs = result.get("outputs", [])
        if not outputs:
            raise ValueError(f"No outputs in result: {result}")
        output = outputs[0]
        if isinstance(output, dict):
            return output.get("url") or output.get("video_url") or str(output)
        return str(output)

    async def _poll_until_done(self, request_id: str, timeout: int = 600) -> dict:
        elapsed = 0
        async with httpx.AsyncClient(timeout=30) as client:
            while elapsed < timeout:
                await asyncio.sleep(POLL_INTERVAL)
                elapsed += POLL_INTERVAL

                resp = await client.get(
                    f"{MUAPI_BASE}/predictions/{request_id}/result",
                    headers=self.headers,
                )
                resp.raise_for_status()
                data = resp.json()

                status = data.get("status", "")
                if status == "completed":
                    return data
                elif status == "failed":
                    raise RuntimeError(
                        f"MuAPI video job {request_id} failed: {data.get('error', 'unknown error')}"
                    )
                elif status == "cancelled":
                    raise RuntimeError(f"MuAPI video job {request_id} was cancelled")

        raise TimeoutError(
            f"MuAPI video job {request_id} did not complete within {timeout}s"
        )


## cine-license https://raw.githubusercontent.com/UllrAI/CineGen-ShortDrama/main/license.md
AniKuku Community License (ACL) v1.0
Copyright (c) 2026 AniKuku.com

1. Grant of License

Subject to the terms and conditions of this License, permission is hereby granted to any person obtaining a copy of this software and associated documentation files (the “Software”) to use, copy, modify, and distribute the Software for personal, educational, research, and non-commercial purposes.

Commercial use is permitted only under the conditions described in Section 4.

2. Attribution Requirement

Any public use, redistribution, modification, derivative work, or deployment of this Software (including SaaS or hosted services) must clearly and prominently include:

- A visible hyperlink to https://AniKuku.com
- A visible hyperlink to the original source repository of this Software

The links must:
- Be publicly accessible
- Not be hidden behind login walls
- Not use "nofollow" or similar attributes intended to suppress attribution
- Be placed in a reasonable and visible location (such as footer, about page, documentation, or UI credits section)

3. Modifications

You may modify and create derivative works of the Software, provided that:
- This License is included in the distribution
- The attribution requirements in Section 2 are fully preserved

4. Commercial Use Without Attribution

If you wish to:
- Use the Software commercially without including the required hyperlinks
- Remove attribution
- Embed the Software in a proprietary product without visible credit

You must obtain a commercial license.

To request a commercial license, contact:
CineGen@ullrai.com

5. Prohibited Actions

You may not:
- Remove this License from the source code
- Misrepresent the origin of the Software
- Use AniKuku branding or trademarks beyond the required attribution

6. Disclaimer

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY.

7. Acceptance

By using, copying, modifying, or distributing this Software, you agree to be bound by this License.


## local-deploy https://raw.githubusercontent.com/xuanyustudio/LocalMiniDrama/main/docs/quickstart.md
# 快速开始 / 开发指南

**导航：[项目主页](../README.md) | [English](en.md) | [AI 配置](configuration.md) | [版本历史](changelog.md)**

---

## 目录

- [运行方式一：下载 exe（推荐普通用户）](#运行方式一下载-exe推荐普通用户)
- [运行方式二：开发模式（推荐开发者）](#运行方式二开发模式推荐开发者)
  - [环境要求](#环境要求)
  - [启动后端](#1-启动后端)
  - [启动前端](#2-启动前端)
  - [一键启动脚本](#3-一键启动脚本)
- [打包为 Windows exe](#打包为-windows-exe)
- [配置文件说明](#配置文件说明)
- [数据库与数据目录](#数据库与数据目录)
- [常见问题 FAQ](#常见问题-faq)

---

## 运行方式一：下载 exe（推荐普通用户）

1. 前往 **[Releases](../../releases)** 页面下载最新版本：
   - `本地短剧助手 Setup x.x.x.exe` — NSIS 安装包（推荐，可选安装路径）
   - `本地短剧助手 x.x.x.exe` — 免安装便携版，解压即用

2. 双击运行，软件会自动启动内置后端服务。

3. 首次运行会在以下路径生成配置文件：
   ```
   %APPDATA%\LocalMiniDrama\backend\configs\config.yaml
   ```

4. 点击软件右上角「AI 配置」，填入你的 AI API Key，即可开始使用。

> 💡 不知道去哪里申请 API Key？请看 → [AI 配置指南](configuration.md)

---

## 运行方式二：开发模式（推荐开发者）

### 环境要求

| 依赖 | 版本要求 |
|------|----------|
| Node.js | >= 18 |
| npm | 随 Node.js 附带 |
| Git | 任意版本 |

---

### 1. 启动后端

```bash
cd backend-node

# 安装依赖
npm install

# 复制配置文件模板
cp configs/config.example.yaml configs/config.yaml
# Windows PowerShell:
# copy configs\config.example.yaml configs\config.yaml

# 编辑 config.yaml，填入你的 AI API 地址与密钥（见配置指南）

# 首次运行：初始化数据库
npm run migrate

# 启动服务（默认端口 5679）
npm start

# 开发模式（热重载）
npm run dev
```

后端启动成功后，终端会输出：
```
Server started on port 5679
```

---

### 2. 启动前端

**新开一个终端窗口：**

```bash
cd frontweb

# 安装依赖
npm install

# 启动开发服务器（默认端口 3013，自动代理到后端 5679）
npm run dev
```

浏览器访问 `http://localhost:3013` 即可看到界面。

---

### 3. 一键启动脚本

在项目根目录提供了一键启动脚本，**同时启动后端和前端**：

**Windows（双击运行）：**
```
run_dev.bat
```

**PowerShell：**
```powershell
.\run_dev.ps1
```

脚本会分别在两个窗口中启动后端（端口 5679）和前端（端口 3013），并自动打开浏览器。

---

## 打包为 Windows exe

> 打包前请先确保已完成后端和前端的 `npm install`。

```bash
cd desktop

# 安装 Electron 相关依赖
npm install

# 打包（生成 NSIS 安装包 + 便携版 exe）
npm run dist

# 国内网络 Electron 下载慢时，使用镜像加速：
npm run dist:cn
```

打包产物位于 `desktop/release/` 目录：
- `本地短剧助手 Setup x.x.x.exe` — NSIS 安装包
- `本地短剧助手 x.x.x.exe` — 便携版

**打包原理：**
1. 构建前端静态文件
2. 复制后端代码与前端产物到 `desktop/` 
3. electron-builder 打包为 Windows exe

---

## 配置文件说明

配置文件位于 `backend-node/configs/config.yaml`（开发模式）或 `%APPDATA%\LocalMiniDrama\backend\configs\config.yaml`（exe 模式）。

主要配置项：

```yaml
server:
  port: 5679          # 后端端口

database:
  path: ./data/drama_generator.db   # SQLite 数据库路径

storage:
  local_path: ./data/storage        # 生成图片/视频的本地存储目录

language: zh          # 界面及提示词语言（zh / en）

style:
  default_style: realistic           # 默认画风
  default_image_ratio: "16:9"        # 默认图片比例
  default_video_ratio: "16:9"        # 默认视频比例
```

AI 服务配置通过软件内「AI 配置」页面管理，无需手动编辑 YAML。  
详细说明请见 → [AI 配置指南](configuration.md)

---

## 数据库与数据目录

| 路径 | 说明 |
|------|------|
| `backend-node/data/drama_generator.db` | SQLite 数据库（开发模式） |
| `backend-node/data/storage/` | 生成的图片和视频文件 |
| `%APPDATA%\LocalMiniDrama\` | exe 模式下的所有数据 |

> ⚠️ 升级版本前建议备份 `data/` 目录；数据库会在启动时自动执行迁移脚本，一般无需手动操作。

---

## 常见问题 FAQ

### Q: 后端启动报错 `Cannot find module 'better-sqlite3'`

```bash
cd backend-node
npm install
```

如果仍然报错，可能是 Node.js 版本不兼容，请升级到 >= 18。

---

### Q: 前端报错 `Failed to fetch` 或 API 请求 404

确认后端已正常启动（终端显示 `Server started on port 5679`），且前端代理配置指向正确端口。  
检查 `frontweb/vite.config.js` 中的 `proxy` 配置，确保 target 为 `http://localhost:5679`。

---

### Q: 打包 exe 时 Electron 下载失败

使用国内镜像：
```bash
cd desktop
npm run dist:cn
```

或手动设置环境变量后再运行：
```bash
set ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/
npm run dist
```

---

### Q: 生成的图片/视频保存在哪里？

开发模式：`backend-node/data/storage/`  
exe 模式：`%APPDATA%\LocalMiniDrama\backend\data\storage\`

目录结构：
```
storage/
├── images/        # 分镜生成的图片
├── characters/    # 角色图片
├── scenes/        # 场景图片
├── videos/        # 生成的视频片段
└── merged/        # 合成后的完整视频
```

---

### Q: 如何备份/迁移项目数据？

**方法一（推荐）**：在软件首页点击项目卡片上的「导出」按钮，下载 ZIP 格式的工程文件，在新机器上导入即可。

**方法二**：直接备份整个 `data/` 目录，将其复制到新机器的相同位置。

---

### Q: 支持 Mac / Linux 吗？

目前仅测试了 Windows。后端（Node.js）理论上跨平台，前端（Vue 3）完全跨平台，但桌面版（Electron）打包仅配置了 Windows 目标。  
欢迎提 PR 添加 Mac / Linux 打包支持。

---

[← 返回项目主页](../README.md)
