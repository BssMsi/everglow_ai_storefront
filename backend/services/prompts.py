from typing import Dict, Any, Optional
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from .config import llm
from .data_utils import AVAILABLE_CATEGORIES, AVAILABLE_SKIN_CONCERNS, AVAILABLE_INGREDIENTS

def make_agent_llm(system_prompt_template_str: str,
                   human_prompt_template_str: str = "{input}",
                   template_format_kwargs: Optional[Dict[str, Any]] = None):
    formatted_system_prompt = system_prompt_template_str
    if template_format_kwargs:
        formatted_system_prompt = system_prompt_template_str.format(**template_format_kwargs)

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(formatted_system_prompt),
        HumanMessagePromptTemplate.from_template(human_prompt_template_str)
    ])
    return prompt | llm

# System prompts for each agent
CONVERSATIONAL_SEARCH_SYSTEM_PROMPT_TEMPLATE = """You are a skincare expert. Your task is to perform Named Entity Recognition (NER) to identify and manage lists for 'product_categories', 'product_ingredients', and 'skin_concerns'.
# ... (rest of the prompt)
"""

CONVERSATIONAL_SEARCH_HUMAN_PROMPT_TEMPLATE = """
User's latest query: {user_input}
Current identified entities: {current_entities_json}
Chat history (for context):
{chat_history_formatted}
"""

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
# ... (rest of the brand info)
"""

# Instantiate LLMChains for each agent
conversational_search_system_prompt_kwargs = {
    "available_categories": ", ".join(AVAILABLE_CATEGORIES),
    "available_ingredients": ", ".join(AVAILABLE_INGREDIENTS),
    "available_skin_concerns": ", ".join(AVAILABLE_SKIN_CONCERNS)
}

conversational_search_llm = make_agent_llm(
    CONVERSATIONAL_SEARCH_SYSTEM_PROMPT_TEMPLATE,
    CONVERSATIONAL_SEARCH_HUMAN_PROMPT_TEMPLATE,
    template_format_kwargs=conversational_search_system_prompt_kwargs
)
recommendation_llm = make_agent_llm(RECOMMENDATION_SYSTEM_PROMPT)
reviews_llm = make_agent_llm(REVIEWS_SYSTEM_PROMPT)
brand_llm = make_agent_llm(BRAND_SYSTEM_PROMPT)