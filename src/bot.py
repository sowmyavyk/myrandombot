from typing import Dict, Any, List
from src.graph import AdvancedReplyGraph
from src.core.chain import load_training_data, save_training_data, TrainingExample
from src.core.mood import PersonalityManager
from src.tools.manager import ToolManager


class PersonalReplyBot:
    def __init__(self):
        self.graph = AdvancedReplyGraph()
        self.examples = load_training_data()
        self.personality_manager = PersonalityManager()
        self.tools = ToolManager()
        
        # Fast file command detection
        self.file_prefixes = (
            'ls', 'list', 'cd ', 'pwd', 'find ', 'search ', 'grep ',
            'read ', 'cat ', 'analyze ', 'run ', 'shell ', 'drives',
            'desktop', 'documents', 'downloads', 'home'
        )
        
        # Keywords that trigger full system search permission
        self.search_triggers = (
            'find', 'search', 'look for', 'where is', 'locate',
            'search all', 'search everywhere', 'search entire',
            'find in', 'search in all', 'full search', 'deep search'
        )
        
        # Cache for fast responses
        self._cache: Dict[str, str] = {}

    def is_file_command(self, message: str) -> bool:
        msg = message.lower().strip()
        
        # Fast prefix check
        if any(msg.startswith(p) for p in self.file_prefixes):
            return True
        
        # Fast keyword check for common patterns
        file_keywords = (
            'list files', 'show files', 'files in', 'folder',
            'go to', 'find file', 'search for', 'look for',
            'what\'s in', 'contents of', 'navigate'
        )
        return any(kw in msg for kw in file_keywords)

    def needs_full_access(self, message: str) -> bool:
        msg = message.lower().strip()
        
        # Check if it's a broad search request
        broad_search_keywords = (
            'find', 'search', 'look for', 'where is', 'locate',
            'search all', 'search everywhere', 'entire', 'full',
            'every folder', 'every file', 'all folders', 'all files'
        )
        
        is_search = any(kw in msg for kw in broad_search_keywords)
        
        # Check if they specified a location
        specific_locations = ('downloads', 'desktop', 'documents', 'folder', 'directory')
        has_location = any(loc in msg for loc in specific_locations)
        
        # If searching but no specific location, needs full access
        return is_search and not has_location

    def get_reply(self, message: str, user_id: str = "default") -> Dict[str, Any]:
        msg = message.strip()
        
        # Check if needs full access permission
        if self.needs_full_access(msg):
            return {
                "reply": "🔍 This requires a full system search. Would you like me to search all folders on your computer? (This may take a moment)",
                "type": "permission",
                "tool_used": True,
                "pending_action": {
                    "action": "full_search",
                    "query": msg
                }
            }
        
        # Handle permission response
        if msg.lower() in ['yes', 'yeah', 'sure', 'do it', 'go ahead', 'please do']:
            if hasattr(self, '_pending_search') and self._pending_search:
                # Do full search
                query = self._pending_search.pop()
                tool_result = self.tools.execute_full_search(query)
                formatted = self.tools.format_result(tool_result)
                return {
                    "reply": formatted,
                    "type": "tool",
                    "tool_used": True
                }
        
        # Fast path for file commands
        if self.is_file_command(msg):
            tool_result = self.tools.execute(msg)
            formatted = self.tools.format_result(tool_result)
            
            return {
                "reply": formatted,
                "type": "tool",
                "tool_used": True
            }
        
        # Check cache for simple queries
        cache_key = f"{user_id}:{msg.lower()}"
        if cache_key in self._cache:
            return {
                "reply": self._cache[cache_key],
                "type": "llm",
                "tool_used": False
            }
        
        # Use LangGraph for chat
        result = self.graph.get_reply(msg, user_id)
        
        # Cache the result
        if len(self._cache) > 100:
            self._cache.clear()
        self._cache[cache_key] = result
        
        return {
            "reply": result,
            "type": "llm",
            "tool_used": False
        }

    def chat(self, user_input: str, user_id: str = "default") -> str:
        result = self.get_reply(user_input, user_id)
        
        if result.get("tool_used"):
            return f"🔧 {result['reply']}"
        else:
            return f"🤖 {result['reply']}"

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
        self._cache.clear()

    def add_memory(self, user_id: str, fact: str):
        self.graph.long_term_memory.add_fact(user_id, fact)

    def handle_file_command(self, command: str) -> str:
        result = self.tools.execute(command)
        return self.tools.format_result(result)
