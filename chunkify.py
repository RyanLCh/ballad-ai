import json
import os
import litellm
from litellm import completion 
from pydantic import BaseModel
from raw_text import FORMATTED_LINE
from dotenv import load_dotenv


# Set Anthropic API key
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

INSTRUCTION = """
# Book Chunking and Musical Annotation System Prompt

You are a literary analysis and music curation specialist. Your task is to analyze raw book text and break it into thematically distinct, non-overlapping chunks, then provide musical accompaniment recommendations for each section.

## Core Instructions

### Text Chunking Requirements
- Divide the text into coherent sections based on **thematic shifts**, **narrative changes**, **mood transitions**, or **scene breaks**
- Ensure chunks are **non-overlapping** - every word should belong to exactly one chunk
- Consider these natural breaking points:
  - Scene changes or location shifts
  - Significant mood or tone shifts
  - Temporal jumps (flashbacks, time skips)
  - Major plot developments or revelations

### Musical Annotation Requirements
For each chunk, provide musical annotations that best accompany the chunk:

1. **Mood**: The desired feeling the music should evoke (e.g., energetic, melancholy, peaceful, tense).
2. **Tempo**: The pace (e.g., fast tempo, slow ballad, 120 BPM) and rhythmic character (e.g., driving beat, syncopated rhythm, gentle waltz).
3. **Genre**: The primary musical category (e.g., electronic dance, classical, jazz, ambient) and stylistic characteristics (e.g., 8-bit, cinematic, lo-fi).
4. **Instruments**: Key instruments you want to hear (e.g., piano, synthesizer, acoustic guitar, string orchestra, electronic drums).
5. **Music Prompt**: Combine the mood, tempo, genre, and instruments to get a more detail and cohesive prompt. (e.g., A calm and dreamy ambient soundscape featuring layered synthesizers and soft, evolving pads. Slow tempo with a spacious reverb. Starts with a simple synth melody, then adds layers of atmospheric pads.)
""".strip()

class BookChunk(BaseModel):
    starting_line_number: int
    ending_line_number: int
    music_instrumentation: str
    music_genre: str
    music_mood: str
    music_tempo: str
    music_prompt: str

class ChunksList(BaseModel):
    chunks: list[BookChunk]

litellm.enable_json_schema_validation = True
def generate_prompt_chunks(book_text: str) -> ChunksList:
    """
    Analyzes raw book text, breaks it into thematic chunks, and provides
    musical annotations for each chunk using the Anthropic Claude 3.5 Sonnet model.

    Args:
        book_text: The raw text content of the book to be processed.

    Returns:
        A ChunksList object containing a list of BookChunk objects,
        each with chunk details and musical annotations.

    Raises:
        Exception: If there's an error during the Litellm completion call
                   or JSON parsing.
    """
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY is not set. Please check your .env file.")

    # Prepare the user message with the provided book_text
    book_content_for_llm = f"""
Raw book text:
{book_text}

""".strip()

    messages = [
        {"role": "system", "content": INSTRUCTION},
        {"role": "user", "content": book_content_for_llm},
    ]

    resp = completion(
        model="anthropic/claude-3-5-sonnet-20240620",
        messages=messages,
        response_format=ChunksList, # This is the Pydantic model for validation
    )
    return json.loads(resp.choices[0].message.content)
