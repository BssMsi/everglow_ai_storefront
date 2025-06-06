"""
english_agent.py
Module for English Agent logic (e.g., LLM or custom logic) using LangGraph for multi-turn, multi-agent conversations.
"""

from typing import Dict, Any, List, Tuple, Optional
from langchain_google_genai import ChatGoogleGenerativeAI # Import for Gemini
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import copy
import os
import json
import logging
import pandas as pd
from dotenv import load_dotenv

# Pinecone and Cohere Imports
from pinecone import Pinecone
from langchain_cohere import CohereEmbeddings

load_dotenv()  # Load environment variables

logger = logging.getLogger(__name__)

# --- State Management ---
class AgentState:
    """
    Tracks the conversation state, including history, extracted entities, user intent, and active agent.
    """
    def __init__(self, history=None, entities=None, intent=None, active_agent=None, followup_questions=None):
        self.history: List[Tuple[str, str]] = history or []  # List of (user, agent) tuples
        self.entities: Dict[str, Any] = entities or {}  # e.g., {"categories": ["serum"]}
        self.intent: Optional[str] = intent  # e.g., "search", "recommend", "review_explanation", "brand_info"
        self.active_agent: Optional[str] = active_agent  # e.g., "conversational_search"
        self.followup_questions: List[str] = followup_questions or []

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
if not os.getenv("GEMINI_API_KEY"):
    logger.error("GEMINI_API_KEY not set in environment variables.")
# Using the same LLM base URL and API key from main.py
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-05-20", # Specify the Gemini model, gemini-pro is a common default
    temperature=0.2,
    google_api_key=os.getenv("GEMINI_API_KEY") # Use the new environment variable
)

# --- Pinecone and Cohere Setup ---
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")
CATALOG_PINECONE_INDEX_NAME = os.getenv("CATALOG_PINECONE_INDEX_NAME", "everglow-catalog")  # Consistent index name
FEEDBACK_PINECONE_INDEX_NAME = os.getenv("FEEDBACK_PINECONE_INDEX_NAME", "everglow-feedback")  # Consistent index name
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# Initialize Cohere Embeddings (1024 dimensions)
# Use a singleton pattern for efficiency
_cohere_embeddings: Optional[CohereEmbeddings] = None

def get_cohere_embeddings() -> CohereEmbeddings:
    global _cohere_embeddings
    if _cohere_embeddings is None:
        if not COHERE_API_KEY:
            logger.error("COHERE_API_KEY not set in environment variables.")
            raise ValueError("COHERE_API_KEY not set in environment variables.")
        _cohere_embeddings = CohereEmbeddings(cohere_api_key=COHERE_API_KEY, model="embed-english-light-v2.0")
        logger.info("Initialized Cohere Embeddings model: embed-english-light-v2.0")
    return _cohere_embeddings

# Initialize Pinecone Client
# Use a singleton pattern for efficiency
_pinecone_client: Optional[Pinecone] = None

def get_pinecone_client() -> Pinecone:
    global _pinecone_client
    if _pinecone_client is None:
        if not PINECONE_API_KEY:
            logger.error("PINECONE_API_KEY not set in environment variables.")
            raise ValueError("PINECONE_API_KEY not set in environment variables.")
        _pinecone_client = Pinecone(api_key=PINECONE_API_KEY)
        logger.info("Initialized Pinecone client.")
    return _pinecone_client

# Get Pinecone Index objects
def get_catalog_index():
    pc = get_pinecone_client()
    if CATALOG_PINECONE_INDEX_NAME not in [idx.name for idx in pc.list_indexes()]:
        logger.error(f"Pinecone catalog index '{CATALOG_PINECONE_INDEX_NAME}' not found. Please run preprocessing script.")
        raise ValueError(f"Pinecone catalog index '{CATALOG_PINECONE_INDEX_NAME}' not found. Please run preprocessing script.")
    return pc.Index(CATALOG_PINECONE_INDEX_NAME)

def get_feedback_index():
    pc = get_pinecone_client()
    if FEEDBACK_PINECONE_INDEX_NAME not in [idx.name for idx in pc.list_indexes()]:
        logger.error(f"Pinecone feedback index '{FEEDBACK_PINECONE_INDEX_NAME}' not found. Please run preprocessing script.")
        raise ValueError(f"Pinecone feedback index '{FEEDBACK_PINECONE_INDEX_NAME}' not found. Please run preprocessing script.")
    return pc.Index(FEEDBACK_PINECONE_INDEX_NAME)

