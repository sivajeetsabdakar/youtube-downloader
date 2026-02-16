# Quick Push to Docker Hub

## Step 1: Login to Docker Hub
```bash
docker login
```
Enter your Docker Hub username and password.

## Step 2: Build the Image
```bash
docker build -f deployment/Dockerfile.production -t YOUR_USERNAME/yt-downloader:latest .
```

Replace `YOUR_USERNAME` with your Docker Hub username.

## Step 3: Push to Docker Hub
```bash
docker push YOUR_USERNAME/yt-downloader:latest
```

## Example
If your Docker Hub username is `johndoe`:
```bash
docker build -f deployment/Dockerfile.production -t johndoe/yt-downloader:latest .
docker push johndoe/yt-downloader:latest
```

## After Pushing
Your image will be available at:
`https://hub.docker.com/r/YOUR_USERNAME/yt-downloader`

Others can pull and run it with:
```bash
docker pull YOUR_USERNAME/yt-downloader:latest
docker run -d -p 5000:5000 YOUR_USERNAME/yt-downloader:latest
```

