import firebase_admin
from firebase_admin import credentials, firestore, storage
import os

# Initialize Firebase
try:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'vr-interview-system.appspot.com'
    })
    print("Firebase initialized successfully")
except Exception as e:
    print(f"Firebase initialization failed: {e}")
    # Continue without Firebase for now
    db = None
    bucket = None

if firebase_admin._apps:
    db = firestore.client()
    bucket = storage.bucket()
else:
    db = None
    bucket = None

def save_analysis_data(session_id, analysis_data, document_id=None):
    """Save analysis JSON to Firestore in session folder structure"""
    if db is None:
        print("Firebase not initialized, skipping save")
        return False
    try:
        # Create session folder structure: interview-sessions/Session_{session_id}/data/{document_id}
        if document_id is None:
            import time
            document_id = f"analysis_{int(time.time())}"
        
        print(f"Attempting to save to path: interview-sessions/Session_{session_id}/data/{document_id}")
        doc_ref = db.collection('interview-sessions').document(f'Session_{session_id}').collection('data').document(document_id)
        doc_ref.set({
            'analysis': analysis_data,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'session_id': session_id
        })
        print(f"Successfully saved analysis data for session {session_id} in document {document_id}")
        return True
    except Exception as e:
        print(f"Error saving to Firebase: {e}")
        return False

def upload_audio_file(session_id, audio_file_path, audio_id=None):
    """Upload WAV file to Firebase Storage in session folder structure"""
    if bucket is None:
        print("Firebase not initialized, skipping audio upload")
        return None
    try:
        if audio_id is None:
            audio_id = "main_audio"
        
        blob = bucket.blob(f'audio/Session_{session_id}/{audio_id}.wav')
        blob.upload_from_filename(audio_file_path)
        
        # Also save audio metadata to Firestore
        save_analysis_data(session_id, {
            'type': 'audio_upload',
            'audio_url': blob.public_url,
            'audio_id': audio_id
        }, f'audio_{audio_id}')
        
        return blob.public_url
    except Exception as e:
        print(f"Error uploading audio: {e}")
        return None

def get_session_data(session_id):
    """Get all data for a session"""
    if db is None:
        print("Firebase not initialized")
        return None
    try:
        docs = db.collection('interview-sessions').document(f'Session_{session_id}').collection('data').stream()
        session_data = []
        for doc in docs:
            data = doc.to_dict()
            data['document_id'] = doc.id
            session_data.append(data)
        return session_data
    except Exception as e:
        print(f"Error getting session data: {e}")
        return None

def save_session_metadata(session_id, metadata):
    """Save session metadata (user_id, role, level, etc.)"""
    if db is None:
        print("Firebase not initialized, skipping save")
        return False
    try:
        print(f"Attempting to save metadata to path: interview-sessions/Session_{session_id}")
        doc_ref = db.collection('interview-sessions').document(f'Session_{session_id}')
        doc_ref.set({
            'metadata': metadata,
            'created_at': firestore.SERVER_TIMESTAMP,
            'session_id': session_id
        })
        print(f"Successfully saved metadata for session {session_id}")
        return True
    except Exception as e:
        print(f"Error saving session metadata: {e}")
        return False