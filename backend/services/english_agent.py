"""
english_agent.py
Module for English Agent logic (e.g., LLM or custom logic) using LangGraph for multi-turn, multi-agent conversations.
"""

from typing import Dict, Any, Optional
from langchain.llms import OpenAI  # or your preferred LLM
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain.prompts import PromptTemplate
import copy
import os
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import LLMChain
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate

# --- State Management ---
class AgentState:
    """
    Tracks the conversation state, including history, extracted entities, user intent, and active agent.
    """
    def __init__(self, history=None, entities=None, intent=None, active_agent=None, followup_questions=None):
        self.history = history or []  # List of (user, agent) tuples
        self.entities = entities or {}  # e.g., {"product_category": "serum"}
        self.intent = intent  # e.g., "search", "recommend", "review_explanation", "brand_info"
        self.active_agent = active_agent  # e.g., "conversational_search"
        self.followup_questions = followup_questions or []

    def to_dict(self):
        return {
            "history": self.history,
            "entities": self.entities,
            "intent": self.intent,
            "active_agent": self.active_agent,
            "followup_questions": self.followup_questions,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            history=d.get("history", []),
            entities=d.get("entities", {}),
            intent=d.get("intent"),
            active_agent=d.get("active_agent"),
            followup_questions=d.get("followup_questions", []),
        )

# --- LLM Setup (Replace with your preferred LLM and config) ---
llm = OpenAI(
    base_url="https://api.aimlapi.com/v1",
    temperature=0.2,
    api_key=os.getenv("AIMLAPI_API_KEY")
)

# --- Load vector store and embeddings (singleton pattern for efficiency) ---
CATALOG_VECTORSTORE_DIR = os.path.join(os.path.dirname(__file__), "../catalog_vectorstore")
_embeddings = None
_vectorstore = None

def get_catalog_vectorstore():
    global _embeddings, _vectorstore
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    if _vectorstore is None:
        _vectorstore = Chroma(persist_directory=CATALOG_VECTORSTORE_DIR, embedding_function=_embeddings)
    return _vectorstore

# --- Extract available categories and skin concerns from catalog at startup ---
def get_catalog_categories_and_skin_concerns():
    vectorstore = get_catalog_vectorstore()
    # Extract all unique categories and tags (as skin concerns) from the vector store metadata
    categories = set()
    skin_concerns = set()
    # Chroma stores documents in _collection, which has get() for all docs
    for doc in vectorstore.get()['metadatas']:
        if doc is None:
            continue
        cat = doc.get('category')
        if cat:
            categories.add(str(cat).strip())
        tags = doc.get('tags')
        if tags:
            # tags is a list
            for tag in tags:
                skin_concerns.add(str(tag).strip())
    return sorted(categories), sorted(skin_concerns)

# Cache these at startup
AVAILABLE_CATEGORIES, AVAILABLE_SKIN_CONCERNS = get_catalog_categories_and_skin_concerns()

# --- Agent-specific LLMs with system prompts ---
def make_agent_llm(system_prompt):
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    return LLMChain(llm=OpenAI(
        base_url="https://api.aimlapi.com/v1",
        temperature=0.2,
        api_key=os.getenv("AIMLAPI_API_KEY")
    ), prompt=prompt)

