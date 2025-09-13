"""
File Structure Mapper for AI Terminal Workflow
Intelligent directory structure analysis and relationship mapping

Addresses user struggles:
- AI having to relearn file structure every time
- Missing project file relationship maps
- Lack of dependency tracking
- No instant navigation context
"""

import os
import sys
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
import re

@dataclass
class FileNode:
    """Represents a file or directory in the structure."""
    path: str
    name: str
    type: str  # 'file' or 'directory'
    size: int
    modified_time: float
    parent: Optional[str] = None
    children: List[str] = None
    imports: List[str] = None
    exports: List[str] = None
    dependencies: List[str] = None
    language: Optional[str] = None
    file_type: Optional[str] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []
        if self.imports is None:
            self.imports = []
        if self.exports is None:
            self.exports = []
        if self.dependencies is None:
            self.dependencies = []

class FileStructureMapper:
    """Maps and analyzes project file structure with relationships."""
    
    def __init__(self):
        self.project_root = Path(os.getcwd())
        self.structure_cache = {}
        self.relationship_graph = defaultdict(set)
        self.file_nodes: Dict[str, FileNode] = {}
        self.last_scan_time = 0
        self.ignore_patterns = {
            'directories': {'.git', '__pycache__', 'node_modules', '.vscode', '.idea', 'venv', 'env', '.env'},
            'files': {'.DS_Store', 'Thumbs.db', '*.pyc', '*.pyo', '*.pyd', '.gitignore'}
        }
        
    def scan_project_structure(self, force_rescan: bool = False) -> Dict[str, Any]:
        """Scan and map the complete project structure."""
        if not force_rescan and time.time() - self.last_scan_time < 300:  # 5 minutes cache
            return self.structure_cache
        
        print("🔍 Scanning project structure...")
        
        structure = {
            'root_path': str(self.project_root),
            'scan_time': time.time(),
            'total_files': 0,
            'total_directories': 0,
            'file_types': defaultdict(int),
            'languages': set(),
            'size_distribution': defaultdict(int),
            'depth_analysis': defaultdict(int)
        }
        
        self.file_nodes.clear()
        
        try:
            for root, dirs, files in os.walk(self.project_root):
                # Filter out ignored directories
                dirs[:] = [d for d in dirs if d not in self.ignore_patterns['directories']]
                
                current_depth = len(Path(root).relative_to(self.project_root).parts)
                structure['depth_analysis'][current_depth] += len(files) + len(dirs)
                
                # Process directories
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    self._create_directory_node(dir_path, root)
                    structure['total_directories'] += 1
                
                # Process files
                for file_name in files:
                    if self._should_ignore_file(file_name):
                        continue
                        
                    file_path = os.path.join(root, file_name)
                    file_node = self._create_file_node(file_path, root)
                    
                    if file_node:
                        structure['total_files'] += 1
                        structure['file_types'][file_node.file_type] += 1
                        
                        if file_node.language:
                            structure['languages'].add(file_node.language)
                        
                        # Size distribution
                        size_category = self._categorize_file_size(file_node.size)
                        structure['size_distribution'][size_category] += 1
        
        except Exception as e:
            print(f"⚠ Error during structure scan: {e}")
            return {}
        
        structure['languages'] = list(structure['languages'])
        structure['file_types'] = dict(structure['file_types'])
        structure['size_distribution'] = dict(structure['size_distribution'])
        structure['depth_analysis'] = dict(structure['depth_analysis'])
        
        self.structure_cache = structure
        self.last_scan_time = time.time()
        
        print(f"✓ Scanned {structure['total_files']} files and {structure['total_directories']} directories")
        
        return structure    

    def _create_directory_node(self, dir_path: str, parent_path: str) -> FileNode:
        """Create a directory node."""
        try:
            stat = os.stat(dir_path)
            
            node = FileNode(
                path=dir_path,
                name=os.path.basename(dir_path),
                type='directory',
                size=0,  # Directories don't have meaningful size
                modified_time=stat.st_mtime,
                parent=parent_path if parent_path != dir_path else None
            )
            
            self.file_nodes[dir_path] = node
            return node
            
        except Exception:
            return None
    
    def _create_file_node(self, file_path: str, parent_path: str) -> Optional[FileNode]:
        """Create a file node with analysis."""
        try:
            stat = os.stat(file_path)
            file_ext = Path(file_path).suffix.lower()
            
            node = FileNode(
                path=file_path,
                name=os.path.basename(file_path),
                type='file',
                size=stat.st_size,
                modified_time=stat.st_mtime,
                parent=parent_path,
                language=self._detect_language(file_ext),
                file_type=self._categorize_file_type(file_ext)
            )
            
            # Analyze file content for relationships
            if self._is_analyzable_file(file_ext):
                self._analyze_file_relationships(node)
            
            self.file_nodes[file_path] = node
            return node
            
        except Exception:
            return None
    
    def _should_ignore_file(self, file_name: str) -> bool:
        """Check if file should be ignored."""
        for pattern in self.ignore_patterns['files']:
            if pattern.startswith('*'):
                if file_name.endswith(pattern[1:]):
                    return True
            elif file_name == pattern:
                return True
        return False
    
    def _detect_language(self, file_ext: str) -> Optional[str]:
        """Detect programming language from file extension."""
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'JavaScript',
            '.tsx': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.h': 'C/C++',
            '.cs': 'C#',
            '.go': 'Go',
            '.rs': 'Rust',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.less': 'LESS',
            '.sql': 'SQL',
            '.sh': 'Shell',
            '.ps1': 'PowerShell',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.json': 'JSON',
            '.xml': 'XML',
            '.md': 'Markdown',
            '.rst': 'reStructuredText'
        }
        return language_map.get(file_ext)
    
    def _categorize_file_type(self, file_ext: str) -> str:
        """Categorize file by type."""
        categories = {
            'source': {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.cs', '.go', '.rs', '.php', '.rb'},
            'config': {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf'},
            'documentation': {'.md', '.rst', '.txt', '.doc', '.docx'},
            'web': {'.html', '.css', '.scss', '.less'},
            'data': {'.csv', '.xml', '.sql', '.db', '.sqlite'},
            'image': {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico'},
            'archive': {'.zip', '.tar', '.gz', '.rar', '.7z'},
            'executable': {'.exe', '.app', '.deb', '.rpm'}
        }
        
        for category, extensions in categories.items():
            if file_ext in extensions:
                return category
        
        return 'other'
    
    def _categorize_file_size(self, size: int) -> str:
        """Categorize file by size."""
        if size < 1024:  # < 1KB
            return 'tiny'
        elif size < 10240:  # < 10KB
            return 'small'
        elif size < 102400:  # < 100KB
            return 'medium'
        elif size < 1048576:  # < 1MB
            return 'large'
        else:
            return 'very_large'
    
    def _is_analyzable_file(self, file_ext: str) -> bool:
        """Check if file can be analyzed for relationships."""
        analyzable_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.cs', '.go', '.rs'}
        return file_ext in analyzable_extensions
    
    def _analyze_file_relationships(self, node: FileNode) -> None:
        """Analyze file for imports, exports, and dependencies."""
        try:
            with open(node.path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract imports based on language
            if node.language == 'Python':
                node.imports = self._extract_python_imports(content)
            elif node.language in ['JavaScript', 'TypeScript']:
                node.imports = self._extract_js_imports(content)
            elif node.language == 'Java':
                node.imports = self._extract_java_imports(content)
            
            # Build relationship graph
            for imported_item in node.imports:
                self.relationship_graph[node.path].add(imported_item)
                
        except Exception:
            pass
    
    def _extract_python_imports(self, content: str) -> List[str]:
        """Extract Python imports."""
        imports = []
        lines = content.split('\n')
        
        for line in lines[:50]:  # Only check first 50 lines
            line = line.strip()
            
            # Standard import
            if line.startswith('import '):
                module = line.replace('import ', '').split(' as ')[0].split(',')[0].strip()
                imports.append(module)
            
            # From import
            elif line.startswith('from '):
                match = re.match(r'from\s+([^\s]+)\s+import', line)
                if match:
                    imports.append(match.group(1))
        
        return imports
    
    def _extract_js_imports(self, content: str) -> List[str]:
        """Extract JavaScript/TypeScript imports."""
        imports = []
        
        # ES6 imports
        import_patterns = [
            r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'import\s+[\'"]([^\'"]+)[\'"]',
            r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            imports.extend(matches)
        
        return imports
    
    def _extract_java_imports(self, content: str) -> List[str]:
        """Extract Java imports."""
        imports = []
        
        import_pattern = r'import\s+([^;]+);'
        matches = re.findall(import_pattern, content)
        imports.extend(matches)
        
        return imports
    
    def get_file_relationships(self, file_path: str) -> Dict[str, Any]:
        """Get relationships for a specific file."""
        if file_path not in self.file_nodes:
            return {}
        
        node = self.file_nodes[file_path]
        
        # Find files that import this file
        imported_by = []
        for path, relationships in self.relationship_graph.items():
            if any(file_path in rel or node.name in rel for rel in relationships):
                imported_by.append(path)
        
        # Find related files in same directory
        same_directory = []
        parent_dir = os.path.dirname(file_path)
        for path, other_node in self.file_nodes.items():
            if (os.path.dirname(path) == parent_dir and 
                path != file_path and 
                other_node.type == 'file'):
                same_directory.append(path)
        
        return {
            'file_path': file_path,
            'imports': node.imports,
            'imported_by': imported_by,
            'same_directory': same_directory[:10],  # Limit to 10
            'language': node.language,
            'file_type': node.file_type,
            'size': node.size,
            'last_modified': datetime.fromtimestamp(node.modified_time).isoformat()
        }
    
    def get_project_overview(self) -> Dict[str, Any]:
        """Get comprehensive project overview."""
        if not self.structure_cache:
            self.scan_project_structure()
        
        # Calculate additional metrics
        source_files = [n for n in self.file_nodes.values() if n.file_type == 'source']
        config_files = [n for n in self.file_nodes.values() if n.file_type == 'config']
        
        # Find entry points (files with main functions or similar)
        entry_points = self._find_entry_points()
        
        # Calculate complexity metrics
        complexity = self._calculate_complexity_metrics()
        
        return {
            'structure_summary': self.structure_cache,
            'source_files_count': len(source_files),
            'config_files_count': len(config_files),
            'entry_points': entry_points,
            'complexity_metrics': complexity,
            'top_level_directories': self._get_top_level_directories(),
            'largest_files': self._get_largest_files(5),
            'most_connected_files': self._get_most_connected_files(5)
        }
    
    def _find_entry_points(self) -> List[str]:
        """Find potential entry points in the project."""
        entry_points = []
        
        common_entry_names = {'main.py', 'app.py', 'index.js', 'index.ts', 'server.js', 'manage.py'}
        
        for path, node in self.file_nodes.items():
            if node.name in common_entry_names:
                entry_points.append(path)
        
        return entry_points
    
    def _calculate_complexity_metrics(self) -> Dict[str, Any]:
        """Calculate project complexity metrics."""
        total_relationships = sum(len(rels) for rels in self.relationship_graph.values())
        source_files = [n for n in self.file_nodes.values() if n.file_type == 'source']
        
        return {
            'total_relationships': total_relationships,
            'avg_imports_per_file': total_relationships / len(source_files) if source_files else 0,
            'max_directory_depth': max(self.structure_cache.get('depth_analysis', {}).keys(), default=0),
            'coupling_score': total_relationships / len(self.file_nodes) if self.file_nodes else 0
        }
    
    def _get_top_level_directories(self) -> List[str]:
        """Get top-level directories."""
        top_level = []
        
        for path, node in self.file_nodes.items():
            if (node.type == 'directory' and 
                node.parent == str(self.project_root)):
                top_level.append(node.name)
        
        return sorted(top_level)
    
    def _get_largest_files(self, count: int) -> List[Dict[str, Any]]:
        """Get largest files by size."""
        files = [n for n in self.file_nodes.values() if n.type == 'file']
        largest = sorted(files, key=lambda x: x.size, reverse=True)[:count]
        
        return [
            {
                'path': f.path,
                'name': f.name,
                'size': f.size,
                'language': f.language
            }
            for f in largest
        ]
    
    def _get_most_connected_files(self, count: int) -> List[Dict[str, Any]]:
        """Get files with most relationships."""
        file_connections = {}
        
        for path, node in self.file_nodes.items():
            if node.type == 'file':
                connection_count = len(node.imports) + len(self.relationship_graph.get(path, []))
                file_connections[path] = connection_count
        
        most_connected = sorted(file_connections.items(), key=lambda x: x[1], reverse=True)[:count]
        
        return [
            {
                'path': path,
                'name': os.path.basename(path),
                'connections': count,
                'language': self.file_nodes[path].language
            }
            for path, count in most_connected
        ]
    
    def save_structure_map(self, output_file: Optional[str] = None) -> str:
        """Save structure map to file."""
        if output_file is None:
            output_file = str(self.project_root / ".terminal_data" / "structure_map.json")
        
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            map_data = {
                'timestamp': datetime.now().isoformat(),
                'project_root': str(self.project_root),
                'structure_cache': self.structure_cache,
                'file_nodes': {path: asdict(node) for path, node in self.file_nodes.items()},
                'relationship_graph': {path: list(rels) for path, rels in self.relationship_graph.items()}
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(map_data, f, indent=2, default=str)
            
            return output_file
            
        except Exception as e:
            print(f"⚠ Could not save structure map: {e}")
            return ""

# Global mapper instance
_mapper_instance = None

def get_structure_mapper() -> FileStructureMapper:
    """Get the global structure mapper instance."""
    global _mapper_instance
    if _mapper_instance is None:
        _mapper_instance = FileStructureMapper()
    return _mapper_instance

if __name__ == "__main__":
    print("🗺️ Testing File Structure Mapper...")
    
    mapper = get_structure_mapper()
    
    # Scan project structure
    structure = mapper.scan_project_structure()
    
    print(f"\n📊 Project Structure:")
    print(f"  Files: {structure['total_files']}")
    print(f"  Directories: {structure['total_directories']}")
    print(f"  Languages: {', '.join(structure['languages'])}")
    print(f"  File types: {structure['file_types']}")
    
    # Get project overview
    overview = mapper.get_project_overview()
    
    print(f"\n🔍 Project Overview:")
    print(f"  Source files: {overview['source_files_count']}")
    print(f"  Config files: {overview['config_files_count']}")
    print(f"  Entry points: {overview['entry_points']}")
    print(f"  Top directories: {overview['top_level_directories']}")
    
    # Save structure map
    map_file = mapper.save_structure_map()
    if map_file:
        print(f"\n💾 Structure map saved to: {map_file}")
    
    print("\n✅ File Structure Mapper test completed!")