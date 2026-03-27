# FZSeries Interactive Downloader

An interactive command-line interface for downloading TV series from `fztvseries.live` using the `fzseries-api` library.

## Features
- Search for any TV series by name.
- Choose from multiple search results.
- List all available seasons for a selected show.
- Download a specific season or start from any season/episode.
- Real-time download progress bar.
- Automatic directory management (organized by Show/Season).

## Prerequisites
- Python 3.10 or higher.

## Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd merlin
```

### 2. Create a Virtual Environment
It is highly recommended to use a virtual environment to avoid dependency conflicts.

**On Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**On Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage

Simply run the `main.py` script:
```bash
python main.py
```

### Steps:
1. **Enter the TV Series Name**: Type the name of the show you want to find.
2. **Select the Show**: If multiple shows match your query, pick the correct one by entering its number.
3. **Select a Season**: The script will list all available seasons. Enter the number of the season you want to download.
4. **Set Download Folder**: Enter the path where you want to save the files (default is `./downloads`).
5. **Wait for Download**: The script will automatically fetch and download all episodes in that season with a visible progress bar.

## Project Structure
- `main.py`: The main entry point for the interactive downloader.
- `requirements.txt`: List of necessary Python packages.
- `test_interactive.py`: A script to test the search and selection logic without downloading massive files.

## Credits
This project uses the [fzseries-api](https://github.com/Simatwa/fzseries-api) developed by Smartwa.

---
**Disclaimer**: This tool is for educational purposes only. Please respect the copyright of the content owners.
