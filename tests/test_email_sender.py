"""Tests for email sender module."""

import pytest
from yt_transcribe.core import email_sender


def test_email_config_dataclass():
    """Test EmailConfig dataclass."""
    config = email_sender.EmailConfig(
        server="smtp.gmail.com",
        port=587,
        username="user@gmail.com",
        password="secret",
        from_address="from@gmail.com",
        to_address="to@gmail.com",
    )
    
    assert config.server == "smtp.gmail.com"
    assert config.port == 587
    assert config.username == "user@gmail.com"


def test_markdown_to_html():
    """Test basic Markdown to HTML conversion."""
    markdown = """
# Main Title
## Subtitle
This is a paragraph.

- Item 1
- Item 2

Another paragraph.
"""
    
    html = email_sender.markdown_to_html(markdown)
    
    assert "<h1>Main Title</h1>" in html
    assert "<h2>Subtitle</h2>" in html
    assert "<li>Item 1</li>" in html
    assert "<li>Item 2</li>" in html
    assert "<p>This is a paragraph.</p>" in html


def test_markdown_to_html_code_blocks():
    """Test Markdown code block conversion."""
    markdown = """
```python
def hello():
    print("Hello")
```
"""
    
    html = email_sender.markdown_to_html(markdown)
    
    assert "<pre><code>" in html
    assert "</pre>" in html
    assert "def hello():" in html


def test_verify_smtp_config_invalid():
    """Test SMTP verification with invalid config."""
    config = email_sender.EmailConfig(
        server="invalid.server.com",
        port=99999,
        username="invalid",
        password="invalid",
        from_address="invalid@test.com",
        to_address="invalid@test.com",
    )
    
    result = email_sender.verify_smtp_config(config)
    
    assert result is False
