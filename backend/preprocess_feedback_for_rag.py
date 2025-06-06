import os
import re
import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from rapidfuzz import process, fuzz
import logging

# Pinecone imports
from pinecone import Pinecone, ServerlessSpec
from langchain_cohere import CohereEmbeddings

from dotenv import load_dotenv

load_dotenv()
# --- Config ---
FEEDBACK_PATH = os.path.join(os.path.dirname(__file__), "CustomerFeedback.xlsx")
CATALOG_PATH = os.path.join(os.path.dirname(__file__), "skincare catalog.xlsx")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "everglow-feedback") # Using a different index name for feedback
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# --- Logging setup ---
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Step 1: Load Catalog for Product Linking ---
def load_catalog_products(path):
    """
    Loads the skincare catalog Excel file and returns a set of product names (lowercase) for linking.
    """
    try:
        df = pd.read_excel(path)
        # Use lowercase for matching
        # product_names = set(str(p).strip().lower() for p in df["name"].dropna().unique())
        # TODO: Check duplicate product ids
        logger.info(f"Loaded {len(df)} product_ids names from catalog.")
        return df.set_index('product_id')['name'].to_dict()
    except FileNotFoundError:
        logger.error(f"Catalog file not found at {path}")
        raise
    except KeyError:
        logger.error(f"Catalog file is missing 'name' column at {path}")
        raise
    except Exception as e:
        logger.exception(f"Error loading catalog products from {path}: {e}")
        raise

# --- Utility: Normalize star ratings ---
def normalize_rating(rating):
    """
    Normalizes star ratings from various formats to 'X out of 5'.
    """
    rating_str = str(rating).strip()
    if not rating_str:
        return "N/A"
    # Handle star strings like "★★★☆☆"
    if set(rating_str) <= set("★☆") and len(rating_str) == 5:
        stars = rating_str.count("★")
        return f"{stars} out of 5"
    # Handle numeric or "4/5" style
    try:
        rating_num = int(float(rating_str.split("/")[0]))
        if 0 <= rating_num <= 5:
             return f"{rating_num} out of 5"
    except Exception:
        pass # Fallback to returning original string if parsing fails

    logger.warning(f"Could not normalize rating: {rating_str}. Returning original.")
    return rating_str

# --- Step 2: Preprocess Reviews Sheet ---
def preprocess_reviews(df_reviews, catalog_products):
    """
    Converts review rows into LangChain Documents with metadata.
    """
    docs = []
    for index, row in df_reviews.iterrows():
        try:
            reviewer = str(row.get("Reviewer", "")).strip()
            product_name = str(row.get("Product", "")).strip()
            review = str(row.get("Review", "")).strip()
            rating = normalize_rating(row.get("Rating", ""))
            # Link to catalog
            product_id = extract_product_from_text(product_name, catalog_products) or ""
            # Build document text
            text = f"Review for Product ID: {product_id}\nName: {product_name}: {review}\nRating: {rating}\nReviewer: {reviewer}"
            metadata = {
                "source": "review",
                "source_id": f"review_{index}", # Add original row index for potential debugging/tracking
                "reviewer": reviewer.lower(),
                "product_id": product_id,
                "rating": rating,
                "product_in_catalog": bool(product_id),
            }
            docs.append(Document(page_content=text, metadata=metadata))
        except Exception as e:
             logger.error(f"Error processing review row {index}: {e}")
             continue # Skip this row and continue with the next

    logger.info(f"Processed {len(docs)} review documents.")
    return docs

# --- Utility: Fuzzy match product in text ---
def extract_product_from_text(text, catalog_products: dict, threshold=80):
    """
    Uses fuzzy matching to find a product name from the catalog within a given text
    and returns the corresponding product ID.

    Args:
        text (str): The input text to search within.
        catalog_products (dict): A dictionary where keys are product IDs and values are product names.
                                 Example: {'prod_1': 'HydraCloud Daily Gel-Cream SPF 30'}
        threshold (int): The minimum fuzzy matching score (0-100) to consider a match.

    Returns:
        str: The ID of the matched product, or None if no match is found above the threshold.
    """
    if not text or not catalog_products:
        return None
    # Create a list of product names (choices) for fuzzy matching
    # and a mapping from lowercased name back to original ID
    product_names_lower_to_id = {}
    choices_for_fuzzy_match = []

    for product_id, product_name in catalog_products.items():
        # cleaned_product_name = re.sub(r'[^\w\s]', '', product_name).lower()
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

# --- Step 3: Preprocess Customer Support Tickets Sheet ---
def preprocess_support_tickets(df_tickets, catalog_products):
    """
    Converts support ticket rows into LangChain Documents with metadata.
    """
    docs = []
    for index, row in df_tickets.iterrows():
        try:
            ticket_id = str(row.get("Ticket ID", "")).strip()
            customer_msg = str(row.get("Customer Message", "")).strip()
            support_resp = str(row.get("Support Response", "")).strip()
            # Try to extract product from customer message or support response
            product_id = extract_product_from_text(customer_msg, catalog_products) or extract_product_from_text(support_resp, catalog_products) or ""
            in_catalog = bool(product_id) # True if a product was extracted
            text = f"Product ID:{product_id}\nCustomer Support Ticket {ticket_id}:\nQ: {customer_msg}\nA: {support_resp}"
            metadata = {
                "source": "support_ticket",
                "source_id": ticket_id,
                "product_id": product_id,
                "product_in_catalog": in_catalog,
            }
            docs.append(Document(page_content=text, metadata=metadata))
        except Exception as e:
             logger.error(f"Error processing ticket row {index}: {e}")
             continue # Skip this row and continue with the next

    logger.info(f"Processed {len(docs)} support ticket documents.")
    return docs

