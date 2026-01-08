"""Tests for summarizer module."""

import pytest
from yt_transcribe.core import summarizer
from yt_transcribe import prompt_templates


@pytest.mark.asyncio
async def test_ollama_summarizer_init():
    """Test Ollama summarizer initialization."""
    sum_service = summarizer.OllamaSummarizer()

    assert sum_service.base_url == "http://localhost:11434"
    assert sum_service.model == "llama2"


@pytest.mark.asyncio
async def test_ollama_summarizer_custom_config():
    """Test Ollama summarizer with custom configuration."""
    sum_service = summarizer.OllamaSummarizer(
        base_url="http://custom:8080",
        model="mistral",
    )

    assert sum_service.base_url == "http://custom:8080"
    assert sum_service.model == "mistral"


@pytest.mark.asyncio
async def test_check_connection_failure():
    """Test connection check when Ollama is not running."""
    sum_service = summarizer.OllamaSummarizer(base_url="http://localhost:99999")

    is_connected = await sum_service.check_connection()

    assert is_connected is False


@pytest.mark.asyncio
async def test_list_models_failure():
    """Test listing models when Ollama is not running."""
    sum_service = summarizer.OllamaSummarizer(base_url="http://localhost:99999")

    with pytest.raises(summarizer.SummarizationError):
        await sum_service.list_models()


def test_create_summarizer():
    """Test creating a summarizer with factory function."""
    sum_service = summarizer.create_summarizer()

    assert isinstance(sum_service, summarizer.OllamaSummarizer)
    assert sum_service.base_url == "http://localhost:11434"


def test_create_summarizer_custom():
    """Test creating a summarizer with custom settings."""
    sum_service = summarizer.create_summarizer(
        base_url="http://custom:8080",
        model="mistral",
    )

    assert sum_service.base_url == "http://custom:8080"
    assert sum_service.model == "mistral"


def test_summary_result_dataclass():
    """Test SummaryResult dataclass."""
    result = summarizer.SummaryResult(
        summary="Test summary",
        raw_response="Raw response",
        model="llama2",
        tokens_used=100,
    )

    assert result.summary == "Test summary"
    assert result.raw_response == "Raw response"
    assert result.model == "llama2"
    assert result.tokens_used == 100
