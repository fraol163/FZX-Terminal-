"""
Chat Transcript Manager for AI Terminal Workflow
Stores multi-message chats across editors, auto-summarizes, and builds token-aware prompts.
"""

import os
import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from context_manager import get_context_manager, ContextPriority, MemoryLayer


@dataclass
class ChatMessage:
    message_id: str
    role: str  # user|assistant|system
    content: str
    timestamp: float
    metadata: Dict[str, Any]


class ChatTranscriptManager:
    """Manages chat transcripts with JSONL storage and auto-summaries."""

    def __init__(self, project_root: Optional[str] = None, auto_summary_every: int = 5):
        self.project_root = Path(project_root or os.getcwd())
        self.messages_dir = self.project_root / ".terminal_data" / "messages"
        self.messages_dir.mkdir(parents=True, exist_ok=True)
        self.chat_file = self.messages_dir / "chat.jsonl"
        self.auto_summary_every = max(1, auto_summary_every)
        self._message_counter = 0

    def _estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        return max(1, max(len(text) // 4, len(text.split())))

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        message_id = f"m_{int(time.time()*1000)}"
        msg = ChatMessage(
            message_id=message_id,
            role=role,
            content=content,
            timestamp=time.time(),
            metadata=metadata or {},
        )

        with open(self.chat_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(msg), ensure_ascii=False) + "\n")

        self._message_counter += 1
        if self._message_counter % self.auto_summary_every == 0:
            try:
                self._auto_summarize_recent(self.auto_summary_every)
            except Exception:
                pass

        return message_id

    def _read_tail(self, max_lines: int) -> List[Dict[str, Any]]:
        messages: List[Dict[str, Any]] = []
        if not self.chat_file.exists():
            return messages
        # Efficient tail-read (simple fallback)
        try:
            with open(self.chat_file, "rb") as f:
                f.seek(0, os.SEEK_END)
                size = f.tell()
                block = 4096
                data = b""
                while size > 0 and len(messages) < max_lines:
                    read_size = min(block, size)
                    size -= read_size
                    f.seek(size)
                    data = f.read(read_size) + data
                    lines = data.split(b"\n")
                    messages = [json.loads(l.decode("utf-8")) for l in lines if l.strip()][:max_lines]
                    if len(messages) >= max_lines:
                        break
        except Exception:
            # Fallback: read all
            with open(self.chat_file, "r", encoding="utf-8") as f:
                lines = f.readlines()[-max_lines:]
                messages = [json.loads(l) for l in lines if l.strip()]
        return messages

    def get_recent_messages(self, limit: int = 20) -> List[Dict[str, Any]]:
        msgs = self._read_tail(limit)
        return msgs[-limit:]

    def build_chat_prompt(
        self,
        max_tokens: int = 2000,
        reserved_reply_tokens: int = 500,
        system_header: str = "",
        recent_limit: int = 30,
    ) -> Dict[str, Any]:
        budget = max(0, max_tokens - reserved_reply_tokens)
        header = system_header.strip()
        header_tokens = self._estimate_tokens(header) if header else 0
        remaining = max(0, budget - header_tokens)

        parts: List[str] = []
        if header:
            parts.append(header)

        recent = self.get_recent_messages(limit=recent_limit)
        # Oldest to newest
        recent = list(reversed(recent))

        included_ids: List[str] = []
        used_tokens = header_tokens
        for m in recent:
            prefix = "User:" if m.get("role") == "user" else "Assistant:" if m.get("role") == "assistant" else "System:"
            text = f"{prefix} {m.get('content','').strip()}"
            t = self._estimate_tokens(text)
            if t <= remaining:
                parts.append(text)
                included_ids.append(m.get("message_id", ""))
                used_tokens += t
                remaining -= t
            else:
                # Try a smaller form
                short = text[:400]
                t2 = self._estimate_tokens(short)
                if t2 <= remaining and t2 < t:
                    parts.append(short)
                    included_ids.append(f"{m.get('message_id','')}:trunc")
                    used_tokens += t2
                    remaining -= t2
                else:
                    break

        return {
            "prompt_text": "\n".join(parts),
            "included_ids": included_ids,
            "token_count": used_tokens,
            "truncated": remaining <= 0,
        }

    def _auto_summarize_recent(self, turns: int) -> None:
        recent = self.get_recent_messages(limit=turns)
        if not recent:
            return
        # Simple extractive summary: keep first/last user+assistant lines
        user_lines = [m for m in recent if m.get("role") == "user"]
        asst_lines = [m for m in recent if m.get("role") == "assistant"]
        pieces: List[str] = []
        if user_lines:
            pieces.append(f"User start: {user_lines[0]['content'][:200]}")
        if asst_lines:
            pieces.append(f"Assistant key: {asst_lines[-1]['content'][:200]}")
        pieces.append(f"Turns summarized: {len(recent)} at {datetime.now().isoformat()}")
        summary_text = "\n".join(pieces)

        cm = get_context_manager()
        cm.add_context(
            content=summary_text,
            context_type="chat_summary",
            priority=ContextPriority.HIGH,
            layer=MemoryLayer.SESSION,
            tags=["chat", "summary"],
        )
        cm.save_persistent_context()


_chat_manager_instance: Optional[ChatTranscriptManager] = None


def get_chat_manager() -> ChatTranscriptManager:
    global _chat_manager_instance
    if _chat_manager_instance is None:
        _chat_manager_instance = ChatTranscriptManager()
    return _chat_manager_instance


if __name__ == "__main__":
    mgr = get_chat_manager()
    mid = mgr.add_message("user", "Test message from user")
    mgr.add_message("assistant", "Reply message from assistant")
    prompt = mgr.build_chat_prompt(max_tokens=800, reserved_reply_tokens=200, system_header="You are helpful.")
    print("Built prompt tokens:", prompt["token_count"]) 

