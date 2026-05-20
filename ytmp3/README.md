# ytmp3

轻量级 YouTube 转换器原型（后端：FastAPI + yt-dlp；前端：静态 HTML；浏览器扩展：Manifest V3 popup）。

快速启动（macOS / Linux）:

```bash
# ytmp3

轻量级 YouTube 转换器原型（后端：FastAPI + yt-dlp；前端：静态 HTML；浏览器扩展：Manifest V3 popup）。

Lightweight YouTube converter prototype (backend: FastAPI + yt-dlp; frontend: static HTML; browser extension: Manifest V3 popup).

快速启动（macOS / Linux） / Quick start (macOS / Linux):

```bash
# 1) 后端依赖安装 / Install backend deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# 2) 启动后端 / Run the backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 3) 在浏览器打开前端 / Open the frontend in browser
# 本地静态文件已由后端挂载：
# - 前端页面: http://127.0.0.1:8000/frontend/index.html
# - 扩展监控页: http://127.0.0.1:8000/extension/monitor.html?job=<job_id>
open http://127.0.0.1:8000/frontend/index.html
```

说明：后端使用 `yt-dlp` 命令行工具，建议在系统中安装 `yt-dlp`（或在虚拟环境中通过 `pip install yt-dlp`）。生产环境请参考 Docker 化和安全策略（转码限制、队列、鉴权、版权合规）。

Note: The backend uses the `yt-dlp` CLI tool; install it system-wide or in the virtualenv via `pip install yt-dlp`. For production, consider Dockerization, job queues, rate limits, authentication and copyright compliance.
