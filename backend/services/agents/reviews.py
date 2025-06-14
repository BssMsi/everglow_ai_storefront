import json
import logging
from langchain.prompts import PromptTemplate
from ..state import AgentState
from ..config import llm, get_cohere_embeddings, get_feedback_index
from ..prompts import reviews_llm
from ..data_utils import extract_product_from_text, get_product_catalog_data

logger = logging.getLogger(__name__)

def reviews_explanation_agent(state: AgentState, user_input: str) -> (str, AgentState):
    """
    Generates embeddings for the user query/product question, queries the Pinecone feedback index for relevant reviews, and uses agent-specific LLM to answer with review-backed explanations.
    Now also handles product name extraction if not already in state.
    """
    logger.info(f"Reviews Explanation Agent: Started with input: {user_input}")

    # --- 1. Extract or confirm Product Name ---
    product_id = state.entities.get("review_product_id") # Check if product ID is already in state

    if not product_id:
        # If not in state, attempt to extract from user_input using fuzzy matching
        try:
            extracted_product_id = extract_product_from_text(user_input)
            if extracted_product_id:
                product_id = extracted_product_id
                state.entities["review_product_id"] = product_id
                logger.info(f"Reviews Explanation Agent: Extracted product ID from fuzzy matching: {product_id}")
            # else:
            #     # Fallback to LLM extraction if fuzzy matching fails
            #     extraction_prompt_template = """
            #     Given the user's input, identify the specific product name they are asking about for reviews.
            #     If a product name is mentioned, extract it. If not, return null.

            #     User input: {user_input}

            #     Respond ONLY with a JSON object like: {{"product_name": <product name or null>}}
            #     """
            #     extraction_prompt = PromptTemplate(
            #         input_variables=["user_input"],
            #         template=extraction_prompt_template
            #     )
            #     extracted_product_name = None
            #     try:
            #         logger.debug(f"Reviews Explanation Agent: Product extraction prompt input: {extraction_prompt.format(user_input=user_input)}")
            #         extraction_output = llm.invoke(extraction_prompt.format(user_input=user_input))
            #         logger.debug(f"Reviews Explanation Agent: Product extraction raw output: {extraction_output}")
            #         cleaned_output = extraction_output.content.strip()
            #         if "```json" in cleaned_output:
            #              cleaned_output = cleaned_output.split("```json")[1].split("```")[0].strip()
            #         elif "```" in cleaned_output:
            #              cleaned_output = cleaned_output.split("```")[1].strip()

            #         logger.debug(f"Reviews Explanation Agent: Product extraction cleaned output: {cleaned_output}")
            #         extraction_json = json.loads(cleaned_output)
            #         extracted_product_name = extraction_json.get("product_name")
            #         logger.info(f"Reviews Explanation Agent: Extracted product name from LLM: {extracted_product_name}")

            #         if extracted_product_name:
            #              product = extracted_product_name
            #              state.entities["product_name"] = product # Store in state for future turns

            #     except json.JSONDecodeError as e:
            #         logger.error(f"Failed to decode JSON from product extraction LLM output. Error: {e}. Output was: {cleaned_output}", exc_info=True)
            #         # If JSON decode fails, it means the LLM likely gave a conversational response.
            #         # Use this response as a clarifying question.
            #         response = cleaned_output
            #         state.active_agent = "reviews_explanation" # Stay in reviews agent context or clarify
            #         state.followup_questions = [response] # Use the non-JSON response as a followup
            #         # Do NOT update product in entities, as extraction failed
            #         state.history.append(("agent", response))
            #         logger.warning("Reviews Explanation Agent: LLM returned non-JSON output during product extraction. Using it as a clarifying question.")
            #         return {"response": response}, state # Return the conversational response
            #     except Exception as e:
            #         logger.exception(f"Error during product name extraction: {e}")
            #         error_msg = "Sorry, an error occurred while trying to identify the product you're asking about for reviews."
            #         state.history.append(("agent", error_msg))
            #         logger.error("Reviews Explanation Agent: Unexpected error during product extraction. Returning error.")
            #         return {"error": error_msg}, state
        except Exception as e:
            logger.exception(f"Error during fuzzy product extraction: {e}")

    if not product_id:
        # If product still not identified, ask user for clarification
        response = "Which product would you like to know about? Please specify the product name." # Agent response
        state.active_agent = "conversational_search" # Or a dedicated clarification state
        state.followup_questions = [response]
        # state.history.append(("user", user_input)) # Avoid double logging
        state.history.append(("agent", response))
        logger.warning("Reviews Explanation Agent: No product name found. Asking for clarification.")
        # Returning a dictionary like other agents for consistency, even if just a response
        return {"response": response}, state

    # Product name or ID is identified, proceed with review search
    logger.info(f"Reviews Explanation Agent: Proceeding with reviews search for product: {product_id}")

    embeddings_model = get_cohere_embeddings()
    feedback_index = get_feedback_index()

    # 2. Generate embedding for the query (user input + product)
    query_text = f"Reviews and feedback for product: {product_id}. User question: {user_input}" # Use full user_input as context for query
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

    # 3. Build metadata filter (filter by product name or ID if available)
    metadata_filter = {}
    if product_id:
        metadata_filter["product_id"] = product_id
        logger.debug(f"Reviews Explanation Agent: Adding product_id filter for feedback search: {metadata_filter['product_id']}")

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
        logger.info(f"Reviews Explanation Agent: No feedback found for product: {product_id}")
        response = f"I couldn't find any reviews or feedback for {product_id}. Is there anything else I can help with?"  # Agent response
        state.history.append(("agent", response))
        return {"response": response}, state # Return success with message

    # Extract text content from metadata
    feedback_texts = []
    for match in results:
        # Get the full text from metadata
        text = match.metadata.get('text')
        if text:
            feedback_texts.append(str(text))
    
    # Handle case where no valid text content is found
    if not feedback_texts:
        logger.warning(f"Reviews Explanation Agent: No valid text content found in metadata for product: {product_id}")
        response = f"I found some reviews for {product_id}, but couldn't extract the text content. Please try again later."
        state.history.append(("agent", response))
        return {"response": response}, state
    
    feedback_context = "\n---\n".join(feedback_texts)
    logger.debug(f"Reviews Explanation Agent: Feedback context for LLM: {feedback_context[:200]}...")

    # 6. Use agent-specific LLM to answer with review-backed explanations
    review_prompt_template = """
    Given the following customer feedback and reviews for a product, summarize the key points and address the user's question.
    Cite specific feedback points where possible.

    Product: {product}
    User Question: {user_question}
    Other Customers Feedback:
    {feedback_context}

    Answer:
    """
    review_prompt = PromptTemplate(
        input_variables=["product", "user_question", "feedback_context"],
        template=review_prompt_template
    )

    try:
        df = get_product_catalog_data()
        user_question = user_input # Use original user input as the question context
        product = df.loc[product_id].to_dict() # Use product name if available
        logger.debug(f"Reviews Explanation Agent: Review prompt input: {review_prompt.format(product=product, user_question=user_question, feedback_context=feedback_context[:200] + '...')}")
        response = reviews_llm.invoke({
            "input": review_prompt.format(
                product=product,
                user_question=user_question,
                feedback_context=feedback_context
            )
        })
    except Exception as e:
        logger.exception(f"Error generating review explanation: {e}")
        error_msg = "Sorry, I couldn't generate a review explanation for that product at this time."
        state.history.append(("agent", error_msg))
        logger.error("Reviews Explanation Agent: Failed to generate review explanation. Returning error.")
        return {"error": error_msg}, state

    state.active_agent = "reviews_explanation"
    # state.history.append(("user", user_input))  # Avoid double logging user input
    # The response is added to history below in the main english_agent if no top-level error
    # Ensure consistent return type (dict)
    return {"response": response.content}, state # Return success with response
