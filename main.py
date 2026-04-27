import os
import requests
import time
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
    SpinnerColumn
)

# Set a working domain for the API before importing fzseries_api
os.environ["FZSERIES_DEFAULT_SITE"] = "https://fztvseries.live/"

# Try to force a better User-Agent for requests
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

# Increase connection pool size for faster concurrent downloads
retry_strategy = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import fzseries_api.hunter
# Sync the API session with our high-speed settings
fzseries_api.hunter.session.mount("http://", adapter)
fzseries_api.hunter.session.mount("https://", adapter)
fzseries_api.hunter.session.verify = False

from fzseries_api import Search, TVSeriesMetadata, EpisodeMetadata, Download, Auto

def download_file(episode, save_path, progress, task_id):
    """Worker function to download an episode with its own progress bar."""
    full_path = None
    try:
        # Get the download URL - Try alternate link (index 1) for potentially better speeds
        dl_manager = Download(episode)
        try:
            dl_manager.final_download_link_index = 1
            url = dl_manager.last_url
        except:
            url = dl_manager.last_url
            
        if not url:
            raise ValueError("Could not retrieve a valid download URL.")
        
        # Sanitize filename for Windows
        clean_title = re.sub(r'[<>:"/\\|?*]', '_', episode.title)
        filename = f"{clean_title}.mp4"
        full_path = Path(save_path) / filename

        # Update description to active status
        progress.update(task_id, description=f"[cyan]Downloading: {episode.title}")

        # Stream the download using the global session
        response = session.get(url, stream=True, verify=False, timeout=60)
        response.raise_for_status()
        
        try:
            total_size = int(response.headers.get('content-length', 0))
        except (ValueError, TypeError):
            total_size = 0
            
        progress.update(task_id, total=total_size, visible=True)

        with open(full_path, "wb") as f:
            # Aggressive 1MB chunks for high-speed streaming
            for chunk in response.iter_content(chunk_size=1024 * 1024): 
                if chunk:
                    f.write(chunk)
                    progress.update(task_id, advance=len(chunk))
        
        progress.update(task_id, description=f"[green]✓ {episode.title}")
        time.sleep(0.5) 
        progress.update(task_id, visible=False)
        return True
    except Exception as e:
        progress.update(task_id, description=f"[red]✗ Error: {episode.title}")
        # Clean up partial file on failure
        try:
            if full_path and full_path.exists():
                full_path.unlink()
        except:
            pass
        time.sleep(2)
        progress.update(task_id, visible=False)
        return False

def interactive_downloader():
    print("=== FZSeries Downloader ===")
    
    query = input("Enter the name of the TV Series: ").strip()
    if not query:
        print("No name entered. Exiting.")
        return

    print(f"Searching for '{query}'...")
    search = Search(query=query)
    results = search.results

    if not results.series:
        print(f"No series found matching '{query}'.")
        return

    # If multiple results, let the user pick
    print("\nResults found:")
    for i, show in enumerate(results.series):
        print(f"[{i + 1}] {show.title}")
    
    choice = input("\nSelect a number (default 1): ").strip()
    index = int(choice) - 1 if choice.isdigit() and 0 < int(choice) <= len(results.series) else 0
    selected_show = results.series[index]

    # Fetch and list seasons
    print(f"\nFetching seasons for '{selected_show.title}'...")
    tv_metadata = TVSeriesMetadata(selected_show).results
    seasons = tv_metadata.seasons
    
    if not seasons:
        print("No seasons found for this show.")
        return

    print(f"\nAvailable Seasons ({len(seasons)} total):")
    for s in seasons:
        print(f"Season {s.number}: {s.identity}")

    season_str = input(f"\nEnter season number to download (1-{len(seasons)}, or type 'all'): ").strip().lower()
    
    selected_seasons = []
    if season_str == 'all':
        selected_seasons = seasons
    else:
        try:
            num = int(season_str) if season_str else 1
            target = next((s for s in seasons if s.number == num), seasons[0])
            selected_seasons = [target]
        except:
            print("Invalid input. Defaulting to Season 1.")
            selected_seasons = [seasons[0]]

    save_path = input(f"Enter download folder (default './downloads'): ").strip() or "downloads"
    # Create a subfolder for the specific series to keep things organized
    clean_series_name = re.sub(r'[<>:"/\\|?*]', '_', selected_show.title)
    save_path = os.path.join(save_path, clean_series_name)
    os.makedirs(save_path, exist_ok=True)

    try:
        # Gather all episodes from selected seasons in parallel
        print(f"\nGathering metadata for '{selected_show.title}'...")
        all_episodes = []
        
        def fetch_season_episodes(s):
            print(f"  Fetching Season {s.number}...")
            return EpisodeMetadata(s).results.episodes

        with ThreadPoolExecutor(max_workers=len(selected_seasons) if selected_seasons else 1) as metadata_executor:
            results = list(metadata_executor.map(fetch_season_episodes, selected_seasons))
            for eps in results:
                all_episodes.extend(eps)

        if not all_episodes:
            print("No episodes found to download.")
            return

        print(f"\nReady to download {len(all_episodes)} episodes.")
        concurrency = input("How many parallel downloads? (default 10): ").strip()
        max_workers = int(concurrency) if concurrency.isdigit() and int(concurrency) > 0 else 10

        # Use Rich Progress for a nice UI
        progress = Progress(
            TextColumn("[bold blue]{task.description}", justify="right"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•",
            DownloadColumn(),
            "•",
            TransferSpeedColumn(),
            "•",
            TimeRemainingColumn(),
        )

        with progress:
            # Master task for overall progress
            overall_task = progress.add_task(f"[bold yellow]Overall Progress (0/{len(all_episodes)})", total=len(all_episodes))
            
            # Function to wrap worker and update overall progress
            def worker_wrapper(episode, idx):
                # Create a task for this specific episode
                task_id = progress.add_task(f"Queued: {episode.title}", visible=False)
                success = download_file(episode, save_path, progress, task_id)
                
                # Update overall task description with current count
                completed = progress.tasks[overall_task].completed + 1
                progress.update(overall_task, advance=1, description=f"[bold yellow]Overall Progress ({completed}/{len(all_episodes)})")
                return success

            # Execute using ThreadPool
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Map episodes to worker wrapper
                list(executor.map(lambda x: worker_wrapper(x[1], x[0]), enumerate(all_episodes)))

        print("\n=== All Download Tasks Completed ===")

    except KeyboardInterrupt:
        print("\nDownload cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    interactive_downloader()
