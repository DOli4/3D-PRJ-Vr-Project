import os
import cv2
import csv
import time
from datetime import datetime
from fer import FER
from config.settings import FACIAL_LOG

def capture_multiple_emotions(session_id, duration=20, interval=5, log_file=FACIAL_LOG):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    detector = FER(mtcnn=True)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Webcam not available.")

    results = []
    print(f"📸 Capturing emotions every {interval}s for {duration}s...")

    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Session ID", "Capture Timestamp", "Relative Time (s)", "Emotion", "Confidence"])

        start_time = time.time()
        while (time.time() - start_time) < duration:
            ret, frame = cap.read()
            if not ret:
                print("⚠️ Frame capture failed.")
                continue

            emotion, score = detector.top_emotion(frame)
            rel_time = round(time.time() - start_time)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if emotion:
                print(f"[{rel_time}s] Detected: {emotion} ({round(score * 100)}%)")
                results.append((emotion, score))
                writer.writerow([session_id, timestamp, rel_time, emotion, round(score, 3)])
            else:
                print(f"[{rel_time}s] No emotion detected.")
                writer.writerow([session_id, timestamp, rel_time, "none", 0.0])

    cap.release()
    return results
