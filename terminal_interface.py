"""
Robust Terminal Interface for AI Terminal Workflow
Comprehensive interactive terminal with advanced features
"""

import os
import sys
import json
import time
import uuid
import shutil
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from terminal_persistence import get_terminal_engine
    from session_bridge import SessionBridge
    from context_manager import ContextManager, get_context_manager
    from chat_manager import get_chat_manager
    from ai_service import get_ai_manager
    # Import our new simple AI manager
    from simple_ai_manager import get_simple_ai_manager
    # Import building agents
    from building_agent import get_building_agent
    from advanced_building_agent import get_advanced_building_agent
    # Import enhanced AI provider
    from enhanced_ai_provider import get_enhanced_ai_provider
except ImportError as e:
    print(f"Warning: Could not import workflow components: {e}")
    print("Some features may be limited.")
    ProjectInferenceEngine = None
    get_ai_manager = None
    get_simple_ai_manager = None
    get_building_agent = None
    get_advanced_building_agent = None
    get_enhanced_ai_provider = None

class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    ITALIC = '\033[3m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    STRIKETHROUGH = '\033[9m'
    
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BLACK = '\033[90m'
    
    PRIMARY_GRADIENT_TOP = '\033[38;2;64;224;255m'
    PRIMARY_GRADIENT_MID = '\033[38;2;100;149;237m'
    PRIMARY_GRADIENT_BOT = '\033[38;2;138;43;226m'
    
    ACCENT_GOLD = '\033[38;2;255;215;0m'
    ACCENT_SILVER = '\033[38;2;192;192;192m'
    ACCENT_PLATINUM = '\033[38;2;229;228;226m'
    
    NEON_CYAN = '\033[38;2;0;255;255m'
    NEON_PURPLE = '\033[38;2;138;43;226m'
    NEON_BLUE = '\033[38;2;0;191;255m'
    NEON_GREEN = '\033[38;2;57;255;20m'
    NEON_PINK = '\033[38;2;255;20;147m'
    NEON_ORANGE = '\033[38;2;255;165;0m'
    
    DEEP_PURPLE = '\033[38;2;75;0;130m'
    DEEP_BLUE = '\033[38;2;25;25;112m'
    DEEP_TEAL = '\033[38;2;0;128;128m'
    
    SUCCESS_GREEN = '\033[38;2;46;204;113m'
    WARNING_AMBER = '\033[38;2;241;196;15m'
    ERROR_RED = '\033[38;2;231;76;60m'
    INFO_BLUE = '\033[38;2;52;152;219m'
    
    BG_BLACK = '\033[40m'
    BG_DARK = '\033[48;2;20;20;30m'
    BG_DARKER = '\033[48;2;15;15;25m'
    BG_GRADIENT = '\033[48;2;25;25;40m'
    BG_ACCENT = '\033[48;2;35;35;50m'
    
    GLOW_EFFECT = '\033[38;2;135;206;250m'
    SHADOW_EFFECT = '\033[38;2;20;20;20m'
    HIGHLIGHT = '\033[48;2;255;255;0;38;2;0;0;0m'
    
    BORDER_STYLE = {
        'double': ('╔', '╗', '╚', '╝', '║', '═'),
        'single': ('┌', '┐', '└', '┘', '│', '─'),
        'rounded': ('╭', '╮', '╰', '╯', '│', '─'),
        'thick': ('┏', '┓', '┗', '┛', '┃', '━'),
        'premium': ('╔', '╗', '╚', '╝', '║', '═', '╤', '╧', '╠', '╣')
    }
    
    @staticmethod
    def rgb(r: int, g: int, b: int) -> str:
        """Create custom RGB color."""
        return f'\033[38;2;{r};{g};{b}m'
    
    @staticmethod
    def bg_rgb(r: int, g: int, b: int) -> str:
        """Create custom RGB background color."""
        return f'\033[48;2;{r};{g};{b}m'
    
    @staticmethod
    def gradient_text(text: str, start_color: tuple, end_color: tuple) -> str:
        """Create gradient text effect."""
        if len(text) <= 1:
            return f'{Colors.rgb(*start_color)}{text}{Colors.RESET}'
        
        result = ""
        for i, char in enumerate(text):
            ratio = i / (len(text) - 1)
            r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
            result += f'{Colors.rgb(r, g, b)}{char}'
        return result + Colors.RESET

def get_display_length(text: str) -> int:
    """Calculate the actual display length of text without ANSI color codes."""
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    clean_text = ansi_escape.sub('', text)
    return len(clean_text)

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"

@dataclass
class Task:
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: int
    created_at: str
    updated_at: str
    project_id: Optional[str] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class Message:
    id: str
    content: str
    timestamp: str
    message_type: str
    project_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class Project:
    id: str
    name: str
    description: str
    path: str
    created_at: str
    last_accessed: str
    settings: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.settings is None:
            self.settings = {}

class RobustTerminalInterface:
    """Advanced terminal interface with comprehensive features."""
    
    def __init__(self):
        self.project_root = Path(os.getcwd())
        self.data_dir = self.project_root / ".terminal_data"
        self.config_file = self.project_root / "todo_improved.json"
        self.state_file = self.project_root / "project_state.json"
        
        self.running = True
        self.current_project = None
        self.current_session_id = None
        self.command_history = []
        self.message_history = []
        self.tasks = {}
        self.projects = {}
        self.sessions = {}
        
        self.theme = "default"
        self.show_timestamps = True
        self.auto_save = True
        self.token_limit = 4000
        self.session_cleared = False
        self.auto_perform_on_start = False
        self.verbose = False
        self.assume_yes = False
        self.max_batch_perform = 20
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        # Initialize state history
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10

        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        # Initialize state history
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        # Initialize state history
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")

        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Simple AI service initialization failed: {e}", "warning")
        
        # Building agent integration (to be removed)
        self.building_agent = None
        self.advanced_building_agent = None
        if get_building_agent:
            try:
                self.building_agent = get_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Building agent initialization failed: {e}", "warning")
        
        if get_advanced_building_agent:
            try:
                self.advanced_building_agent = get_advanced_building_agent(str(self.project_root))
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        self.state_history = []
        self.max_history_size = 10
        
        # Remembered instructions persistence
        self.memory_dir = self.data_dir / "memory"
        self.exports_dir = self.data_dir / "exports"
        self.remember_file = self.memory_dir / "remembered.json"
        
        # Editor signaling
        self.editor_events_file = self.exports_dir / "editor_events.jsonl"
        self._editor_signal_version = 0
        
        # Minimal command registry (hook for future full refactor)
        self.command_registry = {}
        
        # AI service integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: AI service initialization failed: {e}", "warning")
        
        # Simple AI manager integration (new)
        self.simple_ai_manager = None
        if get_simple_ai_manager:
            try:
                self.simple_ai_manager = get_simple_ai_manager()
            except Exception as e:
                self.log_message(f"Warning: Advanced building agent initialization failed: {e}", "warning")
        
        # Enhanced AI provider
        self.enhanced_ai_provider = None
        if get_enhanced_ai_provider:
            try:
                self.enhanced_ai_provider = get_enhanced_ai_provider()
            except Exception as e:
                self.log_message(f"Warning: Enhanced AI provider initialization failed: {e}", "warning")
        
        self._register_commands()
        
        self.initialize_system()
        self.load_persistent_data()
        
    def initialize_system(self) -> None:
        """Initialize the terminal system and create necessary directories."""
        try:
            self.data_dir.mkdir(exist_ok=True)
            (self.data_dir / "sessions").mkdir(exist_ok=True)
            (self.data_dir / "messages").mkdir(exist_ok=True)
            (self.data_dir / "projects").mkdir(exist_ok=True)
            (self.data_dir / "backups").mkdir(exist_ok=True)
            # Ensure memory and exports dirs exist for remember/perform flow
            (self.data_dir / "memory").mkdir(exist_ok=True)
            (self.data_dir / "exports").mkdir(exist_ok=True)
            
            self.current_session_id = f"session_{uuid.uuid4().hex[:8]}_{int(time.time())}"
            
            try:
                self.session_bridge = SessionBridge()
                self.context_manager = ContextManager()
                self.ctx = get_context_manager()
                self.chat = get_chat_manager()
            except Exception as e:
                self.log_message(f"Warning: Limited workflow integration: {e}", "warning")
                
        except Exception as e:
            self.log_message(f"System initialization error: {e}", "error")
    
    def load_persistent_data(self) -> None:
        """Load all persistent data from storage."""
        try:
            projects_file = self.data_dir / "projects" / "projects.json"
            if projects_file.exists():
                with open(projects_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.projects = {pid: Project(**pdata) for pid, pdata in data.items()}
            
            tasks_file = self.data_dir / "tasks.json"
            if tasks_file.exists():
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for tid, tdata in data.items():
                        if 'status' in tdata and isinstance(tdata['status'], str):
                            tdata['status'] = TaskStatus(tdata['status'])
                        self.tasks[tid] = Task(**tdata)
            
            messages_file = self.data_dir / "messages" / "history.json"
            if messages_file.exists():
                with open(messages_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.message_history = [Message(**mdata) for mdata in data]
            
            self.detect_current_project()
            
        except Exception as e:
            self.log_message(f"Data loading error: {e}", "error")
    
    def save_persistent_data(self) -> None:
        """Save all data to persistent storage."""
        try:
            projects_file = self.data_dir / "projects" / "projects.json"
            with open(projects_file, 'w', encoding='utf-8') as f:
                json.dump({pid: asdict(proj) for pid, proj in self.projects.items()}, f, indent=2)
            
            tasks_file = self.data_dir / "tasks.json"
            with open(tasks_file, 'w', encoding='utf-8') as f:
                tasks_data = {}
                for tid, task in self.tasks.items():
                    task_dict = asdict(task)
                    task_dict['status'] = task.status.value
                    tasks_data[tid] = task_dict
                json.dump(tasks_data, f, indent=2)
            
            messages_file = self.data_dir / "messages" / "history.json"
            with open(messages_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(msg) for msg in self.message_history], f, indent=2)
            
            self.save_session()
            
        except Exception as e:
            self.log_message(f"Data saving error: {e}", "error")
    
    def detect_current_project(self) -> None:
        """Detect or create current project based on working directory."""
        project_name = self.project_root.name
        project_id = f"proj_{uuid.uuid4().hex[:8]}"
        
        for pid, proj in self.projects.items():
            if Path(proj.path) == self.project_root:
                self.current_project = pid
                proj.last_accessed = datetime.now().isoformat()
                return
        
        new_project = Project(
            id=project_id,
            name=project_name,
            description=f"Auto-detected project in {self.project_root}",
            path=str(self.project_root),
            created_at=datetime.now().isoformat(),
            last_accessed=datetime.now().isoformat()
        )
        
        self.projects[project_id] = new_project
        self.current_project = project_id
    
    def log_message(self, content: str, msg_type: str = "info", save: bool = True, auto_persist: bool = False) -> None:
        """Log a message with timestamp and optional persistence."""
        message = Message(
            id=f"msg_{uuid.uuid4().hex[:8]}",
            content=content,
            timestamp=datetime.now().isoformat(),
            message_type=msg_type,
            project_id=self.current_project,
            session_id=self.current_session_id
        )
        
        if save:
            self.message_history.append(message)
            
            if len(self.message_history) > 1000:
                self.message_history = self.message_history[-800:]
            
            if auto_persist or msg_type in ["ai_message", "user_to_ai", "error"]:
                self.save_persistent_data()
    
    def format_text(self, text: str, color: str = None, bold: bool = False, italic: bool = False) -> str:
        """Format text with colors and styles."""
        formatted = text
        
        if bold:
            formatted = f"{Colors.BOLD}{formatted}"
        if italic:
            formatted = f"{Colors.ITALIC}{formatted}"
        if color:
            color_code = getattr(Colors, color.upper(), Colors.WHITE)
            formatted = f"{color_code}{formatted}"
        
        return f"{formatted}{Colors.RESET}"
    
    def display_header(self) -> None:
        """Display enhanced main interface with improved branding and visual hierarchy."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        gradient_top = Colors.PRIMARY_GRADIENT_TOP
        gradient_mid = Colors.PRIMARY_GRADIENT_MID
        gradient_bot = Colors.PRIMARY_GRADIENT_BOT
        accent_gold = Colors.ACCENT_GOLD
        accent_silver = Colors.ACCENT_SILVER
        neon_cyan = Colors.NEON_CYAN
        deep_purple = Colors.DEEP_PURPLE
        cyan = Colors.CYAN
        blue = Colors.BLUE
        white = Colors.WHITE
        dim = Colors.DIM
        yellow = Colors.YELLOW
        green = Colors.SUCCESS_GREEN
        
        print(f"\n{gradient_top}╔{'═'*100}╗{Colors.RESET}")
        print(f"{gradient_top}║{Colors.RESET}{' '*100}")
        
        brand_title = "🚀 FZX DEVELOPMENT TERMINAL"
        brand_subtitle = "Advanced AI-Powered Workspace Management"
        
        brand_title_display_len = get_display_length(brand_title)
        brand_title_padding = (98 - brand_title_display_len) // 2
        brand_title_spacing = 98 - brand_title_display_len - brand_title_padding
        
        print(f"{gradient_top}║{Colors.RESET}{' '*brand_title_padding}{Colors.BOLD}{accent_gold}{brand_title}{Colors.RESET}")
        
        brand_subtitle_display_len = get_display_length(brand_subtitle)
        brand_subtitle_padding = (98 - brand_subtitle_display_len) // 2
        brand_subtitle_spacing = 98 - brand_subtitle_display_len - brand_subtitle_padding
        
        print(f"{gradient_top}║{Colors.RESET}{' '*brand_subtitle_padding}{Colors.DIM}{accent_silver}{brand_subtitle}{Colors.RESET}")
        print(f"{gradient_top}║{Colors.RESET}{' '*100}")
        print(f"{gradient_top}╚{'═'*100}╝{Colors.RESET}")
        
        print(f"\n{gradient_mid}╔{'═'*100}╗{Colors.RESET}")
        
        nav_header = "📋 MAIN NAVIGATION MENU"
        nav_header_display_len = get_display_length(nav_header)
        nav_header_padding = (98 - nav_header_display_len) // 2
        nav_header_spacing = 98 - nav_header_display_len - nav_header_padding
        
        print(f"{gradient_mid}║{Colors.RESET}{' '*nav_header_padding}{Colors.BOLD}{accent_gold}{nav_header}{Colors.RESET}")
        print(f"{gradient_mid}╠{'═'*100}╣{Colors.RESET}")
        
        nav_categories = [
            ("🚀", "PROJECTS", "project list | create | switch | info", accent_gold),
            ("✅", "TASKS", "task list | create | update | priority", neon_cyan),
            ("🔨", "BUILD", "build describe | setup-ai | analyze | status", accent_gold),
            ("🤖", "AI ASSISTANT", "ai config setup | ai chat | ai help", gradient_bot),
            ("⚙️", "SETTINGS", "config | theme | backup | performance", accent_silver),
            ("📚", "HELP", "help | status | clear", green)
        ]
        
        for icon, category, commands, color in nav_categories:
            category_content = f" {icon} {Colors.BOLD}{color}{category}{Colors.RESET}"
            category_display_len = get_display_length(category_content)
            category_spacing = max(2, 15 - category_display_len)
            
            commands_content = f"{Colors.DIM}{commands}{Colors.RESET}"
            
            full_content = f"{category_content}{' '*category_spacing}{commands_content}"
            full_display_len = get_display_length(full_content)
            end_spacing = max(1, 98 - full_display_len)
            
            print(f"{gradient_mid}║{Colors.RESET}{category_content}{' '*category_spacing}{commands_content}")
        
        print(f"{gradient_mid}║{Colors.RESET}{' '*98}")
        
        tip_content = f" {Colors.DIM}{accent_silver}💡 Quick Access:{Colors.RESET} {Colors.DIM}Type any command above or use 'help' for detailed documentation{Colors.RESET}"
        tip_display_len = get_display_length(tip_content)
        tip_spacing = max(1, 98 - tip_display_len)
        print(f"{gradient_mid}║{Colors.RESET}{tip_content}")
        print(f"{gradient_mid}╚{'═'*100}╝{Colors.RESET}")
        
        print(f"\n{gradient_bot}╔{'═'*100}╗{Colors.RESET}")
        
        dashboard_header = "📊 WORKSPACE DASHBOARD"
        dashboard_header_display_len = get_display_length(dashboard_header)
        dashboard_header_padding = (98 - dashboard_header_display_len) // 2
        dashboard_header_spacing = 98 - dashboard_header_display_len - dashboard_header_padding
        
        print(f"{gradient_bot}║{Colors.RESET}{' '*dashboard_header_padding}{Colors.BOLD}{accent_gold}{dashboard_header}{Colors.RESET}")
        print(f"{gradient_bot}╠{'═'*100}╣{Colors.RESET}")
        
        current_dir = os.getcwd()
        dir_name = os.path.basename(current_dir)
        
        try:
            import glob
            py_files = len(glob.glob("*.py"))
            json_files = len(glob.glob("*.json"))
            total_files = len([f for f in os.listdir('.') if os.path.isfile(f)])
            directories = len([d for d in os.listdir('.') if os.path.isdir(d)])
            
            has_git = "✅" if os.path.exists('.git') else "❌"
            has_venv = "✅" if (os.path.exists('venv') or os.path.exists('.venv')) else "❌"
            has_requirements = "✅" if os.path.exists('requirements.txt') else "❌"
            
        except Exception:
            py_files = json_files = total_files = directories = 0
            has_git = has_venv = has_requirements = "❌"
        
        dashboard_metrics = [
            ("📁", "Current Directory", [f"{dir_name}"], accent_gold),
            ("📊", "Project Stats", [f"{py_files} Python files", f"{json_files} JSON files", f"{total_files} Total files"], neon_cyan),
            ("🔧", "Development Tools", [f"Git Repository: {has_git}", f"Virtual Environment: {has_venv}", f"Requirements File: {has_requirements}"], gradient_mid),
            ("💾", "Active Sessions", [f"{len(self.sessions)} sessions", f"{len(self.tasks)} tasks", f"{len(self.projects)} projects"], accent_silver)
        ]
        
        for icon, metric_name, metric_values, color in dashboard_metrics:
            metric_header = f" {icon} {Colors.BOLD}{color}{metric_name}:{Colors.RESET}"
            metric_header_display_len = get_display_length(metric_header)
            metric_header_spacing = max(1, 98 - metric_header_display_len)
            print(f"{gradient_bot}║{Colors.RESET}{metric_header}")
            
            for value in metric_values:
                value_content = f"    {Colors.DIM}{value}{Colors.RESET}"
                value_display_len = get_display_length(value_content)
                
                if value_display_len > 96:
                    max_chars = 93
                    truncated_value = value[:max_chars] + "..."
                    value_content = f"    {Colors.DIM}{truncated_value}{Colors.RESET}"
                    value_display_len = get_display_length(value_content)
                
                value_spacing = max(1, 98 - value_display_len)
                print(f"{gradient_bot}║{Colors.RESET}{value_content}")
            
            print(f"{gradient_bot}║{Colors.RESET} {' '*98}")
        
        print(f"{gradient_bot}║{Colors.RESET}{' '*98}")
        
        status_content = f" {Colors.DIM}{green}🟢 System Status:{Colors.RESET} {Colors.DIM}All systems operational | Auto-save: {'ON' if self.auto_save else 'OFF'}{Colors.RESET}"
        status_display_len = get_display_length(status_content)
        status_spacing = max(1, 98 - status_display_len)
        print(f"{gradient_bot}║{Colors.RESET}{status_content}")
        print(f"{gradient_bot}╚{'═'*100}╝{Colors.RESET}")
        
        print(f"\n{gradient_bot}╔{'═'*100}╗{Colors.RESET}")
        
        header_content = f" {accent_gold}▓{Colors.RESET} {Colors.BOLD}📋 SYSTEM OVERVIEW{Colors.RESET}"
        header_display_len = get_display_length(header_content)
        header_spacing = max(1, 98 - header_display_len - 2)
        print(f"{gradient_bot}║{Colors.RESET}{header_content}{' '*header_spacing} {accent_gold}▓{Colors.RESET}")
        
        print(f"{gradient_bot}╠{'═'*100}╣{Colors.RESET}")
        
        desc_content = f" {Colors.DIM}{neon_cyan}▶{Colors.RESET} {Colors.DIM}Comprehensive workflow management with integrated capabilities{Colors.RESET}"
        desc_display_len = get_display_length(desc_content)
        desc_spacing = max(1, 98 - desc_display_len)
        print(f"{gradient_bot}║{Colors.RESET}{desc_content}")
        
        print(f"{gradient_bot}║{Colors.RESET} {' '*98}")
        
        features_line = f" 🎯 {accent_gold}Project{Colors.RESET} {Colors.DIM}• ✅ Task Tracking • 🤖 AI Assistant • 💾 Session Persistence{Colors.RESET}"
        print(f"{gradient_bot}║{Colors.RESET}{features_line}")
        
        print(f"{gradient_bot}║{Colors.RESET} {' '*98}")
        adv_features_content = f" {Colors.DIM}{accent_silver}◆ Advanced Features:{Colors.RESET} Auto-save, Context awareness, Cross-platform"
        adv_features_display_len = get_display_length(adv_features_content)
        adv_features_spacing = max(1, 98 - adv_features_display_len)
        print(f"{gradient_bot}║{Colors.RESET}{adv_features_content}")
        print(f"{gradient_bot}╚{'═'*100}╝{Colors.RESET}")
        
        print(f"\n{gradient_top}╔{'═'*100}╗{Colors.RESET}")
        
        qs_header_content = f" {accent_gold}▓{Colors.RESET} {Colors.BOLD}⚡ QUICK START COMMANDS{Colors.RESET}"
        qs_header_display_len = get_display_length(qs_header_content)
        qs_header_spacing = max(1, 98 - qs_header_display_len - 2)
        print(f"{gradient_top}║{Colors.RESET}{qs_header_content}{' '*qs_header_spacing} {accent_gold}▓{Colors.RESET}")
        
        print(f"{gradient_top}╠{'═'*100}╣{Colors.RESET}")
        
        qs_desc_content = f" {Colors.DIM}{neon_cyan}▶{Colors.RESET} {Colors.DIM}Essential commands for your development workflow{Colors.RESET}"
        qs_desc_display_len = get_display_length(qs_desc_content)
        qs_desc_spacing = max(1, 98 - qs_desc_display_len)
        print(f"{gradient_top}║{Colors.RESET}{qs_desc_content}")
        
        print(f"{gradient_top}║{Colors.RESET} {' '*98}")
        
        quick_commands = [
            ("🚀", "project create <name>", "Initialize a new project workspace with intelligent setup"),
            ("✅", "task create <title>", "Add development tasks with priority tracking and progress monitoring"),
            ("🔨", "build describe '<description>'", "Generate any project from natural language with AI"),
            ("🤖", "build setup-ai openrouter", "Setup OpenRouter AI with 100+ models for enhanced generation"),
            ("💬", "ai chat <message>", "Chat with AI using your project context for development help"),
            ("📚", "help", "View complete command reference, documentation, and advanced features")
        ]
        
        for icon, cmd, desc in quick_commands:
            base_content = f" {icon} {accent_gold}{cmd}{Colors.RESET}"
            base_display_len = get_display_length(base_content)
            spacing = max(2, 28 - base_display_len)
            
            desc_formatted = f"{Colors.DIM}{desc}{Colors.RESET}"
            
            full_content = f"{base_content}{' '*spacing}{desc_formatted}"
            full_display_len = get_display_length(full_content)
            end_spacing = max(1, 98 - full_display_len)
            
            print(f"{gradient_top}║{Colors.RESET}{base_content}{' '*spacing}{desc_formatted}")
        
        print(f"{gradient_top}║{Colors.RESET} {' '*98}")
        pro_tip_content = f" {Colors.DIM}{accent_silver}💡 Pro Tip:{Colors.RESET} {Colors.DIM}Use tab completion for faster navigation{Colors.RESET}"
        pro_tip_display_len = get_display_length(pro_tip_content)
        pro_tip_spacing = max(1, 98 - pro_tip_display_len)
        print(f"{gradient_top}║{Colors.RESET}{pro_tip_content}")
        print(f"{gradient_top}╚{'═'*100}╝{Colors.RESET}")
        
        current_dir = os.getcwd()
        dir_name = os.path.basename(current_dir)
        
        try:
            import glob
            py_files = len(glob.glob("*.py"))
            json_files = len(glob.glob("*.json"))
            total_files = len([f for f in os.listdir('.') if os.path.isfile(f)])
            directories = len([d for d in os.listdir('.') if os.path.isdir(d)])
            
            has_git = os.path.exists('.git')
            has_venv = os.path.exists('venv') or os.path.exists('.venv')
            has_requirements = os.path.exists('requirements.txt')
            
            session_files = 0
            if os.path.exists('.terminal_data/sessions'):
                session_files = len([f for f in os.listdir('.terminal_data/sessions') if f.endswith('.json')])
                
        except Exception:
            py_files = json_files = total_files = directories = session_files = 0
            has_git = has_venv = has_requirements = False
        
        print(f"\n{gradient_mid}╔{'═'*100}╗{Colors.RESET}")
        
        ws_header_content = f" {accent_gold}▓{Colors.RESET} {Colors.BOLD}📊 WORKSPACE STATUS{Colors.RESET}"
        ws_header_display_len = get_display_length(ws_header_content)
        ws_header_spacing = max(1, 98 - ws_header_display_len - 2)
        print(f"{gradient_mid}║{Colors.RESET}{ws_header_content}{' '*ws_header_spacing} {accent_gold}▓{Colors.RESET}")
        
        print(f"{gradient_mid}╠{'═'*100}╣{Colors.RESET}")
        
        ws_desc_content = f" {Colors.DIM}{neon_cyan}▶{Colors.RESET} {Colors.DIM}Current workspace analysis and configuration overview{Colors.RESET}"
        ws_desc_display_len = get_display_length(ws_desc_content)
        ws_desc_spacing = max(1, 98 - ws_desc_display_len)
        print(f"{gradient_mid}║{Colors.RESET}{ws_desc_content}")
        
        print(f"{gradient_mid}║{Colors.RESET} {' '*98}")
        
        dir_info_content = f" {accent_silver}📁 Directory Info:{Colors.RESET}"
        dir_info_display_len = get_display_length(dir_info_content)
        dir_info_spacing = max(1, 98 - dir_info_display_len)
        print(f"{gradient_mid}║{Colors.RESET}{dir_info_content}")
        
        name_content = f"    {Colors.BOLD}Name:{Colors.RESET} {accent_gold}{dir_name}{Colors.RESET}"
        name_display_len = get_display_length(name_content)
        name_spacing = max(1, 98 - name_display_len)
        print(f"{gradient_mid}║{Colors.RESET}{name_content}")
        
        path_display = current_dir if len(current_dir) <= 71 else f"...{current_dir[-68:]}"
        path_content = f"    {Colors.BOLD}Path:{Colors.RESET} {Colors.DIM}{path_display}{Colors.RESET}"
        path_display_len = get_display_length(path_content)
        path_spacing = max(1, 98 - path_display_len)
        print(f"{gradient_mid}║{Colors.RESET}{path_content}")
        print(f"{gradient_mid}║{Colors.RESET} {' '*98}")
        
        stats_header_content = f" {accent_silver}📈 Project Statistics:{Colors.RESET}"
        stats_header_display_len = get_display_length(stats_header_content)
        stats_header_spacing = max(1, 98 - stats_header_display_len)
        print(f"{gradient_mid}║{Colors.RESET}{stats_header_content}")
        
        stats_line = f"    🐍 {accent_gold}{py_files}{Colors.RESET} py  📄 {accent_gold}{json_files}{Colors.RESET} json  📂 {accent_gold}{directories}{Colors.RESET} dirs  📋 {accent_gold}{total_files}{Colors.RESET} files  💾 {accent_gold}{session_files}{Colors.RESET} sessions"
        print(f"{gradient_mid}║{Colors.RESET}{stats_line}")
        
        print(f"{gradient_mid}║{Colors.RESET} {' '*98}")
        
        dev_env_content = f" {accent_silver}🔧 Development Environment:{Colors.RESET}"
        dev_env_display_len = get_display_length(dev_env_content)
        dev_env_spacing = max(1, 98 - dev_env_display_len)
        print(f"{gradient_mid}║{Colors.RESET}{dev_env_content}")
        
        git_status = f"{Colors.GREEN}●{Colors.RESET} {accent_gold}Git{Colors.RESET}" if has_git else f"{Colors.RED}○{Colors.RESET} {Colors.DIM}Git{Colors.RESET}"
        venv_status = f"{Colors.GREEN}●{Colors.RESET} {accent_gold}VEnv{Colors.RESET}" if has_venv else f"{Colors.RED}○{Colors.RESET} {Colors.DIM}VEnv{Colors.RESET}"
        req_status = f"{Colors.GREEN}●{Colors.RESET} {accent_gold}Requirements{Colors.RESET}" if has_requirements else f"{Colors.RED}○{Colors.RESET} {Colors.DIM}Requirements{Colors.RESET}"
        dev_features_line = f"    {git_status}  {venv_status}  {req_status}"
        print(f"{gradient_mid}║{Colors.RESET}{dev_features_line}")
        
        print(f"{gradient_mid}║{Colors.RESET} {' '*98}")
        
        if not (has_git and has_venv):
            tip_content = f" {Colors.DIM}{neon_cyan}💡 Recommendation: Initialize git and virtual environment{Colors.RESET}"
            tip_display_len = get_display_length(tip_content)
            tip_spacing = max(1, 98 - tip_display_len)
            print(f"{gradient_mid}║{Colors.RESET}{tip_content}")
        else:
            success_content = f" {Colors.BOLD}{green}✨ Excellent! Well-configured development environment detected{Colors.RESET}"
            success_display_len = get_display_length(success_content)
            success_spacing = max(1, 98 - success_display_len)
            print(f"{gradient_mid}║{Colors.RESET}{success_content}")
        
        print(f"{gradient_mid}╚{'═'*100}╝{Colors.RESET}")
    
    def display_help(self) -> None:
        """Display comprehensive help information with modern styling."""
        gradient_top = Colors.PRIMARY_GRADIENT_TOP
        gradient_mid = Colors.PRIMARY_GRADIENT_MID
        gradient_bot = Colors.PRIMARY_GRADIENT_BOT
        
        print(f"\n{gradient_top}╔{'═'*120}╗{Colors.RESET}")
        
        help_header_content = f" {Colors.BOLD}{gradient_mid}📚 COMPREHENSIVE COMMAND REFERENCE{Colors.RESET}"
        help_header_display_len = get_display_length(help_header_content)
        help_header_spacing = max(1, 118 - help_header_display_len)
        print(f"{gradient_top}║{Colors.RESET}{help_header_content}")
        print(f"{gradient_top}╚{'═'*120}╝{Colors.RESET}")
        
        help_sections = {
            "🚀 Project Management": [
                ("project list", "List all projects", "📋"),
                ("project create <name>", "Create new project", "➕"),
                ("project switch <id/name>", "Switch to project", "🔄"),
                ("project info", "Show current project info", "ℹ️"),
                ("project delete <id/name>", "Delete project", "🗑️"),
                ("project rename <id/name> <new_name>", "Rename project", "✏️"),
                ("project settings", "Show project settings", "⚙️"),
                ("project export [format]", "Export projects (json/xml/txt/csv)", "📤"),
                ("project clear exports", "Clear all exported files", "🧹")
            ],
            "🤖 AI Integration": [
                ("ai config setup", "Interactive setup with latest models and real-time validation", "🔧"),
                ("ai config show", "Show current AI configuration with masked key", "👁️"),
                ("ai config test", "Test AI connection with current configuration", "🧪"),
                ("ai config add-key", "Add or replace API key with validation", "🔑"),
                ("ai config edit-key", "Edit current API key with validation", "✏️"),
                ("ai config delete-key", "Remove API key and configuration completely", "🗑️"),
                ("ai chat <message>", "Chat with AI using project context", "💬"),
                ("ai status", "Show detailed AI service and integration status", "📊"),
                ("ai help", "Show comprehensive AI commands help", "❓")
            ],
            "🧠 Chat & Memory": [
                ("chat add <user|assistant|system> <text>", "Append a chat message to durable log", "➕"),
                ("chat prompt", "Build token-aware prompt from recent turns", "🧪"),
                ("chat export", "Export universal memory JSONL for AI editors", "📤"),
                ("chat snapshot", "Append daily long-term memory snapshot", "🧷"),
                ("chat clear", "Clear durable chat transcript (.terminal_data/messages/chat.jsonl)", "🧹"),
                ("remember <text>", "Save instruction; also export to exports/remember_last.txt", "📌"),
                ("remember", "Perform all saved remembered entries sequentially", "⚡"),
                ("remember list", "List saved remembered entries with indexes", "📜"),
                ("remember remove <n>", "Remove a remembered entry by index", "🗑️"),
                ("remember purge executed", "Remove all executed remembered entries", "🧹"),
                ("remember clear", "Clear all remembered entries", "🧹"),
                ("perform", "Auto-execute last remembered entry or push to chat", "🚀"),
                ("perform <n>", "Execute the nth remembered entry directly", "🎯"),
                ("perform range <a> <b>", "Execute a range of remembered entries", "📐"),
                ("perform clear", "Clear only the last remembered entry", "🧹")
            ],
            "✅ Task Management": [
                ("task list", "List all tasks", "📝"),
                ("task create <title>", "Create new task", "➕"),
                ("task update <id> <status>", "Update task status", "🔄"),
                ("task delete <id>", "Delete task", "❌"),
                ("task priority <id> <1-5>", "Set task priority", "⭐"),
                ("task clear", "Clear all tasks", "🧹")
            ],
            "💬 Messaging System": [
                ("message send <content>", "Send message to AI editor", "📨"),
                ("message history", "Show message history", "📜"),
                ("message export <format>", "Export messages (json/xml/txt)", "📤"),
                ("message clear", "Clear message history", "🧹")
            ],
            "🔄 Session Management": [
                ("session save", "Save current session", "💾"),
                ("session restore <id>", "Restore session", "🔄"),
                ("session list", "List saved sessions", "📋"),
                ("session export", "Export session data", "📤"),
                ("session clear", "Clear all sessions", "🧹")
            ],
            "💻 Terminal Operations": [
                ("run <command>", "Execute shell command", "⚡"),
                ("cd <path>", "Change directory", "📁"),
                ("ls / dir", "List directory contents", "📂"),
                ("pwd", "Show current directory", "📍"),
                ("clear", "Clear screen", "🧹"),
                ("clear all", "Clear ALL data - comprehensive system reset", "🗥️")
            ],
            "📁 File Operations": [
                ("@path/to/file", "Direct file access and preview", "📄"),
                ("@./filename", "Access file in current directory", "📝"),
                ("@/absolute/path", "Access file with absolute path", "🗂️"),
                ("@directory/", "List directory contents", "📂")
            ],
            "⚙️ Interface & Settings": [
                ("theme <name>", "Change color theme", "🎨"),
                ("config show", "Show all configuration", "👁️"),
                ("config set <key> <value>", "Set configuration value", "🔧"),
                ("config set auto_perform_on_start <on|off>", "Run remembered entries on startup", "🚀"),
                ("config set verbose <on|off>", "Enable verbose logging", "🗒️"),
                ("config set assume_yes <on|off>", "Skip confirmations for batch actions", "✅"),
                ("config set max_batch_perform <n>", "Limit batch size for perform operations", "📦"),
                ("config set auto_save <on/off>", "Toggle auto-save feature", "💾"),
                ("config reset [project]", "Reset to defaults", "🔄"),
                ("config export [format]", "Export config (json/xml/txt/csv)", "📤"),
                ("config import <file>", "Import configuration", "📥"),
                ("config backup", "Create config backup", "💾"),
                ("config restore <file>", "Restore from backup", "🔄"),
                ("status", "Show system status", "📊"),
                ("performance", "Show performance metrics", "⚡"),
                ("backup create/restore/list/clear", "Backup operations", "🔙"),
                ("back [number]", "Go back to previous state", "⬅️"),
                ("back restore <number>", "Restore specific state", "🔄"),
                ("back clear", "Clear state history", "🧹"),
                ("memory status", "Show memory counters and last entry preview", "🧮"),
                ("memory clear", "Wipe remembered entries, snapshots and context store", "🧹")
            ]
        }
        
        for section_title, commands in help_sections.items():
            print(f"\n{gradient_mid}┌─ {Colors.BOLD}{section_title}{Colors.RESET} {'─'*(91-len(section_title))}┐{Colors.RESET}")
            
            for cmd, desc, icon in commands:
                cmd_formatted = f"{Colors.CYAN}{cmd}{Colors.RESET}"
                spacing = max(1, 30 - len(cmd))
                desc_formatted = f"{Colors.DIM}{desc}{Colors.RESET}"
                
                print(f"{gradient_mid}│{Colors.RESET} {icon} {cmd_formatted}{' '*spacing} {desc_formatted}")
            
            print(f"{gradient_mid}└{'─'*100}┘{Colors.RESET}")
        
        print(f"\n{gradient_bot}┌─ 💡 TIPS & SHORTCUTS {'─'*76}┐{Colors.RESET}")
        tips = [
            ("⌨️", "Use Tab for command completion"),
            ("⛔", "Press Ctrl+C to interrupt running commands"),
            ("📁", "Use @path/to/file for instant file operations"),
            ("🎯", "Interface now uses horizontal layouts for better space efficiency"),
            ("🔍", "Type 'help <command>' for detailed command info")
        ]
        
        for icon, tip in tips:
            print(f"{gradient_bot}│{Colors.RESET} {icon} {Colors.YELLOW}{tip}{Colors.RESET}")
        
        print(f"{gradient_bot}└{'─'*100}┘{Colors.RESET}\n")
    
    def handle_project_command(self, args: List[str]) -> None:
        """Handle project management commands."""
        if not args:
            self.display_help()
            return
        
        subcommand = args[0].lower()
        
        if subcommand == "list":
            print(f"\n{Colors.BOLD}Projects:{Colors.RESET}")
            if not self.projects:
                print("  No projects found")
                return
            
            for pid, proj in self.projects.items():
                current = "*" if pid == self.current_project else " "
                print(f"  {current} {Colors.GREEN}{proj.name}{Colors.RESET} ({pid})")
                print(f"    Path: {proj.path}")
                print(f"    Last accessed: {proj.last_accessed}")
        
        elif subcommand in ["create", "add"] and len(args) > 1:
            project_name = " ".join(args[1:])
            project_id = f"proj_{uuid.uuid4().hex[:8]}"
            
            new_project = Project(
                id=project_id,
                name=project_name,
                description=f"Project: {project_name}",
                path=str(self.project_root),
                created_at=datetime.now().isoformat(),
                last_accessed=datetime.now().isoformat()
            )
            
            self.projects[project_id] = new_project
            self.current_project = project_id
            
            print(f"{Colors.GREEN}Created project: {Colors.BOLD}{project_name}{Colors.RESET} ({project_id}){Colors.RESET}")
            self.log_message(f"Created project: {project_name}")
        
        elif subcommand == "switch" and len(args) > 1:
            target = args[1]
            
            found_project = None
            for pid, proj in self.projects.items():
                if pid == target or proj.name.lower() == target.lower():
                    found_project = pid
                    break
            
            if found_project:
                self.current_project = found_project
                proj = self.projects[found_project]
                proj.last_accessed = datetime.now().isoformat()
                print(f"{Colors.GREEN}Switched to project: {Colors.BOLD}{proj.name}{Colors.RESET}")
                self.log_message(f"Switched to project: {proj.name}")
            else:
                print(f"{Colors.RED}Project not found: {target}{Colors.RESET}")
        
        elif subcommand == "info":
            if self.current_project and self.current_project in self.projects:
                proj = self.projects[self.current_project]
                print(f"\n{Colors.BOLD}Current Project:{Colors.RESET}")
                print(f"  Name: {Colors.GREEN}{proj.name}{Colors.RESET}")
                print(f"  ID: {proj.id}")
                print(f"  Path: {proj.path}")
                print(f"  Created: {proj.created_at}")
                print(f"  Last accessed: {proj.last_accessed}")
                print(f"  Description: {proj.description}")
            else:
                print(f"{Colors.YELLOW}No current project{Colors.RESET}")
        
        elif subcommand == "delete" and len(args) > 1:
            target = args[1]
            found_project = None
            for pid, proj in self.projects.items():
                if pid == target or proj.name.lower() == target.lower():
                    found_project = pid
                    break
            
            if found_project:
                proj_name = self.projects[found_project].name
                del self.projects[found_project]
                if self.current_project == found_project:
                    self.current_project = None
                print(f"{Colors.GREEN}Deleted project: {Colors.BOLD}{proj_name}{Colors.RESET}")
                self.log_message(f"Deleted project: {proj_name}")
            else:
                print(f"{Colors.RED}Project not found: {target}{Colors.RESET}")
        
        elif subcommand == "rename" and len(args) > 2:
            target = args[1]
            new_name = " ".join(args[2:])
            found_project = None
            for pid, proj in self.projects.items():
                if pid == target or proj.name.lower() == target.lower():
                    found_project = pid
                    break
            
            if found_project:
                old_name = self.projects[found_project].name
                self.projects[found_project].name = new_name
                self.projects[found_project].last_accessed = datetime.now().isoformat()
                print(f"{Colors.GREEN}Renamed project from '{old_name}' to '{new_name}'{Colors.RESET}")
                self.log_message(f"Renamed project: {old_name} -> {new_name}")
            else:
                print(f"{Colors.RED}Project not found: {target}{Colors.RESET}")
        
        elif subcommand == "settings":
            if self.current_project and self.current_project in self.projects:
                proj = self.projects[self.current_project]
                print(f"\n{Colors.BOLD}Project Settings: {proj.name}{Colors.RESET}")
                print(f"  Settings: {proj.settings}")
                print(f"\n{Colors.YELLOW}Use 'config set project.<key> <value>' to modify project settings{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}No current project{Colors.RESET}")
        
        elif subcommand == "export":
            if not self.projects:
                print(f"{Colors.YELLOW}No projects to export{Colors.RESET}")
                return
            
            format_type = args[1].lower() if len(args) > 1 else "json"
            
            if format_type not in ["json", "xml", "txt", "csv"]:
                print(f"{Colors.RED}Invalid format: {format_type}. Use: json, xml, txt, csv{Colors.RESET}")
                return
            
            export_file = self.data_dir / "exports" / f"projects_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
            export_file.parent.mkdir(exist_ok=True)
            
            try:
                if format_type == "json":
                    export_data = {pid: asdict(proj) for pid, proj in self.projects.items()}
                    with open(export_file, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, indent=2)
                        
                elif format_type == "xml":
                    with open(export_file, 'w', encoding='utf-8') as f:
                        f.write("<?xml version='1.0' encoding='UTF-8'?>\n<projects>\n")
                        for pid, proj in self.projects.items():
                            f.write(f"  <project id='{pid}'>\n")
                            f.write(f"    <name>{proj.name}</name>\n")
                            f.write(f"    <path>{proj.path}</path>\n")
                            f.write(f"    <created_at>{proj.created_at}</created_at>\n")
                            f.write(f"    <description>{proj.description}</description>\n")
                            if proj.settings:
                                f.write(f"    <settings>\n")
                                for key, value in proj.settings.items():
                                    f.write(f"      <{key}>{value}</{key}>\n")
                                f.write(f"    </settings>\n")
                            f.write(f"  </project>\n")
                        f.write("</projects>\n")
                        
                elif format_type == "txt":
                    with open(export_file, 'w', encoding='utf-8') as f:
                        f.write("PROJECT EXPORT\n")
                        f.write("=" * 50 + "\n\n")
                        for pid, proj in self.projects.items():
                            f.write(f"Project ID: {pid}\n")
                            f.write(f"Name: {proj.name}\n")
                            f.write(f"Path: {proj.path}\n")
                            f.write(f"Created: {proj.created_at}\n")
                            f.write(f"Description: {proj.description}\n")
                            if proj.settings:
                                f.write(f"Settings: {proj.settings}\n")
                            f.write("-" * 30 + "\n\n")
                            
                elif format_type == "csv":
                    with open(export_file, 'w', encoding='utf-8') as f:
                        f.write("ID,Name,Path,Created,Description,Settings\n")
                        for pid, proj in self.projects.items():
                            settings_str = str(proj.settings) if proj.settings else ""
                            f.write(f'"{pid}","{proj.name}","{proj.path}","{proj.created_at}","{proj.description}","{settings_str}"\n')
                
                print(f"{Colors.GREEN}Projects exported to: {export_file}{Colors.RESET}")
                self.log_message(f"Projects exported to {export_file}")
            except Exception as e:
                print(f"{Colors.RED}Export failed: {e}{Colors.RESET}")
        
        elif subcommand == "clear":
            if len(args) > 1 and args[1] == "exports":
                export_dir = self.data_dir / "exports"
                if export_dir.exists():
                    import shutil
                    shutil.rmtree(export_dir)
                    export_dir.mkdir(exist_ok=True)
                    print(f"{Colors.GREEN}All exported files cleared{Colors.RESET}")
                    self.log_message("Cleared all exported files")
                else:
                    print(f"{Colors.YELLOW}No exports directory found{Colors.RESET}")
            else:
                print(f"{Colors.RED}Usage: project clear exports{Colors.RESET}")
        
        else:
            print(f"{Colors.RED}Unknown project command: {subcommand}{Colors.RESET}")
            print(f"Available commands: list, create, switch, info, delete, rename, settings, export, clear")
    
    def handle_task_command(self, args: List[str]) -> None:
        """Handle task management commands."""
        if not args:
            self.display_help()
            return
        
        subcommand = args[0].lower()
        
        if subcommand == "list":
            print(f"\n{Colors.BOLD}Tasks:{Colors.RESET}")
            if not self.tasks:
                print("  No tasks found")
                return
            
            by_status = {}
            for task in self.tasks.values():
                status = task.status.value
                if status not in by_status:
                    by_status[status] = []
                by_status[status].append(task)
            
            for status, tasks in by_status.items():
                status_color = {
                    "pending": Colors.YELLOW,
                    "in_progress": Colors.BLUE,
                    "completed": Colors.GREEN,
                    "blocked": Colors.RED
                }.get(status, Colors.WHITE)
                
                print(f"\n  {status_color}{status.upper()}{Colors.RESET}:")
                for task in sorted(tasks, key=lambda t: t.priority, reverse=True):
                    priority_indicator = "HIGH" if task.priority >= 4 else "MED" if task.priority >= 3 else "LOW"
                    print(f"    {priority_indicator} {task.title} ({task.id})")
                    if task.description:
                        print(f"      {Colors.ITALIC}{task.description}{Colors.RESET}")
        
        elif subcommand in ["create", "add"] and len(args) > 1:
            title = " ".join(args[1:])
            task_id = f"task_{uuid.uuid4().hex[:8]}"
            
            new_task = Task(
                id=task_id,
                title=title,
                description="",
                status=TaskStatus.PENDING,
                priority=3,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                project_id=self.current_project
            )
            
            self.tasks[task_id] = new_task
            print(f"{Colors.GREEN}Created task: {Colors.BOLD}{title}{Colors.RESET} ({task_id})")
            self.log_message(f"Created task: {title}")
        
        elif subcommand == "update" and len(args) >= 3:
            task_id = args[1]
            new_status = args[2].lower()
            
            if task_id in self.tasks:
                try:
                    status_enum = TaskStatus(new_status)
                    self.tasks[task_id].status = status_enum
                    self.tasks[task_id].updated_at = datetime.now().isoformat()
                    
                    print(f"{Colors.GREEN}Updated task {task_id} status to: {Colors.BOLD}{new_status}{Colors.RESET}")
                    self.log_message(f"Updated task {task_id} status to {new_status}")
                except ValueError:
                    print(f"{Colors.RED}Invalid status: {new_status}{Colors.RESET}")
                    print(f"Valid statuses: {', '.join([s.value for s in TaskStatus])}")
            else:
                print(f"{Colors.RED}Task not found: {task_id}{Colors.RESET}")
        
        elif subcommand == "clear":
            self.tasks.clear()
            try:
                tasks_file = self.data_dir / "tasks.json"
                if tasks_file.exists():
                    with open(tasks_file, 'w', encoding='utf-8') as f:
                        json.dump({}, f)
                print(f"{Colors.GREEN}All tasks cleared (memory and storage){Colors.RESET}")
                self.log_message("All tasks cleared")
            except Exception as e:
                print(f"{Colors.YELLOW}Memory cleared, but storage clear failed: {e}{Colors.RESET}")
        
        else:
            print(f"{Colors.RED}Unknown task command: {subcommand}{Colors.RESET}")
    
    def handle_message_command(self, args: List[str]) -> None:
        """Handle messaging system commands."""
        if not args:
            self.display_help()
            return
        
        subcommand = args[0].lower()
        
        if subcommand == "send" and len(args) > 1:
            content = " ".join(args[1:])
            
            message = Message(
                id=f"msg_{uuid.uuid4().hex[:8]}",
                content=content,
                timestamp=datetime.now().isoformat(),
                message_type="user_to_ai",
                project_id=self.current_project,
                session_id=self.current_session_id
            )
            
            self.message_history.append(message)
            
            print(f"{Colors.GREEN}Message sent to AI editor: {Colors.ITALIC}{content}{Colors.RESET}")
            print(f"  Message ID: {message.id}")
            print(f"  Tokens used: ~{len(content.split())}")
            
            self.log_message(f"Sent message to AI: {content[:50]}...", "ai_message")
            
            self.save_persistent_data()
        
        elif subcommand == "history":
            print(f"\n{Colors.BOLD}Message History:{Colors.RESET}")
            
            if not self.message_history:
                print("  No messages found")
                return
            
            recent_messages = self.message_history[-10:]
            for msg in recent_messages:
                timestamp = datetime.fromisoformat(msg.timestamp).strftime("%H:%M:%S")
                type_icon = {
                    "user_to_ai": ">",
                    "ai_response": "<",
                    "info": "i",
                    "warning": "!",
                    "error": "X"
                }.get(msg.message_type, "*")
                
                print(f"  {type_icon} [{timestamp}] {msg.content[:80]}...")
        
        elif subcommand == "clear":
            self.message_history.clear()
            try:
                history_file = self.data_dir / "messages" / "history.json"
                if history_file.exists():
                    with open(history_file, 'w', encoding='utf-8') as f:
                        json.dump([], f)
                print(f"{Colors.GREEN}Message history cleared (memory and storage){Colors.RESET}")
                self.log_message("Message history cleared")
            except Exception as e:
                print(f"{Colors.YELLOW}Memory cleared, but storage clear failed: {e}{Colors.RESET}")
        
        elif subcommand == "export" and len(args) > 1:
            format_type = args[1].lower()
            
            if format_type in ["json", "xml", "txt"]:
                export_file = self.data_dir / f"message_export_{int(time.time())}.{format_type}"
                
                try:
                    if format_type == "json":
                        with open(export_file, 'w', encoding='utf-8') as f:
                            json.dump([asdict(msg) for msg in self.message_history], f, indent=2)
                    
                    elif format_type == "xml":
                        with open(export_file, 'w', encoding='utf-8') as f:
                            f.write("<?xml version='1.0' encoding='UTF-8'?>\n<messages>\n")
                            for msg in self.message_history:
                                f.write(f"  <message id='{msg.id}' timestamp='{msg.timestamp}' type='{msg.message_type}'>\n")
                                f.write(f"    <content>{msg.content}</content>\n")
                                f.write(f"  </message>\n")
                            f.write("</messages>\n")
                    
                    elif format_type == "txt":
                        with open(export_file, 'w', encoding='utf-8') as f:
                            for msg in self.message_history:
                                f.write(f"[{msg.timestamp}] {msg.message_type}: {msg.content}\n")
                    
                    print(f"{Colors.GREEN}Messages exported to: {export_file}{Colors.RESET}")
                    
                except Exception as e:
                    print(f"{Colors.RED}Export failed: {e}{Colors.RESET}")
            else:
                print(f"{Colors.RED}Invalid format: {format_type}. Use: json, xml, txt{Colors.RESET}")
        
        else:
            print(f"{Colors.RED}Unknown message command: {subcommand}{Colors.RESET}")

    def handle_chat_command(self, args: List[str]) -> None:
        """Handle chat operations: add, prompt, export, snapshot."""
        if not hasattr(self, 'chat'):
            print(f"{Colors.YELLOW}Chat manager not available{Colors.RESET}")
            return
        if not args:
            print("Usage: chat <add|prompt|export|snapshot|clear> [args...]")
            return
        sub = args[0].lower()
        if sub == 'add':
            if len(args) < 3:
                print("Usage: chat add <user|assistant|system> <message text>")
                return
            role = args[1].lower()
            content = ' '.join(args[2:])
            mid = self.chat.add_message(role, content)
            print(f"Added chat message: {mid}")
        elif sub == 'prompt':
            max_tokens = self.token_limit
            prompt = self.chat.build_chat_prompt(max_tokens=max_tokens, reserved_reply_tokens=800, system_header="You are an AI code editor.")
            print(f"Prompt tokens: {prompt['token_count']} | truncated: {prompt['truncated']}")
            preview = prompt['prompt_text'][:600]
            print(preview + ("..." if len(prompt['prompt_text']) > 600 else ""))
        elif sub == 'export':
            try:
                path = self.context_manager.export_universal_memory()
                print(f"Exported universal memory: {path}")
                self._emit_editor_signal('memory_exported', {"path": str(path)})
            except Exception as e:
                print(f"{Colors.RED}Export failed: {e}{Colors.RESET}")
        elif sub == 'snapshot':
            try:
                path = self.context_manager.snapshot_long_term_memory()
                print(f"Snapshot appended: {path}")
                self._emit_editor_signal('memory_snapshot', {"path": str(path)})
            except Exception as e:
                print(f"{Colors.RED}Snapshot failed: {e}{Colors.RESET}")
        elif sub == 'clear':
            # Clear chat.jsonl by truncation
            try:
                chat_path = self.chat.chat_file
                if chat_path.exists():
                    with open(chat_path, 'w', encoding='utf-8') as f:
                        f.write("")
                print(f"{Colors.GREEN}Chat history cleared{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}Failed to clear chat: {e}{Colors.RESET}")
        else:
            print("Usage: chat <add|prompt|export|snapshot|clear> [args...]")
    
    def handle_session_command(self, args: List[str]) -> None:
        """Handle session management commands."""
        if not args:
            self.display_help()
            return
        
        subcommand = args[0].lower()
        
        if subcommand == "save":
            self.save_session()
            print(f"{Colors.GREEN}Session saved: {self.current_session_id}{Colors.RESET}")
        
        elif subcommand == "list":
            sessions_dir = self.data_dir / "sessions"
            if sessions_dir.exists():
                session_files = list(sessions_dir.glob("*.json"))
                if session_files:
                    print(f"\n{Colors.BOLD}Saved Sessions:{Colors.RESET}")
                    for session_file in sorted(session_files, key=lambda f: f.stat().st_mtime, reverse=True):
                        session_name = session_file.stem
                        modified = datetime.fromtimestamp(session_file.stat().st_mtime)
                        print(f"  {session_name} - {modified.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    print("  No saved sessions found")
            else:
                print("  No sessions directory found")
        
        elif subcommand == "restore" and len(args) > 1:
            session_id = args[1]
            session_file = self.data_dir / "sessions" / f"{session_id}.json"
            
            if session_file.exists():
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    self.command_history = session_data.get('command_history', [])
                    self.current_project = session_data.get('current_project')
                    
                    print(f"{Colors.GREEN}Session restored: {session_id}{Colors.RESET}")
                    self.log_message(f"Restored session: {session_id}")
                    
                except Exception as e:
                    print(f"{Colors.RED}Failed to restore session: {e}{Colors.RESET}")
            else:
                print(f"{Colors.RED}Session not found: {session_id}{Colors.RESET}")
        
        elif subcommand == "clear":
            self.command_history.clear()
            self.session_cleared = True
            try:
                sessions_dir = self.data_dir / "sessions"
                if sessions_dir.exists():
                    for session_file in sessions_dir.glob("*.json"):
                        session_file.unlink()
                print(f"{Colors.GREEN}All sessions cleared (memory and storage){Colors.RESET}")
                self.log_message("All sessions cleared")
            except Exception as e:
                print(f"{Colors.YELLOW}Memory cleared, but storage clear failed: {e}{Colors.RESET}")
        
        else:
            print(f"{Colors.RED}Unknown session command: {subcommand}{Colors.RESET}")
    
    def save_session(self) -> None:
        """Save current session state."""
        if self.session_cleared:
            return
            
        try:
            session_data = {
                'session_id': self.current_session_id,
                'timestamp': datetime.now().isoformat(),
                'current_project': self.current_project,
                'command_history': self.command_history[-100:],
                'working_directory': str(self.project_root),
                'settings': {
                    'theme': self.theme,
                    'show_timestamps': self.show_timestamps,
                    'auto_save': self.auto_save
                }
            }
            
            session_file = self.data_dir / "sessions" / f"{self.current_session_id}.json"
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2)
                
        except Exception as e:
            self.log_message(f"Session save error: {e}", "error")
    
    def run_command(self, command: str) -> None:
        """Execute shell commands (alias for handle_run_command)."""
        self.handle_run_command(command)
    
    def handle_run_command(self, command: str) -> None:
        """Execute shell commands with enhanced output handling."""
        if not command.strip():
            print(f"{Colors.YELLOW}Please specify a command to run{Colors.RESET}")
            return
        
        self.command_history.append({
            'command': command,
            'timestamp': datetime.now().isoformat(),
            'session_id': self.current_session_id
        })
        
        print(f"\n{Colors.BLUE}Executing:{Colors.RESET} {Colors.BOLD}{command}{Colors.RESET}")
        
        try:
            if command.startswith('cd '):
                path = command[3:].strip()
                try:
                    if path == '..':
                        new_path = self.project_root.parent
                    elif path.startswith('/'):
                        new_path = Path(path)
                    else:
                        new_path = self.project_root / path
                    
                    if new_path.exists() and new_path.is_dir():
                        os.chdir(new_path)
                        self.project_root = Path(os.getcwd())
                        print(f"{Colors.GREEN}Changed directory to: {self.project_root}{Colors.RESET}")
                    else:
                        print(f"{Colors.RED}Directory not found: {path}{Colors.RESET}")
                except Exception as e:
                    print(f"{Colors.RED}Failed to change directory: {e}{Colors.RESET}")
                return
            
            elif command in ['ls', 'dir']:
                print(f"\n{Colors.BOLD}Directory Contents:{Colors.RESET}")
                try:
                    for item in sorted(self.project_root.iterdir()):
                        if item.is_dir():
                            print(f"  [DIR] {Colors.BLUE}{item.name}/{Colors.RESET}")
                        else:
                            print(f"  [FILE] {item.name}")
                except Exception as e:
                    print(f"{Colors.RED}Failed to list directory: {e}{Colors.RESET}")
                return
            
            elif command == 'pwd':
                print(f"{Colors.GREEN}Current directory: {Colors.BOLD}{self.project_root}{Colors.RESET}")
                return
            
            elif command == 'clear':
                os.system('cls' if os.name == 'nt' else 'clear')
                return
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=30
            )
            
            if result.stdout:
                print(f"\n{Colors.GREEN}Output:{Colors.RESET}")
                print(result.stdout)
            
            if result.stderr:
                print(f"\n{Colors.RED}Errors:{Colors.RESET}")
                print(result.stderr)
            
            if result.returncode == 0:
                print(f"\n{Colors.GREEN}Command completed successfully{Colors.RESET}")
                self.log_message(f"System command executed successfully: {command} (exit: {result.returncode})", "system_command", auto_persist=True)
            else:
                print(f"\n{Colors.RED}Command failed (exit code: {result.returncode}){Colors.RESET}")
                self.log_message(f"System command failed: {command} (exit: {result.returncode})", "system_error", auto_persist=True)
            
            if result.stdout:
                self.log_message(f"Command output: {result.stdout[:500]}...", "command_output", auto_persist=True)
            if result.stderr:
                self.log_message(f"Command error: {result.stderr[:500]}...", "command_error", auto_persist=True)
            
        except subprocess.TimeoutExpired:
            print(f"{Colors.RED}Command timed out after 30 seconds{Colors.RESET}")
            self.log_message(f"System command timeout: {command}", "system_error", auto_persist=True)
        except Exception as e:
            print(f"{Colors.RED}Command execution failed: {e}{Colors.RESET}")
            self.log_message(f"System command exception: {command} - {e}", "system_error", auto_persist=True)
    
    def handle_status_command(self) -> None:
        """Display comprehensive system status."""
        print(f"\n{Colors.BOLD}System Status:{Colors.RESET}")
        
        print(f"\n{Colors.BLUE}Session:{Colors.RESET}")
        print(f"  ID: {self.current_session_id}")
        print(f"  Directory: {self.project_root}")
        print(f"  Commands executed: {len(self.command_history)}")
        
        if self.current_project and self.current_project in self.projects:
            proj = self.projects[self.current_project]
            print(f"\n{Colors.GREEN}Current Project:{Colors.RESET}")
            print(f"  Name: {proj.name}")
            print(f"  ID: {proj.id}")
            print(f"  Tasks: {len([t for t in self.tasks.values() if t.project_id == self.current_project])}")
        
        print(f"\n{Colors.YELLOW}Statistics:{Colors.RESET}")
        print(f"  Total projects: {len(self.projects)}")
        print(f"  Total tasks: {len(self.tasks)}")
        print(f"  Messages: {len(self.message_history)}")
        
        if self.tasks:
            status_counts = {}
            for task in self.tasks.values():
                status = task.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print(f"\n{Colors.MAGENTA}Task Status:{Colors.RESET}")
            for status, count in status_counts.items():
                print(f"  {status}: {count}")
        
        print(f"\n{Colors.CYAN}System Health:{Colors.RESET}")
        print(f"  Data directory: {'OK' if self.data_dir.exists() else 'FAIL'}")
        print(f"  Auto-save: {'ON' if self.auto_save else 'OFF'}")
        print(f"  Theme: {self.theme}")
    
    def handle_config_command(self, args: List[str]) -> None:
        """Handle configuration commands."""
        if not args:
            print(f"{Colors.RED}Usage: config <show|set|reset|export|import|backup|restore> [key] [value]{Colors.RESET}")
            return
            
        subcommand = args[0].lower()
        
        if subcommand == 'show':
            print(f"\n{Colors.CYAN}System Configuration{Colors.RESET}")
            config_items = {
                'theme': self.theme,
                'show_timestamps': self.show_timestamps,
                'auto_save': self.auto_save,
                'token_limit': self.token_limit,
                'auto_perform_on_start': self.auto_perform_on_start,
                'verbose': self.verbose,
                'assume_yes': self.assume_yes,
                'max_batch_perform': self.max_batch_perform,
                'data_directory': str(self.data_dir),
                'current_project': self.current_project,
                'session_cleared': self.session_cleared,
                'running': self.running
            }
            for key, value in config_items.items():
                status_color = Colors.GREEN if value else Colors.RED if isinstance(value, bool) else Colors.WHITE
                print(f"   {key}: {status_color}{value}{Colors.RESET}")
            print()
            
            if self.current_project and self.current_project in self.projects:
                proj = self.projects[self.current_project]
                if proj.settings:
                    print(f"{Colors.CYAN}Project Settings ({proj.name}){Colors.RESET}")
                    for key, value in proj.settings.items():
                        print(f"   project.{key}: {value}")
                    print()
        elif subcommand == 'set' and len(args) >= 3:
            key, value = args[1], args[2]
            
            if key.startswith('project.'):
                if not self.current_project or self.current_project not in self.projects:
                    print(f"{Colors.RED}No current project selected{Colors.RESET}")
                    return
                
                proj_key = key[8:]
                proj = self.projects[self.current_project]
                if proj.settings is None:
                    proj.settings = {}
                proj.settings[proj_key] = value
                print(f"{Colors.GREEN}Project setting '{proj_key}' set to: {value}{Colors.RESET}")
                self.log_message(f"Project setting updated: {proj_key} = {value}")
                return
            
            if key == 'theme':
                available_themes = ['dark', 'light', 'blue', 'green', 'matrix', 'ocean', 'default']
                if value in available_themes:
                    self.theme = value
                    self.apply_theme(value)
                    print(f"{Colors.GREEN}Theme set to: {value}{Colors.RESET}")
                else:
                    print(f"{Colors.RED}Invalid theme. Available: {', '.join(available_themes)}{Colors.RESET}")
                    return
            elif key == 'show_timestamps':
                if value.lower() in ['true', '1', 'yes', 'on']:
                    self.show_timestamps = True
                    print(f"{Colors.GREEN}Timestamps enabled{Colors.RESET}")
                elif value.lower() in ['false', '0', 'no', 'off']:
                    self.show_timestamps = False
                    print(f"{Colors.GREEN}Timestamps disabled{Colors.RESET}")
                else:
                    print(f"{Colors.RED}Invalid value. Use: true/false{Colors.RESET}")
                    return
            elif key == 'auto_save':
                if value.lower() in ['true', '1', 'yes', 'on']:
                    self.auto_save = True
                    print(f"{Colors.GREEN}Auto-save enabled{Colors.RESET}")
                elif value.lower() in ['false', '0', 'no', 'off']:
                    self.auto_save = False
                    print(f"{Colors.GREEN}Auto-save disabled{Colors.RESET}")
                else:
                    print(f"{Colors.RED}Invalid value. Use: true/false{Colors.RESET}")
                    return
            elif key == 'token_limit':
                try:
                    limit = int(value)
                    if 1000 <= limit <= 10000:
                        self.token_limit = limit
                        print(f"{Colors.GREEN}Token limit set to: {limit}{Colors.RESET}")
                    else:
                        print(f"{Colors.RED}Token limit must be between 1000 and 10000{Colors.RESET}")
                        return
                except ValueError:
                    print(f"{Colors.RED}Invalid number: {value}{Colors.RESET}")
                    return
            elif key == 'auto_perform_on_start':
                if value.lower() in ['true', '1', 'yes', 'on']:
                    self.auto_perform_on_start = True
                    print(f"{Colors.GREEN}Auto-perform on start enabled{Colors.RESET}")
                elif value.lower() in ['false', '0', 'no', 'off']:
                    self.auto_perform_on_start = False
                    print(f"{Colors.GREEN}Auto-perform on start disabled{Colors.RESET}")
                else:
                    print(f"{Colors.RED}Invalid value. Use: true/false{Colors.RESET}")
                    return
            elif key == 'verbose':
                if value.lower() in ['true', '1', 'yes', 'on']:
                    self.verbose = True
                    print(f"{Colors.GREEN}Verbose logging enabled{Colors.RESET}")
                elif value.lower() in ['false', '0', 'no', 'off']:
                    self.verbose = False
                    print(f"{Colors.GREEN}Verbose logging disabled{Colors.RESET}")
                else:
                    print(f"{Colors.RED}Invalid value. Use: true/false{Colors.RESET}")
                    return
            elif key == 'assume_yes':
                if value.lower() in ['true', '1', 'yes', 'on']:
                    self.assume_yes = True
                    print(f"{Colors.GREEN}Assume-yes enabled{Colors.RESET}")
                elif value.lower() in ['false', '0', 'no', 'off']:
                    self.assume_yes = False
                    print(f"{Colors.GREEN}Assume-yes disabled{Colors.RESET}")
                else:
                    print(f"{Colors.RED}Invalid value. Use: true/false{Colors.RESET}")
                    return
            elif key == 'max_batch_perform':
                try:
                    limit = int(value)
                    if limit < 1:
                        print(f"{Colors.RED}max_batch_perform must be >= 1{Colors.RESET}")
                        return
                    self.max_batch_perform = limit
                    print(f"{Colors.GREEN}max_batch_perform set to: {limit}{Colors.RESET}")
                except ValueError:
                    print(f"{Colors.RED}Invalid number: {value}{Colors.RESET}")
                    return
            else:
                print(f"{Colors.RED}Unknown configuration key: {key}{Colors.RESET}")
                print("Available keys: theme, show_timestamps, auto_save, token_limit, auto_perform_on_start, verbose, assume_yes, max_batch_perform")
                print("Project keys: project.<key> (requires active project)")
                return
                
            self.log_message(f"Configuration updated: {key} = {value}")
        elif subcommand == 'reset':
            if len(args) > 1 and args[1] == 'project':
                if self.current_project and self.current_project in self.projects:
                    self.projects[self.current_project].settings = {}
                    print(f"{Colors.GREEN}Project settings reset{Colors.RESET}")
                    self.log_message("Project settings reset")
                else:
                    print(f"{Colors.RED}No current project selected{Colors.RESET}")
            else:
                self.theme = 'default'
                self.show_timestamps = True
                self.auto_save = True
                self.token_limit = 4000
                self.session_cleared = False
                self.apply_theme('default')
                print(f"{Colors.GREEN}System configuration reset to defaults{Colors.RESET}")
                self.log_message("System configuration reset to defaults")
        
        elif subcommand == 'export':
            format_type = args[1].lower() if len(args) > 1 else "json"
            
            if format_type not in ["json", "xml", "txt", "csv"]:
                print(f"{Colors.RED}Invalid format: {format_type}. Use: json, xml, txt, csv{Colors.RESET}")
                return
            
            export_file = self.data_dir / "exports" / f"config_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
            export_file.parent.mkdir(exist_ok=True)
            
            try:
                config_data = {
                    'system': {
                        'theme': self.theme,
                        'show_timestamps': self.show_timestamps,
                        'auto_save': self.auto_save,
                        'token_limit': self.token_limit
                    },
                    'projects': {pid: proj.settings for pid, proj in self.projects.items() if proj.settings}
                }
                
                if format_type == "json":
                    with open(export_file, 'w', encoding='utf-8') as f:
                        json.dump(config_data, f, indent=2)
                        
                elif format_type == "xml":
                    with open(export_file, 'w', encoding='utf-8') as f:
                        f.write("<?xml version='1.0' encoding='UTF-8'?>\n<configuration>\n")
                        f.write("  <system>\n")
                        for key, value in config_data['system'].items():
                            f.write(f"    <{key}>{value}</{key}>\n")
                        f.write("  </system>\n")
                        if config_data['projects']:
                            f.write("  <projects>\n")
                            for pid, settings in config_data['projects'].items():
                                f.write(f"    <project id='{pid}'>\n")
                                for key, value in settings.items():
                                    f.write(f"      <{key}>{value}</{key}>\n")
                                f.write(f"    </project>\n")
                            f.write("  </projects>\n")
                        f.write("</configuration>\n")
                        
                elif format_type == "txt":
                    with open(export_file, 'w', encoding='utf-8') as f:
                        f.write("CONFIGURATION EXPORT\n")
                        f.write("=" * 50 + "\n\n")
                        f.write("SYSTEM SETTINGS:\n")
                        f.write("-" * 20 + "\n")
                        for key, value in config_data['system'].items():
                            f.write(f"{key}: {value}\n")
                        f.write("\n")
                        if config_data['projects']:
                            f.write("PROJECT SETTINGS:\n")
                            f.write("-" * 20 + "\n")
                            for pid, settings in config_data['projects'].items():
                                f.write(f"Project {pid}:\n")
                                for key, value in settings.items():
                                    f.write(f"  {key}: {value}\n")
                                f.write("\n")
                                
                elif format_type == "csv":
                    with open(export_file, 'w', encoding='utf-8') as f:
                        f.write("Type,Key,Value,Project\n")
                        for key, value in config_data['system'].items():
                            f.write(f"system,{key},{value},\n")
                        for pid, settings in config_data['projects'].items():
                            for key, value in settings.items():
                                f.write(f"project,{key},{value},{pid}\n")
                
                print(f"{Colors.GREEN}Configuration exported to: {export_file}{Colors.RESET}")
                self.log_message(f"Configuration exported to {export_file}")
            except Exception as e:
                print(f"{Colors.RED}Export failed: {e}{Colors.RESET}")
        
        elif subcommand == 'import' and len(args) > 1:
            import_file = Path(args[1])
            if not import_file.exists():
                print(f"{Colors.RED}Import file not found: {import_file}{Colors.RESET}")
                return
            
            try:
                with open(import_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                if 'system' in config_data:
                    sys_config = config_data['system']
                    self.theme = sys_config.get('theme', self.theme)
                    self.show_timestamps = sys_config.get('show_timestamps', self.show_timestamps)
                    self.auto_save = sys_config.get('auto_save', self.auto_save)
                    self.token_limit = sys_config.get('token_limit', self.token_limit)
                    self.apply_theme(self.theme)
                
                if 'projects' in config_data:
                    for pid, settings in config_data['projects'].items():
                        if pid in self.projects:
                            self.projects[pid].settings = settings
                
                print(f"{Colors.GREEN}Configuration imported from: {import_file}{Colors.RESET}")
                self.log_message(f"Configuration imported from {import_file}")
            except Exception as e:
                print(f"{Colors.RED}Import failed: {e}{Colors.RESET}")
        
        elif subcommand == 'backup':
            backup_file = self.data_dir / "backups" / f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_file.parent.mkdir(exist_ok=True)
            
            try:
                backup_data = {
                    'timestamp': datetime.now().isoformat(),
                    'system': {
                        'theme': self.theme,
                        'show_timestamps': self.show_timestamps,
                        'auto_save': self.auto_save,
                        'token_limit': self.token_limit
                    },
                    'projects': {pid: asdict(proj) for pid, proj in self.projects.items()}
                }
                
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(backup_data, f, indent=2)
                print(f"{Colors.GREEN}Configuration backed up to: {backup_file}{Colors.RESET}")
                self.log_message(f"Configuration backed up to {backup_file}")
            except Exception as e:
                print(f"{Colors.RED}Backup failed: {e}{Colors.RESET}")
        
        elif subcommand == 'restore' and len(args) > 1:
            restore_file = Path(args[1])
            if not restore_file.exists():
                print(f"{Colors.RED}Restore file not found: {restore_file}{Colors.RESET}")
                return
            
            try:
                with open(restore_file, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
                
                if 'system' in backup_data:
                    sys_config = backup_data['system']
                    self.theme = sys_config.get('theme', 'default')
                    self.show_timestamps = sys_config.get('show_timestamps', True)
                    self.auto_save = sys_config.get('auto_save', True)
                    self.token_limit = sys_config.get('token_limit', 4000)
                    self.apply_theme(self.theme)
                
                if 'projects' in backup_data:
                    for pid, proj_data in backup_data['projects'].items():
                        self.projects[pid] = Project(**proj_data)
                
                print(f"{Colors.GREEN}Configuration restored from: {restore_file}{Colors.RESET}")
                self.log_message(f"Configuration restored from {restore_file}")
            except Exception as e:
                print(f"{Colors.RED}Restore failed: {e}{Colors.RESET}")
        
        else:
            print(f"{Colors.RED}Usage: config <show|set|reset|export|import|backup|restore> [key] [value]{Colors.RESET}")
            print("Available actions:")
            print("  show                    - Show current configuration")
            print("  set <key> <value>       - Set configuration value")
            print("  reset [project]         - Reset to defaults")
            print("  export                  - Export configuration")
            print("  import <file>           - Import configuration")
            print("  backup                  - Create configuration backup")
            print("  restore <file>          - Restore from backup")
    
    def handle_backup_command(self, args: List[str]) -> None:
        """Handle backup operations."""
        if not args:
            print(f"{Colors.RED}Usage: backup <create|restore|list|clear> [name]{Colors.RESET}")
            return
            
        subcommand = args[0].lower()
        
        if subcommand == 'create':
            backup_name = args[1] if len(args) > 1 else f"backup_{int(time.time())}"
            self.create_backup(backup_name)
            
        elif subcommand == 'list':
            backup_dir = self.data_dir / 'backups'
            try:
                backups = list(backup_dir.glob('*.json'))
                if backups:
                    print(f"\n{Colors.CYAN}Available Backups{Colors.RESET}")
                    for backup in sorted(backups, key=lambda f: f.stat().st_mtime, reverse=True):
                        backup_name = backup.stem
                        modified = datetime.fromtimestamp(backup.stat().st_mtime)
                        size = backup.stat().st_size
                        print(f"   {backup_name} - {modified.strftime('%Y-%m-%d %H:%M:%S')} ({size} bytes)")
                    print()
                else:
                    print(f"{Colors.YELLOW}No backups found{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}Failed to list backups: {e}{Colors.RESET}")
                
        elif subcommand == 'restore' and len(args) > 1:
            backup_name = args[1]
            self.restore_backup(backup_name)
            
        elif subcommand == 'clear':
            backup_dir = self.data_dir / 'backups'
            if backup_dir.exists():
                import shutil
                shutil.rmtree(backup_dir)
                backup_dir.mkdir(exist_ok=True)
                print(f"{Colors.GREEN}All backups cleared{Colors.RESET}")
                self.log_message("Cleared all backups")
            else:
                print(f"{Colors.YELLOW}No backups directory found{Colors.RESET}")
                
        else:
            print(f"{Colors.RED}Usage: backup <create|restore|list|clear> [name]{Colors.RESET}")
    
    def create_backup(self, backup_name: str) -> None:
        """Create a backup of current session data."""
        try:
            backup_dir = self.data_dir / 'backups'
            backup_dir.mkdir(exist_ok=True)
            backup_path = backup_dir / f"{backup_name}.json"
            
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'projects': {pid: asdict(proj) for pid, proj in self.projects.items()},
                'tasks': {tid: asdict(task) for tid, task in self.tasks.items()},
                'messages': [asdict(msg) for msg in self.message_history],
                'current_project': self.current_project,
                'session_id': self.current_session_id,
                'settings': {
                    'theme': self.theme,
                    'show_timestamps': self.show_timestamps,
                    'auto_save': self.auto_save,
                    'token_limit': self.token_limit
                }
            }
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2)
            
            print(f"{Colors.GREEN}Backup '{backup_name}' created successfully{Colors.RESET}")
            self.log_message(f"Backup created: {backup_name}")
            
        except Exception as e:
            print(f"{Colors.RED}Error creating backup: {e}{Colors.RESET}")
    
    def restore_backup(self, backup_name: str) -> None:
        """Restore session data from a backup."""
        try:
            backup_dir = self.data_dir / 'backups'
            backup_path = backup_dir / f"{backup_name}.json"
            
            if not backup_path.exists():
                print(f"{Colors.RED}Backup '{backup_name}' not found{Colors.RESET}")
                return
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            if 'projects' in backup_data:
                self.projects = {pid: Project(**pdata) for pid, pdata in backup_data['projects'].items()}
            if 'tasks' in backup_data:
                self.tasks = {tid: Task(**tdata) for tid, tdata in backup_data['tasks'].items()}
            if 'messages' in backup_data:
                self.message_history = [Message(**mdata) for mdata in backup_data['messages']]
            if 'current_project' in backup_data:
                self.current_project = backup_data['current_project']
            if 'settings' in backup_data:
                settings = backup_data['settings']
                self.theme = settings.get('theme', self.theme)
                self.show_timestamps = settings.get('show_timestamps', self.show_timestamps)
                self.auto_save = settings.get('auto_save', self.auto_save)
                self.token_limit = settings.get('token_limit', self.token_limit)
            
            self.apply_theme(self.theme)
            
            print(f"{Colors.GREEN}Backup '{backup_name}' restored successfully{Colors.RESET}")
            print(f"  Restored {len(self.message_history)} messages")
            print(f"  Theme: {self.theme}")
            print(f"  Backup date: {backup_data.get('timestamp', 'Unknown')}")
            
            self.log_message(f"Backup restored: {backup_name}")
            
        except Exception as e:
            print(f"{Colors.RED}Error restoring backup: {e}{Colors.RESET}")
    
    def handle_performance_command(self) -> None:
        """Display performance metrics."""
        print(f"\n{Colors.CYAN}Performance Metrics{Colors.RESET}")
        
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('.')
            
            print(f"   CPU Usage: {cpu_percent}%")
            print(f"   Memory: {memory.percent}% ({memory.used // 1024 // 1024} MB / {memory.total // 1024 // 1024} MB)")
            print(f"   Disk: {disk.percent}% ({disk.used // 1024 // 1024 // 1024} GB / {disk.total // 1024 // 1024 // 1024} GB)")
            
            try:
                net_io = psutil.net_io_counters()
                print(f"   Network: {net_io.bytes_sent / (1024**2):.1f}MB sent, {net_io.bytes_recv / (1024**2):.1f}MB received")
            except:
                print("   Network: Information unavailable")
                
        except ImportError:
            print(f"   System metrics not available (install psutil)")
        
        completed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
        active_tasks = len(self.tasks) - completed_tasks
        
        print(f"   Active Projects: {len(self.projects)}")
        print(f"   Active Tasks: {active_tasks}")
        print(f"   Completed Tasks: {completed_tasks}")
        print(f"   Total Messages: {len(self.message_history)}")
        print(f"   Command History: {len(self.command_history)}")
        
        import sys
        total_size = sys.getsizeof(self.projects) + sys.getsizeof(self.tasks) + sys.getsizeof(self.message_history)
        print(f"   Data Size: ~{total_size / 1024:.1f} KB")
        print()
    
    def handle_theme_command(self, args: List[str]) -> None:
        """Handle theme changes with real terminal color updates."""
        if not args:
            print(f"{Colors.RED}Usage: theme <dark|light|blue|green|matrix|ocean>{Colors.RESET}")
            return
            
        theme_name = args[0].lower()
        available_themes = ['dark', 'light', 'blue', 'green', 'matrix', 'ocean', 'default']
        
        if theme_name in available_themes:
            self.theme = theme_name
            self.apply_theme(theme_name)
            print(f"{Colors.GREEN}Theme changed to: {theme_name}{Colors.RESET}")
            self.log_message(f"Theme changed to: {theme_name}")
        else:
            print(f"{Colors.RED}Unknown theme: {theme_name}{Colors.RESET}")
            print(f"   Available themes: {', '.join(available_themes)}")
    
    def apply_theme(self, theme_name: str) -> None:
        """Apply theme colors to the actual terminal."""
        import os
        
        theme_configs = {
            'dark': {
                'bg': '\033]11;#1e1e1e\007',
                'fg': '\033]10;#d4d4d4\007',
                'cursor': '\033]12;#ffffff\007'
            },
            'light': {
                'bg': '\033]11;#ffffff\007',
                'fg': '\033]10;#000000\007',
                'cursor': '\033]12;#000000\007'
            },
            'blue': {
                'bg': '\033]11;#0f1419\007',
                'fg': '\033]10;#bfbdb6\007',
                'cursor': '\033]12;#00d4ff\007'
            },
            'green': {
                'bg': '\033]11;#0d1117\007',
                'fg': '\033]10;#c9d1d9\007',
                'cursor': '\033]12;#00ff00\007'
            },
            'matrix': {
                'bg': '\033]11;#000000\007',
                'fg': '\033]10;#00ff00\007',
                'cursor': '\033]12;#00ff00\007'
            },
            'ocean': {
                'bg': '\033]11;#001122\007',
                'fg': '\033]10;#88ccff\007',
                'cursor': '\033]12;#00aaff\007'
            },
            'default': {
                'bg': '\033]11;#000000\007',
                'fg': '\033]10;#ffffff\007',
                'cursor': '\033]12;#ffffff\007'
            }
        }
        
        if theme_name in theme_configs:
            config = theme_configs[theme_name]
            
            try:
                print(config['bg'], end='', flush=True)
                print(config['fg'], end='', flush=True)
                print(config['cursor'], end='', flush=True)
                
                os.system('cls' if os.name == 'nt' else 'clear')
                self.display_header()
                
                print(f"{Colors.CYAN}{theme_name.title()} theme applied to terminal{Colors.RESET}")
                
            except Exception as e:
                print(f"{Colors.YELLOW}Theme colors set, but terminal may not support all features: {e}{Colors.RESET}")
    
    def save_current_state(self) -> None:
        """Save current state to history for back command."""
        try:
            current_state = {
                'current_project': self.current_project,
                'projects': {pid: asdict(proj) for pid, proj in self.projects.items()},
                'tasks': {tid: asdict(task) for tid, task in self.tasks.items()},
                'theme': self.theme,
                'show_timestamps': self.show_timestamps,
                'auto_save': self.auto_save,
                'token_limit': self.token_limit,
                'timestamp': datetime.now().isoformat()
            }
            
            self.state_history.append(current_state)
            
            if len(self.state_history) > self.max_history_size:
                self.state_history.pop(0)
                
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not save state for back command: {e}{Colors.RESET}")
    
    def handle_back_command(self, args: List[str]) -> None:
        """Handle back command to restore previous state."""
        if not args:
            if not self.state_history:
                print(f"{Colors.YELLOW}No previous states available{Colors.RESET}")
                return
            
            print(f"\n{Colors.BOLD}Available Previous States:{Colors.RESET}")
            for i, state in enumerate(reversed(self.state_history[-5:]), 1):
                timestamp = state.get('timestamp', 'Unknown')
                project = state.get('current_project', 'None')
                task_count = len(state.get('tasks', {}))
                print(f"  {i}. {timestamp[:19]} - Project: {project}, Tasks: {task_count}")
            print(f"\nUsage: back <number> or back restore <number>")
            return
        
        subcommand = args[0].lower()
        
        if subcommand == "restore" and len(args) > 1:
            try:
                index = int(args[1]) - 1
                if 0 <= index < len(self.state_history):
                    state_index = len(self.state_history) - 1 - index
                    state = self.state_history[state_index]
                    
                    self.save_current_state()
                    
                    self.current_project = state.get('current_project')
                    
                    self.projects = {}
                    for pid, proj_data in state.get('projects', {}).items():
                        self.projects[pid] = Project(**proj_data)
                    
                    self.tasks = {}
                    for tid, task_data in state.get('tasks', {}).items():
                        self.tasks[tid] = Task(**task_data)
                    
                    self.theme = state.get('theme', 'default')
                    self.show_timestamps = state.get('show_timestamps', True)
                    self.auto_save = state.get('auto_save', True)
                    self.token_limit = state.get('token_limit', 4000)
                    
                    self.apply_theme(self.theme)
                    
                    print(f"{Colors.GREEN}State restored from {state.get('timestamp', 'unknown time')}{Colors.RESET}")
                    self.log_message(f"State restored from backup {index + 1}")
                    
                else:
                    print(f"{Colors.RED}Invalid state number. Use 1-{len(self.state_history)}{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}Invalid number format{Colors.RESET}")
        
        elif subcommand == "clear":
            self.state_history.clear()
            print(f"{Colors.GREEN}State history cleared{Colors.RESET}")
            
        elif subcommand.isdigit():
            try:
                index = int(subcommand) - 1
                if 0 <= index < len(self.state_history):
                    self.handle_back_command(['restore', str(index + 1)])
                else:
                    print(f"{Colors.RED}Invalid state number. Use 1-{len(self.state_history)}{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}Invalid number format{Colors.RESET}")
        
        else:
            print(f"{Colors.RED}Usage: back [list|restore <number>|clear|<number>]{Colors.RESET}")
    
    def handle_file_operation(self, file_path: str) -> None:
        """Handle file operations using @path/to/file syntax."""
        try:
            clean_path = file_path[1:].strip()
            
            if not clean_path:
                print(f"{Colors.RED}Error: No file path provided{Colors.RESET}")
                print(f"Usage: @path/to/file")
                return
            
            if not os.path.isabs(clean_path):
                clean_path = os.path.abspath(clean_path)
            
            if os.path.exists(clean_path):
                if os.path.isfile(clean_path):
                    file_size = os.path.getsize(clean_path)
                    file_modified = os.path.getmtime(clean_path)
                    modified_time = datetime.fromtimestamp(file_modified).strftime('%Y-%m-%d %H:%M:%S')
                    
                    print(f"\n{Colors.BOLD}📁 File Operations: {Colors.CYAN}{clean_path}{Colors.RESET}")
                    print(f"   Size: {file_size} bytes | Modified: {modified_time}")
                    
                    try:
                        with open(clean_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()[:10]
                            print(f"\n{Colors.DIM}Content preview (first 10 lines):{Colors.RESET}")
                            for i, line in enumerate(lines, 1):
                                print(f"{Colors.DIM}{i:2}: {line.rstrip()}{Colors.RESET}")
                            if len(lines) == 10:
                                print(f"{Colors.DIM}... (file continues){Colors.RESET}")
                    except UnicodeDecodeError:
                        print(f"{Colors.YELLOW}Binary file - content preview not available{Colors.RESET}")
                    
                    print(f"\n{Colors.GREEN}✓ File accessible for operations{Colors.RESET}")
                    
                elif os.path.isdir(clean_path):
                    print(f"\n{Colors.BOLD}📂 Directory: {Colors.CYAN}{clean_path}{Colors.RESET}")
                    try:
                        items = os.listdir(clean_path)
                        if items:
                            print(f"Contents ({len(items)} items):")
                            for item in sorted(items)[:20]:
                                item_path = os.path.join(clean_path, item)
                                if os.path.isdir(item_path):
                                    print(f"  📂 {item}/")
                                else:
                                    print(f"  📄 {item}")
                            if len(items) > 20:
                                print(f"  {Colors.DIM}... and {len(items) - 20} more items{Colors.RESET}")
                        else:
                            print(f"{Colors.DIM}Directory is empty{Colors.RESET}")
                    except PermissionError:
                        print(f"{Colors.RED}Permission denied accessing directory{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}File/directory does not exist: {clean_path}{Colors.RESET}")
                print(f"You can create it using standard commands or your editor")
                
        except Exception as e:
            print(f"{Colors.RED}File operation error: {e}{Colors.RESET}")
    
    def _load_remembered(self) -> Dict[str, Any]:
        """Load remembered instructions from disk."""
        try:
            if self.remember_file.exists():
                with open(self.remember_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
        except Exception:
            pass
        return {"last": None, "history": []}
    
    def _save_remembered(self, data: Dict[str, Any]) -> None:
        """Persist remembered instructions and export a plain-text copy for AI editors."""
        try:
            self.memory_dir.mkdir(parents=True, exist_ok=True)
            with open(self.remember_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            # Export a light-weight file any AI editor can pick up
            self.exports_dir.mkdir(parents=True, exist_ok=True)
            last_text = (data.get("last") or {}).get("text", "")
            export_txt = self.exports_dir / "remember_last.txt"
            with open(export_txt, 'w', encoding='utf-8') as f:
                f.write(last_text)
            # Emit editor signal
            self._emit_editor_signal('remember_updated', {"last_preview": last_text[:120]})
        except Exception as e:
            self.log_message(f"Remember save error: {e}", "error")
    
    def _emit_editor_signal(self, event: str, payload: Dict[str, Any]) -> None:
        try:
            self.exports_dir.mkdir(parents=True, exist_ok=True)
            signal_path = self.exports_dir / "editor_signal.json"
            self._editor_signal_version += 1
            signal = {
                "event": event,
                "version": self._editor_signal_version,
                "timestamp": datetime.now().isoformat(),
                "payload": payload or {}
            }
            with open(signal_path, 'w', encoding='utf-8') as f:
                json.dump(signal, f, indent=2, ensure_ascii=False)
            # Append to events stream
            with open(self.editor_events_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(signal, ensure_ascii=False) + "\n")
            self.vprint(f"Emitted editor signal: {event} v{self._editor_signal_version}")
        except Exception:
            pass
    
    def handle_remember_command(self, args: List[str]) -> None:
        """Store user intent/instructions for later automatic execution or sharing."""
        # Subcommands: clear | list | remove <n> | purge executed | (no args -> perform all) | text
        if args and args[0].lower() == 'clear':
            try:
                data = {"last": None, "history": []}
                self._save_remembered(data)
                print(f"{Colors.GREEN}Remembered instructions cleared{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}Failed to clear remembered instructions: {e}{Colors.RESET}")
            return
        if args and args[0].lower() == 'list':
            data = self._load_remembered()
            history = data.get('history', [])
            if not history:
                print("No remembered entries.")
                return
            print(f"\n{Colors.BOLD}Remembered Entries:{Colors.RESET}")
            for idx, entry in enumerate(history, start=1):
                ts = entry.get('timestamp', '')
                txt = (entry.get('text') or '').strip()
                preview = (txt[:80] + ('…' if len(txt) > 80 else ''))
                executed = entry.get('executed', False)
                marker = '✔' if executed else '✗'
                print(f"  {idx}. [{marker}] [{ts}] {preview}")
            return
        if len(args) >= 2 and args[0].lower() == 'remove' and args[1].isdigit():
            n = int(args[1])
            data = self._load_remembered()
            history = data.get('history', [])
            if 1 <= n <= len(history):
                removed = history.pop(n-1)
                # Fix last if it pointed to removed
                if data.get('last') and data['last'].get('text') == removed.get('text'):
                    data['last'] = history[-1] if history else None
                data['history'] = history
                self._save_remembered(data)
                print(f"{Colors.GREEN}Removed entry {n}{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}Index out of range. Use 1..{len(history)}{Colors.RESET}")
            return
        if args and args[0].lower() == 'purge' and len(args) > 1 and args[1].lower() == 'executed':
            data = self._load_remembered()
            history = data.get('history', [])
            filtered = [e for e in history if not e.get('executed')]
            data['history'] = filtered
            if data.get('last') and data['last'].get('executed'):
                data['last'] = filtered[-1] if filtered else None
            self._save_remembered(data)
            print(f"{Colors.GREEN}Purged executed entries{Colors.RESET}")
            return
        
        if not args:
            # Execute all saved entries sequentially with guardrails
            data = self._load_remembered()
            history = data.get("history", [])
            if not history:
                print(f"{Colors.YELLOW}No remembered entries to perform.{Colors.RESET}")
                return
            pending = [e for e in history if not e.get('executed')]
            batch_count = len(pending)
            if batch_count > self.max_batch_perform and not self.assume_yes:
                print(f"{Colors.YELLOW}Batch of {batch_count} exceeds max_batch_perform={self.max_batch_perform}. Set `config set max_batch_perform <n>` or `config set assume_yes on` to proceed.{Colors.RESET}")
                return
            print(f"{Colors.BLUE}Performing {batch_count} pending remembered entries...{Colors.RESET}")
            for entry in pending:
                text = (entry.get("text") or "").strip()
                if not text:
                    continue
                route = 'chat'
                status = 'ok'
                try:
                    # Temporarily set last and call perform
                    orig = data.get("last")
                    data["last"] = entry
                    self._save_remembered(data)
                    # Determine if command or chat
                    known_prefixes = [
                        'project', 'task', 'message', 'session', 'chat', 'run', 'status', 'config',
                        'backup', 'performance', 'theme', 'clear', 'back', 'ls', 'dir', 'pwd', 'cd', '@'
                    ]
                    if any(text.startswith(p) for p in known_prefixes):
                        route = 'command'
                    self.handle_perform_command()
                    # restore last
                    data["last"] = orig
                    # mark executed
                    entry['executed'] = True
                    entry['executed_at'] = datetime.now().isoformat()
                    entry['result'] = {'route': route, 'status': status}
                    self._save_remembered(data)
                except Exception as e:
                    entry['executed'] = True
                    entry['executed_at'] = datetime.now().isoformat()
                    entry['result'] = {'route': route, 'status': f'error: {e}'}
                    self._save_remembered(data)
            print(f"{Colors.GREEN}Completed performing pending entries.{Colors.RESET}")
            return
        
        text = ' '.join(args).strip()
        if not text:
            print(f"{Colors.YELLOW}Please provide instruction text to remember{Colors.RESET}")
            return
        data = self._load_remembered()
        timestamp = datetime.now().isoformat()
        entry = {"text": text, "timestamp": timestamp, "executed": False}
        # Deduplicate if same as last
        if not data.get("last") or data["last"].get("text") != text:
            data.setdefault("history", []).append(entry)
        data["last"] = entry
        self._save_remembered(data)
        # Also add to chat/context for global availability/dedupe
        try:
            if hasattr(self, 'chat'):
                self.chat.add_message("user", f"REMEMBER: {text}", metadata={"remember": True})
        except Exception:
            pass
        try:
            if hasattr(self, 'context_manager'):
                self.context_manager.add_context(text, context_type="remembered_intent")
                self.context_manager.save_persistent_context()
        except Exception:
            pass
        print(f"{Colors.GREEN}Remembered instruction.{Colors.RESET} Exported to {self.exports_dir / 'remember_last.txt'}")
    
    def handle_perform_command(self) -> None:
        """Auto-execute the last remembered instruction if it is a command."""
        # Support 'perform clear' by checking previous parsed args? Implement separate router in process_command.
        data = self._load_remembered()
        last = data.get("last")
        if not last or not last.get("text"):
            print(f"{Colors.YELLOW}No remembered instruction found. Use 'remember <text>' first.{Colors.RESET}")
            return
        text = last["text"].strip()
        # Heuristic: if it starts with a known command keyword or '@', route to command processor
        known_prefixes = [
            'project', 'task', 'message', 'session', 'chat', 'run', 'status', 'config',
            'backup', 'performance', 'theme', 'clear', 'back', 'ls', 'dir', 'pwd', 'cd', '@'
        ]
        if any(text.startswith(p) for p in known_prefixes):
            print(f"{Colors.BLUE}Performing remembered command:{Colors.RESET} {Colors.BOLD}{text}{Colors.RESET}")
            # Avoid infinite recursion if 'perform' itself was remembered
            if text.split()[0].lower() == 'perform':
                print(f"{Colors.YELLOW}Refusing to recursively perform 'perform'. Update remembered text first.{Colors.RESET}")
                return
            self.process_command(text)
            return
        # Otherwise, treat as a message to the AI editor environment
        try:
            if hasattr(self, 'chat'):
                self.chat.add_message("user", text, metadata={"auto_perform": True})
            self.log_message(f"Auto-performed remembered text to chat: {text}", "user_to_ai")
            print(f"{Colors.GREEN}Pushed remembered text to chat/messages for AI editor.{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.YELLOW}Performed storage only (chat push failed): {e}{Colors.RESET}")
    
    def process_command(self, user_input: str) -> None:
        """Process and route user commands with guaranteed persistence."""
        parts = user_input.strip().split()
        if not parts:
            return
        
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        self.log_message(f"Command executed: {user_input}", "command", auto_persist=True)
        
        # Try registry first
        if self.command_registry.get(command):
            try:
                self.command_registry[command](args)
                return
            except Exception as e:
                print(f"{Colors.RED}Command error: {e}{Colors.RESET}")
                self.log_message(f"Command error: {command} - {e}", "error")
                return
        
        try:
            if command in ['exit', 'quit', 'q']:
                print(f"\n{Colors.YELLOW}Saving session and exiting...{Colors.RESET}")
                if self.auto_save:
                    self.save_persistent_data()
                self.running = False
                
            elif command == 'help':
                self.display_help()
                
            elif command == 'project':
                self.handle_project_command(args)
                
            elif command == 'task':
                self.handle_task_command(args)
                
            elif command == 'message':
                self.handle_message_command(args)
                
            elif command == 'session':
                self.handle_session_command(args)

            elif command == 'chat':
                self.handle_chat_command(args)
                
            elif command == 'run':
                cmd_to_run = ' '.join(args)
                self.handle_run_command(cmd_to_run)
                
            elif command == 'ai':
                self.handle_ai_command(args)
                
            elif command == 'status':
                self.handle_status_command()
                
            elif command == 'config':
                self.handle_config_command(args)
                
            elif command == 'backup':
                self.handle_backup_command(args)
                
            elif command == 'performance':
                self.handle_performance_command()
                
            elif command == 'theme':
                self.handle_theme_command(args)
                
            elif command == 'remember':
                self.handle_remember_command(args)
                
            elif command == 'perform':
                # Support `perform clear` to wipe last only
                if args and args[0].lower() == 'clear':
                    try:
                        data = self._load_remembered()
                        data['last'] = None
                        self._save_remembered(data)
                        print(f"{Colors.GREEN}Cleared last remembered entry{Colors.RESET}")
                    except Exception as e:
                        print(f"{Colors.RED}Failed to clear last remembered: {e}{Colors.RESET}")
                else:
                    self.handle_perform_command()
                
            elif command == 'memory':
                self.handle_memory_command(args)
                
            elif command == 'clear':
                if args and args[0].lower() == 'all':
                    self._handle_clear_all_command()
                else:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    self.display_header()
                
            elif command == 'back':
                self.handle_back_command(args)
                
            elif command in ['ls', 'dir', 'pwd'] or command.startswith('cd'):
                self.handle_run_command(user_input)
                
            elif user_input.startswith('@'):
                self.handle_file_operation(user_input)
                
            else:
                print(f"{Colors.RED}Unknown command: '{command}'{Colors.RESET}")
                print(f"   Type '{Colors.BOLD}help{Colors.RESET}' for available commands")
                
        except Exception as e:
            print(f"{Colors.RED}Command error: {e}{Colors.RESET}")
            self.log_message(f"Command error: {command} - {e}", "error")
    
    def handle_memory_command(self, args: List[str]) -> None:
        """Handle memory-related operations like clear."""
        if not args or args[0].lower() not in ['clear', 'status']:
            print("Usage: memory <clear|status>")
            return
        sub = args[0].lower()
        if sub == 'clear':
            errors = []
            # Clear remembered entries
            try:
                self._save_remembered({"last": None, "history": []})
            except Exception as e:
                errors.append(f"remembered: {e}")
            # Clear memory snapshots (.terminal_data/memory/*) but keep directory
            try:
                if self.memory_dir.exists():
                    for fp in self.memory_dir.glob('*'):
                        if fp.is_file():
                            try:
                                fp.unlink()
                            except Exception:
                                pass
            except Exception as e:
                errors.append(f"snapshots: {e}")
            # Clear context manager persistent file if available
            try:
                ctx_file = self.project_root / 'context_memory.json'
                if ctx_file.exists():
                    ctx_file.unlink()
            except Exception as e:
                errors.append(f"context: {e}")
            if errors:
                print(f"{Colors.YELLOW}Memory cleared with warnings: {', '.join(errors)}{Colors.RESET}")
            else:
                print(f"{Colors.GREEN}All memory cleared (remembered entries, snapshots, context).{Colors.RESET}")
        elif sub == 'status':
            data = self._load_remembered()
            history = data.get('history', [])
            total = len(history)
            executed = len([e for e in history if e.get('executed')])
            pending = total - executed
            last_text = (data.get('last') or {}).get('text')
            print(f"Remembered: total={total}, executed={executed}, pending={pending}")
            if last_text:
                prev = (last_text[:80] + ('…' if len(last_text) > 80 else ''))
                print(f"Last: {prev}")
    
    def start(self) -> None:
        """Start the terminal interface (alias for run)."""
        self.run()
    
    def run(self) -> None:
        """Main interactive loop with enhanced error handling."""
        try:
            self.display_header()
            # Auto-perform on start if enabled
            if self.auto_perform_on_start:
                self.vprint("auto_perform_on_start is enabled; performing all remembered entries")
                try:
                    self.handle_remember_command([])
                except Exception as e:
                    self.vprint(f"Auto-perform failed: {e}")
            
            while self.running:
                try:
                    gradient_top = Colors.PRIMARY_GRADIENT_TOP
                    gradient_mid = Colors.PRIMARY_GRADIENT_MID
                    gradient_bot = Colors.PRIMARY_GRADIENT_BOT
                    accent_gold = Colors.ACCENT_GOLD
                    accent_silver = Colors.ACCENT_SILVER
                    neon_cyan = Colors.NEON_CYAN
                    deep_purple = Colors.DEEP_PURPLE
                    
                    print(f"\n\n{gradient_bot}╔{'═'*100}╗{Colors.RESET}")
                    cmd_header_content = f" {accent_gold}▓{Colors.RESET} {Colors.BOLD}💬 COMMAND INTERFACE{Colors.RESET}"
                    cmd_header_display_len = get_display_length(cmd_header_content)
                    cmd_header_spacing = max(1, 98 - cmd_header_display_len - 2)
                    print(f"{gradient_bot}║{Colors.RESET}{cmd_header_content}{' '*cmd_header_spacing} {accent_gold}▓{Colors.RESET}")
                    print(f"{gradient_bot}╠{'═'*100}╣{Colors.RESET}")
                    
                    cmd_desc_content = f" {Colors.DIM}{neon_cyan}▶{Colors.RESET} {Colors.DIM}Enter your command, message, or file operation below{Colors.RESET}"
                    cmd_desc_display_len = get_display_length(cmd_desc_content)
                    cmd_desc_spacing = max(1, 98 - cmd_desc_display_len)
                    print(f"{gradient_bot}║{Colors.RESET}{cmd_desc_content}")
                    print(f"{gradient_bot}║{Colors.RESET} {' '*98}")
                    
                    core_commands = f" 🎯 {accent_silver}Core:{Colors.RESET} {Colors.DIM}project, task, ai config, ai chat, help, status{Colors.RESET}"
                    print(f"{gradient_bot}║{Colors.RESET}{core_commands}")
                    
                    file_ops = f" 📁 {accent_silver}File ops:{Colors.RESET} {Colors.DIM}@path/to/file for direct file operations{Colors.RESET}"
                    print(f"{gradient_bot}║{Colors.RESET}{file_ops}")
                    
                    navigation = f" 🧭 {accent_silver}Navigation:{Colors.RESET} {Colors.DIM}ls, cd, pwd for directory operations{Colors.RESET}"
                    print(f"{gradient_bot}║{Colors.RESET}{navigation}")
                    
                    advanced = f" ⚙️ {accent_silver}Advanced:{Colors.RESET} {Colors.DIM}config, backup, performance, theme{Colors.RESET}"
                    print(f"{gradient_bot}║{Colors.RESET}{advanced}")
                    
                    memory_line = f" 🧠 {accent_silver}Memory:{Colors.RESET} {Colors.DIM}remember, perform, chat clear, remember clear, memory clear{Colors.RESET}"
                    print(f"{gradient_bot}║{Colors.RESET}{memory_line}")
                    
                    print(f"{gradient_bot}║{Colors.RESET} {' '*98}")
                    
                    print(f"{gradient_bot}║{Colors.RESET} {' '*98}")
                    
                    tip_content = f" {Colors.DIM}{accent_gold}💡 Tip:{Colors.RESET} {Colors.DIM}Use 'remember' (no args) to perform all saved entries{Colors.RESET}"
                    tip_display_len = get_display_length(tip_content)
                    tip_spacing = max(1, 98 - tip_display_len)
                    print(f"{gradient_bot}║{Colors.RESET}{tip_content}")
                    print(f"{gradient_bot}╚{'═'*100}╝{Colors.RESET}")
                    
                    print(f"\n{gradient_mid}╔{'═'*100}╗{Colors.RESET}")
                    
                    input_header_content = f" {accent_gold}▓{Colors.RESET} {Colors.BOLD}⚡ INPUT PROMPT{Colors.RESET}"
                    input_header_display_len = get_display_length(input_header_content)
                    input_header_spacing = max(1, 98 - input_header_display_len - 2)
                    print(f"{gradient_mid}║{Colors.RESET}{input_header_content}{' '*input_header_spacing} {accent_gold}▓{Colors.RESET}")
                    print(f"{gradient_mid}╠{'═'*100}╣{Colors.RESET}")
                    
                    input_desc_content = f" {Colors.DIM}Enter your command, message, or file operation below:{Colors.RESET}"
                    input_desc_display_len = get_display_length(input_desc_content)
                    input_desc_spacing = max(1, 98 - input_desc_display_len)
                    print(f"{gradient_mid}║{Colors.RESET}{input_desc_content}")
                    print(f"{gradient_mid}║{Colors.RESET} {' '*98}")
                    print(f"{gradient_mid}║{Colors.RESET} {deep_purple}❯{Colors.RESET} ", end="")
                    
                    user_input = input("").strip()
                    
                    print(f"{gradient_mid}║{Colors.RESET} {' '*98}")
                    print(f"{gradient_mid}╚{'═'*100}╝{Colors.RESET}")
                    
                    if user_input:
                        self.process_command(user_input)
                        
                        if self.auto_save:
                            self.save_persistent_data()
                            
                except KeyboardInterrupt:
                    print(f"\n\n{Colors.YELLOW}Interrupted by user{Colors.RESET}")
                    print(f"Type '{Colors.BOLD}exit{Colors.RESET}' to quit properly")
                    continue
                    
                except EOFError:
                    print(f"\n\n{Colors.YELLOW}Session ended{Colors.RESET}")
                    break
                    
        except Exception as e:
            print(f"\n{Colors.RED}Unexpected error: {e}{Colors.RESET}")
            self.log_message(f"Fatal error: {e}", "error")
        
        finally:
            try:
                self.save_persistent_data()
                print(f"\n{Colors.GREEN}Terminal interface closed - All data saved{Colors.RESET}")
            except Exception as e:
                print(f"\n{Colors.RED}Error saving data on exit: {e}{Colors.RESET}")
    
    def vprint(self, text: str) -> None:
        if self.verbose:
            print(f"{Colors.DIM}[verbose]{Colors.RESET} {text}")

    def _register_commands(self) -> None:
        """Register core commands to a simple registry for future auto-routing/help."""
        try:
            self.command_registry = {
                'project': self.handle_project_command,
                'task': self.handle_task_command,
                'message': self.handle_message_command,
                'session': self.handle_session_command,
                'chat': self.handle_chat_command,
                'run': lambda args: self.handle_run_command(' '.join(args)),
                'status': lambda args: self.handle_status_command(),
                'config': self.handle_config_command,
                'backup': self.handle_backup_command,
                'performance': lambda args: self.handle_performance_command(),
                'theme': self.handle_theme_command,
                'remember': self.handle_remember_command,
                'perform': lambda args: self._route_perform(args),
                'memory': self.handle_memory_command,
                'clear': lambda args: self._handle_clear_command(args),
                'ai': self.handle_ai_command,
            }
        except Exception:
            # Non-fatal; fallback to legacy routing
            self.command_registry = {}

    def _route_perform(self, args: List[str]) -> None:
        """Router for 'perform' supporting clear, index, and range operations."""
        if args:
            if args[0].lower() == 'clear':
                try:
                    data = self._load_remembered()
                    data['last'] = None
                    self._save_remembered(data)
                    print(f"{Colors.GREEN}Cleared last remembered entry{Colors.RESET}")
                except Exception as e:
                    print(f"{Colors.RED}Failed to clear last remembered: {e}{Colors.RESET}")
                return
            if args[0].lower() == 'range' and len(args) >= 3 and args[1].isdigit() and args[2].isdigit():
                a, b = int(args[1]), int(args[2])
                data = self._load_remembered()
                history = data.get('history', [])
                if a > b:
                    a, b = b, a
                if a < 1 or b > len(history):
                    print(f"{Colors.YELLOW}Range out of bounds. Use 1..{len(history)}{Colors.RESET}")
                    return
                count = b - a + 1
                if count > self.max_batch_perform and not self.assume_yes:
                    print(f"{Colors.YELLOW}Batch of {count} exceeds max_batch_perform={self.max_batch_perform}. Adjust config or enable assume_yes.{Colors.RESET}")
                    return
                for n in range(a, b + 1):
                    entry = history[n-1]
                    orig = data.get('last')
                    data['last'] = entry
                    self._save_remembered(data)
                    self.handle_perform_command()
                    # mark executed
                    entry['executed'] = True
                    entry['executed_at'] = datetime.now().isoformat()
                    entry['result'] = {'route': 'unknown', 'status': 'ok'}
                    self._save_remembered(data)
                    data['last'] = orig
                print(f"{Colors.GREEN}Performed range {a}-{b}{Colors.RESET}")
                return
            if args[0].isdigit():
                n = int(args[0])
                data = self._load_remembered()
                history = data.get('history', [])
                if 1 <= n <= len(history):
                    entry = history[n-1]
                    orig = data.get('last')
                    data['last'] = entry
                    self._save_remembered(data)
                    self.handle_perform_command()
                    # mark executed
                    entry['executed'] = True
                    entry['executed_at'] = datetime.now().isoformat()
                    entry['result'] = {'route': 'unknown', 'status': 'ok'}
                    self._save_remembered(data)
                    data['last'] = orig
                else:
                    print(f"{Colors.YELLOW}Index out of range. Use 1..{len(history)}{Colors.RESET}")
                return
        self.handle_perform_command()

    def handle_ai_command(self, args: List[str]) -> None:
        """Handle AI-related commands for Gemini integration."""
        if not args:
            print(f"{Colors.RED}Usage: ai <config|chat|status|help> [options]{Colors.RESET}")
            return
        
        subcommand = args[0].lower()
        
        if subcommand == 'config':
            self._handle_ai_config(args[1:])
        elif subcommand == 'chat':
            self._handle_ai_chat(args[1:])
        elif subcommand == 'status':
            self._handle_ai_status()
        elif subcommand == 'help':
            self._handle_ai_help()
        else:
            print(f"{Colors.RED}Unknown AI subcommand: {subcommand}{Colors.RESET}")
            print(f"Available: config, chat, status, help")
    
    def _handle_ai_config(self, args: List[str]) -> None:
        """Handle AI configuration commands."""
        if not self.ai_manager:
            print(f"{Colors.RED}AI service not available{Colors.RESET}")
            return
        
        if not args:
            print(f"{Colors.RED}Usage: ai config <setup|show|test|add-key|edit-key|delete-key|change-key>{Colors.RESET}")
            return
        
        action = args[0].lower()
        
        if action == 'setup':
            print(f"\n{Colors.CYAN}🤖 AI Configuration Setup{Colors.RESET}")
            print(f"{Colors.DIM}Setting up Google Gemini API integration...{Colors.RESET}\n")
            
            # Check if already configured
            if self.ai_manager.is_configured():
                current_key = self.ai_manager.config.api_key
                masked_key = current_key[:8] + "*" * (len(current_key) - 12) + current_key[-4:] if len(current_key) > 12 else "*" * len(current_key)
                print(f"{Colors.YELLOW}Existing configuration detected:{Colors.RESET}")
                print(f"  API Key: {masked_key}")
                print(f"  Model: {self.ai_manager.config.model.value}")
                print(f"\nChoose an option:")
                print(f"  1. Replace existing configuration")
                print(f"  2. Edit API key only")
                print(f"  3. Cancel")
                
                choice = input(f"\n{Colors.YELLOW}Enter choice (1-3): {Colors.RESET}").strip()
                if choice == '2':
                    self._handle_edit_api_key()
                    return
                elif choice == '3':
                    print(f"{Colors.CYAN}Setup cancelled.{Colors.RESET}")
                    return
                elif choice != '1':
                    print(f"{Colors.RED}Invalid choice. Setup cancelled.{Colors.RESET}")
                    return
                print()  # Add spacing
            
            # Get provider preference
            print(f"\n{Colors.CYAN}Available AI providers:{Colors.RESET}")
            providers = [
                ('gemini', 'Google Gemini (Default)'),
                ('openrouter', 'OpenRouter (Multi-model)')
            ]
            
            for i, (provider_id, description) in enumerate(providers, 1):
                print(f"  {i}. {description}")
            
            provider_choice = input(f"\n{Colors.YELLOW}Choose provider (1-2) [default: 1]: {Colors.RESET}").strip()
            try:
                provider_idx = int(provider_choice) - 1 if provider_choice else 0
                selected_provider = providers[provider_idx][0] if 0 <= provider_idx < len(providers) else providers[0][0]
            except (ValueError, IndexError):
                selected_provider = providers[0][0]
            
            # Get API key
            if selected_provider == 'openrouter':
                api_key = input(f"{Colors.YELLOW}Enter your OpenRouter API key: {Colors.RESET}").strip()
                print(f"\n{Colors.CYAN}Fetching available models from OpenRouter...{Colors.RESET}")
                
                # Fetch models in real-time
                import asyncio
                async def fetch_models():
                    models = await self.ai_manager.fetch_openrouter_models()
                    return models
                
                try:
                    openrouter_models = asyncio.run(fetch_models())
                    if openrouter_models and openrouter_models.get('all'):
                        all_models = openrouter_models.get('all', [])
                        free_models = openrouter_models.get('free', [])
                        paid_models = openrouter_models.get('paid', [])
                        
                        print(f"{Colors.GREEN}✅ Found {len(all_models)} models ({len(free_models)} free, {len(paid_models)} paid){Colors.RESET}")
                        
                        # Ask user which category they want to see
                        print(f"\n{Colors.CYAN}Model categories:{Colors.RESET}")
                        print(f"  1. Free models ({len(free_models)} available)")
                        print(f"  2. Paid models ({len(paid_models)} available)")
                        print(f"  3. All models ({len(all_models)} available)")
                        
                        category_choice = input(f"\n{Colors.YELLOW}Choose category (1-3) [default: 1]: {Colors.RESET}").strip()
                        
                        if category_choice == '2':
                            models_to_show = paid_models
                            category_name = "Paid"
                        elif category_choice == '3':
                            models_to_show = all_models
                            category_name = "All"
                        else:
                            models_to_show = free_models
                            category_name = "Free"
                        
                        # Show models with pagination
                        def show_models_page(models, page_num, page_size=20):
                            start_idx = page_num * page_size
                            end_idx = start_idx + page_size
                            page_models = models[start_idx:end_idx]
                            
                            print(f"\n{Colors.CYAN}{category_name} models (Page {page_num + 1}/{(len(models) - 1) // page_size + 1}):{Colors.RESET}")
                            for i, model in enumerate(page_models, start_idx + 1):
                                model_id = model.get('id', 'unknown')
                                description = model.get('description', model_id)
                                pricing = model.get('pricing', {})
                                try:
                                    prompt_cost = float(pricing.get('prompt', 0)) if pricing.get('prompt') else 0
                                    completion_cost = float(pricing.get('completion', 0)) if pricing.get('completion') else 0
                                    if prompt_cost > 0 or completion_cost > 0:
                                        price_info = f" (${pricing.get('prompt', '0')}/prompt, ${pricing.get('completion', '0')}/completion)"
                                    else:
                                        price_info = " (Free)"
                                except (ValueError, TypeError):
                                    # If we can't parse the pricing, consider it free
                                    price_info = " (Free)"
                                print(f"  {i}. {model_id}{price_info} - {description[:100]}{'...' if len(description) > 100 else ''}")
                            
                            if len(models) > end_idx:
                                print(f"\n{Colors.DIM}Enter model number or 'n' for next page, 'p' for previous page, or 'q' to quit browsing{Colors.RESET}")
                            else:
                                print(f"\n{Colors.DIM}Enter model number or 'q' to quit browsing{Colors.RESET}")
                        
                        # Pagination loop
                        current_page = 0
                        page_size = 20
                        selected_model = None
                        
                        while selected_model is None:
                            show_models_page(models_to_show, current_page, page_size)
                            
                            user_input = input(f"\n{Colors.YELLOW}Enter choice: {Colors.RESET}").strip().lower()
                            
                            if user_input == 'q':
                                selected_model = "openrouter/auto"
                                break
                            elif user_input == 'n' and (current_page + 1) * page_size < len(models_to_show):
                                current_page += 1
                            elif user_input == 'p' and current_page > 0:
                                current_page -= 1
                            elif user_input.isdigit():
                                model_idx = int(user_input) - 1
                                if 0 <= model_idx < len(models_to_show):
                                    selected_model = models_to_show[model_idx].get('id', 'unknown')
                                else:
                                    print(f"{Colors.RED}Invalid model number. Please try again.{Colors.RESET}")
                            else:
                                print(f"{Colors.RED}Invalid input. Please try again.{Colors.RESET}")
                        
                        # If no model was selected, use default
                        if selected_model is None:
                            selected_model = "openrouter/auto"
                    else:
                        print(f"{Colors.YELLOW}Could not fetch models, using default{Colors.RESET}")
                        selected_model = "openrouter/auto"
                except Exception as e:
                    print(f"{Colors.YELLOW}⚠ Could not fetch models: {e}{Colors.RESET}")
                    selected_model = "openrouter/auto"
            else:
                api_key = input(f"{Colors.YELLOW}Enter your Gemini API key: {Colors.RESET}").strip()
                
                # Get model preference
                print(f"\n{Colors.CYAN}Available models (latest versions only):{Colors.RESET}")
                models = [
                    ('gemini-2.0-flash-exp', 'Gemini 2.0 Flash (Latest Experimental)'),
                    ('gemini-1.5-pro-latest', 'Gemini 1.5 Pro (Latest)'),
                    ('gemini-1.5-flash-latest', 'Gemini 1.5 Flash (Latest)'),
                    ('gemini-1.5-flash-8b-latest', 'Gemini 1.5 Flash 8B (Latest Fastest)')
                ]
                
                for i, (model_id, description) in enumerate(models, 1):
                    print(f"  {i}. {description}")
                
                model_choice = input(f"\n{Colors.YELLOW}Choose model (1-4) [default: 1]: {Colors.RESET}").strip()
                try:
                    model_idx = int(model_choice) - 1 if model_choice else 0
                    selected_model = models[model_idx][0] if 0 <= model_idx < len(models) else models[0][0]
                except (ValueError, IndexError):
                    selected_model = models[0][0]
            
            if not api_key:
                print(f"{Colors.RED}API key is required{Colors.RESET}")
                return
            
            # Get additional settings
            max_tokens = input(f"{Colors.YELLOW}Max tokens [default: 4000]: {Colors.RESET}").strip()
            try:
                max_tokens = int(max_tokens) if max_tokens else 4000
            except ValueError:
                max_tokens = 4000
            
            temperature = input(f"{Colors.YELLOW}Temperature (0.0-1.0) [default: 0.7]: {Colors.RESET}").strip()
            try:
                temperature = float(temperature) if temperature else 0.7
            except ValueError:
                temperature = 0.7
            
            # Validate API key before configuration
            print(f"\n{Colors.CYAN}Validating API key...{Colors.RESET}")
            
            import asyncio
            async def validate_key():
                # Determine provider for validation
                from ai_service import AIProvider
                provider = AIProvider.OPENROUTER if selected_provider == 'openrouter' else AIProvider.GEMINI
                is_valid, message = await self.ai_manager.validate_api_key(api_key, selected_model, provider)
                return is_valid, message
            
            try:
                is_valid, validation_message = asyncio.run(validate_key())
                if not is_valid:
                    print(f"{Colors.RED}❌ {validation_message}{Colors.RESET}")
                    print(f"{Colors.YELLOW}Please check your API key and try again.{Colors.RESET}")
                    return
                else:
                    print(f"{Colors.GREEN}✅ {validation_message}{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.YELLOW}⚠ Could not validate API key: {e}{Colors.RESET}")
                confirm = input(f"{Colors.YELLOW}Continue anyway? (y/N): {Colors.RESET}").strip().lower()
                if confirm not in ['y', 'yes']:
                    print(f"{Colors.CYAN}Setup cancelled.{Colors.RESET}")
                    return
            
            # Configure the AI service with provider
            from ai_service import AIProvider
            provider_enum = AIProvider.OPENROUTER if selected_provider == 'openrouter' else AIProvider.GEMINI
            if self.ai_manager.configure(api_key, selected_model, max_tokens, temperature, provider_enum):
                print(f"\n{Colors.GREEN}✅ AI service configured successfully!{Colors.RESET}")
                self._show_api_key_status()
                print(f"\n{Colors.CYAN}You can now use 'ai chat <message>' to interact with AI{Colors.RESET}")
                print(f"{Colors.DIM}Tip: Use 'ai config test' to verify your configuration{Colors.RESET}")
            else:
                print(f"\n{Colors.RED}❌ Failed to configure AI service{Colors.RESET}")
        
        elif action == 'show':
            if self.ai_manager.is_configured():
                config = self.ai_manager.config
                print(f"\n{Colors.CYAN}🤖 AI Configuration{Colors.RESET}")
                print(f"  Provider: {config.provider.value}")
                print(f"  Model: {config.model.value}")
                print(f"  Max tokens: {config.max_tokens}")
                print(f"  Temperature: {config.temperature}")
                print(f"  Context window: {config.context_window}")
                print(f"  Context integration: {'Enabled' if config.enable_context_integration else 'Disabled'}")
                print(f"  Streaming: {'Enabled' if config.enable_streaming else 'Disabled'}")
                
                # Show additional provider-specific information
                if config.provider.value == 'openrouter':
                    print(f"  {Colors.DIM}Note: OpenRouter provides access to 100+ models{Colors.RESET}")
                    print(f"  {Colors.DIM}Use 'ai config setup' to change model{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}AI service not configured. Use 'ai config setup' to configure.{Colors.RESET}")
        
        elif action == 'test':
            if not self.ai_manager.is_configured():
                print(f"{Colors.RED}AI service not configured. Use 'ai config setup' first.{Colors.RESET}")
                return
            
            print(f"{Colors.CYAN}🚀 Testing AI connection...{Colors.RESET}")
            
            import asyncio
            async def test_ai():
                try:
                    response = await self.ai_manager.chat("Hello! Please respond with a brief greeting.", use_context=False)
                    if response.success:
                        # Use the cool design for displaying the response
                        tokens = response.usage.get('totalTokenCount', 0) if response.usage else 0
                        self._display_ai_response(response.content, response.model, response.response_time, tokens)
                    else:
                        self._display_cool_response("❌ AI TEST FAILED", response.error)
                except Exception as e:
                    print(f"{Colors.RED}❌ AI test error: {e}{Colors.RESET}")
            
            asyncio.run(test_ai())
        
        elif action == 'add-key':
            self._handle_add_api_key()
        elif action == 'edit-key':
            self._handle_edit_api_key()
        elif action == 'delete-key':
            self._handle_delete_api_key()
        elif action == 'change-key':
            self._handle_change_api_key()
        
        else:
            print(f"{Colors.RED}Unknown config action: {action}{Colors.RESET}")
            print(f"Available: setup, show, test, add-key, edit-key, delete-key, change-key")
    
    def _handle_add_api_key(self) -> None:
        """Handle adding a new API key."""
        print(f"\n{Colors.CYAN}🔑 Add API Key{Colors.RESET}")
        
        # Check if already configured
        if self.ai_manager.is_configured():
            current_key = self.ai_manager.config.api_key
            masked_key = current_key[:8] + "*" * (len(current_key) - 12) + current_key[-4:] if len(current_key) > 12 else "*" * len(current_key)
            print(f"\n{Colors.YELLOW}Current API key: {masked_key}{Colors.RESET}")
            
            replace = input(f"{Colors.YELLOW}Replace existing key? (y/N): {Colors.RESET}").strip().lower()
            if replace not in ['y', 'yes']:
                print(f"{Colors.CYAN}Operation cancelled.{Colors.RESET}")
                return
        
        # Get provider preference
        print(f"\n{Colors.CYAN}Available AI providers:{Colors.RESET}")
        providers = [
            ('gemini', 'Google Gemini (Default)'),
            ('openrouter', 'OpenRouter (Multi-model)')
        ]
        
        for i, (provider_id, description) in enumerate(providers, 1):
            print(f"  {i}. {description}")
        
        provider_choice = input(f"\n{Colors.YELLOW}Choose provider (1-2) [default: 1]: {Colors.RESET}").strip()
        try:
            provider_idx = int(provider_choice) - 1 if provider_choice else 0
            selected_provider = providers[provider_idx][0] if 0 <= provider_idx < len(providers) else providers[0][0]
        except (ValueError, IndexError):
            selected_provider = providers[0][0]
        
        # Get API key based on provider
        if selected_provider == 'openrouter':
            api_key = input(f"{Colors.YELLOW}Enter your OpenRouter API key: {Colors.RESET}").strip()
        else:
            api_key = input(f"{Colors.YELLOW}Enter your Gemini API key: {Colors.RESET}").strip()
        
        if not api_key:
            print(f"{Colors.RED}API key cannot be empty{Colors.RESET}")
            return
        
        # Validate the API key
        print(f"\n{Colors.CYAN}Validating API key...{Colors.RESET}")
        
        import asyncio
        async def validate_new_key():
            # Determine model to test
            if self.ai_manager.is_configured():
                model_to_test = self.ai_manager.config.model.value
                provider = self.ai_manager.config.provider
            else:
                model_to_test = "gemini-1.5-flash-latest" if selected_provider != 'openrouter' else "openrouter/auto"
                from ai_service import AIProvider
                provider = AIProvider.OPENROUTER if selected_provider == 'openrouter' else AIProvider.GEMINI
            
            is_valid, message = await self.ai_manager.validate_api_key(api_key, model_to_test, provider)
            return is_valid, message
        
        try:
            is_valid, validation_message = asyncio.run(validate_new_key())
            if not is_valid:
                print(f"{Colors.RED}❌ {validation_message}{Colors.RESET}")
                confirm = input(f"{Colors.YELLOW}Save invalid key anyway? (y/N): {Colors.RESET}").strip().lower()
                if confirm not in ['y', 'yes']:
                    print(f"{Colors.CYAN}Operation cancelled.{Colors.RESET}")
                    return
            else:
                print(f"{Colors.GREEN}✅ {validation_message}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠ Could not validate API key: {e}{Colors.RESET}")
            confirm = input(f"{Colors.YELLOW}Continue anyway? (y/N): {Colors.RESET}").strip().lower()
            if confirm not in ['y', 'yes']:
                print(f"{Colors.CYAN}Operation cancelled.{Colors.RESET}")
                return

        # Use existing config or create new one
        if self.ai_manager.is_configured():
            config = self.ai_manager.config
            success = self.ai_manager.configure(
                api_key=api_key,
                model=config.model.value,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                provider=config.provider
            )
        else:
            # Create new config with latest defaults
            from ai_service import AIProvider
            provider_enum = AIProvider.OPENROUTER if selected_provider == 'openrouter' else AIProvider.GEMINI
            default_model = "openrouter/auto" if selected_provider == 'openrouter' else "gemini-1.5-flash-latest"
            success = self.ai_manager.configure(
                api_key=api_key,
                model=default_model,
                max_tokens=4000,
                temperature=0.7,
                provider=provider_enum
            )

        if success:
            self._display_cool_response("✅ API KEY ADDED", "API key added successfully!", {"Status": "Success"})
            self._show_api_key_status()
        else:
            self._display_cool_response("❌ ADD API KEY FAILED", "Failed to add API key", {"Status": "Error"})
    
    def _handle_edit_api_key(self) -> None:
        """Handle editing the current API key."""
        if not self.ai_manager.is_configured():
            self._display_cool_response("❌ CONFIGURATION ERROR", "No API key configured. Use 'ai config add-key' first.")
            return
        
        self._display_cool_response("🔎 EDIT API KEY", "Editing current API key configuration")
        
        current_key = self.ai_manager.config.api_key
        masked_key = current_key[:8] + "*" * (len(current_key) - 12) + current_key[-4:] if len(current_key) > 12 else "*" * len(current_key)
        print(f"Current key: {masked_key}")
        
        # Show current provider
        current_provider = self.ai_manager.config.provider.value
        print(f"{Colors.YELLOW}Current provider: {current_provider}{Colors.RESET}")
        
        new_key = input(f"\n{Colors.YELLOW}Enter new API key (or press Enter to cancel): {Colors.RESET}").strip()
        if not new_key:
            print(f"{Colors.CYAN}Edit cancelled.{Colors.RESET}")
            return
        
        # Validate the new API key
        print(f"\n{Colors.CYAN}Validating new API key...{Colors.RESET}")
        
        import asyncio
        async def validate_edit_key():
            is_valid, message = await self.ai_manager.validate_api_key(new_key, self.ai_manager.config.model.value, self.ai_manager.config.provider)
            return is_valid, message
        
        try:
            is_valid, validation_message = asyncio.run(validate_edit_key())
            if not is_valid:
                print(f"{Colors.RED}❌ {validation_message}{Colors.RESET}")
                confirm = input(f"{Colors.YELLOW}Save invalid key anyway? (y/N): {Colors.RESET}").strip().lower()
                if confirm not in ['y', 'yes']:
                    print(f"{Colors.CYAN}Edit cancelled.{Colors.RESET}")
                    return
            else:
                print(f"{Colors.GREEN}✅ {validation_message}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠ Could not validate API key: {e}{Colors.RESET}")
            confirm = input(f"{Colors.YELLOW}Continue anyway? (y/N): {Colors.RESET}").strip().lower()
            if confirm not in ['y', 'yes']:
                print(f"{Colors.CYAN}Edit cancelled.{Colors.RESET}")
                return

        config = self.ai_manager.config
        success = self.ai_manager.configure(
            api_key=new_key,
            model=config.model.value,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            provider=config.provider
        )
        
        if success:
            self._display_cool_response("✅ API KEY UPDATED", "API key updated successfully!", {"Status": "Success"})
            self._show_api_key_status()
        else:
            self._display_cool_response("❌ UPDATE API KEY FAILED", "Failed to update API key", {"Status": "Error"})
    
    def _handle_delete_api_key(self) -> None:
        """Handle deleting the API key."""
        if not self.ai_manager.is_configured():
            self._display_cool_response("❌ CONFIGURATION ERROR", "No API key configured to delete.")
            return
        
        self._display_cool_response("🗑️ DELETE API KEY", "Deleting current API key configuration")
        
        current_key = self.ai_manager.config.api_key
        masked_key = current_key[:8] + "*" * (len(current_key) - 12) + current_key[-4:] if len(current_key) > 12 else "*" * len(current_key)
        print(f"Current key: {masked_key}")
        
        confirm = input(f"\n{Colors.YELLOW}Are you sure you want to delete the API key? (y/N): {Colors.RESET}").strip().lower()
        if confirm not in ['y', 'yes']:
            print(f"{Colors.CYAN}Deletion cancelled.{Colors.RESET}")
            return
        
        # Delete config file
        try:
            if self.ai_manager.config_file.exists():
                self.ai_manager.config_file.unlink()
            self.ai_manager.config = None
            self._display_cool_response("✅ API KEY DELETED", "API key deleted successfully!", {"Status": "Success"})
            self._display_cool_response("ℹ️ NEXT STEPS", "Use 'ai config add-key' to configure a new key.")
        except Exception as e:
            self._display_cool_response("❌ DELETE API KEY FAILED", f"Failed to delete API key: {e}", {"Status": "Error"})
    
    def _handle_change_api_key(self) -> None:
        """Handle changing to a different API key (alias for edit)."""
        self._handle_edit_api_key()
    
    def _show_api_key_status(self) -> None:
        """Show current API key status with security masking."""
        if self.ai_manager.is_configured():
            config = self.ai_manager.config
            api_key = config.api_key
            
            # Mask the API key for security
            if len(api_key) > 12:
                masked_key = api_key[:8] + "*" * (len(api_key) - 12) + api_key[-4:]
            else:
                masked_key = "*" * len(api_key)
            
            print(f"\n{Colors.CYAN}Current Configuration:{Colors.RESET}")
            print(f"  🔑 API Key: {masked_key}")
            print(f"  🤖 Model: {config.model}")
            print(f"  📊 Max Tokens: {config.max_tokens}")
            print(f"  🌡️ Temperature: {config.temperature}")
        else:
            print(f"{Colors.YELLOW}No API key configured{Colors.RESET}")
    
    def _display_ai_response(self, response_content: str, model: str = "", response_time: float = 0.0, tokens: int = 0) -> None:
        """Display AI response with a cool design."""
        # Create a fancy border
        border = "═" * 77
        print(f"\n{Colors.CYAN}╔{border}╗{Colors.RESET}")
        print(f"{Colors.CYAN}║{Colors.RESET} {Colors.BOLD}{Colors.GREEN}🤖 AI RESPONSE{Colors.RESET} {Colors.DIM}{' ' * 61}║{Colors.RESET}")
        print(f"{Colors.CYAN}╠{border}╣{Colors.RESET}")
        
        # Display the response content with word wrapping
        lines = response_content.split('\n')
        for line in lines:
            if len(line) > 75:
                # Wrap long lines
                words = line.split()
                current_line = ""
                for word in words:
                    if len(current_line + word) <= 75:
                        current_line += word + " "
                    else:
                        print(f"{Colors.CYAN}║{Colors.RESET} {current_line:<75} {Colors.CYAN}║{Colors.RESET}")
                        current_line = word + " "
                if current_line:
                    print(f"{Colors.CYAN}║{Colors.RESET} {current_line:<75} {Colors.CYAN}║{Colors.RESET}")
            else:
                print(f"{Colors.CYAN}║{Colors.RESET} {line:<75} {Colors.CYAN}║{Colors.RESET}")
        
        # Display metadata if available
        if model or response_time > 0 or tokens > 0:
            print(f"{Colors.CYAN}╠{border}╣{Colors.RESET}")
            metadata_parts = []
            if model:
                metadata_parts.append(f"Model: {model}")
            if response_time > 0:
                metadata_parts.append(f"Time: {response_time:.2f}s")
            if tokens > 0:
                metadata_parts.append(f"Tokens: {tokens}")
            
            metadata_str = " | ".join(metadata_parts)
            print(f"{Colors.CYAN}║{Colors.RESET} {Colors.DIM}{metadata_str:<75} {Colors.CYAN}║{Colors.RESET}")
        
        print(f"{Colors.CYAN}╚{border}╝{Colors.RESET}")
    
    def _display_cool_response(self, title: str, response_content: str, metadata: Dict[str, Any] = None) -> None:
        """Display any response with a cool design."""
        # Create a fancy border
        border = "═" * 77
        print(f"\n{Colors.CYAN}╔{border}╗{Colors.RESET}")
        print(f"{Colors.CYAN}║{Colors.RESET} {Colors.BOLD}{Colors.GREEN}{title}{Colors.RESET} {Colors.DIM}{' ' * (77 - len(title) - 3)}║{Colors.RESET}")
        print(f"{Colors.CYAN}╠{border}╣{Colors.RESET}")
        
        # Display the response content with word wrapping
        lines = response_content.split('\n')
        for line in lines:
            if len(line) > 75:
                # Wrap long lines
                words = line.split()
                current_line = ""
                for word in words:
                    if len(current_line + word) <= 75:
                        current_line += word + " "
                    else:
                        print(f"{Colors.CYAN}║{Colors.RESET} {current_line:<75} {Colors.CYAN}║{Colors.RESET}")
                        current_line = word + " "
                if current_line:
                    print(f"{Colors.CYAN}║{Colors.RESET} {current_line:<75} {Colors.CYAN}║{Colors.RESET}")
            else:
                print(f"{Colors.CYAN}║{Colors.RESET} {line:<75} {Colors.CYAN}║{Colors.RESET}")
        
        # Display metadata if available
        if metadata:
            print(f"{Colors.CYAN}╠{border}╣{Colors.RESET}")
            metadata_parts = []
            for key, value in metadata.items():
                metadata_parts.append(f"{key}: {value}")
            
            metadata_str = " | ".join(metadata_parts)
            print(f"{Colors.CYAN}║{Colors.RESET} {Colors.DIM}{metadata_str:<75} {Colors.CYAN}║{Colors.RESET}")
        
        print(f"{Colors.CYAN}╚{border}╝{Colors.RESET}")
    
    def _handle_ai_chat(self, args: List[str]) -> None:
        """Handle AI chat commands with codebase understanding capability."""
        if not self.ai_manager:
            print(f"{Colors.RED}AI service not available{Colors.RESET}")
            return
        
        if not self.ai_manager.is_configured():
            print(f"{Colors.RED}AI service not configured. Use 'ai config setup' first.{Colors.RESET}")
            return
        
        if not args:
            print(f"{Colors.RED}Usage: ai chat <message>{Colors.RESET}")
            return
        
        message = ' '.join(args)
        print(f"\n{Colors.CYAN}🚀 Sending message to AI...{Colors.RESET}")
        
        import asyncio
        async def chat_with_ai():
            try:
                response = await self.ai_manager.chat(message, use_context=True)
                
                if response.success:
                    # Use the cool design for displaying the response
                    tokens = response.usage.get('totalTokenCount', 0) if response.usage else 0
                    self._display_ai_response(response.content, response.model, response.response_time, tokens)
                    
                    # Log the interaction to chat manager for context preservation
                    if hasattr(self.ai_manager, 'service') and self.ai_manager.service:
                        service = self.ai_manager.service
                        if hasattr(service, 'chat_manager') and service.chat_manager:
                            service.chat_manager.add_message("user", message)
                            service.chat_manager.add_message("assistant", response.content)
                    
                    # Also log to terminal messages
                    self.log_message(f"AI Chat - User: {message}", "ai_user")
                    self.log_message(f"AI Chat - Assistant: {response.content[:200]}...", "ai_assistant")
                    
                else:
                    print(f"\n{Colors.RED}❌ AI Error: {response.error}{Colors.RESET}")
                    self.log_message(f"AI Chat Error: {response.error}", "ai_error")
                    
            except Exception as e:
                print(f"\n{Colors.RED}❌ Chat error: {e}{Colors.RESET}")
                self.log_message(f"AI Chat Exception: {e}", "ai_error")
        
        asyncio.run(chat_with_ai())
    
    def _handle_ai_status(self) -> None:
        """Show AI service status."""
        if not self.ai_manager:
            print(f"{Colors.RED}AI service not available{Colors.RESET}")
            return
        
        print(f"\n{Colors.CYAN}🤖 AI Service Status{Colors.RESET}")
        
        if self.ai_manager.is_configured():
            config = self.ai_manager.config
            api_key = config.api_key
            
            # Mask the API key for security
            if len(api_key) > 12:
                masked_key = api_key[:8] + "*" * (len(api_key) - 12) + api_key[-4:]
            else:
                masked_key = "*" * len(api_key)
            
            print(f"  Status: {Colors.GREEN}Configured{Colors.RESET}")
            print(f"  🔑 API Key: {masked_key}")
            print(f"  🤖 Provider: {config.provider.value}")
            print(f"  📊 Model: {config.model.value}")
            print(f"  📊 Max Tokens: {config.max_tokens}")
            print(f"  🌡️ Temperature: {config.temperature}")
            print(f"  🔗 Context integration: {'Enabled' if config.enable_context_integration else 'Disabled'}")
            print(f"  📡 Streaming: {'Enabled' if config.enable_streaming else 'Disabled'}")
        else:
            print(f"  Status: {Colors.YELLOW}Not configured{Colors.RESET}")
            print(f"  🔧 Use 'ai config setup' or 'ai config add-key' to configure")
        
        # Show integration status
        print(f"\n{Colors.CYAN}Integration Status:{Colors.RESET}")
        print(f"  🧠 Context manager: {'Available' if hasattr(self, 'ctx') else 'Not available'}")
        print(f"  💬 Chat manager: {'Available' if hasattr(self, 'chat') else 'Not available'}")
        print(f"  💾 Terminal persistence: {'Available' if hasattr(self, 'session_bridge') else 'Not available'}")
        
        # Show available commands
        print(f"\n{Colors.CYAN}Available Commands:{Colors.RESET}")
        print(f"  🔧 Configuration: setup, show, test, add-key, edit-key, delete-key")
        print(f"  💬 Interaction: chat, status, help")
    
    def _handle_ai_help(self) -> None:
        """Show AI command help."""
        print(f"\n{Colors.CYAN}🤖 AI Commands Help{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Configuration & Setup:{Colors.RESET}")
        print(f"  ai config setup     - Interactive setup with latest Gemini models and validation")
        print(f"  ai config show      - Show current configuration with masked API key")
        print(f"  ai config test      - Test AI connection with current model")
        print(f"\n{Colors.YELLOW}API Key Management:{Colors.RESET}")
        print(f"  ai config add-key   - Add or replace API key with real-time validation")
        print(f"  ai config edit-key  - Edit current API key with validation")
        print(f"  ai config change-key - Change to different API key (alias for edit)")
        print(f"  ai config delete-key - Remove API key and configuration completely")
        print(f"\n{Colors.YELLOW}AI Interaction:{Colors.RESET}")
        print(f"  ai chat <message>   - Chat with AI using project context")
        print(f"  ai status           - Show detailed AI service and integration status")
        print(f"  ai help             - Show this comprehensive help")
        print(f"\n{Colors.GREEN}Available Models (Latest Only):{Colors.RESET}")
        print(f"  🚀 Gemini 2.0 Flash (Latest Experimental)")
        print(f"  ⚡ Gemini 1.5 Pro (Latest Stable)")
        print(f"  🔥 Gemini 1.5 Flash (Latest Stable) - Default")
        print(f"  🏃 Gemini 1.5 Flash 8B (Fastest)")
        print(f"\n{Colors.GREEN}Quick Start Examples:{Colors.RESET}")
        print(f"  ai config setup")
        print(f"  ai config add-key")
        print(f"  ai chat How do I create a Python virtual environment?")
        print(f"  ai chat Explain this code: def fibonacci(n): return n if n <= 1 else fib(n-1) + fib(n-2)")
        print(f"  ai chat Help me debug this error: NameError")
        print(f"\n{Colors.CYAN}Key Features:{Colors.RESET}")
        print(f"  ✨ Real-time API key validation during setup")
        print(f"  🔒 Secure API key storage with masking")
        print(f"  🧠 Codebase understanding with project file analysis")
        print(f"  🔄 Seamless integration with terminal workflow")
        print(f"  🚀 Always uses latest Gemini models")
        print(f"\n{Colors.DIM}Note: AI responses use context from your current project and session{Colors.RESET}")

        print(f"  🌐 Multi-provider support (Gemini & OpenRouter)")
        print(f"\n{Colors.DIM}Note: AI responses use context from your current project and session{Colors.RESET}")

    def handle_build_command(self, args: List[str]) -> None:
        """Handle universal building agent commands with AI integration."""
        if not self.building_agent and not self.advanced_building_agent:
            print(f"{Colors.RED}Building agent not available{Colors.RESET}")
            return
        
        if not args:
            print(f"{Colors.RED}Usage: build <command> [options]{Colors.RESET}")
            print(f"\n{Colors.CYAN}🔨 Project Creation:{Colors.RESET}")
            print(f"  web <name>           - Create web application (React, Vue, Angular)")
            print(f"  api <name>           - Create API server (Node.js, Python, Go)")
            print(f"  desktop <name>       - Create desktop app (Electron, Tauri)")
            print(f"  mobile <name>        - Create mobile app (React Native, Flutter)")
            print(f"  cli <name>           - Create CLI tool")
            print(f"  library <name>       - Create reusable library")
            print(f"\n{Colors.CYAN}🧠 AI-Powered Generation:{Colors.RESET}")
            print(f"  describe '<description>' - Generate project from natural language")
            print(f"  setup-ai <provider>     - Setup AI provider (openrouter, gemini)")
            print(f"  ai-status              - Show AI provider configuration")
            print(f"\n{Colors.CYAN}🔍 Analysis & Intelligence:{Colors.RESET}")
            print(f"  detect              - Detect current project type")
            print(f"  suggest             - Get build suggestions")
            print(f"  analyze             - Analyze generated code")
            print(f"  status              - Show terminal and build status")
            print(f"\n{Colors.CYAN}📊 History & Management:{Colors.RESET}")
            print(f"  history             - Show build history")
            print(f"  templates           - List available templates")
            print(f"  check-updates       - Check for AI model updates")
            print(f"  browse-models       - Browse and explore available AI models")
            print(f"\n{Colors.CYAN}🧹 Clear & Reset:{Colors.RESET}")
            print(f"  clear-history       - Clear build generation history")
            print(f"  clear-cache         - Clear AI models cache")
            print(f"  clear-configs       - Clear AI provider configurations")
            print(f"  clear-all           - Clear all building agent data")
            return
        
        subcommand = args[0].lower()
        
        # Route to appropriate handler
        if subcommand == 'describe':
            self._handle_build_describe(args[1:] if len(args) > 1 else [])
        elif subcommand == 'setup-ai':
            self._handle_build_setup_ai(args[1:] if len(args) > 1 else [])
        elif subcommand == 'ai-status':
            self._handle_build_ai_status()
        elif subcommand == 'analyze':
            self._handle_build_analyze(args[1:] if len(args) > 1 else [])
        elif subcommand == 'status':
            self._handle_build_status()
        elif subcommand == 'check-updates':
            self._handle_build_check_updates()
        elif subcommand == 'browse-models':
            self._handle_build_browse_models()
        elif subcommand == 'clear-history':
            self._handle_build_clear_history()
        elif subcommand == 'clear-cache':
            self._handle_build_clear_cache()
        elif subcommand == 'clear-configs':
            self._handle_build_clear_configs()
        elif subcommand == 'clear-all':
            self._handle_build_clear_all()
        elif subcommand == 'detect':
            self._handle_build_detect()
        elif subcommand == 'suggest':
            self._handle_build_suggest()
        elif subcommand == 'history':
            self._handle_build_history()
        elif subcommand == 'templates':
            self._handle_build_templates()
        elif subcommand in ['web', 'api', 'desktop', 'mobile', 'cli', 'library', 'microservice', 'fullstack']:
            if len(args) < 2:
                print(f"{Colors.RED}Usage: build {subcommand} <name> [--framework <framework>]{Colors.RESET}")
                return
            self._handle_build_create(subcommand, args[1:])
        else:
            print(f"{Colors.RED}Unknown build command: {subcommand}{Colors.RESET}")
            print(f"Use 'build' without arguments to see available commands")
    
    def _handle_build_detect(self) -> None:
        """Detect current project type and framework."""
        try:
            build_type, framework, info = self.building_agent.detect_project_type()
            
            print(f"\n{Colors.CYAN}🔍 Project Detection Results:{Colors.RESET}")
            print(f"  Build Type: {Colors.GREEN}{build_type.value}{Colors.RESET}")
            print(f"  Framework: {Colors.GREEN}{framework.value if framework else 'default'}{Colors.RESET}")
            print(f"  Confidence: {Colors.YELLOW}{info['confidence']:.1%}{Colors.RESET}")
            
            if info['indicators']:
                print(f"\n{Colors.CYAN}Detection Indicators:{Colors.RESET}")
                for indicator in info['indicators']:
                    print(f"  • {indicator}")
            
            if info['files']:
                print(f"\n{Colors.DIM}Files found: {', '.join(info['files'][:10])}{Colors.RESET}")
                if len(info['files']) > 10:
                    print(f"{Colors.DIM}  ... and {len(info['files']) - 10} more{Colors.RESET}")
                    
        except Exception as e:
            print(f"{Colors.RED}Detection failed: {e}{Colors.RESET}")
    
    def _handle_build_suggest(self) -> None:
        """Get intelligent build suggestions."""
        try:
            suggestions = self.building_agent.get_build_suggestions()
            
            if not suggestions:
                print(f"{Colors.YELLOW}No build suggestions available{Colors.RESET}")
                return
            
            print(f"\n{Colors.CYAN}🚀 Build Suggestions:{Colors.RESET}")
            for i, suggestion in enumerate(suggestions[:8], 1):
                type_icon = "🔨" if suggestion['type'] == 'create' else "⚡"
                print(f"  {i}. {type_icon} {Colors.BOLD}{suggestion['title']}{Colors.RESET}")
                print(f"     {Colors.DIM}{suggestion['description']}{Colors.RESET}")
                print(f"     {Colors.GREEN}Command:{Colors.RESET} {suggestion['command']}")
                print()
                
        except Exception as e:
            print(f"{Colors.RED}Failed to get suggestions: {e}{Colors.RESET}")
    
    def _handle_build_history(self) -> None:
        """Show build history."""
        try:
            history = self.building_agent.get_build_history()
            
            if not history:
                print(f"{Colors.YELLOW}No build history found{Colors.RESET}")
                return
            
            print(f"\n{Colors.CYAN}📚 Build History:{Colors.RESET}")
            for entry in history[-10:]:  # Show last 10
                config = entry['config']
                status = entry['status']
                timestamp = entry['timestamp'][:19]  # Remove microseconds
                
                status_icon = "✅" if status == "completed" else "❌" if status == "failed" else "⏳"
                status_color = Colors.GREEN if status == "completed" else Colors.RED if status == "failed" else Colors.YELLOW
                
                print(f"  {status_icon} {Colors.BOLD}{config['name']}{Colors.RESET}")
                print(f"    Type: {config['build_type']} | Framework: {config.get('framework', 'default')}")
                print(f"    Status: {status_color}{status}{Colors.RESET} | {timestamp}")
                print()
                
        except Exception as e:
            print(f"{Colors.RED}Failed to get build history: {e}{Colors.RESET}")
    
    def _handle_build_templates(self) -> None:
        """List available project templates."""
        try:
            if hasattr(self.building_agent, 'project_templates') and self.building_agent.project_templates:
                templates = self.building_agent.project_templates.get_available_templates()
                
                if not templates:
                    print(f"{Colors.YELLOW}No templates available{Colors.RESET}")
                    return
                
                print(f"\n{Colors.CYAN}📋 Available Templates:{Colors.RESET}")
                for template in templates:
                    print(f"  • {Colors.BOLD}{template['name']}{Colors.RESET}")
                    print(f"    Key: {template['key']} | Type: {template['build_type']} | Framework: {template['framework']}")
                    if template['description']:
                        print(f"    {Colors.DIM}{template['description']}{Colors.RESET}")
                    print()
            else:
                print(f"{Colors.YELLOW}Template system not available{Colors.RESET}")
                
        except Exception as e:
            print(f"{Colors.RED}Failed to list templates: {e}{Colors.RESET}")
    
    def _handle_build_create(self, build_type: str, args: List[str]) -> None:
        """Handle project creation."""
        try:
            project_name = args[0]
            
            # Parse additional arguments
            framework = None
            language = "javascript"
            features = []
            
            i = 1
            while i < len(args):
                if args[i] == '--framework' and i + 1 < len(args):
                    framework_str = args[i + 1]
                    try:
                        from building_agent import Framework
                        framework = Framework(framework_str)
                    except ValueError:
                        print(f"{Colors.YELLOW}Unknown framework: {framework_str}. Using default.{Colors.RESET}")
                    i += 2
                elif args[i] == '--language' and i + 1 < len(args):
                    language = args[i + 1]
                    i += 2
                elif args[i] == '--feature' and i + 1 < len(args):
                    features.append(args[i + 1])
                    i += 2
                else:
                    i += 1
            
            # Create build configuration
            from building_agent import BuildConfig, BuildType
            config = BuildConfig(
                name=project_name,
                build_type=BuildType(build_type),
                framework=framework,
                language=language,
                features=features
            )
            
            print(f"\n{Colors.CYAN}🔨 Creating {build_type} project '{project_name}'...{Colors.RESET}")
            if framework:
                print(f"Framework: {framework.value}")
            if language != "javascript":
                print(f"Language: {language}")
            if features:
                print(f"Features: {', '.join(features)}")
            
            # Execute build
            import asyncio
            result = asyncio.run(self.building_agent.build_project(config))
            
            if result['success']:
                print(f"\n{Colors.GREEN}✅ {result['message']}{Colors.RESET}")
                
                if result['files_created']:
                    print(f"\n{Colors.CYAN}Files created:{Colors.RESET}")
                    for file_path in result['files_created'][:10]:  # Show first 10
                        print(f"  • {file_path}")
                    if len(result['files_created']) > 10:
                        print(f"  ... and {len(result['files_created']) - 10} more files")
                
                if result['next_steps']:
                    print(f"\n{Colors.CYAN}Next steps:{Colors.RESET}")
                    for i, step in enumerate(result['next_steps'], 1):
                        print(f"  {i}. {step}")
                        
            else:
                print(f"\n{Colors.RED}❌ {result['message']}{Colors.RESET}")
                
        except Exception as e:
            print(f"{Colors.RED}Build failed: {e}{Colors.RESET}")
    
    def _handle_build_describe(self, args: List[str]) -> None:
        """Handle natural language project description."""
        if not args:
            print(f"{Colors.RED}Usage: build describe '<project description>'{Colors.RESET}")
            print(f"\n{Colors.CYAN}Examples:{Colors.RESET}")
            print(f"  build describe 'Create a React todo app with authentication'")
            print(f"  build describe 'Build a FastAPI server for a blog with database'")
            print(f"  build describe 'Make a Python CLI tool for file management'")
            return
        
        if not self.advanced_building_agent:
            print(f"{Colors.RED}Advanced building agent not available{Colors.RESET}")
            return
        
        description = ' '.join(args)
        print(f"\n{Colors.CYAN}🧠 Processing description:{Colors.RESET} '{description}'")
        
        try:
            # Use asyncio to run the async method
            import asyncio
            
            async def generate_from_desc():
                result = await self.advanced_building_agent.generate_from_description(description)
                return result
            
            result = asyncio.run(generate_from_desc())
            
            if result.success:
                self._display_cool_response("✅ PROJECT GENERATION", result.message)
                
                if result.files_created:
                    print(f"\n{Colors.CYAN}Files created:{Colors.RESET}")
                    for file_path in result.files_created[:15]:  # Show first 15
                        print(f"  • {file_path}")
                    if len(result.files_created) > 15:
                        print(f"  ... and {len(result.files_created) - 15} more files")
                
                if result.design_recommendations:
                    print(f"\n{Colors.CYAN}🎨 Design Recommendations:{Colors.RESET}")
                    for rec in result.design_recommendations[:10]:
                        print(f"  • {rec}")
                
                if result.performance_metrics:
                    metrics = result.performance_metrics
                    print(f"\n{Colors.CYAN}📊 Performance Metrics:{Colors.RESET}")
                    if 'execution_time' in metrics:
                        print(f"  ⏱️ Generation time: {metrics['execution_time']:.2f}s")
                    if 'code_quality_score' in metrics:
                        print(f"  🏆 Code quality: {metrics['code_quality_score']:.1f}/100")
                    if 'total_issues' in metrics:
                        print(f"  ⚠️ Issues found: {metrics['total_issues']}")
                
                if result.next_steps:
                    print(f"\n{Colors.CYAN}Next steps:{Colors.RESET}")
                    for i, step in enumerate(result.next_steps, 1):
                        print(f"  {i}. {step}")
                        
            else:
                self._display_cool_response("❌ GENERATION FAILED", result.message)
                
                if result.errors:
                    print(f"\n{Colors.RED}Errors:{Colors.RESET}")
                    for error in result.errors[:10]:
                        print(f"  • {error}")
                        
        except Exception as e:
            self._display_cool_response("❌ PROCESSING FAILED", f"Description processing failed: {e}")
    
    def _handle_build_setup_ai(self, args: List[str]) -> None:
        """Handle AI provider setup."""
        if not args:
            print(f"{Colors.RED}Usage: build setup-ai <provider>{Colors.RESET}")
            print(f"\n{Colors.CYAN}Available providers:{Colors.RESET}")
            print(f"  openrouter - OpenRouter (supports 100+ models with real-time fetching)")
            print(f"  gemini     - Google Gemini (free tier available)")
            return
        
        if not self.advanced_building_agent:
            print(f"{Colors.RED}Advanced building agent not available{Colors.RESET}")
            return
        
        provider = args[0].lower()
        
        if provider not in ['openrouter', 'gemini']:
            print(f"{Colors.RED}Unsupported provider: {provider}{Colors.RESET}")
            return
        
        # Get API key
        provider_name = "OpenRouter" if provider == "openrouter" else "Google Gemini"
        api_key = input(f"\n{Colors.YELLOW}Enter your {provider_name} API key: {Colors.RESET}").strip()
        
        if not api_key:
            print(f"{Colors.RED}API key cannot be empty{Colors.RESET}")
            return
        
        # For OpenRouter, fetch and display real-time models
        selected_model = None
        if provider == "openrouter" and self.enhanced_ai_provider:
            print(f"\n{Colors.CYAN}🔍 Fetching latest models from OpenRouter...{Colors.RESET}")
            
            try:
                import asyncio
                
                async def fetch_and_select_model():
                    print(f"{Colors.DIM}This may take a moment...{Colors.RESET}")
                    await self.enhanced_ai_provider.update_models_cache(force=True)
                    
                    # Get free models as default selection
                    models = self.enhanced_ai_provider.get_available_models()
                    openrouter_models = [m for m in models if m.provider.value == "openrouter"]
                    free_models = [m for m in openrouter_models if m.cost_per_1k_tokens == 0][:10]
                    
                    if free_models:
                        print(f"\n{Colors.GREEN}🆓 Top Free OpenRouter Models:{Colors.RESET}")
                        for i, model in enumerate(free_models[:5], 1):
                            print(f"  {i}. {model.name} ({model.id})")
                        
                        model_choice = input(f"\n{Colors.YELLOW}Choose model (1-5) or enter model ID [default: 1]: {Colors.RESET}").strip()
                        
                        if not model_choice:
                            selected_model = free_models[0].id
                        elif model_choice.isdigit():
                            idx = int(model_choice) - 1
                            if 0 <= idx < len(free_models):
                                selected_model = free_models[idx].id
                            else:
                                selected_model = free_models[0].id
                        else:
                            selected_model = model_choice
                    else:
                        print(f"{Colors.YELLOW}Could not fetch models. Using default.{Colors.RESET}")
                        selected_model = "mistralai/mistral-7b-instruct"
                        
                    return selected_model
                
                selected_model = asyncio.run(fetch_and_select_model())
                
            except Exception as e:
                print(f"{Colors.YELLOW}Could not fetch real-time models: {e}. Using default.{Colors.RESET}")
                selected_model = "mistralai/mistral-7b-instruct"
        else:
            # For Gemini or if enhanced provider not available
            selected_model = "gemini-1.5-flash-latest"
        
        print(f"\n{Colors.CYAN}🔄 Setting up {provider_name} provider...{Colors.RESET}")
        print(f"  Model: {selected_model}")
        
        try:
            import asyncio
            
            async def setup_provider():
                return await self.advanced_building_agent.setup_ai_provider(provider, api_key, model_id=selected_model, interactive=True)
            
            success = asyncio.run(setup_provider())
            
            if success:
                self._display_cool_response("🎉 PROVIDER CONFIGURED", f"Successfully configured {provider_name} provider!", {"Next Step": "You can now use 'build describe' for AI-powered project generation"})
            else:
                self._display_cool_response("❌ CONFIGURATION FAILED", f"Failed to configure {provider_name} provider")
                
        except Exception as e:
            self._display_cool_response("❌ SETUP FAILED", f"Setup failed: {e}")
    
    def _handle_build_ai_status(self) -> None:
        """Show AI provider status."""
        if not self.advanced_building_agent:
            print(f"{Colors.RED}Advanced building agent not available{Colors.RESET}")
            return
        
        try:
            status = self.advanced_building_agent.get_terminal_status()
            ai_status = status.get('ai_provider', {})
            
            print(f"\n{Colors.CYAN}🤖 AI Provider Status:{Colors.RESET}")
            
            if ai_status.get('configured', False):
                print(f"  Status: {Colors.GREEN}Configured{Colors.RESET}")
                print(f"  Provider: {ai_status.get('provider', 'Unknown')}")
                print(f"  Model: {ai_status.get('model', 'Unknown')}")
                
                # Show generation stats
                gen_stats = status.get('generation_history', {})
                total = gen_stats.get('total_generations', 0)
                successful = gen_stats.get('successful_generations', 0)
                
                print(f"\n{Colors.CYAN}Generation Statistics:{Colors.RESET}")
                print(f"  Total generations: {total}")
                print(f"  Successful: {successful}")
                if total > 0:
                    success_rate = (successful / total) * 100
                    print(f"  Success rate: {success_rate:.1f}%")
                
                if gen_stats.get('last_generation'):
                    print(f"  Last generation: {gen_stats['last_generation'][:19]}")
                    
            else:
                print(f"  Status: {Colors.YELLOW}Not configured{Colors.RESET}")
                print(f"  Use 'build setup-ai <provider>' to configure")
                
        except Exception as e:
            print(f"{Colors.RED}Failed to get AI status: {e}{Colors.RESET}")
    
    def _handle_build_analyze(self, args: List[str]) -> None:
        """Analyze generated code or current project."""
        if not self.advanced_building_agent:
            self._display_cool_response("❌ SERVICE UNAVAILABLE", "Advanced building agent not available")
            return
        
        print(f"\n{Colors.CYAN}🔍 Analyzing current workspace...{Colors.RESET}")
        
        try:
            # Get recent generation history
            history = self.advanced_building_agent.get_generation_history(1)
            
            if not history:
                print(f"{Colors.YELLOW}No recent generations found to analyze{Colors.RESET}")
                return
            
            recent = history[0]
            result_data = recent.get('result', {})
            
            print(f"\n{Colors.CYAN}Analysis of last generation:{Colors.RESET}")
            print(f"  Project: {recent.get('requirements', {}).get('project_name', 'Unknown')}")
            print(f"  Generated: {recent['timestamp'][:19]}")
            
            if result_data.get('performance_metrics'):
                metrics = result_data['performance_metrics']
                
                print(f"\n{Colors.CYAN}Code Quality Metrics:{Colors.RESET}")
                if 'code_quality_score' in metrics:
                    score = metrics['code_quality_score']
                    color = Colors.GREEN if score >= 80 else Colors.YELLOW if score >= 60 else Colors.RED
                    print(f"  {color}Quality Score: {score:.1f}/100{Colors.RESET}")
                
                if 'total_issues' in metrics:
                    issues = metrics['total_issues']
                    color = Colors.GREEN if issues == 0 else Colors.YELLOW if issues < 5 else Colors.RED
                    print(f"  {color}Issues Found: {issues}{Colors.RESET}")
                
                if 'total_suggestions' in metrics:
                    print(f"  Suggestions: {metrics['total_suggestions']}")
                
                print(f"\n{Colors.CYAN}Performance:{Colors.RESET}")
                if 'execution_time' in metrics:
                    print(f"  Generation Time: {metrics['execution_time']:.2f}s")
                if 'memory_delta' in metrics:
                    print(f"  Memory Usage: {metrics['memory_delta']:.1f}MB")
                    
            # Show recent errors/warnings
            if result_data.get('errors'):
                print(f"\n{Colors.RED}Recent Errors:{Colors.RESET}")
                for error in result_data['errors'][:5]:
                    print(f"  • {error}")
            
            if result_data.get('warnings'):
                print(f"\n{Colors.YELLOW}Recent Warnings:{Colors.RESET}")
                for warning in result_data['warnings'][:5]:
                    print(f"  • {warning}")
                    
        except Exception as e:
            self._display_cool_response("❌ ANALYSIS FAILED", f"Analysis failed: {e}")
    
    def _handle_build_status(self) -> None:
        """Show comprehensive build and terminal status."""
        if not self.advanced_building_agent:
            self._display_cool_response("❌ SERVICE UNAVAILABLE", "Advanced building agent not available")
            return
        
        try:
            status = self.advanced_building_agent.get_terminal_status()
            
            print(f"\n{Colors.CYAN}📊 Terminal & Build Status:{Colors.RESET}")
            
            # System status
            system = status.get('system', {})
            if 'error' not in system:
                cpu = system.get('cpu_percent', 0)
                memory = system.get('memory_percent', 0)
                
                cpu_color = Colors.RED if cpu > 80 else Colors.YELLOW if cpu > 60 else Colors.GREEN
                memory_color = Colors.RED if memory > 80 else Colors.YELLOW if memory > 60 else Colors.GREEN
                
                print(f"\n{Colors.CYAN}System Resources:{Colors.RESET}")
                print(f"  {cpu_color}CPU Usage: {cpu:.1f}%{Colors.RESET}")
                print(f"  {memory_color}Memory Usage: {memory:.1f}%{Colors.RESET}")
                print(f"  Active Processes: {system.get('active_processes', 'Unknown')}")
                print(f"  Python Processes: {system.get('python_processes', 'Unknown')}")
            
            # AI Provider status
            ai_status = status.get('ai_provider', {})
            ai_color = Colors.GREEN if ai_status.get('configured') else Colors.YELLOW
            print(f"\n{Colors.CYAN}AI Integration:{Colors.RESET}")
            print(f"  {ai_color}Status: {'Configured' if ai_status.get('configured') else 'Not Configured'}{Colors.RESET}")
            
            if ai_status.get('configured'):
                print(f"  Provider: {ai_status.get('provider', 'Unknown')}")
                print(f"  Model: {ai_status.get('model', 'Unknown')}")
            
            # Generation history
            gen_history = status.get('generation_history', {})
            print(f"\n{Colors.CYAN}Build History:{Colors.RESET}")
            print(f"  Total Builds: {gen_history.get('total_generations', 0)}")
            print(f"  Successful: {gen_history.get('successful_generations', 0)}")
            
            # Workspace info
            workspace = status.get('workspace', {})
            workspace_color = Colors.GREEN if workspace.get('exists') else Colors.RED
            print(f"\n{Colors.CYAN}Workspace:{Colors.RESET}")
            print(f"  {workspace_color}Path: {workspace.get('path', 'Unknown')}{Colors.RESET}")
            print(f"  Data Directory: {'Yes' if workspace.get('data_dir_exists') else 'No'}")
            
        except Exception as e:
            self._display_cool_response("❌ STATUS CHECK FAILED", f"Failed to get status: {e}")
    
    def _handle_build_check_updates(self) -> None:
        """Check for AI model updates and system health."""
        if not self.advanced_building_agent:
            print(f"{Colors.RED}Advanced building agent not available{Colors.RESET}")
            return
        
        print(f"\n{Colors.CYAN}🔄 Checking for updates...{Colors.RESET}")
        
        try:
            import asyncio
            
            async def check_updates():
                return await self.advanced_building_agent.check_for_updates()
            
            results = asyncio.run(check_updates())
            
            print(f"\n{Colors.CYAN}Update Results:{Colors.RESET}")
            
            if results.get('models_updated'):
                new_count = results.get('new_models_count', 0)
                if new_count > 0:
                    print(f"  {Colors.GREEN}✅ Found {new_count} new AI models{Colors.RESET}")
                else:
                    print(f"  {Colors.GREEN}✅ Model cache updated{Colors.RESET}")
            else:
                print(f"  {Colors.YELLOW}⚠️ No model updates available{Colors.RESET}")
            
            health_color = Colors.GREEN if results.get('system_healthy') else Colors.RED
            health_status = "Healthy" if results.get('system_healthy') else "Issues Detected"
            print(f"  {health_color}System Health: {health_status}{Colors.RESET}")
            
            recommendations = results.get('recommendations', [])
            if recommendations:
                print(f"\n{Colors.CYAN}Recommendations:{Colors.RESET}")
                for rec in recommendations:
                    print(f"  • {rec}")
                    
        except Exception as e:
            self._display_cool_response("❌ UPDATE CHECK FAILED", f"Failed to check for updates: {e}")
    
    def _handle_build_browse_models(self) -> None:
        """Browse and explore available AI models with enhanced interface."""
        if not self.enhanced_ai_provider:
            self._display_cool_response("❌ SERVICE UNAVAILABLE", "Enhanced AI provider not available")
            return
        
        print(f"\n{Colors.CYAN}🔍 Browsing Available AI Models...{Colors.RESET}")
        
        try:
            import asyncio
            
            async def browse_models():
                # Update models cache first
                print(f"{Colors.CYAN}📡 Fetching latest models from providers...{Colors.RESET}")
                await self.enhanced_ai_provider.update_models_cache(force=True)
                
                # Start interactive model selection
                selected_model = await self.enhanced_ai_provider.interactive_model_selection()
                
                if selected_model:
                    print(f"\n{Colors.GREEN}🎯 Model Details:{Colors.RESET}")
                    print(f"  Name: {selected_model.name}")
                    print(f"  ID: {selected_model.id}")
                    print(f"  Provider: {selected_model.provider.value}")
                    
                    cost_str = f"${selected_model.cost_per_1k_tokens:.6f}/1k tokens" if selected_model.cost_per_1k_tokens > 0 else "FREE"
                    print(f"  Cost: {cost_str}")
                    
                    context_str = f"{selected_model.context_length:,}" if selected_model.context_length > 0 else "Unknown"
                    print(f"  Context Length: {context_str} tokens")
                    
                    if selected_model.capabilities:
                        print(f"  Capabilities: {', '.join(selected_model.capabilities)}")
                    
                    if selected_model.description:
                        print(f"  Description: {selected_model.description}")
                    
                    # Ask if user wants to configure this model
                    configure = input(f"\n{Colors.CYAN}Would you like to configure this model? (y/n): {Colors.RESET}").strip().lower()
                    if configure == 'y':
                        if selected_model.provider.value == 'openrouter':
                            api_key = input(f"{Colors.CYAN}Enter your OpenRouter API key: {Colors.RESET}").strip()
                            if api_key:
                                # Configure the provider
                                success = self.enhanced_ai_provider.configure_provider(
                                    provider=selected_model.provider,
                                    api_key=api_key,
                                    model_id=selected_model.id
                                )
                                if success:
                                    print(f"{Colors.GREEN}✅ Model configured successfully!{Colors.RESET}")
                                else:
                                    print(f"{Colors.RED}❌ Failed to configure model{Colors.RESET}")
                        elif selected_model.provider.value == 'gemini':
                            api_key = input(f"{Colors.CYAN}Enter your Google Gemini API key: {Colors.RESET}").strip()
                            if api_key:
                                success = self.enhanced_ai_provider.configure_provider(
                                    provider=selected_model.provider,
                                    api_key=api_key,
                                    model_id=selected_model.id
                                )
                                if success:
                                    print(f"{Colors.GREEN}✅ Model configured successfully!{Colors.RESET}")
                                else:
                                    print(f"{Colors.RED}❌ Failed to configure model{Colors.RESET}")
                else:
                    print(f"{Colors.YELLOW}No model selected{Colors.RESET}")
            
            asyncio.run(browse_models())
            
        except Exception as e:
            self._display_cool_response("❌ MODEL BROWSING FAILED", f"Failed to browse models: {e}")
    
    def _handle_clear_all_command(self) -> None:
        """Comprehensive clear all command that clears everything."""
        print(f"\n{Colors.CYAN}🧹 CLEARING ALL DATA - COMPREHENSIVE RESET{Colors.RESET}")
        print(f"{Colors.YELLOW}This will clear all data across the entire system!{Colors.RESET}")
        
        confirm = input(f"\n{Colors.RED}Are you sure you want to proceed? Type 'yes' to confirm: {Colors.RESET}").strip().lower()
        if confirm != 'yes':
            print(f"{Colors.YELLOW}Clear all operation cancelled.{Colors.RESET}")
            return
        
        print(f"\n{Colors.CYAN}Starting comprehensive clear operation...{Colors.RESET}")
        cleared_items = []
        failed_items = []
        
        # 1. Clear screen first
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
            cleared_items.append("🖥️ Screen")
        except Exception as e:
            failed_items.append(f"Screen: {e}")
        
        # 2. Clear all projects
        try:
            self.projects.clear()
            self.current_project = None
            cleared_items.append("🚀 Projects")
        except Exception as e:
            failed_items.append(f"Projects: {e}")
        
        # 3. Clear all tasks
        try:
            self.tasks.clear()
            self._save_tasks()
            cleared_items.append("✅ Tasks")
        except Exception as e:
            failed_items.append(f"Tasks: {e}")
        
        # 4. Clear all messages
        try:
            self.message_history.clear()
            cleared_items.append("💬 Messages")
        except Exception as e:
            failed_items.append(f"Messages: {e}")
        
        # 5. Clear chat transcripts
        try:
            if hasattr(self, 'context_manager') and self.context_manager:
                # Clear chat.jsonl
                chat_file = self.data_dir / "messages" / "chat.jsonl"
                if chat_file.exists():
                    chat_file.unlink()
            cleared_items.append("📝 Chat transcripts")
        except Exception as e:
            failed_items.append(f"Chat transcripts: {e}")
        
        # 6. Clear remembered entries
        try:
            data = {'history': [], 'last': None}
            self._save_remembered(data)
            cleared_items.append("🧠 Remembered entries")
        except Exception as e:
            failed_items.append(f"Remembered entries: {e}")
        
        # 7. Clear memory snapshots
        try:
            memory_dir = self.memory_dir
            if memory_dir.exists():
                for file in memory_dir.glob("*.jsonl"):
                    file.unlink()
                # Clear context memory
                context_file = self.data_dir / "context_memory.json"
                if context_file.exists():
                    context_file.unlink()
            cleared_items.append("📋 Memory snapshots")
        except Exception as e:
            failed_items.append(f"Memory snapshots: {e}")
        
        # 8. Clear all sessions
        try:
            self.sessions.clear()
            self.current_session_id = None
            sessions_dir = self.data_dir / "sessions"
            if sessions_dir.exists():
                for file in sessions_dir.glob("*.json"):
                    file.unlink()
            cleared_items.append("📏 Sessions")
        except Exception as e:
            failed_items.append(f"Sessions: {e}")
        
        # 9. Clear exported files
        try:
            exports_dir = self.exports_dir
            if exports_dir.exists():
                for file in exports_dir.glob("*"):
                    if file.is_file():
                        file.unlink()
            cleared_items.append("📎 Exported files")
        except Exception as e:
            failed_items.append(f"Exported files: {e}")
        
        # 10. Clear state history
        try:
            self.state_history.clear()
            cleared_items.append("🔄 State history")
        except Exception as e:
            failed_items.append(f"State history: {e}")
        
        # 11. Clear command history
        try:
            self.command_history.clear()
            cleared_items.append("⚡ Command history")
        except Exception as e:
            failed_items.append(f"Command history: {e}")
        
        # 12. Clear AI configurations (if available)
        try:
            if hasattr(self, 'ai_manager') and self.ai_manager:
                # Clear AI manager config
                self.ai_manager.config = None
            cleared_items.append("🤖 AI configurations")
        except Exception as e:
            failed_items.append(f"AI configurations: {e}")
        
        # 13. Clear building agent data
        try:
            if hasattr(self, 'advanced_building_agent') and self.advanced_building_agent:
                self.advanced_building_agent.generation_history.clear()
                self.advanced_building_agent._save_history()
            cleared_items.append("🔨 Build history")
        except Exception as e:
            failed_items.append(f"Build history: {e}")
        
        # 14. Clear AI models cache
        try:
            if hasattr(self, 'enhanced_ai_provider') and self.enhanced_ai_provider:
                self.enhanced_ai_provider.available_models.clear()
                self.enhanced_ai_provider.last_model_check = None
                cache_file = self.enhanced_ai_provider.models_cache_file
                if cache_file.exists():
                    cache_file.unlink()
            cleared_items.append("🧠 AI models cache")
        except Exception as e:
            failed_items.append(f"AI models cache: {e}")
        
        # 15. Clear configuration files
        try:
            config_files = [
                self.config_file,
                self.state_file,
                self.data_dir / ".project_context.json"
            ]
            for file in config_files:
                if file.exists():
                    file.unlink()
            cleared_items.append("⚙️ Configuration files")
        except Exception as e:
            failed_items.append(f"Configuration files: {e}")
        
        # 16. Final save and reset
        try:
            self.save_persistent_data()
            cleared_items.append("💾 Persistent data reset")
        except Exception as e:
            failed_items.append(f"Persistent data reset: {e}")
        
        # Display results
        print(f"\n{Colors.CYAN}CLEAR ALL OPERATION COMPLETED{Colors.RESET}")
        print(f"{Colors.GREEN}✅ Successfully cleared {len(cleared_items)} categories:{Colors.RESET}")
        for item in cleared_items:
            print(f"  ✅ {item}")
        
        if failed_items:
            print(f"\n{Colors.RED}❌ Failed to clear {len(failed_items)} categories:{Colors.RESET}")
            for item in failed_items:
                print(f"  ❌ {item}")
        
        print(f"\n{Colors.GREEN}✨ System has been completely reset! All data cleared.{Colors.RESET}")
        print(f"{Colors.CYAN}You can now start fresh with a clean workspace.{Colors.RESET}")
        
        # Display header again
        self.display_header()
    
    def _handle_clear_command(self, args: List[str]) -> None:
        """Handle clear command with optional 'all' parameter."""
        if args and args[0].lower() == 'all':
            self._handle_clear_all_command()
        else:
            os.system('cls' if os.name == 'nt' else 'clear')
            self.display_header()
    
    def _handle_build_clear_history(self) -> None:
        """Clear build generation history."""
        try:
            if self.advanced_building_agent:
                # Clear generation history
                self.advanced_building_agent.generation_history.clear()
                self.advanced_building_agent._save_history()
                print(f"{Colors.GREEN}✅ Build history cleared{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}⚠️ Advanced building agent not available{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to clear build history: {e}{Colors.RESET}")
    
    def _handle_build_clear_cache(self) -> None:
        """Clear AI models cache."""
        try:
            if self.enhanced_ai_provider:
                # Clear models cache
                self.enhanced_ai_provider.available_models.clear()
                self.enhanced_ai_provider.last_model_check = None
                
                # Clear cache files
                cache_file = self.enhanced_ai_provider.models_cache_file
                if cache_file.exists():
                    cache_file.unlink()
                
                print(f"{Colors.GREEN}✅ AI models cache cleared{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}⚠️ Enhanced AI provider not available{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to clear models cache: {e}{Colors.RESET}")
    
    def _handle_build_clear_configs(self) -> None:
        """Clear AI provider configurations."""
        try:
            if self.enhanced_ai_provider:
                # Clear configuration
                self.enhanced_ai_provider.config = None
                
                # Clear config file
                config_file = self.enhanced_ai_provider.config_file
                if config_file.exists():
                    config_file.unlink()
                
                print(f"{Colors.GREEN}✅ AI provider configurations cleared{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}⚠️ Enhanced AI provider not available{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to clear AI configurations: {e}{Colors.RESET}")
    
    def _handle_build_clear_all(self) -> None:
        """Clear all building agent data."""
        print(f"{Colors.CYAN}🧹 Clearing all building agent data...{Colors.RESET}")
        
        # Clear build history
        try:
            self._handle_build_clear_history()
        except Exception as e:
            print(f"{Colors.RED}Error clearing history: {e}{Colors.RESET}")
        
        # Clear models cache
        try:
            self._handle_build_clear_cache()
        except Exception as e:
            print(f"{Colors.RED}Error clearing cache: {e}{Colors.RESET}")
        
        # Clear AI configurations
        try:
            self._handle_build_clear_configs()
        except Exception as e:
            print(f"{Colors.RED}Error clearing configs: {e}{Colors.RESET}")
        
        print(f"{Colors.GREEN}✨ All building agent data cleared successfully!{Colors.RESET}")

def main():
    """Main entry point for the robust terminal interface."""
    try:
        interface = RobustTerminalInterface()
        interface.run()
        return 0
    except Exception as e:
        print(f"{Colors.RED}Failed to start terminal interface: {e}{Colors.RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())