import requests
from pydub import AudioSegment
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
        "response_format": "wav",
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
    with open("narration.wav", "wb") as f:
        f.write(audio_bytes)
    print("Audio saved as narration.wav")

    # Extract and print timestamps
    word_timestamps = data.get("word_timestamps", [])
    # for word_info in word_timestamps:
    #     print(f"{word_info['word']}: {word_info['start']}s - {word_info['end']}s")

    # print(word_timestamps)
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

def merge_timestamps_with_lines(word_timestamps, annotated_text_block, word_to_line):
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


def rebuild_annotated_text(word_timestamps, max_line_length=120):
    annotated_lines = []
    word_to_line_map = []

    current_line = ""
    current_line_idx = 0

    for ts in word_timestamps:
        word = ts["word"]

        # Skip purely punctuation words (optional)
        if all(char in string.punctuation for char in word):
            continue

        # If adding this word would exceed the line limit, start new line
        if len(current_line) + len(word) + 1 > max_line_length:
            annotated_lines.append(f"[Line {current_line_idx}] {current_line.strip()}")
            current_line = ""
            current_line_idx += 1

        # Add word to current line
        current_line += word + " "
        word_clean = word.strip(".,?!;:\"“”‘’()[]").lower()
        word_to_line_map.append((word_clean, current_line_idx))

    # Final line
    if current_line.strip():
        annotated_lines.append(f"[Line {current_line_idx}] {current_line.strip()}")

    annotated_text = "\n".join(annotated_lines)
    return annotated_text, word_to_line_map


def get_current_line(t: float, merged_list):
    # Finds the latest word at or before timestamp t
    current_line = None
    for entry in merged_list:
        if entry["start"] <= t:
            current_line = entry["line"]
        else:
            break
    return current_line

def get_music_sync_timeline(chunks, merged_word_timestamps):
    timeline = []
    for chunk in chunks:
        start_line = chunk["start_line"]
        end_line = chunk["end_line"]
        music_file_path = chunk["music_file_path"]

        # Get all word timestamps for lines in this chunk
        relevant_words = [
            word for word in merged_word_timestamps
            if start_line <= word["line"] <= end_line
        ]

        if not relevant_words:
            continue  # skip empty chunks

        chunk_start_time = min(word["start"] for word in relevant_words)
        chunk_end_time = max(word["end"] for word in relevant_words)

        timeline.append({
            "music_file_path": music_file_path,
            "chunk_start": chunk_start_time,
            "chunk_end": chunk_end_time
        })

    return timeline



def orchestrate_audio(narration_path, timeline, fade_duration=2000, duck_db=-8):
    # Load narration
    narration = AudioSegment.from_wav(narration_path)

    # Base audio output starts with narration
    output = narration

    # Prepare a working music bed the same length as the narration
    music_bed = AudioSegment.silent(duration=len(narration))

    for chunk in timeline:
        music = AudioSegment.from_wav(chunk["music_file_path"])

        # Compute desired duration in milliseconds
        duration_ms = int((chunk["chunk_end"] - chunk["chunk_start"]) * 1000)

        # Loop and trim music to fit
        looped_music = (music * ((duration_ms // len(music)) + 1))[:duration_ms]

        # Apply fade in/out
        looped_music = looped_music.fade_in(fade_duration).fade_out(fade_duration)
        looped_music = looped_music + duck_db 
        # Position in music_bed
        start_ms = int(chunk["chunk_start"] * 1000)
        
        # Overlay looped music on top of current music bed
        music_bed = music_bed.overlay(looped_music, position=start_ms)
        
    # Combine narration with music bed
    final = narration.overlay(music_bed)

    # Export the result
    final.export("orchestrated_output.wav", format="wav")
    print("✅ Exported: orchestrated_output.wav")

def create_soundtrack_for_text(text):
    word_timestamps = query_lemonfox_tts(text, LEMONFOX_API_KEY)

    annon_text, word_to_line_map = rebuild_annotated_text(word_timestamps)
    file_path = "annotated_story.txt"
    try:
        # Open the file in write mode ('w').
        # If the file doesn't exist, it will be created.
        # If the file already exists, its content will be overwritten.
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(annon_text)
        print(f"Content successfully written to {file_path}")
    except IOError as e:
        print(f"Error writing to file {file_path}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    # print(word_timestamps)
    merged = merge_timestamps_with_lines(word_timestamps, annotated_text, word_to_line_map)
    print(merged)
    chunks = generate_song_chunks(generate_prompt_chunks(FORMATTED_LINE))

    timeline = get_music_sync_timeline(chunks, merged)
    print(timeline)

    orchestrate_audio("./narration.wav", timeline)

if __name__=="__main__":
    # Example usage
    try:
        with open('story.txt', 'r') as file:
            test_text = file.read()
    except FileNotFoundError:
        print("Skipping local test: story.txt not found")