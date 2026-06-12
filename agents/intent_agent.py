from google import genai
from google.genai import types
from config.settings import GEMINI_API_KEY
from config.prompts import INTENT_PROMPT

_client = genai.Client(api_key=GEMINI_API_KEY)

VALID_INTENTS = {"eligibility_check", "scheme_info", "youtube_help", "general_query"}


def classify_intent(user_message: str) -> str:
    try:
        response = _client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{INTENT_PROMPT}\n\nUser message: {user_message}",
        )
        intent = response.text.strip().lower()
        return intent if intent in VALID_INTENTS else "general_query"
    except Exception:
        return "general_query"


