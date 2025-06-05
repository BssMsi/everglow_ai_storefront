import logging
import sys # Import sys to output to stdout

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

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
import asyncio
from typing import Any, Dict, List, Tuple, Optional # Added Tuple
from pydantic import BaseModel

# Import modularized service functions
from services.speech_to_text import speech_to_text
from services.english_agent import english_agent, AgentState # Import AgentState for type hinting if needed
from services.text_to_speech import text_to_speech

app = FastAPI()

# Pydantic model for the chat request
class ChatRequest(BaseModel):
    text: str
    # Frontend sends messages as a list of dicts: [{'id': '...', 'content': '...', 'sender': 'user'|'agent', ...}]
    state_dict: Optional[List[Dict[str, Any]]] = None 

logger = logging.getLogger(__name__)

@app.post("/api/chat")
async def http_chat_agent(request: ChatRequest):
    """
    HTTP endpoint for text-based interaction with the English agent.
    """
    try:
        logger.info("Received /api/chat request: %s", request)
        current_state_data = {
            "history": [],
            "entities": {},
            "intent": None, 
            "active_agent": None, 
            "followup_questions": []
        }

        if request.state_dict:
            # Convert frontend message list to AgentState history format: List of (user, agent) tuples
            # The frontend sends a flat list of messages. We need to pair them up.
            # This assumes a user message is always followed by an agent message in the history for pairing.
            # Or, if the last message is a user message, it means the agent hasn't responded to it yet in the history.
            
            paired_history: List[Tuple[str, str]] = []
            user_msg_content = None
            for i, msg_data in enumerate(request.state_dict):
                sender = msg_data.get("sender")
                content = msg_data.get("content")

                if sender == "user":
                    # If there was a pending user message, it means no agent response followed it.
                    # This scenario might indicate an incomplete pair from previous turns, 
                    # or the agent is about to process this new user message.
                    # For constructing history for the *current* call, we only add complete pairs.
                    # The current user's input (`request.text`) is handled separately by english_agent.
                    user_msg_content = content 
                elif sender == "agent" and user_msg_content is not None:
                    paired_history.append((user_msg_content, content))
                    user_msg_content = None # Reset after pairing
                # We ignore agent messages that don't have a preceding user message for pairing in history.
                # The very first message from agent is usually a greeting and not part of a (user,agent) pair.
            
            current_state_data["history"] = paired_history
            
            # You could also try to extract the latest entities, intent, etc., 
            # if the frontend were to send the full last agent state. 
            # For now, we only focus on reconstructing history.
            # Example: if frontend sent full last_agent_state.to_dict():
            # last_agent_response_obj = request.state_dict.get("last_agent_state") # if frontend sent this
            # if last_agent_response_obj and isinstance(last_agent_response_obj, dict):
            #     current_state_data["entities"] = last_agent_response_obj.get("entities", {})
            #     current_state_data["intent"] = last_agent_response_obj.get("intent")
            #     current_state_data["active_agent"] = last_agent_response_obj.get("active_agent")
            #     current_state_data["followup_questions"] = last_agent_response_obj.get("followup_questions", [])

        # Call the synchronous english_agent function
        # The english_agent function itself will call AgentState.from_dict(current_state_data)
        result = english_agent(text=request.text, state_dict=current_state_data)
        logger.info("english_agent result: %s", result)
        return result # english_agent returns a dict like {"response": ..., "state": ...}
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

# TODO: Add authentication, streaming audio support, and production-level error handling as needed.