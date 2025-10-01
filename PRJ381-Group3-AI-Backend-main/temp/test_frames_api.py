import requests
import json
import time

def test_frames_api():
    base_url = "http://127.0.0.1:8000"
    
    print("🎯 Testing /frames API")
    print("=" * 40)
    
    # Start camera
    print("1. Starting camera...")
    try:
        response = requests.post(f"{base_url}/frames/start")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # Get frame analysis (5 times)
    print("\n2. Getting frame analysis...")
    for i in range(5):
        try:
            response = requests.get(f"{base_url}/frames")
            if response.status_code == 200:
                data = response.json()
                print(f"\n   Frame {i+1}:")
                print(f"   Posture: {data['posture_percent']}%")
                print(f"   Eye Contact: {data['eye_contact_percent']}%")
                print(f"   Gestures: {data['gestures_percent']}%")
                print(f"   Emotion: {data['emotion']} ({data['emotion_confidence']})")
                print(f"   Overall Score: {data['overall_score']}%")
                print(f"   JSON: {json.dumps(data, indent=2)}")
            else:
                print(f"   Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"   Error: {e}")
        
        time.sleep(2)
    
    # Stop camera
    print("\n3. Stopping camera...")
    try:
        response = requests.post(f"{base_url}/frames/stop")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    print("Make sure your FastAPI server is running:")
    print("python -m uvicorn app:app --reload")
    print("\nPress Enter to test the API...")
    input()
    test_frames_api()