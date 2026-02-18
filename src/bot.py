from typing import List, Dict, Any
from src.graph import ReplyGraph
from src.chain import load_training_data, save_training_data, TrainingExample


class PersonalReplyBot:
    def __init__(self):
        self.graph = ReplyGraph()
        self.examples = load_training_data()

    def get_reply(self, message: str, language: str = "en") -> str:
        return self.graph.get_reply(message, language)

    def train(self, input_text: str, reply: str, language: str = "en"):
        example = TrainingExample(
            input=input_text,
            reply=reply,
            language=language
        )
        
        self.examples.append(example)
        save_training_data(self.examples, language)
        
        self.graph.add_training_example(input_text, reply, language)

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
