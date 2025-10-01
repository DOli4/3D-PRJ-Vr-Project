import os
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__ + "/.."))  

UNITY_BASE_DIR = os.getenv("UNITY_BASE_DIR")
if not UNITY_BASE_DIR:
    raise ValueError("⚠️ UNITY_BASE_DIR not set in .env")

UNITY_BASE_PATH = os.path.join(
    os.getenv("LOCALAPPDATA").replace("Local", "LocalLow"),
    *UNITY_BASE_DIR.replace("\\", "/").split("/")
)

# Always absolute paths:
LOG_DIR = os.path.join(ROOT_DIR, "data", "logs")
FACIAL_LOG = os.path.join(LOG_DIR, "facial_emotions_log.csv")
AUDIO_LOG = os.path.join(LOG_DIR, "audio_emotion_log.csv")
SUMMARY_LOG = os.path.join(LOG_DIR, "emotion_summary_log.csv")
