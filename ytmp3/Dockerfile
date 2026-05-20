FROM python:3.11-alpine

ENV PYTHONUNBUFFERED=1

# Use Alpine packages for ffmpeg to avoid large Debian apt installs/mirror issues
RUN apk add --no-cache ffmpeg ca-certificates

WORKDIR /app

# Install Python dependencies (project lives in ./ytmp3 when compose context is repo root)
COPY ytmp3/backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy application code (frontend + backend + extension)
COPY ytmp3 /app

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