# System prompts for each agent
CONVERSATIONAL_SEARCH_SYSTEM_PROMPT = (
    "You are a friendly, curious skincare shopping assistant. "
    "Your job is to help users clarify what they are looking for, ask relevant follow-up questions, and extract product categories and skin concerns from their queries. "
    "Always use the provided list of categories and skin concerns."
)
RECOMMENDATION_SYSTEM_PROMPT = (
    "You are an expert skincare product recommender. "
    "Given a user's query and a set of products, generate a concise, friendly justification for why these products are a good fit. "
    "Mention relevant categories, tags, or ingredients."
)
REVIEWS_SYSTEM_PROMPT = (
    "You are a trustworthy skincare review explainer. "
    "Given a product and user question, summarize relevant customer reviews and cite them to build trust."
)
BRAND_SYSTEM_PROMPT = """You are an expert on the Everglow brand. Below is the brand's philosophy, sustainability, and practices. 
EverGlow Labs exists to prove that nature and science can co-author skincare that
actually works.
We formulate every product around three uncompromising pillars:
1. Plant-Powered, Clinically Proven
• 100% vegan, cruelty-free, and silicone-free.
• We pair high-potency botanicals (rosewater, cactus enzymes, oat lipids) with gold-
standard actives (retinaldehyde, peptides, ceramides) validated in peer-reviewed
studies.
• Every finished formula undergoes third-party in-vitro and in-vivo testing for efficacy
and safety.
2. Radical Transparency
• Full-dose percentages of hero ingredients on every carton.
• Carbon-neutral supply chain; FSC-certified packaging and soy inks.
• Real, verified customer reviews only—no paid placements, no bots.
3. Barrier-First, Planet-First
• pH-optimized, microbiome-friendly formulas that respect your skin barrier.
• Cold-processed where possible to reduce energy use and preserve phyto-nutrients.
• 1% of revenue funds reef-safe sunscreen education and re-wilding projects.
The result: skincare, body care, and haircare that deliver visible results without
compromising ethics, the environment, or your wallet.

Answer questions about the brand's philosophy, sustainability, and practices in a positive, cheerful, optimistic and transparent manner."""


# Instantiate LLMChains for each agent
conversational_search_llm = make_agent_llm(CONVERSATIONAL_SEARCH_SYSTEM_PROMPT)
recommendation_llm = make_agent_llm(RECOMMENDATION_SYSTEM_PROMPT)
reviews_llm = make_agent_llm(REVIEWS_SYSTEM_PROMPT)
brand_llm = make_agent_llm(BRAND_SYSTEM_PROMPT)

# --- Conversational Search Agent ---
def conversational_search_agent(state: AgentState, user_input: str) -> (dict, AgentState):
    """
    Handles conversational search, uses agent-specific LLM for NER, asks follow-up questions, and hands off to Recommendation Agent when ready.
    Returns a dict with either a follow-up question or recommendation results.
    """
    # 1. Use agent-specific LLM to extract entities (NER) and match category with confidence
    ner_prompt = PromptTemplate(
        input_variables=["input", "categories"],
        template="""
        Given the user's query and the available product categories, select the closest matching category from the list. 
        If none are a good match, return null. Also provide a confidence score between 0 and 1 for your match.
        
        Available categories: {categories}
        User query: {input}
        
        Respond in JSON format: {{"category": <category or null>, "confidence": <score between 0 and 1>}}
        """
    )
    import json
    ner_output = conversational_search_llm.run({
        "input": user_input,
        "categories": ", ".join(AVAILABLE_CATEGORIES)
    })
    ner_output = ner_output.strip()
    try:
        ner_json = json.loads(ner_output.split("\n")[-1])
        extracted_category = ner_json.get("category")
        confidence = float(ner_json.get("confidence", 0))
    except Exception:
        extracted_category = None
        confidence = 0
    CONFIDENCE_THRESHOLD = 0.7
    entities = copy.deepcopy(state.entities)

    # --- Check if extracted category is valid and confident ---
    if extracted_category and extracted_category in AVAILABLE_CATEGORIES and confidence >= CONFIDENCE_THRESHOLD:
        entities["product_category"] = extracted_category
    elif extracted_category and extracted_category in AVAILABLE_CATEGORIES and confidence < CONFIDENCE_THRESHOLD:
        # Low confidence, ask user to pick
        response = (
            f"I'm not sure if you meant '{extracted_category}'. Would you like to see products from one of these categories instead? {', '.join(AVAILABLE_CATEGORIES)}."
        )
        entities.pop("product_category", None)
        state.active_agent = "conversational_search"
        state.followup_questions = [response]
        state.entities = entities
        state.history.append(("user", user_input))
        state.history.append(("agent", response))
        return {"response": response}, state
    elif extracted_category and extracted_category not in AVAILABLE_CATEGORIES:
        # LLM hallucinated a category not in catalog
        response = (
            f"Looks like we don't have products in the '{extracted_category}' category yet. "
            f"Would you like to see products from one of these categories instead? {', '.join(AVAILABLE_CATEGORIES)}."
        )
        entities.pop("product_category", None)
        state.active_agent = "conversational_search"
        state.followup_questions = [response]
        state.entities = entities
        state.history.append(("user", user_input))
        state.history.append(("agent", response))
        return {"response": response}, state
    else:
        # No category extracted
        entities.pop("product_category", None)

    # 2. Decide if follow-up questions are needed
    followup_questions = []
    if not entities.get("product_category"):
        # Vague query, ask clarifying question with up-to-date categories
        followup_questions.append(
            f"What products are you interested in? Choose from: {', '.join(AVAILABLE_CATEGORIES)}."
        )
    else:
        # Specific query, ask about skin concern with up-to-date skin concerns
        followup_questions.append(
            f"Great choice! What skin concern are you targeting? Options: {', '.join(AVAILABLE_SKIN_CONCERNS)}."
        )

    # 3. If enough info, hand off to Recommendation Agent
    ready_for_recommendation = entities.get("product_category") and state.intent == "recommend"
    if ready_for_recommendation:
        # Hand off to Recommendation Agent
        rec_result, new_state = recommendation_agent(state, query=user_input, entities=entities)
        new_state.history.append(("agent", rec_result["justification"]))
        new_state.active_agent = "recommendation"
        return rec_result, new_state
    else:
        # Continue conversational search
        response = followup_questions[0] if followup_questions else "Can you tell me more about what you're looking for?"
        state.active_agent = "conversational_search"
        state.followup_questions = followup_questions
        state.entities = entities
        state.history.append(("user", user_input))
        state.history.append(("agent", response))
        return {"response": response}, state

