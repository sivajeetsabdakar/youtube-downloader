# YouTube Downloader

A web application to download videos and audio from YouTube, built with Flask and yt-dlp.

## 🌐 Live Demo

**Try it now:** [https://yt-downloader-production-ce78.up.railway.app/](https://yt-downloader-production-ce78.up.railway.app/)

## Deployment Guide

This directory contains Docker deployment files for the YouTube Downloader web application.

## Quick Start

### Using Docker Compose (Recommended)

1. Build and run:
```bash
docker-compose up -d
```

2. Access the application:
   - Open http://localhost:5000 in your browser

3. Stop the application:
```bash
docker-compose down
```

### Using Docker directly

1. Build the image:
```bash
docker build -f deployment/Dockerfile -t yt-downloader .
```

2. Run the container:
```bash
docker run -d \
  -p 5000:5000 \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/cookies.txt:/app/cookies.txt:ro \
  --name yt-downloader \
  yt-downloader
```

3. Access the application:
   - Open http://localhost:5000 in your browser

## Volumes

- `downloads/`: Directory where downloaded videos are stored
- `cookies.txt`: (Optional) YouTube cookies file for better access

## Environment Variables

- `FLASK_ENV`: Set to `production` for production deployment
- `FLASK_APP`: Set to `app.py` (default)

## Notes

- The application runs on port 5000 by default
- Downloads are persisted in the `downloads/` volume
- Cookies file is mounted as read-only for security
- FFmpeg is included in the image for video processing

