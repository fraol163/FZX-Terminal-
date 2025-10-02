# FZX-Terminal

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](https://github.com/your-repo)

Advanced AI-powered terminal interface with codebase understanding capabilities.

FZX-Terminal is a command-line tool that provides intelligent AI assistance with the ability to read and understand your project files. The AI can analyze your codebase to provide contextual responses, though conversation history preservation is limited.

## Features

- **Codebase Understanding**: AI can read and analyze project files for contextual responses
- **Limited Conversation Memory**: Basic conversation history tracking
- **Multi-Provider Support**: Google Gemini and OpenRouter integration
- **Latest AI Models**: Access to Gemini 2.0 Flash Experimental and other cutting-edge models
- **Enhanced Response Design**: Cool borders and formatting for all AI responses
- **Secure API Key Management**: Safe storage and management of API keys
- **Real-time Validation**: API key validation during setup
- **Cross-platform Support**: Works on Windows, macOS, and Linux

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
   ai config setup
   ```
   
2. **Chat with AI**:
   ```bash
   ai chat 'Explain how to create a Python virtual environment'
   ```

3. **Manage API Keys**:
   ```bash
   ai config add-key
   ai config edit-key
   ai config delete-key
   ```

### AI Commands

#### AI Configuration
```bash
ai config setup     # Interactive setup with latest Gemini models and validation
ai config show      # Show current configuration with masked API key
ai config test      # Test AI connection with current model
```

#### API Key Management
```bash
ai config add-key   # Add or replace API key with real-time validation
ai config edit-key  # Edit current API key with validation
ai config delete-key # Remove API key and configuration completely
```

#### AI Chat
```bash
# Chat with AI using project context
ai chat 'Explain how to implement authentication in Python'

# Codebase-aware queries
ai chat 'How does the context manager work in this project?'
ai chat 'Explain the chat manager implementation'
ai chat 'What are the key components of the AI service?'
```

## AI Models

### Latest Gemini Models
- **Gemini 2.0 Flash Experimental** - Latest experimental model with enhanced capabilities
- **Gemini 1.5 Pro Latest** - Most capable model for complex tasks
- **Gemini 1.5 Flash Latest** - Fast and efficient model
- **Gemini 1.5 Flash 8B Latest** - Lightweight and fast model

### OpenRouter Models
Access to 300+ models including:
- **Free Models**: DeepSeek-Coder-V2, Qwen3-Coder, CodeLlama-70B
- **Premium Models**: GPT-4, Claude-3, and more

## Enhanced User Experience

### Cool Design for All AI Responses
All AI responses feature a consistent, professional design with:
- Colorful borders for better visual separation
- Proper alignment and spacing
- Metadata display (model, response time, tokens)
- Consistent formatting across all commands

### Codebase Understanding
FZX-Terminal's AI can read and understand your project files:
- **Code Analysis**: AI can examine your code for contextual responses
- **File Referencing**: Ask about specific components and get relevant information
- **Implementation Details**: Get explanations of how different parts work

Example queries:
```bash
ai chat 'How does the context manager work in this project?'
# AI reads the context_manager.py file and explains its implementation

ai chat 'Explain the chat manager implementation'
# AI examines chat_manager.py and provides details

ai chat 'What are the key components of the AI service?'
# AI analyzes ai_service.py and describes the architecture
```

## Project Architecture

FZX-Terminal consists of several core components that work together to provide an AI-powered terminal experience:

### Core Components

- **[terminal_interface.py](terminal_interface.py)** - Main CLI interface handling user commands and interactions
- **[ai_service.py](ai_service.py)** - AI service implementation with provider integrations (Gemini, OpenRouter)
- **[chat_manager.py](chat_manager.py)** - Basic chat history management
- **[context_manager.py](context_manager.py)** - Context management and optimization system

### How Codebase Understanding Works

1. **File Access**: The AI service can read project files when referenced in queries
2. **Context Building**: Relevant code sections are included in the AI prompt
3. **Response Generation**: AI provides informed responses based on actual code

### Current Limitations

- **Conversation Memory**: Limited conversation history preservation
- **Context Persistence**: Context may not persist across sessions
- **Follow-up Capabilities**: Basic follow-up support, may not reference previous responses reliably

## File Structure

```
FZX-Terminal/
├── Core Components
│   ├── terminal_interface.py       # Main CLI interface
│   ├── ai_service.py              # AI service implementation
│   ├── chat_manager.py            # Basic chat history management
│   └── context_manager.py         # Context management system
│
├── Documentation
│   ├── docs/MODELS.md             # Model selection guide
│   ├── docs/SECURITY.md           # Security considerations
│   └── docs/COSTS.md              # Cost and rate limits
│
├── Configuration
│   └── .terminal_data/            # User data and API keys
│       └── config.json            # AI configuration
```

## Commands Reference

### AI Commands
```bash
ai config setup              # Setup AI provider and model
ai config test               # Test AI connection
ai config show               # Show current configuration
ai config add-key            # Add API key
ai config edit-key           # Edit API key
ai config delete-key         # Delete API key

# AI Chat
ai chat <message>            # Chat with AI using project context
ai status                    # Show AI configuration status
ai help                      # Show comprehensive help
```

### Utility Commands
```bash
help                         # Show help information
status                       # System status
clear                        # Clear screen
exit                         # Exit FZX-Terminal
```

For complete command reference, run `help` in FZX-Terminal.

## Configuration

### API Keys

Store API keys securely:

```bash
# Option 1: Interactive setup
ai config setup

# Option 2: Environment variables
export GEMINI_API_KEY="your-key"
export OPENROUTER_API_KEY="your-key"
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
ai status  # Check usage
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

MIT License 

## Support

- **Issues**: [GitHub Issues](https://github.com/fraol163/FZX-Terminal-/issues)
- **Documentation**: [docs/](docs/) directory