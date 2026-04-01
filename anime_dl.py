import asyncio
import os
import re
import sys
from pathlib import Path

# Add local bin to PATH for ffmpeg
bin_path = str(Path(__file__).parent / "bin")
if bin_path not in os.environ["PATH"]:
    os.environ["PATH"] = bin_path + os.path.pathsep + os.environ["PATH"]
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
)
from anipy_api.provider import get_provider, LanguageTypeEnum
from anipy_api.download import Downloader

console = Console()

async def download_episode(video, save_path, progress, task_id, episode_title):
    """Download a single episode using anipy-api Downloader."""
    try:
        # Sanitize filename
        clean_title = re.sub(r'[<>:"/\\|?*]', '_', episode_title)
        # anipy-api download() expects path WITHOUT suffix
        file_path = Path(save_path) / clean_title
        
        # Callback to update rich progress
        def progress_cb(percentage):
            progress.update(task_id, completed=percentage, visible=True)

        # Downloader needs callbacks for info and progress
        dl = Downloader(
            progress_callback=progress_cb,
            info_callback=lambda msg, exc=None: None,
            soft_error_callback=lambda msg, exc=None: None
        )
        
        # anipy-api download is synchronous/blocking requests-based
        await asyncio.to_thread(dl.download, video, file_path, container=".mp4", ffmpeg=True)
        
        progress.update(task_id, description=f"[green]✓ {episode_title}")
        return True
    except Exception as e:
        progress.update(task_id, description=f"[red]✗ Error: {episode_title}")
        return False

async def main():
    console.print("[bold magenta]=== Anime Downloader (anipy-api) ===[/bold magenta]\n")
    
    query = Prompt.ask("Enter anime name")
    
    provider = get_provider("allanime")
    if not provider:
        console.print("[red]Could not load allanime provider.[/red]")
        return
    
    console.print(f"[yellow]Searching for '{query}' on allanime...")
    search_results = await asyncio.to_thread(provider.get_search, query)
    
    if not search_results:
        console.print("[red]No results found.")
        return

    # Selection
    for i, res in enumerate(search_results[:10]):
        langs = ", ".join([str(l) for l in res.languages])
        console.print(f"[[bold cyan]{i+1}[/bold cyan]] {res.name} ({langs})")
    
    choice = Prompt.ask("\nSelect a number", default="1")
    idx = int(choice) - 1 if choice.isdigit() and 0 < int(choice) <= len(search_results) else 0
    selected_anime = search_results[idx]
    
    # Pick language
    lang = LanguageTypeEnum.SUB
    if LanguageTypeEnum.DUB in selected_anime.languages:
        if Prompt.ask("Dub available. Use Dub?", choices=["y", "n"], default="n") == "y":
            lang = LanguageTypeEnum.DUB
            
    console.print(f"\n[yellow]Fetching episodes for '{selected_anime.name}' [{lang}]...")
    episodes = await asyncio.to_thread(provider.get_episodes, selected_anime.identifier, lang)
    
    if not episodes:
        console.print("[red]No episodes found.")
        return

    console.print(f"[green]Found {len(episodes)} episodes.")
    
    # Range selection
    range_str = Prompt.ask(
        f"Enter episode range (e.g. '1-12', '5', or 'all')", 
        default="all"
    )
    
    selected_episodes = []
    if range_str.lower() == 'all':
        selected_episodes = episodes
    elif '-' in range_str:
        try:
            start_str, end_str = range_str.split('-')
            start = int(start_str)
            end = int(end_str)
            selected_episodes = episodes[start-1:end]
        except ValueError:
            selected_episodes = episodes
    elif range_str.isdigit():
        num = int(range_str)
        if 0 < num <= len(episodes):
            selected_episodes = [episodes[num-1]]
        else:
            selected_episodes = episodes
    
    save_path = Prompt.ask("Download folder", default="./downloads")
    anime_folder = os.path.join(save_path, re.sub(r'[<>:"/\\|?*]', '_', selected_anime.name))
    os.makedirs(anime_folder, exist_ok=True)
    
    max_workers = int(Prompt.ask("Parallel downloads", default="3"))
    
    progress = Progress(
        TextColumn("[bold blue]{task.description}", justify="right"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        DownloadColumn(),
        "•",
        TransferSpeedColumn(),
        "•",
        TimeRemainingColumn(),
    )
    
    console.print(f"\n[bold green]Starting download of {len(selected_episodes)} episodes...[/bold green]")
    
    with progress:
        overall_task = progress.add_task(f"[yellow]Overall Progress", total=len(selected_episodes))
        semaphore = asyncio.Semaphore(max_workers)
        
        async def limited_download(ep_num, idx):
            async with semaphore:
                task_id = progress.add_task(f"Ep {ep_num}", visible=False, total=100)
                try:
                    videos = await asyncio.to_thread(provider.get_video, selected_anime.identifier, ep_num, lang)
                    if not videos:
                        progress.update(overall_task, advance=1)
                        return
                    
                    selected_video = videos[0]
                    
                    success = await download_episode(
                        selected_video, 
                        anime_folder, 
                        progress, 
                        task_id, 
                        f"{selected_anime.name} - Ep {ep_num}"
                    )
                    
                    if success:
                        progress.update(task_id, visible=False)
                    
                    progress.update(overall_task, advance=1)
                except Exception as e:
                    progress.update(overall_task, advance=1)

        tasks = [limited_download(ep, i) for i, ep in enumerate(selected_episodes)]
        await asyncio.gather(*tasks)

    console.print("\n[bold green]=== All tasks completed ===[/bold green]")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[red]Cancelled by user.[/red]")
    except Exception as e:
        console.print(f"\n[bold red]Fatal error: {e}[/bold red]")
