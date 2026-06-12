from loguru import logger
from config.settings import LOG_LEVEL, TELEGRAM_BOT_TOKEN
from bot.telegram_handler import build_app

import sys
import codecs
if sys.platform == 'win32':
    try:
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')
    except Exception:
        pass

from pathlib import Path

def check_initialization():
    db_path = Path("data/schemes.db")
    chroma_path = Path("data/chroma_db")
    if not db_path.exists() or not chroma_path.exists():
        logger.info("Initializing Database and ChromaDB RAG...")
        from initialize_db import initialize_system
        initialize_system()

def main():
    logger.add("logs/bot.log", level=LOG_LEVEL, rotation="10 MB", serialize=True)

    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set. Please configure your .env file.")
        return

    check_initialization()

    logger.info("Starting SchemeOrchestra bot...")
    app = build_app()
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