# --- Extract available categories and skin concerns from catalog at startup ---
# This part still needs to read from the catalog data itself, not the Pinecone index,
# unless you want to query Pinecone for all distinct categories/tags, which might be slow.
# Keeping the original logic for now, assuming the preprocessed data source (excel) is available for this.
# If the excel isn't available here, we'd need an alternative way to get these lists.
CATALOG_PATH = os.path.join(os.path.dirname(__file__), "../preprocess_catalog_for_rag.py")  # This path seems wrong for reading data
# Assuming the catalog data source is available relative to this file, e.g., ../skincare catalog.xlsx
CATALOG_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "skincare catalog.xlsx")

def get_catalog_categories_and_skin_concerns_from_source():
    """
    Loads the skincare catalog Excel file and returns a set of product names, categories, and tags.
    This is used to get available options for the agent.
    Note: This function reads the source file, not the Pinecone index.
    """
    try:
        df = pd.read_excel(CATALOG_DATA_PATH).dropna()
        categories = set(str(p).strip() for p in df["category"].dropna().unique())
        skin_concerns = set()
        for tags_str in df["tags"].dropna().unique():
            tag_list = [t.strip() for t in str(tags_str).split('|') if t.strip()]
            skin_concerns.update(tag_list)
        ingredients = set()
        for ingredient in df['top_ingredients'].str.split('; ').explode().unique():
            ingredients.update(ingredient.lower())
        logger.info(f"Loaded {len(categories)} categories and {len(skin_concerns)} skin concerns and {len(ingredients)} ingredients from catalog source.")
        return sorted(list(categories)), sorted(list(skin_concerns)), sorted(list(ingredients))
    except FileNotFoundError:
        logger.error(f"Catalog source file not found at {CATALOG_DATA_PATH}. Cannot extract categories and skin concerns.")
        return [], [], []
    except KeyError as e:
        logger.error(f"Catalog source file is missing expected column: {e}.")
        return [], [], []
    except Exception as e:
        logger.exception(f"Error loading categories and skin concerns from catalog source: {e}.")
        return [], [], []

# Cache these at startup from the source file
AVAILABLE_CATEGORIES, AVAILABLE_SKIN_CONCERNS, AVAILABLE_INGREDIENTS = get_catalog_categories_and_skin_concerns_from_source()

# --- Agent-specific LLMs with system prompts ---
def make_agent_llm(system_prompt):
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    # Reuse the main LLM configuration
    return prompt | llm

