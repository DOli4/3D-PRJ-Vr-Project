# pipeline/session_pipeline.py
"""
High-level operations that coordinate user and session management.
"""

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import logging
from typing import Dict, Optional, List
from pathlib import Path

ROLES_DIR = Path(__file__).resolve().parent.parent / "interview" / "roles"

from utils import user_manager, session_manager, question_selector
from pipeline import answer_score

roles = [d.name for d in ROLES_DIR.iterdir() if d.is_dir()]

def create_user_pipeline(name: str, email: str) -> Dict:
    """
    Create a new user.
    """
    if user_manager.email_exists(email):
        raise ValueError(f"Email '{email}' is already in use.")
    return user_manager.create_user(name, email)

def create_session_pipeline(user_id: str, role: str, level: int) -> Dict:
    """
    Create a new session and link it to the user.
    """
    if not user_manager.user_exists(user_id):
        raise ValueError(f"User '{user_id}' does not exist.")
    
    if role not in roles:
        raise ValueError(f"Invalid role '{role}'. Must be one of {', '.join(roles)}.")
    
    session = session_manager.create_session(user_id, role, level)
    user_manager.append_session_to_user(user_id, session["session_id"])
    return session

def append_question_to_session(session_id: str, question_data: Dict) -> bool:
    """
    Add a scored question to an existing session.
    """
    if not session_manager.session_exists(session_id):
        raise ValueError(f"Session '{session_id}' does not exist.")
    return session_manager.append_question(session_id, question_data)

def finalize_session(session_id: str, final_score: float, summary_feedback: str) -> bool:
    """
    Write the final score and feedback into the session.
    """
    if not session_manager.session_exists(session_id):
        raise ValueError(f"Session '{session_id}' does not exist.")
    return session_manager.update_session_scores(session_id, final_score, summary_feedback)

def get_user_sessions(user_id: str) -> Optional[Dict]:
    """
    Retrieve all session IDs for a user.
    """
    if not user_manager.user_exists(user_id):
        raise ValueError(f"User '{user_id}' does not exist.")
        return None
    return user_manager.load_user(user_id).get("sessions", [])

def get_session_details(session_id: str) -> Optional[Dict]:
    """
    Load full session data by ID.
    """
    return session_manager.load_session(session_id)

def get_questions_for_session(session_id: str) -> List[Dict]:
    """
    Fetches a set of questions for the session's role and level.
    """
    session = session_manager.load_session(session_id)
    if session is None:
        # logging.info(f"Session '{session_id}' not found. --1")
        raise ValueError(f"Session '{session_id}' not found.")
    
    role = session.get("role")
    level = session.get("level")

    # logging.info(f"🔍 Fetching questions for session '{session_id}' with role='{role}' and level={level}")

    if not role or level is None:
        # logging.info(f"Session '{session_id}' is missing role or level. --2")
        raise ValueError(f"Session '{session_id}' is missing role or level.")

    return question_selector.select_questions_by_level(role, level)

