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

def get_word_to_line_map(annotated_text_block):
    word_to_line = []
    lines = annotated_text_block.strip().splitlines()
    
    for line in lines:
        if not line.strip():  # skip blank lines
            continue
        if not line.startswith("[Line"):
            continue
        
        try:
            prefix, content = line.split("] ", 1)
        except ValueError:
            continue  # In case there's a line like "[Line 1]" with no text
        
        line_number = int(prefix.strip()[6:])  # Extract N from "[Line N]"
        words = content.strip().split()
        for word in words:
            word_clean = word.strip(".,?!;:\"“”‘’()[]")
            word_to_line.append((word_clean.lower(), line_number))
    
    return word_to_line

import string

def merge_timestamps_with_lines(word_timestamps, annotated_text_block):
    word_to_line = get_word_to_line_map(annotated_text_block)
    merged = []
    idx = 0

    for ts in word_timestamps:
        word = ts["word"].lower().strip(".,?!;:\"“”‘’()[]")
        
        # Skip purely punctuation tokens
        if all(char in string.punctuation for char in ts["word"]):
            continue

        # Try to find the next matching word in the word_to_line list
        while idx < len(word_to_line) and word != word_to_line[idx][0]:
            idx += 1

        if idx < len(word_to_line):
            line = word_to_line[idx][1]
            idx += 1
        else:
            line = -1  # fallback if no match found

        merged.append({
            "word": ts["word"],
            "start": ts["start"],
            "end": ts["end"],
            "line": line
        })

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
text ='''The Lottery" (1948) by Shirley Jackson. 

The morning of June 27th was clear and sunny, with the fresh warmth of a full-summer day; the flowers
were blossoming profusely and the grass was richly green. The people of the village began to gather in
the square, between the post office and the bank, around ten o'clock; in some towns there were so many
people that the lottery took two days and had to be started on June 2th. but in this village, where there
were only about three hundred people, the whole lottery took less than two hours, so it could begin at ten
o'clock in the morning and still be through in time to allow the villagers to get home for noon dinner.'''
annotated_text = '''[Line 0] "The Lottery" (1948) by Shirley Jackson
[Line 1] 
[Line 2] The morning of June 27th was clear and sunny, with the fresh warmth of a full-summer day; the flowers
[Line 3] were blossoming profusely and the grass was richly green. The people of the village began to gather in
[Line 4] the square, between the post office and the bank, around ten o'clock; in some towns there were so many
[Line 5] people that the lottery took two days and had to be started on June 2th. but in this village, where there
[Line 6] were only about three hundred people, the whole lottery took less than two hours, so it could begin at ten
[Line 7] o'clock in the morning and still be through in time to allow the villagers to get home for noon dinner.
'''
word_timestamps = query_lemonfox_tts(text, LEMONFOX_API_KEY)
merged = merge_timestamps_with_lines(word_timestamps, annotated_text)
print(merged)
# Now query real-time position:
print(get_current_line(0.3, merged))
print(get_current_line(0.6, merged))
print(get_current_line(1.6, merged))
print(get_current_line(3.0, merged))  