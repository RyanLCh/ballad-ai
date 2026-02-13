import json
import google.auth
import google.auth.transport.requests
import requests
import base64
import os # Make sure os is imported
from .chunkify import generate_prompt_chunks, BookChunk, ChunksList
from raw_text import FORMATTED_LINE

# --- Configuration ---
# Replace with your actual Google Cloud Project ID
PROJECT_ID = "balladai-463622"

# Lyria 2 model endpoint. This is fixed for the public model.
# Make sure Lyria 2 is available in 'us-central1' in your project.
MUSIC_MODEL_ENDPOINT = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models/lyria-002:predict"


# Directory where generated songs will be saved
SONGS_DIR = "./songs" # Define the directory

def send_request_to_google_api(api_endpoint, data=None):
    """
    Sends an HTTP request to a Google API endpoint.

    Args:
        api_endpoint: The URL of the Google API endpoint.
        data: (Optional) Dictionary of data to send in the request body (for POST, PUT, etc.).

    Returns:
        The response from the Google API.
    """
    # Get access token using default credentials (will use Cloud Shell's auth)
    creds, project = google.auth.default()
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    access_token = creds.token

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    print(f"Sending request to: {api_endpoint}")
    response = requests.post(api_endpoint, headers=headers, json=data)
    response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
    return response.json()


def generate_music(prompt_request: dict):
    """
    Generates music using the Lyria 2 model.

    Args:
        prompt_request: A dictionary containing the prompt, negative_prompt, and sample_count/seed.
                        Example: {"prompt": "smooth jazz", "sample_count": 1}
    Returns:
        A list of predictions (audio data).
    """
    req = {"instances": [prompt_request], "parameters": {}}
    print(f"Request payload: {json.dumps(req, indent=2)}")
    resp = send_request_to_google_api(MUSIC_MODEL_ENDPOINT, req)
    print(resp)
    return resp["predictions"]

def generate_song_chunks(prompt_chunks_list: dict) -> list[dict]:
    """
    Iterates through a list of book chunks, generates music for each chunk's prompt,
    saves the generated audio to the SONGS_DIR, and returns a list of dictionaries with
    music file paths and line numbers.

    Args:
        prompt_chunks_list: A dictionary in the format of ChunksList,
                            e.g., {"chunks": [{"music_prompt": "...", "starting_line_number": ..., ...}]}

    Returns:
        A list of dictionaries, where each dictionary contains:
        - "music_file_path": The path to the saved WAV file for the chunk (e.g., "./songs/lyria_chunk_1.wav").
        - "start_line": The starting line number of the text chunk.
        - "end_line": The ending line number of the text chunk.
    """
    # Create the songs directory if it doesn't exist
    os.makedirs(SONGS_DIR, exist_ok=True)
    print(f"Ensured '{SONGS_DIR}' directory exists.")

    processed_chunks = []
    # Access the 'chunks' list within the passed dictionary
    for i, chunk_data in enumerate(prompt_chunks_list.get("chunks", [])):
        music_prompt = chunk_data.get("music_prompt")
        starting_line = chunk_data.get("starting_line_number")
        ending_line = chunk_data.get("ending_line_number")

        if not music_prompt:
            print(f"Warning: Chunk {i} has no music_prompt. Skipping music generation.")
            continue

        print(f"\n--- Generating music for Chunk {i+1} (Lines {starting_line}-{ending_line}) ---")
        # Prepare the prompt for the Lyria model
        lyria_prompt_request = {
            "prompt": music_prompt,
            "sample_count": 1 # Generate one audio sample per prompt
        }

        print(f"Request {i}: {lyria_prompt_request}")

        # Generate music
        predictions = generate_music(lyria_prompt_request)
        print(predictions) 
        if predictions:
            # Assuming we get at least one prediction and want the first one
            bytes_b64 = predictions[0]["bytesBase64Encoded"]
            decoded_audio_data = base64.b64decode(bytes_b64)

        print("writing to audio file")
        # Create a unique filename for the audio chunk within the SONGS_DIR
        output_filename = os.path.join(SONGS_DIR, f"lyria_chunk_{i+1}_lines_{starting_line}-{ending_line}.wav")
        with open(output_filename, "wb") as f:
            f.write(decoded_audio_data)
        print(f"Saved audio for chunk {i+1} to: {output_filename}")

        processed_chunks.append({
            "music_file_path": output_filename, # This now stores the path to the actual file
            "start_line": starting_line,
            "end_line": ending_line,
        })

    return processed_chunks


if __name__=="__main__":
    print(generate_song_chunks(generate_prompt_chunks(FORMATTED_LINE)))