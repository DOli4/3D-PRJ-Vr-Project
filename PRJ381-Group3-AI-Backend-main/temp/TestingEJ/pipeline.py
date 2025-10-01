import os
os.environ["TRANSFORMERS_NO_TF"] = "1"
import cv2
import csv
import time
import torch
from datetime import datetime
from fer import FER
from transformers import pipeline
from collections import Counter

# === CONFIGURATION ===
UNITY_BASE_PATH = r"C:\Users\chesa\AppData\LocalLow\DefaultCompany\VRInterviewSimulator"
SESSION_ID = "Session_1753410568"  # ✅ change this to your actual Unity folder
RESPONSE_FILENAME = "response_1.wav"  # or loop through all response_*.wav later

# === FACIAL EMOTION (Snapshot-based analysis) ===
def capture_multiple_emotions(session_id, duration=20, interval=5, log_file="facial_emotions_log.csv"):
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

# === FACIAL AGGREGATION ===
def summarize_emotions(results, session_id, log_file="facial_emotions_log.csv"):
    emotion_counter = Counter()
    weighted_scores = {}

    for emotion, score in results:
        emotion_counter[emotion] += 1
        weighted_scores.setdefault(emotion, []).append(score)

    most_common = emotion_counter.most_common(1)[0][0]
    avg_score = round(sum(weighted_scores[most_common]) / len(weighted_scores[most_common]), 2)

    print(f"\n🧠 Most frequent emotion: {most_common} (avg. confidence: {round(avg_score * 100)}%)")

    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["SESSION SUMMARY", "", "", "", ""])
        writer.writerow(["Session ID", "Most Common Emotion", "Average Score", "", ""])
        writer.writerow([session_id, most_common, avg_score, "", ""])
        writer.writerow([])

    return most_common, avg_score

# === AUDIO EMOTION ANALYSIS ===
def analyze_audio_emotion(audio_path, session_id, log_file="audio_emotion_log.csv"):
    print("\n🗣️ Analyzing audio...")

    whisper_pipe = whisper_pipe = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-small",
    framework="pt",               
    return_timestamps=True         
)

    result_whisper = whisper_pipe(audio_path)
    transcript = result_whisper["text"]
    print("📝 Transcript:", transcript)

    emotion_pipe = pipeline("text-classification", model="bhadresh-savani/distilbert-base-uncased-emotion", framework="pt")
    result = emotion_pipe(transcript)[0]

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Session ID", "Timestamp", "Transcript", "Emotion", "Confidence"])
        writer.writerow([session_id, timestamp, transcript, result['label'], round(result['score'], 3)])
        writer.writerow(["SESSION SUMMARY", "", "", "", ""])
        writer.writerow(["Session ID", "Top Audio Emotion", "Confidence"])
        writer.writerow([session_id, result['label'], round(result['score'], 3)])
        writer.writerow([])

    print(f"🎯 Audio Emotion: {result['label']} ({round(result['score'] * 100)}%)")
    return result['label'], result['score']

# === FINAL SCORE ===
TARGET_EMOTION = "happy"

def compute_alignment_score(audio_emotion, audio_score, facial_emotion, facial_score, session_id, log_file="emotion_summary_log.csv"):
    total_score = 0
    if audio_emotion == TARGET_EMOTION:
        total_score += audio_score
    if facial_emotion == TARGET_EMOTION:
        total_score += facial_score
    final_score = round((total_score / 2) * 100)

    print(f"\n✅ Final Alignment Score: {final_score}%")

    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Session ID", "Facial Emotion", "Facial Score", "Audio Emotion", "Audio Score", "Final Alignment Score"])
        writer.writerow([session_id, facial_emotion, round(facial_score, 3), audio_emotion, round(audio_score, 3), final_score])
        writer.writerow([])

    return final_score


def list_unity_sessions(base_path):
    folders = sorted([f for f in os.listdir(base_path) if f.startswith("Session_")])
    if not folders:
        print("❌ No Unity session folders found.")
        return None

    print("\n=== 🎧 Available Unity Sessions ===")
    for i, folder in enumerate(folders, start=1):
        print(f"[{i}] {folder}")
    
    while True:
        try:
            choice = int(input(f"\nSelect a session to analyze (1–{len(folders)}): "))
            if 1 <= choice <= len(folders):
                return folders[choice - 1]
        except ValueError:
            pass
        print("⚠️ Invalid choice. Try again.")


# === MAIN ===
if __name__ == "__main__":
    selected_session = list_unity_sessions(os.path.join(UNITY_BASE_PATH, "Recordings"))
    if selected_session is None:
        exit(1)

    session_path = os.path.join(UNITY_BASE_PATH, "Recordings", selected_session)
    if not os.path.exists(session_path):
        raise FileNotFoundError(f"❌ Session folder not found: {session_path}")

    # Find and sort response_*.wav files by numeric order
    wav_files = sorted([
        f for f in os.listdir(session_path)
        if f.startswith("response_") and f.endswith(".wav")
    ], key=lambda x: int(x.split("_")[1].split(".")[0]))

    if not wav_files:
        print("❌ No response_*.wav files found in selected session.")
        exit(1)

    print(f"\n📁 Analyzing all responses in: {selected_session}\n")

    for i, wav_filename in enumerate(wav_files, start=1):
        audio_path = os.path.join(session_path, wav_filename)
        print(f"\n🎧 [{i}/{len(wav_files)}] Processing {wav_filename}...")

        facial_emotions = capture_multiple_emotions(selected_session, duration=20, interval=5)
        audio_emotion, audio_score = analyze_audio_emotion(audio_path, selected_session)
        facial_emotion, facial_score = summarize_emotions(facial_emotions, selected_session)
        compute_alignment_score(audio_emotion, audio_score, facial_emotion, facial_score, selected_session)

