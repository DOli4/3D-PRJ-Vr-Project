#!/usr/bin/env python3
"""
Test unified analysis (facial + body language from single camera)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pipeline.unified_analysis import unified_capture_analysis, get_unified_score

def test_unified_analysis():
    print("🎯 Testing Unified Analysis System")
    print("=" * 50)
    
    session_id = "unified_test_001"
    
    print(f"📋 Session ID: {session_id}")
    print("⏱️  Starting 15-second unified analysis...")
    print("📸 Make sure your camera is connected")
    print("🤖 Sit in front of camera like you're in an interview")
    print("\nPress Enter to start...")
    input()
    
    try:
        # Run unified analysis
        facial_results, body_results = unified_capture_analysis(session_id, duration=15)
        scores = get_unified_score(facial_results, body_results)
        
        print("\n" + "=" * 50)
        print("📊 UNIFIED ANALYSIS RESULTS")
        print("=" * 50)
        
        print(f"Overall Interview Score: {scores['overall']:.1f}%")
        print(f"Grade: {get_grade(scores['overall'])}")
        
        print(f"\n👤 Facial Analysis Score: {scores['facial']:.1f}%")
        print(f"🤖 Body Language Score: {scores['body']:.1f}%")
        
        print(f"\n📈 Detailed Results:")
        print(f"  - Facial emotions captured: {len(facial_results)}")
        print(f"  - Body language samples: {len(body_results)}")
        
        if body_results:
            avg_posture = sum(r['posture'] for r in body_results) / len(body_results)
            avg_eye_contact = sum(r['eye_contact'] for r in body_results) / len(body_results)
            avg_gestures = sum(r['hand_gestures'] for r in body_results) / len(body_results)
            
            print(f"  - Average posture: {avg_posture:.1f}%")
            print(f"  - Average eye contact: {avg_eye_contact:.1f}%")
            print(f"  - Average gestures: {avg_gestures:.1f}%")
        
        print("\n✅ Unified test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

def get_grade(score):
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
    test_unified_analysis()