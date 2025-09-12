# AI Terminal Workflow - Robust Terminal Interface

A comprehensive, intelligent terminal interface designed for AI-powered development workflows with advanced project management, session persistence, and context-aware features.

## Project Overview

### Purpose
The AI Terminal Workflow is a sophisticated terminal interface that bridges the gap between traditional command-line tools and modern AI-assisted development. It provides an intelligent, context-aware environment for managing projects, tasks, messages, and development workflows.

### Key Features
- **🚀 Project Management**: Automatic project detection, creation, and switching
- **✅ Task Management**: Create, update, and track tasks with priority levels
- **💬 Message System**: Persistent message history with export capabilities
- **🧠 Chat Memory**: JSONL-based chat transcripts with auto-summaries every 5 turns
- **🔄 Session Bridge**: Seamless context preservation across sessions
- **📁 File Operations**: Direct file access with `@path/to/file` syntax
- **🎨 Premium UI**: Beautiful terminal interface with gradient themes
- **💾 Data Persistence**: Automatic saving of all project data
- **🧠 Context Intelligence**: Smart context compression and management
- **⚙️ Configuration**: Customizable themes, settings, and performance options
- **📊 Analytics**: Project statistics and workspace insights

### Benefits
- **Enhanced Productivity**: Streamlined workflow management in a single interface
- **Context Preservation**: Never lose your work context between sessions
- **Intelligent Organization**: Automatic project detection and organization
- **AI-Ready**: Designed specifically for AI-assisted development workflows
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Extensible**: Modular architecture for easy feature additions

## Product Requirements Document (PRD)

### Core Requirements

#### Functional Requirements
1. **Terminal Interface**
   - Interactive command-line interface with rich formatting
   - Real-time command processing and feedback
   - Keyboard interrupt handling and graceful shutdown

2. **Project Management**
   - Automatic project detection based on directory structure
   - Project creation, switching, and information display
   - Project-specific settings and configurations

3. **Task Management**
   - Task creation with titles, descriptions, and priorities
   - Task status tracking (pending, in-progress, completed, blocked)
   - Task filtering and search capabilities

4. **Session Management**
   - Persistent session storage and recovery
   - Context compression for memory optimization
   - Session history and backup functionality

5. **File Operations**
   - Direct file access using `@path/to/file` syntax
   - File and directory information display
   - Integration with system file operations

#### Technical Specifications

**Programming Language**: Python 3.8+

**Core Dependencies**:
- `pathlib` - File system operations
- `json` - Data serialization
- `uuid` - Unique identifier generation
- `datetime` - Timestamp management
- `threading` - Concurrent operations
- `dataclasses` - Data structure definitions

**Architecture**:
- **Modular Design**: Separate modules for different functionalities
- **Event-Driven**: Command processing with event handling
- **Data Persistence**: JSON-based storage with automatic backups
- **Memory Management**: Intelligent context compression and optimization
- **Token Budgeting**: Prompt builders that fit within configurable token limits

**Performance Requirements**:
- Startup time: < 2 seconds
- Command response time: < 100ms
- Memory usage: < 50MB for typical sessions
- File operations: Support for files up to 100MB

**Security Requirements**:
- No sensitive data logging
- Secure file path validation
- Input sanitization for all user commands
- Safe JSON parsing with error handling

### System Requirements

**Minimum Requirements**:
- Python 3.8 or higher
- 100MB available disk space
- 256MB RAM
- Terminal with ANSI color support

**Recommended Requirements**:
- Python 3.10 or higher
- 500MB available disk space
- 512MB RAM
- Modern terminal with Unicode support

## Installation Guide

### Prerequisites
1. **Python Installation**
   ```bash
   # Check Python version (must be 3.8+)
   python --version
   
   # If Python is not installed, download from:
   # https://www.python.org/downloads/
   ```

