# Merlin Series & Anime Downloader

An interactive command-line interface for downloading TV series and Anime.

## Features
- **TV Series**: Download from FZSeries with automatic organization.
- **Anime**: Download from AllAnime with quality selection (360p to 1080p).
- **Quality Control**: Choose lower resolutions for Anime to save space.
- **Parallel Downloads**: Faster downloads with configurable concurrency.
- **Real-time Progress**: Detailed progress bars for overall and individual tasks.

## Prerequisites
- Python 3.10 or higher.
- **FFmpeg**: Required for Anime downloading (merging segments).
  - The Anime script is configured to look for `ffmpeg.exe` and `ffprobe.exe` in a `bin/` folder in the project root.

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd merlin
```

### 2. Create a Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. FFmpeg Setup (For Anime)
If you want to download Anime, you need FFmpeg binaries in the `bin/` folder:
1. Create a `bin` folder.
2. Download FFmpeg essentials from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
3. Place `ffmpeg.exe` and `ffprobe.exe` inside the `bin/` folder.

## Usage

### TV Series (FZSeries)
```bash
python main.py
```

### Anime (AllAnime)
```bash
python anime_dl.py
```

## Credits
- [fzseries-api](https://github.com/Simatwa/fzseries-api)
- [anipy-api](https://github.com/sdaqo/anipy-api)

---
**Disclaimer**: This tool is for educational purposes only. Please respect the copyright of the content owners.
