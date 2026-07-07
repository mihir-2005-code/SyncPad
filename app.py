from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
from datetime import datetime
import uuid
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory storage for documents.
documents = {}

DEFAULT_ROOM = "main"


def get_or_create_room(room_id):
    """Fetch a room's document state, creating it if it doesn't exist yet."""
    if room_id not in documents:
        documents[room_id] = {
            "content": "",
            "users": {},
            "version": 0
        }
    return documents[room_id]


@app.route("/")
def home():
    return render_template("index.html")


@socketio.on("connect")
def handle_connect():
    print(f"Client connected: {request.sid}")


@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    for room_id, room in documents.items():
        if sid in room["users"]:
            username = room["users"].pop(sid)
            emit(
                "user_left",
                {
                    "username": username,
                    "active_users": list(room["users"].values())
                },
                room=room_id
            )
            print(f"{username} disconnected from room {room_id}")


@socketio.on("join_document")
def handle_join(data):
    room_id = data.get("room", DEFAULT_ROOM)
    username = data.get("username", f"User-{uuid.uuid4().hex[:4]}")
    sid = request.sid

    join_room(room_id)
    room = get_or_create_room(room_id)
    room["users"][sid] = username

    emit(
        "document_state",
        {
            "content": room["content"],
            "version": room["version"],
            "active_users": list(room["users"].values())
        }
    )

    emit(
        "user_joined",
        {
            "username": username,
            "active_users": list(room["users"].values())
        },
        room=room_id,
        include_self=False
    )

    print(f"{username} joined room {room_id}")


@socketio.on("edit_document")
def handle_edit(data):
    room_id = data.get("room", DEFAULT_ROOM)
    content = data.get("content", "")
    username = data.get("username", "Unknown")
    client_version = data.get("version", 0)

    room = get_or_create_room(room_id)

    stale_edit = client_version < room["version"]

    room["content"] = content
    room["version"] += 1

    emit(
        "document_updated",
        {
            "content": content,
            "version": room["version"],
            "editor": username,
            "timestamp": datetime.utcnow().isoformat(),
            "stale_edit": stale_edit
        },
        room=room_id
    )


@socketio.on("cursor_position")
def handle_cursor(data):
    room_id = data.get("room", DEFAULT_ROOM)

    emit(
        "cursor_update",
        {
            "username": data.get("username"),
            "position": data.get("position")
        },
        room=room_id,
        include_self=False
    )


if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )