"""
Configuration management for yt-transcribe.

This module handles:
- Creation and management of ~/.yt-transcribe/ directory
- Configuration file storage (config.yaml)
- Model storage location
- Database initialization

TypeScript Context:
- Similar to managing ~/.npm or ~/.config directories
- Uses pathlib.Path instead of path.join() for cleaner path operations
- Type hints help IDE autocomplete (like TypeScript interfaces)
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


# Default configuration directory
# Similar to process.env.HOME in Node.js
CONFIG_DIR = Path.home() / ".yt-transcribe"
CONFIG_FILE = CONFIG_DIR / "config.yaml"
DATABASE_FILE = CONFIG_DIR / "state.db"
MODELS_DIR = CONFIG_DIR / "models"
TEMPLATES_DIR = CONFIG_DIR / "templates"


def get_config_dir() -> Path:
    """
    Get the configuration directory path.

    Returns:
        Path: The configuration directory (e.g., ~/.yt-transcribe)

    TypeScript Equivalent:
        const getConfigDir = (): string => path.join(os.homedir(), '.yt-transcribe')
    """
    return CONFIG_DIR


def ensure_config_dir() -> None:
    """
    Create the configuration directory structure if it doesn't exist.

    This is idempotent - safe to call multiple times.

    Raises:
        PermissionError: If unable to create directories

    TypeScript Context:
        Similar to fs.mkdirSync(dir, { recursive: true })
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict[str, Any]:
    """
    Load configuration from config.yaml.

    Returns:
        Dict[str, Any]: Configuration dictionary with all settings

    TypeScript Equivalent:
        const loadConfig = async (): Promise<Record<string, any>> => {
            const data = await fs.readFile(configFile, 'utf-8')
            return yaml.parse(data)
        }
    """
    if not CONFIG_FILE.exists():
        return get_default_config()

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config or get_default_config()


def save_config(config: Dict[str, Any]) -> None:
    """
    Save configuration to config.yaml.

    Args:
        config: Configuration dictionary to save

    Raises:
        IOError: If unable to write configuration file

    TypeScript Context:
        Similar to fs.writeFileSync(file, yaml.stringify(config))
    """
    ensure_config_dir()

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def get_default_config() -> Dict[str, Any]:
    """
    Get the default configuration structure.

    Returns:
        Dict[str, Any]: Default configuration with all required fields

    TypeScript Context:
        Like defining a default config object with interface:
        interface Config {
            ollama: { url: string; model: string };
            smtp: { server: string; port: number; ... };
            transcription: { model: string; ... };
        }
    """
    return {
        "ollama": {
            "url": "http://localhost:11434",
            "model": "llama2",
        },
        "smtp": {
            "server": "",
            "port": 587,
            "username": "",
            "password": "",
            "from_address": "",
            "to_address": "",
        },
        "transcription": {
            "model": "parakeet-tdt",
            "device": "cuda",  # or "cpu"
        },
        "playlists": [],
    }


def update_smtp_config(
    server: str,
    port: int,
    username: str,
    password: str,
    from_address: str,
    to_address: str,
) -> None:
    """
    Update SMTP configuration for email delivery.

    Args:
        server: SMTP server hostname (e.g., smtp.gmail.com)
        port: SMTP port (typically 587 for TLS)
        username: SMTP username
        password: SMTP password or app-specific password
        from_address: Email address to send from
        to_address: Email address to send to

    TypeScript Context:
        Similar to updating nested object properties:
        config.smtp = { server, port, username, ... }
    """
    config = load_config()
    config["smtp"].update(
        {
            "server": server,
            "port": port,
            "username": username,
            "password": password,
            "from_address": from_address,
            "to_address": to_address,
        }
    )
    save_config(config)


def get_smtp_config() -> Optional[Dict[str, Any]]:
    """
    Get SMTP configuration if configured.

    Returns:
        Optional[Dict[str, Any]]: SMTP config or None if not configured

    TypeScript Equivalent:
        const getSmtpConfig = (): SmtpConfig | null => { ... }
    """
    config = load_config()
    smtp = config.get("smtp", {})

    # Check if SMTP is configured
    if not smtp.get("server") or not smtp.get("username"):
        return None

    return smtp


def add_playlist(
    playlist_id: str,
    name: str,
    prompt_template: str,
) -> None:
    """
    Add a playlist configuration to the config file.

    Args:
        playlist_id: YouTube playlist ID
        name: Friendly name for the playlist
        prompt_template: Name of the prompt template to use

    TypeScript Context:
        Like pushing to an array:
        config.playlists.push({ playlistId, name, promptTemplate })
    """
    config = load_config()

    # Check if playlist already exists
    for playlist in config["playlists"]:
        if playlist["id"] == playlist_id:
            # Update existing
            playlist["name"] = name
            playlist["prompt_template"] = prompt_template
            save_config(config)
            return

    # Add new playlist
    config["playlists"].append(
        {
            "id": playlist_id,
            "name": name,
            "prompt_template": prompt_template,
        }
    )

    save_config(config)


def get_playlists() -> list[Dict[str, str]]:
    """
    Get all configured playlists.

    Returns:
        list[Dict[str, str]]: List of playlist configurations

    TypeScript Equivalent:
        const getPlaylists = (): Playlist[] => config.playlists

    Note:
        In Python 3.11+, we can use list[X] instead of List[X] from typing
        This is more similar to TypeScript's X[] syntax
    """
    config = load_config()
    return config.get("playlists", [])


def get_playlist_by_id(playlist_id: str) -> Optional[Dict[str, str]]:
    """
    Get a specific playlist configuration by ID.

    Args:
        playlist_id: YouTube playlist ID

    Returns:
        Optional[Dict[str, str]]: Playlist config or None if not found

    TypeScript Equivalent:
        const getPlaylistById = (id: string): Playlist | null =>
            config.playlists.find(p => p.id === id) ?? null
    """
    playlists = get_playlists()
    for playlist in playlists:
        if playlist["id"] == playlist_id:
            return playlist
    return None
