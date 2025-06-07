import json
import logging
from langchain.prompts import PromptTemplate
from ..state import AgentState
from ..config import llm, get_cohere_embeddings, get_feedback_index
from ..prompts import reviews_llm

logger = logging.getLogger(__name__)

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