# System prompts for each agent
CONVERSATIONAL_SEARCH_SYSTEM_PROMPT = """You are a skincare expert. You need to do perform NER to identify three entities - product_categories and product_ingredients and skin_concerns. Maintain a high confidence for extraction of each value.
Given the user's query and chat history and the list of available product_categories and product_ingredients

Available categories: %s
Available ingredients: %s
Available skin concerns: %s

Extract values only from the available list, do not hallucinate or make up your own values.
Respond ONLY in JSON format: {{"categories": [<category>], "ingredients": [<ingredient>], "skin_concerns": [<skin_concern>]}}
""" % (", ".join(AVAILABLE_CATEGORIES), ", ".join(AVAILABLE_INGREDIENTS), ", ".join(AVAILABLE_SKIN_CONCERNS))

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
    logger.info("Conversational Search Agent: Started.")
    entities = copy.deepcopy(state.entities) # Initialize entities at the start
    # 1. Use agent-specific LLM to extract entities (NER) and match category with confidence
    try:
        ner_output = conversational_search_llm.invoke({
            "input": user_input
        })
        ner_output_content = ner_output.content.strip()
        # Attempt to parse the JSON output from the LLM
        try:
            # Handle cases where the LLM might output more than just JSON, e.g., in markdown code blocks
            cleaned_output = ner_output_content
            if "```json" in cleaned_output:
                cleaned_output = cleaned_output.split("```json")[1].split("```" )[0].strip()
            elif "```" in cleaned_output:  # A more general attempt to extract from a code block
                cleaned_output = cleaned_output.split("```" )[1].strip()

            logger.debug(f"Conversational Search Agent: NER cleaned output: {cleaned_output}")
            updated_entities = json.loads(cleaned_output)
            entities.update(json.loads(cleaned_output))  # Use cleaned_output

            logger.info(f"Conversational Search Agent: NER extracted categories: {cleaned_output}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during LLM NER output parsing. Error: {e}. Output was: {ner_output}", exc_info=True)
            confidence = 0
            # Return error immediately on other parsing failures
            error_msg = "Sorry, an unexpected error occurred while processing the product category."
            state.history.append(("agent", error_msg))
            logger.error(f"Conversational Search Agent: Unexpected error during NER parsing. Returning error. cleaned_output={cleaned_output}")
            return {"error": error_msg}, state # Return error structure

    except Exception as e:
        logger.exception(f"Error running conversational search LLM for NER: {e}")
        # Return error immediately on LLM invocation failure
        error_msg = "Sorry, I encountered an error while trying to understand your request."
        state.history.append(("agent", error_msg))
        logger.error(f"Conversational Search Agent: LLM invocation error during NER. Returning error. ner_output={ner_output}")
        return {"error": error_msg}, state # Return error structure

    # CONFIDENCE_THRESHOLD = 0.7

    # # --- Check if extracted category is valid and confident ---
    # # Convert extracted category to lowercase for case-insensitive comparison with AVAILABLE_CATEGORIES
    # extracted_category_lower = extracted_category.lower() if extracted_category else None
    # available_categories_lower = [c.lower() for c in AVAILABLE_CATEGORIES]

    # if extracted_category_lower and extracted_category_lower in available_categories_lower and confidence >= CONFIDENCE_THRESHOLD:
    #     # Find the correctly cased category name from the available list
    #     correctly_cased_category = next((c for c in AVAILABLE_CATEGORIES if c.lower() == extracted_category_lower), extracted_category)
    #     entities["product_category"] = correctly_cased_category
    #     logger.info(f"Conversational Search Agent: Using extracted category: {entities["product_category"]}")
    # elif extracted_category_lower and extracted_category_lower in available_categories_lower and confidence < CONFIDENCE_THRESHOLD:
    #     # Low confidence, ask user to pick
    #     response = (
    #         f"I'm not sure if you meant '{extracted_category}'. Would you like to see products from one of these categories instead? {', '.join(AVAILABLE_CATEGORIES)}."
    #     )
    #     entities.pop("product_category", None)
    #     state.active_agent = "conversational_search"
    #     state.followup_questions = [response]
    #     state.entities = entities
    #     # state.history.append(("user", user_input))  # Avoid double logging user input
    #     state.history.append(("agent", response))
    #     logger.info(f"Conversational Search Agent: Low confidence for category '{extracted_category}'. Asking for clarification.")
    #     return {"response": response}, state
    # elif extracted_category_lower and extracted_category_lower not in available_categories_lower:
    #     # LLM hallucinated a category not in catalog
    #     response = (
    #         f"Looks like we don't have products in the '{extracted_category}' category yet. "
    #         f"Would you like to see products from one of these categories instead? {', '.join(AVAILABLE_CATEGORIES)}."
    #     )
    #     entities.pop("product_category", None)
    #     state.active_agent = "conversational_search"
    #     state.followup_questions = [response]
    #     state.entities = entities
    #     # state.history.append(("user", user_input))  # Avoid double logging user input
    #     state.history.append(("agent", response))
    #     logger.warning(f"Conversational Search Agent: LLM hallucinated category: {extracted_category}")
    #     return {"response": response}, state
    # else:
    #     # No valid category extracted
    #     entities.pop("product_category", None)
    #     logger.info("Conversational Search Agent: No valid category extracted from user input.")

    # 2. Decide if follow-up questions are needed
    followup_questions = []
    # Logic to determine if enough info is present (e.g., category AND skin concern)
    if not entities.get("categories", []):
        # Vague query, ask clarifying question with up-to-date categories
        followup_questions.append(
            f"What products are you looking for? Choose from: {', '.join(AVAILABLE_CATEGORIES)}."
        )
        logger.info("Conversational Search Agent: Asking for product category.")

    # 3. If enough info, hand off to Recommendation Agent
    # For now, let's hand off if we have at least a category and the intent is recommend
    # NOTE: The router sets the intent. The conversational agent acts ON that intent.
    ready_for_recommendation = entities.get("categories", []) and state.intent == "recommend"

    if ready_for_recommendation:
        logger.info("Conversational Search Agent: Ready for recommendation. Calling recommendation_agent.")
        rec_result, new_state = recommendation_agent(state, user_input, entities)
        # History updated within recommendation_agent
        new_state.active_agent = "recommendation"
        return rec_result, new_state
    else:
        # Continue conversational search or indicate need for more info
        response = followup_questions[0] if followup_questions else "Can you tell me more about what you're looking for?"
        state.active_agent = "conversational_search"
        state.followup_questions = followup_questions
        state.entities = entities  # Update state with extracted entities
        # state.history.append(("user", user_input))  # Avoid double logging user input
        state.history.append(("agent", response))
        logger.info(f"Conversational Search Agent: Continuing conversational search. Responding: {response}")
        return {"response": response}, state

