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

def get_music_sync_timeline(chunks, merged_word_timestamps):
    timeline = []
    for chunk in chunks:
        start_line = chunk["start_line"]
        end_line = chunk["end_line"]
        music_file = chunk["music_file"]

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
            "music_file": music_file,
            "chunk_start": chunk_start_time,
            "chunk_end": chunk_end_time
        })

    return timeline



def orchestrate_audio(narration_path, timeline, fade_duration=2000, duck_db=-12):
    # Load narration
    narration = AudioSegment.from_wav(narration_path)

    # Base audio output starts with narration
    output = narration

    # Prepare a working music bed the same length as the narration
    music_bed = AudioSegment.silent(duration=len(narration))

    for chunk in timeline:
        music = AudioSegment.from_wav(chunk["music_file"])

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


# Example usage
text ='''"The Lottery" (1948) by Shirley Jackson

The morning of June 27th was clear and sunny, with the fresh warmth of a full-summer day; the flowers
were blossoming profusely and the grass was richly green. The people of the village began to gather in
the square, between the post office and the bank, around ten o'clock; in some towns there were so many
people that the lottery took two days and had to be started on June 2th. but in this village, where there
were only about three hundred people, the whole lottery took less than two hours, so it could begin at ten
o'clock in the morning and still be through in time to allow the villagers to get home for noon dinner.
The children assembled first, of course. School was recently over for the summer, and the feeling of
liberty sat uneasily on most of them; they tended to gather together quietly for a while before they broke
into boisterous play. and their talk was still of the classroom and the teacher, of books and reprimands.
Bobby Martin had already stuffed his pockets full of stones, and the other boys soon followed his
example, selecting the smoothest and roundest stones; Bobby and Harry Jones and Dickie Delacroix-- the
villagers pronounced this name "Dellacroy"--eventually made a great pile of stones in one corner of the
square and guarded it against the raids of the other boys. The girls stood aside, talking among themselves,
looking over their shoulders at rolled in the dust or clung to the hands of their older brothers or sisters.
Soon the men began to gather. surveying their own children, speaking of planting and rain, tractors and
taxes. They stood together, away from the pile of stones in the corner, and their jokes were quiet and they
smiled rather than laughed. The women, wearing faded house dresses and sweaters, came shortly after
their menfolk. They greeted one another and exchanged bits of gossip as they went to join their husbands.
Soon the women, standing by their husbands, began to call to their children, and the children came
reluctantly, having to be called four or five times. Bobby Martin ducked under his mother's grasping hand
and ran, laughing, back to the pile of stones. His father spoke up sharply, and Bobby came quickly and
took his place between his father and his oldest brother.'''

annotated_text = '''[Line 0] "The Lottery" (1948) by Shirley Jackson
[Line 1] 
[Line 2] The morning of June 27th was clear and sunny, with the fresh warmth of a full-summer day; the flowers
[Line 3] were blossoming profusely and the grass was richly green. The people of the village began to gather in
[Line 4] the square, between the post office and the bank, around ten o'clock; in some towns there were so many
[Line 5] people that the lottery took two days and had to be started on June 2th. but in this village, where there
[Line 6] were only about three hundred people, the whole lottery took less than two hours, so it could begin at ten
[Line 7] o'clock in the morning and still be through in time to allow the villagers to get home for noon dinner.
[Line 8] The children assembled first, of course. School was recently over for the summer, and the feeling of
[Line 9] liberty sat uneasily on most of them; they tended to gather together quietly for a while before they broke
[Line 10] into boisterous play. and their talk was still of the classroom and the teacher, of books and reprimands.
[Line 11] Bobby Martin had already stuffed his pockets full of stones, and the other boys soon followed his
[Line 12] example, selecting the smoothest and roundest stones; Bobby and Harry Jones and Dickie Delacroix-- the
[Line 13] villagers pronounced this name "Dellacroy"--eventually made a great pile of stones in one corner of the
[Line 14] square and guarded it against the raids of the other boys. The girls stood aside, talking among themselves,
[Line 15] looking over their shoulders at rolled in the dust or clung to the hands of their older brothers or sisters.
[Line 16] Soon the men began to gather. surveying their own children, speaking of planting and rain, tractors and
[Line 17] taxes. They stood together, away from the pile of stones in the corner, and their jokes were quiet and they
[Line 18] smiled rather than laughed. The women, wearing faded house dresses and sweaters, came shortly after
[Line 19] their menfolk. They greeted one another and exchanged bits of gossip as they went to join their husbands.
[Line 20] Soon the women, standing by their husbands, began to call to their children, and the children came
[Line 21] reluctantly, having to be called four or five times. Bobby Martin ducked under his mother's grasping hand
[Line 22] and ran, laughing, back to the pile of stones. His father spoke up sharply, and Bobby came quickly and
[Line 23] took his place between his father and his oldest brother.
'''
word_timestamps = query_lemonfox_tts(text, LEMONFOX_API_KEY)
merged = merge_timestamps_with_lines(word_timestamps, annotated_text)
# print(merged)
chunks = [
    {"music_file": "music1.wav", "start_line": 0, "end_line": 10},
    {"music_file": "music2.wav", "start_line": 11, "end_line": 23},
]

timeline = get_music_sync_timeline(chunks, merged)
# print(timeline)

orchestrate_audio("./narration.wav", timeline)

