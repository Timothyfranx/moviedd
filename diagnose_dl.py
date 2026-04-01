import os
# Set a working domain for the API before importing fzseries_api
os.environ["FZSERIES_DEFAULT_SITE"] = "https://fztvseries.live/"

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import fzseries_api.hunter
fzseries_api.hunter.session.verify = False

from fzseries_api import Search, TVSeriesMetadata, EpisodeMetadata

def diagnose():
    print("Searching for 'Kyle XY'...")
    search = Search(query='Kyle XY')
    if not search.results.series:
        print("Series not found.")
        return
        
    selected_show = search.results.series[0]
    print(f"Found: {selected_show.title}")
    
    tv_metadata = TVSeriesMetadata(selected_show).results
    target_season = next((s for s in tv_metadata.seasons if s.number == 1), tv_metadata.seasons[0])
    
    print(f"Fetching episodes for {target_season.identity}...")
    episode_results = EpisodeMetadata(target_season).results
    episodes = episode_results.episodes

    if not episodes:
        print("No episodes found.")
        return
        
    ep = episodes[0]
    print(f"Episode: {ep.title}")
    
    # Check download links
    print("\nChecking download links...")
    # ep.files is a list of File objects
    for i, file in enumerate(ep.files):
        print(f"File {i+1}:")
        print(f"  Identity: {file.identity}")
        print(f"  URL: {file.url}")

    # Attempt to download the first episode
    from fzseries_api import Download
    print(f"\nAttempting to download: {ep.title}")
    save_path = "test_dl"
    os.makedirs(save_path, exist_ok=True)
    
    try:
        dl_manager = Download(ep)
        # Try the second link (index 1) which might be on a faster server
        dl_manager.final_download_link_index = 1
        print(f"Fetching final download link (alternate)...")
        final_url = dl_manager.last_url
        print(f"Final URL: {final_url}")
        
        # Download the file with a larger chunk size
        Download.save(
            link=final_url,
            filename=f"{ep.title}_alt.mp4",
            dir=save_path,
            progress_bar=True,
            chunk_size=2048, # 2MB chunks
            timeout=60
        )
        print(f"\nDownload successful! Check the '{save_path}' folder.")
    except Exception as e:
        print(f"\nDownload failed: {e}")

if __name__ == "__main__":
    diagnose()
