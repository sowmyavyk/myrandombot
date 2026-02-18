import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

DATA_DIR = "data"
TRAINING_DATA_FILE = f"{DATA_DIR}/training_data.json"
VECTOR_STORE_DIR = f"{DATA_DIR}/vector_store"

SIMILARITY_THRESHOLD = 0.7
MAX_RESULTS = 3

SUPPORTED_LANGUAGES = ["en", "hi", "te", "ta", "ml"]

FALLBACK_RESPONSES = [
    "I'm not sure how to respond to that.",
    "Could you rephrase that?",
    "I need more examples to learn from.",
]
