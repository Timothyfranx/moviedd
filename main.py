import os
import requests
import time
from pathlib import Path

# Set a working domain for the API before importing fzseries_api
os.environ["FZSERIES_DEFAULT_SITE"] = "https://fztvseries.live/"

# Try to force a better User-Agent for requests
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import fzseries_api.hunter
fzseries_api.hunter.session.verify = False

from fzseries_api import Search, TVSeriesMetadata, EpisodeMetadata, Download, Auto

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

    season_str = input(f"\nEnter season number to download (1-{len(seasons)}, default 1): ").strip()
    season = int(season_str) if season_str.isdigit() else 1
    
    # Validate season
    if not any(s.number == season for s in seasons):
        print(f"Season {season} not found. Defaulting to Season 1.")
        season = 1

    save_path = input(f"Enter download folder (default './downloads'): ").strip() or "downloads"
    os.makedirs(save_path, exist_ok=True)

    print(f"\nInitializing download for: {selected_show.title} - Season {season}")
    print(f"Files will be saved to: {os.path.abspath(save_path)}")

    try:
        # Get the specific season object
        target_season = next((s for s in seasons if s.number == season), seasons[0])
        
        print(f"Fetching episodes for {target_season.identity}...")
        episode_results = EpisodeMetadata(target_season).results
        episodes = episode_results.episodes

        if not episodes:
            print(f"No episodes found for Season {season}.")
            return

        print(f"Found {len(episodes)} episodes. Starting download...\n")

        for i, episode in enumerate(episodes):
            print(f"[{i + 1}/{len(episodes)}] {episode.title}")
            try:
                # Direct download control
                dl_manager = Download(episode)
                final_url = dl_manager.last_url
                Download.save(
                    link=final_url,
                    filename=f"{episode.title}.mp4",
                    dir=save_path,
                    progress_bar=True,
                    timeout=60
                )
                # Small delay to avoid anti-bot detection
                time.sleep(3)
            except Exception as e:
                print(f"  Error downloading episode: {e}")
                continue

        print("\n=== Download Task Completed ===")

    except KeyboardInterrupt:
        print("\nDownload cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    interactive_downloader()
