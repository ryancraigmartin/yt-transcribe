"""Tests for prompt templates module."""

import pytest
from pathlib import Path
from yt_transcribe import prompt_templates


def test_get_available_templates():
    """Test getting list of available templates."""
    templates = prompt_templates.get_available_templates()
    
    assert "guitar" in templates
    assert "coding" in templates
    assert "business" in templates


def test_load_builtin_template():
    """Test loading a built-in template."""
    template = prompt_templates.load_builtin_template("guitar")
    
    assert template is not None
    assert template.name == "guitar"
    assert len(template.system_prompt) > 0
    assert len(template.summary_format) > 0


def test_load_builtin_template_not_found():
    """Test loading a non-existent template returns None."""
    template = prompt_templates.load_builtin_template("nonexistent")
    assert template is None


def test_get_template_builtin():
    """Test getting a built-in template."""
    template = prompt_templates.get_template("coding")
    
    assert template is not None
    assert template.name == "coding"


def test_prompt_template_to_dict():
    """Test converting template to dictionary."""
    template = prompt_templates.PromptTemplate(
        name="test",
        system_prompt="Test prompt",
        summary_format="Test format",
    )
    
    data = template.to_dict()
    
    assert data["name"] == "test"
    assert data["system_prompt"] == "Test prompt"
    assert data["summary_format"] == "Test format"


def test_prompt_template_from_dict():
    """Test creating template from dictionary."""
    data = {
        "name": "test",
        "system_prompt": "Test prompt",
        "summary_format": "Test format",
    }
    
    template = prompt_templates.PromptTemplate.from_dict(data)
    
    assert template.name == "test"
    assert template.system_prompt == "Test prompt"
    assert template.summary_format == "Test format"


def test_prompt_template_format_summary():
    """Test formatting a summary with variables."""
    template = prompt_templates.PromptTemplate(
        name="test",
        system_prompt="Test",
        summary_format="Summary: {summary}\nActions: {actions}",
    )
    
    result = template.format_summary(
        summary="Main points here",
        actions="1. Do this\n2. Do that",
    )
    
    assert "Main points here" in result
    assert "1. Do this" in result


def test_validate_template_valid():
    """Test validating a valid template."""
    template = prompt_templates.PromptTemplate(
        name="test",
        system_prompt="Test prompt",
        summary_format="Test format",
    )
    
    assert prompt_templates.validate_template(template) is True


def test_validate_template_invalid():
    """Test validating an invalid template."""
    template = prompt_templates.PromptTemplate(
        name="",
        system_prompt="",
        summary_format="",
    )
    
    assert prompt_templates.validate_template(template) is False


def test_load_custom_template(tmp_path):
    """Test loading a custom template from file."""
    template_file = tmp_path / "custom.yaml"
    template_file.write_text("""
name: custom
system_prompt: Custom prompt
summary_format: Custom format {summary}
""")
    
    template = prompt_templates.load_custom_template(str(template_file))
    
    assert template.name == "custom"
    assert template.system_prompt == "Custom prompt"
    assert "Custom format" in template.summary_format


def test_load_custom_template_not_found():
    """Test loading a non-existent custom template."""
    with pytest.raises(FileNotFoundError):
        prompt_templates.load_custom_template("/nonexistent/path.yaml")


def test_load_custom_template_invalid():
    """Test loading an invalid custom template."""
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("name: custom\n")  # Missing required fields
        f.flush()
        
        with pytest.raises(ValueError):
            prompt_templates.load_custom_template(f.name)
