import os
import pandas as pd
import logging
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from pinecone import Pinecone, ServerlessSpec

# Import CohereEmbeddings
from langchain_cohere import CohereEmbeddings

from dotenv import load_dotenv
from services.data_utils import load_products_catalog  # Import the load_catalog function from data_util

load_dotenv()
# --- Config ---
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "everglow-catalog")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")  # e.g., "us-east-1"
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")  # e.g., "aws"
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# --- Logging setup ---
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Step 1: Load and Clean Excel File ---


# --- Step 2: Format Each Product as a RAG Document ---
def make_documents(df):
    """
    Converts each product row into a LangChain Document for RAG using the correct columns.
    Splits tags on '|', lowercases and strips them, includes in text and metadata.
    Ensures all metadata values are primitives (str, int, float, bool, None).
    """
    docs = []
    for _, row in df.iterrows():
        # --- Build document text ---
        text = (
            f"Product ID: {row.get('product_id', '')}\n"
            f"Name: {row.get('name', '')}\n"
            f"Category: {row.get('category', '')}\n"
            f"Description: {row.get('description', '')}\n"
            f"Top Ingredients: {row.get('top_ingredients', '')}\n"
            f"Tags: {row.get('tags', '')}\n"
            f"Price (USD): {row.get('price (USD)', '')}\n"
            f"Margin (%): {row.get('margin (%)', '')}"
        )
        # --- Lowercase and Store all metadata ---
        metadata = {k: row[k] for k in row.index}
        metadata['tags'] = [t.strip().lower() for t in row.get('tags', '').split('|') if t.strip()] if row.get('tags', '') else []
        metadata['top_ingredients'] = [t.strip().lower() for t in row.get('top_ingredients', '').split('; ') if t.strip()] if row.get('top_ingredients', '') else []
        metadata['category'] = row.get('category', '').strip().lower()  # Ensure category is a string
        # Ensure all metadata values are primitives
        for k, v in metadata.items():
            if isinstance(v, (dict, set)):
                logger.warning(f"Non-primitive metadata value for key '{k}': {v}. Converting to string.")
                metadata[k] = str(v)
        try:
            docs.append(Document(page_content=text, metadata=metadata))
        except Exception as e:
            logger.error(f"Error creating Document for row {row.get('product_id', '[unknown]')}: {e}")
            continue
    logger.info(f"Created {len(docs)} documents for vector store.")
    return docs

# --- Step 3: Generate Embeddings and Store in Pinecone Vector Store ---
def build_and_upsert_pinecone(docs):
    # 1. Generate embeddings using a 1024-dimensional model
    if not COHERE_API_KEY:
        logger.error("COHERE_API_KEY must be set in environment variables to use Cohere embeddings.")
        raise ValueError("COHERE_API_KEY must be set in environment variables to use Cohere embeddings.")
    embeddings_model = CohereEmbeddings(cohere_api_key=COHERE_API_KEY, model="embed-english-light-v2.0")
    texts = [doc.page_content for doc in docs]
    metadatas = [doc.metadata for doc in docs]
    ids = [str(meta.get("product_id", i)) for i, meta in enumerate(metadatas)]
    vectors = embeddings_model.embed_documents(texts)
    assert len(vectors) == len(ids) == len(metadatas)

    # 2. Initialize Pinecone client
    if not PINECONE_API_KEY:
        logger.error("PINECONE_API_KEY must be set in environment variables.")
        raise ValueError("PINECONE_API_KEY must be set in environment variables.")
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Check index dimension if it exists
    if PINECONE_INDEX_NAME in [idx.name for idx in pc.list_indexes()]:
        index_description = pc.describe_index(PINECONE_INDEX_NAME)
        existing_dimension = index_description.dimension
        if existing_dimension != len(vectors[0]):
             logger.error(f"Pinecone index dimension mismatch. Existing: {existing_dimension}, Embedding dimension: {len(vectors[0])}")
             raise ValueError(f"Pinecone index '{PINECONE_INDEX_NAME}' has dimension {existing_dimension}, but embeddings are dimension {len(vectors[0])}. Please delete the index and try again.")

    if PINECONE_INDEX_NAME not in [idx.name for idx in pc.list_indexes()]:
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=len(vectors[0]),  # Use dimension from the chosen model
            metric="cosine",
            spec=ServerlessSpec(
                cloud=PINECONE_CLOUD,
                region=PINECONE_REGION
            )
        )
        logger.info(f"Created new Pinecone index: {PINECONE_INDEX_NAME} with dimension {len(vectors[0])}")

    # 3. Get index object
    index = pc.Index(PINECONE_INDEX_NAME)

    # 4. Prepare upsert data
    upsert_data = [
        {"id": id_, "values": vector, "metadata": metadata}
        for id_, vector, metadata in zip(ids, vectors, metadatas)
    ]

    # 5. Upsert to Pinecone
    logger.info(f"Upserting {len(upsert_data)} vectors to Pinecone index: {PINECONE_INDEX_NAME}")
    # Implement batching for larger datasets
    batch_size = 100
    for i in range(0, len(upsert_data), batch_size):
        batch = upsert_data[i:i + batch_size]
        index.upsert(vectors=batch)
        logger.info(f"Upserted batch {i // batch_size + 1} of {len(upsert_data) // batch_size + 1}")

    logger.info("Upsert complete.")

if __name__ == "__main__":
    df = load_products_catalog()
    docs = make_documents(df)
    build_and_upsert_pinecone(docs)
    logger.info("Catalog preprocessing and upsert to Pinecone complete.")

# TODO: Add error handling, logging, and support for incremental updates.
# TODO: Document the expected Excel columns and add validation.
# TODO: Normalize tags (e.g., split by comma) and ensure price/margin are numeric if needed.
# TODO: Add error handling for malformed tags or missing values if needed.
# TODO: Add instructions for Pinecone setup and environment variables, including COHERE_API_KEY. 