@echo off
REM Script to build and push Docker image to Docker Hub

REM Configuration - REPLACE WITH YOUR DOCKER HUB USERNAME
REM Example: set DOCKER_USERNAME=myusername
set DOCKER_USERNAME=your-dockerhub-username
set IMAGE_NAME=yt-downloader
set VERSION=latest

echo Building Docker image...
docker build -f deployment\Dockerfile.production -t %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION% ..

echo Tagging image...
docker tag %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION% %DOCKER_USERNAME%/%IMAGE_NAME%:latest

echo Logging in to Docker Hub...
docker login

echo Pushing to Docker Hub...
docker push %DOCKER_USERNAME%/%IMAGE_NAME%:%VERSION%
docker push %DOCKER_USERNAME%/%IMAGE_NAME%:latest

echo Done! Image available at: https://hub.docker.com/r/%DOCKER_USERNAME%/%IMAGE_NAME%