# --- Recommendation Agent (Complete Implementation) ---
def recommendation_agent(state: AgentState, query: str = None, entities: Dict[str, Any] = None) -> (Dict[str, Any], AgentState):
    """
    Filters the product catalog using entities, performs semantic search, and returns top recommendations with justification.
    Returns a dict with 'products' (list of product dicts) and 'justification' (string for chat/TTS).
    """
    vectorstore = get_catalog_vectorstore()
    entities = entities or state.entities or {}
    query = query or entities.get("query") or ""

    # --- Build metadata filter ---
    metadata_filter = {}
    if "category" in entities:
        metadata_filter["category"] = entities["category"].lower()
    if "product_category" in entities:
        metadata_filter["category"] = entities["product_category"].lower()
    if "tags" in entities and entities["tags"]:
        tags = entities["tags"] if isinstance(entities["tags"], list) else [entities["tags"]]
        tags = [t.lower() for t in tags]
        metadata_filter["tags"] = {"$in": tags}
    # TODO: Add more filters (e.g., price range) if needed

    # --- Perform search ---
    results = vectorstore.similarity_search(
        query,
        k=5,
        filter=metadata_filter if metadata_filter else None
    )

    # --- Format product results ---
    products = []
    for doc in results:
        meta = doc.metadata
        products.append({
            "product_id": meta.get("product_id"),
            "name": meta.get("name"),
            "category": meta.get("category"),
            "description": meta.get("description"),
            "top_ingredients": meta.get("top_ingredients"),
            "tags": meta.get("tags"),
            "price": meta.get("price (USD)"),
            "margin": meta.get("margin (%)"),
        })

    # --- Generate contextual justification using agent-specific LLM ---
    justification_prompt = PromptTemplate(
        input_variables=["query", "products"],
        template="""
        You are a helpful skincare shopping assistant. Given the user's query and the recommended products, write a friendly, concise of upto 10 words justification for why these products are a good fit. Mention the category, tags, or ingredients if relevant. This justification will act like a search result title.
        User query: {query}
        Products: {products}
        Justification:
        """
    )
    justification = recommendation_llm.run({
        "input": justification_prompt.format(query=query, products="\n".join([p["name"] for p in products]))
    }).strip()

    # --- Update state and return ---
    state.active_agent = "recommendation"
    state.history.append(("agent", justification))
    return {"products": products, "justification": justification}, state

