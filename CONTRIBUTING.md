# Contributing to FZX-Terminal

## Codebase Organization

FZX-Terminal/
├── Core Components (DO NOT MODIFY without discussion)
│   ├── terminal_interface.py      # Main CLI (4,100 lines)
│   ├── advanced_building_agent.py # AI logic (950 lines)
│   ├── enhanced_ai_provider.py    # Model management (850 lines)
│   └── building_agent.py          # Generation engine (500 lines)
│
├── Extend Here (SAFE to modify)
│   ├── project_templates.py       # Add new project templates here
│   ├── templates/                 # Template files
│   └── plugins/                   # Custom plugins
│
├── Utilities (MODIFY carefully)
│   ├── context_manager.py
│   ├── session_bridge.py
│   └── file_manager.py
│
└── Data (NEVER commit)
    └── .terminal_data/            # User data, API keys

## How Components Interact

```
User Command
    ↓
terminal_interface.py
    ↓
advanced_building_agent.py (parses description)
    ↓
enhanced_ai_provider.py (calls AI model)
    ↓
building_agent.py (generates files)
    ↓
project_templates.py (applies template)
    ↓
Output to disk
```

## Adding Features

### Add a New Project Template

1. Edit project_templates.py
2. Add template to TEMPLATES dict:

```python
"svelte": {
    "name": "Svelte App",
    "description": "Modern Svelte application",
    "files": {
        "src/App.svelte": "svelte_app_template",
        "package.json": "svelte_package_json",
    },
    "commands": ["npm install", "npm run dev"]
}
```

3. Add template content below
4. Test: `build web my-app --framework svelte`
5. Submit PR with example output

### Add a New AI Provider

1. Edit enhanced_ai_provider.py
2. Add to AIProvider enum
3. Implement API calls in _call_provider()
4. Add configuration in configure_provider()
5. Test with real API key
6. Document in docs/MODELS.md

### Add a New Command

1. Edit terminal_interface.py
2. Add command to _register_commands()
3. Implement handler method
4. Add to help text
5. Test all edge cases
6. Update docs/COMMANDS.md

## Development Setup

```bash
# Fork and clone
git clone https://github.com/fraol163/FZX-Terminal-.git
cd FZX-Terminal-

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dev dependencies
pip install -r requirements.txt
pip install pytest black pylint

# Run tests
python test_imports.py
pytest tests/

# Check code style
black .
pylint *.py
```

## Development Guidelines

### Code Style
- Follow PEP 8
- Use type hints where possible
- Add docstrings to all functions
- Keep functions under 50 lines
- Use meaningful variable names

### Testing
- Write tests for new features
- Test with multiple AI models
- Test error conditions
- Test with and without API keys

### Documentation
- Update relevant docs/ files
- Add examples for new features
- Update README if needed
- Include usage examples

### Security
- Never commit API keys
- Validate all user inputs
- Review generated code examples
- Don't store sensitive data

## Submitting Changes

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make your changes**
4. **Test thoroughly**: `python test_imports.py`
5. **Commit with clear message**: `git commit -m "Add: new feature description"`
6. **Push to your fork**: `git push origin feature-name`
7. **Create Pull Request**

### Pull Request Guidelines

- Include clear description of changes
- Add tests for new functionality
- Update documentation as needed
- Include before/after examples
- Reference any related issues

## Getting Help

- **Questions**: Open a GitHub issue with "Question:" prefix
- **Bug Reports**: Include reproduction steps and error messages
- **Feature Requests**: Describe the use case and benefit
- **Documentation**: Help improve our docs

## Solo Developer Context

This project is optimized for solo developers working without salary. Contributions should focus on:
- Personal productivity improvements
- Zero-cost tools and solutions
- Individual workflow enhancements
- Simple, practical features

Thank you for contributing to FZX-Terminal!