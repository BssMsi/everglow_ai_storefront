import logging
from ..state import AgentState
from ..prompts import brand_llm

logger = logging.getLogger(__name__)

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
