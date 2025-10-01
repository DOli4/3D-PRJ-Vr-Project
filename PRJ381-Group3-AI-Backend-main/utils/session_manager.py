# utils/session_manager.py
import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

SESSIONS_DIR = Path(__file__).resolve().parent.parent / "interview" / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)

def generate_unique_session_id() -> str:
    while True:
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        if not (SESSIONS_DIR / f"{session_id}.json").exists():
            return session_id

def _is_valid_session(session: dict) -> bool:
    required = {"session_id", "user_id", "role", "level", "created_at", "questions"}
    return isinstance(session, dict) and required.issubset(session.keys())

def create_session(user_id: str, role: str, level: int) -> Dict:
    session_id = generate_unique_session_id()
    session = {
        "session_id": session_id,
        "user_id": user_id,
        "role": role,
        "level": level,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "questions": []
    }
    path = SESSIONS_DIR / f"{session_id}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(session, f, indent=2)
    logging.info(f"Created session: {session_id} for user: {user_id}")
    return session

def load_session(session_id: str) -> Optional[Dict]:
    path = SESSIONS_DIR / f"{session_id}.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        session = json.load(f)
        return session if _is_valid_session(session) else None

def list_sessions(user_id: Optional[str] = None) -> List[str]:
    sessions = []
    for file in SESSIONS_DIR.glob("session_*.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if _is_valid_session(data) and (user_id is None or data["user_id"] == user_id):
                    sessions.append(data["session_id"])
        except Exception as e:
            logging.warning(f"Skipping invalid session file {file.name}: {e}")
    return sessions

def append_question(session_id: str, question_data: Dict) -> bool:
    session = load_session(session_id)
    if not session:
        logging.error(f"Cannot append question; session '{session_id}' not found.")
        return False
    session["questions"].append(question_data)
    try:
        with open(SESSIONS_DIR / f"{session_id}.json", "w", encoding="utf-8") as f:
            json.dump(session, f, indent=2)
        return True
    except Exception as e:
        logging.error(f"Failed to update session {session_id}: {e}")
        return False

def update_question_grade(session_id: str, question_number: int, grade: Dict, score: float) -> bool:
    """
    Updates a specific question in the session with its grade and score.
    """
    session = load_session(session_id)
    if not session:
        logging.error(f"Session '{session_id}' not found.")
        return False

    questions = session.get("questions")
    if not questions or question_number < 1 or question_number > len(questions):
        logging.error(f"Invalid question number {question_number} in session '{session_id}'.")
        return False

    q = questions[question_number - 1]
    q["grade"] = grade
    q["score"] = round(score, 3) if isinstance(score, (int, float)) else None

    try:
        with open(SESSIONS_DIR / f"{session_id}.json", "w", encoding="utf-8") as f:
            json.dump(session, f, indent=2)
        return True
    except Exception as e:
        logging.error(f"Failed to update question {question_number} in session '{session_id}': {e}")
        return False

def update_session_feedback(session_id: str, feedback_list: list, final_score: float) -> bool:
    """
    Updates the session with feedback and final_score fields.
    """
    session = load_session(session_id)
    if not session:
        logging.error(f"Session '{session_id}' not found.")
        return False

    session["feedback"] = feedback_list
    session["score"] = round(final_score, 3)

    try:
        with open(SESSIONS_DIR / f"{session_id}.json", "w", encoding="utf-8") as f:
            json.dump(session, f, indent=2)
        logging.info(f"✅ Updated session {session_id} with feedback and score.")
        return True
    except Exception as e:
        logging.error(f"❌ Failed to update session feedback: {e}")
        return False


def delete_session(session_id: str) -> bool:
    path = SESSIONS_DIR / f"{session_id}.json"
    if path.exists():
        path.unlink()
        logging.info(f"Deleted session: {session_id}")
        return True
    return False

def session_exists(session_id: str) -> bool:
    return (SESSIONS_DIR / f"{session_id}.json").exists()
