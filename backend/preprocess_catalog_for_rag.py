import os
import pandas as pd
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document

# --- Config ---
CATALOG_PATH = os.path.join(os.path.dirname(__file__), "skincare catalog.xlsx")
VECTORSTORE_DIR = os.path.join(os.path.dirname(__file__), "catalog_vectorstore")

# --- Step 1: Load and Clean Excel File ---
def load_catalog(path):
    """
    Loads the skincare catalog Excel file and returns a cleaned DataFrame.
    Validates required columns.
    """
    required_columns = [
        "product_id", "name", "category", "description", "top_ingredients", "tags", "price (USD)", "margin (%)"
    ]
    df = pd.read_excel(path)
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in catalog: {missing}")
    # TODO: Add more cleaning/normalization as needed
    return df

# --- Step 2: Format Each Product as a RAG Document ---
def make_documents(df):
    """
    Converts each product row into a LangChain Document for RAG using the correct columns.
    Splits tags on '|', lowercases and strips them, includes in text and metadata.
    """
    docs = []
    for _, row in df.iterrows():
        # --- Normalize tags ---
        raw_tags = str(row.get('tags', ''))
        tag_list = [t.strip().lower() for t in raw_tags.split('|') if t.strip()] if raw_tags else []
        tags_text = ', '.join(tag_list)
        # --- Build document text ---
        text = (
            f"Product ID: {row.get('product_id', '')}\n"
            f"Name: {row.get('name', '')}\n"
            f"Category: {row.get('category', '')}\n"
            f"Description: {row.get('description', '')}\n"
            f"Top Ingredients: {row.get('top_ingredients', '')}\n"
            f"Tags: {tags_text}\n"
            f"Price (USD): {row.get('price (USD)', '')}\n"
            f"Margin (%): {row.get('margin (%)', '')}"
        )
        # --- Store all columns as metadata, but tags as a list ---
        metadata = {k: row[k] for k in row.index}
        metadata['tags'] = tag_list
        docs.append(Document(page_content=text, metadata=metadata))
    return docs

# --- Step 3: Generate Embeddings and Store in Vector Store ---
def build_vectorstore(docs, persist_dir):
    """
    Generates embeddings and stores documents in a Chroma vector store.
    """
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")  # TODO: Change model if needed
    vectorstore = Chroma.from_documents(docs, embeddings, persist_directory=persist_dir)
    vectorstore.persist()
    print(f"Vector store saved to {persist_dir}")
    return vectorstore

if __name__ == "__main__":
    df = load_catalog(CATALOG_PATH)
    docs = make_documents(df)
    build_vectorstore(docs, VECTORSTORE_DIR)
    print("Catalog preprocessing for RAG complete.")

# TODO: Add error handling, logging, and support for incremental updates.
# TODO: Document the expected Excel columns and add validation.
# TODO: Normalize tags (e.g., split by comma) and ensure price/margin are numeric if needed.
# TODO: Add error handling for malformed tags or missing values if needed. 