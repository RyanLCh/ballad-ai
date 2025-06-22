import base64
import os
import json
from IPython.display import Audio, display # These are for Jupyter/IPython environment
import google.auth
import google.auth.transport.requests
import requests
import sys

# --- Configuration ---
# Replace with your actual Google Cloud Project ID
PROJECT_ID = "balladai-463622"

# Lyria 2 model endpoint. This is fixed for the public model.
# Make sure Lyria 2 is available in 'us-central1' in your project.
MUSIC_MODEL_ENDPOINT = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models/lyria-002:predict"

# --- Helper Functions (from your notebook) ---

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
    return resp["predictions"]


def play_audio(preds):
    """
    Decodes and displays base64 encoded audio from Lyria predictions.
    This function is primarily for Jupyter/IPython environments.
    For Cloud Shell, it will attempt to display, but direct playback
    in the terminal isn't supported without specific tools.
    You'd typically download the WAV file to listen.
    """
    for i, pred in enumerate(preds):
        bytes_b64 = dict(pred)["bytesBase64Encoded"]
        decoded_audio_data = base64.b64decode(bytes_b64)

        output_filename = f"lyria_output_{i}.wav"
        with open(output_filename, "wb") as f:
            f.write(decoded_audio_data)
        print(f"Audio saved to {output_filename}")

        # Attempt to play in environments that support IPython.display.Audio
        if "ipykernel" in sys.modules or "google.colab" in sys.modules:
            audio = Audio(decoded_audio_data, rate=48000, autoplay=False)
            display(audio)
        else:
            print(f"To listen to '{output_filename}', download it from Cloud Shell.")

# --- Main Execution ---
if __name__ == "__main__":
    print("--- Lyria 2 Music Generation Example ---")
    print("Ensure Vertex AI API is enabled in your project and you have 'Vertex AI User' role.")
    print(f"Using Project ID: {PROJECT_ID}")

    # --- Example 1: Generate smooth jazz ---
    print("\n--- Generating Smooth Jazz ---")
    prompt_jazz = {
        "prompt": "Smooth, atmospheric jazz. Moderate tempo, rich harmonies. Featuring mellow brass",
        "negative_prompt": "fast",
        "sample_count": 1 # Generating 1 sample for quick demonstration
    }
    try:
        music_jazz = generate_music(prompt_jazz)
        play_audio(music_jazz)
    except requests.exceptions.HTTPError as e:
        print(f"Error generating jazz music: {e}")
        print(f"Response content: {e.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    # --- Example 2: Generate dramatic dance symphony with a seed ---
    # print("\n--- Generating Dramatic Dance Symphony (with seed) ---")
    # prompt_symphony = {
    #     "prompt": "Dramatic dance symphony",
    #     "negative_prompt": "",
    #     "seed": 111 # Use seed for deterministic generation (cannot be combined with sample_count)
    # }
    # try:
    #     music_symphony = generate_music(prompt_symphony)
    #     play_audio(music_symphony)
    # except requests.exceptions.HTTPError as e:
    #     print(f"Error generating symphony music: {e}")
    #     print(f"Response content: {e.response.text}")
    # except Exception as e:
    #     print(f"An unexpected error occurred: {e}")

    print("\n--- Script Finished ---")