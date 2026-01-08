"""Test configuration and fixtures."""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_config_dir(monkeypatch):
    """
    Create a temporary config directory for testing.

    This fixture:
    - Creates a temporary directory
    - Patches config.CONFIG_DIR to use it
    - Cleans up after the test

    TypeScript Context:
        Similar to beforeEach/afterEach in Jest:
        beforeEach(() => {
            tempDir = fs.mkdtempSync()
            process.env.CONFIG_DIR = tempDir
        })
        afterEach(() => fs.rmSync(tempDir))
    """
    temp_dir = Path(tempfile.mkdtemp())

    # Patch all config paths to use temp directory
    from yt_transcribe import config

    monkeypatch.setattr(config, "CONFIG_DIR", temp_dir)
    monkeypatch.setattr(config, "CONFIG_FILE", temp_dir / "config.yaml")
    monkeypatch.setattr(config, "DATABASE_FILE", temp_dir / "state.db")
    monkeypatch.setattr(config, "MODELS_DIR", temp_dir / "models")
    monkeypatch.setattr(config, "TEMPLATES_DIR", temp_dir / "templates")

    yield temp_dir

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_audio_file(tmp_path):
    """Create a mock audio file for testing."""
    audio_file = tmp_path / "test_audio.wav"
    audio_file.write_text("mock audio data")
    return audio_file
