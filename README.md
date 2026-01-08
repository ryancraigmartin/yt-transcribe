# YouTube Playlist Auto-Transcriber

A local-first utility for transcribing and summarizing YouTube playlists using AI. Built with privacy and zero recurring costs in mind.

## 🎯 Features

- **Local Transcription**: Uses NVIDIA NeMo Parakeet TDT for ultra-fast, accurate transcription (140x-300x real-time)
- **Local Summarization**: Integrates with Ollama for private, local AI summarization
- **Playlist-Specific Prompts**: Different templates for different content types (guitar lessons, coding tutorials, business content)
- **Automated Email Delivery**: Sends formatted Markdown summaries via SMTP
- **State Management**: SQLite database tracks processed videos to prevent duplicates
- **Beautiful CLI**: Built with Click and Rich for an excellent terminal experience

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for downloading videos
- [Ollama](https://ollama.ai/) for local AI summarization (optional but recommended)
- NVIDIA GPU with CUDA for fast transcription (optional, CPU works but slower)

### Installation

```bash
# Clone the repository
git clone https://github.com/ryancraigmartin/yt-transcribe.git
cd yt-transcribe

# Install dependencies
pip install -e .

# For development with testing tools
pip install -e ".[dev]"

# Install yt-dlp
pip install yt-dlp
```

### Initial Setup

```bash
# Initialize configuration
yt-transcribe init

# This will prompt you for:
# - SMTP server settings (for email delivery)
# - Email addresses
# And will create ~/.yt-transcribe/ directory
```

**Gmail Users**: Use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

## 📖 Usage

### Add a Playlist

```bash
yt-transcribe add \
  --playlist PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf \
  --name "Guitar Lessons" \
  --prompt guitar
```

### List Configured Playlists

```bash
yt-transcribe list
```

### Process Videos

```bash
# Process all videos in all playlists
yt-transcribe run --all

# Process specific playlist
yt-transcribe run --id PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf

# Dry run (see what would be processed)
yt-transcribe run --all --dry-run
```

## 🎨 Prompt Templates

The application includes three built-in templates optimized for different content types:

### Guitar Template
Focuses on:
- Chord progressions and voicings
- Techniques (fingerpicking, strumming, bending, vibrato)
- Practice exercises
- Musical theory concepts

### Coding Template
Focuses on:
- Programming concepts and design patterns
- Code architecture and best practices
- Dependencies and frameworks
- Implementation steps
- Security considerations

### Business Template
Focuses on:
- Business concepts and strategies
- Market insights and trends
- Financial principles
- Action items and ROI considerations

### Custom Templates

Create your own YAML template:

```yaml
name: my-template
system_prompt: |
  You are an expert in analyzing [topic].
  Focus on [specific aspects].
  
summary_format: |
  ## Summary
  {summary}
  
  ## Key Points
  {key_points}
  
  ## Action Items
  {actions}
```

Use it with:
```bash
yt-transcribe add --playlist <ID> --name "My Content" --prompt /path/to/my-template.yaml
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                  CLI (Click)                     │
│              Beautiful UI (Rich)                 │
└───────────────────┬─────────────────────────────┘
                    │
    ┌───────────────┴───────────────┐
    │                               │
    ▼                               ▼
┌─────────┐                   ┌──────────┐
│ Config  │                   │ Database │
│ Manager │                   │ (SQLite) │
└─────────┘                   └──────────┘
    │
    ├─────────────────────────────────────┐
    │                                     │
    ▼                                     ▼
┌──────────────┐                    ┌────────────┐
│  Downloader  │                    │ Templates  │
│   (yt-dlp)   │                    │  Manager   │
└──────┬───────┘                    └────────────┘
       │
       ▼
┌──────────────┐
│ Transcriber  │
│ (NeMo/Mock)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Summarizer   │
│  (Ollama)    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Email Sender │
│    (SMTP)    │
└──────────────┘
```

## 🧪 Development

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_config.py

# Run with verbose output
pytest -v

# Check coverage
pytest --cov=yt_transcribe --cov-report=html
```

### Code Quality

```bash
# Format code with black
black src/ tests/

# Type checking with mypy
mypy src/
```

### Project Structure

```
yt-transcribe/
├── src/yt_transcribe/
│   ├── __init__.py
│   ├── cli.py              # Main CLI interface
│   ├── config.py           # Configuration management
│   ├── database.py         # SQLite state management
│   ├── prompt_templates.py # Template handling
│   ├── core/
│   │   ├── downloader.py   # YouTube download via yt-dlp
│   │   ├── transcriber.py  # Audio transcription
│   │   ├── summarizer.py   # AI summarization
│   │   └── email_sender.py # Email delivery
│   └── templates/          # Built-in prompt templates
│       ├── guitar.yaml
│       ├── coding.yaml
│       └── business.yaml
├── tests/                  # Comprehensive test suite
├── pyproject.toml          # Project configuration
└── README.md
```

## 🐳 Docker Support (Coming Soon)

A complete Docker setup will be added that includes:
- Pre-configured environment with all dependencies
- NVIDIA Container Toolkit for GPU support
- Ollama service
- One-command deployment

## 🔧 Configuration

Configuration is stored in `~/.yt-transcribe/config.yaml`:

```yaml
ollama:
  url: http://localhost:11434
  model: llama2

smtp:
  server: smtp.gmail.com
  port: 587
  username: your-email@gmail.com
  password: your-app-password
  from_address: your-email@gmail.com
  to_address: recipient@gmail.com

transcription:
  model: parakeet-tdt
  device: cuda  # or cpu

playlists:
  - id: PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf
    name: Guitar Lessons
    prompt_template: guitar
```

## 📚 Learning Python from TypeScript

This codebase is designed to help TypeScript developers learn Python idioms:

- **Type Hints**: Extensive use of Python type hints (similar to TypeScript types)
- **Docstrings**: Every function includes TypeScript equivalents in docstrings
- **Async/Await**: Python's asyncio works similarly to Node.js async/await
- **Path Operations**: Uses `pathlib.Path` (cleaner than string concatenation)
- **Context Managers**: Python's `with` statement handles resource cleanup automatically

Example comparison:

```typescript
// TypeScript
const getConfig = async (): Promise<Config> => {
    const data = await fs.readFile(configPath, 'utf-8')
    return JSON.parse(data)
}
```

```python
# Python
def get_config() -> Config:
    """Get configuration."""
    with open(config_path, 'r') as f:
        return json.load(f)
```

## 🤝 Contributing

Contributions welcome! This is an educational project, so:

1. Keep the TypeScript/Python comparisons in docstrings
2. Add tests for new features
3. Update documentation
4. Use type hints everywhere

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- [NVIDIA NeMo](https://github.com/NVIDIA/NeMo) for state-of-the-art transcription
- [Ollama](https://ollama.ai/) for local AI inference
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for reliable YouTube downloading
- [Click](https://click.palletsprojects.com/) and [Rich](https://rich.readthedocs.io/) for beautiful CLI

## 🗺️ Roadmap

- [ ] Docker and docker-compose setup
- [ ] GitHub Actions CI/CD
- [ ] Real NeMo Parakeet TDT integration
- [ ] Web UI for playlist management
- [ ] Support for other video platforms
- [ ] Batch processing optimizations
- [ ] Resume interrupted processing
- [ ] Export summaries to multiple formats (PDF, Notion, etc.)
