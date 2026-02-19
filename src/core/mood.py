import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

import config


@dataclass
class MoodResult:
    mood: str
    confidence: float
    intensity: float


class MoodDetector:
    def __init__(self):
        self.mood_keywords = config.MOODS
        self.emoji_pattern = re.compile(
            "[" 
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "]+", 
            flags=re.UNICODE
        )
        
        self.mood_emoji_map = {
            "😊": "happy", "😄": "happy", "🎉": "happy", "❤️": "happy",
            "😢": "sad", "💔": "sad", "😭": "sad", "😞": "sad",
            "😠": "angry", "🤬": "angry", "😤": "angry",
            "🚀": "excited", "🎊": "excited", "⭐": "excited",
            "😴": "tired", "💤": "tired", "🥱": "tired",
        }

    def detect(self, text: str) -> MoodResult:
        text_lower = text.lower()
        
        emojis = self.emoji_pattern.findall(text)
        for emoji in emojis:
            for char in emoji:
                if char in self.mood_emoji_map:
                    return MoodResult(
                        mood=self.mood_emoji_map[char],
                        confidence=0.9,
                        intensity=1.0
                    )
        
        mood_scores = {mood: 0 for mood in self.mood_keywords}
        
        for mood, keywords in self.mood_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    mood_scores[mood] += 1
        
        if max(mood_scores.values()) == 0:
            return MoodResult(mood="neutral", confidence=0.5, intensity=0.3)
        
        detected_mood = max(mood_scores, key=mood_scores.get)
        max_score = mood_scores[detected_mood]
        confidence = min(0.95, 0.5 + (max_score * 0.15))
        
        return MoodResult(
            mood=detected_mood,
            confidence=confidence,
            intensity=min(1.0, max_score / 3)
        )

    def get_response_modifier(self, mood: MoodResult) -> str:
        if mood.mood == "happy":
            return "Match the user's happy energy!"
        elif mood.mood == "sad":
            return "Be gentle and supportive. The user might need comfort."
        elif mood.mood == "angry":
            return "Stay calm and understanding. Don't take it personally."
        elif mood.mood == "excited":
            return "Match the excitement! Be energetic!"
        elif mood.mood == "tired":
            return "Be understanding and keep responses brief."
        else:
            return ""


class LanguageDetector:
    def __init__(self):
        self.language_patterns = {
            "hi": re.compile(r'[\u0900-\u097F]'),
            "te": re.compile(r'[\u0C00-\u0C7F]'),
            "ta": re.compile(r'[\u0B80-\u0BFF]'),
            "ml": re.compile(r'[\u0D00-\u0D7F]'),
        }

    def detect(self, text: str) -> str:
        for lang_code, pattern in self.language_patterns.items():
            if pattern.search(text):
                return lang_code
        return "en"

    def get_language_name(self, code: str) -> str:
        return config.SUPPORTED_LANGUAGES.get(code, {}).get("name", "English")


class PersonalityManager:
    def __init__(self):
        self.personalities = config.PERSONALITIES
        self.current_personality = "default"

    def set_personality(self, personality_key: str):
        if personality_key in self.personalities:
            self.current_personality = personality_key
            return True
        return False

    def get_personality(self) -> Dict[str, Any]:
        return self.personalities[self.current_personality]

    def get_system_prompt(self) -> str:
        return self.get_personality()["system_prompt"]

    def list_personalities(self) -> List[Dict[str, str]]:
        return [
            {"key": key, "name": val["name"], "description": val["description"]}
            for key, val in self.personalities.items()
        ]
