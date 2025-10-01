# FZX-Terminal

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](https://github.com/your-repo)

Generate software projects from natural language using 330+ AI models.

FZX-Terminal is a command-line tool that converts project descriptions into working code. It integrates with OpenRouter (326+ models) and Google Gemini to provide access to both free and paid AI models for code generation.

## Features

- Generate projects from natural language descriptions
- Access to 330+ AI models (57 free models available)
- Interactive model browser with cost and capability information
- Support for multiple programming languages and frameworks
- Real-time code analysis and quality assessment
- Built-in project templates for common use cases
- Session management and build history tracking
- Cross-platform support (Windows, macOS, Linux)

## Installation

### Requirements

- Python 3.8 or higher
- Internet connection for AI model access
- 100MB available disk space

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/fraol163/FZX-Terminal-.git
cd FZX-Terminal-

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify installation
python test_imports.py

# 4. Launch FZX-Terminal
python terminal_interface.py
```

### Verification

Run the installation verification script:

```bash
python test_imports.py
```

Expected output:
```
FZX-Terminal Installation Check
========================================
Testing module imports...
✅ aiohttp
✅ psutil
✅ All modules imported successfully

Testing FZX-Terminal modules...
✅ enhanced_ai_provider
✅ advanced_building_agent
✅ building_agent
✅ All FZX-Terminal modules imported successfully

✅ Installation verified! Ready to use FZX-Terminal
```

## Usage

### Quick Start

1. **Setup AI Provider** (one-time):
   ```bash
   build setup-ai openrouter
   ```
   
2. **Generate a Project**:
   ```bash
   build describe 'Create a React todo app with dark mode'
   ```

3. **Browse Available Models**:
   ```bash
   build browse-models
   ```

### Core Commands

#### Project Generation
```bash
# Natural language generation
build describe 'Create a FastAPI server with JWT authentication'
build describe 'Build a React dashboard with charts and dark mode'
build describe 'Make a Python CLI tool for file management'

# Template-based generation
build web my-app --framework react
build api my-server --framework fastapi
build cli my-tool --language python
```

#### AI Provider Management
```bash
build setup-ai openrouter    # Setup OpenRouter (326+ models)
build setup-ai gemini        # Setup Google Gemini (4 models)
build ai-status              # Show current AI configuration
build browse-models          # Interactive model browser
```

#### Analysis and Monitoring
```bash
build analyze                # Analyze generated code quality
build status                 # System and build status
build history                # View build history
```

## Examples

### React Todo App

**Command:**
```bash
build describe 'Create a React todo app with add, delete, and mark complete functionality. Use modern React hooks. Add dark mode toggle. Make it mobile responsive.'
```

**Generated files:**
- `src/App.jsx` - Main application component
- `src/components/TodoList.jsx` - Todo list component  
- `src/components/TodoItem.jsx` - Individual todo item
- `src/components/AddTodo.jsx` - Add todo form
- `src/styles/App.css` - Responsive CSS with dark mode
- `package.json` - Project dependencies

**Features automatically included:**
- Local storage persistence
- Mobile-responsive design
- Dark mode toggle
- Modern React hooks (useState, useEffect)

See complete example: [examples/react-todo/](examples/react-todo/)

### FastAPI Blog Server

**Command:**
```bash
build describe 'Build a FastAPI server for a simple blog with user authentication, post creation, and basic CRUD operations'
```

**Generated components:**
- User registration and login endpoints
- JWT token authentication
- Post CRUD operations
- Automatic API documentation
- Password hashing
- Request validation

See complete example: [examples/fastapi-blog/](examples/fastapi-blog/)

### Python CLI Tool

**Command:**
```bash
build describe 'Create a Python CLI tool for file management with colors and progress bars'
```

**Generated features:**
- Argument parsing with argparse
- Colored terminal output
- Progress bars for operations
- File operations (copy, move, delete)
- Error handling

See complete example: [examples/cli-file-manager/](examples/cli-file-manager/)

## AI Models

### Free Models (0 cost)
FZX-Terminal provides access to 57 free models:

- **DeepSeek-Coder-V2**: Best free coding model
- **Gemini 2.0 Flash**: 1M context, good for large projects
- **Qwen3-Coder**: Strong Python generation
- **CodeLlama-70B**: Good for basic applications

### Model Selection Guide

| Task | Free Option | Paid Option | Cost (typical project) |
|------|-------------|-------------|------------------------|
| React apps | DeepSeek-Coder-V2 | GPT-4 | $0.02 - $0.05 |
| Python APIs | Qwen3-Coder | Claude-3-Sonnet | $0.01 - $0.03 |
| CLI tools | CodeLlama-70B | GPT-4-Turbo | $0.02 - $0.04 |
| Documentation | Gemini-2.0-Flash | Claude-3-Opus | $0.01 - $0.02 |

**Daily Limits (Free Tier):**
- OpenRouter: 200 requests, 200k tokens
- Gemini: 1,500 requests, higher token limit

For detailed model information, see [docs/MODELS.md](docs/MODELS.md)

## File Structure

```
FZX-Terminal/
├── Core Components
│   ├── terminal_interface.py       # Main CLI interface
│   ├── advanced_building_agent.py  # AI logic and parsing
│   ├── enhanced_ai_provider.py     # Model management
│   └── building_agent.py          # Project generation
│
├── Documentation
│   ├── docs/MODELS.md             # Model selection guide
│   ├── docs/SECURITY.md           # Security considerations
│   ├── docs/COSTS.md              # Cost and rate limits
│   └── docs/KNOWN_ISSUES.md       # Common issues and solutions
│
├── Examples
│   ├── examples/react-todo/       # Complete React app
│   ├── examples/fastapi-blog/     # FastAPI server
│   └── examples/cli-file-manager/ # Python CLI tool
│
├── Templates
│   └── templates/                 # Project templates
│
└── Configuration
    └── .terminal_data/            # User data and API keys
```

## Commands Reference

### Building Commands
```bash
build describe '<description>'   # Generate from natural language
build web <name> --framework <fw>   # Create web application
build api <name> --framework <fw>   # Create API server
build cli <name> --language <lang>  # Create CLI tool
build templates                     # List available templates
```

### AI Commands
```bash
build setup-ai <provider>      # Configure AI provider
build ai-status                # Show AI configuration
build browse-models            # Interactive model browser
build check-updates            # Check for new models
```

### Analysis Commands
```bash
build analyze                  # Analyze code quality
build status                   # System status
build history                  # Build history
```

### Utility Commands
```bash
help                          # Show help information
status                        # System status
clear                         # Clear screen
exit                          # Exit FZX-Terminal
```

For complete command reference, run `help` in FZX-Terminal.

## Configuration

### API Keys

Store API keys securely:

```bash
# Option 1: Interactive setup
build setup-ai openrouter

# Option 2: Environment variables
export OPENROUTER_API_KEY="your-key"
export GEMINI_API_KEY="your-key"
```

### Security Notes

- API keys are stored in `.terminal_data/config.json`
- This directory is added to `.gitignore`
- Use separate keys for development and production
- See [docs/SECURITY.md](docs/SECURITY.md) for details

## Troubleshooting

### Common Issues

**Installation Problems:**
```bash
# Module import errors
pip install -r requirements.txt
python test_imports.py

# Python version issues
python --version  # Should be 3.8+
```

**API Issues:**
```bash
# Rate limit exceeded
build ai-status  # Check usage
# Switch to different model or wait

# Model timeout
# Use simpler description or faster model
```

**Generation Issues:**
- Be specific in descriptions
- Test with free models first
- Review generated code before use

For detailed troubleshooting, see [docs/KNOWN_ISSUES.md](docs/KNOWN_ISSUES.md)

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
```bash
git clone https://github.com/fraol163/FZX-Terminal-.git
cd FZX-Terminal-
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python test_imports.py
```

### Testing
```bash
python test_imports.py        # Verify installation
python terminal_interface.py  # Launch FZX-Terminal
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/fraol163/FZX-Terminal-/issues)
- **Documentation**: [docs/](docs/) directory
- **Examples**: [examples/](examples/) directory

---
