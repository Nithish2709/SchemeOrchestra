def detect_language(text: str) -> str:
    """Returns 'ta' for Tamil, 'en' for English, defaults to 'en'.
    Uses simple Unicode range detection for Tamil characters.
    """
    if not text:
        return "en"
    
    # Count Tamil Unicode characters (Tamil block: U+0B80 to U+0BFF)
    tamil_chars = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF')
    
    # If more than 20% of non-space characters are Tamil, classify as Tamil
    non_space_chars = sum(1 for c in text if not c.isspace())
    if non_space_chars > 0 and (tamil_chars / non_space_chars) > 0.2:
        return "ta"
    
    return "en"
