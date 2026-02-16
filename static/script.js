const urlInput = document.getElementById('urlInput');
const infoBtn = document.getElementById('infoBtn');
const downloadBtn = document.getElementById('downloadBtn');
const videoInfo = document.getElementById('videoInfo');
const errorMessage = document.getElementById('errorMessage');
const downloadProgress = document.getElementById('downloadProgress');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const refreshBtn = document.getElementById('refreshBtn');

let currentStatusKey = null;
let statusCheckInterval = null;

function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

async function getVideoInfo() {
    const url = urlInput.value.trim();
    
    if (!url) {
        showError('Please enter a YouTube URL');
        return;
    }

    if (!url.includes('youtube.com') && !url.includes('youtu.be')) {
        showError('Please enter a valid YouTube URL');
        return;
    }

    infoBtn.disabled = true;
    infoBtn.textContent = 'Loading...';
    hideError();
    videoInfo.classList.add('hidden');

    try {
        const response = await fetch('/api/info', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url }),
        });

        const data = await response.json();

        if (data.error) {
            showError(data.error);
            return;
        }

        // Display video info
        document.getElementById('videoTitle').textContent = data.title;
        document.getElementById('uploader').textContent = data.uploader;
        document.getElementById('duration').textContent = formatDuration(data.duration);
        document.getElementById('views').textContent = data.view_count.toLocaleString();
        document.getElementById('thumbnail').src = data.thumbnail;

        videoInfo.classList.remove('hidden');
    } catch (error) {
        showError('Failed to fetch video information: ' + error.message);
    } finally {
        infoBtn.disabled = false;
        infoBtn.textContent = 'Get Info';
    }
}

async function startDownload() {
    const url = urlInput.value.trim();
    const format = document.querySelector('input[name="format"]:checked').value;
    const quality = document.getElementById('quality').value;

    if (!url) {
        showError('Please enter a YouTube URL');
        return;
    }

    downloadBtn.disabled = true;
    downloadBtn.textContent = 'Preparing download...';
    hideError();
    downloadProgress.classList.remove('hidden');
    progressBar.style.width = '0%';
    progressText.textContent = 'Starting download... This may take a moment.';

    try {
        // Stream download directly to user's browser
        const response = await fetch('/api/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url, format, quality }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Download failed');
        }

        // Get filename from Content-Disposition header
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'video.mp4';
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="(.+)"/);
            if (filenameMatch) {
                filename = filenameMatch[1];
            }
        }

        // Create blob and trigger download
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(downloadUrl);

        // Update UI
        progressBar.style.width = '100%';
        progressText.textContent = 'Download complete!';
        downloadBtn.disabled = false;
        downloadBtn.textContent = 'Download';
        
        // Hide progress after a moment
        setTimeout(() => {
            downloadProgress.classList.add('hidden');
        }, 2000);
        
    } catch (error) {
        showError('Download failed: ' + error.message);
        downloadProgress.classList.add('hidden');
        downloadBtn.disabled = false;
        downloadBtn.textContent = 'Download';
    }
}

// Status checking not needed for streaming downloads
// Keeping function for backward compatibility but it won't be called
function startStatusCheck() {
    // Not used in streaming mode
}

async function loadDownloads() {
    try {
        const response = await fetch('/api/downloads');
        const data = await response.json();
        const filesList = document.getElementById('filesList');

        if (data.files.length === 0) {
            filesList.innerHTML = '<p style="color: #718096; padding: 20px; text-align: center;">No downloads yet</p>';
            return;
        }

        filesList.innerHTML = data.files.map(file => `
            <div class="file-item">
                <span class="file-name">${file.name}</span>
                <span class="file-size">${formatFileSize(file.size)}</span>
                <a href="/api/download-file/${encodeURIComponent(file.name)}" class="file-download">Download</a>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading downloads:', error);
    }
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
}

function hideError() {
    errorMessage.classList.add('hidden');
}

// Event listeners
infoBtn.addEventListener('click', getVideoInfo);
downloadBtn.addEventListener('click', startDownload);
refreshBtn.addEventListener('click', loadDownloads);

urlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        getVideoInfo();
    }
});

// Update quality options based on format selection
document.querySelectorAll('input[name="format"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
        const qualityGroup = document.getElementById('qualityGroup');
        if (e.target.value === 'audio') {
            qualityGroup.style.display = 'none';
        } else {
            qualityGroup.style.display = 'flex';
        }
    });
});

// Note: Downloads list is kept for local use, but streaming mode doesn't store files
// Uncomment the line below if you want to show downloads list (for local development)
// loadDownloads();

