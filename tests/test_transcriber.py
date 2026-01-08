"""Tests for transcriber module."""

import pytest
from yt_transcribe.core import transcriber


def test_mock_transcription_service_available():
    """Test that mock service is always available."""
    service = transcriber.MockTranscriptionService()
    assert service.is_available() is True


def test_mock_transcription_service_transcribe(mock_audio_file):
    """Test mock transcription."""
    service = transcriber.MockTranscriptionService()

    result = service.transcribe(mock_audio_file)

    assert isinstance(result, str)
    assert len(result) > 0
    assert "mock transcription" in result.lower()


def test_mock_transcription_service_file_not_found(tmp_path):
    """Test mock transcription with non-existent file."""
    service = transcriber.MockTranscriptionService()

    nonexistent_file = tmp_path / "nonexistent.wav"

    with pytest.raises(transcriber.TranscriptionError):
        service.transcribe(nonexistent_file)


def test_get_transcription_service_mock():
    """Test getting mock transcription service."""
    service = transcriber.get_transcription_service(use_mock=True)

    assert isinstance(service, transcriber.MockTranscriptionService)
    assert service.is_available()


def test_nemo_transcription_service_not_implemented(mock_audio_file):
    """Test that NeMo service raises NotImplementedError."""
    service = transcriber.NeMoTranscriptionService()

    with pytest.raises(NotImplementedError):
        service.transcribe(mock_audio_file)


def test_nemo_transcription_service_is_available():
    """Test checking if NeMo is available (should be False without install)."""
    service = transcriber.NeMoTranscriptionService()

    # Should be False since nemo_toolkit is not installed in test environment
    assert service.is_available() is False
