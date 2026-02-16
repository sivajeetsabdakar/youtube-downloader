# Railway Environment Variables

## Required Environment Variables

Railway automatically sets some variables, but you may want to configure these:

### Automatically Set by Railway:
- ✅ `PORT` - Railway sets this automatically (usually 5000 or dynamic)
- ✅ `RAILWAY_ENVIRONMENT` - Set by Railway

### Optional but Recommended:

1. **FLASK_ENV** (Recommended)
   - **Value**: `production`
   - **Purpose**: Disables debug mode for production
   - **Set in Railway**: Yes, set to `production`

### Not Needed:
- ❌ `FLASK_APP` - Not required (defaults to app.py)
- ❌ `TMPDIR` - Set in Dockerfile
- ❌ `PYTHONUNBUFFERED` - Set in Dockerfile

## How to Set Environment Variables in Railway

1. Go to your Railway project dashboard
2. Click on your service
3. Go to the **Variables** tab
4. Click **+ New Variable**
5. Add:
   - **Name**: `FLASK_ENV`
   - **Value**: `production`
6. Click **Add**

## Summary

**Minimum Setup**: No environment variables needed! Railway will work out of the box.

**Recommended Setup**: Add one variable:
- `FLASK_ENV=production`

That's it! The app will work with just that.

## Notes

- **Cookies**: If you want to use cookies.txt, you'll need to add it as a file in Railway (not an env var)
- **Port**: Railway handles this automatically
- **Storage**: No persistent storage needed (streaming mode)

