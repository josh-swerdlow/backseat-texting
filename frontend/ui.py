import streamlit as st
import random
import time
import json

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

# Streamed response emulator
def response_generator():
    response = random.choice(
        [
            "Hello there! How can I assist you today?",
            "Hi, human! Is there anything I can help you with?",
            "Do you need help?",
        ]
    )
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

# Set page layout to wide
st.set_page_config(layout="wide")

st.title("Text Messages")

# Initialize chat history
if "messages" not in st.session_state:
    dump = json.loads(starter_text)
    st.session_state.messages = []
    for msg in dump:
        st.session_state.messages.append(msg)

# Define a function to simulate typing pause detection
def detect_typing_pause(text_input):
    # Add logic to simulate typing pause detection
    if text_input:
        st.session_state["input_value"] = text_input
        st.write("User paused typing. Current text:", text_input)
    else:
        st.session_state["input_value"] = ""

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if message := st.chat_input():
    # Simulate typing pause detection
    detect_typing_pause(message)

    # Send message
    with st.chat_message("Josh"):
        st.session_state.messages.append({"role": "J", "content": message})
        st.markdown(message)

    # Recv response
    with st.chat_message("Christina"):
        response = st.write_stream(response_generator())
        st.session_state.messages.append({"role": "C", "content": response})

# Send comment back on events
with st.sidebar:
    st.header("Backseat Texter")

    # Fetch comment
    comment = "ugh what a bad response"
    st.write(comment)
