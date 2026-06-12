from telegram import InlineKeyboardButton, InlineKeyboardMarkup

LANG_KEYBOARD = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"),
        InlineKeyboardButton("தமிழ் 🇮🇳", callback_data="lang_ta"),
    ]
])

MAIN_MENU_EN = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("Search Schemes 🔍", callback_data="menu_search"),
        InlineKeyboardButton("Check Eligibility ✅", callback_data="menu_eligibility"),
    ],
    [
        InlineKeyboardButton("All Schemes 📋", callback_data="menu_all"),
        InlineKeyboardButton("YouTube Help 🎥", callback_data="menu_youtube"),
    ],
])

MAIN_MENU_TA = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("திட்டத்தை தேடுங்கள் 🔍", callback_data="menu_search"),
        InlineKeyboardButton("தகுதி சரிபாருங்கள் ✅", callback_data="menu_eligibility"),
    ],
    [
        InlineKeyboardButton("அனைத்து திட்டங்களும் 📋", callback_data="menu_all"),
        InlineKeyboardButton("YouTube உதவி 🎥", callback_data="menu_youtube"),
    ],
])

SCHEME_ACTION_EN = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("Learn More 📖", callback_data="action_learn"),
        InlineKeyboardButton("YouTube 🎥", callback_data="action_youtube"),
        InlineKeyboardButton("Apply 🔗", callback_data="action_apply"),
    ]
])
