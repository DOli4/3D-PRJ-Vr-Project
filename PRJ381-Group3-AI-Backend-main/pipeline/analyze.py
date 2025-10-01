import os
from datetime import datetime
from transformers import pipeline
import csv
from config.settings import AUDIO_LOG

def analyze_audio_emotion(audio_path, session_id, log_file=AUDIO_LOG):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    print("\n🗣️ Analyzing audio...")

    whisper_pipe = pipeline(
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
