#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.bot import PersonalReplyBot
import config


def print_banner():
    print("""
╔═══════════════════════════════════════════════════════════╗
║         ADVANCED PERSONAL REPLY BOT - NLP Chatbot          ║
║           Built with LangChain + LangGraph                 ║
║                                                               ║
║  ✨ Mood Detection    ✨ Multi-Language    ✨ Memory         ║
║  ✨ Personas          ✨ Learning          ✨ Analytics       ║
╚═══════════════════════════════════════════════════════════╝
    """)


def print_menu():
    print("\n" + "─"*50)
    print("  1. Chat with bot")
    print("  2. Add new training example")
    print("  3. View all training examples")
    print("  4. Switch personality")
    print("  5. View analytics/stats")
    print("  6. Clear conversation history")
    print("  7. Add long-term memory")
    print("  8. Correct a reply (teach bot)")
    print("  9. Exit")
    print("─"*50 + "\n")


def chat_mode(bot: PersonalReplyBot, user_id: str = "cli_user"):
    print("\n🤖 Chat mode started! (type 'exit' to go back, 'mood' to see detected mood)")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == "exit":
            print("\n👋 Exiting chat mode...")
            break
        
        if user_input.lower() == "mood":
            print("Use 'stats' command to see mood analytics")
            continue
        
        if user_input.lower() == "stats":
            stats = bot.get_stats()
            print(f"\n📊 Messages: {stats['total_messages']}")
            print(f"📈 Top mood: {list(stats['top_moods'].keys())[0] if stats['top_moods'] else 'N/A'}")
            continue
        
        if not user_input:
            print("Please enter a message!")
            continue
        
        result = bot.get_reply(user_input, user_id)
        print(f"Bot: {result['reply']}\n")


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


def switch_personality(bot: PersonalReplyBot):
    print("\n🎭 Available Personalities")
    print("─"*30)
    
    personalities = bot.list_personalities()
    for p in personalities:
        print(f"  {p['key']}: {p['name']} - {p['description']}")
    
    print()
    choice = input("Choose personality (key): ").strip()
    
    if bot.set_personality(choice):
        print(f"\n✅ Switched to {choice} personality!")
    else:
        print("\n❌ Invalid personality!")


def view_stats(bot: PersonalReplyBot):
    stats = bot.get_stats()
    
    print("\n📊 BOT ANALYTICS")
    print("="*40)
    print(f"Total Messages: {stats['total_messages']}")
    print(f"Unique Users: {stats['unique_users']}")
    
    print(f"\n😊 Top Moods:")
    for mood, count in stats['top_moods'].items():
        print(f"   {mood}: {count}")
    
    print(f"\n🌐 Languages:")
    for lang, count in stats['top_languages'].items():
        lang_name = config.SUPPORTED_LANGUAGES.get(lang, {}).get("name", lang)
        print(f"   {lang_name}: {count}")
    
    print(f"\n📝 Corrections made: {stats['recent_corrections_count']}")
    print("="*40)


def add_memory(bot: PersonalReplyBot, user_id: str = "cli_user"):
    print("\n💾 Add Long-term Memory")
    print("─"*30 + "\n")
    
    fact = input("What should I remember about you? ").strip()
    if not fact:
        print("Error: Cannot remember empty fact!")
        return
    
    bot.add_memory(user_id, fact)
    print(f"\n✅ Got it! I'll remember: {fact}")


def correct_reply(bot: PersonalReplyBot, user_id: str = "cli_user"):
    print("\n📚 Correct a Reply")
    print("─"*30 + "\n")
    
    query = input("What was the message? ").strip()
    if not query:
        print("Error: Message cannot be empty!")
        return
    
    wrong = input("What did I reply incorrectly? ").strip()
    if not wrong:
        print("Error: Original reply cannot be empty!")
        return
    
    correct = input("What should I have replied? ").strip()
    if not correct:
        print("Error: Correct reply cannot be empty!")
        return
    
    result = bot.correct(query, wrong, correct, user_id)
    print(f"\n✅ {result}")


def main():
    print_banner()
    
    print("Initializing advanced bot...")
    bot = PersonalReplyBot()
    print(f"✅ Bot ready!")
    print(f"   Training examples: {len(bot.get_training_examples())}")
    print(f"   Current personality: {bot.graph.personality_manager.current_personality}")
    
    user_id = "cli_user"
    
    while True:
        print_menu()
        choice = input("Select an option: ").strip()
        
        if choice == "1":
            chat_mode(bot, user_id)
        elif choice == "2":
            add_example(bot)
        elif choice == "3":
            bot.list_examples()
        elif choice == "4":
            switch_personality(bot)
        elif choice == "5":
            view_stats(bot)
        elif choice == "6":
            bot.clear_conversation(user_id)
            print("\n✅ Conversation history cleared!")
        elif choice == "7":
            add_memory(bot, user_id)
        elif choice == "8":
            correct_reply(bot, user_id)
        elif choice == "9":
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid option! Please try again.")


if __name__ == "__main__":
    main()
