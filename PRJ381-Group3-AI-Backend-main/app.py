# app.py
"""
Barebones FastAPI server for the AI interview backend.
Delegates user and session operations to pipeline/session_pipeline.py
Run with: uvicorn app:app --reload
"""

import os
import sys
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# Fix path import to reach utils and pipeline
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from pipeline import session_pipeline as pipeline
from utils.user_manager import user_exists
from pipeline.answer_score import score_answer
from pipeline.integrated_analysis import start_vr_analysis, analyze_audio_only
from pipeline.realtime_analysis import realtime_analyzer
from firebase_config import save_analysis_data, upload_audio_file, save_session_metadata, get_session_data

app = FastAPI()

# ---------- In-memory session state ----------
active = {"user_id": None, "session_id": None}

# ---------- Request Models ----------
class UserCreateRequest(BaseModel):
    name: str
    email: str
class LoginRequest(BaseModel):
    user_id: str
class SessionCreateRequest(BaseModel):
    user_id: str
    role: str
    level: int
class AnswerSubmitRequest(BaseModel):
    question_id: str
    answer: str
class FinalizeSessionRequest(BaseModel):
    final_score: float
    summary_feedback: str
class SetActiveRequest(BaseModel):
    user_id: str
    session_id: str

class BodyLanguageAnalysisRequest(BaseModel):
    session_id: str
    duration: Optional[int] = 60

class AudioAnalysisRequest(BaseModel):
    session_id: str
    audio_file_path: str

class UnityAnalysisRequest(BaseModel):
    timestamp: str
    posture_score: float
    eye_contact_score: float
    gesture_score: float
    emotion: str
    emotion_confidence: float
    overall_score: float

class FrameAnalysisRequest(BaseModel):
    image_data: str  # base64 encoded image
    timestamp: int

# ---------- User Routes ----------
@app.post("/users/register")
def register_user(req: UserCreateRequest):
    try:
        user = pipeline.create_user_pipeline(req.name, req.email)
        active["user_id"] = user.get("user_id")
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/users/login")
def login_user(req: LoginRequest):
    try:
        if user_exists(req.user_id):
            active["user_id"] = req.user_id
            return {"status": "ok", "user_id": req.user_id}
        raise ValueError("User not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/sessions")
def get_all_user_sessions():
    try:
        sessions = pipeline.get_user_sessions(active["user_id"])
        return {"sessions": sessions}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ---------- Session Routes ----------
