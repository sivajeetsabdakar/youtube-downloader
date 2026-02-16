#!/bin/bash
# Script to build and push Docker image to Docker Hub

# Configuration
DOCKER_USERNAME="your-dockerhub-username"  # Replace with your Docker Hub username
IMAGE_NAME="yt-downloader"
VERSION="latest"

echo "Building Docker image..."
docker build -f deployment/Dockerfile.production -t ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION} .

echo "Tagging image..."
docker tag ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION} ${DOCKER_USERNAME}/${IMAGE_NAME}:latest

echo "Logging in to Docker Hub..."
docker login

echo "Pushing to Docker Hub..."
docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}
docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:latest

echo "Done! Image available at: https://hub.docker.com/r/${DOCKER_USERNAME}/${IMAGE_NAME}"

