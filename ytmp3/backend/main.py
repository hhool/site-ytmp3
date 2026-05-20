from fastapi import FastAPI, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import tempfile
import os
import uuid
import threading
import json
from typing import Dict, Any, Optional

import redis
import time

app = FastAPI()

# Serve frontend and extension static files
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
app.mount("/extension", StaticFiles(directory="extension"), name="extension")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _cleanup_path(path: str):
    try:
        if os.path.isdir(path):
            for f in os.listdir(path):
                try:
                    os.remove(os.path.join(path, f))
                except Exception:
                    pass
            os.rmdir(path)
        elif os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


# Redis client for job persistence. Falls back to in-memory dict if Redis unavailable.
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
_redis_client: Optional[redis.Redis] = None
try:
    _redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    _redis_client.ping()
except Exception:
    _redis_client = None


def _set_job(job_id: str, data: Dict[str, Any]):
    if _redis_client:
        _redis_client.set(f"job:{job_id}", json.dumps(data))
    else:
        JOBS[job_id] = data


def _get_job(job_id: str) -> Optional[Dict[str, Any]]:
    if _redis_client:
        val = _redis_client.get(f"job:{job_id}")
        return json.loads(val) if val else None
    else:
        return JOBS.get(job_id)


# Job TTL (seconds) and cleanup helpers
JOB_TTL_SECONDS = int(os.environ.get('JOB_TTL_SECONDS', '3600'))


def _expire_job_cleanup(job_id: str):
    """Called after JOB_TTL_SECONDS to cleanup tmpdir and remove job record."""
    job = _get_job(job_id)
    if not job:
        return
    tmpdir = job.get('tmpdir')
    try:
        _cleanup_path(tmpdir)
    except Exception:
        pass
    # remove job record
    try:
        if _redis_client:
            _redis_client.delete(f"job:{job_id}")
        else:
            JOBS.pop(job_id, None)
    except Exception:
        pass


def _cleanup_and_delete_job(job_id: str, delay: int = 30):
    """Schedule cleanup after a short delay (used after download)."""
    time.sleep(delay)
    _expire_job_cleanup(job_id)


@app.post("/convert")
async def convert(background_tasks: BackgroundTasks, url: str = Form(...), format: str = Form("mp3")):
    if format not in ("mp3", "mp4"):
        raise HTTPException(status_code=400, detail="format must be 'mp3' or 'mp4'")

    tmpdir = tempfile.mkdtemp(prefix="ytmp3_")
    out_template = os.path.join(tmpdir, "%(title)s.%(ext)s")

    if format == "mp3":
        cmd = [
            "yt-dlp",
            "-o",
            out_template,
            "--extract-audio",
            "--audio-format",
            "mp3",
            url,
        ]
    else:
        cmd = ["yt-dlp", "-o", out_template, url]

    try:
        subprocess.check_call(cmd, cwd=tmpdir)
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="yt-dlp failed to download/convert")

    # find output file
    files = [f for f in os.listdir(tmpdir) if not f.startswith('.')]
    if not files:
        raise HTTPException(status_code=500, detail="no output file found")

    # pick first file
    filepath = os.path.join(tmpdir, files[0])

    # Return file response and schedule cleanup of temp dir
    filename = os.path.basename(filepath)
    background_tasks.add_task(_cleanup_path, tmpdir)
    return FileResponse(filepath, media_type="application/octet-stream", filename=filename)


@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})


# Simple async job management (in-memory). For production use persistent store.
JOBS: Dict[str, Dict[str, Any]] = {}


def _run_job(job_id: str, cmd, tmpdir: str):
    job = _get_job(job_id)
    if not job:
        return
    try:
        proc = subprocess.Popen(cmd, cwd=tmpdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        job['pid'] = proc.pid
        _set_job(job_id, job)
        out, err = proc.communicate()
        # find output file
        files = [f for f in os.listdir(tmpdir) if not f.startswith('.')]
        if files:
            job['filename'] = files[0]
            job['status'] = 'completed'
            job['error'] = None
        else:
            job['status'] = 'failed'
            job['error'] = err.decode(errors='ignore') if err else 'no output'
        _set_job(job_id, job)
    except Exception as e:
        job['status'] = 'failed'
        job['error'] = str(e)
        _set_job(job_id, job)


@app.post("/convert_async")
async def convert_async(url: str = Form(...), format: str = Form("mp4")):
    if format not in ("mp3", "mp4"):
        raise HTTPException(status_code=400, detail="format must be 'mp3' or 'mp4'")

    tmpdir = tempfile.mkdtemp(prefix="ytmp3_job_")
    out_template = os.path.join(tmpdir, "%(title)s.%(ext)s")

    if format == "mp3":
        cmd = [
            "yt-dlp",
            "-o",
            out_template,
            "--extract-audio",
            "--audio-format",
            "mp3",
            url,
        ]
    else:
        cmd = ["yt-dlp", "-o", out_template, url]

    job_id = str(uuid.uuid4())
    job = {"status": "processing", "tmpdir": tmpdir, "filename": None, "pid": None, "error": None}
    _set_job(job_id, job)

    thread = threading.Thread(target=_run_job, args=(job_id, cmd, tmpdir), daemon=True)
    thread.start()
    # schedule expiry cleanup after JOB_TTL_SECONDS
    try:
        timer = threading.Timer(JOB_TTL_SECONDS, _expire_job_cleanup, args=(job_id,))
        timer.daemon = True
        timer.start()
    except Exception:
        pass

    return JSONResponse({"job_id": job_id})


@app.get("/status/{job_id}")
async def job_status(job_id: str):
    job = _get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return JSONResponse({"job_id": job_id, "status": job['status'], "filename": job.get('filename'), "error": job.get('error')})


@app.get("/download/{job_id}")
async def download_job(job_id: str, background_tasks: BackgroundTasks):
    job = _get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    if job['status'] != 'completed' or not job.get('filename'):
        raise HTTPException(status_code=400, detail="job not ready")
    filepath = os.path.join(job['tmpdir'], job['filename'])
    # schedule cleanup shortly after download is served
    background_tasks.add_task(_cleanup_and_delete_job, job_id, 30)
    return FileResponse(filepath, media_type="application/octet-stream", filename=job['filename'])
