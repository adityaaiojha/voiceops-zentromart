import os
from dotenv import load_dotenv

load_dotenv()

GNANI_API_KEY = os.getenv("GNANI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Fixed capstone rules
REFERENCE_DATE = "2026-10-20"
TTS_MODEL = "timbre-v2.5"
TTS_VOICE = "Kaveri"
DEFAULT_LANGUAGE = "en-IN"