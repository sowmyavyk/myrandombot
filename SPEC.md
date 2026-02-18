# Personal NLP Auto-Reply Bot

## Project Overview
- **Project name**: Personal Reply Bot
- **Type**: NLP-powered auto-reply chatbot
- **Core functionality**: A bot that learns from user-provided message-reply pairs and generates contextual responses using LangChain and LangGraph
- **Target users**: Personal use for automating replies

## Functionality Specification

### Core Features
1. **Training Data Management** - Store and manage user's message-reply pairs
2. **Semantic Search** - Use embeddings to find similar messages
3. **Response Generation** - Generate appropriate replies based on context
4. **Multi-lingual Support** - Ready for future language expansion (Hindi, Telugu, etc.)
5. **LangGraph Workflow** - Orchestrate the reply generation pipeline

### User Interactions
- Add new message-reply pairs to training data
- Query the bot with a new message
- Get AI-generated reply based on learned patterns

### Data Handling
- Store training data in JSON format
- Use Chroma vector store for embeddings
- Support for multiple languages (UTF-8)

### Edge Cases
- No similar messages found - use fallback response
- Empty input - prompt for valid message
- New language - auto-detect and handle

## Acceptance Criteria
1. Bot can learn from user-provided examples
2. Bot can find similar messages semantically
3. Bot generates contextual replies
4. Multi-lingual infrastructure is in place
5. Clean LangGraph workflow
