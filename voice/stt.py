import whisper
from pathlib import Path
from config.settings import WHISPER_MODEL

_model = None


def get_model():
    global _model
    if _model is None:
        _model = whisper.load_model(WHISPER_MODEL)
    return _model


def transcribe(audio_path: str) -> str:
    """Transcribe audio file to text using Whisper."""
    result = get_model().transcribe(audio_path)
    return result["text"].strip()
