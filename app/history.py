import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Dict

SESSIONS_DIR = Path("chat_sessions")
SESSIONS_DIR.mkdir(exist_ok=True)

def create_session() -> str:
    """Creates a new empty session and returns its ID."""
    session_id = str(uuid.uuid4())
    session_file = SESSIONS_DIR / f"{session_id}.json"
    
    session_data = {
        "id": session_id,
        "created_at": datetime.now().isoformat(),
        "messages": []
    }
    
    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)
        
    return session_id

def get_session(session_id: str) -> Dict:
    """Retrieves session data by ID. Returns None if not found."""
    session_file = SESSIONS_DIR / f"{session_id}.json"
    if not session_file.exists():
        return None
        
    with open(session_file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_message(session_id: str, role: str, content: str):
    """Appends a message to the session history."""
    session_data = get_session(session_id)
    if not session_data:
        raise ValueError("Session not found")
        
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    
    session_data["messages"].append(message)
    
    session_file = SESSIONS_DIR / f"{session_id}.json"
    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)

def list_sessions() -> List[Dict]:
    """Lists all available sessions, sorted by creation date (newest first)."""
    sessions = []
    for file_path in SESSIONS_DIR.glob("*.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                sessions.append({
                    "id": data["id"],
                    "created_at": data["created_at"],
                    "message_count": len(data.get("messages", []))
                })
        except Exception:
            continue
            
    # Sort by created_at descending
    sessions.sort(key=lambda x: x["created_at"], reverse=True)
    return sessions
