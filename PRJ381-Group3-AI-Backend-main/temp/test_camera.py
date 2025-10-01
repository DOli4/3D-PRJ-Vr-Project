import cv2

def test_camera():
    print("Testing camera access...")
    
    # Try different camera indices
    for i in range(3):
        print(f"Trying camera index {i}...")
        cap = cv2.VideoCapture(i)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ Camera {i} working! Frame shape: {frame.shape}")
                cap.release()
                return i
            else:
                print(f"❌ Camera {i} opened but no frame")
        else:
            print(f"❌ Camera {i} not available")
        
        cap.release()
    
    print("❌ No working camera found")
    return None

if __name__ == "__main__":
    working_camera = test_camera()
    if working_camera is not None:
        print(f"\nUse camera index {working_camera} in your code")
    else:
        print("\nCheck if your camera is connected and not being used by another app")