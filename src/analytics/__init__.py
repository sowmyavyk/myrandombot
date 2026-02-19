import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from pathlib import Path
from collections import defaultdict

import config


class Analytics:
    def __init__(self):
        self.data = {
            "total_messages": 0,
            "conversations": 0,
            "messages_by_user": defaultdict(int),
            "messages_by_mood": defaultdict(int),
            "messages_by_language": defaultdict(int),
            "daily_stats": defaultdict(int),
            "corrections": [],
            "feedback": []
        }
        self._load()

    def _load(self):
        path = Path(config.ANALYTICS_FILE)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                loaded["messages_by_user"] = defaultdict(int, loaded.get("messages_by_user", {}))
                loaded["messages_by_mood"] = defaultdict(int, loaded.get("messages_by_mood", {}))
                loaded["messages_by_language"] = defaultdict(int, loaded.get("messages_by_language", {}))
                loaded["daily_stats"] = defaultdict(int, loaded.get("daily_stats", {}))
                self.data = loaded

    def _save(self):
        path = Path(config.ANALYTICS_FILE)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        data_to_save = {
            "total_messages": self.data["total_messages"],
            "conversations": self.data["conversations"],
            "messages_by_user": dict(self.data["messages_by_user"]),
            "messages_by_mood": dict(self.data["messages_by_mood"]),
            "messages_by_language": dict(self.data["messages_by_language"]),
            "daily_stats": dict(self.data["daily_stats"]),
            "corrections": self.data["corrections"][-100:],
            "feedback": self.data["feedback"][-100:]
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)

    def track_message(self, user_id: str, mood: str = None, language: str = None):
        self.data["total_messages"] += 1
        self.data["messages_by_user"][user_id] += 1
        
        today = datetime.now().strftime("%Y-%m-%d")
        self.data["daily_stats"][today] += 1
        
        if mood:
            self.data["messages_by_mood"][mood] += 1
        if language:
            self.data["messages_by_language"][language] += 1
        
        self._save()

    def track_correction(self, user_id: str, original_reply: str, corrected_reply: str):
        self.data["corrections"].append({
            "user_id": user_id,
            "original": original_reply,
            "corrected": corrected_reply,
            "timestamp": datetime.now().isoformat()
        })
        self._save()

    def track_feedback(self, user_id: str, reply: str, feedback_type: str):
        self.data["feedback"].append({
            "user_id": user_id,
            "reply": reply,
            "type": feedback_type,
            "timestamp": datetime.now().isoformat()
        })
        self._save()

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_messages": self.data["total_messages"],
            "unique_users": len(self.data["messages_by_user"]),
            "top_moods": dict(sorted(
                self.data["messages_by_mood"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]),
            "top_languages": dict(sorted(
                self.data["messages_by_language"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]),
            "recent_corrections_count": len(self.data["corrections"]),
        }

    def get_daily_stats(self, days: int = 7) -> Dict[str, int]:
        result = {}
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            result[date] = self.data["daily_stats"].get(date, 0)
        return result


class LearningSystem:
    def __init__(self):
        self.pending_corrections: List[Dict[str, Any]] = []

    def add_correction(self, user_id: str, query: str, 
                       original_reply: str, corrected_reply: str):
        correction = {
            "user_id": user_id,
            "query": query,
            "original": original_reply,
            "corrected": corrected_reply,
            "timestamp": datetime.now().isoformat()
        }
        self.pending_corrections.append(correction)
        
        from src.chain import load_training_data, save_training_data, TrainingExample
        examples = load_training_data()
        
        examples.append(TrainingExample(
            input=query,
            reply=corrected_reply,
            language="en"
        ))
        
        save_training_data(examples)
        
        return "Thanks! I've learned from your correction."

    def get_pending_corrections(self) -> List[Dict[str, Any]]:
        return self.pending_corrections[-10:]
