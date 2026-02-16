# Pushing to Docker Hub Guide

## Prerequisites

1. **Docker Hub Account**: Sign up at https://hub.docker.com (free)
2. **Docker installed**: Make sure Docker is running on your machine

## Steps to Push to Docker Hub

### Step 1: Login to Docker Hub

```bash
docker login
```

Enter your Docker Hub username and password when prompted.

### Step 2: Build the Image

```bash
# From the project root directory
docker build -f deployment/Dockerfile.production -t YOUR_DOCKERHUB_USERNAME/yt-downloader:latest .
```

Replace `YOUR_DOCKERHUB_USERNAME` with your actual Docker Hub username.

### Step 3: Push to Docker Hub

```bash
docker push YOUR_DOCKERHUB_USERNAME/yt-downloader:latest
```

### Step 4: Verify

Check your Docker Hub repository at:
```
https://hub.docker.com/r/YOUR_DOCKERHUB_USERNAME/yt-downloader
```

## Using the Scripts

### Windows:
1. Edit `push-to-dockerhub.bat`
2. Replace `your-dockerhub-username` with your Docker Hub username
3. Run: `deployment\push-to-dockerhub.bat`

### Linux/Mac:
1. Edit `push-to-dockerhub.sh`
2. Replace `your-dockerhub-username` with your Docker Hub username
3. Make executable: `chmod +x deployment/push-to-dockerhub.sh`
4. Run: `./deployment/push-to-dockerhub.sh`

## Pulling and Running Your Image

Once pushed, anyone can run your image with:

```bash
docker pull YOUR_DOCKERHUB_USERNAME/yt-downloader:latest
docker run -d -p 5000:5000 YOUR_DOCKERHUB_USERNAME/yt-downloader:latest
```

## Image Tags

- `latest` - Always points to the most recent version
- You can also tag specific versions: `v1.0.0`, `v1.0.1`, etc.

## Making Repository Public/Private

1. Go to https://hub.docker.com
2. Navigate to your repository
3. Click "Settings"
4. Change visibility to "Public" or "Private"

Public repositories are free. Private repositories have limits on the free tier.

