import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
BOT_NAME = os.getenv("BOT_NAME", "SchemeOrchestra")
LANGUAGE_DEFAULT = os.getenv("LANGUAGE_DEFAULT", "ta")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

SEARCH_DOMAINS = [
    "tn.gov.in",
    "india.gov.in",
    "myscheme.gov.in",
    "pmschemes.gov.in",
    "mosje.gov.in",
    "tnsche.ac.in",
]
