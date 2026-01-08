"""
Video downloader using yt-dlp.

Handles downloading audio from YouTube videos with proper error handling
and metadata extraction.

TypeScript Context:
- yt-dlp is like youtube-dl but faster (similar to using a well-maintained npm package)
- subprocess is like child_process.exec() in Node.js
- Error handling similar to try-catch with custom error types
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class VideoInfo:
    """
    Video metadata information.

    TypeScript Equivalent:
        interface VideoInfo {
            id: string;
            title: string;
            channel: string;
            duration: number;
            url: string;
        }

    Python Note:
        @dataclass auto-generates __init__, __repr__, etc.
        Similar to TypeScript classes with public fields
    """

    id: str
    title: str
    channel: str
    duration: int  # seconds
    url: str
    description: Optional[str] = None


class DownloadError(Exception):
    """Raised when video download fails."""

    pass


def get_playlist_videos(playlist_url: str) -> List[VideoInfo]:
    """
    Get list of videos in a playlist without downloading.

    Args:
        playlist_url: YouTube playlist URL or ID

    Returns:
        List[VideoInfo]: List of video metadata

    Raises:
        DownloadError: If unable to fetch playlist info

    TypeScript Context:
        Similar to calling an API:
        const getPlaylistVideos = async (url: string): Promise<VideoInfo[]> => {
            const response = await ytdl.getInfo(url)
            return response.entries.map(parseVideoInfo)
        }
    """
    # Convert playlist ID to URL if needed
    if not playlist_url.startswith("http"):
        playlist_url = f"https://www.youtube.com/playlist?list={playlist_url}"

    try:
        # Use yt-dlp to get playlist info
        result = subprocess.run(
            [
                "yt-dlp",
                "--flat-playlist",  # Don't download, just get info
                "--dump-json",  # Output JSON
                playlist_url,
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=60,
        )

        # Parse JSON output (one JSON object per line)
        videos = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue

            data = json.loads(line)
            videos.append(
                VideoInfo(
                    id=data["id"],
                    title=data.get("title", "Unknown"),
                    channel=data.get("channel", "Unknown"),
                    duration=data.get("duration", 0),
                    url=f"https://www.youtube.com/watch?v={data['id']}",
                    description=data.get("description"),
                )
            )

        return videos

    except subprocess.CalledProcessError as e:
        raise DownloadError(f"Failed to fetch playlist info: {e.stderr}")
    except subprocess.TimeoutExpired:
        raise DownloadError("Playlist fetch timed out")
    except (json.JSONDecodeError, KeyError) as e:
        raise DownloadError(f"Failed to parse playlist info: {e}")


def get_video_info(video_url: str) -> VideoInfo:
    """
    Get metadata for a single video.

    Args:
        video_url: YouTube video URL or ID

    Returns:
        VideoInfo: Video metadata

    Raises:
        DownloadError: If unable to fetch video info
    """
    # Convert video ID to URL if needed
    if not video_url.startswith("http"):
        video_url = f"https://www.youtube.com/watch?v={video_url}"

    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--dump-json",
                "--no-playlist",  # Only get single video
                video_url,
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )

        data = json.loads(result.stdout)

        return VideoInfo(
            id=data["id"],
            title=data.get("title", "Unknown"),
            channel=data.get("channel", "Unknown"),
            duration=data.get("duration", 0),
            url=f"https://www.youtube.com/watch?v={data['id']}",
            description=data.get("description"),
        )

    except subprocess.CalledProcessError as e:
        raise DownloadError(f"Failed to fetch video info: {e.stderr}")
    except subprocess.TimeoutExpired:
        raise DownloadError("Video info fetch timed out")
    except (json.JSONDecodeError, KeyError) as e:
        raise DownloadError(f"Failed to parse video info: {e}")


def download_audio(video_url: str, output_dir: Path) -> Path:
    """
    Download audio from a YouTube video.

    Args:
        video_url: YouTube video URL or ID
        output_dir: Directory to save audio file

    Returns:
        Path: Path to downloaded audio file

    Raises:
        DownloadError: If download fails

    TypeScript Context:
        Similar to:
        const downloadAudio = async (url: string, dir: string): Promise<string> => {
            await ytdl(url, {
                format: 'bestaudio',
                output: path.join(dir, '%(id)s.%(ext)s')
            })
            return audioPath
        }
    """
    # Convert video ID to URL if needed
    if not video_url.startswith("http"):
        video_url = f"https://www.youtube.com/watch?v={video_url}"

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Output template: video_id.ext
    output_template = str(output_dir / "%(id)s.%(ext)s")

    try:
        # Download audio only, best quality
        subprocess.run(
            [
                "yt-dlp",
                "--extract-audio",  # Extract audio only
                "--audio-format",
                "wav",  # Convert to WAV for transcription
                "--audio-quality",
                "0",  # Best quality
                "--output",
                output_template,
                "--no-playlist",  # Single video only
                video_url,
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes max
        )

        # Get video ID to find the downloaded file
        info = get_video_info(video_url)
        audio_file = output_dir / f"{info.id}.wav"

        if not audio_file.exists():
            raise DownloadError(f"Downloaded file not found: {audio_file}")

        return audio_file

    except subprocess.CalledProcessError as e:
        raise DownloadError(f"Failed to download audio: {e.stderr}")
    except subprocess.TimeoutExpired:
        raise DownloadError("Audio download timed out")


def verify_ytdlp_installed() -> bool:
    """
    Verify that yt-dlp is installed and accessible.

    Returns:
        bool: True if yt-dlp is available, False otherwise

    TypeScript Context:
        Like checking if a binary exists:
        const verifyInstalled = (): boolean => {
            try {
                execSync('yt-dlp --version')
                return true
            } catch {
                return false
            }
        }
    """
    try:
        subprocess.run(
            ["yt-dlp", "--version"],
            capture_output=True,
            check=True,
            timeout=5,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False
