"""Tests for configuration module."""

import pytest
from pathlib import Path
from yt_transcribe import config


def test_get_config_dir():
    """Test getting config directory path."""
    config_dir = config.get_config_dir()
    assert isinstance(config_dir, Path)
    assert ".yt-transcribe" in str(config_dir)


def test_ensure_config_dir(temp_config_dir):
    """Test creating config directory structure."""
    config.ensure_config_dir()
    
    assert config.CONFIG_DIR.exists()
    assert config.MODELS_DIR.exists()
    assert config.TEMPLATES_DIR.exists()


def test_get_default_config():
    """Test default configuration structure."""
    default = config.get_default_config()
    
    assert "ollama" in default
    assert "smtp" in default
    assert "transcription" in default
    assert "playlists" in default
    
    assert default["ollama"]["url"] == "http://localhost:11434"
    assert default["smtp"]["port"] == 587
    assert isinstance(default["playlists"], list)


def test_save_and_load_config(temp_config_dir):
    """Test saving and loading configuration."""
    test_config = config.get_default_config()
    test_config["test_key"] = "test_value"
    
    config.save_config(test_config)
    
    assert config.CONFIG_FILE.exists()
    
    loaded = config.load_config()
    assert loaded["test_key"] == "test_value"
    assert loaded["ollama"]["url"] == "http://localhost:11434"


def test_update_smtp_config(temp_config_dir):
    """Test updating SMTP configuration."""
    config.update_smtp_config(
        server="smtp.example.com",
        port=587,
        username="user@example.com",
        password="secret",
        from_address="from@example.com",
        to_address="to@example.com",
    )
    
    loaded = config.load_config()
    smtp = loaded["smtp"]
    
    assert smtp["server"] == "smtp.example.com"
    assert smtp["port"] == 587
    assert smtp["username"] == "user@example.com"
    assert smtp["password"] == "secret"


def test_add_playlist(temp_config_dir):
    """Test adding a playlist configuration."""
    config.add_playlist(
        playlist_id="PLtest123",
        name="Test Playlist",
        prompt_template="guitar",
    )
    
    playlists = config.get_playlists()
    
    assert len(playlists) == 1
    assert playlists[0]["id"] == "PLtest123"
    assert playlists[0]["name"] == "Test Playlist"
    assert playlists[0]["prompt_template"] == "guitar"


def test_add_playlist_updates_existing(temp_config_dir):
    """Test that adding a playlist with same ID updates it."""
    config.add_playlist("PLtest123", "Original Name", "guitar")
    config.add_playlist("PLtest123", "Updated Name", "coding")
    
    playlists = config.get_playlists()
    
    assert len(playlists) == 1
    assert playlists[0]["name"] == "Updated Name"
    assert playlists[0]["prompt_template"] == "coding"


def test_get_playlists(temp_config_dir):
    """Test getting all playlists."""
    config.add_playlist("PL1", "Playlist 1", "guitar")
    config.add_playlist("PL2", "Playlist 2", "coding")
    
    playlists = config.get_playlists()
    
    assert len(playlists) == 2
    assert playlists[0]["id"] == "PL1"
    assert playlists[1]["id"] == "PL2"


def test_get_playlist_by_id(temp_config_dir):
    """Test getting a specific playlist by ID."""
    config.add_playlist("PLtest123", "Test Playlist", "guitar")
    
    playlist = config.get_playlist_by_id("PLtest123")
    
    assert playlist is not None
    assert playlist["id"] == "PLtest123"
    assert playlist["name"] == "Test Playlist"


def test_get_playlist_by_id_not_found(temp_config_dir):
    """Test getting a non-existent playlist returns None."""
    playlist = config.get_playlist_by_id("PLnonexistent")
    assert playlist is None


def test_get_smtp_config(temp_config_dir):
    """Test getting SMTP configuration."""
    config.update_smtp_config(
        server="smtp.example.com",
        port=587,
        username="user@example.com",
        password="secret",
        from_address="from@example.com",
        to_address="to@example.com",
    )
    
    smtp = config.get_smtp_config()
    
    assert smtp is not None
    assert smtp["server"] == "smtp.example.com"


def test_get_smtp_config_not_configured(temp_config_dir):
    """Test getting SMTP config when not configured returns None."""
    smtp = config.get_smtp_config()
    assert smtp is None
