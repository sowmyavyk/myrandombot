#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.bot import PersonalReplyBot


def print_banner():
    print("""
╔═══════════════════════════════════════════╗
║     PERSONAL REPLY BOT - NLP Chatbot      ║
║     Built with LangChain + LangGraph       ║
╚═══════════════════════════════════════════╝
    """)


def print_menu():
    print("\n" + "─"*40)
    print("  1. Chat with bot")
    print("  2. Add new training example")
    print("  3. View all training examples")
    print("  4. Exit")
    print("─"*40 + "\n")


def chat_mode(bot: PersonalReplyBot):
    print("\n🤖 Chat mode started! (type 'exit' to go back)\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == "exit":
            print("\n👋 Exiting chat mode...")
            break
        
        if not user_input:
            print("Please enter a message!")
            continue
        
        reply = bot.get_reply(user_input)
        print(f"Bot: {reply}\n")


def add_example(bot: PersonalReplyBot):
    print("\n📝 Add new training example")
    print("─"*30 + "\n")
    
    user_input = input("Enter the message/pattern: ").strip()
    if not user_input:
        print("Error: Message cannot be empty!")
        return
    
    reply = input("Enter your reply: ").strip()
    if not reply:
        print("Error: Reply cannot be empty!")
        return
    
    language = input("Language (default: en): ").strip() or "en"
    
    bot.train(user_input, reply, language)
    print(f"\n✅ Example added successfully!")


def main():
    print_banner()
    
    print("Initializing bot...")
    bot = PersonalReplyBot()
    print(f"✅ Bot ready! Loaded {len(bot.get_training_examples())} training examples\n")
    
    while True:
        print_menu()
        choice = input("Select an option: ").strip()
        
        if choice == "1":
            chat_mode(bot)
        elif choice == "2":
            add_example(bot)
        elif choice == "3":
            bot.list_examples()
        elif choice == "4":
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid option! Please try again.")


if __name__ == "__main__":
    main()
