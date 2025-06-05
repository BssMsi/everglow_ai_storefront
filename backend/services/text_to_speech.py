"""
text_to_speech.py
Module for Text-to-Speech (TTS) functionality using AIML API (async version).
"""

import os
import httpx
import asyncio
from dotenv import load_dotenv
import logging

# Load environment variables from .env
load_dotenv()

AIML_API_KEY = os.getenv("AIML_API_KEY")
BASE_URL = "https://api.aimlapi.com/v1"
TTS_MODEL = "#g1_aura-angus-en"
CONTAINER = "wav"
ENCODING = "linear16"
SAMPLE_RATE = 24000

logger = logging.getLogger(__name__)

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
        logger.error("AIML_API_KEY not set in environment variables.")
        raise ValueError("AIML_API_KEY not set in environment variables.")
    logger.info("Starting text-to-speech for text: %s", text[:50])
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
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            logger.info("TTS response status: %d", response.status_code)
            if response.status_code >= 400:
                logger.error("AIML TTS error: %d - %s", response.status_code, response.text)
                raise RuntimeError(f"AIML TTS error: {response.status_code} - {response.text}")
            if response.headers.get("content-type", "").startswith("audio") or response.headers.get("content-type", "").endswith("wav"):
                logger.info("TTS succeeded, returning audio bytes.")
                return response.content
            try:
                data = response.json()
                logger.error("AIML TTS: Audio data not found in response. Metadata: %s", data)
                raise RuntimeError(f"AIML TTS: Audio data not found in response. Metadata: {data}")
            except Exception as e:
                logger.exception("AIML TTS: Unexpected response format, audio not found. Error: %s", e)
                raise RuntimeError("AIML TTS: Unexpected response format, audio not found.")
    except Exception as e:
        logger.exception("Exception in text_to_speech: %s", e)
        raise

# TODO: Confirm with AIML API docs if audio is returned directly or via a follow-up request. 