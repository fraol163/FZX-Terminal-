"""
Terminal Persistence Engine for AI Terminal Workflow
Handles command correlation, output tracking, and terminal state preservation

Addresses user struggles:
- Terminal history disappearing between sessions
- Lost command context and output correlation
- Inability to resume interrupted workflows
- Missing command execution patterns
"""

import os
import sys
import json
import time
import uuid
import hashlib
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from enum import Enum
import re

class CommandStatus(Enum):
    """Command execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    INTERRUPTED = "interrupted"
    TIMEOUT = "timeout"

class OutputType(Enum):
    """Output stream types."""
    STDOUT = "stdout"
    STDERR = "stderr"
    COMBINED = "combined"

@dataclass
class CommandExecution:
    """Represents a single command execution."""
    command_id: str
    command: str
    working_directory: str
    environment: Dict[str, str]
    start_time: float
    end_time: Optional[float] = None
    status: CommandStatus = CommandStatus.PENDING
    exit_code: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    output_chunks: List[Dict[str, Any]] = None
    parent_command_id: Optional[str] = None
    child_command_ids: List[str] = None
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.output_chunks is None:
            self.output_chunks = []
        if self.child_command_ids is None:
            self.child_command_ids = []
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}

@dataclass
class TerminalSession:
    """Represents a terminal session."""
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    working_directory: str = ""
    environment_snapshot: Dict[str, str] = None
    command_history: List[str] = None
    active_processes: Dict[str, Any] = None
    session_metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.environment_snapshot is None:
            self.environment_snapshot = {}
        if self.command_history is None:
            self.command_history = []
        if self.active_processes is None:
            self.active_processes = {}
        if self.session_metadata is None:
            self.session_metadata = {}

class CommandCorrelator:
    """Correlates commands with their outputs and relationships."""
    
    def __init__(self):
        self.correlation_patterns = {
            'build_sequence': [r'npm\s+install', r'npm\s+run\s+build', r'npm\s+start'],
            'git_workflow': [r'git\s+add', r'git\s+commit', r'git\s+push'],
            'test_sequence': [r'npm\s+test', r'pytest', r'python\s+-m\s+unittest'],
            'docker_workflow': [r'docker\s+build', r'docker\s+run', r'docker\s+push'],
            'python_workflow': [r'pip\s+install', r'python\s+.*\.py', r'python\s+-m'],
            'file_operations': [r'mkdir', r'touch', r'cp', r'mv', r'rm']
        }
        
        self.command_relationships = defaultdict(list)
        self.workflow_patterns = defaultdict(int)
        
    def analyze_command_sequence(self, commands: List[CommandExecution]) -> Dict[str, Any]:
        """Analyze a sequence of commands for patterns and relationships."""
        analysis = {
            'detected_workflows': [],
            'command_chains': [],
            'error_patterns': [],
            'optimization_suggestions': [],
            'success_patterns': []
        }
        
        sorted_commands = sorted(commands, key=lambda x: x.start_time)
        
        for workflow_name, patterns in self.correlation_patterns.items():
            matches = self._find_workflow_matches(sorted_commands, patterns)
            if matches:
                analysis['detected_workflows'].append({
                    'workflow': workflow_name,
                    'matches': matches,
                    'success_rate': self._calculate_success_rate(matches)
                })
        
        chains = self._identify_command_chains(sorted_commands)
        analysis['command_chains'] = chains
        
        error_patterns = self._analyze_error_patterns(sorted_commands)
        analysis['error_patterns'] = error_patterns
        
        suggestions = self._generate_optimization_suggestions(sorted_commands)
        analysis['optimization_suggestions'] = suggestions
        
        return analysis
    
    def _find_workflow_matches(self, commands: List[CommandExecution], patterns: List[str]) -> List[Dict[str, Any]]:
        """Find matches for a specific workflow pattern."""
        matches = []
        pattern_index = 0
        current_match = {'commands': [], 'start_time': None, 'success': True}
        
        for cmd in commands:
            if pattern_index < len(patterns):
                if re.search(patterns[pattern_index], cmd.command, re.IGNORECASE):
                    if current_match['start_time'] is None:
                        current_match['start_time'] = cmd.start_time
                    
                    current_match['commands'].append({
                        'command_id': cmd.command_id,
                        'command': cmd.command,
                        'status': cmd.status.value,
                        'exit_code': cmd.exit_code
                    })
                    
                    if cmd.status == CommandStatus.FAILED:
                        current_match['success'] = False
                    
                    pattern_index += 1
                    
                    if pattern_index == len(patterns):
                        current_match['end_time'] = cmd.end_time or cmd.start_time
                        current_match['duration'] = current_match['end_time'] - current_match['start_time']
                        matches.append(current_match.copy())
                        
                        current_match = {'commands': [], 'start_time': None, 'success': True}
                        pattern_index = 0
        
        return matches
    
    def _identify_command_chains(self, commands: List[CommandExecution]) -> List[Dict[str, Any]]:
        """Identify chains of related commands."""
        chains = []
        current_chain = []
        
        for i, cmd in enumerate(commands):
            if not current_chain:
                current_chain.append(cmd)
                continue
            
            prev_cmd = current_chain[-1]
            time_gap = cmd.start_time - (prev_cmd.end_time or prev_cmd.start_time)
            
            if (time_gap < 30 and 
                cmd.working_directory == prev_cmd.working_directory):
                current_chain.append(cmd)
            else:
                if len(current_chain) > 1:
                    chains.append(self._create_chain_summary(current_chain))
                current_chain = [cmd]
        
        if len(current_chain) > 1:
            chains.append(self._create_chain_summary(current_chain))
        
        return chains
    
    def _create_chain_summary(self, commands: List[CommandExecution]) -> Dict[str, Any]:
        """Create a summary for a command chain."""
        return {
            'chain_id': f"chain_{commands[0].command_id[:8]}",
            'command_count': len(commands),
            'start_time': commands[0].start_time,
            'end_time': commands[-1].end_time or commands[-1].start_time,
            'working_directory': commands[0].working_directory,
            'commands': [{
                'command_id': cmd.command_id,
                'command': cmd.command,
                'status': cmd.status.value,
                'exit_code': cmd.exit_code
            } for cmd in commands],
            'overall_success': all(cmd.status == CommandStatus.COMPLETED for cmd in commands)
        }
    
    def _analyze_error_patterns(self, commands: List[CommandExecution]) -> List[Dict[str, Any]]:
        """Analyze patterns in command failures."""
        error_patterns = []
        failed_commands = [cmd for cmd in commands if cmd.status == CommandStatus.FAILED]
        
        error_groups = defaultdict(list)
        
        for cmd in failed_commands:
            error_signature = self._extract_error_signature(cmd.stderr)
            error_groups[error_signature].append(cmd)
        
        for error_sig, cmd_list in error_groups.items():
            if len(cmd_list) > 1:
                error_patterns.append({
                    'error_signature': error_sig,
                    'occurrence_count': len(cmd_list),
                    'affected_commands': [cmd.command for cmd in cmd_list],
                    'first_occurrence': min(cmd.start_time for cmd in cmd_list),
                    'last_occurrence': max(cmd.start_time for cmd in cmd_list)
                })
        
        return error_patterns
    
    def _extract_error_signature(self, stderr: str) -> str:
        """Extract a signature from error output for pattern matching."""
        if not stderr:
            return "unknown_error"
        
        error_patterns = [
            r'ModuleNotFoundError: No module named \'([^\']*)\'',
            r'FileNotFoundError: \[Errno 2\] No such file or directory: \'([^\']*)\'',
            r'SyntaxError: (.+)',
            r'TypeError: (.+)',
            r'ValueError: (.+)',
            r'npm ERR! (.+)',
            r'Error: (.+)',
        ]
        
        for pattern in error_patterns:
            match = re.search(pattern, stderr, re.IGNORECASE)
            if match:
                return f"{pattern.split(':')[0]}_{match.group(1)[:50]}"
        
        first_line = stderr.split('\n')[0].strip()
        return first_line[:100] if first_line else "unknown_error"
    
    def _calculate_success_rate(self, matches: List[Dict[str, Any]]) -> float:
        """Calculate success rate for workflow matches."""
        if not matches:
            return 0.0
        
        successful_matches = sum(1 for match in matches if match['success'])
        return successful_matches / len(matches)
    
    def _generate_optimization_suggestions(self, commands: List[CommandExecution]) -> List[str]:
        """Generate optimization suggestions based on command patterns."""
        suggestions = []
        
        command_frequency = defaultdict(int)
        for cmd in commands:
            base_command = cmd.command.split()[0] if cmd.command.split() else cmd.command
            command_frequency[base_command] += 1
        
        for cmd, count in command_frequency.items():
            if count > 5 and len(cmd) > 10:
                suggestions.append(f"Consider creating an alias for '{cmd}' (used {count} times)")
        
        failed_commands = [cmd for cmd in commands if cmd.status == CommandStatus.FAILED]
        if len(failed_commands) > len(commands) * 0.2:
            suggestions.append("High command failure rate detected. Consider reviewing command syntax and dependencies.")
        
        long_commands = []
        for cmd in commands:
            if cmd.end_time and (cmd.end_time - cmd.start_time) > 300:
                long_commands.append(cmd)
        
        if long_commands:
            suggestions.append(f"Found {len(long_commands)} long-running commands. Consider optimization or background execution.")
        
        return suggestions

class OutputTracker:
    """Tracks and correlates command outputs."""
    
    def __init__(self):
        self.output_buffer_size = 10000
        self.output_patterns = {
            'success_indicators': [r'success', r'completed', r'done', r'✓', r'✅'],
            'error_indicators': [r'error', r'failed', r'exception', r'✗', r'❌'],
            'warning_indicators': [r'warning', r'warn', r'⚠', r'deprecated'],
            'progress_indicators': [r'\d+%', r'\d+/\d+', r'loading', r'processing']
        }
    
    def track_output(self, command_execution: CommandExecution, 
                    output_data: str, output_type: OutputType) -> Dict[str, Any]:
        """Track and analyze command output."""
        
        if output_type == OutputType.STDOUT:
            command_execution.stdout += output_data
        elif output_type == OutputType.STDERR:
            command_execution.stderr += output_data
        
        chunk = {
            'timestamp': time.time(),
            'output_type': output_type.value,
            'content': output_data,
            'size': len(output_data),
            'analysis': self._analyze_output_chunk(output_data)
        }
        
        command_execution.output_chunks.append(chunk)
        
        self._trim_output_if_needed(command_execution)
        
        return chunk
    
    def _analyze_output_chunk(self, output_data: str) -> Dict[str, Any]:
        """Analyze output chunk for patterns and indicators."""
        analysis = {
            'indicators': [],
            'patterns': [],
            'severity': 'info',
            'contains_error': False,
            'contains_warning': False,
            'progress_info': None
        }
        
        output_lower = output_data.lower()
        
        for indicator_type, patterns in self.output_patterns.items():
            for pattern in patterns:
                if re.search(pattern, output_lower):
                    analysis['indicators'].append(indicator_type)
                    
                    if indicator_type == 'error_indicators':
                        analysis['contains_error'] = True
                        analysis['severity'] = 'error'
                    elif indicator_type == 'warning_indicators':
                        analysis['contains_warning'] = True
                        if analysis['severity'] == 'info':
                            analysis['severity'] = 'warning'
        
        progress_match = re.search(r'(\d+)%|(\d+)/(\d+)', output_data)
        if progress_match:
            if progress_match.group(1):
                analysis['progress_info'] = {'type': 'percentage', 'value': int(progress_match.group(1))}
            else:
                current = int(progress_match.group(2))
                total = int(progress_match.group(3))
                percentage = (current / total) * 100 if total > 0 else 0
                analysis['progress_info'] = {
                    'type': 'fraction',
                    'current': current,
                    'total': total,
                    'percentage': percentage
                }
        
        return analysis
    
    def _trim_output_if_needed(self, command_execution: CommandExecution) -> None:
        """Trim output if it exceeds buffer size."""
        if len(command_execution.stdout) > self.output_buffer_size:
            keep_size = self.output_buffer_size // 3
            command_execution.stdout = (
                command_execution.stdout[:keep_size] + 
                "\n... [OUTPUT TRUNCATED] ...\n" +
                command_execution.stdout[-keep_size:]
            )
        
        if len(command_execution.stderr) > self.output_buffer_size:
            keep_size = self.output_buffer_size // 3
            command_execution.stderr = (
                command_execution.stderr[:keep_size] + 
                "\n... [ERROR OUTPUT TRUNCATED] ...\n" +
                command_execution.stderr[-keep_size:]
            )
    
    def get_output_summary(self, command_execution: CommandExecution) -> Dict[str, Any]:
        """Get a summary of command output."""
        summary = {
            'total_output_size': len(command_execution.stdout) + len(command_execution.stderr),
            'stdout_size': len(command_execution.stdout),
            'stderr_size': len(command_execution.stderr),
            'chunk_count': len(command_execution.output_chunks),
            'has_errors': any(chunk['analysis']['contains_error'] for chunk in command_execution.output_chunks),
            'has_warnings': any(chunk['analysis']['contains_warning'] for chunk in command_execution.output_chunks),
            'final_status': command_execution.status.value,
            'exit_code': command_execution.exit_code
        }
        
        if command_execution.stdout:
            summary['stdout_preview'] = command_execution.stdout[:200] + ('...' if len(command_execution.stdout) > 200 else '')
        
        if command_execution.stderr:
            summary['stderr_preview'] = command_execution.stderr[:200] + ('...' if len(command_execution.stderr) > 200 else '')
        
        return summary

class TerminalPersistenceEngine:
    """Main terminal persistence engine."""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.persistence_dir = self.project_root / ".terminal_persistence"
        self.persistence_dir.mkdir(exist_ok=True)
        
        self.sessions_file = self.persistence_dir / "sessions.json"
        self.commands_file = self.persistence_dir / "commands.json"
        self.correlations_file = self.persistence_dir / "correlations.json"
        
        self.correlator = CommandCorrelator()
        self.output_tracker = OutputTracker()
        
        self.active_sessions: Dict[str, TerminalSession] = {}
        self.command_history: Dict[str, CommandExecution] = {}
        
        self._load_persistent_data()
    
    def create_session(self, working_directory: str = None) -> str:
        """Create a new terminal session."""
        session_id = str(uuid.uuid4())[:8]
        
        session = TerminalSession(
            session_id=session_id,
            start_time=time.time(),
            working_directory=working_directory or os.getcwd(),
            environment_snapshot=dict(os.environ)
        )
        
        self.active_sessions[session_id] = session
        
        print(f"✓ Created terminal session: {session_id}")
        return session_id
    
    def execute_command(self, command: str, session_id: str = None, 
                       working_directory: str = None, 
                       environment: Dict[str, str] = None,
                       timeout: int = None) -> str:
        """Execute a command and track its execution."""
        
        command_id = str(uuid.uuid4())[:12]
        
        cmd_execution = CommandExecution(
            command_id=command_id,
            command=command,
            working_directory=working_directory or os.getcwd(),
            environment=environment or dict(os.environ),
            start_time=time.time()
        )
        
        if session_id and session_id in self.active_sessions:
            self.active_sessions[session_id].command_history.append(command_id)
        
        self.command_history[command_id] = cmd_execution
        
        print(f"🚀 Executing command [{command_id}]: {command}")
        
        try:
            self._execute_with_tracking(cmd_execution, timeout)
            
        except Exception as e:
            cmd_execution.status = CommandStatus.FAILED
            cmd_execution.stderr += f"\nExecution error: {str(e)}"
            cmd_execution.end_time = time.time()
            print(f"✗ Command failed [{command_id}]: {str(e)}")
        
        self._save_persistent_data()
        
        return command_id
    
    def _execute_with_tracking(self, cmd_execution: CommandExecution, timeout: int = None) -> None:
        """Execute command with real-time output tracking."""
        cmd_execution.status = CommandStatus.RUNNING
        
        try:
            process = subprocess.Popen(
                cmd_execution.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cmd_execution.working_directory,
                env=cmd_execution.environment
            )
            
            stdout_thread = threading.Thread(
                target=self._track_output_stream,
                args=(process.stdout, cmd_execution, OutputType.STDOUT)
            )
            stderr_thread = threading.Thread(
                target=self._track_output_stream,
                args=(process.stderr, cmd_execution, OutputType.STDERR)
            )
            
            stdout_thread.start()
            stderr_thread.start()
            
            try:
                exit_code = process.wait(timeout=timeout)
                cmd_execution.exit_code = exit_code
                cmd_execution.status = CommandStatus.COMPLETED if exit_code == 0 else CommandStatus.FAILED
            except subprocess.TimeoutExpired:
                process.kill()
                cmd_execution.status = CommandStatus.TIMEOUT
                cmd_execution.exit_code = -1
            
            stdout_thread.join(timeout=5)
            stderr_thread.join(timeout=5)
            
        except KeyboardInterrupt:
            cmd_execution.status = CommandStatus.INTERRUPTED
            if 'process' in locals():
                process.kill()
        
        cmd_execution.end_time = time.time()
        
        duration = cmd_execution.end_time - cmd_execution.start_time
        status_symbol = "✓" if cmd_execution.status == CommandStatus.COMPLETED else "✗"
        print(f"{status_symbol} Command completed [{cmd_execution.command_id}] in {duration:.2f}s (exit: {cmd_execution.exit_code})")
    
    def _track_output_stream(self, stream, cmd_execution: CommandExecution, output_type: OutputType) -> None:
        """Track output from a stream in real-time."""
        try:
            for line in iter(stream.readline, ''):
                if line:
                    self.output_tracker.track_output(cmd_execution, line, output_type)
                    print(line.rstrip())
        except Exception as e:
            print(f"Warning: Error tracking {output_type.value} stream: {e}")
    
    def get_command_status(self, command_id: str) -> Optional[Dict[str, Any]]:
        """Get status and details of a command execution."""
        if command_id not in self.command_history:
            return None
        
        cmd_execution = self.command_history[command_id]
        output_summary = self.output_tracker.get_output_summary(cmd_execution)
        
        return {
            'command_id': command_id,
            'command': cmd_execution.command,
            'status': cmd_execution.status.value,
            'start_time': cmd_execution.start_time,
            'end_time': cmd_execution.end_time,
            'duration': (cmd_execution.end_time - cmd_execution.start_time) if cmd_execution.end_time else None,
            'exit_code': cmd_execution.exit_code,
            'working_directory': cmd_execution.working_directory,
            'output_summary': output_summary
        }
    
    def analyze_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Analyze a terminal session for patterns and insights."""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        
        session_commands = [
            self.command_history[cmd_id] 
            for cmd_id in session.command_history 
            if cmd_id in self.command_history
        ]
        
        correlation_analysis = self.correlator.analyze_command_sequence(session_commands)
        
        return {
            'session_id': session_id,
            'start_time': session.start_time,
            'command_count': len(session_commands),
            'working_directory': session.working_directory,
            'correlation_analysis': correlation_analysis,
            'session_summary': {
                'successful_commands': len([cmd for cmd in session_commands if cmd.status == CommandStatus.COMPLETED]),
                'failed_commands': len([cmd for cmd in session_commands if cmd.status == CommandStatus.FAILED]),
                'total_duration': sum(
                    (cmd.end_time - cmd.start_time) if cmd.end_time else 0 
                    for cmd in session_commands
                )
            }
        }
    
    def restore_session_state(self, session_id: str) -> bool:
        """Restore terminal state from a previous session."""
        if session_id not in self.active_sessions:
            print(f"✗ Session {session_id} not found")
            return False
        
        session = self.active_sessions[session_id]
        
        try:
            os.chdir(session.working_directory)
            
            safe_env_vars = ['PATH', 'PYTHONPATH', 'NODE_PATH', 'VIRTUAL_ENV']
            for var in safe_env_vars:
                if var in session.environment_snapshot:
                    os.environ[var] = session.environment_snapshot[var]
            
            print(f"✓ Restored session state: {session_id}")
            print(f"  Working directory: {session.working_directory}")
            print(f"  Commands in history: {len(session.command_history)}")
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to restore session state: {e}")
            return False
    
    def _load_persistent_data(self) -> None:
        """Load persistent data from disk."""
        try:
            if self.sessions_file.exists():
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    sessions_data = json.load(f)
                    for session_id, session_data in sessions_data.items():
                        self.active_sessions[session_id] = TerminalSession(**session_data)
            
            if self.commands_file.exists():
                with open(self.commands_file, 'r', encoding='utf-8') as f:
                    commands_data = json.load(f)
                    for command_id, command_data in commands_data.items():
                        command_data['status'] = CommandStatus(command_data['status'])
                        self.command_history[command_id] = CommandExecution(**command_data)
            
        except Exception as e:
            print(f"⚠ Warning: Could not load persistent data: {e}")
    
    def _save_persistent_data(self) -> None:
        """Save persistent data to disk."""
        try:
            sessions_data = {}
            for session_id, session in self.active_sessions.items():
                sessions_data[session_id] = asdict(session)
            
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(sessions_data, f, indent=2, ensure_ascii=False)
            
            commands_data = {}
            for command_id, command in self.command_history.items():
                command_dict = asdict(command)
                command_dict['status'] = command.status.value
                commands_data[command_id] = command_dict
            
            with open(self.commands_file, 'w', encoding='utf-8') as f:
                json.dump(commands_data, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            print(f"⚠ Warning: Could not save persistent data: {e}")
    
    def get_persistence_summary(self) -> Dict[str, Any]:
        """Get summary of terminal persistence state."""
        return {
            'active_sessions': len(self.active_sessions),
            'total_commands': len(self.command_history),
            'successful_commands': len([cmd for cmd in self.command_history.values() if cmd.status == CommandStatus.COMPLETED]),
            'failed_commands': len([cmd for cmd in self.command_history.values() if cmd.status == CommandStatus.FAILED]),
            'recent_activity': {
                'last_command_time': max((cmd.start_time for cmd in self.command_history.values()), default=0),
                'commands_last_hour': len([
                    cmd for cmd in self.command_history.values() 
                    if cmd.start_time > time.time() - 3600
                ])
            }
        }

_terminal_engine_instance = None

def get_terminal_engine() -> TerminalPersistenceEngine:
    """Get the global terminal persistence engine instance."""
    global _terminal_engine_instance
    if _terminal_engine_instance is None:
        _terminal_engine_instance = TerminalPersistenceEngine()
    return _terminal_engine_instance

if __name__ == "__main__":
    engine = get_terminal_engine()
    
    print("🖥️  Testing Terminal Persistence Engine...")
    
    session_id = engine.create_session()
    
    cmd1_id = engine.execute_command("echo 'Hello World'", session_id)
    cmd2_id = engine.execute_command("python --version", session_id)
    
    status1 = engine.get_command_status(cmd1_id)
    print(f"\n📊 Command Status: {status1['status']} (exit: {status1['exit_code']})")
    
    analysis = engine.analyze_session(session_id)
    if analysis:
        print(f"\n🔍 Session Analysis:")
        print(f"  Commands executed: {analysis['command_count']}")
        print(f"  Successful: {analysis['session_summary']['successful_commands']}")
        print(f"  Failed: {analysis['session_summary']['failed_commands']}")
    
    summary = engine.get_persistence_summary()
    print(f"\n📈 Persistence Summary:")
    print(f"  Active sessions: {summary['active_sessions']}")
    print(f"  Total commands: {summary['total_commands']}")
    print(f"  Success rate: {summary['successful_commands']}/{summary['total_commands']}")
    
    print("\n✅ Terminal Persistence Engine test completed")