# --- Recommendation Agent (Uses Pinecone Catalog Index) ---
def recommendation_agent(state: AgentState, user_input: str, entities: Dict[str, Any]) -> (Dict[str, Any], AgentState):
    """
    Generates embeddings for the user query, filters the Pinecone catalog index using entities, performs semantic search, and returns top recommendations with justification.
    Returns a dict with 'products' (list of product dicts) and 'justification' (string for chat/TTS).
    """
    logger.info(f"Recommendation Agent: Started with entities: {entities}")

    embeddings_model = get_cohere_embeddings()
    catalog_index = get_catalog_index()

    # 1. Generate embedding for the user query
    try:
        query_vector = embeddings_model.embed_query(user_input)
    except Exception as e:
        logger.exception(f"Error generating embedding for query: {e}")
        # Fallback or error response
        error_msg = "Sorry, I had trouble processing your request to find recommendations."
        state.history.append(("agent", error_msg))
        logger.error("Recommendation Agent: Failed to generate embedding. Returning error.")
        return {"error": error_msg}, state # Return error structure

    # 2. Build metadata filter based on extracted entities
    metadata_filter = {}
    # Filter by category (case-insensitive match requires $eq or transforming all metadata to lower)
    # Pinecone filter values are case-sensitive. We can either lowercase all category metadata during preprocessing
    # or use a more complex filter if needed, but for now assuming lowercase in index.
    # The preprocessing script already lowercases and strips category and tags before storing.
    if entities.get("categories"):
        metadata_filter["category"] = {"$in": list(map(str.lower, entities["categories"]))}
        logger.debug(f"Recommendation Agent: Adding category filter: {metadata_filter['category']}")

    # Filter by tags (using $in for list matching)
    if entities.get("skin_concerns"):
        metadata_filter["tags"] = {"$in": list(map(str.lower, entities["skin_concerns"]))}
        logger.debug(f"Recommendation Agent: Adding tags filter: {metadata_filter['tags']}")

    if entities.get('ingredients'):
        metadata_filter["top_ingredients"] = {"$in": list(map(str.lower, entities["ingredients"]))}
        logger.debug(f"Recommendation Agent: Adding ingredients filter: {metadata_filter['ingredients']}")

    logger.info(f"Recommendation Agent: Performing Pinecone similarity search with filter: {metadata_filter}")

    # 3. Perform Pinecone similarity search
    try:
        query_response = catalog_index.query(
            vector=query_vector,
            top_k=5,  # Get top 5 results
            include_metadata=True,  # Include metadata to get product details
            filter=metadata_filter if metadata_filter else {}  # Apply filter if exists
        )
        results = query_response.matches
        logger.info(f"Recommendation Agent: Pinecone query returned {len(results)} matches.")

    except Exception as e:
        logger.exception(f"Error during Pinecone similarity search: {e}")
        error_msg = "Sorry, I encountered an error while searching for products based on your criteria."
        state.history.append(("agent", error_msg))
        logger.error("Recommendation Agent: Pinecone search failed. Returning error.")
        return {"error": error_msg}, state # Return error structure

    # 4. Format product results from Pinecone response
    product_ids = []
    products = []
    if not results:
        logger.info("Recommendation Agent: No products found matching the criteria.")
        response = "Sorry, I couldn't find any products matching your criteria."  # Agent response
        state.history.append(("agent", response))
        return {"response": response, "products": []}, state # Return success with empty products and message

    for match in results:
        meta = match.metadata
        products.append({
            "product_id": meta.get("product_id"),
            "name": meta.get("name"),
            "category": meta.get("category"),
            "description": meta.get("description"),
            "top_ingredients": meta.get("top_ingredients"),
            "tags": meta.get("tags"),  # Should be a list from Pinecone metadata
            "price": meta.get("price (USD)"),
        })
        
        product_ids.append(meta["product_id"])
        logger.debug(f"Recommendation Agent: Formatted product: {meta.get('name')}")

    # 5. Generate contextual justification using agent-specific LLM
    justification_prompt = PromptTemplate(
        input_variables=["query", "products"],
        template="""
        You are a helpful skincare shopping assistant. Given the user's query and the recommended products, write a friendly, concise of upto 10 words justification for why these products are a good fit. Mention the category, tags, or ingredients if relevant. This justification will act like a search result title.
        User query: {query}
        Products: {products}
        Justification:
        """
    )
    try:
        # Pass product names or a summary to the LLM for justification
        product_summary = ", ".join([p.get("name", "Unknown Product") for p in products])
        logger.debug(f"Recommendation Agent: Justification prompt input: {justification_prompt.format(query=user_input, products=product_summary)}")
        justification = recommendation_llm.invoke({
            "input": justification_prompt.format(query=user_input, products=product_summary)
        })
        logger.debug(f"Recommendation Agent: LLM Response {justification}")
    except Exception as e:
        logger.exception(f"Error generating recommendation justification: {e}")
        # This error is less critical, can fallback to a generic justification
        justification = "Here are some products I found."  # Fallback justification
        logger.error("Recommendation Agent: Failed to generate justification. Using fallback.")

    # --- Update state and return ---
    # state.history.append(("user", user_input))  # Avoid double logging user input
    # The justification is added to history below in the main english_agent if no top-level error
    state.active_agent = "recommendation"

    logger.info("Recommendation Agent: Finished.")
    # Return products and justification for the main agent to format the final response
    return {"product_ids": product_ids, "justification": justification.content}, state

