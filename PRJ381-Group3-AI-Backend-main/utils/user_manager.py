# utils/user_manager.py
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

USERS_DIR = Path(__file__).resolve().parent.parent / "interview" / "users"
USERS_DIR.mkdir(parents=True, exist_ok=True)

def generate_unique_user_id() -> str:
    while True:
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        if not (USERS_DIR / f"{user_id}.json").exists():
            return user_id

def create_user(name: str, email: str) -> Dict:
    user_id = generate_unique_user_id()
    path = USERS_DIR / f"{user_id}.json"
    if path.exists():
        raise FileExistsError(f"User '{user_id}' already exists.")
    user = {
        "user_id": user_id,
        "name": name,
        "email": email,
        "created_at": datetime.utcnow().isoformat(),
        "sessions": [],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(user, f, indent=2)
    return user

def load_user(user_id: str) -> Optional[Dict]:
    path = USERS_DIR / f"{user_id}.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def update_user(user_id: str, updates: Dict) -> Optional[Dict]:
    user = load_user(user_id)
    if not user:
        return None
    user.update(updates)
    with open(USERS_DIR / f"{user_id}.json", "w", encoding="utf-8") as f:
        json.dump(user, f, indent=2)
    return user

def delete_user(user_id: str) -> bool:
    path = USERS_DIR / f"{user_id}.json"
    if path.exists():
        path.unlink()
        return True
    return False

def list_users() -> List[str]:
    return [f.stem for f in USERS_DIR.glob("*.json") if f.is_file()]

def append_session_to_user(user_id: str, session_id: str) -> bool:
    user = load_user(user_id)
    if not user:
        return False
    if session_id not in user.get("sessions", []):
        user.setdefault("sessions", []).append(session_id)
        with open(USERS_DIR / f"{user_id}.json", "w", encoding="utf-8") as f:
            json.dump(user, f, indent=2)
    return True

def user_exists(user_id: str) -> bool:
    return (USERS_DIR / f"{user_id}.json").exists()

def email_exists(email: str) -> bool:
    for user_file in USERS_DIR.glob("*.json"):
        with open(user_file, "r", encoding="utf-8") as f:
            user = json.load(f)
            if user.get("email") == email:
                return True
    return False