2. **Terminal Requirements**
   - Ensure your terminal supports ANSI colors
   - For Windows: Use Windows Terminal, PowerShell, or WSL
   - For macOS: Use Terminal.app or iTerm2
   - For Linux: Most modern terminals are supported

### Installation Steps

1. **Download the Project**
   ```bash
   # Clone or download the project files to your desired directory
   cd /path/to/your/project/directory
   ```

2. **Verify File Structure**
   Ensure all required files are present:
   ```
   ├── terminal_interface.py    # Main interface
   ├── launch.py              # Quick launcher
   ├── context_manager.py     # Context management
   ├── session_bridge.py      # Session persistence
   ├── project_inference.py   # Project detection
   ├── terminal_persistence.py # Data persistence
   └── README.md              # This file
   ```

3. **Initial Setup**
   ```bash
   # Make the main script executable (Linux/macOS)
   chmod +x terminal_interface.py
   
   # Test the installation
   python terminal_interface.py
   ```

4. **Configuration (Optional)**
   - The system will create necessary directories automatically
   - Configuration files will be generated on first run
   - Customize settings using the `config` command within the interface

### Verification
After installation, you should see:
- A colorful terminal interface with gradient borders
- Project detection for your current directory
- Command categories displayed horizontally
- An input prompt ready for commands

## Usage Instructions

### Starting the Interface

**Method 1: Direct Launch**
```bash
python terminal_interface.py
```

**Method 2: Quick Launcher**
```bash
python launch.py
```

### Core Commands

#### Project Management
- `project list` - Display all projects
- `project create <name>` - Create a new project
- `project switch <name>` - Switch to a project
- `project info` - Show current project details

#### Task Management
- `task list` - Show all tasks
- `task create <title>` - Create a new task
- `task update <id> <status>` - Update task status
- `task priority <id> <level>` - Set task priority
- `task delete <id>` - Delete a task

#### Message System
- `message send <content>` - Send a message
- `message history` - View message history
- `message export` - Export messages to file
- `message clear` - Clear message history

#### Chat & Memory
- `chat add <user|assistant|system> <text>` - Append a chat message
- `chat prompt` - Build a token-aware prompt from recent turns
- `chat export` - Export universal memory to `.terminal_data/exports/memory_universal.jsonl`
- `chat snapshot` - Append daily long-term memory snapshot to `.terminal_data/memory/YYYY-MM-DD.jsonl`
- `chat clear` - Clear the durable chat transcript (`.terminal_data/messages/chat.jsonl`)
- `remember <text>` - Store intent/instructions to `.terminal_data/memory/remembered.json` and export last text to `.terminal_data/exports/remember_last.txt` for AI editors
- `remember` - Perform all saved remembered entries sequentially (commands are executed, plain text is pushed to chat)
- `remember list` - Show indexed list of saved remembered entries
- `remember remove <n>` - Remove a remembered entry by index
- `remember purge executed` - Remove all executed remembered entries
- `perform` - Auto-execute last `remember` text when it is a command or push it to chat/messages so AI editors can continue without re-asking
- `perform <n>` - Execute the nth remembered entry directly (from `remember list`)
- `perform range <a> <b>` - Execute a range of remembered entries with guardrails
- `perform clear` - Clear only the last remembered entry
- `memory clear` - Wipe remembered entries, memory snapshots, and `context_memory.json`
- `memory status` - Display remembered totals, executed/pending counts, and last preview

#### File Operations
- `@path/to/file` - View file information
- `@path/to/directory` - List directory contents
- `ls` - List current directory
- `cd <path>` - Change directory
- `pwd` - Show current directory

#### System Commands
- `help` - Show detailed help information
- `status` - Display system status
- `clear` - Clear the screen
- `config` - Access configuration settings
- `backup` - Create data backup
- `exit` - Exit the interface

### Advanced Features

#### Session Management
- Sessions are automatically saved and restored
- Use `back` to navigate through command history
- Session data includes projects, tasks, and messages