def score_questions(session_id: str) -> Dict:
    """
    Loops through all questions in a session and scores any that are ungraded.
    Returns a summary with which questions were updated.
    """
    logging.info(f"🔍 Starting scoring for session '{session_id}'")

    session = session_manager.load_session(session_id)
    if session is None:
        logging.error(f"❌ Session '{session_id}' not found.")
        raise ValueError(f"Session '{session_id}' not found.")

    questions = session.get("questions")
    if not questions:
        logging.warning(f"⚠️ No questions found in session '{session_id}'.")
        raise ValueError(f"No questions in session '{session_id}'.")

    scored_questions = []
    errors = []

    for idx, q in enumerate(questions):
        logging.info(f"➡️ Processing question index {idx}")

        if not isinstance(q, dict):
            msg = f"❌ Question at index {idx} is not a valid dictionary."
            logging.warning(msg)
            errors.append(msg)
            continue

        if q.get("grade") is not None:
            logging.info(f"⏩ Skipping question at index {idx} (already graded)")
            continue

        question_id = q.get("question_id")
        answer = q.get("answer")

        if not question_id:
            msg = f"❌ Question at index {idx} is missing 'question_id'."
            logging.warning(msg)
            errors.append(msg)
            continue
        if not answer:
            msg = f"❌ Question '{question_id}' is missing answer."
            logging.warning(msg)
            errors.append(msg)
            continue

        logging.info(f"🔎 Fetching full question data for ID '{question_id}'")
        question = question_selector.find_question_by_id(session.get("role"), question_id)

        if not question:
            msg = f"❌ Could not find question data for ID '{question_id}'"
            logging.error(msg)
            errors.append(msg)
            continue

        qna_package = {
            "id": question_id,
            "question": question.get("question"),
            "role": question.get("role"),
            "difficulty": question.get("difficulty"),
            "type": question.get("type"),
            "answer": answer,
            "ideal": question.get("ideal", []),
            "keywords": question.get("keywords", []),
            "weights": question.get("weights", {})
        }        

        try:
            logging.info(f"🧠 Scoring question ID '{question_id}'")
            logging.info("📦 Q&A Package for scoring:\n%s", json.dumps(qna_package, indent=2))

            scoring = answer_score.score_answer(qna_package)
            grade = scoring.get("modules")
            score = scoring.get("final_score")

            session_manager.update_question_grade(
                session_id, idx + 1, grade, score
            )

            scored_questions.append(idx + 1)
            logging.info(f"✅ Scored question {question_id} with final score: {score}")
        except Exception as e:
            msg = f"❌ Error scoring question {question_id}: {e}"
            logging.exception(msg)
            errors.append(msg)

    logging.info(f"🏁 Finished scoring. Total scored: {len(scored_questions)}")

    if errors:
        logging.warning(f"⚠️ Scoring completed with {len(errors)} issues.")

    return {
        "status": "ok",
        "scored_count": len(scored_questions),
        "questions_scored": scored_questions,
        "errors": errors  # Optional: you can remove this from response if not needed
    }

def generate_session_feedback(session_id: str) -> Dict:
    """
    Aggregates all question grades in a session and generates feedback per module.
    Also computes and stores the session's final score.
    """
    session = session_manager.load_session(session_id)
    if session is None:
        raise ValueError(f"Session '{session_id}' not found.")

    questions = session.get("questions", [])
    if not questions:
        raise ValueError("No questions in session.")

    grades = [q.get("grade") for q in questions if isinstance(q.get("grade"), dict)]
    if not grades:
        raise ValueError("No graded questions found. Run scoring first.")

    feedback = answer_score.get_feedback(grades)

    final_score = round(
        sum(q.get("score", 0.0) for q in questions if isinstance(q.get("score"), (float, int)))
        / len(grades),
        3
    )

    success = session_manager.update_session_feedback(session_id, feedback, final_score)
    if not success:
        raise ValueError("Failed to save feedback to session.")

    return {
        "status": "ok",
        "final_score": final_score,
        "feedback": feedback
    }

if __name__ == "__main__":
    import os, sys, json, time
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

    # Hardcoded test session ID (must exist in your sessions/ directory)
    session_id = "session_87efed84"

    print(f"🔍 Testing get_questions_for_session with session_id='{session_id}'\n")

    try:
        session = session_manager.load_session(session_id)
        if not session:
            print(f"❌ Session '{session_id}' not found.")
            sys.exit(1)

        print(f"ℹ️  Session: role='{session.get('role')}', level={session.get('level')}\n")

        questions = get_questions_for_session(session_id)

        if not questions:
            print("⚠️  No questions were returned from the pipeline.")
        else:
            print(f"✅ {len(questions)} question(s) returned by session_pipeline:")
            time.sleep(0.5)
            print(json.dumps(questions, indent=2))

    except Exception as e:
        print(f"💥 Exception: {e}")
