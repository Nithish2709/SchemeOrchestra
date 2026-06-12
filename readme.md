# 🎼 SchemeOrchestra
## AI-Powered Government Scheme Assistant for Tamil Nadu Students

> A production-grade, intelligent Telegram bot that helps students in Tamil Nadu discover, check eligibility, and apply for government schemes — with personalized recommendations, detailed information, and curated educational videos.

---

## ✅ Current Status: PRODUCTION READY

**15 Schemes** | **100% Free** | **Bilingual** | **AI-Powered** | **Personalized**

All core functionalities, including stateful session management, personalized filtering, fuzzy scheme matching, and scheme-specific YouTube recommendations, are successfully implemented and tested.

---

## 🌟 Key Features

✅ **Personalized Eligibility Checking** - 7 quick questions, instant personalized results
✅ **AI-Powered Search** - LLM-based scheme recommendations filtered by your profile
✅ **Detailed Scheme Information** - Complete eligibility, documents, benefits, and application steps
✅ **Smart YouTube Integration** - Curated educational videos using scheme-specific keywords (no entertainment content)
✅ **Bilingual Support** - Seamless English and Tamil interaction
✅ **15 Government Schemes** - Tamil Nadu State + Central schemes for students
✅ **100% Free** - No cost to use, powered by free-tier APIs

---

## 🎯 What Makes This Special

### 1. Personalized, Not Generic
- **Problem with traditional search:** Shows all schemes to everyone, user must manually check eligibility.
- **Our solution:** User answers 7 questions (age, education, caste, income, etc.), the bot remembers their profile, and all searches are automatically filtered by eligibility. Shows ONLY schemes they qualify for (100% relevance).

### 2. LLM-Powered Intelligence
- **Problem with keyword search:** Misses context, shows irrelevant results.
- **Our solution:** Uses Google Gemini 2.5 Flash for understanding. Natural language explanations, not just data dumps. Considers user's education level, income, background. Conversational responses in user's language.

### 3. Complete Information
- **Problem with simple bots:** Only show scheme name and link.
- **Our solution:** Full eligibility criteria breakdown, complete list of required documents, benefits with amounts and frequency, official application links, and last updated dates. Just one command: `details [scheme name]`.

### 4. Curated Video Content
- **Problem with YouTube search:** Returns music videos, movies, entertainment.
- **Our solution:** Enhanced queries with scheme-specific keywords from database. Filters out entertainment content automatically and shows video descriptions for preview.

---

## 🏗️ Architecture Overview

```
User (Telegram)
     │
     ▼
Telegram Bot Interface (python-telegram-bot)
     │
     ├── Language Detection ──► Auto-detect Tamil/English (Unicode-based)
     ├── Voice Input ─────────► Whisper STT (optional)
     │
     ▼
Orchestrator Agent (Main Controller)
     │
     ├── Intent Classifier
     │   └── eligibility_check / scheme_info / youtube_help / general_query
     │
     ├── Session Manager
     │   └── Stores user profile across messages
     │
     ├── Eligibility Flow Agent
     │   └── Asks 7 questions, stores profile
     │
     ├── Search Agent (LLM-Powered)
     │   ├── Fuzzy search in local database with relevance scoring
     │   ├── Filter by user's eligibility
     │   └── Gemini 2.5 Flash explains results
     │
     ├── YouTube Agent (Curated)
     │   ├── Uses scheme-specific keywords
     │   ├── Filters entertainment content
     │   └── Returns educational videos only
     │
     └── Details Handler
         └── Shows complete scheme information
     │
     ▼
Local Database
     ├── 15 schemes (JSON)
     ├── Eligibility rules
     └── YouTube keywords
```

**Key Improvements:**
- ✅ **Stateful sessions** - Bot remembers your profile
- ✅ **Personalized filtering** - Only eligible schemes shown
- ✅ **LLM intelligence** - Natural explanations, not lists
- ✅ **Fuzzy matching** - Finds schemes with partial keywords and stop-word removal
- ✅ **Content curation** - No random YouTube videos

