import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from collections import deque
from dataclasses import dataclass, asdict

import config


@dataclass
class Message:
    role: str
    content: str
    timestamp: str
    mood: Optional[str] = None
    language: Optional[str] = None


class ConversationMemory:
    def __init__(self, max_turns: int = None):
        self.max_turns = max_turns or config.MAX_CONVERSATION_TURNS
        self.conversations: Dict[str, deque] = {}
        self._load_conversations()

    def _load_conversations(self):
        path = Path(config.CONVERSATIONS_FILE)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for user_id, messages in data.items():
                    self.conversations[user_id] = deque(
                        [Message(**m) for m in messages],
                        maxlen=self.max_turns
                    )

    def _save_conversations(self):
        data = {
            user_id: [asdict(msg) for msg in msgs]
            for user_id, msgs in self.conversations.items()
        }
        path = Path(config.CONVERSATIONS_FILE)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_message(self, user_id: str, role: str, content: str, 
                    mood: str = None, language: str = None):
        if user_id not in self.conversations:
            self.conversations[user_id] = deque(maxlen=self.max_turns)
        
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            mood=mood,
            language=language
        )
        self.conversations[user_id].append(message)
        self._save_conversations()

    def get_context(self, user_id: str) -> List[Message]:
        return list(self.conversations.get(user_id, []))

    def get_formatted_context(self, user_id: str) -> str:
        messages = self.get_context(user_id)
        if not messages:
            return ""
        
        context_parts = []
        for msg in messages:
            role = "User" if msg.role == "user" else "Bot"
            context_parts.append(f"{role}: {msg.content}")
        
        return "\n".join(context_parts)

    def clear_conversation(self, user_id: str):
        if user_id in self.conversations:
            self.conversations[user_id].clear()
            self._save_conversations()

    def get_conversation_summary(self, user_id: str) -> str:
        messages = self.get_context(user_id)
        if not messages:
            return "No conversation history."
        
        return f"Recent conversation ({len(messages)} turns):\n{self.get_formatted_context(user_id)}"


class LongTermMemory:
    def __init__(self):
        self.facts: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        path = Path(config.MEMORY_FILE)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                self.facts = json.load(f)

    def _save(self):
        path = Path(config.MEMORY_FILE)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.facts, f, indent=2, ensure_ascii=False)

    def add_fact(self, user_id: str, fact: str, category: str = "general"):
        self.facts.append({
            "user_id": user_id,
            "fact": fact,
            "category": category,
            "timestamp": datetime.now().isoformat()
        })
        self._save()

    def get_facts(self, user_id: str) -> List[str]:
        user_facts = [f["fact"] for f in self.facts if f["user_id"] == user_id]
        return user_facts[-10:]

    def get_formatted_memory(self, user_id: str) -> str:
        facts = self.get_facts(user_id)
        if not facts:
            return ""
        return "Things I remember about you: " + "; ".join(facts)
