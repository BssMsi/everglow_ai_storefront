"""
speech_to_text.py
Module for Speech-to-Text (STT) functionality using AIML API (async version).
"""

import os
import io
import asyncio
import httpx
from dotenv import load_dotenv
import logging

# Load environment variables from .env in the parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

AIML_API_KEY = os.getenv("AIML_API_KEY")
BASE_URL = "https://api.aimlapi.com/v1"
MODEL = "#g1_whisper-large"  # You can make this configurable if needed

logger = logging.getLogger(__name__)

async def speech_to_text(audio_bytes: bytes, filename: str = "audio.mp3") -> str:
    """
    Converts audio bytes to text using the AIML API (async).
    Args:
        audio_bytes (bytes): The audio data in bytes (must be mp3 or compatible with AIML API).
        filename (str): The filename to use for the upload (default: audio.mp3).
    Returns:
        str: The transcribed text, or raises an error.
    """
    if not AIML_API_KEY:
        logger.error("AIML_API_KEY not set in environment variables.")
        raise ValueError("AIML_API_KEY not set in environment variables.")
    logger.info("Starting speech-to-text process for file: %s", filename)
    url = f"{BASE_URL}/stt/create"
    headers = {"Authorization": f"Bearer {AIML_API_KEY}"}
    data = {"model": MODEL}
    files = {"audio": (filename, io.BytesIO(audio_bytes), "audio/mpeg")}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data, headers=headers, files=files)
            logger.info("STT create response status: %d", response.status_code)
            if response.status_code >= 400:
                logger.error("AIML STT create error: %d - %s", response.status_code, response.text)
                raise RuntimeError(f"AIML STT create error: {response.status_code} - {response.text}")
            response_data = response.json()
            gen_id = response_data.get("generation_id")
            if not gen_id:
                logger.error("AIML STT create did not return a generation_id. Response: %s", response.text)
                raise RuntimeError("AIML STT create did not return a generation_id.")
            poll_url = f"{BASE_URL}/stt/{gen_id}"
            timeout = 600
            poll_interval = 5
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < timeout:
                poll_response = await client.get(poll_url, headers=headers)
                logger.info("Polling STT status: %d", poll_response.status_code)
                if poll_response.status_code >= 400:
                    logger.error("AIML STT poll error: %d - %s", poll_response.status_code, poll_response.text)
                    raise RuntimeError(f"AIML STT poll error: {poll_response.status_code} - {poll_response.text}")
                poll_data = poll_response.json()
                status = poll_data.get("status")
                logger.debug("STT poll status: %s", status)
                if status in ("waiting", "active"):
                    await asyncio.sleep(poll_interval)
                    continue
                elif status == "succeeded":
                    try:
                        transcript = poll_data["result"]["results"]["channels"][0]["alternatives"][0]["transcript"]
                        logger.info("STT succeeded. Transcript: %s", transcript)
                        return transcript
                    except Exception as e:
                        logger.exception("AIML STT result parsing error: %s", e)
                        raise RuntimeError(f"AIML STT result parsing error: {e}")
                else:
                    logger.error("AIML STT failed with status: %s", status)
                    raise RuntimeError(f"AIML STT failed with status: {status}")
            logger.error("AIML STT polling timed out.")
            raise TimeoutError("AIML STT polling timed out.")
    except Exception as e:
        logger.exception("Exception in speech_to_text: %s", e)
        raise

# TODO: Document required audio format for frontend (e.g., mp3).