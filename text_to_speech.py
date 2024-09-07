import os
import sys

from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI

# load environmental variables from .env file
load_dotenv()

# set OpenAI client
client = OpenAI(
  api_key=os.getenv("OPENAI_API_KEY"),
)

# make audio file
def audio(response_string="give me a string!"):
  speech_file_path = Path(__file__).parent / "speech.mp3"
  response = client.audio.speech.create(
    model="tts-1",
    voice="nova",
    input=response_string
  )

  response.stream_to_file(speech_file_path)

if __name__ == '__main__':
  audio(response_string=str(sys.argv))