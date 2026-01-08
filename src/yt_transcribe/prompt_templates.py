"""
Template management for prompt customization.

Handles loading, validation, and management of prompt templates
for different playlist types (guitar, coding, business, custom).

TypeScript Context:
- Like managing configuration files or JSON schemas
- Path resolution similar to require.resolve() in Node.js
- Type hints make template structure clear (like TS interfaces)
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from importlib import resources

from . import templates as templates_package


class PromptTemplate:
    """
    Represents a prompt template for video summarization.
    
    TypeScript Equivalent:
        interface PromptTemplate {
            name: string;
            systemPrompt: string;
            summaryFormat: string;
        }
    """
    
    def __init__(self, name: str, system_prompt: str, summary_format: str):
        """
        Initialize a prompt template.
        
        Args:
            name: Template name (e.g., 'guitar', 'coding')
            system_prompt: System prompt for the LLM
            summary_format: Format string for the summary output
        """
        self.name = name
        self.system_prompt = system_prompt
        self.summary_format = summary_format
    
    def format_summary(self, **kwargs: Any) -> str:
        """
        Format the summary using provided variables.
        
        Args:
            **kwargs: Variables to interpolate into the summary format
            
        Returns:
            str: Formatted summary
            
        Example:
            template.format_summary(
                summary="Main concepts...",
                actions="1. Practice...",
            )
        """
        try:
            return self.summary_format.format(**kwargs)
        except KeyError as e:
            # If a variable is missing, return format string with available data
            return self.summary_format
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptTemplate":
        """
        Create a template from a dictionary.
        
        Args:
            data: Dictionary containing template data
            
        Returns:
            PromptTemplate: New template instance
            
        TypeScript Context:
            Similar to a factory method:
            static fromDict(data: TemplateData): PromptTemplate
        """
        return cls(
            name=data["name"],
            system_prompt=data["system_prompt"],
            summary_format=data["summary_format"],
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert template to dictionary.
        
        Returns:
            Dict[str, Any]: Template data as dictionary
        """
        return {
            "name": self.name,
            "system_prompt": self.system_prompt,
            "summary_format": self.summary_format,
        }


def load_builtin_template(name: str) -> Optional[PromptTemplate]:
    """
    Load a built-in template by name.
    
    Args:
        name: Template name (e.g., 'guitar', 'coding', 'business')
        
    Returns:
        Optional[PromptTemplate]: Template if found, None otherwise
        
    TypeScript Context:
        Like loading a bundled resource:
        const loadTemplate = (name: string): Template | null => {
            const path = require.resolve(`./templates/${name}.yaml`)
            return yaml.parse(fs.readFileSync(path, 'utf-8'))
        }
    """
    template_file = f"{name}.yaml"
    
    try:
        # Python 3.11+ way to read package resources
        template_path = Path(__file__).parent / "templates" / template_file
        
        if not template_path.exists():
            return None
        
        with open(template_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return PromptTemplate.from_dict(data)
    
    except (FileNotFoundError, KeyError, yaml.YAMLError):
        return None


def load_custom_template(path: str) -> PromptTemplate:
    """
    Load a custom template from a file path.
    
    Args:
        path: Path to custom template YAML file
        
    Returns:
        PromptTemplate: Loaded template
        
    Raises:
        FileNotFoundError: If template file doesn't exist
        ValueError: If template is invalid
    """
    template_path = Path(path).expanduser()
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {path}")
    
    with open(template_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Validate required fields
    required_fields = ["name", "system_prompt", "summary_format"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Template missing required field: {field}")
    
    return PromptTemplate.from_dict(data)


def get_available_templates() -> List[str]:
    """
    Get list of available built-in templates.
    
    Returns:
        List[str]: List of template names
        
    TypeScript Equivalent:
        const getAvailableTemplates = (): string[] => {
            return fs.readdirSync('./templates')
                .filter(f => f.endsWith('.yaml'))
                .map(f => f.replace('.yaml', ''))
        }
    """
    templates_dir = Path(__file__).parent / "templates"
    
    if not templates_dir.exists():
        return []
    
    templates = []
    for file in templates_dir.glob("*.yaml"):
        templates.append(file.stem)  # stem = filename without extension
    
    return sorted(templates)


def validate_template(template: PromptTemplate) -> bool:
    """
    Validate that a template has all required fields.
    
    Args:
        template: Template to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not template.name or not template.system_prompt or not template.summary_format:
        return False
    
    return True


def get_template(name: str) -> Optional[PromptTemplate]:
    """
    Get a template by name, checking built-in templates first,
    then treating the name as a file path for custom templates.
    
    Args:
        name: Template name or file path
        
    Returns:
        Optional[PromptTemplate]: Template if found, None otherwise
        
    TypeScript Context:
        Similar to a flexible module resolver:
        const getTemplate = (name: string): Template | null => {
            return loadBuiltin(name) ?? loadCustom(name) ?? null
        }
    """
    # Try built-in first
    template = load_builtin_template(name)
    if template:
        return template
    
    # Try as custom file path
    try:
        return load_custom_template(name)
    except (FileNotFoundError, ValueError):
        return None
