# YouTube Downloader

A modern, web-based YouTube video and audio downloader built with Flask and yt-dlp. Download videos in multiple quality options or extract audio as MP3 with a beautiful, user-friendly interface.

## Live Demo

**Try it now:** [https://yt-downloader-production-ce78.up.railway.app/](https://yt-downloader-production-ce78.up.railway.app/)

## Features

- **Video Downloads** - Download videos in multiple quality options (Best, 720p, 480p, 360p)
- **Audio Extraction** - Extract audio as MP3 files
- **Streaming Downloads** - Files stream directly to your browser (no server storage)
- **Modern UI** - Beautiful, responsive interface with smooth animations
- **Mobile Friendly** - Works seamlessly on all devices
- **Privacy First** - No files stored on server, direct streaming to user
- **Fast & Reliable** - Optimized for performance with multiple fallback strategies

## How It Works

### Architecture Overview

The application uses a **client-server architecture** with streaming capabilities:

1. **Frontend (HTML/CSS/JavaScript)**
   - User enters YouTube URL
   - Displays video information (thumbnail, title, duration, views)
   - Handles download requests and progress display
   - Receives streamed files directly from server

2. **Backend (Flask + yt-dlp)**
   - Extracts video metadata using `yt-dlp`
   - Downloads video/audio to temporary storage
   - Streams file directly to user's browser
   - Automatically cleans up temporary files after streaming

3. **Download Process**
   ```
   User Request → Flask API → yt-dlp → Temporary File → Stream to Browser → Auto Cleanup
   ```

### Technical Details

- **Video Extraction**: Uses `yt-dlp` library with multiple client configurations (`android_vr`, `web`, `ios`) to bypass YouTube restrictions
- **Streaming**: Files are downloaded to temporary directories and streamed using Flask's `Response` with `stream_with_context`
- **Format Selection**: Automatically selects best available format, with fallbacks for compatibility
- **Error Handling**: Multiple fallback strategies for different YouTube client types and format availability
- **No Storage**: Files are deleted immediately after streaming, ensuring no server-side storage

### Key Technologies

- **Backend**: Flask (Python web framework)
- **Video Processing**: yt-dlp (YouTube downloader)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Containerization**: Docker with Gunicorn for production
- **Deployment**: Railway.app (containerized hosting)

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- (Optional) Docker for containerized deployment

### Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sivajeetsabdakar/youtube-downloader.git
   cd youtube-downloader
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser and navigate to: `http://localhost:5000`

### Docker Installation

1. **Build the Docker image**
   ```bash
   docker build -f deployment/Dockerfile.production -t yt-downloader .
   ```

2. **Run the container**
   ```bash
   docker run -d -p 5000:5000 --name yt-downloader yt-downloader
   ```

3. **Access the application**
   - Open your browser and navigate to: `http://localhost:5000`

### Docker Compose (Recommended for Local Development)

1. **Start the application**
   ```bash
   cd deployment
   docker-compose up -d
   ```

2. **Stop the application**
   ```bash
   docker-compose down
   ```

## Usage

1. **Get Video Information**
   - Paste a YouTube URL in the input field
   - Click "Get Info" to view video details (thumbnail, title, channel, duration, views)

2. **Download Video**
   - Select "Video" format
   - Choose quality (Best, 720p, 480p, or 360p)
   - Click "Download"
   - The file will download directly to your browser

3. **Download Audio**
   - Select "Audio (MP3)" format
   - Click "Download"
   - The MP3 file will download directly to your browser

## Requirements

- Python 3.10+
- Flask 3.0.0
- yt-dlp >= 2024.3.10
- Gunicorn 21.2.0 (for production)
- FFmpeg (included in Docker image, optional for local use)

## Configuration

### Optional: YouTube Cookies

For better access to restricted or age-restricted videos, you can add a `cookies.txt` file:

1. Export cookies from your browser using extensions like "Get cookies.txt LOCALLY"
2. Save the file as `cookies.txt` in the project root
3. The application will automatically use cookies if present

**Note**: Cookies are optional. The application works without them but may have limited access to some videos.

## Docker Hub

The application is available on Docker Hub:

```bash
docker pull sivajeetsabdakar/yt-downloader:latest
docker run -d -p 5000:5000 sivajeetsabdakar/yt-downloader:latest
```

**Docker Hub Repository**: [sivajeetsabdakar/yt-downloader](https://hub.docker.com/r/sivajeetsabdakar/yt-downloader)

## Project Structure

```
youtube-downloader/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Frontend HTML
├── static/
│   ├── style.css         # Stylesheet
│   ├── script.js         # Frontend JavaScript
│   ├── logo.png          # Application logo
│   └── favicon.png       # Browser favicon
├── deployment/
│   ├── Dockerfile        # Development Dockerfile
│   ├── Dockerfile.production  # Production Dockerfile
│   └── docker-compose.yml     # Docker Compose configuration
└── README.md             # This file
```

## Privacy & Security

- **No Data Storage**: Files are streamed directly to users and deleted immediately
- **No Tracking**: No analytics or user tracking implemented
- **Open Source**: Full source code available for review
- **Temporary Files**: All temporary files are automatically cleaned up

## Legal Notice

This tool is for educational purposes. Users are responsible for ensuring they have the right to download content from YouTube. Respect copyright laws and YouTube's Terms of Service.

## Author

**Made by Shiva**

- **GitHub**: [sivajeetsabdakar](https://github.com/sivajeetsabdakar/youtube-downloader)
- **LinkedIn**: [Sivajeet Sabdakar](https://www.linkedin.com/in/sivajeet-sabdakar-5a03aa278/)

## License

This project is open source and available for educational purposes.

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/sivajeetsabdakar/youtube-downloader/issues).

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloader library
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Railway](https://railway.app/) - Hosting platform

---

If you find this project useful, please consider giving it a star on GitHub!
