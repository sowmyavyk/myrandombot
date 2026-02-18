from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_core.documents import Document

from src.chain import (
    VectorStoreManager, 
    ReplyGenerator, 
    TrainingExample,
    load_training_data
)
import config


class BotState(TypedDict):
    query: str
    language: str
    similar_docs: Optional[List[Document]]
    similar_examples: Optional[List[Dict[str, Any]]]
    reply: str
    is_fallback: bool


class ReplyGraph:
    def __init__(self):
        self.vector_store = VectorStoreManager()
        self.reply_generator = ReplyGenerator()
        self._init_vector_store()
        self.graph = self._build_graph()

    def _init_vector_store(self):
        examples = load_training_data()
        if examples and self.vector_store.vector_store is None:
            self.vector_store.create_vector_store(examples)

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(BotState)

        workflow.add_node("search", self._search_step)
        workflow.add_node("generate", self._generate_step)

        workflow.set_entry_point("search")
        workflow.add_edge("search", "generate")
        workflow.add_edge("generate", END)

        return workflow.compile()

    def _search_step(self, state: BotState) -> BotState:
        query = state["query"]
        
        docs = self.vector_store.similarity_search(query)
        
        similar_examples = []
        for doc in docs:
            similar_examples.append({
                "input": doc.page_content,
                "reply": doc.metadata.get("reply", ""),
                "language": doc.metadata.get("language", "en"),
                "score": 1.0
            })
        
        return {
            **state,
            "similar_docs": docs,
            "similar_examples": similar_examples
        }

    def _generate_step(self, state: BotState) -> BotState:
        query = state["query"]
        similar_examples = state.get("similar_examples", [])
        
        if not similar_examples:
            reply = self.reply_generator._get_fallback_response()
            is_fallback = True
        else:
            reply = self.reply_generator.generate_reply(
                query, 
                similar_examples
            )
            is_fallback = False
        
        return {
            **state,
            "reply": reply,
            "is_fallback": is_fallback
        }

    def get_reply(self, query: str, language: str = "en") -> str:
        initial_state: BotState = {
            "query": query,
            "language": language,
            "similar_docs": None,
            "similar_examples": None,
            "reply": "",
            "is_fallback": False
        }
        
        final_state = self.graph.invoke(initial_state)
        return final_state["reply"]

    def add_training_example(self, input_text: str, reply: str, language: str = "en"):
        example = TrainingExample(
            input=input_text,
            reply=reply,
            language=language
        )
        self.vector_store.add_example(example)
