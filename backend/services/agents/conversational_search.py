import copy
import json
import logging
from ..state import AgentState
from ..prompts import conversational_search_llm
from ..data_utils import AVAILABLE_CATEGORIES
from .recommendation import recommendation_agent

logger = logging.getLogger(__name__)

def conversational_search_agent(state: AgentState, user_input: str) -> (dict, AgentState):
    """
    Handles conversational search, uses agent-specific LLM for NER, asks follow-up questions, 
    and hands off to Recommendation Agent when ready.
    Returns a dict with either a follow-up question or recommendation results.
    """
    logger.info("Conversational Search Agent: Started.")
    entities = copy.deepcopy(state.entities) # Initialize entities at the start

    # Format chat history and current entities for the prompt
    formatted_history = "\n".join([f"User: {turn[0]}\nAgent: {turn[1]}" for turn in state.history])
    current_entities_json = json.dumps(state.entities if isinstance(state.entities, dict) else state.entities.to_dict())
    logger.info(f"Conversational Search Agent: Formatted history: {formatted_history}")
    logger.info(f"Conversational Search Agent: Current entities JSON: {current_entities_json}")
    # 1. Use agent-specific LLM to extract entities (NER) and match category with confidence
    try:
        ner_input_payload = {
            "user_input": user_input,
            "current_entities_json": current_entities_json,
            "chat_history_formatted": formatted_history
        }
        logger.debug(f"Conversational Search Agent: NER input payload: {ner_input_payload}")
        ner_output = conversational_search_llm.invoke(ner_input_payload)
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
            entities.update(updated_entities)  # Use cleaned_output, LLM provides the full new entity state

            logger.info(f"Conversational Search Agent: NER processed entities: {cleaned_output}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during LLM NER output parsing. Error: {e}. Output was: {ner_output_content}", exc_info=True) # Log ner_output_content
            # Return error immediately on other parsing failures
            confidence = 0
            # Return error immediately on other parsing failures
            error_msg = "Sorry, an unexpected error occurred while processing the product category."
            state.history.append(("agent", error_msg))
            logger.error(f"Conversational Search Agent: Unexpected error during NER parsing. Returning error. cleaned_output={cleaned_output if 'cleaned_output' in locals() else 'undefined'}")
            return {"error": error_msg}, state # Return error structure

    except Exception as e:
        logger.exception(f"Error running conversational search LLM for NER: {e}")
        # Return error immediately on LLM invocation failure
        error_msg = "Sorry, I encountered an error while trying to understand your request."
        state.history.append(("agent", error_msg))
        logger.error(f"Conversational Search Agent: LLM invocation error during NER. Returning error. ner_output={ner_output if 'ner_output' in locals() else 'undefined'}")
        return {"error": error_msg}, state # Return error structure

    # If NER was successful and 'entities' (local copy) was updated:
    state.entities = entities # Ensure the state object reflects these updated entities.

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