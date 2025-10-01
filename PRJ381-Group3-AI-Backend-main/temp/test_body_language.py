#!/usr/bin/env python3
"""
Test script for body language analysis
Run this to test the body language detection system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pipeline.integrated_analysis import IntegratedInterviewAnalyzer

def test_body_language_analysis():
    """Test the integrated analysis system"""
    print("🎯 Testing Body Language Analysis System")
    print("=" * 50)
    
    # Create analyzer instance
    session_id = "test_session_001"
    analyzer = IntegratedInterviewAnalyzer(session_id)
    
    print(f"📋 Session ID: {session_id}")
    print("⏱️  Starting 20-second analysis...")
    print("📸 Make sure your camera is connected and working")
    print("🤖 Sit in front of your camera and act like you're in an interview")
    print("\nPress Enter to start the analysis...")
    input()
    
    try:
        # Run analysis for 20 seconds
        report = analyzer.start_analysis(duration=20)
        
        print("\n" + "=" * 50)
        print("📊 ANALYSIS RESULTS")
        print("=" * 50)
        
        print(f"Overall Interview Score: {report['overall_score']:.1f}%")
        print(f"Grade: {get_grade(report['overall_score'])}")
        
        print(f"\n👤 Facial Analysis:")
        print(f"  - Score: {report['facial_analysis']['score']:.1f}%")
        print(f"  - Dominant Emotion: {report['facial_analysis']['dominant_emotion']}")
        print(f"  - Confidence: {report['facial_analysis']['confidence']:.3f}")
        
        print(f"\n🤖 Body Language:")
        print(f"  - Score: {report['body_language']['score']:.1f}%")
        print(f"  - Feedback: {report['body_language']['feedback']}")
        
        print(f"\n🎤 Audio Emotion:")
        print(f"  - Score: {report['audio_emotion']['score']:.1f}%")
        print(f"  - Emotion: {report['audio_emotion']['emotion']}")
        print(f"  - Confidence: {report['audio_emotion']['confidence']:.3f}")
        
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("Make sure your camera is connected and MediaPipe is installed:")
        print("pip install mediapipe")

def get_grade(score):
    """Convert score to letter grade"""
    if score >= 90: return "A+"
    elif score >= 85: return "A"
    elif score >= 80: return "A-"
    elif score >= 75: return "B+"
    elif score >= 70: return "B"
    elif score >= 65: return "B-"
    elif score >= 60: return "C+"
    elif score >= 55: return "C"
    elif score >= 50: return "C-"
    else: return "F"

if __name__ == "__main__":
    test_body_language_analysis()