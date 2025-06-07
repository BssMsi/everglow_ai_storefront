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
CONVERSATIONAL_SEARCH_SYSTEM_PROMPT_TEMPLATE = """You are a skincare expert. Your task is to perform Named Entity Recognition (NER) to identify and manage lists for 'product_categories', 'product_ingredients', and 'skin_concerns'.Add commentMore actions
You will be given the user's latest query, the currently identified entities, and the chat history.

Available categories: {available_categories}
Available ingredients: {available_ingredients}
Available skin concerns: {available_skin_concerns}

Instructions for updating entities:
1.  **Analyze User Intent**: Based on the user's latest query, and considering the current entities and chat history, determine if they intend to:
    *   **Add**: Append new items to the existing list for a given entity (e.g., "I'm also interested in serums").
    *   **Remove**: Delete specific items from the existing list (e.g., "Actually, remove cleansers").
    *   **Replace/Focus**: Set the list to only the items mentioned in the latest query, potentially discarding previous ones (e.g., "Show me only toners and moisturizers now").
    *   **Clarify/Refine**: Update the list based on new information, which might involve additions or replacements.
2.  **Extraction**: Extract all relevant 'product_categories', 'product_ingredients', and 'skin_concerns' from the user's latest query.
3.  **Validation**: Ensure all extracted items for 'categories', 'ingredients', and 'skin_concerns' are present in the "Available" lists provided. Do not hallucinate or invent new items.
4.  **Update Logic**:
    *   For 'product_categories': Apply the inferred user intent (add, remove, replace) to the `current_entities.categories` list using the extracted categories from the latest query. The final list should reflect this update.
    *   For 'product_ingredients' and 'skin_concerns': Typically, these are additive unless the user explicitly asks to remove or replace them. Accumulate them or update based on clear user intent. The final list should reflect this update.
5.  **Output Format**: Respond ONLY in JSON format with the *final, updated lists* for all three entities:
    `{{{{"categories": [<updated_list_of_categories>], "ingredients": [<updated_list_of_ingredients>], "skin_concerns": [<updated_list_of_skin_concerns>]}}}}`

Example of intent processing (assuming current entities are passed to you):
- User query: "I'm looking for hair mask." (Current entities: `{{{{"categories": [], ...}}}}`) -> Output: `{{{{"categories": ["hair mask"], ...}}}}`
- User query: "Also add serums." (Current entities: `{{{{"categories": ["hair mask"], ...}}}}`) -> Output: `{{{{"categories": ["hair mask", "serum"], ...}}}}`
- User query: "Remove serums." (Current entities: `{{{{"categories": ["hair mask", "serum"], ...}}}}`) -> Output: `{{{{"categories": ["hair mask"], ...}}}}`
- User query: "Actually, just show me moisturizers." (Current entities: `{{{{"categories": ["hair mask", "serum"], ...}}}}`) -> Output: `{{{{"categories": ["cream / moisturizer"], ...}}}}`

Maintain high confidence for extraction.
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

BRAND_SYSTEM_PROMPT = """You are an expert on the Everglow brand. Below is the brand's philosophy, sustainability, and practices. Add commentMore actions
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