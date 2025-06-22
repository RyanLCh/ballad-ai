import os
import logging
from deepgram.utils import verboselogs
from dotenv import load_dotenv

load_dotenv()
from deepgram import (
    DeepgramClient,
    SpeakOptions,
)

SPEAK_TEXT = {"text": '''The morning of June 27th was clear and sunny, with the fresh warmth of a full-summer day; the flowers
were blossoming profusely and the grass was richly green. The people of the village began to gather in
the square, between the post office and the bank, around ten o'clock; in some towns there were so many
people that the lottery took two days and had to be started on June 2th. but in this village, where there
were only about three hundred people, the whole lottery took less than two hours, so it could begin at ten
o'clock in the morning and still be through in time to allow the villagers to get home for noon dinner.'''}

filename = "narration.mp3"

def main():
    try:
        # STEP 1 Create a Deepgram client using the API key from environment variables
        deepgram = DeepgramClient()

        # STEP 2 Call the save method on the speak property
        options = SpeakOptions(
            model="aura-2-draco-en",
        )

        response = deepgram.speak.rest.v("1").save(filename, SPEAK_TEXT, options)
        print(response.to_json(indent=4))

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    main()
