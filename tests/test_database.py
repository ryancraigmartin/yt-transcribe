"""Tests for database module."""

import pytest
from yt_transcribe import database


def test_init_db(temp_config_dir):
    """Test database initialization."""
    database.init_db()
    
    assert database.get_db_path().exists()
    
    # Verify tables exist
    with database.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='processed_videos'"
        )
        assert cursor.fetchone() is not None


def test_is_video_processed_false(temp_config_dir):
    """Test checking if video is processed when it's not."""
    database.init_db()
    
    assert database.is_video_processed("video123") is False


def test_mark_video_processed(temp_config_dir):
    """Test marking a video as processed."""
    database.init_db()
    
    database.mark_video_processed(
        video_id="video123",
        playlist_id="PLtest",
        title="Test Video",
        channel="Test Channel",
        duration_seconds=300,
        transcription="Test transcription",
        summary="Test summary",
        status="completed",
    )
    
    assert database.is_video_processed("video123") is True


def test_get_processed_video(temp_config_dir):
    """Test retrieving processed video data."""
    database.init_db()
    
    database.mark_video_processed(
        video_id="video123",
        playlist_id="PLtest",
        title="Test Video",
        channel="Test Channel",
        duration_seconds=300,
        transcription="Test transcription",
        summary="Test summary",
    )
    
    video = database.get_processed_video("video123")
    
    assert video is not None
    assert video["video_id"] == "video123"
    assert video["title"] == "Test Video"
    assert video["channel"] == "Test Channel"
    assert video["transcription"] == "Test transcription"


def test_get_processed_video_not_found(temp_config_dir):
    """Test getting a non-existent video returns None."""
    database.init_db()
    
    video = database.get_processed_video("nonexistent")
    assert video is None


def test_get_playlist_videos(temp_config_dir):
    """Test getting all videos from a playlist."""
    database.init_db()
    
    database.mark_video_processed(
        video_id="video1",
        playlist_id="PLtest",
        title="Video 1",
    )
    database.mark_video_processed(
        video_id="video2",
        playlist_id="PLtest",
        title="Video 2",
    )
    database.mark_video_processed(
        video_id="video3",
        playlist_id="PLother",
        title="Video 3",
    )
    
    playlist_videos = database.get_playlist_videos("PLtest")
    
    assert len(playlist_videos) == 2
    assert playlist_videos[0]["video_id"] in ["video1", "video2"]


def test_get_all_processed_videos(temp_config_dir):
    """Test getting all processed videos."""
    database.init_db()
    
    database.mark_video_processed(video_id="video1", playlist_id="PL1")
    database.mark_video_processed(video_id="video2", playlist_id="PL2")
    
    all_videos = database.get_all_processed_videos()
    
    assert len(all_videos) == 2


def test_delete_video_record(temp_config_dir):
    """Test deleting a video record."""
    database.init_db()
    
    database.mark_video_processed(video_id="video123", playlist_id="PLtest")
    
    assert database.is_video_processed("video123") is True
    
    deleted = database.delete_video_record("video123")
    
    assert deleted is True
    assert database.is_video_processed("video123") is False


def test_delete_video_record_not_found(temp_config_dir):
    """Test deleting a non-existent video returns False."""
    database.init_db()
    
    deleted = database.delete_video_record("nonexistent")
    assert deleted is False


def test_mark_video_processed_updates_existing(temp_config_dir):
    """Test that marking a video as processed updates existing record."""
    database.init_db()
    
    database.mark_video_processed(
        video_id="video123",
        playlist_id="PLtest",
        title="Original Title",
        summary="Original Summary",
    )
    
    database.mark_video_processed(
        video_id="video123",
        playlist_id="PLtest",
        title="Updated Title",
        summary="Updated Summary",
    )
    
    video = database.get_processed_video("video123")
    
    assert video["title"] == "Updated Title"
    assert video["summary"] == "Updated Summary"
    
    # Should only have one record
    all_videos = database.get_all_processed_videos()
    assert len(all_videos) == 1
