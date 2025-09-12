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
    from project_inference import ProjectInferenceEngine
except ImportError as e:
    print(f"Warning: Could not import workflow components: {e}")
    print("Some features may be limited.")
    ProjectInferenceEngine = None

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
            ("💬", "MESSAGES", "message send | history | export", gradient_bot),
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
        
        features_line = f" 🎯 {accent_gold}Project{Colors.RESET} {Colors.DIM}• ✅ Task Tracking • 💬 AI Communication • 💾 Session Persistence{Colors.RESET}"
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
            ("💬", "message send <text>", "Communicate with AI assistants for code help and guidance"),
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
                ("clear", "Clear screen", "🧹")
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
                    
                    core_commands = f" 🎯 {accent_silver}Core:{Colors.RESET} {Colors.DIM}project, task, message, help, clear, status{Colors.RESET}"
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
                'clear': lambda args: (os.system('cls' if os.name == 'nt' else 'clear'), self.display_header()),
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