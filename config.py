import os
from pathlib import Path

# ==================== LLM Configuration ====================
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
LLM_MODEL = os.getenv("LLM_MODEL", "phi4-mini")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# ==================== Data Paths ====================
DATA_DIR = "data"
TRAINING_DATA_FILE = f"{DATA_DIR}/training_data.json"
CONVERSATIONS_FILE = f"{DATA_DIR}/conversations.json"
MEMORY_FILE = f"{DATA_DIR}/long_term_memory.json"
ANALYTICS_FILE = f"{DATA_DIR}/analytics.json"
VECTOR_STORE_DIR = f"{DATA_DIR}/vector_store"

# ==================== Bot Settings ====================
SIMILARITY_THRESHOLD = 0.7
MAX_RESULTS = 3
MAX_CONVERSATION_TURNS = 10

# ==================== Security Settings ====================
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "10000"))

ALLOWED_EXTENSIONS = {
    ".txt", ".md", ".json", ".yaml", ".yml", ".xml", ".csv",
    ".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".hpp",
    ".go", ".rs", ".swift", ".kt", ".rb", ".php", ".html",
    ".css", ".scss", ".sql", ".sh", ".bash", ".zsh",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".mp3", ".mp4",
    ".zip", ".tar", ".gz", ".rar", ".env", ".gitignore",
    "README", "LICENSE", "Makefile", "Dockerfile", ".dockerignore"
}

BLOCKED_PATHS = {
    "/System", "/Library/Caches", "/private",
    "/Applications/.Trashes", "/Users/vyakaranamsowmya/.Trash",
    "/etc", "/usr/bin", "/usr/sbin", "/bin", "/sbin"
}

# ==================== Server Settings ====================
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# ==================== Language Support ====================
SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "code": "en"},
    "hi": {"name": "Hindi", "code": "hi"},
    "te": {"name": "Telugu", "code": "te"},
    "ta": {"name": "Tamil", "code": "ta"},
    "ml": {"name": "Malayalam", "code": "ml"}
}

# ==================== Personalities ====================
PERSONALITIES = {
    "default": {
        "name": "Your Style",
        "description": "Replies exactly like you",
        "system_prompt": "You are a personal assistant who responds exactly like the user would."
    },
    "friendly": {
        "name": "Friendly Buddy",
        "description": "Warm, casual and enthusiastic",
        "system_prompt": "You are a friendly, warm, and enthusiastic buddy. Use emojis occasionally. Keep responses casual and fun!"
    },
    "professional": {
        "name": "Professional",
        "description": "Clean, formal and concise",
        "system_prompt": "You are a professional assistant. Keep responses concise, clear, and formal."
    },
    "sarcastic": {
        "name": "Sarcastic",
        "description": "Witty with some sarcasm",
        "system_prompt": "You are witty and clever. Use light sarcasm occasionally. Keep it fun!"
    },
    "motivational": {
        "name": "Motivational Coach",
        "description": "Encouraging and inspiring",
        "system_prompt": "You are a motivational coach. Always encourage, inspire, and lift others up. Be positive and empowering!"
    }
}

# ==================== Mood Detection ====================
MOODS = {
    "happy": ["😊", "😄", "🎉", "awesome", "great", "love"],
    "sad": ["😢", "💔", "upset", "miss", "lonely", "sad"],
    "angry": ["😠", "🤬", "mad", "annoyed", "frustrated"],
    "excited": ["🎉", "🚀", "can't wait", "excited", "amazing"],
    "tired": ["😴", "exhausted", "sleepy", "tired", "drained"],
    "neutral": ["okay", "fine", "alright", "normal"]
}

FALLBACK_RESPONSES = [
    "I'm not sure how to respond to that.",
    "Could you rephrase that?",
    "I need more examples to learn from.",
]

# ==================== Webhook Integrations ====================
WEBHOOK_CONFIG = {
    "telegram": {
        "enabled": os.getenv("TELEGRAM_ENABLED", "false"),
        "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "chat_id": os.getenv("TELEGRAM_CHAT_ID", "")
    },
    "discord": {
        "enabled": os.getenv("DISCORD_ENABLED", "false"),
        "webhook_url": os.getenv("DISCORD_WEBHOOK_URL", "")
    }
}
