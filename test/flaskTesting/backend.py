from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit, join_room, leave_room

app = Flask(__name__)
app.config["SECRET_KEY"] = "lol_secret_key"

socketio = SocketIO(app)
users = {}


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("join")
def handle_join(username):
    users[request.sid] = username
    emit("message", f"{username} joined the chat", broadcast=True)


@socketio.on("message")
def handle_message(data):
    username = users.get(request.sid, "Anonymous")
    emit("message", f"{username}: {data}", broadcast=True)


@socketio.on("disconnect")
def handle_disconnect():
    username = users.pop(request.sid, "Anonymous")
    emit("message", f"{username} left the chat", broadcast=True)


if __name__ == "__main__":
    socketio.run(app, debug=True, port=5001)