# --- Step 4: Generate Embeddings and Upsert to Pinecone Vector Store ---
def build_and_upsert_pinecone_feedback(docs):
    """
    Generates embeddings using Cohere and upserts documents to a Pinecone index.
    """
    # 1. Generate embeddings using a 1024-dimensional model
    if not COHERE_API_KEY:
        logger.error("COHERE_API_KEY must be set in environment variables to use Cohere embeddings.")
        raise ValueError("COHERE_API_KEY must be set in environment variables to use Cohere embeddings.")
    try:
        embeddings_model = CohereEmbeddings(cohere_api_key=COHERE_API_KEY, model="embed-english-light-v2.0")
        texts = [doc.page_content for doc in docs]
        metadatas = [doc.metadata for doc in docs]
        # Generate unique IDs for each document, perhaps combining source and row index
        ids = [f"{meta.get('source', 'unknown')}-{meta.get('row_index', i)}" for i, meta in enumerate(metadatas)]
        vectors = embeddings_model.embed_documents(texts)
        assert len(vectors) == len(ids) == len(metadatas)
        logger.info(f"Generated {len(vectors)} embeddings with dimension {len(vectors[0])}.")
    except Exception as e:
         logger.exception(f"Error generating embeddings: {e}")
         raise

    # 2. Initialize Pinecone client
    if not PINECONE_API_KEY:
        logger.error("PINECONE_API_KEY must be set in environment variables.")
        raise ValueError("PINECONE_API_KEY must be set in environment variables.")
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
    except Exception as e:
         logger.exception(f"Error initializing Pinecone client: {e}")
         raise

    # Check index existence and dimension
    expected_dimension = len(vectors[0])
    if PINECONE_INDEX_NAME in [idx.name for idx in pc.list_indexes()]:
        try:
            index_description = pc.describe_index(PINECONE_INDEX_NAME)
            existing_dimension = index_description.dimension
            if existing_dimension != expected_dimension:
                 logger.error(f"Pinecone index dimension mismatch. Existing: {existing_dimension}, Embedding dimension: {expected_dimension}")
                 raise ValueError(f"Pinecone index '{PINECONE_INDEX_NAME}' has dimension {existing_dimension}, but embeddings are dimension {expected_dimension}. Please delete the index and try again.")
            logger.info(f"Pinecone index '{PINECONE_INDEX_NAME}' exists with matching dimension {existing_dimension}.")
        except Exception as e:
             logger.exception(f"Error describing Pinecone index {PINECONE_INDEX_NAME}: {e}")
             raise
    else:
        # Create index if it doesn't exist
        try:
            logger.info(f"Pinecone index '{PINECONE_INDEX_NAME}' does not exist. Creating with dimension {expected_dimension}.")
            pc.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=expected_dimension,
                metric="cosine", # Assuming cosine similarity
                spec=ServerlessSpec(
                    cloud=PINECONE_CLOUD,
                    region=PINECONE_REGION
                )
            )
            logger.info(f"Created new Pinecone index: {PINECONE_INDEX_NAME} with dimension {expected_dimension}.")
        except Exception as e:
             logger.exception(f"Error creating Pinecone index {PINECONE_INDEX_NAME}: {e}")
             raise

    # 3. Get index object
    try:
        index = pc.Index(PINECONE_INDEX_NAME)
        logger.info(f"Connected to Pinecone index: {PINECONE_INDEX_NAME}")
    except Exception as e:
         logger.exception(f"Error connecting to Pinecone index {PINECONE_INDEX_NAME}: {e}")
         raise e

    # 4. Prepare upsert data
    upsert_data = [
        {"id": id_, "values": vector, "metadata": metadata}
        for id_, vector, metadata in zip(ids, vectors, metadatas)
    ]

    # 5. Upsert to Pinecone with batching
    logger.info(f"Starting upsert of {len(upsert_data)} vectors to Pinecone index: {PINECONE_INDEX_NAME}")
    batch_size = 100
    for i in range(0, len(upsert_data), batch_size):
        batch = upsert_data[i:i + batch_size]
        try:
            index.upsert(vectors=batch)
            logger.info(f"Upserted batch {i // batch_size + 1} of {len(upsert_data) // batch_size + 1} to {PINECONE_INDEX_NAME}")
        except Exception as e:
             logger.error(f"Error upserting batch {i // batch_size + 1} to {PINECONE_INDEX_NAME}: {e}")
             # Depending on requirements, you might want to raise the exception
             # or log and continue. Here, we log and continue to process other batches.
             pass

    logger.info("Upsert complete.")

if __name__ == "__main__":
    try:
        logger.info("Starting customer feedback preprocessing for RAG.")
        catalog_products = load_catalog_products(CATALOG_PATH)
        xls = pd.ExcelFile(FEEDBACK_PATH)
        df_reviews = pd.read_excel(xls, sheet_name="Reviews").dropna()
        df_tickets = pd.read_excel(xls, sheet_name="Customer Support Tickets").dropna()
        docs = preprocess_reviews(df_reviews, catalog_products) + preprocess_support_tickets(df_tickets, catalog_products)
        build_and_upsert_pinecone_feedback(docs)
        logger.info("Customer feedback preprocessing for RAG complete.")
    except FileNotFoundError as e:
        logger.error(f"Required input file not found: {e}")
    except ValueError as e:
        logger.error(f"Configuration or data error: {e}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred during feedback preprocessing: {e}")

# TODO: Add error handling, logging, and support for incremental updates.
# TODO: Document the expected Excel columns and add validation. 