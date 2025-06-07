import logging
import sys # Import sys to output to stdout
import pandas as pd # Import pandas for Excel handling
import os # Import os for path joining
import re  # Add this import

# Configure basic logging
# This will log messages from all loggers (including the one in english_agent.py)
# to standard output (console) with a specified format and level.
logging.basicConfig(
    level=logging.INFO,  # Set the logging level (e.g., INFO, DEBUG, ERROR)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # Output logs to stdout
        # You can also add logging.FileHandler("app.log") to log to a file
    ]
)

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.responses import HTMLResponse
import asyncio
from typing import Any, Dict, List, Tuple, Optional # Added Tuple
from pydantic import BaseModel

# Import modularized service functions
from services.speech_to_text import speech_to_text
from services.english_agent import english_agent, AgentState # Import AgentState for type hinting if needed
from services.text_to_speech import text_to_speech

app = FastAPI()

# Define the path to the skincare catalog file
CATALOG_PATH = os.path.join(os.path.dirname(__file__), "skincare catalog.xlsx")

# Placeholder for in-memory product data loaded from "skincare catalog.xlsx"
# This will be populated on application startup.
PRODUCT_CATALOG_DATA: Any = None # Change type hint to Any, as it will be a DataFrame

# Pydantic model for the chat request
class ChatRequest(BaseModel):
    text: str
    # Frontend sends messages as a list of dicts: [{'id': '...', 'content': '...', 'sender': 'user'|'agent', ...}]
    # It should also send the full last agent state for proper context continuation.
    state_dict: Optional[Dict[str, Any]] = None # Changed from List[Dict[str, Any]] to Dict[str, Any]

logger = logging.getLogger(__name__)

@app.post("/api/chat")
async def http_chat_agent(request: ChatRequest):
    """
    HTTP endpoint for text-based interaction with the English agent.
    """
    try:
        logger.info(f"Received /api/chat request. Text: '{request.text}', State Dict from Frontend: {request.state_dict}") # <-- ADD THIS LINE

        # Initialize current_state_data with defaults
        current_state_data = {
            "history": [],
            "entities": {},
            "intent": None, 
            "active_agent": None, 
            "followup_questions": []
        }

        if request.state_dict:
            logger.info(f"Received state_dict from frontend: {request.state_dict}")
            # Reconstruct history from the 'history' key if it's in the AgentState format
            # (list of [user_msg, agent_msg] tuples)
            history_from_state = request.state_dict.get("history")
            if isinstance(history_from_state, list):
                current_state_data["history"] = history_from_state
            else:
                # Fallback or handle if history is in a different format (e.g., flat list of messages)
                # This part adapts your previous logic for flat message lists if needed,
                # but ideally, frontend sends history in the (user, agent) tuple format.
                paired_history: List[Tuple[str, str]] = []
                user_msg_content = None
                # Assuming request.state_dict might still be the old flat list for history if not updated on frontend
                # This is a transitional step. Ideally, frontend sends state_dict.history as list of tuples.
                messages_list = request.state_dict.get("messages", request.state_dict) # Check for 'messages' key or use root
                if isinstance(messages_list, list):
                    for i, msg_data in enumerate(messages_list):
                        sender = msg_data.get("sender")
                        content = msg_data.get("content")
                        if sender == "user":
                            user_msg_content = content
                        elif sender == "agent" and user_msg_content is not None:
                            paired_history.append((user_msg_content, content))
                            user_msg_content = None
                    current_state_data["history"] = paired_history

            # Populate other state fields directly from the received state_dict
            current_state_data["entities"] = request.state_dict.get("entities", {})
            current_state_data["intent"] = request.state_dict.get("intent")
            current_state_data["active_agent"] = request.state_dict.get("active_agent")
            current_state_data["followup_questions"] = request.state_dict.get("followup_questions", [])
        else:
            logger.info("No state_dict received from frontend, starting with default state.")

        # Call the synchronous english_agent function
        # The english_agent function itself will call AgentState.from_dict(current_state_data)
        result = english_agent(text=request.text, state_dict=current_state_data)
        return result # english_agent returns a dict like {"response": ..., "state": ..., "product_ids": []}
    except Exception as e:
        logger.exception("Error processing chat: %s", e)
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.websocket("/ws/voice-agent")
async def websocket_voice_agent(websocket: WebSocket):
    await websocket.accept()
    try:
        logger.info("WebSocket connection accepted.")
        while True:
            audio_bytes = await websocket.receive_bytes()
            logger.info("Received audio bytes from frontend.")
            text = await speech_to_text(audio_bytes)
            logger.info("Transcribed text: %s", text)
            response_data = english_agent(text, state_dict=None)
            logger.info("english_agent WS result: %s", response_data)
            response_text_content = ""
            if isinstance(response_data.get("response"), dict):
                 response_text_content = response_data.get("response", {}).get("response", "Sorry, I could not understand.")
            elif isinstance(response_data.get("response"), str):
                 response_text_content = response_data.get("response", "Sorry, I could not understand.")
            else:
                response_text_content = "I received a response I could not process."
            response_audio = await text_to_speech(response_text_content)
            logger.info("Sending audio bytes back to frontend.")
            await websocket.send_bytes(response_audio)
    except WebSocketDisconnect:
        logger.info("Client disconnected from voice agent WebSocket")
        pass
    except Exception as e:
        logger.exception("Error in voice agent WebSocket: %s", e)
        await websocket.close(code=1011, reason=f"Server error: {str(e)}")

