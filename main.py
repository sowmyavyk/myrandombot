#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.bot import PersonalReplyBot


def print_banner():
    print("""
╔═══════════════════════════════════════════════════════════╗
║         🤖 PERSONAL AI ASSISTANT BOT v3.0                ║
║           Built with LangChain + LangGraph              ║
║                                                               ║
║  💬 Just chat with me - I'll handle everything!          ║
║                                                               ║
║  ✨ Auto-detects: File ops • Terminal • Chat • Memory    ║
╚═══════════════════════════════════════════════════════════╝
    """)


def main():
    print_banner()
    
    print("Initializing your AI assistant...")
    bot = PersonalReplyBot()
    print("✅ Bot ready! Just type your message.\n")
    print("─" * 60)
    print("Examples of what I can do:")
    print("  • 'hello, how are you?'              → Just chat")
    print("  • 'list files in Downloads'          → File manager")  
    print("  • 'go to Desktop and list files'    → Navigate + list")
    print("  • 'find myresume'                   → Search files")
    print("  • 'read config.py'                  → Read file content")
    print("  • 'search for password in files'    → Search content")
    print("  • 'analyze main.py'                 → Code analysis")
    print("  • 'run ls -la'                      → Terminal command")
    print("  • 'what files did I create?'        → Memory + search")
    print("─" * 60 + "\n")
    
    user_id = "cli_user"
    
    while True:
        try:
            user_input = input("💬 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                print("\n👋 Goodbye! Talk to you soon!")
                break
            
            if user_input.lower() == 'clear':
                bot.clear_conversation(user_id)
                print("✅ Conversation cleared!\n")
                continue
            
            if user_input.lower() == 'stats':
                stats = bot.get_stats()
                print(f"\n📊 Messages: {stats['total_messages']}, Users: {stats['unique_users']}\n")
                continue
            
            if user_input.lower().startswith('personality '):
                key = user_input.split()[1]
                bot.set_personality(key)
                print(f"✅ Switched to {key} personality!\n")
                continue
            
            response = bot.chat(user_input, user_id)
            print(f"{response}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()
