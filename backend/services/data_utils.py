import os
import re
import logging
import pandas as pd
from rapidfuzz import process, fuzz
# Global variable to hold the product catalog DataFrame
PRODUCT_CATALOG_DATA: pd.DataFrame = pd.DataFrame()

def set_product_catalog_data(data=None):
    """Set the global product catalog data."""
    global PRODUCT_CATALOG_DATA
    if data is not None:
        PRODUCT_CATALOG_DATA = data
    else:
        PRODUCT_CATALOG_DATA = load_products_catalog()

def get_product_catalog_data() -> pd.DataFrame:
    """Get the global product catalog data."""
    return PRODUCT_CATALOG_DATA

logger = logging.getLogger(__name__)

CATALOG_PATH = os.path.join(os.path.dirname(__file__), "..", "skincare catalog.xlsx")

def get_catalog_categories_and_skin_concerns_from_source():
    """
    Loads the skincare catalog Excel file and returns a set of product names, categories, and tags.
    This is used to get available options for the agent.
    Note: This function reads the source file, not the Pinecone index.
    """
    try:
        # Use the shared data if available, otherwise load from file
        df = get_product_catalog_data()
        if df is None or df.empty:
            df = pd.read_excel(CATALOG_PATH).dropna()
        # Convert all values to strings and remove whitespace, then get uniques
        categories = set(str(p).strip().lower() for p in df["category"].dropna().unique())
        skin_concerns = set()
        for tags_str in df["tags"].dropna().unique():
            tag_list = [t.strip().lower() for t in str(tags_str).split('|') if t.strip()]
            skin_concerns.update(tag_list)
        ingredients = set()
        for ingredient in df['top_ingredients'].str.split('; ').explode().unique():
            ingredients.update(ingredient.lower())
        logger.info(f"Loaded {len(categories)} categories and {len(skin_concerns)} skin concerns and {len(ingredients)} ingredients from catalog source.")
        return sorted(list(categories)), sorted(list(skin_concerns)), sorted(list(ingredients))
    except FileNotFoundError:
        logger.error(f"Catalog source file not found at {CATALOG_PATH}. Cannot extract categories and skin concerns.")
        return [], [], []
    except KeyError as e:
        logger.error(f"Catalog source file is missing expected column: {e}.")
        return [], [], []
    except Exception as e:
        logger.exception(f"Error loading categories and skin concerns from catalog source: {e}.")
        return [], [], []

def load_products_catalog():
    """
    Loads the skincare catalog Excel file and returns a DataFrame.
    This is used for catalog-related operations.
    """
    try:
        df = pd.read_excel(CATALOG_PATH).dropna()
        # Clean column names: keep only alphabets and underscores, trim whitespace
        df.columns = [re.sub(r'[^a-zA-Z_]', '', col).strip().lower() for col in df.columns]

        # Store the DataFrame with cleaned column names
        PRODUCT_CATALOG_DATA = df.set_index('product_id')
        logger.info(f"Successfully loaded {len(df)} products into DataFrame from catalog.")
        logger.info(f"Cleaned column names: {list(df.columns)}")
        return PRODUCT_CATALOG_DATA
    except FileNotFoundError:
        logger.error(f"Product catalog file not found at {CATALOG_PATH}. The /api/products endpoint will return empty results.")
        PRODUCT_CATALOG_DATA = pd.DataFrame() # Assign an empty DataFrame if file is missing
        return PRODUCT_CATALOG_DATA
    except Exception as e:
        logger.exception(f"Error loading product catalog from {CATALOG_PATH}: {e}")
        PRODUCT_CATALOG_DATA = pd.DataFrame() # Assign an empty DataFrame if loading fails
        return PRODUCT_CATALOG_DATA

def load_catalog_product_id_name(df=None):
    """
    Loads the skincare catalog Excel file and returns a dictionary mapping product_id to product name.
    This is used for product name extraction and linking.
    """
    try:
        if df is None:
            df = get_product_catalog_data()
        if df is None or df.empty:
            df = pd.read_excel(CATALOG_PATH)
        logger.info(f"Loaded {len(df)} products from catalog.")
        return df['name'].to_dict()
    except FileNotFoundError:
        logger.error(f"Catalog file not found at {CATALOG_PATH}")
        return {}
    except KeyError:
        logger.error(f"Catalog file is missing 'product_id' or 'name' column at {CATALOG_PATH}")
        return {}
    except Exception as e:
        logger.exception(f"Error loading catalog products from {CATALOG_PATH}: {e}")
        return {}

def extract_product_from_text(text, threshold=80):
    """
    Uses fuzzy matching to find a product name from the catalog within a given text
    and returns the corresponding product ID.

    Args:
        text (str): The input text to search within.
        threshold (int): The minimum fuzzy matching score (0-100) to consider a match.

    Returns:
        str: The ID of the matched product, or None if no match is found above the threshold.
    """
    global PRODUCT_CATALOG_DATA
    if not text:
        return None
    
    # Load catalog products if not provided
    if PRODUCT_CATALOG_DATA is None:
        PRODUCT_CATALOG_DATA = get_product_catalog_data()
    
    if PRODUCT_CATALOG_DATA.empty:
        logger.error("No catalog products loaded. Cannot perform fuzzy product extraction.")
        return None
    
    # Create a list of product names (choices) for fuzzy matching
    # and a mapping from lowercased name back to original ID
    product_id_names = load_catalog_product_id_name(PRODUCT_CATALOG_DATA)
    product_names_lower_to_id = {}
    choices_for_fuzzy_match = []

    for product_id, product_name in product_id_names.items():
        product_names_lower_to_id[product_name.lower()] = product_id
        choices_for_fuzzy_match.append(product_name.lower())
    
    try:
        match, score, _ = process.extractOne(text.lower(), choices_for_fuzzy_match, scorer=fuzz.partial_token_set_ratio)
        if score >= threshold:
            logger.debug(f"Fuzzy matched product '{match}' with score {score} from text: {text[:50]}...")
            return product_names_lower_to_id.get(match)
        logger.debug(f"No fuzzy match found for text: {text[:50]}...")
        return None
    except Exception as e:
        logger.error(f"Error during fuzzy product extraction from text: {text[:50]}... Error: {e}")
        return None

# Cache these at startup from the source file
set_product_catalog_data()
AVAILABLE_CATEGORIES, AVAILABLE_SKIN_CONCERNS, AVAILABLE_INGREDIENTS = get_catalog_categories_and_skin_concerns_from_source()