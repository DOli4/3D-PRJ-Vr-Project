import cv2
import mediapipe as mp
import numpy as np
from fer import FER
from datetime import datetime

class RealtimeAnalyzer:
    def __init__(self):
        self.emotion_detector = FER(mtcnn=True)
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.cap = None
        
    def start_camera(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
        return self.cap.isOpened()
    
    def stop_camera(self):
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def calculate_angle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        
        if angle > 180.0:
            angle = 360-angle
            
        return angle
    
    def analyze_frame(self):
        if not self.cap or not self.cap.isOpened():
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        # Initialize response
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "posture_percent": 0,
            "eye_contact_percent": 0,
            "gestures_percent": 0,
            "emotion": "none",
            "emotion_confidence": 0.0,
            "overall_score": 0,
            "status": "success"
        }
        
        try:
            # Facial emotion analysis
            emotion, score = self.emotion_detector.top_emotion(frame)
            if emotion:
                analysis["emotion"] = emotion
                analysis["emotion_confidence"] = round(score, 3)
            
            # Body language analysis
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results_pose = self.pose.process(rgb_frame)
            
            if results_pose.pose_landmarks:
                landmarks = results_pose.pose_landmarks.landmark
                
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
                analysis["posture_percent"] = round(min(100, posture_score), 1)
                
                # Eye contact
                head_center = abs(nose[0] - 0.5)
                eye_contact_score = max(0, 100 - (head_center * 200))
                analysis["eye_contact_percent"] = round(min(100, eye_contact_score), 1)
                
                # Hand gestures
                left_arm_angle = self.calculate_angle(left_shoulder, left_elbow, [left_elbow[0], left_elbow[1]-0.1])
                right_arm_angle = self.calculate_angle(right_shoulder, right_elbow, [right_elbow[0], right_elbow[1]-0.1])
                
                gesture_score = 50
                if 30 < left_arm_angle < 150 and 30 < right_arm_angle < 150:
                    gesture_score = 80
                analysis["gestures_percent"] = round(gesture_score, 1)
                
                # Overall score
                emotion_score = 0
                if emotion:
                    emotion_scores = {
                        'happy': 85, 'neutral': 80, 'surprise': 70,
                        'sad': 40, 'angry': 20, 'fear': 30, 'disgust': 25
                    }
                    emotion_score = emotion_scores.get(emotion, 50) * score
                
                body_score = (analysis["posture_percent"] + analysis["eye_contact_percent"] + analysis["gestures_percent"]) / 3
                
                if emotion_score > 0:
                    analysis["overall_score"] = round((emotion_score + body_score) / 2, 1)
                else:
                    analysis["overall_score"] = round(body_score, 1)
            
        except Exception as e:
            analysis["status"] = f"error: {str(e)}"
        
        return analysis

# Global analyzer instance
realtime_analyzer = RealtimeAnalyzer()