# Free Hosting Deployment Guide

This guide covers deploying the YouTube Downloader to free hosting services.

## Best Free Hosting Options

### 1. **Railway.app** (Recommended - Easiest)
- ✅ Free tier: $5 credit/month (usually enough for small apps)
- ✅ Direct Docker support
- ✅ Automatic HTTPS
- ✅ Easy GitHub integration
- ✅ Simple setup

### 2. **Render.com**
- ✅ Free tier available
- ✅ Docker support
- ✅ Automatic HTTPS
- ✅ Good for web services
- ⚠️ Free tier spins down after inactivity

### 3. **Fly.io**
- ✅ Free tier: 3 shared VMs
- ✅ Great Docker support
- ✅ Global edge network
- ✅ Good performance

### 4. **Google Cloud Run**
- ✅ Free tier: 2 million requests/month
- ✅ Pay-per-use pricing
- ✅ Serverless containers
- ⚠️ Requires credit card (but free tier is generous)

## Deployment Steps

### Option 1: Railway.app (Recommended)

1. **Sign up**: Go to https://railway.app and sign up with GitHub

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your repository

3. **Configure Deployment**:
   - Railway will auto-detect the Dockerfile
   - Set root directory to: `deployment` (or move Dockerfile to root)
   - Or use the Dockerfile in the deployment folder

4. **Environment Variables** (if needed):
   - `FLASK_ENV=production`
   - `PORT=5000` (Railway sets this automatically)

5. **Deploy**: Railway will build and deploy automatically

6. **Get URL**: Railway provides a free `.railway.app` domain

### Option 2: Render.com

1. **Sign up**: Go to https://render.com

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

3. **Configure**:
   - **Name**: yt-downloader
   - **Environment**: Docker
   - **Dockerfile Path**: `deployment/Dockerfile`
   - **Root Directory**: (leave empty or set to project root)
   - **Build Command**: (auto-detected)
   - **Start Command**: (auto-detected from Dockerfile)

4. **Environment Variables**:
   - `FLASK_ENV=production`
   - `PORT=5000` (Render sets this automatically)

5. **Deploy**: Click "Create Web Service"

6. **Get URL**: Render provides a free `.onrender.com` domain

### Option 3: Fly.io

1. **Install Fly CLI**:
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. **Sign up**: Go to https://fly.io and sign up

3. **Login**:
   ```bash
   fly auth login
   ```

4. **Create fly.toml** (see deployment/fly.toml)

5. **Deploy**:
   ```bash
   fly deploy
   ```

## Important Modifications Needed

### 1. Update Dockerfile for Production

The current Dockerfile uses Flask's development server. For production, you should use a production WSGI server like Gunicorn.

### 2. Port Configuration

Most hosting services set the PORT environment variable. Update app.py to use it:

```python
port = int(os.environ.get('PORT', 5000))
app.run(debug=debug_mode, host='0.0.0.0', port=port)
```

### 3. Storage Considerations

- Downloads are stored in the container filesystem
- They will be lost when the container restarts
- For persistent storage, consider:
  - Using cloud storage (S3, Google Cloud Storage)
  - Mounting volumes (if supported by host)
  - Using a database for metadata

## Quick Setup Checklist

- [ ] Choose hosting service
- [ ] Create account
- [ ] Connect GitHub repository
- [ ] Configure Dockerfile path
- [ ] Set environment variables
- [ ] Deploy
- [ ] Test the application
- [ ] (Optional) Set up custom domain

## Notes

- **Free tiers have limitations**: CPU, memory, bandwidth
- **Sleep/Spin-down**: Some services spin down inactive apps (Render)
- **Storage**: Container storage is ephemeral - downloads may be lost
- **HTTPS**: All services provide automatic HTTPS
- **Scaling**: Free tiers usually have limits on concurrent requests

