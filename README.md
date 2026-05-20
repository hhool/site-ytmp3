# ytmp3

Lightweight YouTube converter prototype.

Overview: This repository contains a minimal runnable prototype for converting YouTube videos to MP3/MP4. Implementations include:
- Backend: FastAPI + yt-dlp (synchronous `/convert` and asynchronous `/convert_async` + `/status` + `/download`).
- Frontend: static page (`frontend/index.html`) with async job flow and Chinese/English i18n.
- Browser extension: Manifest V3 popup (`extension/`), which can create async jobs and open a monitor page.

Quick start

```bash
# go to repository root
cd /Users/yanmenghou/Desktop/ytmp3

# create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# install backend dependencies
pip install -r ytmp3/backend/requirements.txt

# run the backend (listens on 127.0.0.1:8000 by default)
uvicorn ytmp3.backend.main:app --reload --host 0.0.0.0 --port 8000

# open frontend
open http://127.0.0.1:8000/frontend/index.html
```

Load extension (developer mode): open `chrome://extensions/` in Chrome/Edge, enable Developer Mode, click "Load unpacked extension" and choose the `ytmp3/ytmp3/extension` directory.

Main API (local development):
- `POST /convert` — synchronous convert and return a file (useful for short/small files during debugging).
- `POST /convert_async` — create an async conversion job and return a `job_id`.
- `GET /status/{job_id}` — check job status.
- `GET /download/{job_id}` — download the completed job file.

Notes / Security & Legal
- Only download or convert videos you have the legal right to use. Before deploying to production, implement authentication, rate limits, job persistence, logging, and copyright compliance workflows.

Project structure
- ytmp3/backend — backend code and dependencies.
- ytmp3/frontend — static frontend pages and i18n strings.
- ytmp3/extension — browser extension source (popup & monitor).
- docs — documentation and reference materials.

License: MIT (example project — replace with appropriate license and legal notices for production).

## Docker deployment

Build and run with Docker (recommended for deployment/testing):

```bash
# build image
docker-compose build

# start service
docker-compose up -d

# check logs
docker-compose logs -f

# stop
docker-compose down
```

Notes:
- The Docker image installs `ffmpeg` which is required by `yt-dlp` for media processing.
- Static frontend and extension directories are mounted into the container for easy local edits.
