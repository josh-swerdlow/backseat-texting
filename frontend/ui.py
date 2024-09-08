import streamlit as st
import random
import json
from backend.main import generate_summary, generate_response, Message
from datetime import datetime, timedelta
import pygame
from text_to_speech import audio
import time

USE_API = False

# Initialize pygame mixer
pygame.mixer.init()

current_summary = ""
current_message_context = []
starter_text = """
[
  {
    "role": "J",
    "content": "Hey! Are you coming to the game night tomorrow?"
  },
  {
    "role": "C",
    "content": "Hey! I’m not sure yet. I have a lot of work to catch up on. What time does it start?"
  },
  {
    "role": "J",
    "content": "It starts at 7 PM. But no pressure! We’re just playing some casual board games."
  },
  {
    "role": "C",
    "content": "That sounds fun! I’ll try to make it, but if I’m late, just start without me."
  },
  {
    "role": "J",
    "content": "No worries at all. Just come if you can. We’ll save you a spot!"
  }
]
"""


def json_message_to_class(json_message):
    return Message(
        role=json_message["role"],
        content=json_message["content"],
        timestamp=datetime.now(),
    )


# Streamed response emulator
def response_generator():
    response = random.choice(
        [
            "Hello there! How can I assist you today?",
            "Hi, human! Is there anything I can help you with?",
            "Do you need help?",
        ]
    )
    return response


# Set page layout to wide
st.set_page_config(layout="wide")

st.title("Text Messages")

# Initialize chat history
if "messages" not in st.session_state:
    dump = json.loads(starter_text)
    st.session_state.messages = []
    for msg in dump:
        st.session_state.messages.append(msg)

# Initialize typing state tracking
if "last_input" not in st.session_state:
    st.session_state.last_input = ""
    st.session_state.last_input_time = datetime.now()

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Text input for user response
message = st.text_input(
    label="Response form", label_visibility="hidden", key="input_value"
)

# Detect typing and pause
current_time = datetime.now()
current_input = st.session_state.get("input_value", "")

# Check for pause in typing
if current_input != st.session_state.last_input:
    # User is typing
    st.write("User is typing...")
    st.session_state.last_input = current_input
    st.session_state.last_input_time = current_time
else:
    # Check if pause has been detected (1-second threshold)
    time_since_last_input = current_time - st.session_state.last_input_time
    if time_since_last_input > timedelta(seconds=1) and current_input:
        st.write("User paused typing. Current text:", current_input)

# Accept user input
if message:
    print(f"Text detected: {message}")

    # Send message
    with st.chat_message("Josh"):
        new_message = {"role": "J", "content": message}
        st.session_state.messages.append(new_message)
        st.markdown(message)

    # Send comment back on events
    with st.sidebar:
        st.header("Backseat Texter")

        # Generate message class
        messages = [json_message_to_class(msg) for msg in current_message_context]

        # Generate a response or comment
        comment = (
            generate_response(current_summary, [json_message_to_class(new_message)], 7)
            if USE_API
            else "This is a comment"
        )

        st.write(comment)

        # Play audio if USE_API is enabled
        if USE_API:
            audio(comment)
            pygame.mixer.music.load("speech.mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(1)

    # Update message context
    current_message_context.append(new_message)
    if len(current_message_context) > 5:
        current_message_context.pop()

    # Update summary if using API
    current_summary = (
        generate_summary(current_summary, messages) if USE_API else "This is a summary"
    )

    # Display response
    with st.chat_message("Christina"):
        comment = response_generator() if USE_API else "Ugh, such a weird thing to say."
        st.session_state.messages.append({"role": "C", "content": comment})
        st.write(comment)
