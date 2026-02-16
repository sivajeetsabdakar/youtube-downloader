from flask import Flask, render_template, request, jsonify, send_file, Response, stream_with_context
import yt_dlp
from yt_dlp import utils as yt_dlp_utils
import os
import json
from pathlib import Path
import threading
import time
import sys
import io
import tempfile
import shutil
from contextlib import redirect_stderr

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create downloads directory if it doesn't exist
DOWNLOADS_DIR = Path('downloads')
DOWNLOADS_DIR.mkdir(exist_ok=True)

# Store download progress
download_status = {}

def get_video_info(url):
    """Extract video information without downloading"""
    cookies_file = Path('cookies.txt')
    has_cookies = cookies_file.exists()
    
    # According to yt-dlp README: when cookies are present, yt-dlp automatically uses
    # tv_downgraded,web,web_safari for free accounts or tv_downgraded,web_creator,web for premium
    # So we should let yt-dlp use defaults when cookies are present
    # Note: android_vr doesn't support cookies, so we try it as fallback
    if has_cookies:
        # With cookies, try cookie-supported clients first
        client_configs = [
            {},  # Default - yt-dlp will auto-select based on account type
            {'player_client': ['tv_downgraded', 'web', 'web_safari']},  # Free account fallback
            {'player_client': ['tv_downgraded', 'web_creator', 'web']},  # Premium account fallback
            {'player_client': ['web']},
            # Fallback: try android_vr without cookies if cookie clients fail
            {'player_client': ['android_vr'], 'no_cookies': True},
        ]
    else:
        # Without cookies, try different clients
        client_configs = [
            {'player_client': ['android_vr']},  # Works without JS runtime
            {'player_client': ['android_vr', 'web', 'web_safari']},
            {'player_client': ['web']},
            {'player_client': ['mweb', 'web']},
            {},  # No extractor args
        ]
    
    errors = []
    
    for config in client_configs:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.youtube.com/',
            'extractor_retries': 3,
        }
        
        if config:
            # Handle special case: android_vr without cookies
            if isinstance(config, dict) and config.get('no_cookies'):
                # Don't use cookies for this config
                player_client = config['player_client']
                ydl_opts['extractor_args'] = {'youtube': {'player_client': player_client}}
            else:
                ydl_opts['extractor_args'] = {'youtube': config}
        
        # Only use cookies if not explicitly disabled for this config
        if has_cookies and (not isinstance(config, dict) or not config.get('no_cookies')):
            ydl_opts['cookiefile'] = str(cookies_file)
        
        # Try to extract info - handle format errors gracefully
        try:
            stderr_buffer = io.StringIO()
            with redirect_stderr(stderr_buffer):
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
            
            # Successfully extracted info
            formats = info.get('formats', [])
            return {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', ''),
                'formats': len(formats),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
            }
        except yt_dlp_utils.DownloadError as e:
            error_msg = str(e)
            # Check if it's a format error - if so, try to get basic info anyway
            if 'format is not available' in error_msg or 'Requested format' in error_msg:
                # Format errors don't prevent us from getting basic metadata
                # Try with extract_flat or ignore format validation
                try:
                    # Use extract_flat to bypass format validation
                    flat_opts = ydl_opts.copy()
                    flat_opts['extract_flat'] = True
                    stderr_buffer = io.StringIO()
                    with redirect_stderr(stderr_buffer):
                        with yt_dlp.YoutubeDL(flat_opts) as ydl:
                            basic_info = ydl.extract_info(url, download=False)
                    
                    # Got basic info despite format error
                    return {
                        'title': basic_info.get('title', 'Unknown'),
                        'duration': basic_info.get('duration', 0),
                        'thumbnail': basic_info.get('thumbnail', ''),
                        'formats': 0,  # Can't get format count with extract_flat
                        'uploader': basic_info.get('uploader', 'Unknown'),
                        'view_count': basic_info.get('view_count', 0),
                    }
                except Exception:
                    # Even extract_flat failed, continue to next config
                    errors.append(error_msg)
                    continue
            else:
                # Not a format error, add to errors and continue
                errors.append(error_msg)
                continue
        except Exception as e:
            error_msg = str(e)
            errors.append(error_msg)
            # Continue to next config
            continue
    
    # All configs failed - provide helpful error message
    error_summary = 'Failed to access video. '
    
    # Check for specific error types
    has_bot_error = any('bot' in e.lower() or 'Sign in' in e for e in errors)
    has_unavailable = any('not available' in e.lower() or 'unavailable' in e.lower() for e in errors)
    has_private = any('private' in e.lower() or 'unlisted' in e.lower() for e in errors)
    
    if has_bot_error:
        error_summary += 'YouTube is blocking automated requests. '
    elif has_unavailable:
        error_summary += 'Video may be unavailable or restricted. '
    elif has_private:
        error_summary += 'Video may be private or unlisted. '
    
    if not has_cookies:
        error_summary += 'COOKIES REQUIRED: Please export cookies from your browser (use extension like "Get cookies.txt LOCALLY") and save as cookies.txt in the project directory. This is essential for accessing YouTube videos.'
    else:
        error_summary += 'Cookies are present but access is still blocked. The video may be region-restricted, age-restricted, or YouTube may be rate-limiting. Try: 1) Refreshing cookies, 2) Waiting a few minutes, 3) Checking if the video is accessible in your browser.'
    
    # Include first error for debugging (but keep it concise)
    if errors:
        first_error = errors[0][:100]  # First 100 chars
        if len(errors[0]) > 100:
            first_error += '...'
        error_summary += f' Error: {first_error}'
    
    return {'error': error_summary}

