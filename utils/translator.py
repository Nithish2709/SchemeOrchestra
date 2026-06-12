from deep_translator import GoogleTranslator


def translate(text: str, target_lang: str = "ta") -> str:
    """Translate text to target language ('ta' or 'en')."""
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except Exception:
        return text
