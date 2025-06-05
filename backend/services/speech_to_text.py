"""
speech_to_text.py
Module for Speech-to-Text (STT) functionality using AIML API (async version).
"""

import os
import io
import asyncio
import httpx
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

AIML_API_KEY = os.getenv("AIML_API_KEY")
BASE_URL = "https://api.aimlapi.com/v1"
MODEL = "#g1_whisper-large"  # You can make this configurable if needed


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
        raise ValueError("AIML_API_KEY not set in environment variables.")

    # Step 1: Create STT task
    url = f"{BASE_URL}/stt/create"
    headers = {"Authorization": f"Bearer {AIML_API_KEY}"}
    data = {"model": MODEL}
    files = {"audio": (filename, io.BytesIO(audio_bytes), "audio/mpeg")}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data, headers=headers, files=files)
        if response.status_code >= 400:
            raise RuntimeError(f"AIML STT create error: {response.status_code} - {response.text}")
        response_data = response.json()
        gen_id = response_data.get("generation_id")
        if not gen_id:
            raise RuntimeError("AIML STT create did not return a generation_id.")

        # Step 2: Poll for result
        poll_url = f"{BASE_URL}/stt/{gen_id}"
        timeout = 600  # seconds
        poll_interval = 5  # seconds
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < timeout:
            poll_response = await client.get(poll_url, headers=headers)
            if poll_response.status_code >= 400:
                raise RuntimeError(f"AIML STT poll error: {poll_response.status_code} - {poll_response.text}")
            poll_data = poll_response.json()
            status = poll_data.get("status")
            if status in ("waiting", "active"):
                await asyncio.sleep(poll_interval)
                continue
            elif status == "succeeded":
                # Extract transcript
                try:
                    transcript = poll_data["result"]["results"]["channels"][0]["alternatives"][0]["transcript"]
                    return transcript
                except Exception as e:
                    raise RuntimeError(f"AIML STT result parsing error: {e}")
            else:
                raise RuntimeError(f"AIML STT failed with status: {status}")
        raise TimeoutError("AIML STT polling timed out.")

# TODO: Add 'httpx' to requirements.txt if not present.
# TODO: Document required audio format for frontend (e.g., mp3). 