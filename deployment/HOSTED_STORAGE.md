# Download Storage in Hosted Environments

## Current Behavior

Right now, the app:
1. Downloads videos to `downloads/` directory on the server
2. Stores them permanently
3. Lists them in the "Downloaded Files" section
4. Serves them when users click "Download"

## Problems on Hosted Services

### 1. **Ephemeral Storage**
- Container filesystems are **temporary**
- Files are **lost when container restarts**
- Downloads directory gets wiped

### 2. **Storage Limits**
- **Railway**: ~1GB free storage
- **Render**: ~512MB free storage  
- **Fly.io**: ~3GB free storage
- Videos can be 50-500MB each
- **Storage fills up quickly**

### 3. **Costs**
- Exceeding free tier = charges
- Large files = higher bandwidth costs

### 4. **Multiple Users**
- Each user's download takes space
- Concurrent downloads = storage exhaustion

## Solutions

### ✅ Solution 1: Stream Downloads Directly (BEST for Free Hosting)

**How it works:**
- Download video and immediately stream to user's browser
- No server storage needed
- File deleted after streaming completes

**Implementation:**
- Modify download endpoint to stream instead of save
- User gets file directly in browser
- No "Downloaded Files" list (not needed)

**Pros:**
- ✅ No storage limits
- ✅ Works on all free tiers
- ✅ No cleanup needed
- ✅ Lower costs

**Cons:**
- ❌ User must wait for download
- ❌ No file history

### Solution 2: Temporary Storage with Auto-Cleanup

**How it works:**
- Store files temporarily (e.g., 1 hour)
- Auto-delete old files
- Limit total storage usage

**Implementation:**
- Add cleanup job to delete files older than X hours
- Limit downloads directory size
- Clean up on startup

**Pros:**
- ✅ File list available
- ✅ Multiple downloads possible
- ✅ Controlled storage

**Cons:**
- ❌ Files expire
- ❌ Still limited by storage quota

### Solution 3: Cloud Storage (S3, Google Cloud, etc.)

**How it works:**
- Upload downloads to cloud storage
- Serve via signed URLs
- Persistent and scalable

**Pros:**
- ✅ Persistent storage
- ✅ Scalable
- ✅ Professional

**Cons:**
- ❌ Requires cloud account
- ❌ Additional setup
- ❌ May have costs

## Recommendation for Free Hosting

**Use Solution 1: Stream Downloads Directly**

This is the best approach because:
1. No storage concerns
2. Works within free tier limits
3. Simple to implement
4. Users get files immediately

The current "Downloaded Files" list won't be needed - users download directly.

## What Needs to Change

1. **Remove file storage** - Stream directly to user
2. **Update download endpoint** - Return file stream instead of saving
3. **Remove downloads list** - Not needed with streaming
4. **Optional: Add cleanup** - If you want to keep some storage option

Would you like me to implement the streaming solution?

