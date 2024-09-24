from dataclasses import dataclass, field
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta
from typing import Optional

""" To Do
Demo Requirements
[x] Make msgs print once
[x] Log time delta in message
[x] Monitor event queue to any mistakes
[x] Monitor msg history for any duplicates
[ ] How should responses work (MVP)
[ ] Generate responses
[ ] Upgrade the chat sidebar to incorproate responses
[ ] Hook up to API

Nice to Have
[ ] Enable response typing bubbles
[ ] Enable response pausing (remove bubbles)
[ ] Make sidebar have a 'siri' like chat icon
[x] Put chat in bubbles
[x] Add time sent underneath chat bubbles
[ ] Enable read receipts

Bugs
[ ] Status should not start as 'stopped' should be empty
"""

@dataclass
class Message:
    content: str = ""
    role: str = ""

@dataclass
class Event:
    message: Message = field(default_factory=Message)
    action: str = ""
    timestamp: datetime = None

def create_event(data):
    return Event(
        message=create_msg(data),
        action=data["action"],
        timestamp=datetime.now(),
    )

def create_msg(data) -> Message:
    return Message(content=data["content"], role=data["role"])

app = Flask(__name__)
socketio = SocketIO(app)

# Contains all chat messages send and recv
chat_history = []

# Contains last 10 chat events (send, recv, typing, pausing, stopping)
event_cache = []

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("message")
def handle_message(data):
    event = create_event(data)
    log_event(event)
    emit("message", data, broadcast=False)

# Split on the spaces and count the words
# Edge case: When previous msg is "" we register the first new letter typed
def words_changed(new_msg: Message, old_msg: Message) -> bool:
    new_length = len(new_msg.content.split())
    old_length = len(old_msg.content.split())

    return False if new_length - old_length == 0 else True

def isRelevant(event: Event) -> bool:
    relevant_actions = ["paused", "stopped", "full stop", "sent"]
    # If paused or stopped
    if event.action in relevant_actions:
        return True

    last_event = event_cache[-1] if len(event_cache) > 0 else Event()
    # If previously relevant
    if last_event.action in relevant_actions:
        return True

    # Adding and Deleting are only relevant when more than a word is altered
    if words_changed(event.message, last_event.message) != 0:
        return True

    return False

@socketio.on("typing")
def handle_typing(data):
    event = create_event(data)
    if isRelevant(event):
        log_event(event)

    emit("typing", data, broadcast=True)

def respond_to_user():
    content = "Yeh that's pretty intense."
    response = {'content': content,
                'role' : "responder"}
    emit("user-response", response, broadcast=True)

def backseat_response():
    content = "Boiler plate response to get your anxious."
    response = {"content": content, "role": "backseat"}
    emit("backseat-response", response, broadcast=True)

@socketio.on("response")
def handle_response(data):
    backseat_response()
    respond_to_user()

EVENT_CACHE_LIMIT = 25
def log_event(event: Event):
    if len(event_cache) == EVENT_CACHE_LIMIT:
        event_cache.pop(0)
    event_cache.append(event)
    for event in event_cache:
        if event.action != 'paused' or event.action != 'stopped':
            print(event)

if __name__ == "__main__":
    socketio.run(app, debug=True)