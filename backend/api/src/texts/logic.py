from .lemon_fox import query_lemonfox_tts, rebuild_annotated_text, merge_timestamps_with_lines
from .song_gen import generate_song_chunks
from .chunkify import generate_prompt_chunks
import os

async def process_text_to_multimodal(text: str, api_key: str):
    # 1. Get TTS and Word Timestamps
    word_timestamps = query_lemonfox_tts(text, api_key)
    
    # 2. Format text for the music model (Greedy line wrap)
    annotated_text, word_to_line_map = rebuild_annotated_text(word_timestamps)
    
    # 3. Generate Music Prompts and Audio Chunks
    # This uses your Lyria 2 integration in song_gen.py
    prompt_chunks = generate_prompt_chunks(annotated_text)
    music_chunks = generate_song_chunks(prompt_chunks)
    
    # 4. Merge everything for the Frontend
    # This gives the frontend the exact timing for word highlighting
    final_merged_data = merge_timestamps_with_lines(
        word_timestamps, 
        annotated_text, 
        word_to_line_map
    )
    
    return final_merged_data