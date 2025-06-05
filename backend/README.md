# Everglow AI Storefront Backend

## Overview
This backend powers the Everglow AI Storefront's conversational agent system, enabling multi-turn, multi-agent, retrieval-augmented conversations for product search, recommendations, reviews, and brand Q&A. It is built with FastAPI, LangChain, LangGraph, and leverages RAG (Retrieval-Augmented Generation) for product and feedback retrieval.

---

## Architecture

### Agentic Router-Executor Design
- **Router Agent:** Uses an LLM to classify user intent and route queries to specialized agents.
- **Specialized Agents:**
  - **Conversational Search Agent:** Handles NER, follow-up questions, and hands off to Recommendation Agent.
  - **Recommendation Agent:** Filters and semantically searches the product catalog (RAG).
  - **Reviews Agent:** Answers with review-backed explanations, citing both customer reviews and support tickets (RAG).
  - **Brand Answer Agent:** Answers questions about the brand's philosophy, sustainability, and practices.
- **State Management:** All agents share a unified `AgentState` object, which tracks conversation history, extracted entities, user intent, and active agent.
- **Agent-Specific LLMs:** Each agent uses its own LLMChain with a unique system prompt, ensuring modular, role-specific behavior.

### Data & RAG Vectorstores
- **Product Catalog:**
  - Source: `skincare catalog.xlsx`
  - Preprocessed by `preprocess_catalog_for_rag.py` into a Chroma vectorstore with HuggingFace embeddings.
  - Each product is stored as a document with all fields and metadata (including normalized tags).
- **Customer Feedback (Reviews & Support Tickets):**
  - Source: `CustomerFeedback.xlsx` (sheets: "Reviews", "Customer Support Tickets")
  - Preprocessed by `preprocess_feedback_for_rag.py` into a single Chroma vectorstore with a `source` field (`review` or `support_ticket`).
  - Reviews: Ratings normalized (e.g., "★★★☆☆" → "3 out of 5"), linked to catalog products if possible, with `product_in_catalog` flag.
  - Support Tickets: Product extracted via fuzzy matching; Q&A stored as document text.

---

## Assumptions
- Product names in the catalog are unique and used for linking reviews/support tickets.
- Ratings in reviews may be numeric, fraction, or star strings; all are normalized to "X out of 5".
- All agents share the same conversation history and state for continuity.
- The catalog and feedback vectorstores are rebuilt when the source Excel files change.
- The LLM API key is provided via the `AIMLAPI_API_KEY` environment variable.

---

## Process & Workflow
1. **Preprocessing:**
   - Run `preprocess_catalog_for_rag.py` to build the product catalog vectorstore.
   - Run `preprocess_feedback_for_rag.py` to build the feedback (reviews/support) vectorstore.
2. **Agent System:**
   - User input is routed by the LLM-based router to the appropriate agent.
   - Agents use their own LLMChain and system prompt for completions.
   - The Recommendation and Reviews agents use RAG to retrieve relevant products, reviews, or support tickets.
   - All agent responses and user messages are tracked in the shared state/history.
3. **Extensibility:**
   - New agents can be added by defining a new LLMChain and system prompt.
   - Catalog and feedback preprocessing scripts are modular and can be extended for new data fields or sources.

---

## Key Files
- `services/english_agent.py`: Main agent logic, state management, and agent definitions.
- `preprocess_catalog_for_rag.py`: Preprocesses the product catalog for RAG.
- `preprocess_feedback_for_rag.py`: Preprocesses reviews and support tickets for RAG.
- `skincare catalog.xlsx`: Product catalog source data.
- `CustomerFeedback.xlsx`: Customer reviews and support tickets source data.

---

## Developer Notes
- **Adding New Data:** Update the preprocessing scripts and rerun them to refresh the vectorstores.
- **Adding New Agents:** Define a new LLMChain with a system prompt and add routing logic.
- **Updating Prompts:** Each agent's system prompt can be tuned for its role/personality.
- **Error Handling:** TODOs are present for adding robust error handling and logging.
- **Performance:** For large catalogs, consider optimizing vectorstore loading and retrieval.
- **Security:** Ensure API keys and sensitive data are managed securely (e.g., via environment variables).

---

## TODOs & Future Improvements
- Add more robust error handling and logging throughout the backend.
- Support incremental updates to vectorstores.
- Enhance product extraction from support tickets with LLM-based NER if needed.
- Integrate LangGraph StateGraph for more complex agent transitions.
- Add validation and schema checks for input Excel files.

---

For any questions or contributions, please refer to this README and the code comments for guidance. 