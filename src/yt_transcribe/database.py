"""
Database module for state management.

This module uses SQLite to track which videos have been processed,
preventing duplicate work and enabling resumption after interruption.

TypeScript Context:
- Similar to using better-sqlite3 or TypeORM in Node.js
- SQLite is like a local JSON file but with ACID guarantees
- Context manager (with statement) similar to try-finally in TS
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from . import config


def get_db_path() -> Path:
    """
    Get the database file path.

    Returns:
        Path: Path to the SQLite database file
    """
    return config.DATABASE_FILE


@contextmanager
def get_connection():
    """
    Context manager for database connections.

    Yields:
        sqlite3.Connection: Database connection

    TypeScript Context:
        Similar to:
        const withConnection = async (callback) => {
            const conn = await db.connect()
            try {
                return await callback(conn)
            } finally {
                await conn.close()
            }
        }

    Python's context manager automatically handles cleanup:
        with get_connection() as conn:
            # use conn
        # conn is automatically closed here
    """
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    """
    Initialize the database schema.

    Creates tables if they don't exist:
    - processed_videos: Tracks which videos have been transcribed

    This is idempotent - safe to call multiple times.

    TypeScript Context:
        Like running database migrations:
        await db.schema.createTableIfNotExists('processed_videos', ...)
    """
    config.ensure_config_dir()

    with get_connection() as conn:
        cursor = conn.cursor()

        # Create processed_videos table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS processed_videos (
                video_id TEXT PRIMARY KEY,
                playlist_id TEXT NOT NULL,
                title TEXT,
                channel TEXT,
                duration_seconds INTEGER,
                transcription TEXT,
                summary TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'completed'
            )
        """
        )

        # Create index for faster playlist queries
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_playlist_id 
            ON processed_videos(playlist_id)
        """
        )

        conn.commit()


def is_video_processed(video_id: str) -> bool:
    """
    Check if a video has already been processed.

    Args:
        video_id: YouTube video ID

    Returns:
        bool: True if video has been processed, False otherwise

    TypeScript Equivalent:
        const isVideoProcessed = async (videoId: string): Promise<boolean> => {
            const result = await db.query(
                'SELECT 1 FROM processed_videos WHERE video_id = ?',
                [videoId]
            )
            return result.length > 0
        }
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM processed_videos WHERE video_id = ? LIMIT 1", (video_id,))
        return cursor.fetchone() is not None


def mark_video_processed(
    video_id: str,
    playlist_id: str,
    title: Optional[str] = None,
    channel: Optional[str] = None,
    duration_seconds: Optional[int] = None,
    transcription: Optional[str] = None,
    summary: Optional[str] = None,
    status: str = "completed",
) -> None:
    """
    Mark a video as processed and store its data.

    Args:
        video_id: YouTube video ID
        playlist_id: YouTube playlist ID
        title: Video title
        channel: Channel name
        duration_seconds: Video duration in seconds
        transcription: Full transcription text
        summary: Generated summary
        status: Processing status (completed, failed, etc.)

    TypeScript Context:
        Similar to an INSERT OR REPLACE operation:
        await db.processedVideos.upsert({
            videoId, playlistId, title, ...
        })
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO processed_videos 
            (video_id, playlist_id, title, channel, duration_seconds, 
             transcription, summary, processed_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                video_id,
                playlist_id,
                title,
                channel,
                duration_seconds,
                transcription,
                summary,
                datetime.now().isoformat(),
                status,
            ),
        )
        conn.commit()


def get_processed_video(video_id: str) -> Optional[Dict[str, Any]]:
    """
    Get processed video data from the database.

    Args:
        video_id: YouTube video ID

    Returns:
        Optional[Dict[str, Any]]: Video data or None if not found

    TypeScript Equivalent:
        const getProcessedVideo = async (
            videoId: string
        ): Promise<ProcessedVideo | null> => {
            return await db.processedVideos.findOne({ videoId })
        }
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM processed_videos WHERE video_id = ?", (video_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def get_playlist_videos(playlist_id: str) -> List[Dict[str, Any]]:
    """
    Get all processed videos for a specific playlist.

    Args:
        playlist_id: YouTube playlist ID

    Returns:
        List[Dict[str, Any]]: List of processed video records

    TypeScript Equivalent:
        const getPlaylistVideos = async (
            playlistId: string
        ): Promise<ProcessedVideo[]> => {
            return await db.processedVideos.find({ playlistId })
        }
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM processed_videos WHERE playlist_id = ? ORDER BY processed_at DESC",
            (playlist_id,),
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_all_processed_videos() -> List[Dict[str, Any]]:
    """
    Get all processed videos across all playlists.

    Returns:
        List[Dict[str, Any]]: List of all processed video records
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM processed_videos ORDER BY processed_at DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def delete_video_record(video_id: str) -> bool:
    """
    Delete a video record from the database.

    Useful for reprocessing a video or cleaning up failed attempts.

    Args:
        video_id: YouTube video ID

    Returns:
        bool: True if a record was deleted, False otherwise
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM processed_videos WHERE video_id = ?", (video_id,))
        conn.commit()
        return cursor.rowcount > 0
