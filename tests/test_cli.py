"""Tests for CLI module."""

import pytest
from click.testing import CliRunner
from yt_transcribe import cli, config


def test_cli_main():
    """Test main CLI entry point."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ["--help"])
    
    assert result.exit_code == 0
    assert "YouTube Playlist Auto-Transcriber" in result.output


def test_cli_version():
    """Test CLI version flag."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ["--version"])
    
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_cli_init_help():
    """Test init command help."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ["init", "--help"])
    
    assert result.exit_code == 0
    assert "Initialize yt-transcribe" in result.output


def test_cli_add_help():
    """Test add command help."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ["add", "--help"])
    
    assert result.exit_code == 0
    assert "Add a playlist configuration" in result.output
    assert "--playlist" in result.output
    assert "--name" in result.output
    assert "--prompt" in result.output


def test_cli_list_help():
    """Test list command help."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ["list", "--help"])
    
    assert result.exit_code == 0
    assert "List all configured playlists" in result.output


def test_cli_run_help():
    """Test run command help."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ["run", "--help"])
    
    assert result.exit_code == 0
    assert "Run the transcription pipeline" in result.output
    assert "--id" in result.output
    assert "--all" in result.output
    assert "--dry-run" in result.output


def test_cli_list_no_playlists(temp_config_dir):
    """Test list command with no configured playlists."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ["list"])
    
    assert result.exit_code == 0
    assert "No playlists configured" in result.output


def test_cli_list_with_playlists(temp_config_dir):
    """Test list command with configured playlists."""
    config.add_playlist("PLtest123", "Test Playlist", "guitar")
    
    runner = CliRunner()
    result = runner.invoke(cli.main, ["list"])
    
    assert result.exit_code == 0
    assert "Test Playlist" in result.output
    assert "PLtest123" in result.output
    assert "guitar" in result.output


def test_cli_run_missing_arguments():
    """Test run command without required arguments."""
    runner = CliRunner()
    result = runner.invoke(cli.main, ["run"])
    
    assert result.exit_code == 1
    assert "Must specify either --id or --all" in result.output
