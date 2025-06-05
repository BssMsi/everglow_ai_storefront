import os
import pandas as pd
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from rapidfuzz import process, fuzz

# --- Config ---
FEEDBACK_PATH = os.path.join(os.path.dirname(__file__), "CustomerFeedback.xlsx")
CATALOG_PATH = os.path.join(os.path.dirname(__file__), "skincare catalog.xlsx")
VECTORSTORE_DIR = os.path.join(os.path.dirname(__file__), "feedback_vectorstore")

# --- Step 1: Load Catalog for Product Linking ---
def load_catalog_products(path):
    df = pd.read_excel(path)
    # Use lowercase for matching
    return set(str(p).strip().lower() for p in df["name"].dropna().unique())

# --- Utility: Normalize star ratings ---
def normalize_rating(rating):
    rating = str(rating).strip()
    # Handle star strings like "★★★☆☆"
    if set(rating) <= set("★☆") and len(rating) == 5:
        stars = rating.count("★")
        return f"{stars} out of 5"
    # Handle numeric or "4/5" style
    try:
        rating_num = int(float(rating.split("/")[0]))
        return f"{rating_num} out of 5"
    except Exception:
        return rating

# --- Step 2: Preprocess Reviews Sheet ---
def preprocess_reviews(df_reviews, catalog_products):
    docs = []
    for _, row in df_reviews.iterrows():
        reviewer = str(row.get("Reviewer", "")).strip()
        product = str(row.get("Product", "")).strip()
        review = str(row.get("Review", "")).strip()
        rating = normalize_rating(row.get("Rating", ""))
        # Link to catalog
        product_key = product.lower()
        in_catalog = product_key in catalog_products
        # Build document text
        text = f"Review for {product}: {review}\nRating: {rating}\nReviewer: {reviewer}"
        metadata = {
            "source": "review",
            "reviewer": reviewer,
            "product": product,
            "rating": rating,
            "product_in_catalog": in_catalog
        }
        docs.append(Document(page_content=text, metadata=metadata))
    return docs

# --- Utility: Fuzzy match product in text ---
def extract_product_from_text(text, catalog_products, threshold=80):
    # Use rapidfuzz to find best match
    choices = list(catalog_products)
    match, score, _ = process.extractOne(text.lower(), choices, scorer=fuzz.partial_ratio)
    if score >= threshold:
        return match
    return None

# --- Step 3: Preprocess Customer Support Tickets Sheet ---
def preprocess_support_tickets(df_tickets, catalog_products):
    docs = []
    for _, row in df_tickets.iterrows():
        ticket_id = str(row.get("Ticket ID", "")).strip()
        customer_msg = str(row.get("Customer Message", "")).strip()
        support_resp = str(row.get("Support Response", "")).strip()
        # Try to extract product from customer message or support response
        product = extract_product_from_text(customer_msg, catalog_products) or extract_product_from_text(support_resp, catalog_products) or ""
        in_catalog = bool(product)
        text = f"Customer Support Ticket {ticket_id}:\nQ: {customer_msg}\nA: {support_resp}"
        metadata = {
            "source": "support_ticket",
            "ticket_id": ticket_id,
            "product": product,
            "product_in_catalog": in_catalog
        }
        docs.append(Document(page_content=text, metadata=metadata))
    return docs

# --- Step 4: Build Vectorstore ---
def build_vectorstore(docs, persist_dir):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(docs, embeddings, persist_directory=persist_dir)
    vectorstore.persist()
    print(f"Feedback vector store saved to {persist_dir}")
    return vectorstore

if __name__ == "__main__":
    catalog_products = load_catalog_products(CATALOG_PATH)
    xls = pd.ExcelFile(FEEDBACK_PATH)
    df_reviews = pd.read_excel(xls, sheet_name="Reviews")
    df_tickets = pd.read_excel(xls, sheet_name="Customer Support Tickets")
    docs = preprocess_reviews(df_reviews, catalog_products) + preprocess_support_tickets(df_tickets, catalog_products)
    build_vectorstore(docs, VECTORSTORE_DIR)
    print("Customer feedback preprocessing for RAG complete.")

# TODO: Add error handling, logging, and support for incremental updates.
# TODO: Document the expected Excel columns and add validation. 