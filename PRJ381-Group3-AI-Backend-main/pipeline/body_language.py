import cv2
import mediapipe as mp
import numpy as np
import csv
import os
import time
from datetime import datetime
from config.settings import FACIAL_LOG

class BodyLanguageAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
    def calculate_angle(self, a, b, c):
        """Calculate angle between three points"""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        
        if angle > 180.0:
            angle = 360-angle
            
        return angle
    
    def analyze_posture(self, landmarks):
        """Analyze posture and return confidence scores"""
        scores = {
            'posture': 0,
            'eye_contact': 0,
            'hand_gestures': 0,
            'overall_confidence': 0
        }
        
        if not landmarks:
            return scores
            
        # Get key landmarks
        left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        right_shoulder = [landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                         landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        left_elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                     landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        right_elbow = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                      landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        nose = [landmarks[self.mp_pose.PoseLandmark.NOSE.value].x,
               landmarks[self.mp_pose.PoseLandmark.NOSE.value].y]
        
        # Posture analysis (shoulder alignment)
        shoulder_diff = abs(left_shoulder[1] - right_shoulder[1])
        posture_score = max(0, 100 - (shoulder_diff * 1000))  # Good posture = aligned shoulders
        scores['posture'] = min(100, posture_score)
        
        # Eye contact simulation (head position)
        head_center = abs(nose[0] - 0.5)  # Distance from center
        eye_contact_score = max(0, 100 - (head_center * 200))
        scores['eye_contact'] = min(100, eye_contact_score)
        
        # Hand gesture analysis (arm position)
        left_arm_angle = self.calculate_angle(left_shoulder, left_elbow, [left_elbow[0], left_elbow[1]-0.1])
        right_arm_angle = self.calculate_angle(right_shoulder, right_elbow, [right_elbow[0], right_elbow[1]-0.1])
        
        # Good interview posture: arms not crossed, moderate gesturing
        gesture_score = 50
        if 30 < left_arm_angle < 150 and 30 < right_arm_angle < 150:
            gesture_score = 80
        scores['hand_gestures'] = gesture_score
        
        # Overall confidence based on all factors
        scores['overall_confidence'] = (scores['posture'] + scores['eye_contact'] + scores['hand_gestures']) / 3
        
        return scores
    
    def get_interview_feedback(self, scores):
        """Generate interview-appropriate feedback"""
        feedback = []
        
        if scores['posture'] < 60:
            feedback.append("Maintain straight posture - sit up straight")
        elif scores['posture'] > 80:
            feedback.append("Excellent posture maintained")
            
        if scores['eye_contact'] < 60:
            feedback.append("Look more directly at the camera")
        elif scores['eye_contact'] > 80:
            feedback.append("Good eye contact with interviewer")
            
        if scores['hand_gestures'] < 50:
            feedback.append("Use natural hand gestures while speaking")
        elif scores['hand_gestures'] > 70:
            feedback.append("Appropriate use of hand gestures")
            
        return feedback

def capture_body_language(session_id, duration=20, interval=2):
    """Capture and analyze body language during interview"""
    analyzer = BodyLanguageAnalyzer()
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        raise Exception("Webcam not available.")
    
    results = []
    log_file = FACIAL_LOG.replace('facial_emotions', 'body_language')
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    print(f"🤖 Analyzing body language every {interval}s for {duration}s...")
    
    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Session ID", "Timestamp", "Relative Time (s)", "Posture Score", 
                        "Eye Contact Score", "Hand Gesture Score", "Overall Confidence", "Feedback"])
        
        start_time = time.time()
        last_capture = 0
        
        while (time.time() - start_time) < duration:
            ret, frame = cap.read()
            if not ret:
                continue
                
            current_time = time.time() - start_time
            
            if current_time - last_capture >= interval:
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results_pose = analyzer.pose.process(rgb_frame)
                
                if results_pose.pose_landmarks:
                    scores = analyzer.analyze_posture(results_pose.pose_landmarks.landmark)
                    feedback = analyzer.get_interview_feedback(scores)
                    
                    rel_time = round(current_time)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    print(f"[{rel_time}s] Posture: {scores['posture']:.1f}% | "
                          f"Eye Contact: {scores['eye_contact']:.1f}% | "
                          f"Gestures: {scores['hand_gestures']:.1f}% | "
                          f"Confidence: {scores['overall_confidence']:.1f}%")
                    
                    results.append(scores)
                    writer.writerow([session_id, timestamp, rel_time, 
                                   round(scores['posture'], 1),
                                   round(scores['eye_contact'], 1), 
                                   round(scores['hand_gestures'], 1),
                                   round(scores['overall_confidence'], 1),
                                   "; ".join(feedback)])
                    
                    last_capture = current_time
    
    cap.release()
    return results

