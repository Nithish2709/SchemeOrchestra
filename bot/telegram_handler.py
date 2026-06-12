from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config.settings import TELEGRAM_BOT_TOKEN
from agents.orchestrator_agent import get_session, clear_session
from bot.keyboards import LANG_KEYBOARD, MAIN_MENU_EN, MAIN_MENU_TA
from bot.message_router import route_text, route_voice


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎼 *Welcome to SchemeOrchestra!*\n"
        "I help students in Tamil Nadu find government schemes.\n\n"
        "Choose language / மொழி தேர்வு:",
        parse_mode="Markdown",
        reply_markup=LANG_KEYBOARD,
    )


async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clear_session(update.effective_user.id)
    await update.message.reply_text("Session reset. Send /start to begin again.")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎼 *SchemeOrchestra Help*\n\n"
        "/start — Start the bot\n"
        "/reset — Reset your session\n\n"
        "Just type your question or send a voice message!\n"
        "Examples:\n"
        "• 'Check my eligibility'\n"
        "• 'Tell me about laptop scheme'\n"
        "• 'YouTube videos about scholarships'",
        parse_mode="Markdown",
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    session = get_session(user_id)
    data = query.data

    if data == "lang_en":
        session["lang"] = "en"
        await query.edit_message_text(
            "Great! What would you like to do?", reply_markup=MAIN_MENU_EN
        )
    elif data == "lang_ta":
        session["lang"] = "ta"
        await query.edit_message_text(
            "நலம். நீங்கள் என்ன செய்ய விரும்புகிறீர்கள்?", reply_markup=MAIN_MENU_TA
        )
    elif data == "menu_eligibility":
        session["intent"] = "eligibility_check"
        session["profile"] = {}
        lang = session.get("lang", "en")
        msg = "What is your age?" if lang == "en" else "உங்கள் வயது என்ன?"
        await query.edit_message_text(msg)
    elif data == "menu_search":
        lang = session.get("lang", "en")
        # Check if user has profile info
        profile = session.get("profile", {})
        if len(profile) < 3:  # Less than 3 fields filled
            msg = (
                "To give you personalized scheme recommendations, I need to know a bit about you.\n\n"
                "Would you like to:\n"
                "1. Check eligibility first (recommended) - I'll ask 7 quick questions\n"
                "2. Just search schemes (you'll see all schemes, not personalized)\n\n"
                "Type '1' for eligibility check or just type your search query to proceed."
            ) if lang == "en" else (
                "நீங்களுக்கு தனிப்படுத்தப்பட்ட திட்டங்களை பரிந்துரைக்க, உங்களை பற்றி தெரிய வேண்டும்.\n\n"
                "1. முதலில் தகுதி சரிபார்க்கவும் (7 கேள்விகள்)\n"
                "2. திட்டங்களை தேடவும்\n\n"
                "'1' என டைப் செய்யவும் அல்லது உங்கள் தேடலை டைப் செய்யவும்."
            )
        else:
            msg = "What scheme are you looking for?" if lang == "en" else "நீங்கள் எந்த திட்டத்தை தேடுகிறீர்கள்?"
        await query.edit_message_text(msg)
    elif data == "menu_youtube":
        lang = session.get("lang", "en")
        msg = "Which scheme do you want YouTube help for?" if lang == "en" else "எந்த திட்டத்திற்கு YouTube உதவி வேண்டும்?"
        await query.edit_message_text(msg)
    elif data == "menu_all":
        from tools.scheme_lookup_tool import scheme_lookup_tool
        from utils.formatter import format_eligible_schemes
        lang = session.get("lang", "en")
        all_schemes = scheme_lookup_tool("")  # Empty query returns all
        msg = f"Total schemes available: {len(all_schemes)}\n\n" if lang == "en" else f"மொத்த திட்டங்கள்: {len(all_schemes)}\n\n"
        msg += format_eligible_schemes(all_schemes[:10], lang)
        await query.edit_message_text(msg)


def build_app() -> Application:
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route_text))
    app.add_handler(MessageHandler(filters.VOICE, route_voice))
    return app