#### Context Intelligence
- The system automatically compresses old context data and auto-summarizes every 5 chat turns
- Important information is preserved across sessions
- Context switching optimizes memory usage

#### Token-Aware Prompts
- `ContextManager.build_prompt(max_tokens, reserved_reply_tokens, system_header)` assembles high-relevance context within a token budget
- `ChatTranscriptManager.build_chat_prompt(...)` builds prompts from chat turns under a token budget

#### Themes and Customization
- Multiple color themes available
- Customizable display options
- Performance tuning settings

### Usage Examples

**Creating and Managing a Project:**
```bash
# Create a new project
project create "My Web App"

# Add some tasks
task create "Set up database"
task create "Create user authentication"
task create "Design homepage"

# Update task status
task update task_001 in_progress

# Check project status
project info
```

**File Operations:**
```bash
# View file information
@src/main.py

# List directory contents
@src/

# Navigate directories
cd src
ls
pwd
```

**Message Management:**
```bash
# Send messages for documentation
message send "Completed user authentication module"
message send "Need to review database schema"

# View history
message history

# Export for sharing
message export
```

**Auto store-and-curate flow:**
```bash
# Add entries
remember Create a React component Button with primary/secondary variants
remember task create "Write tests for Button"

# Inspect and curate
remember list
remember remove 1
remember purge executed

# Execute all pending
remember

# Execute a specific entry or range
perform 2
perform range 1 3

# Status and clearing
memory status
remember clear
perform clear
memory clear
```
Behavior:
- Executed items are marked with `executed=true`, `executed_at`, and a `result` stub; use `remember purge executed` to clean them up.
- Batch operations respect `max_batch_perform` unless `assume_yes` is enabled.
```

 Important Usage Notes

1. Data Persistence: All data is automatically saved. Use `backup` for additional safety.

2. File Paths: Use forward slashes (/) for paths on all platforms.

3. Command History: Use arrow keys to navigate through command history.

4. Interruption: Press Ctrl+C to interrupt commands, type `exit` to quit properly.

5. Performance: Large projects may take longer to load. Use `performance` command for optimization.

6. Themes: Switch themes using `theme <name>` command for better visibility.


```

```
## File Structure

AI-Terminal-Workflow/
├── 📄 Core Files
│   ├── terminal_interface.py    # Main terminal interface with UI and command processing
│   ├── launch.py               # Simple launcher script
│   └── README.md               # Project documentation
│
├── 🧠 Intelligence Modules
│   ├── context_manager.py      # Context compression and memory management
│   ├── session_bridge.py       # Session persistence and recovery
│   ├── project_inference.py    # Intelligent project detection and analysis
│   └── terminal_persistence.py # Data storage and retrieval engine
│
├── 🔧 Utility Modules
│   ├── file_manager.py         # File operations and management
│   ├── file_structure_mapper.py # Directory structure analysis
│   ├── high_performance_file_system.py # Optimized file operations
│   ├── progress_tracker.py     # Task and progress tracking
│   └── startup_hook.py         # System initialization hooks
│
├── 📊 Data Directory (.terminal_data/)
│   ├── sessions/               # Session storage and backups
│   ├── messages/               # Chat transcripts (chat.jsonl) and message history
│   ├── projects/               # Project configuration and data
│   ├── backups/               # Automatic data backups
│   ├── exports/               # Universal memory exports (memory_universal.jsonl)
│   └── memory/                # Daily long-term memory snapshots (YYYY-MM-DD.jsonl)
│
├── ⚙️ Configuration Files
│   ├── project_state.json      # Current project state
│   ├── todo_improved.json      # Enhanced task management data
│   └── .project_context.json   # Project context cache
│
└── 📝 Documentation
    ├── TODO.md                 # Development guidelines and tasks
    └── tasks/                  # Task-specific documentation
```

### Key File Descriptions

