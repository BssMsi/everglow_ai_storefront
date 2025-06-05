from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import asyncio
from typing import Any

# Import modularized service functions
from services.speech_to_text import speech_to_text
from services.english_agent import english_agent
from services.text_to_speech import text_to_speech

app = FastAPI()

@app.websocket("/ws/voice-agent")
async def websocket_voice_agent(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive audio bytes from frontend
            audio_bytes = await websocket.receive_bytes()
            # 1. Speech to Text (async)
            text = await speech_to_text(audio_bytes)
            # 2. English Agent (sync for now)
            response_text = english_agent(text)
            # 3. Text to Speech (async)
            response_audio = await text_to_speech(response_text)
            # Send audio bytes back to frontend
            await websocket.send_bytes(response_audio)
    except WebSocketDisconnect:
        # Handle disconnects gracefully
        pass
    except Exception as e:
        # TODO: Add better error handling/logging
        await websocket.close()

# TODO: Add authentication, streaming audio support, and production-level error handling as needed. 