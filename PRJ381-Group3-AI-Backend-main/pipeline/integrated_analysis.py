import threading
import time
from datetime import datetime
import csv
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.capture import capture_multiple_emotions
from pipeline.analyze import analyze_audio_emotion
# from pipeline.body_language import capture_body_language, get_body_language_score
from config.settings import FACIAL_LOG

class IntegratedInterviewAnalyzer:
    def __init__(self, session_id):
        self.session_id = session_id
        self.facial_results = []
        self.audio_results = []
        self.body_results = []
        self.is_recording = False
        
    def start_analysis(self, duration=60):
        """Start integrated analysis of facial, voice, and body language"""
        print("🎯 Starting integrated interview analysis...")
        self.is_recording = True
        
        # Start body language analysis in separate thread
        body_thread = threading.Thread(
            target=self._capture_body_language, 
            args=(duration,)
        )
        
        # Start facial emotion analysis in separate thread  
        facial_thread = threading.Thread(
            target=self._capture_facial_emotions,
            args=(duration,)
        )
        
        body_thread.start()
        facial_thread.start()
        
        # Wait for completion
        body_thread.join()
        facial_thread.join()
        
        self.is_recording = False
        return self.generate_comprehensive_report()
    
    def _capture_body_language(self, duration):
        """Capture body language in background"""
        try:
            from pipeline.body_language import capture_body_language
            self.body_results = capture_body_language(self.session_id, duration, interval=3)
        except Exception as e:
            print(f"Body language analysis error: {e}")
            self.body_results = []
    
    def _capture_facial_emotions(self, duration):
        """Capture facial emotions in background"""
        try:
            self.facial_results = capture_multiple_emotions(self.session_id, duration, interval=4)
        except Exception as e:
            print(f"Facial emotion analysis error: {e}")
            self.facial_results = []
    
    def analyze_audio_file(self, audio_path):
        """Analyze audio file for emotion"""
        try:
            emotion, confidence = analyze_audio_emotion(audio_path, self.session_id)
            self.audio_results = [(emotion, confidence)]
            return emotion, confidence
        except Exception as e:
            print(f"Audio analysis error: {e}")
            return "neutral", 0.5
    
    def generate_comprehensive_report(self):
        """Generate comprehensive interview performance report"""
        report = {
            'session_id': self.session_id,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'facial_analysis': self._analyze_facial_emotions(),
            'body_language': self._analyze_body_language(),
            'audio_emotion': self._analyze_audio_emotion(),
            'overall_score': 0,
            'recommendations': []
        }
        
        # Calculate overall interview score
        scores = []
        if report['facial_analysis']['score'] > 0:
            scores.append(report['facial_analysis']['score'])
        if report['body_language']['score'] > 0:
            scores.append(report['body_language']['score'])
        if report['audio_emotion']['score'] > 0:
            scores.append(report['audio_emotion']['score'])
            
        report['overall_score'] = sum(scores) / len(scores) if scores else 0
        report['recommendations'] = self._generate_recommendations(report)
        
        # Save comprehensive report
        self._save_comprehensive_report(report)
        
        return report
    
    def _analyze_facial_emotions(self):
        """Analyze facial emotion results for interview context"""
        if not self.facial_results:
            return {'score': 0, 'dominant_emotion': 'unknown', 'confidence': 0}
        
        # Count emotions
        emotion_counts = {}
        total_confidence = 0
        
        for emotion, confidence in self.facial_results:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
            total_confidence += confidence
        
        dominant_emotion = max(emotion_counts, key=emotion_counts.get)
        avg_confidence = total_confidence / len(self.facial_results)
        
        # Interview-appropriate emotion scoring
        interview_scores = {
            'happy': 85, 'neutral': 80, 'surprise': 70,
            'sad': 40, 'angry': 20, 'fear': 30, 'disgust': 25
        }
        
        score = interview_scores.get(dominant_emotion, 50) * avg_confidence
        
        return {
            'score': round(score, 1),
            'dominant_emotion': dominant_emotion,
            'confidence': round(avg_confidence, 3),
            'emotion_distribution': emotion_counts
        }
    
    def _analyze_body_language(self):
        """Analyze body language results"""
        if not self.body_results:
            return {'score': 0, 'feedback': 'No body language data'}
        
        from pipeline.body_language import get_body_language_score
        score, feedback = get_body_language_score(self.body_results)
        return {'score': score, 'feedback': feedback}
    
    def _analyze_audio_emotion(self):
        """Analyze audio emotion results"""
        if not self.audio_results:
            return {'score': 0, 'emotion': 'unknown', 'confidence': 0}
        
        emotion, confidence = self.audio_results[0]
        
        # Interview-appropriate audio emotion scoring
        audio_scores = {
            'joy': 90, 'optimism': 85, 'love': 80, 'surprise': 75,
            'neutral': 70, 'sadness': 45, 'pessimism': 40, 
            'anger': 25, 'fear': 35, 'disgust': 30
        }
        
        score = audio_scores.get(emotion, 60) * confidence
        
        return {
            'score': round(score, 1),
            'emotion': emotion,
            'confidence': round(confidence, 3)
        }
    
    def _generate_recommendations(self, report):
        """Generate personalized recommendations"""
        recommendations = []
        
        # Facial emotion recommendations
        if report['facial_analysis']['score'] < 60:
            if report['facial_analysis']['dominant_emotion'] in ['sad', 'angry', 'fear']:
                recommendations.append("Practice relaxation techniques before interviews")
            recommendations.append("Work on maintaining a positive, confident expression")
        
        # Body language recommendations  
        if report['body_language']['score'] < 65:
            recommendations.append("Focus on maintaining good posture throughout the interview")
            recommendations.append("Practice making eye contact with the camera/interviewer")
            recommendations.append("Use natural hand gestures to emphasize points")
        
        # Audio emotion recommendations
        if report['audio_emotion']['score'] < 60:
            recommendations.append("Practice speaking with more enthusiasm and confidence")
            recommendations.append("Work on voice modulation and tone")
        
        # Overall recommendations
        if report['overall_score'] >= 80:
            recommendations.append("Excellent interview presence! Keep up the great work")
        elif report['overall_score'] >= 65:
            recommendations.append("Good interview skills with room for minor improvements")
        else:
            recommendations.append("Consider practicing mock interviews to improve confidence")
        
        return recommendations
    
    def _save_comprehensive_report(self, report):
        """Save comprehensive report to CSV"""
        report_file = FACIAL_LOG.replace('facial_emotions', 'comprehensive_report')
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        with open(report_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                "Session ID", "Timestamp", "Overall Score", "Facial Score", 
                "Body Language Score", "Audio Score", "Dominant Emotion", 
                "Recommendations"
            ])
            writer.writerow([
                report['session_id'], report['timestamp'], report['overall_score'],
                report['facial_analysis']['score'], report['body_language']['score'],
                report['audio_emotion']['score'], report['facial_analysis']['dominant_emotion'],
                "; ".join(report['recommendations'])
            ])

# Unity/VR Integration functions
def start_vr_analysis(session_id, duration=60):
    """Main function for VR/Unity integration"""
    analyzer = IntegratedInterviewAnalyzer(session_id)
    return analyzer.start_analysis(duration)

def analyze_audio_only(session_id, audio_path):
    """Analyze only audio file - useful for VR scenarios"""
    analyzer = IntegratedInterviewAnalyzer(session_id)
    emotion, confidence = analyzer.analyze_audio_file(audio_path)
    return {
        'session_id': session_id,
        'audio_emotion': emotion,
        'confidence': confidence,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }