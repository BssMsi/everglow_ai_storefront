"""
english_agent.py
Module for English Agent logic (e.g., LLM or custom logic) using LangGraph for multi-turn, multi-agent conversations.
"""

from typing import Dict, Any, Optional
import logging
from .state import AgentState
from .router import llm_intent_router

logger = logging.getLogger(__name__)

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
        # Add a case to handle recommendation agent's specific return structure
        elif isinstance(result, dict) and "product_ids" in result and "justification" in result:
            ai_message = result["justification"]
            # Note: The actual products will need to be handled by the caller/frontend,
            # but the justification is the textual part for the history/response.
            return {"ai_message": ai_message, "state": new_state.to_dict(), "product_ids": result["product_ids"]}
        # The new_state returned by the agent functions should now include the agent's response/error in history
        # Returning ai_message (string) and the state (dict)
        return {"ai_message": ai_message, "state": new_state.to_dict()}  # Return user-facing string response and state
    except Exception as e:
        logger.exception(f"An unexpected error occurred in english_agent for input: {text}. Error: {e}")
        # Handle unexpected errors at the top level
        error_response = "Sorry, I encountered a critical internal error. Please try again."
        # Add the critical error to history
        state.history.append(("agent", error_response))
        logger.error("--- English Agent: Encountered critical unexpected error ---")
        return {"ai_message": error_response, "state": state.to_dict()}  # Return a dict structure for response with error message and state
