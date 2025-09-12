"""
Startup Hook for AI Terminal Workflow
Entry point for automatic integration and session management

This module implements the enhanced AI code editor workflow with:
- Session continuity across restarts
- Context preservation and compression
- Intelligent memory management
- Error recovery mechanisms
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class StartupHook:
    """Main startup hook for AI terminal workflow initialization."""
    
    def __init__(self):
        self.project_root = Path(os.getcwd())
        self.config_file = self.project_root / "todo_improved.json"
        self.state_file = self.project_root / "project_state.json"
        self.tasks_dir = self.project_root / "tasks"
        self.config = None
        
    def load_configuration(self) -> bool:
        """Load the enhanced AI code editor configuration."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                print(f"✓ Configuration loaded from {self.config_file}")
                return True
            else:
                print(f"⚠ Configuration file not found: {self.config_file}")
                return False
        except Exception as e:
            print(f"✗ Error loading configuration: {e}")
            return False
    
    def initialize_project_state(self) -> Dict[str, Any]:
        """Initialize or load project state for session continuity."""
        default_state = {
            "project_name": "ai_terminal_workflow",
            "session_id": int(time.time()),
            "last_active": time.strftime("%Y-%m-%d %H:%M:%S"),
            "context_preserved": True,
            "workflow_phase": "setup",
            "completed_tasks": [],
            "active_files": [],
            "error_history": [],
            "user_preferences": {},
            "memory_state": {
                "file_structure_mapped": False,
                "dependencies_analyzed": False,
                "style_patterns_learned": False
            }
        }
        
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                state["last_active"] = time.strftime("%Y-%m-%d %H:%M:%S")
                state["session_id"] = int(time.time())
                print("✓ Project state restored from previous session")
            else:
                state = default_state
                print("✓ New project state initialized")
                
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
                
            return state
        except Exception as e:
            print(f"⚠ Error with project state: {e}")
            return default_state
    
    def ensure_directory_structure(self) -> bool:
        """Ensure required directories exist."""
        try:
            directories = [
                self.tasks_dir,
                self.project_root / "backups",
                self.project_root / "logs"
            ]
            
            for directory in directories:
                directory.mkdir(exist_ok=True)
                
            print("✓ Directory structure verified")
            return True
        except Exception as e:
            print(f"✗ Error creating directories: {e}")
            return False
    
    def check_required_files(self) -> Dict[str, bool]:
        """Check for required files and report status."""
        required_files = {
            "todo_improved.json": self.config_file.exists(),
            "tasks/todo.md": (self.tasks_dir / "todo.md").exists(),
            "project_state.json": self.state_file.exists()
        }
        
        print("\n📋 File Status Check:")
        for file_name, exists in required_files.items():
            status = "✓" if exists else "✗"
            print(f"  {status} {file_name}")
            
        return required_files
    
    def display_startup_info(self, state: Dict[str, Any]) -> None:
        """Display startup information and system status."""
        print("\n" + "="*60)
        print("🚀 AI Terminal Workflow - Enhanced Edition")
        print("   Addressing 16 Core User Struggles")
        print("="*60)
        print(f"📁 Project: {state.get('project_name', 'Unknown')}")
        print(f"🕒 Session: {state.get('session_id', 'Unknown')}")
        print(f"📅 Last Active: {state.get('last_active', 'Unknown')}")
        print(f"🔄 Workflow Phase: {state.get('workflow_phase', 'Unknown')}")
        print(f"✅ Completed Tasks: {len(state.get('completed_tasks', []))}")
        
        if self.config:
            version = self.config.get('ai_code_editor_enhanced', {}).get('version', 'Unknown')
            print(f"📦 Version: {version}")
            
        print("\n🎯 Core Features Active:")
        print("  • Session continuity across restarts")
        print("  • Context preservation and compression")
        print("  • Intelligent memory management")
        print("  • Error pattern recognition")
        print("  • Progressive task execution")
        print("\n" + "="*60)
    
    def run_startup_sequence(self) -> bool:
        """Execute the complete startup sequence."""
        print("🔧 Initializing AI Terminal Workflow...")
        
        if not self.load_configuration():
            print("⚠ Continuing with default configuration")
        
        if not self.ensure_directory_structure():
            return False
        
        state = self.initialize_project_state()
        
        file_status = self.check_required_files()
        
        self.display_startup_info(state)
        
        if self.config and self.config.get('ai_code_editor_enhanced', {}).get('execution', {}).get('startup_integration', {}).get('enabled', False):
            print("\n🔄 Auto-startup integration enabled")
            try:
                import auto_startup
                auto_startup.run_auto_startup()
            except ImportError:
                print("⚠ auto_startup.py not found - will be created next")
        
        print("\n✅ Startup sequence completed successfully")
        print("\n💡 Ready for enhanced AI-assisted development!")
        
        try:
            print("\n🚀 Launching interactive terminal interface...")
            import terminal_interface
            interface = terminal_interface.TerminalInterface()
            interface.run()
        except KeyboardInterrupt:
            print("\n⏹ Interface interrupted by user")
        except Exception as e:
            print(f"\n⚠ Could not launch interface: {e}")
            print("   You can manually run: python terminal_interface.py")
        
        return True

def main():
    """Main entry point for startup hook."""
    try:
        hook = StartupHook()
        success = hook.run_startup_sequence()
        
        if success:
            print("\n🎉 AI Terminal Workflow is ready!")
            return 0
        else:
            print("\n❌ Startup sequence failed")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⏹ Startup interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error during startup: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())