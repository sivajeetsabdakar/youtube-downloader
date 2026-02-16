@echo off
REM Build script for Docker deployment (Windows)

echo Building YouTube Downloader Docker image...
docker build -f deployment\Dockerfile -t yt-downloader:latest ..

echo Build complete!
echo To run: docker-compose -f deployment\docker-compose.yml up -d

