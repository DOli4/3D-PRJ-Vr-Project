import cv2
import mediapipe as mp
import numpy as np
import csv
import os
import time
from datetime import datetime
from fer import FER
from config.settings import FACIAL_LOG

class UnifiedAnalyzer:
    def __init__(self):
        # Facial emotion detection
        self.emotion_detector = FER(mtcnn=True)
        
        # Body language detection
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
    def calculate_angle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        
        if angle > 180.0:
            angle = 360-angle
            
        return angle
    
    def analyze_posture(self, landmarks):
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
        
        # Posture analysis
        shoulder_diff = abs(left_shoulder[1] - right_shoulder[1])
        posture_score = max(0, 100 - (shoulder_diff * 1000))
        scores['posture'] = min(100, posture_score)
        
        # Eye contact
        head_center = abs(nose[0] - 0.5)
        eye_contact_score = max(0, 100 - (head_center * 200))
        scores['eye_contact'] = min(100, eye_contact_score)
        
        # Hand gestures
        left_arm_angle = self.calculate_angle(left_shoulder, left_elbow, [left_elbow[0], left_elbow[1]-0.1])
        right_arm_angle = self.calculate_angle(right_shoulder, right_elbow, [right_elbow[0], right_elbow[1]-0.1])
        
        gesture_score = 50
        if 30 < left_arm_angle < 150 and 30 < right_arm_angle < 150:
            gesture_score = 80
        scores['hand_gestures'] = gesture_score
        
        scores['overall_confidence'] = (scores['posture'] + scores['eye_contact'] + scores['hand_gestures']) / 3
        
        return scores

def unified_capture_analysis(session_id, duration=20):
    """Unified analysis using single camera feed"""
    analyzer = UnifiedAnalyzer()
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        raise Exception("Webcam not available.")
    
    facial_results = []
    body_results = []
    
    # Setup logging
    facial_log = FACIAL_LOG
    body_log = FACIAL_LOG.replace('facial_emotions', 'body_language')
    os.makedirs(os.path.dirname(facial_log), exist_ok=True)
    
    print(f"🎯 Starting unified analysis for {duration}s...")
    
    # Setup CSV files
    with open(facial_log, mode='a', newline='') as f_file, \
         open(body_log, mode='a', newline='') as b_file:
        
        f_writer = csv.writer(f_file)
        b_writer = csv.writer(b_file)
        
        f_writer.writerow(["Session ID", "Timestamp", "Relative Time (s)", "Emotion", "Confidence"])
        b_writer.writerow(["Session ID", "Timestamp", "Relative Time (s)", "Posture Score", 
                          "Eye Contact Score", "Hand Gesture Score", "Overall Confidence"])
        
        start_time = time.time()
        last_analysis = 0
        
        while (time.time() - start_time) < duration:
            ret, frame = cap.read()
            if not ret:
                continue
                
            current_time = time.time() - start_time
            
            # Analyze every 2 seconds
            if current_time - last_analysis >= 2:
                rel_time = round(current_time)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Facial emotion analysis
                emotion, score = analyzer.emotion_detector.top_emotion(frame)
                if emotion:
                    print(f"[{rel_time}s] Emotion: {emotion} ({round(score * 100)}%)")
                    facial_results.append((emotion, score))
                    f_writer.writerow([session_id, timestamp, rel_time, emotion, round(score, 3)])
                else:
                    print(f"[{rel_time}s] No emotion detected")
                    f_writer.writerow([session_id, timestamp, rel_time, "none", 0.0])
                
                # Body language analysis
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results_pose = analyzer.pose.process(rgb_frame)
                
                if results_pose.pose_landmarks:
                    scores = analyzer.analyze_posture(results_pose.pose_landmarks.landmark)
                    
                    print(f"[{rel_time}s] Posture: {scores['posture']:.1f}% | "
                          f"Eye Contact: {scores['eye_contact']:.1f}% | "
                          f"Gestures: {scores['hand_gestures']:.1f}%")
                    
                    body_results.append(scores)
                    b_writer.writerow([session_id, timestamp, rel_time, 
                                     round(scores['posture'], 1),
                                     round(scores['eye_contact'], 1), 
                                     round(scores['hand_gestures'], 1),
                                     round(scores['overall_confidence'], 1)])
                
                last_analysis = current_time
    
    cap.release()
    return facial_results, body_results

def get_unified_score(facial_results, body_results):
    """Calculate comprehensive interview score"""
    scores = {'facial': 0, 'body': 0, 'overall': 0}
    
    # Facial analysis
    if facial_results:
        emotion_counts = {}
        total_confidence = 0
        
        for emotion, confidence in facial_results:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            total_confidence += confidence
        
        dominant_emotion = max(emotion_counts, key=emotion_counts.get)
        avg_confidence = total_confidence / len(facial_results)
        
        interview_scores = {
            'happy': 85, 'neutral': 80, 'surprise': 70,
            'sad': 40, 'angry': 20, 'fear': 30, 'disgust': 25
        }
        
        scores['facial'] = interview_scores.get(dominant_emotion, 50) * avg_confidence
    
    # Body language analysis
    if body_results:
        avg_body_score = np.mean([r['overall_confidence'] for r in body_results])
        scores['body'] = avg_body_score
    
    # Overall score
    valid_scores = [s for s in [scores['facial'], scores['body']] if s > 0]
    scores['overall'] = sum(valid_scores) / len(valid_scores) if valid_scores else 0
    
    return scores