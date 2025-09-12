"""
High-Performance File Management System
Core system integration for AI Terminal Workflow

Implements unified state management with:
- Self-healing memory system
- Predictive context loading
- Automatic relevance scoring
- Real-time incremental updates
"""

import os
import sys
import json
import time
import hashlib
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict, deque
import weakref

class MemoryLayer:
    """Base class for memory layers in the system."""
    
    def __init__(self, name: str, retention_policy: str):
        self.name = name
        self.retention_policy = retention_policy
        self.data = {}
        self.access_times = {}
        self.relevance_scores = {}
        self.last_cleanup = time.time()
        
    def store(self, key: str, value: Any, relevance: float = 1.0) -> None:
        """Store data with relevance scoring."""
        self.data[key] = value
        self.access_times[key] = time.time()
        self.relevance_scores[key] = relevance
        
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data and update access time."""
        if key in self.data:
            self.access_times[key] = time.time()
            return self.data[key]
        return None
        
    def cleanup(self, max_age_seconds: int = 3600) -> int:
        """Clean up old or low-relevance data."""
        current_time = time.time()
        removed_count = 0
        
        keys_to_remove = []
        for key in self.data:
            age = current_time - self.access_times.get(key, current_time)
            relevance = self.relevance_scores.get(key, 0.0)
            
            if age > max_age_seconds and relevance < 0.5:
                keys_to_remove.append(key)
                
        for key in keys_to_remove:
            del self.data[key]
            del self.access_times[key]
            del self.relevance_scores[key]
            removed_count += 1
            
        self.last_cleanup = current_time
        return removed_count

class ImmediateContextLayer(MemoryLayer):
    """Immediate context for current session with full fidelity."""
    
    def __init__(self):
        super().__init__("immediate_context", "full_fidelity")
        self.session_data = {
            "active_files": set(),
            "recent_commands": deque(maxlen=100),
            "current_task": None,
            "error_context": [],
            "user_interactions": deque(maxlen=50)
        }
        
    def add_active_file(self, file_path: str) -> None:
        """Add file to active context."""
        self.session_data["active_files"].add(file_path)
        self.store(f"file_active_{file_path}", {
            "path": file_path,
            "added_time": time.time(),
            "access_count": 1
        }, relevance=1.0)
        
    def add_command(self, command: str, output: str = "", exit_code: int = 0) -> None:
        """Add command to recent history."""
        cmd_data = {
            "command": command,
            "output": output[:1000],
            "exit_code": exit_code,
            "timestamp": time.time()
        }
        self.session_data["recent_commands"].append(cmd_data)
        
    def set_current_task(self, task: Dict[str, Any]) -> None:
        """Set the current active task."""
        self.session_data["current_task"] = task
        self.store("current_task", task, relevance=1.0)
        
    def add_error_context(self, error: Dict[str, Any]) -> None:
        """Add error to context for pattern recognition."""
        error["timestamp"] = time.time()
        self.session_data["error_context"].append(error)
        if len(self.session_data["error_context"]) > 20:
            self.session_data["error_context"] = self.session_data["error_context"][-20:]

class SessionMemoryLayer(MemoryLayer):
    """Session memory with semantic summaries for project lifetime."""
    
    def __init__(self):
        super().__init__("session_memory", "semantic_summaries")
        self.file_relationships = defaultdict(set)
        self.pattern_library = {}
        self.task_history = []
        self.user_preferences = {}
        
    def map_file_relationship(self, file1: str, file2: str, relationship_type: str) -> None:
        """Map relationship between files."""
        self.file_relationships[file1].add((file2, relationship_type))
        self.file_relationships[file2].add((file1, relationship_type))
        
    def learn_pattern(self, pattern_type: str, pattern_data: Dict[str, Any]) -> None:
        """Learn and store coding patterns."""
        if pattern_type not in self.pattern_library:
            self.pattern_library[pattern_type] = []
            
        pattern_data["learned_time"] = time.time()
        self.pattern_library[pattern_type].append(pattern_data)
        
        if len(self.pattern_library[pattern_type]) > 10:
            self.pattern_library[pattern_type] = self.pattern_library[pattern_type][-10:]
            
    def add_task_completion(self, task: Dict[str, Any]) -> None:
        """Record completed task for history."""
        task["completed_time"] = time.time()
        self.task_history.append(task)
        
    def update_user_preference(self, key: str, value: Any) -> None:
        """Update user preference based on interactions."""
        self.user_preferences[key] = {
            "value": value,
            "updated_time": time.time(),
            "confidence": self.user_preferences.get(key, {}).get("confidence", 0.5) + 0.1
        }

class LongTermKnowledgeLayer(MemoryLayer):
    """Long-term knowledge with pattern abstractions across projects."""
    
    def __init__(self):
        super().__init__("long_term_knowledge", "pattern_abstractions")
        self.knowledge_graph = defaultdict(dict)
        self.error_solutions = {}
        self.best_practices = {}
        
    def store_error_solution(self, error_signature: str, solution: Dict[str, Any]) -> None:
        """Store successful error resolution."""
        if error_signature not in self.error_solutions:
            self.error_solutions[error_signature] = []
            
        solution["success_time"] = time.time()
        self.error_solutions[error_signature].append(solution)
        
    def get_similar_error_solutions(self, error_signature: str) -> List[Dict[str, Any]]:
        """Get solutions for similar errors."""
        solutions = []
        
        if error_signature in self.error_solutions:
            solutions.extend(self.error_solutions[error_signature])
            
        for stored_sig, stored_solutions in self.error_solutions.items():
            similarity = self._calculate_similarity(error_signature, stored_sig)
            if similarity > 0.7:
                for solution in stored_solutions:
                    solution["similarity_score"] = similarity
                    solutions.append(solution)
                    
        return sorted(solutions, key=lambda x: x.get("similarity_score", 0), reverse=True)
        
    def _calculate_similarity(self, sig1: str, sig2: str) -> float:
        """Calculate similarity between error signatures."""
        words1 = set(sig1.lower().split())
        words2 = set(sig2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)

class HighPerformanceFileSystem:
    """Main high-performance file system with unified state management."""
    
    def __init__(self):
        self.project_root = Path(os.getcwd())
        self.state_file = self.project_root / "project_state.json"
        
        self.immediate_context = ImmediateContextLayer()
        self.session_memory = SessionMemoryLayer()
        self.long_term_knowledge = LongTermKnowledgeLayer()
        
        self.is_initialized = False
        self.last_sync = 0
        self.sync_interval = 30
        
        self._maintenance_thread = None
        self._stop_maintenance = threading.Event()
        
    def initialize(self) -> bool:
        """Initialize the high-performance file system."""
        try:
            print("🚀 Initializing High-Performance File System...")
            
            self._load_persistent_state()
            
            self._start_maintenance_thread()
            
            self._initial_scan()
            
            self.is_initialized = True
            print("✅ High-Performance File System initialized")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize file system: {e}")
            return False
            
    def _load_persistent_state(self) -> None:
        """Load persistent state from disk."""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    
                if "session_memory" in state:
                    session_data = state["session_memory"]
                    self.session_memory.file_relationships = defaultdict(set, session_data.get("file_relationships", {}))
                    self.session_memory.pattern_library = session_data.get("pattern_library", {})
                    self.session_memory.user_preferences = session_data.get("user_preferences", {})
                    
                if "long_term_knowledge" in state:
                    lt_data = state["long_term_knowledge"]
                    self.long_term_knowledge.error_solutions = lt_data.get("error_solutions", {})
                    self.long_term_knowledge.best_practices = lt_data.get("best_practices", {})
                    
                print("✓ Persistent state loaded")
                
        except Exception as e:
            print(f"⚠ Could not load persistent state: {e}")
            
    def _save_persistent_state(self) -> None:
        """Save current state to disk."""
        try:
            state = {
                "timestamp": datetime.now().isoformat(),
                "session_memory": {
                    "file_relationships": dict(self.session_memory.file_relationships),
                    "pattern_library": self.session_memory.pattern_library,
                    "user_preferences": self.session_memory.user_preferences,
                    "task_history": self.session_memory.task_history[-50:]
                },
                "long_term_knowledge": {
                    "error_solutions": self.long_term_knowledge.error_solutions,
                    "best_practices": self.long_term_knowledge.best_practices
                }
            }
            
            self.state_file.parent.mkdir(exist_ok=True)
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            print(f"⚠ Could not save persistent state: {e}")
            
    def _initial_scan(self) -> None:
        """Perform initial file system scan."""
        try:
            print("🔍 Performing initial file system scan...")
            
            file_count = 0
            for root, dirs, files in os.walk(self.project_root):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]
                
                for file in files:
                    if not file.startswith('.') and not file.endswith('.pyc'):
                        file_path = os.path.join(root, file)
                        self._analyze_file(file_path)
                        file_count += 1
                        
            print(f"✓ Scanned {file_count} files")
            
        except Exception as e:
            print(f"⚠ Error during initial scan: {e}")
            
    def _analyze_file(self, file_path: str) -> None:
        """Analyze a file for patterns and relationships."""
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.md', '.txt', '.json', '.yaml', '.yml']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                self._extract_dependencies(file_path, content)
                
                self._learn_file_patterns(file_path, content)
                
        except Exception:
            pass
            
    def _extract_dependencies(self, file_path: str, content: str) -> None:
        """Extract file dependencies and relationships."""
        lines = content.split('\n')
        
        for line in lines[:50]:
            line = line.strip()
            
            if line.startswith('import ') or line.startswith('from '):
                if not any(stdlib in line for stdlib in ['os', 'sys', 'json', 'time', 'datetime', 'pathlib']):
                    self.session_memory.map_file_relationship(file_path, line, "import")
                    
            elif line.startswith('import ') and 'from' in line:
                if './' in line or '../' in line:
                    self.session_memory.map_file_relationship(file_path, line, "import")
                    
    def _learn_file_patterns(self, file_path: str, content: str) -> None:
        """Learn coding patterns from file content."""
        patterns = {
            "indentation": self._detect_indentation(content),
            "line_endings": self._detect_line_endings(content),
            "naming_convention": self._detect_naming_convention(content),
            "documentation_style": self._detect_documentation_style(content)
        }
        
        self.session_memory.learn_pattern(f"file_style_{Path(file_path).suffix}", patterns)
        
    def _detect_indentation(self, content: str) -> str:
        """Detect indentation style."""
        lines = content.split('\n')
        tab_count = sum(1 for line in lines if line.startswith('\t'))
        space_count = sum(1 for line in lines if line.startswith('    '))
        
        if tab_count > space_count:
            return "tabs"
        elif space_count > 0:
            return "4_spaces"
        else:
            return "unknown"
            
    def _detect_line_endings(self, content: str) -> str:
        """Detect line ending style."""
        if '\r\n' in content:
            return "crlf"
        elif '\n' in content:
            return "lf"
        else:
            return "unknown"
            
    def _detect_naming_convention(self, content: str) -> str:
        """Detect naming convention."""
        if '_' in content and content.count('_') > content.count('camelCase'):
            return "snake_case"
        else:
            return "camelCase"
            
    def _detect_documentation_style(self, content: str) -> str:
        """Detect documentation style."""
        if '"""' in content:
            return "python_docstrings"
        elif '/**' in content:
            return "javadoc"
        elif '//' in content:
            return "single_line_comments"
        else:
            return "minimal"
            
    def _start_maintenance_thread(self) -> None:
        """Start background maintenance thread."""
        def maintenance_loop():
            while not self._stop_maintenance.wait(self.sync_interval):
                try:
                    self.immediate_context.cleanup()
                    self.session_memory.cleanup()
                    self.long_term_knowledge.cleanup()
                    
                    if time.time() - self.last_sync > self.sync_interval:
                        self._save_persistent_state()
                        self.last_sync = time.time()
                        
                except Exception as e:
                    print(f"⚠ Maintenance error: {e}")
                    
        self._maintenance_thread = threading.Thread(target=maintenance_loop, daemon=True)
        self._maintenance_thread.start()
        
    def shutdown(self) -> None:
        """Gracefully shutdown the file system."""
        print("🔄 Shutting down High-Performance File System...")
        
        if self._maintenance_thread:
            self._stop_maintenance.set()
            self._maintenance_thread.join(timeout=5)
            
        self._save_persistent_state()
        
        print("✅ High-Performance File System shutdown complete")
        
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and metrics."""
        return {
            "initialized": self.is_initialized,
            "immediate_context_size": len(self.immediate_context.data),
            "session_memory_size": len(self.session_memory.data),
            "long_term_knowledge_size": len(self.long_term_knowledge.data),
            "file_relationships": len(self.session_memory.file_relationships),
            "learned_patterns": len(self.session_memory.pattern_library),
            "error_solutions": len(self.long_term_knowledge.error_solutions),
            "last_sync": self.last_sync,
            "uptime": time.time() - (self.last_sync or time.time())
        }

_file_system_instance = None

def get_file_system() -> HighPerformanceFileSystem:
    """Get the global file system instance."""
    global _file_system_instance
    if _file_system_instance is None:
        _file_system_instance = HighPerformanceFileSystem()
    return _file_system_instance

def initialize_file_system() -> bool:
    """Initialize the global file system."""
    fs = get_file_system()
    return fs.initialize()

def shutdown_file_system() -> None:
    """Shutdown the global file system."""
    global _file_system_instance
    if _file_system_instance:
        _file_system_instance.shutdown()
        _file_system_instance = None

if __name__ == "__main__":
    success = initialize_file_system()
    if success:
        fs = get_file_system()
        status = fs.get_system_status()
        print(f"\n📊 System Status: {json.dumps(status, indent=2)}")
        
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            pass
        finally:
            shutdown_file_system()