# --- Customer Reviews Explanation Agent (Uses Pinecone Feedback Index) ---
def reviews_explanation_agent(state: AgentState, user_input: str) -> (str, AgentState):
    """
    Generates embeddings for the user query/product question, queries the Pinecone feedback index for relevant reviews, and uses agent-specific LLM to answer with review-backed explanations.
    Now also handles product name extraction if not already in state.
    """
    logger.info(f"Reviews Explanation Agent: Started with input: {user_input}")

    # --- 1. Extract or confirm Product Name ---
    product = state.entities.get("product_name") # Check if product name is already in state

    if not product:
        # If not in state, attempt to extract from user_input using LLM
        extraction_prompt_template = """
        Given the user's input, identify the specific product name they are asking about for reviews.
        If a product name is mentioned, extract it. If not, return null.

        User input: {user_input}

        Respond ONLY with a JSON object like: {{"product_name": <product name or null>}}
        """
        extraction_prompt = PromptTemplate(
            input_variables=["user_input"],
            template=extraction_prompt_template
        )
        extracted_product_name = None
        try:
            logger.debug(f"Reviews Explanation Agent: Product extraction prompt input: {extraction_prompt.format(user_input=user_input)}")
            extraction_output = llm.invoke(extraction_prompt.format(user_input=user_input))
            logger.debug(f"Reviews Explanation Agent: Product extraction raw output: {extraction_output}") # Log raw output
            cleaned_output = str(extraction_output).strip()
            if "```json" in cleaned_output:
                 cleaned_output = cleaned_output.split("```json")[1].split("```" )[0].strip()
            elif "```" in cleaned_output: # General code block handling
                 cleaned_output = cleaned_output.split("```" )[1].strip()

            logger.debug(f"Reviews Explanation Agent: Product extraction cleaned output: {cleaned_output}") # Log cleaned output
            extraction_json = json.loads(cleaned_output)
            extracted_product_name = extraction_json.get("product_name")
            logger.info(f"Reviews Explanation Agent: Extracted product name from LLM: {extracted_product_name}")

            if extracted_product_name:
                 product = extracted_product_name
                 state.entities["product_name"] = product # Store in state for future turns

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from product extraction LLM output. Error: {e}. Output was: {cleaned_output}", exc_info=True)
            # If JSON decode fails, it means the LLM likely gave a conversational response.
            # Use this response as a clarifying question.
            response = cleaned_output
            state.active_agent = "reviews_explanation" # Stay in reviews agent context or clarify
            state.followup_questions = [response] # Use the non-JSON response as a followup
            # Do NOT update product in entities, as extraction failed
            state.history.append(("agent", response))
            logger.warning("Reviews Explanation Agent: LLM returned non-JSON output during product extraction. Using it as a clarifying question.")
            return {"response": response}, state # Return the conversational response
        except Exception as e:
            logger.exception(f"Error during product name extraction: {e}")
            error_msg = "Sorry, an error occurred while trying to identify the product you're asking about for reviews."
            state.history.append(("agent", error_msg))
            logger.error("Reviews Explanation Agent: Unexpected error during product extraction. Returning error.")
            return {"error": error_msg}, state


    if not product:
        # If product name still not identified, ask user for clarification
        response = "Which product would you like to know reviews about? Please specify the product name." # Agent response
        state.active_agent = "conversational_search" # Or a dedicated clarification state
        state.followup_questions = [response]
        # state.history.append(("user", user_input)) # Avoid double logging
        state.history.append(("agent", response))
        logger.warning("Reviews Explanation Agent: No product name found. Asking for clarification.")
        # Returning a dictionary like other agents for consistency, even if just a response
        return {"response": response}, state

    # Product name is identified, proceed with review search
    logger.info(f"Reviews Explanation Agent: Proceeding with reviews search for product: {product}")

    embeddings_model = get_cohere_embeddings()
    feedback_index = get_feedback_index()

    # 2. Generate embedding for the query (user input + product)
    query_text = f"Reviews and feedback for product: {product}. User question: {user_input}" # Use full user_input as context for query
    try:
        logger.debug(f"Reviews Explanation Agent: Feedback query text: {query_text}")
        query_vector = embeddings_model.embed_query(query_text)
        logger.info("Reviews Explanation Agent: Generated embedding for feedback query.")
    except Exception as e:
        logger.exception(f"Error generating embedding for feedback query: {e}")
        error_msg = "Sorry, I had trouble processing your request to search for reviews."
        state.history.append(("agent", error_msg))
        logger.error("Reviews Explanation Agent: Failed to generate feedback embedding. Returning error.")
        return {"error": error_msg}, state

    # 3. Build metadata filter (filter by product name if available)
    metadata_filter = {}
    if product:
        # Assuming product name in metadata is stored as lowercase
        metadata_filter["product"] = product.lower()
        logger.debug(f"Reviews Explanation Agent: Adding product filter for feedback search: {metadata_filter['product']}")

    logger.info(f"Reviews Explanation Agent: Performing Pinecone feedback search with filter: {metadata_filter}")

    # 4. Perform Pinecone similarity search on feedback index
    try:
        query_response = feedback_index.query(
            vector=query_vector,
            top_k=5,  # Get top 5 relevant feedback entries
            include_metadata=True,  # Include metadata
            filter=metadata_filter if metadata_filter else {}  # Apply filter
        )
        results = query_response.matches
        logger.info(f"Reviews Explanation Agent: Pinecone feedback query returned {len(results)} matches.")

    except Exception as e:
        logger.exception(f"Error during Pinecone feedback search: {e}")
        error_msg = "Sorry, I encountered an error while searching for reviews for that product."
        state.history.append(("agent", error_msg))
        logger.error("Reviews Explanation Agent: Pinecone feedback search failed. Returning error.")
        return {"error": error_msg}, state

    # 5. Format feedback results and provide to LLM
    if not results:
        logger.info(f"Reviews Explanation Agent: No feedback found for product: {product}")
        response = f"I couldn't find any reviews or feedback for {product}. Is there anything else I can help with?"  # Agent response
        state.history.append(("agent", response))
        logger.info("Reviews Explanation Agent: No feedback found.")
        return {"response": response}, state # Return success with message

    feedback_texts = [match.page_content for match in results]  # Assuming original text is stored in page_content
    # You might want to include relevant metadata in the prompt too
    feedback_context = "\n---\n".join(feedback_texts)
    logger.debug(f"Reviews Explanation Agent: Feedback context for LLM: {feedback_context[:200]}...")

    # 6. Use agent-specific LLM to answer with review-backed explanations
    review_prompt_template = """
    Given the following customer feedback and reviews for a product, summarize the key points and address the user's question.
    Cite specific feedback points where possible.

    Product: {product}
    User Question: {user_question}
    Customer Feedback:
    {feedback_context}

    Answer:
    """
    review_prompt = PromptTemplate(
        input_variables=["product", "user_question", "feedback_context"],
        template=review_prompt_template
    )

    try:
        user_question = user_input # Use original user input as the question context
        logger.debug(f"Reviews Explanation Agent: Review prompt input: {review_prompt.format(product=product, user_question=user_question, feedback_context=feedback_context[:200] + '...')}")
        response = reviews_llm.invoke({
            "input": review_prompt.format(
                product=product,
                user_question=user_question,
                feedback_context=feedback_context
            )
        })
        logger.info("Reviews Explanation Agent: Generated review explanation.")
    except Exception as e:
        logger.exception(f"Error generating review explanation: {e}")
        error_msg = "Sorry, I couldn't generate a review explanation for that product at this time."
        state.history.append(("agent", error_msg))
        logger.error("Reviews Explanation Agent: Failed to generate review explanation. Returning error.")
        return {"error": error_msg}, state

    state.active_agent = "reviews_explanation"
    # state.history.append(("user", user_input))  # Avoid double logging user input
    # The response is added to history below in the main english_agent if no top-level error
    logger.info("Reviews Explanation Agent: Finished.")
    # Ensure consistent return type (dict)
    return {"response": response.content}, state # Return success with response

