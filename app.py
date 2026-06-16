from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
from datetime import datetime
import uuid

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key-change-in-production"
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory storage for documents.
# Structure: { room_id: { "content": str, "users": {sid: username}, "version": int } }
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
            emit("user_left", {
                "username": username,
                "active_users": list(room["users"].values())
            }, room=room_id)
            print(f"{username} disconnected from room {room_id}")


@socketio.on("join_document")
def handle_join(data):
    """
    A user joins a document room.
    data = { "room": str, "username": str }
    """
    room_id = data.get("room", DEFAULT_ROOM)
    username = data.get("username", f"User-{uuid.uuid4().hex[:4]}")
    sid = request.sid

    join_room(room_id)
    room = get_or_create_room(room_id)
    room["users"][sid] = username

    # Send the current document state to the joining user
    emit("document_state", {
        "content": room["content"],
        "version": room["version"],
        "active_users": list(room["users"].values())
    })

    # Notify everyone else in the room
    emit("user_joined", {
        "username": username,
        "active_users": list(room["users"].values())
    }, room=room_id, include_self=False)

    print(f"{username} joined room {room_id}")


@socketio.on("edit_document")
def handle_edit(data):
    """
    A user edits the document.
    data = { "room": str, "content": str, "username": str, "version": int }

    Conflict resolution strategy: last-write-wins with version tracking.
    Every edit increments the version number. If a client's version is
    stale (lower than the server's), we still apply the edit but flag
    the client to refresh, since a more recent edit may have been missed.
    """
    room_id = data.get("room", DEFAULT_ROOM)
    content = data.get("content", "")
    username = data.get("username", "Unknown")
    client_version = data.get("version", 0)

    room = get_or_create_room(room_id)

    stale_edit = client_version < room["version"]

    room["content"] = content
    room["version"] += 1

    broadcast_payload = {
        "content": content,
        "version": room["version"],
        "editor": username,
        "timestamp": datetime.utcnow().isoformat(),
        "stale_edit": stale_edit
    }

    # Broadcast the update to everyone in the room, including sender
    # (sender needs the authoritative version number back)
    emit("document_updated", broadcast_payload, room=room_id)


@socketio.on("cursor_position")
def handle_cursor(data):
    """
    Broadcast a user's cursor position to others in the room, so
    collaborators can see where everyone is editing.
    data = { "room": str, "username": str, "position": int }
    """
    room_id = data.get("room", DEFAULT_ROOM)
    emit("cursor_update", {
        "username": data.get("username"),
        "position": data.get("position")
    }, room=room_id, include_self=False)


if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)