# --- Customer Reviews Explanation Agent (Placeholder) ---
def reviews_explanation_agent(state: AgentState, product: str) -> (str, AgentState):
    """
    Uses agent-specific LLM to answer with review-backed explanations.
    """
    response = reviews_llm.run({"input": f"Give a review-backed explanation for {product}."}).strip()
    state.active_agent = "reviews_explanation"
    state.history.append(("agent", response))
    return response, state

# --- Brand Answer Generator (Placeholder) ---
def brand_answer_agent(state: AgentState, user_input: str) -> (str, AgentState):
    """
    Uses agent-specific LLM to answer brand-related questions.
    """
    response = brand_llm.run({"input": user_input}).strip()
    state.active_agent = "brand_answer"
    state.history.append(("agent", response))
    return response, state

# --- LLM-based Intent Detection and Routing ---
def llm_intent_router(state: AgentState, user_input: str) -> (str, AgentState):
    """
    Uses the LLM to classify intent and extract routing arguments/entities from user input.
    Returns the response and updated state.
    """
    # Define canonical intents and their descriptions
    intent_schema = {
        "recommend": "User wants product recommendations or to search for products.",
        "review_explanation": "User wants to know how a product has worked for others, or wants review-backed explanations.",
        "brand_info": "User wants to know about the brand's philosophy, sustainability, or practices.",
        "search": "User is exploring or asking general questions about products.",
    }
    # Prompt for intent and argument extraction
    router_prompt = PromptTemplate(
        input_variables=["input"],
        template="""
        You are an advanced AI assistant for a beauty and skincare store. Classify the user's intent and extract any relevant arguments.
        Possible intents:
        - recommend: User wants product recommendations or to search for products.
        - review_explanation: User wants to know how a product has worked for others, or wants review-backed explanations.
        - brand_info: User wants to know about the brand's philosophy, sustainability, or practices.
        - search: User is exploring or asking general questions about products.
        
        For the following user input, output a JSON object with:
        - intent: one of [recommend, review_explanation, brand_info, search]
        - arguments: a dictionary of any relevant arguments (e.g., product_category, product_name, question, etc.)
        
        User input: {input}
        JSON:
        """
    )
    import json
    router_output = llm(router_prompt.format(input=user_input))
    try:
        router_json = json.loads(router_output.strip().split("\n")[-1])
        intent = router_json.get("intent", "search")
        arguments = router_json.get("arguments", {})
    except Exception as e:
        # Fallback to default intent if parsing fails
        intent = "search"
        arguments = {}
        # TODO: Add error logging here
    state.intent = intent
    # Merge extracted arguments into state.entities
    state.entities.update(arguments)
    # Route to the appropriate agent
    if intent == "recommend":
        return conversational_search_agent(state, user_input)
    elif intent == "review_explanation":
        product = arguments.get("product_name", "[TODO: product]")
        return reviews_explanation_agent(state, product=product)
    elif intent == "brand_info":
        return brand_answer_agent(state, user_input)
    else:
        return conversational_search_agent(state, user_input)

# --- Router Agent (now uses LLM-based routing) ---
def router_agent(state: AgentState, user_input: str) -> (str, AgentState):
    """
    Routes the user input to the appropriate agent using LLM-based intent detection and argument extraction.
    """
    return llm_intent_router(state, user_input)

# --- LangGraph Setup ---
# For now, we use a simple function call chain. TODO: Integrate with LangGraph StateGraph for more complex flows.

def english_agent(text: str, state_dict: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Main entry point for the English Agent. Handles multi-turn, multi-agent conversations.
    Args:
        text: User input string
        state_dict: Optional dict representing the conversation state
    Returns:
        Dict with 'response' and 'state' (for next turn)
    """
    state = AgentState.from_dict(state_dict or {})
    response, new_state = router_agent(state, text)
    return {"response": response, "state": new_state.to_dict()}

# TODO: Integrate with LangGraph StateGraph for robust agent transitions and state management.
# TODO: Implement Recommendation, Reviews, and Brand agents fully.
# TODO: Connect to product catalog and reviews data sources.
# TODO: Add error handling and logging as needed. 