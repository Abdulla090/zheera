"""
ZHEERA Bot — Handlers
Commands are answered instantly; all free-text goes through Gemini AI.
"""

import random
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from bot.ai import ask_zheera

logger = logging.getLogger("zheera.handlers")

# ── Static quick responses ─────────────────────────────────────────────────────
FACTS_KURDISH = [
    "🏔️ کوردستان ناوچەیەکی شکۆداری چیاییە لە ڕۆژهەڵاتی ناوین.",
    "🎵 کوردەکان موسیقا و هونەری فولکلۆری بەئەندازەی زۆر بەئارام دەگرن.",
    "🌿 زمانی کوردی یەکێکە لە کۆنترین زمانەکانی دنیایە.",
    "🦅 هەڵۆی سیمرغ ئەلامەتی کوردستانە — مانای دەرفەت و ئازادی.",
    "🏛️ شارۆچکەی ئەربیل یەکێکە لە کۆنترین شارێستانییەکانی دنیا.",
    "🌹 گوڵی سوور ئەلامەتی هەژارانی کوردە، کە نیشانەی خەباتن.",
    "📚 شاعیری ئەحمەدی خانی یەکێکی گەورەترین شاعیرانی کوردییە.",
    "🎨 قالیچەی کوردی دەستکرد بەناوبانگی جیهانییەتی هەیە.",
]

# ── Keyboards ──────────────────────────────────────────────────────────────────
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [["🌿 ئامۆژگاری", "ℹ️ دەربارە"], ["🏓 پینگ", "❓ یارمەتی"]],
    resize_keyboard=True,
    input_field_placeholder="پرسیارێک بنووسە...",
)


# ── Commands ───────────────────────────────────────────────────────────────────

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    name = user.first_name if user else "هاوڕێ"
    msg = (
        f"سڵاو {name}! 🌟\n\n"
        f"*من ژیرام* — یاریدەرەی زیرەکی کوردی بە هێزی Gemini AI.\n\n"
        f"دەتوانی هەر پرسیارێک بنووسیت — بەکوردی یان ئینگلیزی.\n"
        f"بۆ فەرمانەکان: /help 📖"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=MAIN_KEYBOARD)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "📖 *فەرمانەکانی ژیرا*\n\n"
        "/start — دەستپێک بکە\n"
        "/help — ئەم لیستە\n"
        "/fact — ئامۆژگاری کوردی\n"
        "/about — دەربارەی ژیرا\n"
        "/ping — چک بکە ئایا بوتەکە زیندووە\n\n"
        "💬 *هەروەها:* هەر پرسیارێک بنووسە — ژیرا بە هێزی Gemini AI وەڵامت دەداتەوە!"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    about_text = (
        "🌟 *دەربارەی ژیرا*\n\n"
        "ژیرا کاراکتەرێکی زیرەکی کوردییە — ناوەکەیش لە زمانی کوردییەوە دێت و "
        "مانای *زیرەکی* و *شارەزایی* دەدات.\n\n"
        "🤖 *بە هێزی:* Google Gemini AI\n"
        "🏔️ خوویەکی چیایی و بەئستایی دەیکات — وەک کۆیلەکانی کوردستان.\n"
        "💬 وەڵام دەداتەوە بە کوردی سۆرانی و ئینگلیزی.\n\n"
        "_دروستکراوە بە خۆشی و هەستی فەرهەنگی کوردی_ 🌹"
    )
    await update.message.reply_text(about_text, parse_mode="Markdown")


async def fact_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    fact = random.choice(FACTS_KURDISH)
    await update.message.reply_text(
        f"🌿 *ئامۆژگاری ژیرا*\n\n{fact}", parse_mode="Markdown"
    )


async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🟢 ژیرا زیندووە! Pong! 🏓")


# ── Keyboard button aliases ────────────────────────────────────────────────────

BUTTON_MAP = {
    "🌿 ئامۆژگاری": fact_command,
    "ℹ️ دەربارە": about_command,
    "🏓 پینگ": ping_command,
    "❓ یارمەتی": help_command,
}


# ── AI message handler ─────────────────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route all free-text messages through Gemini AI with typing indicator."""
    text = (update.message.text or "").strip()

    # Handle keyboard buttons
    if text in BUTTON_MAP:
        await BUTTON_MAP[text](update, context)
        return

    # Show typing action while AI thinks
    await update.message.chat.send_action("typing")

    logger.info("📨 User message: %s", text[:80])
    response = await ask_zheera(text)
    await update.message.reply_text(response)


# ── Application builder ────────────────────────────────────────────────────────

def build_application(token: str) -> Application:
    """Build PTB Application in webhook mode (no polling)."""
    app = Application.builder().token(token).updater(None).build()

    app.add_handler(CommandHandler("start",  start_command))
    app.add_handler(CommandHandler("help",   help_command))
    app.add_handler(CommandHandler("about",  about_command))
    app.add_handler(CommandHandler("fact",   fact_command))
    app.add_handler(CommandHandler("ping",   ping_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return app
