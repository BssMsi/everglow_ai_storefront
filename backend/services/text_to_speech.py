"""
text_to_speech.py
Module for Text-to-Speech (TTS) functionality using AIML API (async version).
"""

import os
import httpx
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

AIML_API_KEY = os.getenv("AIML_API_KEY")
BASE_URL = "https://api.aimlapi.com/v1"
TTS_MODEL = "#g1_aura-angus-en"
CONTAINER = "wav"
ENCODING = "linear16"
SAMPLE_RATE = 24000

async def text_to_speech(text: str) -> bytes:
    """
    Converts text to audio bytes using the AIML API (async).
    Args:
        text (str): The text to synthesize.
    Returns:
        bytes: The audio data in WAV format.
    Raises:
        RuntimeError: If the API call fails or audio is not found in the response.
    """
    if not AIML_API_KEY:
        raise ValueError("AIML_API_KEY not set in environment variables.")

    url = f"{BASE_URL}/tts"
    headers = {
        "Authorization": f"Bearer {AIML_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "*/*"
    }
    payload = {
        "model": TTS_MODEL,
        "text": text,
        "container": CONTAINER,
        "encoding": ENCODING,
        "sample_rate": SAMPLE_RATE
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code >= 400:
            raise RuntimeError(f"AIML TTS error: {response.status_code} - {response.text}")
        # Try to get audio from response content
        # If the API returns audio directly, it will be in response.content
        # If not, check for a field or add a TODO for follow-up
        if response.headers.get("content-type", "").startswith("audio") or response.headers.get("content-type", "").endswith("wav"):
            return response.content
        # If response is JSON, audio may be in a field or require a follow-up request
        try:
            data = response.json()
            # TODO: If the API returns a URL or key to fetch audio, implement follow-up fetch here
            raise RuntimeError(f"AIML TTS: Audio data not found in response. Metadata: {data}")
        except Exception:
            raise RuntimeError("AIML TTS: Unexpected response format, audio not found.")

# TODO: Confirm with AIML API docs if audio is returned directly or via a follow-up request. 