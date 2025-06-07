import json
import logging
from langchain.prompts import PromptTemplate
from .state import AgentState
from .config import llm
from .agents.conversational_search import conversational_search_agent
from .agents.reviews import reviews_explanation_agent
from .agents.brand import brand_answer_agent

logger = logging.getLogger(__name__)

# Router prompt template
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

def llm_intent_router(state: AgentState, user_input: str) -> (str, AgentState):
    """
    Uses the LLM to classify intent from user input and route to the appropriate agent.
    Does NOT perform entity extraction.
    Returns the response and updated state from the routed agent.
    """
    logger.info(f"Intent Router: Starting intent classification for input: '{user_input}'.")
    
    router_output = None
    intent = "search"  # Default intent
    
    try:
        # Prepare prompt input
        prompt_input = {
            "input": user_input,
            "history": state.history[-10:] if len(state.history) > 10 else state.history
        }
        logger.debug(f"Intent Router: Prompt input: {prompt_input}")
        router_output = llm.invoke(router_prompt.format(**prompt_input))
        logger.debug(f"Intent Router: Raw LLM output: {router_output}")

        # Attempt to strip any leading/trailing whitespace and then parse
        cleaned_output = str(router_output.content).strip()
        # Handle cases where the LLM might output more than just JSON
        if "```json" in cleaned_output:
            cleaned_output = cleaned_output.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned_output:
            cleaned_output = cleaned_output.split("```")[1].strip()

        # Further cleaning: try to find and extract the JSON object
        json_start = cleaned_output.find('{')
        json_end = cleaned_output.rfind('}')

        if json_start != -1 and json_end != -1 and json_end > json_start:
            cleaned_output = cleaned_output[json_start : json_end + 1]
            logger.debug(f"Intent Router: Extracted potential JSON block: {cleaned_output}")
        else:
            logger.debug(f"Intent Router: No JSON block found, using cleaned output for fallback: {cleaned_output}")

        logger.debug(f"Intent Router: Final cleaned LLM output for parsing: {cleaned_output}")

        router_json = json.loads(cleaned_output)
        intent = router_json.get("intent", "search")
        logger.info(f"Intent Router: Classified intent: {intent}")

    except json.JSONDecodeError as e:
        logger.error(f"Intent Router: Failed to decode JSON from LLM output. Error: {e}. Output was: {cleaned_output}", exc_info=True)
        # If JSON decode fails, check if the output string is a valid intent name
        valid_intents = ["recommend", "review_explanation", "brand_info", "search"]
        if cleaned_output in valid_intents:
            intent = cleaned_output
            logger.warning(f"Intent Router: LLM returned non-JSON intent string: '{intent}'. Using it directly.")
        else:
            intent = "search"
            logger.warning(f"Intent Router: LLM returned unexpected non-JSON output: '{cleaned_output}'. Falling back to search intent.")
    except Exception as e:
        logger.error(f"Intent Router: An unexpected error occurred during intent parsing. Error: {e}. Output was: {router_output}", exc_info=True)
        intent = "search"
        logger.warning("Intent Router: Unexpected error. Falling back to search intent.")

    state.intent = intent
    logger.info(f"Intent Router: Updated state intent: {state.intent}. State entities remain unchanged by router: {state.entities}")

    # Route to the appropriate agent
    if intent == "recommend":
        logger.info("Intent Router: Routing to conversational_search_agent with recommend intent.")
        return conversational_search_agent(state, user_input)
    elif intent == "review_explanation":
        logger.info("Intent Router: Routing to reviews_explanation_agent with review_explanation intent.")
        return reviews_explanation_agent(state, user_input)
    elif intent == "brand_info":
        logger.info("Intent Router: Routing to brand_answer_agent with brand_info intent.")
        return brand_answer_agent(state, user_input)
    else:
        logger.info("Intent Router: Routing to conversational_search_agent with default/search intent.")
        return conversational_search_agent(state, user_input)