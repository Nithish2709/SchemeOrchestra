from gtts import gTTS
from pydub import AudioSegment
import tempfile
import os


def text_to_voice(text: str, lang: str = "ta") -> str:
    """Convert text to .ogg voice file. Returns file path."""
    tts = gTTS(text=text, lang=lang)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as mp3_file:
        mp3_path = mp3_file.name
    tts.save(mp3_path)

    ogg_path = mp3_path.replace(".mp3", ".ogg")
    AudioSegment.from_mp3(mp3_path).export(ogg_path, format="ogg", codec="libopus")
    os.remove(mp3_path)
    return ogg_path
