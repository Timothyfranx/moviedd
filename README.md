# Merlin: High-Speed Series & Anime Downloader 🚀

An advanced, interactive command-line tool for downloading TV Series and Anime, meticulously optimized for high-performance internet connections like **Starlink**.

## 🌟 Key Features

- **Turbo Download Mode**: Pre-configured with a large connection pool (100+) and optimized concurrency (default 10+ threads) to maximize your bandwidth.
- **TV Series (FZSeries)**: Full season downloads with automatic metadata gathering and organization.
- **Anime (AllAnime)**: Quality selection ranging from 360p to 1080p with automatic segment merging via FFmpeg.
- **Smart Retries**: Robust error handling with exponential backoff to bypass server-side rate limiting.
- **Elegant UI**: Real-time progress bars for both individual episodes and overall season progress using `rich`.

## 🛠️ Setup Instructions (Linux Mint / Ubuntu)

### 1. System Prerequisites
Ensure you have Python 3.10+ and FFmpeg installed on your system:
```bash
sudo apt update
sudo apt install python3-venv ffmpeg -y
```

### 2. Installation
Clone the repository and set up the local environment:
```bash
git clone https://github.com/Timothyfranx/moviedd.git
cd moviedd
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🚀 Usage

### TV Series Downloader
```bash
python3 main.py
```
*Tip: When prompted for parallel downloads, use **10-20** for high-speed connections.*

### Anime Downloader
```bash
python3 anime_dl.py
```

## 🔧 Optimization Notes

If you are on a **200Mbps+ connection (Starlink)** and still experiencing slow speeds:
1. Increase **Parallel Downloads** to 30+.
2. Ensure you are downloading to an **SSD** rather than an HDD or USB drive.
3. If server-side throttling is suspected, installing `aria2` can further improve segment-based speeds.

## 🤝 Credits
- **fzseries-api**: Core metadata and link extraction for TV series.
- **anipy-api**: Anime stream provider and downloader.
- **Rich**: Beautiful CLI progress reporting.

---
**Disclaimer**: This project is for educational and personal use only. Users are responsible for complying with the terms of service of the content providers.
