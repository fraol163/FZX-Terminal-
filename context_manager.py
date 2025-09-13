"""
Context Manager for AI Terminal Workflow
Intelligent memory optimization and context preservation

Provides:
- Context compression and optimization
- Memory layer management
- Token usage optimization
- Intelligent context switching
- Pattern recognition and learning
"""

import os
import sys
import json
import time
import hashlib
import pickle
import gzip
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from datetime import datetime, timedelta
from collections import defaultdict, deque
import re
from dataclasses import dataclass, asdict
from enum import Enum

class ContextPriority(Enum):
    """Context priority levels for memory management."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    ARCHIVE = 5

class MemoryLayer(Enum):
    """Memory layer types."""
    IMMEDIATE = "immediate"
    SESSION = "session"
    LONG_TERM = "long_term"
    COMPRESSED = "compressed"

@dataclass
class ContextItem:
    """Individual context item with metadata."""
    content: str
    priority: ContextPriority
    layer: MemoryLayer
    timestamp: float
    access_count: int = 0
    last_accessed: float = 0
    size_bytes: int = 0
    context_type: str = "general"
    tags: List[str] = None
    relationships: List[str] = None
    compression_ratio: float = 1.0
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.relationships is None:
            self.relationships = []
        if self.size_bytes == 0:
            self.size_bytes = len(self.content.encode('utf-8'))
        if self.last_accessed == 0:
            self.last_accessed = self.timestamp

class ContextCompressor:
    """Handles context compression and optimization."""
    
    def __init__(self):
        self.compression_patterns = {
            'code_blocks': r'```[\s\S]*?```',
            'file_paths': r'[a-zA-Z]:\\[\\\w\s.-]+|/[/\w\s.-]+',
            'imports': r'(?:import|from)\s+[\w.]+(?:\s+import\s+[\w,\s]+)?',
            'function_defs': r'def\s+\w+\([^)]*\):',
            'class_defs': r'class\s+\w+(?:\([^)]*\))?:',
            'comments': r'#.*$|//.*$|/\*[\s\S]*?\*/',
            'whitespace': r'\s+',
            'repeated_patterns': r'(\b\w+\b)(?:\s+\1){2,}'
        }
        
    def compress_context(self, content: str, target_ratio: float = 0.7) -> Tuple[str, float]:
        """Compress context while preserving meaning."""
        original_size = len(content)
        compressed = content
        
        compressed = re.sub(r'\n\s*\n\s*\n', '\n\n', compressed)
        compressed = re.sub(r'[ \t]+', ' ', compressed)
        
        for pattern_name, pattern in self.compression_patterns.items():
            if pattern_name == 'repeated_patterns':
                compressed = re.sub(pattern, r'\1 (repeated)', compressed)
            elif pattern_name == 'whitespace':
                continue
            
        current_ratio = len(compressed) / original_size
        if current_ratio > target_ratio:
            compressed = self._summarize_code_blocks(compressed)
            
        current_ratio = len(compressed) / original_size
        if current_ratio > target_ratio:
            compressed = self._extract_key_information(compressed)
            
        final_ratio = len(compressed) / original_size
        return compressed, final_ratio
        
    def _summarize_code_blocks(self, content: str) -> str:
        """Summarize large code blocks."""
        def replace_code_block(match):
            code_block = match.group(0)
            lines = code_block.split('\n')
            
            if len(lines) <= 10:
                return code_block
                
            language = lines[0].replace('```', '').strip()
            key_lines = []
            
            for line in lines[1:-1]:
                if any(keyword in line.lower() for keyword in 
                      ['def ', 'class ', 'import ', 'from ', 'return ', 'if ', 'for ', 'while ']):
                    key_lines.append(line.strip())
                    
            if len(key_lines) > 5:
                key_lines = key_lines[:3] + ['...'] + key_lines[-2:]
                
            return f"```{language}\n" + '\n'.join(key_lines) + f"\n# ... ({len(lines)-2} total lines)\n```"
            
        return re.sub(r'```[\s\S]*?```', replace_code_block, content)
        
    def _extract_key_information(self, content: str) -> str:
        """Extract key information from content."""
        lines = content.split('\n')
        key_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if any(keyword in line.lower() for keyword in [
                'error', 'warning', 'failed', 'success', 'completed',
                'def ', 'class ', 'import ', 'from ', 'return ',
                'todo', 'fixme', 'bug', 'note', 'important'
            ]):
                key_lines.append(line)
            elif len(line) > 100:
                key_lines.append(line[:97] + '...')
                
        if len(key_lines) > 50:
            key_lines = key_lines[:25] + ['...'] + key_lines[-25:]
            
        return '\n'.join(key_lines)
        
    def decompress_context(self, compressed_content: str, metadata: Dict[str, Any]) -> str:
        """Attempt to decompress context (limited reconstruction)."""
        return compressed_content

class PatternRecognizer:
    """Recognizes patterns in user interactions and context."""
    
    def __init__(self):
        self.patterns = {
            'file_operations': defaultdict(int),
            'command_sequences': defaultdict(int),
            'error_patterns': defaultdict(int),
            'workflow_patterns': defaultdict(int),
            'time_patterns': defaultdict(list)
        }
        
    def analyze_context(self, context_item: ContextItem) -> Dict[str, Any]:
        """Analyze context item for patterns."""
        analysis = {
            'detected_patterns': [],
            'suggested_tags': [],
            'priority_adjustment': 0,
            'relationships': []
        }
        
        content = context_item.content.lower()
        
        file_ops = ['create', 'edit', 'delete', 'move', 'copy', 'read', 'write']
        for op in file_ops:
            if op in content:
                self.patterns['file_operations'][op] += 1
                analysis['detected_patterns'].append(f'file_operation_{op}')
                
        error_indicators = ['error', 'failed', 'exception', 'traceback', 'bug']
        for indicator in error_indicators:
            if indicator in content:
                self.patterns['error_patterns'][indicator] += 1
                analysis['detected_patterns'].append(f'error_{indicator}')
                analysis['priority_adjustment'] += 1
                
        code_indicators = ['def ', 'class ', 'import ', 'function', 'method']
        for indicator in code_indicators:
            if indicator in content:
                analysis['suggested_tags'].append('code')
                break
                
        hour = datetime.fromtimestamp(context_item.timestamp).hour
        self.patterns['time_patterns'][hour].append(context_item.context_type)
        
        return analysis
        
    def get_pattern_insights(self) -> Dict[str, Any]:
        """Get insights from recognized patterns."""
        insights = {
            'most_common_operations': [],
            'peak_activity_hours': [],
            'common_error_types': [],
            'workflow_recommendations': []
        }
        
        if self.patterns['file_operations']:
            sorted_ops = sorted(self.patterns['file_operations'].items(), 
                              key=lambda x: x[1], reverse=True)
            insights['most_common_operations'] = sorted_ops[:5]
            
        hour_activity = {}
        for hour, activities in self.patterns['time_patterns'].items():
            hour_activity[hour] = len(activities)
            
        if hour_activity:
            sorted_hours = sorted(hour_activity.items(), key=lambda x: x[1], reverse=True)
            insights['peak_activity_hours'] = sorted_hours[:3]
            
        if self.patterns['error_patterns']:
            sorted_errors = sorted(self.patterns['error_patterns'].items(),
                                 key=lambda x: x[1], reverse=True)
            insights['common_error_types'] = sorted_errors[:5]
            
        return insights

class MemoryOptimizer:
    """Optimizes memory usage and context switching."""
    
    def __init__(self, max_memory_mb: int = 100):
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.current_memory_usage = 0
        self.access_history = deque(maxlen=1000)
        
    def calculate_context_score(self, context_item: ContextItem) -> float:
        """Calculate relevance score for context item."""
        score = 0.0
        
        time_diff = time.time() - context_item.last_accessed
        recency_score = max(0, 1 - (time_diff / (24 * 3600)))
        score += recency_score * 0.3
        
        frequency_score = min(1.0, context_item.access_count / 10)
        score += frequency_score * 0.2
        
        priority_score = (6 - context_item.priority.value) / 5
        score += priority_score * 0.3
        
        size_score = max(0, 1 - (context_item.size_bytes / (10 * 1024)))
        score += size_score * 0.1
        
        type_bonuses = {
            'error': 0.2,
            'code': 0.15,
            'task': 0.1,
            'user_input': 0.1
        }
        score += type_bonuses.get(context_item.context_type, 0)
        
        return min(1.0, score)
        
    def optimize_memory(self, context_items: List[ContextItem]) -> List[ContextItem]:
        """Optimize memory by selecting most relevant context items."""
        scored_items = []
        for item in context_items:
            score = self.calculate_context_score(item)
            scored_items.append((score, item))
            
        scored_items.sort(key=lambda x: x[0], reverse=True)
        
        selected_items = []
        current_size = 0
        
        for score, item in scored_items:
            if current_size + item.size_bytes <= self.max_memory_bytes:
                selected_items.append(item)
                current_size += item.size_bytes
            elif item.priority == ContextPriority.CRITICAL:
                selected_items.append(item)
                current_size += item.size_bytes
                
        self.current_memory_usage = current_size
        return selected_items
        
    def suggest_compression_targets(self, context_items: List[ContextItem]) -> List[ContextItem]:
        """Suggest items that should be compressed."""
        compression_candidates = []
        
        for item in context_items:
            if (item.size_bytes > 5000 and 
                item.access_count < 3 and 
                item.priority.value >= 3):
                compression_candidates.append(item)
                
        return compression_candidates

class ContextManager:
    """Main context manager coordinating all context operations."""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.context_storage = {
            MemoryLayer.IMMEDIATE: {},
            MemoryLayer.SESSION: {},
            MemoryLayer.LONG_TERM: {},
            MemoryLayer.COMPRESSED: {}
        }
        
        self.compressor = ContextCompressor()
        self.pattern_recognizer = PatternRecognizer()
        self.memory_optimizer = MemoryOptimizer()
        
        self.context_index = {}
        self.relationship_graph = defaultdict(set)
        
        self._load_persistent_context()
        
        # Initialize data directories used for long-term memory/export
        try:
            data_root = self.project_root / ".terminal_data"
            (data_root / "memory").mkdir(parents=True, exist_ok=True)
            (data_root / "exports").mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    def add_context(self, content: str, context_type: str = "general", 
                   priority: ContextPriority = ContextPriority.MEDIUM,
                   layer: MemoryLayer = MemoryLayer.IMMEDIATE,
                   tags: List[str] = None) -> str:
        """Add new context item."""
        
        context_item = ContextItem(
            content=content,
            priority=priority,
            layer=layer,
            timestamp=time.time(),
            context_type=context_type,
            tags=tags or []
        )
        
        analysis = self.pattern_recognizer.analyze_context(context_item)
        
        if analysis['priority_adjustment'] > 0:
            new_priority_value = max(1, context_item.priority.value - analysis['priority_adjustment'])
            context_item.priority = ContextPriority(new_priority_value)
            
        context_item.tags.extend(analysis['suggested_tags'])
        
        context_id = hashlib.md5(
            f"{content[:100]}{context_item.timestamp}".encode()
        ).hexdigest()[:12]
        
        self.context_storage[layer][context_id] = context_item
        self.context_index[context_id] = (layer, context_item)
        
        for related_id in analysis['relationships']:
            self.relationship_graph[context_id].add(related_id)
            self.relationship_graph[related_id].add(context_id)
            
        self._check_memory_optimization()
        
        return context_id
        
    def get_context(self, context_id: str) -> Optional[ContextItem]:
        """Retrieve context item by ID."""
        if context_id in self.context_index:
            layer, context_item = self.context_index[context_id]
            
            context_item.access_count += 1
            context_item.last_accessed = time.time()
            
            return context_item
            
        return None
        
    def search_context(self, query: str, max_results: int = 10) -> List[Tuple[str, ContextItem, float]]:
        """Search context items by content similarity."""
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        for context_id, (layer, context_item) in self.context_index.items():
            content_lower = context_item.content.lower()
            content_words = set(content_lower.split())
            
            similarity = 0.0
            
            if query_lower in content_lower:
                similarity += 0.5
                
            common_words = query_words.intersection(content_words)
            if query_words:
                word_similarity = len(common_words) / len(query_words)
                similarity += word_similarity * 0.3
                
            query_tags = set(query_lower.split())
            tag_match = query_tags.intersection(set(tag.lower() for tag in context_item.tags))
            if tag_match:
                similarity += 0.2
                
            if similarity > 0.1:
                results.append((context_id, context_item, similarity))
                
        results.sort(key=lambda x: x[2], reverse=True)
        return results[:max_results]
        
    def get_related_context(self, context_id: str, max_depth: int = 2) -> List[str]:
        """Get related context items using relationship graph."""
        related = set()
        to_explore = {context_id}
        explored = set()
        
        for depth in range(max_depth):
            next_to_explore = set()
            
            for current_id in to_explore:
                if current_id in explored:
                    continue
                    
                explored.add(current_id)
                related_ids = self.relationship_graph.get(current_id, set())
                related.update(related_ids)
                next_to_explore.update(related_ids)
                
            to_explore = next_to_explore - explored
            
        return list(related - {context_id})
        
    def compress_context_layer(self, layer: MemoryLayer, target_ratio: float = 0.7) -> Dict[str, Any]:
        """Compress all context items in a specific layer."""
        compression_results = {
            "compressed_items": 0,
            "original_size": 0,
            "compressed_size": 0,
            "compression_ratio": 0,
            "errors": []
        }
        
        layer_items = self.context_storage[layer]
        
        for context_id, context_item in layer_items.items():
            try:
                original_size = len(context_item.content)
                compressed_content, ratio = self.compressor.compress_context(
                    context_item.content, target_ratio
                )
                
                context_item.content = compressed_content
                context_item.compression_ratio = ratio
                context_item.size_bytes = len(compressed_content.encode('utf-8'))
                
                compression_results["compressed_items"] += 1
                compression_results["original_size"] += original_size
                compression_results["compressed_size"] += len(compressed_content)
                
            except Exception as e:
                compression_results["errors"].append(f"Error compressing {context_id}: {str(e)}")
                
        if compression_results["original_size"] > 0:
            compression_results["compression_ratio"] = (
                compression_results["compressed_size"] / compression_results["original_size"]
            )
            
        return compression_results
        
    def optimize_memory_usage(self) -> Dict[str, Any]:
        """Optimize overall memory usage."""
        optimization_results = {
            "before_optimization": {},
            "after_optimization": {},
            "actions_taken": [],
            "memory_saved": 0
        }
        
        all_items = []
        for layer_items in self.context_storage.values():
            all_items.extend(layer_items.values())
            
        total_size_before = sum(item.size_bytes for item in all_items)
        optimization_results["before_optimization"] = {
            "total_items": len(all_items),
            "total_size_bytes": total_size_before,
            "memory_usage_mb": total_size_before / (1024 * 1024)
        }
        
        optimized_items = self.memory_optimizer.optimize_memory(all_items)
        
        compression_targets = self.memory_optimizer.suggest_compression_targets(optimized_items)
        
        for item in compression_targets:
            try:
                compressed_content, ratio = self.compressor.compress_context(item.content)
                item.content = compressed_content
                item.compression_ratio = ratio
                item.size_bytes = len(compressed_content.encode('utf-8'))
                optimization_results["actions_taken"].append(f"Compressed item (ratio: {ratio:.2f})")
            except Exception as e:
                optimization_results["actions_taken"].append(f"Compression failed: {str(e)}")
                
        total_size_after = sum(item.size_bytes for item in optimized_items)
        optimization_results["after_optimization"] = {
            "total_items": len(optimized_items),
            "total_size_bytes": total_size_after,
            "memory_usage_mb": total_size_after / (1024 * 1024)
        }
        
        optimization_results["memory_saved"] = total_size_before - total_size_after
        
        return optimization_results
        
    def get_context_summary(self) -> Dict[str, Any]:
        """Get comprehensive context summary."""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "layers": {},
            "total_items": 0,
            "total_size_bytes": 0,
            "memory_usage_mb": 0,
            "pattern_insights": self.pattern_recognizer.get_pattern_insights(),
            "optimization_suggestions": []
        }
        
        for layer, layer_items in self.context_storage.items():
            layer_size = sum(item.size_bytes for item in layer_items.values())
            summary["layers"][layer.value] = {
                "item_count": len(layer_items),
                "size_bytes": layer_size,
                "avg_item_size": layer_size / len(layer_items) if layer_items else 0
            }
            
            summary["total_items"] += len(layer_items)
            summary["total_size_bytes"] += layer_size
            
        summary["memory_usage_mb"] = summary["total_size_bytes"] / (1024 * 1024)
        
        if summary["memory_usage_mb"] > 50:
            summary["optimization_suggestions"].append("Consider running memory optimization")
            
        if summary["layers"].get("immediate", {}).get("item_count", 0) > 100:
            summary["optimization_suggestions"].append("Move old immediate context to session layer")
            
        return summary
        
    def _check_memory_optimization(self) -> None:
        """Check if memory optimization is needed."""
        total_size = sum(
            sum(item.size_bytes for item in layer_items.values())
            for layer_items in self.context_storage.values()
        )
        
        if total_size > 80 * 1024 * 1024:
            self.optimize_memory_usage()
            
    # --- Token-aware prompt building and durable memory export ---
    def _estimate_token_count(self, text: str) -> int:
        """Rough token estimate (~4 chars/token fallback)."""
        if not text:
            return 0
        # Heuristic: 1 token per 4 characters, clamp to at least number of words
        char_tokens = max(1, len(text) // 4)
        word_tokens = max(1, len(text.split()))
        return max(char_tokens, word_tokens)

    def build_prompt(self, max_tokens: int = 2000, system_header: str = "", reserved_reply_tokens: int = 500) -> Dict[str, Any]:
        """Assemble the most relevant context into a prompt within a token budget.

        Returns a dict with: prompt_text, included_ids, token_count, truncated.
        """
        budget = max(0, max_tokens - reserved_reply_tokens)
        header = system_header.strip()
        header_tokens = self._estimate_token_count(header) if header else 0
        remaining = max(0, budget - header_tokens)

        # Rank items using existing optimizer
        all_items = [
            item
            for layer_items in self.context_storage.values()
            for item in layer_items.values()
        ]
        ranked = sorted(
            all_items,
            key=lambda it: self.memory_optimizer.calculate_context_score(it),
            reverse=True,
        )

        included_ids: List[str] = []
        parts: List[str] = []
        total_tokens = header_tokens
        if header:
            parts.append(header)

        for context_id, (layer, item) in self.context_index.items():
            pass

        # Iterate ranked items and stop when budget exceeded
        for item in ranked:
            content = item.content.strip()
            tokens = self._estimate_token_count(content)
            if tokens <= remaining:
                parts.append(content)
                remaining -= tokens
                total_tokens += tokens
                # Find id back from index (reverse lookup by object ref)
                for cid, (_layer, ref) in self.context_index.items():
                    if ref is item:
                        included_ids.append(cid)
                        break
            else:
                # Try compressed summary of this item
                summary, ratio = self.compressor.compress_context(content, target_ratio=0.3)
                summary_tokens = self._estimate_token_count(summary)
                if summary_tokens <= remaining and summary_tokens < tokens:
                    parts.append(summary)
                    remaining -= summary_tokens
                    total_tokens += summary_tokens
                    for cid, (_layer, ref) in self.context_index.items():
                        if ref is item:
                            included_ids.append(f"{cid}:compressed")
                            break
                # else skip

            if remaining <= 0:
                break

        prompt_text = "\n\n".join(parts)
        return {
            "prompt_text": prompt_text,
            "included_ids": included_ids,
            "token_count": total_tokens,
            "truncated": remaining <= 0,
        }

    def export_universal_memory(self, export_path: Optional[str] = None) -> str:
        """Export memory as JSONL for any AI editor to ingest.

        Each line: {id, layer, priority, context_type, timestamp, access_count, tags, relationships, content}
        """
        data_root = self.project_root / ".terminal_data" / "exports"
        data_root.mkdir(parents=True, exist_ok=True)
        if export_path is None:
            export_path = str(data_root / "memory_universal.jsonl")

        try:
            with open(export_path, "w", encoding="utf-8") as f:
                for cid, (layer, item) in self.context_index.items():
                    record = {
                        "id": cid,
                        "layer": layer.value,
                        "priority": item.priority.name,
                        "context_type": item.context_type,
                        "timestamp": item.timestamp,
                        "access_count": item.access_count,
                        "tags": item.tags,
                        "relationships": list(self.relationship_graph.get(cid, [])),
                        "content": item.content,
                    }
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            raise e

        return export_path

    def snapshot_long_term_memory(self) -> str:
        """Append a daily snapshot of long-term memory to .terminal_data/memory/YYYY-MM-DD.jsonl."""
        date_key = datetime.now().strftime("%Y-%m-%d")
        mem_dir = self.project_root / ".terminal_data" / "memory"
        mem_dir.mkdir(parents=True, exist_ok=True)
        snapshot_path = mem_dir / f"{date_key}.jsonl"

        with open(snapshot_path, "a", encoding="utf-8") as f:
            for cid, (layer, item) in self.context_index.items():
                if layer in (MemoryLayer.LONG_TERM, MemoryLayer.SESSION):
                    record = {
                        "id": cid,
                        "layer": layer.value,
                        "priority": item.priority.name,
                        "context_type": item.context_type,
                        "timestamp": item.timestamp,
                        "access_count": item.access_count,
                        "tags": item.tags,
                        "content": item.content,
                    }
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")

        return str(snapshot_path)

    def _load_persistent_context(self) -> None:
        """Load persistent context from disk."""
        context_file = self.project_root / "context_memory.json"
        
        if context_file.exists():
            try:
                with open(context_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for layer_name, layer_data in data.get("context_storage", {}).items():
                    layer = MemoryLayer(layer_name)
                    for context_id, item_data in layer_data.items():
                        context_item = ContextItem(**item_data)
                        self.context_storage[layer][context_id] = context_item
                        self.context_index[context_id] = (layer, context_item)
                        
                self.relationship_graph.update(data.get("relationships", {}))
                
            except Exception as e:
                print(f"⚠ Failed to load persistent context: {e}")
                
    def save_persistent_context(self) -> bool:
        """Save persistent context to disk."""
        context_file = self.project_root / "context_memory.json"
        
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "context_storage": {},
                "relationships": dict(self.relationship_graph)
            }
            
            for layer, layer_items in self.context_storage.items():
                data["context_storage"][layer.value] = {}
                for context_id, context_item in layer_items.items():
                    data["context_storage"][layer.value][context_id] = asdict(context_item)
                    
            with open(context_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            # Side effects for durable memory: export and daily snapshot
            try:
                self.export_universal_memory()
                self.snapshot_long_term_memory()
            except Exception:
                pass
                
            return True
            
        except Exception as e:
            print(f"⚠ Failed to save persistent context: {e}")
            return False


# Global context manager instance
_context_manager_instance: Optional[ContextManager] = None


def get_context_manager() -> ContextManager:
    """Get or create the global context manager instance."""
    global _context_manager_instance
    if _context_manager_instance is None:
        _context_manager_instance = ContextManager()
    return _context_manager_instance


def reset_context_manager() -> None:
    """Reset the global context manager instance."""
    global _context_manager_instance
    _context_manager_instance = None


if __name__ == "__main__":
    # Test the context manager
    cm = get_context_manager()
    
    # Add some test context
    context_id = cm.add_context(
        content="This is a test context item for development.",
        context_type="test",
        priority=ContextPriority.HIGH,
        layer=MemoryLayer.SESSION,
        tags=["test", "development"]
    )
    
    print(f"Added context with ID: {context_id}")
    
    # Test search
    results = cm.search_context("test development")
    print(f"Search results: {len(results)} items found")
    
    # Test prompt building
    prompt_data = cm.build_prompt(max_tokens=1000, system_header="You are a helpful assistant.")
    print(f"Built prompt with {prompt_data['token_count']} tokens")
    
    # Test memory export
    export_path = cm.export_universal_memory()
    print(f"Exported memory to: {export_path}")
    
    # Test context summary
    summary = cm.get_context_summary()
    print(f"Context summary: {summary['total_items']} items, {summary['memory_usage_mb']:.2f} MB")
    
    # Save persistent context
    saved = cm.save_persistent_context()
    print(f"Context saved: {saved}")

_context_manager_instance = None

def get_context_manager() -> ContextManager:
    """Get the global context manager instance."""
    global _context_manager_instance
    if _context_manager_instance is None:
        _context_manager_instance = ContextManager()
    return _context_manager_instance

if __name__ == "__main__":
    cm = get_context_manager()
    
    print("🧠 Testing Context Manager...")
    
    context_id1 = cm.add_context(
        "This is a test context about file operations",
        context_type="test",
        priority=ContextPriority.HIGH,
        tags=["test", "file_ops"]
    )
    
    context_id2 = cm.add_context(
        "def test_function():\n    return 'Hello World'",
        context_type="code",
        priority=ContextPriority.MEDIUM,
        tags=["python", "function"]
    )
    
    search_results = cm.search_context("file operations")
    print(f"\n🔍 Search Results: {len(search_results)} items found")
    
    summary = cm.get_context_summary()
    print(f"\n📊 Context Summary:")
    print(f"  Total Items: {summary['total_items']}")
    print(f"  Memory Usage: {summary['memory_usage_mb']:.2f} MB")
    print(f"  Layers: {list(summary['layers'].keys())}")
    
    optimization_result = cm.optimize_memory_usage()
    print(f"\n⚡ Optimization Results:")
    print(f"  Actions Taken: {len(optimization_result['actions_taken'])}")
    print(f"  Memory Saved: {optimization_result['memory_saved']} bytes")
    
    print("\n✅ Context Manager test completed")