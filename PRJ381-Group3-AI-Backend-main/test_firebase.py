#!/usr/bin/env python3
"""Test Firebase connection and save functionality"""

from firebase_config import save_analysis_data, save_session_metadata, get_session_data

def test_firebase():
    print("Testing Firebase connection...")
    
    # Test session metadata save
    test_session_id = "test_123"
    metadata = {
        "user_id": "test_user",
        "role": "developer",
        "level": 1,
        "status": "testing"
    }
    
    print("\n1. Testing metadata save...")
    result1 = save_session_metadata(test_session_id, metadata)
    print(f"Metadata save result: {result1}")
    
    # Test analysis data save
    print("\n2. Testing analysis data save...")
    analysis_data = {
        "type": "test_analysis",
        "score": 85.5,
        "details": "This is a test"
    }
    result2 = save_analysis_data(test_session_id, analysis_data, "test_document")
    print(f"Analysis data save result: {result2}")
    
    # Test data retrieval
    print("\n3. Testing data retrieval...")
    retrieved_data = get_session_data(test_session_id)
    print(f"Retrieved data: {retrieved_data}")

if __name__ == "__main__":
    test_firebase()