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
    with open("narration.mp3", "wb") as f:
        f.write(audio_bytes)
    print("Audio saved as narration.mp3")

    # Extract and print timestamps
    word_timestamps = data.get("word_timestamps", [])
    for word_info in word_timestamps:
        print(f"{word_info['word']}: {word_info['start']}s - {word_info['end']}s")

    print(word_timestamps)
    return word_timestamps

def get_word_to_line_map(annotated_lines):
    word_to_line = []
    for line in annotated_lines:
        prefix, content = line.split("] ", 1)
        line_number = int(prefix.strip()[6:])  # Extract number from "[Line N]"
        words = content.strip().split()
        for word in words:
            # Remove punctuation if needed
            word_clean = word.strip(".,?!;:")
            word_to_line.append((word_clean.lower(), line_number))
    return word_to_line

def merge_timestamps_with_lines(word_timestamps, annotated_lines):
    word_to_line = get_word_to_line_map(annotated_lines)

    merged = []
    idx = 0
    for ts in word_timestamps:
        word = ts["word"].lower().strip(".,?!;:")
        # Handle potential mismatch
        while idx < len(word_to_line) and word != word_to_line[idx][0]:
            idx += 1
        line = word_to_line[idx][1] if idx < len(word_to_line) else -1
        merged.append({
            "word": ts["word"],
            "start": ts["start"],
            "end": ts["end"],
            "line": line
        })
        idx += 1
    return merged

def get_current_line(t: float, merged_list):
    # Finds the latest word at or before timestamp t
    current_line = None
    for entry in merged_list:
        if entry["start"] <= t:
            current_line = entry["line"]
        else:
            break
    return current_line


# Example usage
text = "The quick brown fox jumps over the lazy dog."
annotated_text = [
    "[Line 0] The quick brown,",
    "[Line 1] fox jumps over the lazy dog."
]
word_timestamps = query_lemonfox_tts(text, LEMONFOX_API_KEY)
merged = merge_timestamps_with_lines(word_timestamps, annotated_text)
print(merged)
# Now query real-time position:
print(get_current_line(0.3, merged))   # -> Line 0
print(get_current_line(0.6, merged))   # -> Line 0
print(get_current_line(1.6, merged))   # -> Line 1
print(get_current_line(3.0, merged))   # -> Line 1 (end of narration) 