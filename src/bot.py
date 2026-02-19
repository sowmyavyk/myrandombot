from typing import List, Dict, Any
from src.graph import AdvancedReplyGraph
from src.core.chain import load_training_data, save_training_data, TrainingExample
from src.core.mood import PersonalityManager


class PersonalReplyBot:
    def __init__(self):
        self.graph = AdvancedReplyGraph()
        self.examples = load_training_data()
        self.personality_manager = PersonalityManager()

    def get_reply(self, message: str, user_id: str = "default") -> Dict[str, Any]:
        reply = self.graph.get_reply(message, user_id)
        stats = self.graph.get_stats()
        
        return {
            "reply": reply,
            "stats": stats
        }

    def train(self, input_text: str, reply: str, language: str = "en"):
        example = TrainingExample(
            input=input_text,
            reply=reply,
            language=language
        )
        
        self.examples.append(example)
        save_training_data(self.examples, language)
        
        self.graph.add_training_example(input_text, reply, language)

    def correct(self, query: str, original_reply: str, corrected_reply: str, 
                user_id: str = "default") -> str:
        return self.graph.learning_system.add_correction(
            user_id, query, original_reply, corrected_reply
        )

    def get_training_examples(self) -> List[Dict[str, Any]]:
        return [
            {"input": ex.input, "reply": ex.reply, "language": ex.language}
            for ex in self.examples
        ]

    def list_examples(self):
        print("\n" + "="*50)
        print("YOUR TRAINING EXAMPLES")
        print("="*50)
        for i, ex in enumerate(self.examples, 1):
            print(f"\n[{i}] Input: {ex.input}")
            print(f"    Reply: {ex.reply}")
            print(f"    Language: {ex.language}")
        print("\n" + "="*50)

    def set_personality(self, personality_key: str) -> bool:
        success = self.graph.change_personality(personality_key)
        if success:
            self.personality_manager.set_personality(personality_key)
        return success

    def list_personalities(self) -> List[Dict[str, str]]:
        return self.personality_manager.list_personalities()

    def get_stats(self) -> Dict[str, Any]:
        return self.graph.get_stats()

    def clear_conversation(self, user_id: str = "default"):
        self.graph.conversation_memory.clear_conversation(user_id)

    def add_memory(self, user_id: str, fact: str):
        self.graph.long_term_memory.add_fact(user_id, fact)