- **terminal_interface.py**: The heart of the system, containing the main interface, command processing, and UI rendering
- **context_manager.py**: Handles intelligent context compression and memory optimization
- **chat_manager.py**: Stores chat messages (JSONL), auto-summarizes every N turns, builds token-aware chat prompts
- **session_bridge.py**: Manages session persistence and seamless context restoration
- **project_inference.py**: Automatically detects project types and provides intelligent suggestions
- **terminal_persistence.py**: Handles all data storage, retrieval, and backup operations

## Contributing Guidelines

### How to Contribute

We welcome contributions from developers of all skill levels! Here's how you can help improve the AI Terminal Workflow:

#### Getting Started
1. **Fork the Repository**: Create your own copy of the project
2. **Set Up Development Environment**: Follow the installation guide
3. **Explore the Codebase**: Familiarize yourself with the file structure
4. **Check Issues**: Look for open issues or feature requests

#### Development Process

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Follow Coding Standards**
   - Use Python 3.8+ features
   - Follow PEP 8 style guidelines
   - Add type hints where appropriate
   - Include docstrings for functions and classes
   - Write clear, descriptive commit messages

3. **Testing Guidelines**
   - Test your changes thoroughly
   - Ensure backward compatibility
   - Verify that existing features still work
   - Test on multiple platforms if possible

4. **Code Review Process**
   - Keep changes focused and atomic
   - Provide clear descriptions of changes
   - Be responsive to feedback
   - Update documentation as needed

#### Types of Contributions

**🐛 Bug Fixes**
- Report bugs with detailed reproduction steps
- Include system information and error messages
- Provide minimal test cases when possible

**✨ New Features**
- Discuss major features before implementation
- Ensure features align with project goals
- Include comprehensive documentation
- Add appropriate error handling

**📚 Documentation**
- Improve existing documentation
- Add examples and use cases
- Fix typos and clarify instructions
- Translate documentation to other languages

**🎨 UI/UX Improvements**
- Enhance terminal interface design
- Improve color schemes and themes
- Optimize user experience flows
- Add accessibility features

#### Contribution Checklist

- [ ] Code follows project style guidelines
- [ ] Changes are well-documented
- [ ] All tests pass
- [ ] No breaking changes (or properly documented)
- [ ] Security considerations addressed
- [ ] Performance impact evaluated
- [ ] Cross-platform compatibility verified

#### Getting Help

- **Questions**: Open an issue with the "question" label
- **Discussions**: Use GitHub Discussions for broader topics
- **Documentation**: Check existing docs and README files
- **Code Review**: Request reviews from maintainers

### Development Guidelines

1. **Security First**: Never commit sensitive information
2. **Simplicity**: Keep changes minimal and focused
3. **Compatibility**: Maintain backward compatibility
4. **Performance**: Consider memory and speed implications
5. **Documentation**: Update docs with code changes
6. **Testing**: Verify changes don't break existing functionality

## License Information

### MIT License

Copyright (c) 2024 AI Terminal Workflow Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

### Third-Party Components

This project uses only Python standard library components and does not include any third-party dependencies that require additional licensing considerations.

### Usage Rights

- ✅ **Commercial Use**: You may use this software for commercial purposes
- ✅ **Modification**: You may modify the software to suit your needs
- ✅ **Distribution**: You may distribute copies of the software
- ✅ **Private Use**: You may use the software for private purposes
- ✅ **Patent Use**: This license provides an express grant of patent rights from contributors

### Responsibilities

- 📄 **License Notice**: Include the license notice in all copies
- 🔒 **No Warranty**: The software is provided "as is" without warranty
- 🛡️ **Liability**: Authors are not liable for any damages

### Contributing

By contributing to this project, you agree that your contributions will be licensed under the same MIT License.

---

## Quick Start

1. **Install Python 3.8+**
2. **Download the project files**
3. **Run**: `python terminal_interface.py`
4. **Explore**: Type `help` for available commands
5. **Create**: Start with `project create "My Project"`

**Happy coding! 🚀**

---

*For more information, issues, or contributions, please visit the project repository.*