# --- Brand Answer Generator (Placeholder - Does not use RAG yet) ---
# TODO: Potentially add RAG for brand information if it's stored in a vector store.
def brand_answer_agent(state: AgentState, user_input: str) -> (str, AgentState):
    """
    Uses agent-specific LLM to answer brand-related questions.
    (Does not use RAG yet).
    """
    logger.info("Brand Answer Agent: Started.")
    try:
        response = brand_llm.invoke({"input": user_input})
        logger.info("Brand Answer Agent: Generated brand answer.")
    except Exception as e:
        logger.exception(f"Error generating brand answer: {e}")
        error_msg = "Sorry, I can't answer brand questions right now due to an internal issue."
        state.history.append(("agent", error_msg))
        logger.error("Brand Answer Agent: Failed to generate brand answer. Returning error.")
        return {"error": error_msg}, state # Return error structure

    state.active_agent = "brand_answer"
    # state.history.append(("user", user_input))  # Avoid double logging user input
    # The response is added to history below in the main english_agent if no top-level error
    logger.info("Brand Answer Agent: Finished.")
    # Ensure consistent return type (dict)
    return {"response": response.content}, state # Return success with response

# --- LLM-based Intent Detection and Routing ---
def llm_intent_router(state: AgentState, user_input: str) -> (str, AgentState):
    """
    Uses the LLM to classify intent from user input and route to the appropriate agent.
    Does NOT perform entity extraction.
    Returns the response and updated state from the routed agent.
    """
    logger.info(f"Intent Router: Starting intent classification for input: '{user_input}'.")
    # Prompt for intent and argument extraction
    router_prompt_template = """
    You are an AI assistant for a beauty and skincare store. Your task is to analyze the user's input and determine their primary intent to route them to the correct specialized agent.

    Based on the user's latest input and the conversation history (if available), classify the user's intent.

    Possible intents:
    - recommend: User wants product recommendations or to search for products.
    - review_explanation: User wants to know how a product has worked for others, or wants review-backed explanations.
    - brand_info: User wants to know about the brand's philosophy, sustainability, or practices.
    - search: User is exploring or asking general questions about products, or their intent is unclear.

    Respond ONLY with a JSON object containing a single key 'intent' and its value (one of the possible intents).

    Conversation History (most recent first, up to 2 turns):
    {history}

    User input: {input}

    JSON:
    """
    router_prompt = PromptTemplate(
        input_variables=["input", "history"],
        template=router_prompt_template
    )

    import json
    router_output = None # Initialize router_output to None
    intent = "search" # Default intent
    # arguments = {} # Initialize arguments as empty - removed as router doesn't extract args
    try:
        # Prepare prompt input
        prompt_input = {
            "input": user_input,
            "history": state.history[-4:] if len(state.history) > 4 else state.history # Include recent history
        }
        logger.debug(f"Intent Router: Prompt input: {prompt_input}")
        router_output = llm.invoke(router_prompt.format(**prompt_input))
        logger.debug(f"Intent Router: Raw LLM output: {router_output}") # Log raw output

        # Attempt to strip any leading/trailing whitespace and then parse
        cleaned_output = str(router_output.content).strip()
        # Handle cases where the LLM might output more than just JSON, e.g., in markdown code blocks
        if "```json" in cleaned_output:
            cleaned_output = cleaned_output.split("```json")[1].split("```" )[0].strip()
        elif "```" in cleaned_output:
            cleaned_output = cleaned_output.split("```" )[1].strip()

        # Further cleaning: try to find and extract the JSON object based on curly braces
        json_start = cleaned_output.find('{')
        json_end = cleaned_output.rfind('}') # Use rfind to find the last occurrence

        if json_start != -1 and json_end != -1 and json_end > json_start:
             cleaned_output = cleaned_output[json_start : json_end + 1]
             logger.debug(f"Intent Router: Extracted potential JSON block: {cleaned_output}")
        else:\
            # If no JSON block found, keep the cleaned output for potential string matching fallback
            logger.debug(f"Intent Router: No JSON block found, using cleaned output for fallback: {cleaned_output}")

        logger.debug(f"Intent Router: Final cleaned LLM output for parsing: {cleaned_output}") # Log cleaned output before json.loads

        router_json = json.loads(cleaned_output)
        intent = router_json.get("intent", "search")
        # Remove argument extraction from router
        # arguments = router_json.get("arguments", {})
        logger.info(f"Intent Router: Classified intent: {intent}")

    except json.JSONDecodeError as e:
        logger.error(f"Intent Router: Failed to decode JSON from LLM output. Error: {e}. Output was: {cleaned_output}", exc_info=True)
        # If JSON decode fails, check if the output string is a valid intent name.
        valid_intents = ["recommend", "review_explanation", "brand_info", "search"]
        if cleaned_output in valid_intents:
            intent = cleaned_output # Use the string output as the intent if it's valid
            logger.warning(f"Intent Router: LLM returned non-JSON intent string: '{intent}'. Using it directly.")
        else:
            intent = "search"  # Fallback intent if output is neither JSON nor a valid intent string
            logger.warning(f"Intent Router: LLM returned unexpected non-JSON output: '{cleaned_output}'. Falling back to search intent.")
    except Exception as e:
        # Fallback to default intent if parsing fails for other reasons
        logger.error(f"Intent Router: An unexpected error occurred during intent parsing. Error: {e}. Output was: {router_output}", exc_info=True)
        intent = "search"
        logger.warning("Intent Router: Unexpected error. Falling back to search intent.")

    state.intent = intent
    # Remove merging extracted arguments into state.entities
    # state.entities.update(arguments)
    logger.debug(f"Intent Router: Updated state intent: {state.intent}. State entities remain unchanged by router: {state.entities}")

    # Route to the appropriate agent
    if intent == "recommend":
        # Pass user_input and current state to the conversational_search_agent for entity extraction
        logger.info("Intent Router: Routing to conversational_search_agent with recommend intent.")
        return conversational_search_agent(state, user_input)  # conversational_search_agent handles its own NER
    elif intent == "review_explanation":
        # The reviews agent will need to extract the product name itself or rely on state
        logger.info("Intent Router: Routing to reviews_explanation_agent with review_explanation intent.")
        # Pass user_input to reviews agent so it can extract product
        return reviews_explanation_agent(state, user_input) # reviews_explanation_agent now takes user_input and extracts product
    elif intent == "brand_info":
        logger.info("Intent Router: Routing to brand_answer_agent with brand_info intent.")
        return brand_answer_agent(state, user_input)
    else:
        # Default to conversational search for 'search' intent or any unhandled intents
        logger.info("Intent Router: Routing to conversational_search_agent with default/search intent.")
        return conversational_search_agent(state, user_input)

