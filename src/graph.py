from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_core.documents import Document

from src.core.chain import (
    VectorStoreManager, 
    ReplyGenerator, 
    TrainingExample,
    load_training_data
)
from src.memory import ConversationMemory, LongTermMemory
from src.core.mood import MoodDetector, LanguageDetector, PersonalityManager
from src.analytics import Analytics, LearningSystem
import config


class BotState(TypedDict):
    user_id: str
    query: str
    language: str
    mood: Optional[str]
    mood_confidence: float
    similar_docs: Optional[List[Document]]
    similar_examples: Optional[List[Dict[str, Any]]]
    conversation_context: str
    long_term_memory: str
    system_prompt: str
    mood_modifier: str
    reply: str
    is_fallback: bool


class AdvancedReplyGraph:
    def __init__(self):
        self.vector_store = VectorStoreManager()
        self.reply_generator = ReplyGenerator()
        
        self.conversation_memory = ConversationMemory()
        self.long_term_memory = LongTermMemory()
        
        self.mood_detector = MoodDetector()
        self.language_detector = LanguageDetector()
        self.personality_manager = PersonalityManager()
        
        self.analytics = Analytics()
        self.learning_system = LearningSystem()
        
        self._init_vector_store()
        self.graph = self._build_graph()

    def _init_vector_store(self):
        examples = load_training_data()
        if examples and self.vector_store.vector_store is None:
            self.vector_store.create_vector_store(examples)

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(BotState)

        workflow.add_node("detect_language", self._detect_language_step)
        workflow.add_node("detect_mood", self._detect_mood_step)
        workflow.add_node("get_context", self._get_context_step)
        workflow.add_node("search", self._search_step)
        workflow.add_node("generate", self._generate_step)

        workflow.set_entry_point("detect_language")
        workflow.add_edge("detect_language", "detect_mood")
        workflow.add_edge("detect_mood", "get_context")
        workflow.add_edge("get_context", "search")
        workflow.add_edge("search", "generate")
        workflow.add_edge("generate", END)

        return workflow.compile()

    def _detect_language_step(self, state: BotState) -> BotState:
        detected = self.language_detector.detect(state["query"])
        state["language"] = detected
        return state

    def _detect_mood_step(self, state: BotState) -> BotState:
        mood_result = self.mood_detector.detect(state["query"])
        state["mood"] = mood_result.mood
        state["mood_confidence"] = mood_result.confidence
        state["mood_modifier"] = self.mood_detector.get_response_modifier(mood_result)
        return state

    def _get_context_step(self, state: BotState) -> BotState:
        user_id = state["user_id"]
        
        context = self.conversation_memory.get_formatted_context(user_id)
        memory = self.long_term_memory.get_formatted_memory(user_id)
        personality = self.personality_manager.get_personality()
        
        state["conversation_context"] = context
        state["long_term_memory"] = memory
        state["system_prompt"] = personality.get("system_prompt", "")
        
        return state

    def _search_step(self, state: BotState) -> BotState:
        query = state["query"]
        
        docs = self.vector_store.similarity_search(query)
        
        similar_examples = []
        for doc in docs:
            similar_examples.append({
                "input": doc.page_content,
                "reply": doc.metadata.get("reply", ""),
                "language": doc.metadata.get("language", "en")
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
                query=query,
                similar_examples=similar_examples,
                context=state.get("conversation_context", ""),
                memory=state.get("long_term_memory", ""),
                system_prompt=state.get("system_prompt", ""),
                mood_modifier=state.get("mood_modifier", "")
            )
            is_fallback = False
        
        self.conversation_memory.add_message(
            user_id=state["user_id"],
            role="user",
            content=query,
            mood=state.get("mood"),
            language=state.get("language")
        )
        
        self.conversation_memory.add_message(
            user_id=state["user_id"],
            role="assistant",
            content=reply,
            mood=state.get("mood"),
            language=state.get("language")
        )
        
        self.analytics.track_message(
            user_id=state["user_id"],
            mood=state.get("mood"),
            language=state.get("language")
        )
        
        return {
            **state,
            "reply": reply,
            "is_fallback": is_fallback
        }

    def get_reply(self, query: str, user_id: str = "default") -> str:
        initial_state: BotState = {
            "user_id": user_id,
            "query": query,
            "language": "en",
            "mood": None,
            "mood_confidence": 0.0,
            "similar_docs": None,
            "similar_examples": None,
            "conversation_context": "",
            "long_term_memory": "",
            "system_prompt": "",
            "mood_modifier": "",
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

    def change_personality(self, personality_key: str) -> bool:
        return self.personality_manager.set_personality(personality_key)

    def get_stats(self) -> Dict[str, Any]:
        return self.analytics.get_stats()
