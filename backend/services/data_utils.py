import os
import logging
import pandas as pd

logger = logging.getLogger(__name__)

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