def download_video(url, format_type='best', quality='best'):
    """Download video with progress tracking"""
    video_id = url.split('watch?v=')[-1].split('&')[0] if 'watch?v=' in url else 'video'
    status_key = f"{video_id}_{int(time.time())}"
    
    download_status[status_key] = {
        'status': 'downloading',
        'progress': 0,
        'filename': '',
        'error': None
    }
    
    def progress_hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                progress = (downloaded / total) * 100
                download_status[status_key]['progress'] = round(progress, 2)
        elif d['status'] == 'finished':
            download_status[status_key]['progress'] = 100
            download_status[status_key]['status'] = 'completed'
            download_status[status_key]['filename'] = d.get('filename', '')
    
    # Check for cookies file
    cookies_file = Path('cookies.txt')
    has_cookies = cookies_file.exists()
    
    # Use the same flow that worked successfully earlier:
    # android_vr client without cookies + 'best' format
    # This works reliably without requiring JavaScript runtime or ffmpeg
    if has_cookies:
        # Try android_vr first (proven to work), then cookie clients as fallback
        client_configs = [
            {'player_client': ['android_vr'], 'no_cookies': True},  # This worked!
            {},  # Default - yt-dlp will auto-select based on account type
            {'player_client': ['tv_downgraded', 'web', 'web_safari']},  # Free account fallback
            {'player_client': ['tv_downgraded', 'web_creator', 'web']},  # Premium account fallback
            {'player_client': ['web']},
        ]
    else:
        # Without cookies, android_vr works best
        client_configs = [
            {'player_client': ['android_vr']},  # This worked! Works without JS runtime
            {'player_client': ['android_vr', 'web', 'web_safari']},
            {'player_client': ['web']},
            {'player_client': ['mweb', 'web']},
            {},  # No extractor args
        ]
    
    # Set format based on user selection - use same flow as successful download
    # Use 'best' format (single file, no merging needed, no ffmpeg required)
    format_configs = []
    if format_type == 'video':
        if quality == 'best':
            # Use 'best' format - this worked perfectly (selected format 18)
            format_configs = ['best']
        elif quality == '720p':
            # Try quality-specific single format, fallback to best
            format_configs = ['best[height<=720]', 'best']
        elif quality == '480p':
            format_configs = ['best[height<=480]', 'best']
        elif quality == '360p':
            format_configs = ['best[height<=360]', 'best']
    elif format_type == 'audio':
        format_configs = ['bestaudio/best', 'best']
    
    errors = []
    
    for config in client_configs:
        for format_str in format_configs:
            ydl_opts = {
                'outtmpl': str(DOWNLOADS_DIR / '%(title)s.%(ext)s'),
                'progress_hooks': [progress_hook],
                'quiet': False,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'referer': 'https://www.youtube.com/',
                'format': format_str,
            }
            
            if format_type == 'audio':
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            
            if config:
                # Handle special case: android_vr without cookies
                if isinstance(config, dict) and config.get('no_cookies'):
                    # Don't use cookies for this config
                    player_client = config['player_client']
                    ydl_opts['extractor_args'] = {'youtube': {'player_client': player_client}}
                else:
                    ydl_opts['extractor_args'] = {'youtube': config}
            
            # Only use cookies if not explicitly disabled for this config
            if has_cookies and (not isinstance(config, dict) or not config.get('no_cookies')):
                ydl_opts['cookiefile'] = str(cookies_file)
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                download_status[status_key]['status'] = 'completed'
                return status_key
            except yt_dlp_utils.DownloadError as e:
                error_msg = str(e)
                errors.append(error_msg)
                # Check if it's an ffmpeg merging error - fallback to single format
                if 'ffmpeg' in error_msg.lower() and 'merging' in error_msg.lower():
                    # Try with single format that doesn't require merging
                    try:
                        ydl_opts['format'] = 'best'
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            ydl.download([url])
                        download_status[status_key]['status'] = 'completed'
                        return status_key
                    except:
                        pass
                # Check if it's because only images/storyboards are available
                if 'Only images are available' in error_msg or 'storyboard' in error_msg.lower():
                    # Try with a more permissive format selector
                    try:
                        ydl_opts['format'] = 'best[ext=mp4]/best[height<=360]/best'
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            ydl.download([url])
                        download_status[status_key]['status'] = 'completed'
                        return status_key
                    except:
                        pass
                # If format error, try next format
                if 'format is not available' in error_msg or 'Requested format' in error_msg:
                    continue
                # Otherwise, try next config
                break
            except Exception as e:
                error_msg = str(e)
                errors.append(error_msg)
                # If format error, try next format
                if 'format is not available' in error_msg or 'Requested format' in error_msg:
                    continue
                # Otherwise, try next config
                break
    
    # All configs failed - provide helpful error message
    download_status[status_key]['status'] = 'error'
    error_summary = 'Failed to download video. '
    if any('bot' in e.lower() or 'Sign in' in e for e in errors):
        error_summary += 'YouTube is blocking automated requests. '
    if not has_cookies:
        error_summary += 'COOKIES REQUIRED: Please export cookies from your browser (use extension like "Get cookies.txt LOCALLY") and save as cookies.txt in the project directory. This is essential for accessing YouTube videos.'
    else:
        error_summary += 'Even with cookies, YouTube may be blocking access. Try updating yt-dlp: pip install -U yt-dlp'
    
    download_status[status_key]['error'] = error_summary
    return status_key

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/info', methods=['POST'])
def get_info():
    data = request.json
    url = data.get('url', '')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    info = get_video_info(url)
    return jsonify(info)

