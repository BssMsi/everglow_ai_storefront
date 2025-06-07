import os
import logging
from typing import Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pinecone import Pinecone
from langchain_cohere import CohereEmbeddings

load_dotenv()
logger = logging.getLogger(__name__)

# Environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")
CATALOG_PINECONE_INDEX_NAME = os.getenv("CATALOG_PINECONE_INDEX_NAME", "everglow-catalog")
FEEDBACK_PINECONE_INDEX_NAME = os.getenv("FEEDBACK_PINECONE_INDEX_NAME", "everglow-feedback")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# LLM Setup
if not os.getenv("GEMINI_API_KEY"):
    logger.error("GEMINI_API_KEY not set in environment variables.")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-preview-05-20",
    temperature=0.2,
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# Singleton patterns for efficiency
_cohere_embeddings: Optional[CohereEmbeddings] = None
_pinecone_client: Optional[Pinecone] = None

def get_cohere_embeddings() -> CohereEmbeddings:
    global _cohere_embeddings
    if _cohere_embeddings is None:
        if not COHERE_API_KEY:
            logger.error("COHERE_API_KEY not set in environment variables.")
            raise ValueError("COHERE_API_KEY not set in environment variables.")
        _cohere_embeddings = CohereEmbeddings(cohere_api_key=COHERE_API_KEY, model="embed-english-light-v2.0")
        logger.info("Initialized Cohere Embeddings model: embed-english-light-v2.0")
    return _cohere_embeddings

def get_pinecone_client() -> Pinecone:
    global _pinecone_client
    if _pinecone_client is None:
        if not PINECONE_API_KEY:
            logger.error("PINECONE_API_KEY not set in environment variables.")
            raise ValueError("PINECONE_API_KEY not set in environment variables.")
        _pinecone_client = Pinecone(api_key=PINECONE_API_KEY)
        logger.info("Initialized Pinecone client.")
    return _pinecone_client

def get_catalog_index():
    pc = get_pinecone_client()
    if CATALOG_PINECONE_INDEX_NAME not in [idx.name for idx in pc.list_indexes()]:
        logger.error(f"Pinecone catalog index '{CATALOG_PINECONE_INDEX_NAME}' not found. Please run preprocessing script.")
        raise ValueError(f"Pinecone catalog index '{CATALOG_PINECONE_INDEX_NAME}' not found. Please run preprocessing script.")
    return pc.Index(CATALOG_PINECONE_INDEX_NAME)

def get_feedback_index():
    pc = get_pinecone_client()
    if FEEDBACK_PINECONE_INDEX_NAME not in [idx.name for idx in pc.list_indexes()]:
        logger.error(f"Pinecone feedback index '{FEEDBACK_PINECONE_INDEX_NAME}' not found. Please run preprocessing script.")
        raise ValueError(f"Pinecone feedback index '{FEEDBACK_PINECONE_INDEX_NAME}' not found. Please run preprocessing script.")
    return pc.Index(FEEDBACK_PINECONE_INDEX_NAME)