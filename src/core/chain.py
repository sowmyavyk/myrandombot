import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

import config

if config.LLM_PROVIDER == "ollama":
    from langchain_community.chat_models import ChatOllama
    from langchain_ollama import OllamaEmbeddings
else:
    from langchain_openai import OpenAIEmbeddings
    from langchain_openai import ChatOpenAI

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate


class TrainingExample(BaseModel):
    input: str
    reply: str
    language: Optional[str] = "en"


class VectorStoreManager:
    def __init__(self):
        if config.LLM_PROVIDER == "ollama":
            self.embeddings = OllamaEmbeddings(
                model=config.EMBEDDING_MODEL,
                base_url=config.OLLAMA_BASE_URL
            )
        else:
            self.embeddings = OpenAIEmbeddings(
                model=config.EMBEDDING_MODEL,
                api_key=config.OPENAI_API_KEY
            )
        self.vector_store = None
        self._init_vector_store()

    def _init_vector_store(self):
        db_path = Path(config.VECTOR_STORE_DIR)
        if db_path.exists():
            index_file = db_path / "index.faiss"
            if index_file.exists():
                try:
                    self.vector_store = FAISS.load_local(
                        str(db_path),
                        self.embeddings,
                        allow_dangerous_deserialization=True
                    )
                except Exception:
                    self.vector_store = None

    def create_vector_store(self, examples: List[TrainingExample]):
        documents = []
        for i, example in enumerate(examples):
            doc = Document(
                page_content=example.input,
                metadata={
                    "reply": example.reply,
                    "language": example.language,
                    "index": i
                }
            )
            documents.append(doc)

        self.vector_store = FAISS.from_documents(
            documents=documents,
            embedding=self.embeddings
        )
        self._save_vector_store()

    def _save_vector_store(self):
        if self.vector_store:
            db_path = Path(config.VECTOR_STORE_DIR)
            db_path.mkdir(parents=True, exist_ok=True)
            self.vector_store.save_local(str(db_path))

    def add_example(self, example: TrainingExample):
        doc = Document(
            page_content=example.input,
            metadata={
                "reply": example.reply,
                "language": example.language,
                "index": 0
            }
        )
        
        if self.vector_store is None:
            self.create_vector_store([example])
        else:
            self.vector_store.add_documents([doc])
            self._save_vector_store()

    def similarity_search(self, query: str, k: int = config.MAX_RESULTS) -> List[Document]:
        if self.vector_store is None:
            return []
        
        docs = self.vector_store.similarity_search(query, k=k)
        return docs


class ReplyGenerator:
    def __init__(self):
        if config.LLM_PROVIDER == "ollama":
            self.llm = ChatOllama(
                model=config.LLM_MODEL,
                base_url=config.OLLAMA_BASE_URL,
                temperature=0.7
            )
        else:
            self.llm = ChatOpenAI(
                model=config.LLM_MODEL,
                api_key=config.OPENAI_API_KEY,
                temperature=0.7
            )

    def generate_reply(
        self, 
        query: str, 
        similar_examples: List[Dict[str, Any]],
        context: str = "",
        memory: str = "",
        system_prompt: str = "",
        mood_modifier: str = ""
    ) -> str:
        if not similar_examples:
            return self._get_fallback_response()

        context_str = "\n".join([
            f"Input: {ex['input']} -> Reply: {ex['reply']}"
            for ex in similar_examples
        ])

        system_msg = system_prompt or """You are a personal assistant who responds exactly like the user would.
        Based on the examples provided, generate a reply that matches the user's style and tone."""
        
        if mood_modifier:
            system_msg += f"\n\n{mood_modifier}"
        
        if memory:
            system_msg += f"\n\n{memory}"
        
        if context:
            system_msg += f"\n\nRecent conversation:\n{context}"

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_msg + "\n\nExamples:\n{context}\n\nNow respond to: {query}"),
            ("user", "{query}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "query": query, 
            "context": context_str
        })
        
        return response.content

    def _get_fallback_response(self) -> str:
        import random
        return random.choice(config.FALLBACK_RESPONSES)


def load_training_data() -> List[TrainingExample]:
    data_path = Path(config.TRAINING_DATA_FILE)
    if not data_path.exists():
        return []
    
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    examples = []
    for item in data.get("examples", []):
        examples.append(TrainingExample(
            input=item["input"],
            reply=item["reply"],
            language=data.get("language", "en")
        ))
    
    return examples


def save_training_data(examples: List[TrainingExample], language: str = "en"):
    data_path = Path(config.TRAINING_DATA_FILE)
    data = {
        "language": language,
        "examples": [
            {"input": ex.input, "reply": ex.reply}
            for ex in examples
        ]
    }
    
    data_path.parent.mkdir(parents=True, exist_ok=True)
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
