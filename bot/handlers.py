"""
ZHEERA Bot — Kurdish Intelligent Character 🌟
Bot handlers: commands, messages, and personality responses.
"""

from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import random

# ── Personality Lines (Kurdish + English) ────────────────────────────────────
GREETINGS = [
    "سڵاو! 👋 من ژیرام، یاریدەرە زیرەکەکەت. چۆن دەتوانم یاریت بدەم؟",
    "بەخێر بێیت! ✨ ژیرا ئێرەیە بۆ بەرپرسیاریتان. چ پرسیارێکت هەیە؟",
    "هەڵۆ! 🌟 من ژیرام — زیرەکێکی کوردی. دەتوانم چۆن کومەکت بکەم؟",
]

THINKING = [
    "🤔 چکەلی تەمەن بەرپرسیارم ...",
    "✨ ژیرا بیر دەکاتەوە ...",
    "🧠 لە کارکردندایم ...",
]

UNKNOWN = [
    "ببورە، ئەمە فامم نەبوو. 😅 تکایە دووبارە بکەوە یا /help بنووسە.",
    "ئەمە لە دەرکەوتنی منەوە. 🤷 /help بنووسە بۆ تێگەشتن.",
    "هنر نییە فامم کرد! تکایە جیاتر بسیارە. 💬",
]

FACTS_KURDISH = [
    "🏔️ کوردستان ناوچەیەکی شکۆداری چیاییە لە ڕۆژهەڵاتی ناوین.",
    "🎵 کوردەکان موسیقا و هونەری فولکلۆری بەئەندازەی زۆر بەئارام دەگرن.",
    "🌿 زمانی کوردی یەکێکە لە کۆنترین زمانەکانی دنیایە.",
    "🦅 هەڵۆی سیمرغ ئەلامەتی کوردستانە — مانای دەرفەت و ئازادی.",
    "🏛️ شارۆچکەی ئەربیل یەکێکە لە کۆنترین شارێستانییەکانی دنیا.",
    "🌹 گوڵی سوور ئەلامەتی هەژارانی کوردە، کە نیشانەی خەباتن.",
]


# ── Command Handlers ──────────────────────────────────────────────────────────

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Welcome message with ZHEERA's Kurdish personality."""
    user = update.effective_user
    name = user.first_name if user else "هاوڕێ"
    msg = (
        f"سڵاو {name}! 🌟\n\n"
        f"*من ژیرام* — یاریدەرەی زیرەکی کوردی.\n\n"
        f"ئامادەم بۆ وەڵامدانەوەی پرسیارەکانت، گفتوگۆ، یان دانانی زانیاری.\n\n"
        f"بۆ زانینی فەرمانەکان بنووسە /help 📖"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show available commands."""
    help_text = (
        "📖 *فەرمانەکانی ژیرا*\n\n"
        "/start — دەستپێک بکە\n"
        "/help — ئەم لیستە\n"
        "/fact — ئامۆژگاری کوردی بەکوردی\n"
        "/about — دەربارەی ژیرا\n"
        "/ping — چک بکە ئایا بوتەکە زیندووە\n\n"
        "📩 هەروەها دەتوانی هەر پەیامێک بنێری — ژیرا وەڵامت دەداتەوە!"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ZHEERA's backstory."""
    about_text = (
        "🌟 *دەربارەی ژیرا*\n\n"
        "ژیرا کاراکتەرێکی زیرەکی کوردییە — ناوەکەیش لە زمانی کوردییەوە دێت و "
        "مانای *زیرەکی* و *شارەزایی* دەدات.\n\n"
        "🏔️ خوویەکی چیایی و بەئستایی دەیکات — وەک کۆیلەکانی کوردستان.\n"
        "🤖 بە هەڵبژاردنی تەکنەلۆژیا و کولتووری کوردی تێکەڵ کراوە.\n"
        "💬 ئامادەیە وەڵام بداتەوە بە کوردی و ئینگلیزی.\n\n"
        "_دروستکراوە بە خۆشی و هەستی فەرهەنگی کوردی_ 🌹"
    )
    await update.message.reply_text(about_text, parse_mode="Markdown")


async def fact_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Share a random Kurdish fact."""
    fact = random.choice(FACTS_KURDISH)
    await update.message.reply_text(
        f"🌿 *ئامۆژگاری ژیرا*\n\n{fact}", parse_mode="Markdown"
    )


async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Health check."""
    await update.message.reply_text("🟢 ژیرا زیندووە! Pong! 🏓")


# ── Message Handler ───────────────────────────────────────────────────────────

KEYWORD_RESPONSES: dict[str, str] = {
    # Kurdish keywords
    "سڵاو": random.choice(GREETINGS),
    "باش": "خۆشحاڵم! 😊 چۆت دەیەوێت کومەکت بکەم؟",
    "سپاس": "خوش بێ! 🙏 هەر کاتێک پرسیارت هەبوو ئێرەم.",
    "کوردستان": "🏔️ کوردستان خاکی شکۆداری و فەرهەنگی بەرزە! چییەتی رایەکی تر؟",
    "ژیرا": "بەڵێ دەمخوێنمەتەوە! 😄 چۆن دەتوانم یاریت بدەم؟",
    # English keywords
    "hello": random.choice(GREETINGS),
    "hi": "Hey there! 👋 ZHEERA is here. How can I help you?",
    "thanks": "You're welcome! 🙏 Ask me anything anytime.",
    "help": "Type /help to see my commands 📖",
    "kurdish": "🏔️ Kurdistan is a land of rich culture, ancient history, and resilient people!",
    "zheera": "That's me! 🌟 How can I assist you today?",
    "who are you": (
        "I'm *ZHEERA* — a Kurdish intelligent character powered by AI. 🤖\n"
        "Type /about to learn more about me!"
    ),
}


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Catch-all message handler with keyword matching."""
    text = update.message.text or ""
    lower = text.lower().strip()

    # Check keyword map first
    for keyword, response in KEYWORD_RESPONSES.items():
        if keyword in lower:
            await update.message.reply_text(response, parse_mode="Markdown")
            return

    # Fallback: thoughtful unknown response
    await update.message.reply_text(random.choice(UNKNOWN))


# ── Application Builder ───────────────────────────────────────────────────────

def build_application(token: str) -> Application:
    """Build and configure the PTB Application (no polling — webhook mode)."""
    app = Application.builder().token(token).updater(None).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("fact", fact_command))
    app.add_handler(CommandHandler("ping", ping_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return app