# --- LangGraph Setup ---
def english_agent(text: str, state_dict: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Main entry point for the English Agent. Handles multi-turn, multi-agent conversations.
    Args:
        text: User input string
        state_dict: Optional dict representing the conversation state
    Returns:
        Dict with 'ai_message' and 'state' (for next turn) and optional list of 'product_ids'
    """
    logger.info(f"--- English Agent: Starting processing for input: '{text}' ---")
    state = AgentState.from_dict(state_dict or {})
    # Append current user input to history at the beginning of processing
    state.history.append(("user", text))
    logger.debug(f"Current state: {state.to_dict()}")
    try:
        # Route and get response from the appropriate agent
        result, new_state = llm_intent_router(state, text)

        # Check if the routed agent returned an error
        if isinstance(result, dict) and "error" in result:
            ai_message = result["error"]
            logger.info(f"--- English Agent: Routed agent returned an error. Responding: '{ai_message}' ---")
        elif isinstance(result, dict) and "response" in result:
            # Handle successful response from agent (expecting a dict with 'response')
            ai_message = result["response"]
            # Add the agent's successful response to the history here, as agents now return dicts
            # It might already be added within the agent, but doing it here ensures consistency
            # Let's check if the last history entry is the user's input before adding the agent response
            if state.history and state.history[-1][0] == "user":
                 # Find the agent response in new_state history and add it if not already there
                 agent_response_in_new_state = next((item[1] for item in new_state.history if item[0] == "agent"), None)
                 if agent_response_in_new_state and (not state.history or state.history[-1][1] != agent_response_in_new_state):
                      # Avoid adding duplicate if agent already added it
                     # However, given the agent changes, let's ensure agent responses are added here consistently
                     # Removing adding agent response in agents' success paths and adding here.
                     # Reverting previous edits where agent added response to history on success.
                     pass # Need to manually revert agent edits or rely on them adding to history
            # Reverting the history append in successful agent paths simplifies this.
            # Let's assume agents still add to history for now and clean up later if needed.
            # For now, just use the ai_message and new_state.
        
        # Add a case to handle recommendation agent's specific return structure
        elif isinstance(result, dict) and "product_ids" in result and "justification" in result:
            ai_message = result["justification"]
            # Note: The actual products will need to be handled by the caller/frontend,
            # but the justification is the textual part for the history/response.
            # logger.info(f"--- English Agent: Routed agent returned recommendations. Justification: '{ai_message}' ---")
            return {"ai_message": ai_message, "state": new_state.to_dict(), "product_ids": result["product_ids"]}
        # The new_state returned by the agent functions should now include the agent's response/error in history
        # Returning ai_message (string) and the state (dict)
        return {"ai_message": ai_message, "state": new_state.to_dict()} # Return user-facing string response and state
    except Exception as e:
        logger.exception(f"An unexpected error occurred in english_agent for input: {text}. Error: {e}")
        # Handle unexpected errors at the top level
        error_response = "Sorry, I encountered a critical internal error. Please try again."
        # Add the critical error to history
        state.history.append(("agent", error_response))
        logger.error("--- English Agent: Encountered critical unexpected error ---")
        return {"ai_message": error_response, "state": state.to_dict()}  # Return a dict structure for response with error message and state
