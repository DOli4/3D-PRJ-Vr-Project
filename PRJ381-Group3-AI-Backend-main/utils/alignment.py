import os
from collections import Counter
import csv
from config.settings import SUMMARY_LOG

TARGET_EMOTION = "happy"

def summarize_emotions(results, session_id, log_file="data/logs/facial_emotions_log.csv"):
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

def compute_alignment_score(audio_emotion, audio_score, facial_emotion, facial_score, session_id, log_file=SUMMARY_LOG):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

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
