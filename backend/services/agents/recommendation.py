import logging
from typing import Dict, Any
from langchain.prompts import PromptTemplate
from ..state import AgentState
from ..config import get_cohere_embeddings, get_catalog_index
from ..prompts import recommendation_llm

logger = logging.getLogger(__name__)

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
            top_k=10,  # Get top 5 results
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
        return {"response": response}, state # Return success with empty products and message

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
        products_text = "---\n".join([f"{i+1}. Name: {p['name']}\nTop Ingredients: {p['top_ingredients']}\nTags: {p['tags']}" for i, p in enumerate(products)])
        logger.debug(f"Recommendation Agent: Justification prompt input: {justification_prompt.format(query=user_input, products=products_text)}")
        justification_response = recommendation_llm.invoke({
            "input": justification_prompt.format(query=user_input, products=products_text)
        })
        justification = justification_response.content
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
    return {"product_ids": product_ids, "justification": justification}, state