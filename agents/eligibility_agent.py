QUESTIONS_EN = [
    ("age", "What is your age?"),
    ("gender", "What is your gender? (male/female/other)"),
    ("education_level", "What is your education level?\n(school / college / graduate / postgraduate)"),
    ("caste", "What is your caste category?\n(BC / MBC / SC / ST / OBC / EBC / general / minority)"),
    ("income_annual", "What is your family's annual income in ₹? (e.g. 150000)"),
    ("first_graduate", "Are you the first person in your family to attend college? (yes/no)"),
    ("state_resident", "Are you a resident of Tamil Nadu? (yes/no)"),
]

QUESTIONS_TA = [
    ("age", "உங்கள் வயது என்ன?"),
    ("gender", "உங்கள் பாலினம் என்ன? (male/female/other)"),
    ("education_level", "உங்கள் கல்வி நிலை என்ன?\n(school / college / graduate / postgraduate)"),
    ("caste", "உங்கள் சாதி வகை என்ன?\n(BC / MBC / SC / ST / OBC / EBC / general / minority)"),
    ("income_annual", "உங்கள் குடும்பத்தின் ஆண்டு வருமானம் ₹ எவ்வளவு? (எ.கா: 150000)"),
    ("first_graduate", "உங்கள் குடும்பத்தில் நீங்கள் முதல் தலைமுறை கல்லூரி படிப்பவரா? (yes/no)"),
    ("state_resident", "நீங்கள் தமிழ்நாட்டில் வசிக்கிறீர்களா? (yes/no)"),
]


def get_next_question(session: dict, lang: str = "en") -> tuple[str | None, str | None]:
    """Returns (field_key, question_text) for the next unanswered question, or (None, None) if complete."""
    questions = QUESTIONS_EN if lang == "en" else QUESTIONS_TA
    for key, question in questions:
        if key not in session:
            return key, question
    return None, None


def parse_answer(field: str, raw: str) -> object:
    raw = raw.strip().lower()
    if field == "age":
        try:
            return int(raw)
        except ValueError:
            return None
    if field == "income_annual":
        try:
            return int(raw.replace(",", "").replace("₹", ""))
        except ValueError:
            return None
    if field in ("first_graduate", "state_resident"):
        return raw in ("yes", "ஆம்", "y", "1", "true")
    return raw
