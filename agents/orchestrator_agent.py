from google import genai
from config.settings import GEMINI_API_KEY
from config.prompts import ORCHESTRATOR_PROMPT
from agents.intent_agent import classify_intent
from agents.eligibility_agent import get_next_question, parse_answer
from agents.search_agent import search_scheme_info
from agents.youtube_agent import get_youtube_recommendations
from tools.eligibility_check_tool import eligibility_check_tool
from tools.scheme_lookup_tool import scheme_lookup_tool
from utils.formatter import format_eligible_schemes
from utils.language_detector import detect_language

_client = genai.Client(api_key=GEMINI_API_KEY)

# In-memory sessions: {user_id: {"lang": str, "intent": str, "profile": dict, "history": list}}
_sessions: dict[int, dict] = {}


def get_session(user_id: int) -> dict:
    if user_id not in _sessions:
        _sessions[user_id] = {"lang": None, "intent": None, "profile": {}, "history": []}
    return _sessions[user_id]


def clear_session(user_id: int):
    _sessions.pop(user_id, None)


async def handle_message(user_id: int, text: str) -> str:
    session = get_session(user_id)

    lang = session.get("lang")
    if not lang:
        lang = "en"  # fallback if somehow not set

    # If currently in eligibility collection flow
    if session["intent"] == "eligibility_check":
        return _handle_eligibility_flow(session, text, lang)
    
    # Check for "details" command
    if text.lower().startswith("details ") or text.lower().startswith("விவரம் "):
        query = text.split(maxsplit=1)[1] if len(text.split()) > 1 else ""
        return _handle_scheme_details(query, lang)

    # Classify intent for new messages
    intent = classify_intent(text)
    session["intent"] = intent

    if intent == "eligibility_check":
        session["profile"] = {}
        return _handle_eligibility_flow(session, text, lang)

    if intent == "scheme_info":
        # Pass user profile if available for personalized recommendations
        user_profile = session.get("profile", {})
        return search_scheme_info(text, lang, user_profile)

    if intent == "youtube_help":
        return get_youtube_recommendations(text, lang)

    # General query — use Gemini directly with scheme context
    return _handle_general_query(session, text, lang)


def _handle_eligibility_flow(session: dict, text: str, lang: str) -> str:
    profile = session["profile"]

    from agents.eligibility_agent import QUESTIONS_EN, QUESTIONS_TA
    questions = QUESTIONS_EN if lang == "en" else QUESTIONS_TA

    # Find the field we're expecting an answer for (first unanswered field)
    pending_field = None
    for key, _ in questions:
        if key not in profile:
            pending_field = key
            break

    # If we have a pending field, parse the user's answer and store it
    if pending_field:
        parsed = parse_answer(pending_field, text)
        if parsed is not None:
            profile[pending_field] = parsed

    # Ask next question
    next_field, next_question = get_next_question(profile, lang)
    if next_question:
        return next_question

    # All questions answered — run eligibility check
    try:
        from loguru import logger
        logger.info(f"Running eligibility check with profile: {profile}")
        eligible = eligibility_check_tool(profile)
        logger.info(f"Found {len(eligible)} eligible schemes")
        session["intent"] = None  # reset intent
        return format_eligible_schemes(eligible, lang)
    except Exception as e:
        from loguru import logger
        logger.exception(f"Eligibility check failed: {e}")
        raise


def _handle_general_query(session: dict, text: str, lang: str) -> str:
    """Handle general queries using LLM with scheme database context."""
    
    # Get relevant schemes for context
    matching_schemes = scheme_lookup_tool(text)
    
    scheme_context = ""
    if matching_schemes:
        scheme_context = "\n\nRelevant schemes in database:\n"
        for s in matching_schemes[:5]:
            name = s.get(f"name_{lang}") or s.get("name_en")
            desc = s.get(f"description_{lang}") or s.get("description_en")
            scheme_context += f"- {name}: {desc}\n"
    else:
        from tools.search_tool import search_tool
        web_results = search_tool(text)
        if web_results and not (len(web_results) > 0 and "error" in web_results[0]):
            scheme_context = "\n\nWeb Search Results:\n"
            for res in web_results[:5]:
                scheme_context += f"- {res.get('title', '')}: {res.get('snippet', '')} (URL: {res.get('link', '')})\n"
    
    prompt = f"{ORCHESTRATOR_PROMPT}\n{scheme_context}\n\nUser query: {text}\n\nRespond in {'English' if lang == 'en' else 'Tamil'}."
    
    session["history"].append({"role": "user", "parts": [text]})
    kwargs = {
        "model": "gemini-2.5-flash",
        "contents": [{"role": "user", "parts": [{"text": prompt}]}]
    }
    
    if lang == "ta":
        from config.prompts import TAMIL_SYSTEM_PROMPT
        from google.genai import types
        kwargs["config"] = types.GenerateContentConfig(system_instruction=TAMIL_SYSTEM_PROMPT)
    else:
        from config.prompts import ENGLISH_SYSTEM_PROMPT
        from google.genai import types
        kwargs["config"] = types.GenerateContentConfig(system_instruction=ENGLISH_SYSTEM_PROMPT)
        
    try:
        response = _client.models.generate_content(**kwargs)
        reply = response.text
    except Exception as e:
        from loguru import logger
        logger.exception(f"General query failed: {e}")
        if matching_schemes:
            from utils.formatter import format_eligible_schemes
            reply = format_eligible_schemes(matching_schemes[:3], lang)
        else:
            reply = "I'm currently unable to process your request. Please try again in a moment." if lang == "en" else "உங்கள் கோரிக்கையை செயலாக்க முடியவில்லை. மீண்டும் முயற்சிக்கவும்."
    
    session["history"].append({"role": "model", "parts": [reply]})
    return reply


def _handle_scheme_details(query: str, lang: str) -> str:
    """Show detailed information for a specific scheme using SQLite."""
    from utils.formatter import format_scheme_detailed
    from tools.unified_search import scheme_lookup_tool
    
    schemes = scheme_lookup_tool(query)
    
    if not schemes:
        return "Scheme not found. Please try a different name." if lang == "en" else "திட்டம் காணவில்லை. வேறு பெயரை முயற்சிக்கவும்."
    
    # Show detailed view of the first matching scheme
    return format_scheme_detailed(schemes[0], lang)