def get_body_language_score(results):
    """Calculate overall body language score for interview"""
    if not results:
        return 0, "No body language data captured"
    
    avg_scores = {
        'posture': np.mean([r['posture'] for r in results]),
        'eye_contact': np.mean([r['eye_contact'] for r in results]),
        'hand_gestures': np.mean([r['hand_gestures'] for r in results]),
        'overall_confidence': np.mean([r['overall_confidence'] for r in results])
    }
    
    # Interview-specific scoring
    interview_score = (avg_scores['posture'] * 0.3 + 
                      avg_scores['eye_contact'] * 0.4 + 
                      avg_scores['hand_gestures'] * 0.3)
    
    if interview_score >= 80:
        feedback = "Excellent interview presence and body language"
    elif interview_score >= 65:
        feedback = "Good body language with room for improvement"
    elif interview_score >= 50:
        feedback = "Average body language - focus on posture and eye contact"
    else:
        feedback = "Needs improvement in body language and confidence"
    
    return round(interview_score, 1), feedback

def analyze_body_language_from_image(frame):
    """Analyze body language from a single image frame (for Unity integration)"""
    analyzer = BodyLanguageAnalyzer()
    
    try:
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results_pose = analyzer.pose.process(rgb_frame)
        
        # Detect emotion using face landmarks
        emotion, emotion_confidence = detect_emotion_from_frame(rgb_frame)
        
        if results_pose.pose_landmarks:
            scores = analyzer.analyze_posture(results_pose.pose_landmarks.landmark)
            
            return {
                "posture_score": scores['posture'] / 100.0,
                "eye_contact_score": scores['eye_contact'] / 100.0,
                "gesture_score": scores['hand_gestures'] / 100.0,
                "overall_score": scores['overall_confidence'] / 100.0,
                "emotion": emotion,
                "emotion_confidence": emotion_confidence
            }
        else:
            return {
                "posture_score": 0.0,
                "eye_contact_score": 0.0,
                "gesture_score": 0.0,
                "overall_score": 0.0,
                "emotion": emotion,
                "emotion_confidence": emotion_confidence
            }
    except Exception as e:
        print(f"Error analyzing frame: {e}")
        return {
            "posture_score": 0.0,
            "eye_contact_score": 0.0,
            "gesture_score": 0.0,
            "overall_score": 0.0,
            "emotion": "error",
            "emotion_confidence": 0.0
        }

def detect_emotion_from_frame(rgb_frame):
    """Simple emotion detection based on facial landmarks"""
    try:
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        
        results = face_mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            
            # Simple emotion detection based on mouth and eye positions
            # Mouth corners (left: 61, right: 291)
            # Eyes (left: 33, right: 263)
            
            mouth_left = landmarks[61]
            mouth_right = landmarks[291]
            mouth_center = landmarks[13]
            
            left_eye = landmarks[33]
            right_eye = landmarks[263]
            
            # Calculate mouth curve (smile detection)
            mouth_curve = (mouth_left.y + mouth_right.y) / 2 - mouth_center.y
            
            # Calculate eye openness
            eye_openness = abs(left_eye.y - landmarks[159].y) + abs(right_eye.y - landmarks[386].y)
            
            # Simple emotion classification
            if mouth_curve < -0.01:  # Mouth corners up
                return "happy", min(0.9, abs(mouth_curve) * 50)
            elif mouth_curve > 0.01:  # Mouth corners down
                return "sad", min(0.8, mouth_curve * 40)
            elif eye_openness > 0.02:  # Eyes wide
                return "surprised", min(0.85, eye_openness * 30)
            else:
                return "neutral", 0.7
        else:
            return "neutral", 0.5
            
    except Exception as e:
        print(f"Emotion detection error: {e}")
        return "neutral", 0.5