@app.post("/sessions/start")
def start_session(req: SessionCreateRequest):
    try:
        session = pipeline.create_session_pipeline(req.user_id, req.role, req.level)
        session_id = session.get("session_id")
        active["session_id"] = session_id
        
        # Save session metadata to Firebase
        metadata = {
            "user_id": req.user_id,
            "role": req.role,
            "level": req.level,
            "status": "active"
        }
        save_session_metadata(session_id, metadata)
        
        # Save initial session data
        save_analysis_data(session_id, {
            "type": "session_start",
            "user_id": req.user_id,
            "role": req.role,
            "level": req.level
        }, "session_start")
        
        return {"status": "ok", "session_id": session_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/sessions/questions")
def get_questions_for_active_session():
    session_id = active["session_id"]
    try:
        questions = pipeline.get_questions_for_session(session_id)
        return {"session_id": session_id, "questions": questions}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/sessions/answer")
def submit_answer(data: AnswerSubmitRequest):
    session_id = active["session_id"]
    try:
        question = pipeline.find_question_by_id(session_id, data.question_id)
        if not question:
            raise ValueError("Invalid question_id")

        answer_record = {
            "question_id": data.question_id,
            "answer": data.answer,
            # "grade": None,  # This will be set after scoring
            # "score": None,  # This will be set after scoring
        }

        pipeline.append_question_to_session(session_id, answer_record)
        return {"status": "ok", "message": "Answer submitted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/sessions/score")
def score_answers():
    session_id = active["session_id"]
    try:
        result = pipeline.score_questions(session_id)

        return {
            "status": "ok",
            "scored_count": result["scored_count"],
            "questions_scored": result["questions_scored"]
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sessions/feedback")
def generate_feedback():
    session_id = active["session_id"]
    try:
        result = pipeline.generate_session_feedback(session_id)

        return {
            "status": "ok",
            "final_score": result["final_score"],
            "feedback": result["feedback"]
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sessions/finalize")
def finalize_session(req: FinalizeSessionRequest):
    session_id = active["session_id"]
    try:
        # Save final session data to Firebase
        final_data = {
            "type": "session_end",
            "final_score": req.final_score,
            "summary_feedback": req.summary_feedback,
            "status": "completed"
        }
        save_analysis_data(session_id, final_data, "session_end")
        
        # Update session metadata
        metadata = {
            "status": "completed",
            "final_score": req.final_score,
            "completed_at": pipeline.get_current_timestamp()
        }
        save_session_metadata(session_id, metadata)
        
        return {"status": "ok", "message": "Session finalized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}")
def get_session_by_id(session_id: str):
    try:
        session = pipeline.get_session_details(session_id)
        if session is None:
            raise ValueError(f"Session '{session_id}' not found.")
        return session
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ---------- Status Routes ----------
@app.get("/")
def root():
    return {"message": "AI Interview Backend is running"}

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "AI Interview Backend is healthy"}

@app.get("/getActiveUser")
def get_active_session():
    if active["user_id"] is None:
        raise HTTPException(status_code=404, detail="No active session found")
    return {"user_id": active["user_id"]}

@app.get("/getActiveSession")
def get_active_session():
    if active["session_id"] is None:
        raise HTTPException(status_code=404, detail="No active session found")
    return {"session_id": active["session_id"]}



@app.post("/setActiveSession")
def set_active_session(req: SetActiveRequest):
    if not req.user_id or not req.session_id:
        raise HTTPException(status_code=400, detail="Missing user_id or session_id")

    # Optional: Validate session exists before setting
    session = pipeline.get_session_details(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{req.session_id}' not found.")

    active["user_id"] = req.user_id
    active["session_id"] = req.session_id

    return {
        "status": "ok",
        "message": f"Active session set to {req.session_id}",
        "user_id": req.user_id,
        "session_id": req.session_id
    }

# ---------- Body Language Analysis Routes ----------
@app.post("/analysis/start")
def start_body_language_analysis(req: BodyLanguageAnalysisRequest):
    """Start comprehensive analysis (facial, body language, voice)"""
    try:
        report = start_vr_analysis(req.session_id, req.duration)
        return {
            "status": "ok",
            "session_id": req.session_id,
            "analysis_report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analysis/audio")
def analyze_audio_emotion(req: AudioAnalysisRequest):
    """Analyze audio file for emotion (Unity/VR compatible)"""
    try:
        result = analyze_audio_only(req.session_id, req.audio_file_path)
        return {
            "status": "ok",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio analysis failed: {str(e)}")

@app.get("/analysis/status/{session_id}")
def get_analysis_status(session_id: str):
    """Get analysis status for a session"""
    try:
        from config.settings import FACIAL_LOG
        import os
        
        facial_log = FACIAL_LOG
        body_log = FACIAL_LOG.replace('facial_emotions', 'body_language')
        audio_log = FACIAL_LOG.replace('facial_emotions', 'audio_emotion')
        report_log = FACIAL_LOG.replace('facial_emotions', 'comprehensive_report')
        
        status = {
            "session_id": session_id,
            "facial_analysis": os.path.exists(facial_log),
            "body_language": os.path.exists(body_log),
            "audio_analysis": os.path.exists(audio_log),
            "comprehensive_report": os.path.exists(report_log)
        }
        
        return {"status": "ok", "analysis_status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

# ---------- Real-time Analysis Routes ----------
@app.get("/frames")
def get_frame_analysis():
    """Get real-time frame analysis for Unity"""
    try:
        if not realtime_analyzer.start_camera():
            raise HTTPException(status_code=500, detail="Camera not available")
        
        analysis = realtime_analyzer.analyze_frame()
        if analysis is None:
            raise HTTPException(status_code=500, detail="Failed to capture frame")
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Frame analysis failed: {str(e)}")

@app.post("/frames/start")
def start_realtime_analysis():
    """Start real-time camera for analysis"""
    try:
        if realtime_analyzer.start_camera():
            return {"status": "ok", "message": "Camera started"}
        else:
            raise HTTPException(status_code=500, detail="Failed to start camera")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Camera start failed: {str(e)}")

@app.post("/frames/stop")
def stop_realtime_analysis():
    """Stop real-time camera"""
    try:
        realtime_analyzer.stop_camera()
        return {"status": "ok", "message": "Camera stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Camera stop failed: {str(e)}")

@app.post("/analyze-frame")
def analyze_unity_frame(req: FrameAnalysisRequest):
    """Analyze frame data sent from Unity"""
    try:
        import base64
        import cv2
        import numpy as np
        from pipeline.body_language import analyze_body_language_from_image
        
        # Decode base64 image
        image_data = base64.b64decode(req.image_data)
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise ValueError("Invalid image data")
        
        # Analyze the frame
        analysis = analyze_body_language_from_image(frame)
        
        result = {
            "posture_percent": analysis.get("posture_score", 0.0) * 100,
            "eye_contact_percent": analysis.get("eye_contact_score", 0.0) * 100,
            "gestures_percent": analysis.get("gesture_score", 0.0) * 100,
            "emotion": analysis.get("emotion", "neutral"),
            "emotion_confidence": analysis.get("emotion_confidence", 0.0),
            "overall_score": analysis.get("overall_score", 0.0) * 100,
            "status": "success",
            "timestamp": req.timestamp
        }
        
        # Save to Firebase with proper session structure
        session_id = active.get("session_id", str(req.timestamp))
        save_analysis_data(session_id, result, f"frame_analysis_{req.timestamp}")
        
        return result
    except Exception as e:
        return {
            "posture_percent": 0.0,
            "eye_contact_percent": 0.0,
            "gestures_percent": 0.0,
            "emotion": "error",
            "emotion_confidence": 0.0,
            "overall_score": 0.0,
            "status": f"error: {str(e)}"
        }

@app.post("/analyze")
def analyze_frame_simple(req: FrameAnalysisRequest):
    """Simple analyze endpoint for Unity compatibility"""
    return analyze_unity_frame(req)

@app.post("/upload-audio/{session_id}")
def upload_audio(session_id: str):
    """Upload audio file to Firebase Storage"""
    try:
        # For now, assume audio file is saved locally
        audio_path = f"temp_audio/{session_id}.wav"
        if os.path.exists(audio_path):
            url = upload_audio_file(session_id, audio_path)
            return {"status": "success", "audio_url": url}
        else:
            return {"status": "error", "message": "Audio file not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/sessions/{session_id}/firebase-data")
def get_firebase_session_data(session_id: str):
    """Get all Firebase data for a session"""
    try:
        data = get_session_data(session_id)
        if data is None:
            return {"status": "error", "message": "Session not found or Firebase not available"}
        return {"status": "success", "session_id": session_id, "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/sessions/end")
def end_session():
    """End the current active session and save to Firebase"""
    print(f"[DEBUG] /sessions/end called")
    session_id = active.get("session_id")
    print(f"[DEBUG] Active session_id: {session_id}")
    
    if not session_id:
        print(f"[ERROR] No active session found")
        raise HTTPException(status_code=400, detail="No active session")
    
    try:
        from datetime import datetime
        current_time = datetime.utcnow().isoformat()
        print(f"[DEBUG] Current time: {current_time}")
        
        # Save session end data
        end_data = {
            "type": "session_end",
            "status": "completed",
            "ended_at": current_time
        }
        print(f"[DEBUG] Saving end_data: {end_data}")
        save_analysis_data(session_id, end_data, "session_end")
        print(f"[DEBUG] End data saved successfully")
        
        # Update session metadata
        metadata = {
            "status": "completed",
            "ended_at": current_time
        }
        print(f"[DEBUG] Updating metadata: {metadata}")
        save_session_metadata(session_id, metadata)
        print(f"[DEBUG] Metadata updated successfully")
        
        print(f"[SUCCESS] Session {session_id} ended successfully")
        return {"status": "ok", "message": f"Session {session_id} ended successfully"}
    except Exception as e:
        print(f"[ERROR] Exception in end_session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

