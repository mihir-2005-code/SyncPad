# Real-Time Collaborative Document Editor

A real-time collaborative document editor built with **Flask**, **Flask-SocketIO**, and **WebSockets**. Multiple users can join the same room and edit a shared document simultaneously while viewing active collaborators and live updates.

## Features

* Real-time document synchronization
* Multi-user collaboration
* Room-based document editing
* Live presence tracking
* User join/leave notifications
* Version tracking
* Cursor position broadcasting
* Responsive modern UI
* WebSocket-powered communication

---

## Tech Stack

### Backend

* Python
* Flask
* Flask-SocketIO

### Frontend

* HTML5
* CSS3
* JavaScript

### Real-Time Communication

* Socket.IO
* WebSockets

---

## Project Structure

```text
SyncPad/
│
├── app.py
│
├── templates/
│   └── index.html
│
├── static/
│   ├── style.css
│   └── script.js
│
│
└── README.md
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/your-username/collab-tool.git
cd collab-tool
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

Linux / macOS:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Required Packages

Create a `requirements.txt` file:

```txt
Flask
Flask-SocketIO
eventlet
```

Install:

```bash
pip install -r requirements.txt
```

---

## Running the Application

```bash
python app.py
```

Server will start on:

```text
http://localhost:5000
```

---

## How It Works

### Joining a Room

Users enter:

* Username
* Room ID

and join a collaborative editing session.

### Document Synchronization

Whenever a user edits the document:

1. Changes are sent to the server.
2. Server updates the document state.
3. Updated content is broadcast to all connected users.
4. Version number is incremented.

### Conflict Resolution

Current implementation uses:

```text
Last Write Wins (LWW)
```

Each update contains:

* Document content
* Version number
* Editor name
* Timestamp

If a stale version is detected, the update is flagged.

---

## Socket Events

### Client → Server

#### join_document

```json
{
  "room": "main",
  "username": "John"
}
```

#### edit_document

```json
{
  "room": "main",
  "content": "Updated text",
  "username": "John",
  "version": 3
}
```

#### cursor_position

```json
{
  "room": "main",
  "username": "John",
  "position": 120
}
```

---

### Server → Client

#### document_state

Sends current document state to newly joined user.

#### document_updated

Broadcasts document updates.

#### user_joined

Notifies room when a user joins.

#### user_left

Notifies room when a user leaves.

#### cursor_update

Broadcasts cursor movements.

---

## Future Improvements

* Persistent database storage (MongoDB/PostgreSQL)
* Operational Transformation (OT)
* CRDT-based collaboration
* Authentication & authorization
* Document history
* Rich text editor
* Multiple document support
* File export (PDF/DOCX)
* Typing indicators
* User avatars

---

## Screenshots

Add screenshots here after deployment.

```markdown
![Home Page](screenshots/home.png)
```

---

## Deployment

You can deploy this application on:

* Render
* Railway
* Heroku
* AWS EC2
* Azure App Service
* DigitalOcean

---

## Learning Outcomes

This project demonstrates:

* Real-time systems
* WebSocket communication
* Event-driven architecture
* Flask backend development
* Collaborative software design
* Version management concepts
* Multi-user synchronization

---

## License

MIT License

---

## Author

Your Name

GitHub: https://github.com/your-username
LinkedIn: https://linkedin.com/in/your-profile