# New GET endpoint to fetch product details by IDs
@app.get("/api/products")
async def get_products_by_ids(ids: List[str] = Query()):
    """
    GET endpoint to retrieve product details for a list of product IDs.
    Looks up IDs in the in-memory product catalog data (pandas DataFrame).
    """
    logger.info("Received /api/products request with IDs: %s", ids)
    
    # Ensure PRODUCT_CATALOG_DATA is a DataFrame before attempting to filter
    if PRODUCT_CATALOG_DATA is None or not isinstance(PRODUCT_CATALOG_DATA, pd.DataFrame) or PRODUCT_CATALOG_DATA.empty:
        logger.warning("Product catalog data is not loaded or is empty.")
        return [] # Return empty list if data is not available

    try:
        # Use pandas filtering to find products with matching IDs
        # Assumes 'product_id' is the column name for IDs
        # Use .isin() for efficient checking against a list of IDs
        found_products_df = PRODUCT_CATALOG_DATA[PRODUCT_CATALOG_DATA['product_id'].isin(ids)]
        
        # Convert the filtered DataFrame back to a list of dictionaries for the response
        found_products = found_products_df.to_dict('records')
        
        logger.info("Found %d products for IDs: %s", len(found_products), ids)
        return found_products
    except KeyError:
        logger.error("Product catalog DataFrame is missing the 'product_id' column.")
        return []
    except Exception as e:
        logger.exception(f"Error filtering product catalog by IDs {ids}: {e}")
        return []

# Startup event to load the product catalog
@app.on_event("startup")
async def load_product_catalog():
    logger.info(f"Attempting to load product catalog from {CATALOG_PATH}")
    global PRODUCT_CATALOG_DATA
    try:
        df = pd.read_excel(CATALOG_PATH)
        
        # Clean column names: keep only alphabets and underscores, trim whitespace
        df.columns = [re.sub(r'[^a-zA-Z_]', '', col).strip().lower() for col in df.columns]

        # Store the DataFrame with cleaned column names
        PRODUCT_CATALOG_DATA = df
        logger.info(f"Successfully loaded {len(df)} products into DataFrame from catalog.")
        logger.info(f"Cleaned column names: {list(df.columns)}")
    except FileNotFoundError:
        logger.error(f"Product catalog file not found at {CATALOG_PATH}. The /api/products endpoint will return empty results.")
        PRODUCT_CATALOG_DATA = pd.DataFrame() # Assign an empty DataFrame if file is missing
    except Exception as e:
        logger.exception(f"Error loading product catalog from {CATALOG_PATH}: {e}")
        PRODUCT_CATALOG_DATA = pd.DataFrame() # Assign an empty DataFrame if loading fails

# TODO: Add authentication, streaming audio support, and production-level error handling as needed.