# Everglow AI Storefront Backend
## Overview
This backend powers the Everglow AI Storefront's conversational agent system, enabling multi-turn, multi-agent, retrieval-augmented conversations for product search, recommendations, reviews, and brand Q&A. It is built with FastAPI, LangChain, LangGraph, and leverages RAG (Retrieval-Augmented Generation) for product and feedback retrieval with Pinecone vector database and Cohere embeddings.

## Architecture
### Modular Agent System
The system has been refactored into a modular architecture with specialized agents:

- Router Agent ( services/router.py ): Uses Gemini LLM to classify user intent and route queries to specialized agents
- Specialized Agents (in services/agents/ ):
  - Conversational Search Agent ( conversational_search.py ): Handles NER, follow-up questions, and hands off to Recommendation Agent
  - Recommendation Agent ( recommendation.py ): Filters and semantically searches the product catalog using Pinecone vector database
  - Reviews Agent ( reviews.py ): Answers with review-backed explanations, citing customer reviews and support tickets
  - Brand Answer Agent ( brand.py ): Answers questions about the brand's philosophy, sustainability, and practices
### State Management
- Unified State ( services/state.py ): All agents share a unified AgentState object tracking conversation history, extracted entities, user intent, and active agent
- Persistent Context : State is serializable and can be passed between frontend and backend for session continuity
### Vector Database & RAG
- Pinecone Integration : Migrated from local Chroma to cloud-based Pinecone for scalable vector storage
- Cohere Embeddings : Using Cohere's embed-english-light-v2.0 model for semantic search
- Dual Indexes :
  - Product Catalog Index : Preprocessed skincare catalog with metadata filtering
  - Feedback Index : Customer reviews and support tickets for review-backed recommendations
### Voice Capabilities
- Speech-to-Text ( services/speech_to_text.py ): Async STT using AIML API with Whisper model
- Text-to-Speech ( services/text_to_speech.py ): Async TTS using AIML API with Aura voice synthesis
- WebSocket Support : Real-time voice interaction through WebSocket endpoints
## API Endpoints
### HTTP Endpoints
- POST /api/chat : Text-based chat with state persistence
- GET /api/products : Retrieve product catalog
- GET /api/products/{product_id} : Get specific product details
### WebSocket Endpoints
- /ws/voice : Real-time voice interaction (STT + agent processing + TTS)
- /ws/chat : Real-time text chat with typing indicators
## Configuration & Environment
### Required Environment Variables
```
# LLM Configuration
GEMINI_API_KEY=your_gemini_api_key
AIML_API_KEY=your_aiml_api_key

# Vector Database
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_REGION=us-east-1
PINECONE_CLOUD=aws
CATALOG_PINECONE_INDEX_NAME=everglow-cat
alog
FEEDBACK_PINECONE_INDEX_NAME=everglow-fe
edback

# Embeddings
COHERE_API_KEY=your_cohere_api_key
```
### Dependencies
- FastAPI : Web framework with WebSocket support
- LangChain : Agent orchestration and LLM integration
- Pinecone : Vector database for RAG
- Cohere : Embedding model
- Google Gemini : Primary LLM (gemini-2.5-flash-preview)
- AIML API : Speech-to-text and text-to-speech services
## Data Pipeline
### Preprocessing Scripts
1. preprocess_catalog_for_rag.py :
   
   - Processes skincare catalog.xlsx
   - Creates Pinecone index with product embeddings
   - Normalizes categories and tags for filtering
   - Includes metadata for price, ingredients, and product attributes
2. preprocess_feedback_for_rag.py :
   
   - Processes CustomerFeedback.xlsx (Reviews + Support Tickets)
   - Links feedback to catalog products via fuzzy matching
   - Normalizes ratings to "X out of 5" format
   - Creates separate Pinecone index for review-based retrieval
### Data Sources
- Product Catalog : skincare catalog.xlsx - Complete product information
- Customer Feedback : CustomerFeedback.xlsx - Reviews and support tickets
## Agent Workflow
1. Intent Classification : Router agent determines user intent using Gemini LLM
2. Agent Routing : Request routed to appropriate specialized agent
3. Entity Extraction : Conversational search agent extracts entities (categories, skin concerns, ingredients)
4. RAG Retrieval : Recommendation/Reviews agents query Pinecone with semantic search and metadata filtering
5. Response Generation : Agent-specific LLM generates contextual responses
6. State Update : Conversation state updated and returned to frontend
## Key Features
### Multi-Modal Interaction
- Text-based chat with rich product recommendations
- Voice interaction with real-time STT/TTS
- WebSocket support for real-time communication
### Intelligent Product Discovery
- Semantic search across product catalog
- Metadata filtering by category, skin concerns, ingredients
- Review-backed explanations with customer feedback
### Conversation Continuity
- Persistent state management across sessions
- Multi-turn conversations with context awareness
- Follow-up question generation for better product matching
## File Structure
```
backend/
├── main.
py                              # 
FastAPI application with HTTP/WebSocket 
endpoints
├── requirements.
txt                     # Python 
dependencies
├── preprocess_catalog_for_rag.py      
# Catalog preprocessing for Pinecone
├── preprocess_feedback_for_rag.py     
# Feedback preprocessing for Pinecone
├── services/
│   ├── config.py                       
# Environment config and LLM setup
│   ├── state.py                        
# AgentState class for conversation 
tracking
│   ├── router.py                       
# Intent classification and agent 
routing
│   ├── prompts.py                      
# LLM prompts for each agent
│   ├── data_utils.py                   
# Data loading and utility functions
│   ├── speech_to_text.py              
# AIML API STT integration
│   ├── text_to_speech.py              
# AIML API TTS integration
│   ├── english_agent.py               
# Main agent orchestration
│   └── agents/
│       ├── conversational_search.py   
# NER and conversation management
│       ├── recommendation.py          
# Product recommendation with RAG
│       ├── reviews.py                 
# Review-backed explanations
│       └── brand.py                   
# Brand information agent
```
## Setup Instructions
1. Install Dependencies :
   
   ```
   pip install -r requirements.txt
   ```
2. Environment Setup :
   
   - Copy .env.example to .env
   - Fill in all required API keys
3. Data Preprocessing :
   
   ```
   python preprocess_catalog_for_rag.py
   python preprocess_feedback_for_rag.py
   ```
4. Run Server :
   
   ```
   uvicorn main:app --reload --host 0.0.
   0.0 --port 8000
   ```
## Development Notes
### Adding New Agents
1. Create new agent file in services/agents/
2. Define agent-specific LLM chain in services/prompts.py
3. Add routing logic in services/router.py
4. Update intent classification in router prompt
### Extending Data Sources
1. Update preprocessing scripts for new data formats
2. Modify services/data_utils.py for new data loading functions
3. Update agent prompts to handle new data types
### Performance Optimization
- Pinecone indexes are optimized for fast similarity search
- Singleton patterns used for expensive resources (embeddings, Pinecone client)
- Async operations for STT/TTS to prevent blocking
## TODOs & Future Improvements
- Complete the Voice capabilities, STT and TTS functionality
- Create Database for catalog and feedback instead of xlsx
- Implement conversation analytics and logging
- Add support for incremental Pinecone index updates
- Adjust entity extraction with more sophisticated NER
- Add A/B testing framework for different prompts
- Implement conversation summarization for long sessions
- Create admin dashboard for monitoring agent performance
- Add rate limiting and authentication
- Add comprehensive error handling and retry logic