---

## ⚙️ Technology Stack

| Layer | Tool | Purpose | Cost |
|-------|------|---------|------|
| Bot Platform | python-telegram-bot 21.0+ | Telegram interface | ✅ Free |
| LLM (Core) | Google Gemini 2.5 Flash | AI reasoning, explanations | ✅ Free tier |
| Language Detection | Unicode-based Tamil detector | Tamil/English auto-detect | ✅ Free |
| Database | JSON files (local) | 15 schemes + rules | ✅ Free |
| YouTube API | YouTube Data API v3 | Curated video search | ✅ Free tier |
| Speech (Optional) | OpenAI Whisper (local) | Voice → Text | ✅ Free |
| TTS (Optional) | gTTS | Text → Voice | ✅ Free |
| Language | Python 3.10+ | Core language | ✅ Free |

**Total Cost:** ₹0 (All free tier)

---

## 📊 15 Government Schemes Covered

### Tamil Nadu State Schemes (for Students)
1. Chief Minister's Breakfast Scheme
2. Free Laptop Scheme
3. First Generation Graduate Scholarship - ₹10k/year
4. Free Uniform and Books Scheme
5. BC, MBC Scholarship for School/College Students
6. SC/ST Scholarship
7. Amma Two-Wheeler Scheme - 50% subsidy
8. Free TNPSC Coaching
9. Minority Scholarship Scheme
10. Dr. Ambedkar Law Entrance Coaching

### Central Schemes for Tamil Nadu Students
1. PM Scholarship Scheme - ₹2.5-3k/month
2. National Means-cum-Merit Scholarship - ₹12k/year
3. PM YASASVI Scholarship - ₹75k-1.25L/year
4. Post-Matric Scholarship (Central)
5. Pradhan Mantri Kaushal Vikas Yojana

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Telegram Bot Token (from @BotFather)
- Google Gemini API Key (free from ai.google.dev)
- YouTube Data API v3 Key (optional, for video recommendations)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/your-username/scheme-orchestra.git
cd scheme-orchestra

# 2. Create virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install python-telegram-bot google-generativeai requests loguru pydub

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 5. Verify Setup
python test_quick_check.py

# 6. Run the bot
python main.py
```

### Environment Variables (.env)

```env
# Required
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_from_botfather
GEMINI_API_KEY=your_gemini_api_key_from_google

# Optional
YOUTUBE_API_KEY=your_youtube_api_key
LOG_LEVEL=INFO
```

---

## 📱 Telegram Bot Commands

- `/start` - Welcome message + language selection
- `/reset` - Clear your profile and start over
- `/help` - Show help and examples

**Special Commands:**
- `details [scheme name]` - Show complete scheme information
- `youtube [scheme name]` - Get educational video recommendations

---

## 🔐 Legal & Ethical Guidelines

### ✅ What This Bot Does (Legally Safe)
- Aggregates **publicly available** government scheme information
- Links to **official government websites** as the source
- Does **not** collect sensitive personal data permanently (only session-based for eligibility check)
- Does **not** impersonate any government authority
- Clearly states it is an **AI assistant**, not an official government service

### ⚠️ Important Disclaimers
- "This bot provides informational guidance only. Always verify eligibility with the official government website."
- "SchemeOrchestra is not affiliated with the Government of Tamil Nadu or Government of India."
- "Scheme details may change. Check the official source before applying."

---

## 👨‍💻 Contributing

Help expand SchemeOrchestra by adding more schemes:

1. Fork the repository
2. Add scheme JSON to `data/schemes/tamilnadu_schemes.json` or `data/schemes/central_schemes_tn.json`
3. Add eligibility rules to `data/eligibility_rules/rules.json`
4. Run `python scripts/validate_data.py`
5. Submit a Pull Request

---

## 📄 License

MIT License — Free to use, modify, and distribute.

**This project is not affiliated with or endorsed by the Government of Tamil Nadu or Government of India.**

---

*SchemeOrchestra — Helping every Tamil Nadu student find the scheme they deserve 🎼*