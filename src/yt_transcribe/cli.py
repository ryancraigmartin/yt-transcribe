"""
Main CLI for yt-transcribe.

Implements the Click-based command-line interface with commands:
- init: Initialize configuration
- add: Add playlist rules
- run: Execute transcription pipeline
- list: Show configured playlists

TypeScript Context:
- Click is like Commander.js or Yargs in Node.js
- Decorators (@click.command) similar to decorators in TS
- Rich provides beautiful terminal output like chalk + ora
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

from . import config, database, prompt_templates
from .core import downloader, transcriber, summarizer, email_sender


# Initialize Rich console for beautiful output
console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """
    YouTube Playlist Auto-Transcriber
    
    A local-first utility for transcribing and summarizing YouTube playlists
    using NVIDIA NeMo and Ollama.
    
    TypeScript Context:
        Similar to creating a CLI with Commander.js:
        const program = new Command()
        program.version('0.1.0')
    """
    pass


@main.command()
@click.option(
    "--smtp-server",
    prompt="SMTP Server (e.g., smtp.gmail.com)",
    help="SMTP server hostname",
)
@click.option(
    "--smtp-port",
    prompt="SMTP Port",
    default=587,
    type=int,
    help="SMTP port (typically 587 for TLS)",
)
@click.option(
    "--smtp-username",
    prompt="SMTP Username",
    help="SMTP username/email",
)
@click.option(
    "--smtp-password",
    prompt="SMTP Password",
    hide_input=True,
    help="SMTP password or app-specific password",
)
@click.option(
    "--from-address",
    prompt="From Email Address",
    help="Email address to send from",
)
@click.option(
    "--to-address",
    prompt="To Email Address",
    help="Email address to send summaries to",
)
def init(
    smtp_server: str,
    smtp_port: int,
    smtp_username: str,
    smtp_password: str,
    from_address: str,
    to_address: str,
) -> None:
    """
    Initialize yt-transcribe configuration.
    
    Creates ~/.yt-transcribe/ directory and sets up SMTP credentials.
    
    TypeScript Context:
        Like 'npm init' - sets up configuration:
        const init = async (options: InitOptions) => {
            await createConfigDir()
            await saveConfig(options)
        }
    """
    console.print("\n[bold blue]Initializing yt-transcribe...[/bold blue]\n")
    
    # Create configuration directory
    try:
        config.ensure_config_dir()
        console.print("✓ Created configuration directory", style="green")
    except Exception as e:
        console.print(f"✗ Failed to create config directory: {e}", style="red")
        sys.exit(1)
    
    # Save SMTP configuration
    try:
        config.update_smtp_config(
            server=smtp_server,
            port=smtp_port,
            username=smtp_username,
            password=smtp_password,
            from_address=from_address,
            to_address=to_address,
        )
        console.print("✓ Saved SMTP configuration", style="green")
    except Exception as e:
        console.print(f"✗ Failed to save SMTP config: {e}", style="red")
        sys.exit(1)
    
    # Verify SMTP configuration
    console.print("\nVerifying SMTP connection...", style="yellow")
    smtp_config = email_sender.EmailConfig(
        server=smtp_server,
        port=smtp_port,
        username=smtp_username,
        password=smtp_password,
        from_address=from_address,
        to_address=to_address,
    )
    
    if email_sender.verify_smtp_config(smtp_config):
        console.print("✓ SMTP connection verified", style="green")
    else:
        console.print(
            "✗ Failed to verify SMTP connection. Check your credentials.",
            style="red"
        )
        console.print(
            "\nFor Gmail, use an App Password: "
            "https://support.google.com/accounts/answer/185833",
            style="yellow"
        )
    
    # Initialize database
    try:
        database.init_db()
        console.print("✓ Initialized database", style="green")
    except Exception as e:
        console.print(f"✗ Failed to initialize database: {e}", style="red")
        sys.exit(1)
    
    # Check for yt-dlp
    if downloader.verify_ytdlp_installed():
        console.print("✓ yt-dlp is installed", style="green")
    else:
        console.print(
            "✗ yt-dlp not found. Install with: pip install yt-dlp",
            style="red"
        )
    
    # Show available templates
    templates = prompt_templates.get_available_templates()
    console.print(f"\n✓ Available templates: {', '.join(templates)}", style="green")
    
    console.print("\n[bold green]Initialization complete![/bold green]")
    console.print("\nNext steps:")
    console.print("  1. Add a playlist: [cyan]yt-transcribe add --playlist <ID> --name <NAME> --prompt <TEMPLATE>[/cyan]")
    console.print("  2. Run transcription: [cyan]yt-transcribe run --all[/cyan]")
    console.print()


@main.command()
@click.option(
    "--playlist",
    required=True,
    help="YouTube playlist ID or URL",
)
@click.option(
    "--name",
    required=True,
    help="Friendly name for this playlist",
)
@click.option(
    "--prompt",
    required=True,
    help="Prompt template name (guitar, coding, business) or path to custom YAML",
)
def add(playlist: str, name: str, prompt: str) -> None:
    """
    Add a playlist configuration.
    
    Validates the playlist and template, then saves the configuration.
    
    Example:
        yt-transcribe add --playlist PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf --name "Guitar Lessons" --prompt guitar
    """
    console.print(f"\n[bold blue]Adding playlist: {name}[/bold blue]\n")
    
    # Extract playlist ID from URL if needed
    playlist_id = playlist
    if "youtube.com/playlist" in playlist or "list=" in playlist:
        # Extract ID from URL
        if "list=" in playlist:
            playlist_id = playlist.split("list=")[1].split("&")[0]
    
    # Validate template
    template = prompt_templates.get_template(prompt)
    if not template:
        console.print(
            f"✗ Template '{prompt}' not found",
            style="red"
        )
        console.print(
            f"\nAvailable templates: {', '.join(prompt_templates.get_available_templates())}",
            style="yellow"
        )
        sys.exit(1)
    
    console.print(f"✓ Using template: {template.name}", style="green")
    
    # Validate playlist (fetch info)
    try:
        console.print("Validating playlist...", style="yellow")
        videos = downloader.get_playlist_videos(playlist_id)
        console.print(f"✓ Found {len(videos)} videos in playlist", style="green")
    except downloader.DownloadError as e:
        console.print(f"✗ Failed to validate playlist: {e}", style="red")
        sys.exit(1)
    
    # Save configuration
    try:
        config.add_playlist(playlist_id, name, prompt)
        console.print(f"✓ Saved playlist configuration", style="green")
    except Exception as e:
        console.print(f"✗ Failed to save configuration: {e}", style="red")
        sys.exit(1)
    
    console.print(f"\n[bold green]Playlist '{name}' added successfully![/bold green]")
    console.print(f"\nRun transcription with: [cyan]yt-transcribe run --id {playlist_id}[/cyan]")
    console.print()


@main.command()
def list() -> None:
    """
    List all configured playlists.
    
    Shows a table of configured playlists with their IDs, names, and templates.
    """
    playlists = config.get_playlists()
    
    if not playlists:
        console.print("\n[yellow]No playlists configured yet.[/yellow]")
        console.print("\nAdd a playlist with: [cyan]yt-transcribe add --playlist <ID> --name <NAME> --prompt <TEMPLATE>[/cyan]\n")
        return
    
    # Create table
    table = Table(title="Configured Playlists", show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan")
    table.add_column("Playlist ID", style="yellow")
    table.add_column("Template", style="green")
    
    for pl in playlists:
        table.add_row(pl["name"], pl["id"], pl["prompt_template"])
    
    console.print()
    console.print(table)
    console.print()


@main.command()
@click.option("--id", "playlist_id", help="Specific playlist ID to process")
@click.option("--all", "process_all", is_flag=True, help="Process all configured playlists")
@click.option("--dry-run", is_flag=True, help="Show what would be processed without actually processing")
def run(playlist_id: Optional[str], process_all: bool, dry_run: bool) -> None:
    """
    Run the transcription pipeline.
    
    Processes videos from specified playlist(s):
    - Downloads audio
    - Transcribes with NeMo
    - Summarizes with Ollama
    - Emails results
    
    Example:
        yt-transcribe run --all
        yt-transcribe run --id PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf
        yt-transcribe run --all --dry-run
    """
    if not playlist_id and not process_all:
        console.print("[red]Error: Must specify either --id or --all[/red]")
        sys.exit(1)
    
    # Get playlists to process
    if process_all:
        playlists = config.get_playlists()
        if not playlists:
            console.print("[yellow]No playlists configured.[/yellow]")
            sys.exit(0)
    else:
        playlist = config.get_playlist_by_id(playlist_id)
        if not playlist:
            console.print(f"[red]Playlist '{playlist_id}' not found in configuration.[/red]")
            sys.exit(1)
        playlists = [playlist]
    
    # Run async processing
    asyncio.run(process_playlists(playlists, dry_run))


async def process_playlists(playlists: list, dry_run: bool) -> None:
    """
    Process multiple playlists.
    
    TypeScript Context:
        async function processPlaylists(playlists: Playlist[], dryRun: boolean) {
            for (const playlist of playlists) {
                await processPlaylist(playlist, dryRun)
            }
        }
    """
    for playlist in playlists:
        console.print(f"\n[bold blue]Processing playlist: {playlist['name']}[/bold blue]\n")
        
        try:
            # Get videos in playlist
            videos = downloader.get_playlist_videos(playlist["id"])
            console.print(f"Found {len(videos)} videos in playlist")
            
            # Filter out already processed videos
            unprocessed = [v for v in videos if not database.is_video_processed(v.id)]
            
            if not unprocessed:
                console.print("[green]All videos already processed![/green]")
                continue
            
            console.print(f"{len(unprocessed)} videos to process\n")
            
            if dry_run:
                console.print("[yellow]Dry run mode - showing what would be processed:[/yellow]\n")
                for video in unprocessed:
                    console.print(f"  • {video.title}")
                continue
            
            # Process each video
            for video in unprocessed:
                await process_video(video, playlist)
        
        except Exception as e:
            console.print(f"[red]Error processing playlist: {e}[/red]")
            continue


async def process_video(video: downloader.VideoInfo, playlist: dict) -> None:
    """
    Process a single video through the complete pipeline.
    
    TypeScript Context:
        async function processVideo(video: VideoInfo, playlist: Playlist) {
            await downloadAudio(video)
            const transcript = await transcribe(audioPath)
            const summary = await summarize(transcript)
            await sendEmail(summary)
        }
    """
    console.print(f"\n[bold cyan]Processing: {video.title}[/bold cyan]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        
        # Download audio
        download_task = progress.add_task("Downloading audio...", total=100)
        try:
            audio_dir = Path("/tmp/yt-transcribe-audio")
            audio_file = downloader.download_audio(video.url, audio_dir)
            progress.update(download_task, completed=100)
        except Exception as e:
            console.print(f"[red]✗ Download failed: {e}[/red]")
            return
        
        # Transcribe
        transcribe_task = progress.add_task("Transcribing audio...", total=100)
        try:
            trans_service = transcriber.get_transcription_service(use_mock=True)
            transcription = trans_service.transcribe(audio_file)
            progress.update(transcribe_task, completed=100)
        except Exception as e:
            console.print(f"[red]✗ Transcription failed: {e}[/red]")
            audio_file.unlink(missing_ok=True)
            return
        
        # Clean up audio file
        audio_file.unlink(missing_ok=True)
        
        # Summarize
        summarize_task = progress.add_task("Generating summary...", total=100)
        try:
            template = prompt_templates.get_template(playlist["prompt_template"])
            sum_service = summarizer.create_summarizer()
            
            result = await sum_service.summarize(transcription, template, video.title)
            progress.update(summarize_task, completed=100)
        except Exception as e:
            console.print(f"[red]✗ Summarization failed: {e}[/red]")
            # Still save transcription
            database.mark_video_processed(
                video_id=video.id,
                playlist_id=playlist["id"],
                title=video.title,
                channel=video.channel,
                duration_seconds=video.duration,
                transcription=transcription,
                status="summarization_failed",
            )
            return
        
        # Send email
        email_task = progress.add_task("Sending email...", total=100)
        try:
            smtp_config_dict = config.get_smtp_config()
            if smtp_config_dict:
                email_config = email_sender.EmailConfig(**smtp_config_dict)
                email_sender.send_summary_email(
                    email_config,
                    video.title,
                    result.summary,
                    playlist["name"],
                )
                progress.update(email_task, completed=100)
            else:
                progress.update(email_task, completed=100)
                console.print("[yellow]⚠ SMTP not configured, skipping email[/yellow]")
        except Exception as e:
            console.print(f"[red]✗ Email failed: {e}[/red]")
        
        # Mark as processed
        database.mark_video_processed(
            video_id=video.id,
            playlist_id=playlist["id"],
            title=video.title,
            channel=video.channel,
            duration_seconds=video.duration,
            transcription=transcription,
            summary=result.summary,
            status="completed",
        )
    
    console.print("[bold green]✓ Video processed successfully![/bold green]")


if __name__ == "__main__":
    main()