@app.route('/api/download', methods=['POST'])
def download():
    """Stream download directly to user - no server storage"""
    data = request.json
    url = data.get('url', '')
    format_type = data.get('format', 'best')
    quality = data.get('quality', 'best')
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    # Create temporary directory for this download
    temp_dir = tempfile.mkdtemp()
    temp_file = None
    
    try:
        cookies_file = Path('cookies.txt')
        has_cookies = cookies_file.exists()
        
        # Use the same flow that worked successfully
        if has_cookies:
            client_configs = [
                {'player_client': ['android_vr'], 'no_cookies': True},
                {},  # Default
                {'player_client': ['tv_downgraded', 'web', 'web_safari']},
                {'player_client': ['tv_downgraded', 'web_creator', 'web']},
                {'player_client': ['web']},
            ]
        else:
            client_configs = [
                {'player_client': ['android_vr']},
                {'player_client': ['android_vr', 'web', 'web_safari']},
                {'player_client': ['web']},
                {'player_client': ['mweb', 'web']},
                {},
            ]
        
        # Set format
        format_configs = []
        if format_type == 'video':
            if quality == 'best':
                format_configs = ['best']
            elif quality == '720p':
                format_configs = ['best[height<=720]', 'best']
            elif quality == '480p':
                format_configs = ['best[height<=480]', 'best']
            elif quality == '360p':
                format_configs = ['best[height<=360]', 'best']
        elif format_type == 'audio':
            format_configs = ['bestaudio/best', 'best']
        
        # Try to download
        for config in client_configs:
            for format_str in format_configs:
                ydl_opts = {
                    'outtmpl': str(Path(temp_dir) / '%(title)s.%(ext)s'),
                    'quiet': False,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'referer': 'https://www.youtube.com/',
                    'format': format_str,
                }
                
                if format_type == 'audio':
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                
                if config:
                    if isinstance(config, dict) and config.get('no_cookies'):
                        player_client = config['player_client']
                        ydl_opts['extractor_args'] = {'youtube': {'player_client': player_client}}
                    else:
                        ydl_opts['extractor_args'] = {'youtube': config}
                
                if has_cookies and (not isinstance(config, dict) or not config.get('no_cookies')):
                    ydl_opts['cookiefile'] = str(cookies_file)
                
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                    
                    # Find the downloaded file
                    downloaded_files = list(Path(temp_dir).glob('*'))
                    if downloaded_files:
                        temp_file = downloaded_files[0]
                        filename = temp_file.name
                        
                        # Stream the file to user
                        def generate():
                            try:
                                with open(temp_file, 'rb') as f:
                                    while True:
                                        chunk = f.read(8192)  # 8KB chunks
                                        if not chunk:
                                            break
                                        yield chunk
                            finally:
                                # Clean up temporary file and directory
                                try:
                                    if temp_file and temp_file.exists():
                                        temp_file.unlink()
                                    if os.path.exists(temp_dir):
                                        shutil.rmtree(temp_dir)
                                except:
                                    pass
                        
                        # Determine content type
                        ext = temp_file.suffix.lower()
                        content_type = 'video/mp4' if ext == '.mp4' else 'audio/mpeg' if ext == '.mp3' else 'application/octet-stream'
                        
                        return Response(
                            stream_with_context(generate()),
                            mimetype=content_type,
                            headers={
                                'Content-Disposition': f'attachment; filename="{filename}"',
                                'Content-Length': str(temp_file.stat().st_size)
                            }
                        )
                except Exception as e:
                    error_msg = str(e)
                    if 'format is not available' in error_msg or 'Requested format' in error_msg:
                        continue
                    if 'ffmpeg' in error_msg.lower() and 'merging' in error_msg.lower():
                        try:
                            ydl_opts['format'] = 'best'
                            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                                ydl.download([url])
                            downloaded_files = list(Path(temp_dir).glob('*'))
                            if downloaded_files:
                                temp_file = downloaded_files[0]
                                filename = temp_file.name
                                def generate():
                                    try:
                                        with open(temp_file, 'rb') as f:
                                            while True:
                                                chunk = f.read(8192)
                                                if not chunk:
                                                    break
                                                yield chunk
                                    finally:
                                        try:
                                            if temp_file and temp_file.exists():
                                                temp_file.unlink()
                                            if os.path.exists(temp_dir):
                                                shutil.rmtree(temp_dir)
                                        except:
                                            pass
                                ext = temp_file.suffix.lower()
                                content_type = 'video/mp4' if ext == '.mp4' else 'audio/mpeg' if ext == '.mp3' else 'application/octet-stream'
                                return Response(
                                    stream_with_context(generate()),
                                    mimetype=content_type,
                                    headers={
                                        'Content-Disposition': f'attachment; filename="{filename}"',
                                        'Content-Length': str(temp_file.stat().st_size)
                                    }
                                )
                        except:
                            pass
                    break
        
        # Cleanup on error
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except:
            pass
        
        return jsonify({'error': 'Failed to download video. Please try again.'}), 500
        
    except Exception as e:
        # Cleanup on exception
        try:
            if temp_file and temp_file.exists():
                temp_file.unlink()
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except:
            pass
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/api/status/<status_key>')
def get_status(status_key):
    if status_key in download_status:
        return jsonify(download_status[status_key])
    return jsonify({'error': 'Status not found'}), 404

@app.route('/api/downloads')
def list_downloads():
    """List all downloaded files (for local use only - not used in streaming mode)"""
    files = []
    for file_path in DOWNLOADS_DIR.glob('*'):
        if file_path.is_file():
            files.append({
                'name': file_path.name,
                'size': file_path.stat().st_size,
                'path': str(file_path)
            })
    return jsonify({'files': files})

@app.route('/api/download-file/<filename>')
def download_file(filename):
    """Serve downloaded file (for local use only - not used in streaming mode)"""
    file_path = DOWNLOADS_DIR / filename
    if file_path.exists():
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    # Disable debug mode in production (Docker)
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    # Use PORT environment variable if set (for cloud hosting)
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)

