import requests
import os
import base64
import json
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
LEMONFOX_API_KEY = os.getenv("LEMONFOX_API_KEY")

def query_lemonfox_tts(text: str, api_key: str):
    url = "https://api.lemonfox.ai/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "input": text,
        "voice": "sarah",            # Choose any voice you want
        "response_format": "mp3",
        "word_timestamps": True           # Enables word-level timestamps
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    # print(response.headers)
    # print(response.content)

    data = response.json()

    # Extract and save audio
    audio_b64 = data['audio']
    audio_bytes = base64.b64decode(audio_b64)
    with open("output.mp3", "wb") as f:
        f.write(audio_bytes)
    print("Audio saved as output.mp3")

    # Extract and print timestamps
    word_timestamps = data.get("word_timestamps", [])
    for word_info in word_timestamps:
        print(f"{word_info['word']}: {word_info['start']}s - {word_info['end']}s")

    print(word_timestamps)

# Example usage
text = "The quick brown fox jumps over the lazy dog."
query_lemonfox_tts(text, LEMONFOX_API_KEY)