import os
import tempfile
from telegram import Update
from telegram.ext import ContextTypes
from agents.orchestrator_agent import handle_message, get_session, clear_session
from voice.stt import transcribe
from voice.tts import text_to_voice
from pydub import AudioSegment


async def route_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = get_session(user_id)
    
    if session.get("lang") is None:
        from bot.keyboards import LANG_KEYBOARD
        await update.message.reply_text(
            "Please choose your preferred language / உங்கள் விருப்ப மொழியைத் தேர்ந்தெடுக்கவும்:",
            reply_markup=LANG_KEYBOARD,
        )
        return
        
    text = update.message.text
    try:
        reply = await handle_message(user_id, text)
        # Try with markdown first, fallback to plain text if it fails
        try:
            await update.message.reply_text(reply, parse_mode="Markdown")
        except Exception:
            await update.message.reply_text(reply, parse_mode=None)
    except Exception as e:
        from loguru import logger
        logger.exception(f"Error handling text message: {e}")
        await update.message.reply_text("Something went wrong. Please try again or send /reset.")


async def route_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = get_session(user_id)
    
    if session.get("lang") is None:
        from bot.keyboards import LANG_KEYBOARD
        await update.message.reply_text(
            "Please choose your preferred language / உங்கள் விருப்ப மொழியைத் தேர்ந்தெடுக்கவும்:",
            reply_markup=LANG_KEYBOARD,
        )
        return
        
    try:
        voice_file = await update.message.voice.get_file()
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as ogg_f:
            ogg_path = ogg_f.name
        await voice_file.download_to_drive(ogg_path)

        wav_path = ogg_path.replace(".ogg", ".wav")
        AudioSegment.from_ogg(ogg_path).export(wav_path, format="wav")
        os.remove(ogg_path)

        text = transcribe(wav_path)
        os.remove(wav_path)

        # Feed the transcribed text into the existing agent flow
        reply_text = await handle_message(user_id, text)

        # Retrieve the updated language preference after detection
        session = get_session(user_id)
        lang = session.get("lang", "en")

        # Always send both text and voice reply together
        try:
            await update.message.reply_text(reply_text, parse_mode="Markdown")
        except Exception:
            await update.message.reply_text(reply_text, parse_mode=None)

        ogg_reply = text_to_voice(reply_text, lang=lang)
        await update.message.reply_voice(voice=open(ogg_reply, "rb"))
        os.remove(ogg_reply)
    except Exception as e:
        await update.message.reply_text("Could not process voice message. Please make sure ffmpeg is installed, or type your message instead.")
