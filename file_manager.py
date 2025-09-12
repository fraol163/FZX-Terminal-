"""
File Manager for AI Terminal Workflow
Core file operations, verification, and maintenance

Provides:
- File integrity checking
- Automated backup management
- Security validation
- Performance monitoring
- Dependency tracking
"""

import os
import sys
import json
import time
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict
import tempfile
import subprocess

class FileIntegrityChecker:
    """Handles file integrity checking and validation."""
    
    def __init__(self):
        self.checksums = {}
        self.last_check = {}
        
    def calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum of a file."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""
            
    def verify_file_integrity(self, file_path: str) -> Dict[str, Any]:
        """Verify file integrity and detect changes."""
        result = {
            "path": file_path,
            "exists": os.path.exists(file_path),
            "readable": False,
            "writable": False,
            "size": 0,
            "modified_time": 0,
            "checksum": "",
            "changed": False,
            "errors": []
        }
        
        try:
            if result["exists"]:
                result["readable"] = os.access(file_path, os.R_OK)
                result["writable"] = os.access(file_path, os.W_OK)
                
                stat = os.stat(file_path)
                result["size"] = stat.st_size
                result["modified_time"] = stat.st_mtime
                
                current_checksum = self.calculate_checksum(file_path)
                result["checksum"] = current_checksum
                
                if file_path in self.checksums:
                    result["changed"] = self.checksums[file_path] != current_checksum
                    
                self.checksums[file_path] = current_checksum
                self.last_check[file_path] = time.time()
                
        except Exception as e:
            result["errors"].append(str(e))
            
        return result
        
    def batch_verify(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Verify multiple files in batch."""
        results = []
        for file_path in file_paths:
            results.append(self.verify_file_integrity(file_path))
        return results

class BackupManager:
    """Manages automated backups and rollback functionality."""
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.max_backups = 10
        self.backup_metadata = {}
        
    def create_backup(self, file_path: str, reason: str = "manual") -> Optional[str]:
        """Create a backup of the specified file."""
        try:
            if not os.path.exists(file_path):
                return None
                
            original_path = Path(file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{original_path.stem}_{timestamp}{original_path.suffix}.bak"
            backup_path = self.backup_dir / backup_name
            
            shutil.copy2(file_path, backup_path)
            
            self.backup_metadata[str(backup_path)] = {
                "original_path": file_path,
                "created_time": time.time(),
                "reason": reason,
                "size": os.path.getsize(file_path)
            }
            
            self._cleanup_old_backups(file_path)
            
            return str(backup_path)
            
        except Exception as e:
            print(f"⚠ Backup failed for {file_path}: {e}")
            return None
            
    def restore_backup(self, backup_path: str) -> bool:
        """Restore a file from backup."""
        try:
            if backup_path not in self.backup_metadata:
                return False
                
            metadata = self.backup_metadata[backup_path]
            original_path = metadata["original_path"]
            
            if os.path.exists(original_path):
                self.create_backup(original_path, "pre_restore")
                
            shutil.copy2(backup_path, original_path)
            
            print(f"✓ Restored {original_path} from backup")
            return True
            
        except Exception as e:
            print(f"✗ Restore failed: {e}")
            return False
            
    def _cleanup_old_backups(self, original_file: str) -> None:
        """Remove old backups to maintain backup limit."""
        try:
            file_stem = Path(original_file).stem
            backups = []
            
            for backup_path, metadata in self.backup_metadata.items():
                if metadata["original_path"] == original_file:
                    backups.append((backup_path, metadata["created_time"]))
                    
            backups.sort(key=lambda x: x[1], reverse=True)
            
            for backup_path, _ in backups[self.max_backups:]:
                try:
                    os.remove(backup_path)
                    del self.backup_metadata[backup_path]
                except Exception:
                    pass
                    
        except Exception:
            pass
            
    def list_backups(self, original_file: Optional[str] = None) -> List[Dict[str, Any]]:
        """List available backups."""
        backups = []
        
        for backup_path, metadata in self.backup_metadata.items():
            if original_file is None or metadata["original_path"] == original_file:
                backup_info = metadata.copy()
                backup_info["backup_path"] = backup_path
                backup_info["created_time_str"] = datetime.fromtimestamp(
                    metadata["created_time"]
                ).strftime("%Y-%m-%d %H:%M:%S")
                backups.append(backup_info)
                
        return sorted(backups, key=lambda x: x["created_time"], reverse=True)

class SecurityValidator:
    """Validates files for security issues."""
    
    def __init__(self):
        self.security_patterns = {
            "secrets": [
                r"password\s*=\s*['\"][^'\"]+['\"]?",
                r"api_key\s*=\s*['\"][^'\"]+['\"]?",
                r"secret\s*=\s*['\"][^'\"]+['\"]?",
                r"token\s*=\s*['\"][^'\"]+['\"]?",
                r"-----BEGIN PRIVATE KEY-----",
                r"-----BEGIN RSA PRIVATE KEY-----"
            ],
            "vulnerabilities": [
                r"eval\s*\(",
                r"exec\s*\(",
                r"os\.system\s*\(",
                r"subprocess\.call\s*\(",
                r"shell=True"
            ]
        }
        
    def scan_file(self, file_path: str) -> Dict[str, Any]:
        """Scan file for security issues."""
        result = {
            "path": file_path,
            "safe": True,
            "issues": [],
            "warnings": [],
            "scan_time": time.time()
        }
        
        try:
            if not os.path.exists(file_path):
                result["issues"].append("File does not exist")
                result["safe"] = False
                return result
                
            if not self._is_text_file(file_path):
                return result
                
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            import re
            for pattern in self.security_patterns["secrets"]:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    result["issues"].append(f"Potential secret found: {pattern}")
                    result["safe"] = False
                    
            for pattern in self.security_patterns["vulnerabilities"]:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    result["warnings"].append(f"Potential vulnerability: {pattern}")
                    
        except Exception as e:
            result["issues"].append(f"Scan error: {str(e)}")
            result["safe"] = False
            
        return result
        
    def _is_text_file(self, file_path: str) -> bool:
        """Check if file is a text file."""
        text_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', 
                          '.md', '.txt', '.json', '.yaml', '.yml', '.xml', '.html', 
                          '.css', '.sql', '.sh', '.bat', '.ps1'}
        return Path(file_path).suffix.lower() in text_extensions

class PerformanceMonitor:
    """Monitors file system performance."""
    
    def __init__(self):
        self.metrics = {
            "file_operations": [],
            "response_times": [],
            "error_counts": defaultdict(int)
        }
        
    def time_operation(self, operation_name: str):
        """Context manager to time file operations."""
        return OperationTimer(self, operation_name)
        
    def record_operation(self, operation: str, duration: float, success: bool) -> None:
        """Record a file operation metric."""
        self.metrics["file_operations"].append({
            "operation": operation,
            "duration": duration,
            "success": success,
            "timestamp": time.time()
        })
        
        self.metrics["response_times"].append(duration)
        
        if not success:
            self.metrics["error_counts"][operation] += 1
            
        if len(self.metrics["file_operations"]) > 1000:
            self.metrics["file_operations"] = self.metrics["file_operations"][-500:]
        if len(self.metrics["response_times"]) > 1000:
            self.metrics["response_times"] = self.metrics["response_times"][-500:]
            
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        response_times = self.metrics["response_times"]
        
        if not response_times:
            return {"no_data": True}
            
        return {
            "total_operations": len(self.metrics["file_operations"]),
            "avg_response_time": sum(response_times) / len(response_times),
            "max_response_time": max(response_times),
            "min_response_time": min(response_times),
            "error_counts": dict(self.metrics["error_counts"]),
            "recent_operations": self.metrics["file_operations"][-10:]
        }

class OperationTimer:
    """Context manager for timing operations."""
    
    def __init__(self, monitor: PerformanceMonitor, operation_name: str):
        self.monitor = monitor
        self.operation_name = operation_name
        self.start_time = None
        self.success = True
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.success = exc_type is None
        self.monitor.record_operation(self.operation_name, duration, self.success)

class FileManager:
    """Main file manager coordinating all file operations."""
    
    def __init__(self):
        self.project_root = Path(os.getcwd())
        self.integrity_checker = FileIntegrityChecker()
        self.backup_manager = BackupManager()
        self.security_validator = SecurityValidator()
        self.performance_monitor = PerformanceMonitor()
        
    def verify_project_files(self, file_list: List[str]) -> Dict[str, Any]:
        """Verify all project files comprehensively."""
        with self.performance_monitor.time_operation("verify_project_files"):
            results = {
                "timestamp": datetime.now().isoformat(),
                "total_files": len(file_list),
                "integrity_results": [],
                "security_results": [],
                "backup_status": [],
                "summary": {
                    "files_ok": 0,
                    "files_changed": 0,
                    "files_missing": 0,
                    "security_issues": 0,
                    "backups_created": 0
                }
            }
            
            for file_path in file_list:
                integrity = self.integrity_checker.verify_file_integrity(file_path)
                results["integrity_results"].append(integrity)
                
                if integrity["exists"]:
                    if integrity["changed"]:
                        results["summary"]["files_changed"] += 1
                        backup_path = self.backup_manager.create_backup(file_path, "file_changed")
                        if backup_path:
                            results["summary"]["backups_created"] += 1
                            results["backup_status"].append({
                                "file": file_path,
                                "backup": backup_path,
                                "status": "created"
                            })
                    else:
                        results["summary"]["files_ok"] += 1
                        
                    security = self.security_validator.scan_file(file_path)
                    results["security_results"].append(security)
                    
                    if not security["safe"] or security["warnings"]:
                        results["summary"]["security_issues"] += 1
                        
                else:
                    results["summary"]["files_missing"] += 1
                    
            return results
            
    def create_project_backup(self, reason: str = "project_checkpoint") -> Dict[str, Any]:
        """Create backup of entire project."""
        with self.performance_monitor.time_operation("create_project_backup"):
            backup_info = {
                "timestamp": datetime.now().isoformat(),
                "reason": reason,
                "files_backed_up": [],
                "errors": [],
                "total_size": 0
            }
            
            try:
                for root, dirs, files in os.walk(self.project_root):
                    dirs[:] = [d for d in dirs if d not in ['backups', '.git', 'node_modules', '__pycache__']]
                    
                    for file in files:
                        if not file.startswith('.') and not file.endswith('.pyc'):
                            file_path = os.path.join(root, file)
                            
                            backup_path = self.backup_manager.create_backup(file_path, reason)
                            if backup_path:
                                file_size = os.path.getsize(file_path)
                                backup_info["files_backed_up"].append({
                                    "original": file_path,
                                    "backup": backup_path,
                                    "size": file_size
                                })
                                backup_info["total_size"] += file_size
                            else:
                                backup_info["errors"].append(f"Failed to backup {file_path}")
                                
            except Exception as e:
                backup_info["errors"].append(f"Project backup error: {str(e)}")
                
            return backup_info
            
    def maintenance_check(self) -> Dict[str, Any]:
        """Perform comprehensive maintenance check."""
        with self.performance_monitor.time_operation("maintenance_check"):
            maintenance_report = {
                "timestamp": datetime.now().isoformat(),
                "performance_stats": self.performance_monitor.get_performance_stats(),
                "backup_summary": {
                    "total_backups": len(self.backup_manager.backup_metadata),
                    "recent_backups": self.backup_manager.list_backups()[:5]
                },
                "recommendations": []
            }
            
            perf_stats = maintenance_report["performance_stats"]
            if not perf_stats.get("no_data"):
                avg_time = perf_stats.get("avg_response_time", 0)
                if avg_time > 1.0:
                    maintenance_report["recommendations"].append(
                        "Consider optimizing file operations - average response time is high"
                    )
                    
                error_count = sum(perf_stats.get("error_counts", {}).values())
                if error_count > 10:
                    maintenance_report["recommendations"].append(
                        f"High error count detected ({error_count}) - investigate file system issues"
                    )
                    
            backup_count = maintenance_report["backup_summary"]["total_backups"]
            if backup_count == 0:
                maintenance_report["recommendations"].append(
                    "No backups found - consider creating project backup"
                )
            elif backup_count > 100:
                maintenance_report["recommendations"].append(
                    "Large number of backups - consider cleanup"
                )
                
            return maintenance_report
            
    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report."""
        return {
            "file_manager_status": "active",
            "project_root": str(self.project_root),
            "integrity_checker": {
                "tracked_files": len(self.integrity_checker.checksums),
                "last_checks": len(self.integrity_checker.last_check)
            },
            "backup_manager": {
                "backup_directory": str(self.backup_manager.backup_dir),
                "total_backups": len(self.backup_manager.backup_metadata),
                "max_backups_per_file": self.backup_manager.max_backups
            },
            "performance_monitor": self.performance_monitor.get_performance_stats(),
            "timestamp": datetime.now().isoformat()
        }

_file_manager_instance = None

def get_file_manager() -> FileManager:
    """Get the global file manager instance."""
    global _file_manager_instance
    if _file_manager_instance is None:
        _file_manager_instance = FileManager()
    return _file_manager_instance

if __name__ == "__main__":
    fm = get_file_manager()
    
    test_files = ["startup_hook.py", "auto_startup.py", "high_performance_file_system.py"]
    
    print("🔍 Testing File Manager...")
    
    verification_result = fm.verify_project_files(test_files)
    print(f"\n📋 Verification Results:")
    print(f"  Files OK: {verification_result['summary']['files_ok']}")
    print(f"  Files Changed: {verification_result['summary']['files_changed']}")
    print(f"  Files Missing: {verification_result['summary']['files_missing']}")
    print(f"  Security Issues: {verification_result['summary']['security_issues']}")
    
    status = fm.get_status_report()
    print(f"\n📊 Status Report:")
    print(f"  Tracked Files: {status['integrity_checker']['tracked_files']}")
    print(f"  Total Backups: {status['backup_manager']['total_backups']}")
    
    print("\n✅ File Manager test completed")