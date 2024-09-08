from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# In-memory storage for chat messages
chat_history = []

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("message")
def handle_message(data):
    # Broadcast the message to all clients
    chat_history.append(data)
    emit("message", data, broadcast=True)

@socketio.on("typing")
def handle_typing(data):
    # Broadcast typing event to all clients
    emit("typing", data, broadcast=True)


if __name__ == "__main__":
    socketio.run(app, debug=True)
