
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
from bot.ai import ask_zheera, list_available_models

logger = logging.getLogger("zheera.handlers")

# ── Static quick responses ─────────────────────────────────────────────────────
FACTS_KURDISH = [
    "🏔️ کوردستان لانکەی شارستانیەتە؛ ئەشکەوتی شانەدەر نموونەی ژیانی نیاندەرتاڵەکانە.",
    "🎵 مۆسیقای کوردی ڕەنگدانەوەی سروشت و بەسەرهاتی نەتەوەکەمانە، پڕە لە سۆز و جوانی.",
    "🌿 زمانی کوردی لقێکی سەرەکییە لە خێزانی زمانە هیندە ئەورووپییەکان و دەوڵەمەندترینە.",
    "🦅 سیمرخ لای کورد هێمای دانایی و نەمرییە، کە لە ئەفسانەکاندا ڕۆڵی پارێزەری هەیە.",
    "🏛️ قەڵای هەولێر کۆنترین شوێنی نیشتەجێبوونی بەردەوامە لە جیهاندا.",
    "🌹 گوڵی نێرگز هێمای بەهار و هیوا و سەربەرزیمانە.",
    "📚 مەم و زین شاکارێکی ئەدەبیی کلاسیکی کوردییە کە ئەحمەدی خانی نووسیویەتی.",
    "🎨 هونەری قاڵیچنین لە کوردستان مێژوویەکی دێرینی هەیە و جێی سەرنجی جیهانییانە.",
]

# ── Keyboards ──────────────────────────────────────────────────────────────────
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [["💎 زانیاریی دانسقە", "ℹ️ دەربارەی ژیرا"], ["لایەنی تەکنیکی ⚙️", "ڕێنمایی 📜"]],
    resize_keyboard=True,
    input_field_placeholder="پرسیارێک بنووسە...",
)


# ── Commands ───────────────────────────────────────────────────────────────────

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    name = user.first_name if user else "ئازیز"
    msg = (
        f"سڵاو {name} گیان! 👋\n\n"
        f"من **ژیرام** — ڕاوێژکارە زیرەکەکەت.\n"
        f"خۆشحاڵم کە دەتبینم! ئامادەم بۆ وەڵامدانەوەی ھەر پرسیارێک کە لەلاتە.\n\n"
        f"تکایە هەرچییەک دەتەوێت، بە کوردیی شیرین لێم بپرسە! ✨"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=MAIN_KEYBOARD)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "📜 **ڕێنماییەکانی بەکارهێنان:**\n\n"
        "دەتوانیت ڕاستەوخۆ پرسیارەکانت بنووسیت، یان ئەم فەرمانانە بەکاربهێنیت:\n"
        "/start — دەستپێکردنەوە\n"
        "/fact — زانیارییەکی سەرنجڕاکێش\n"
        "/about — ناسینی ژیرا\n"
        "/models — بینینی لیستی مۆدێلەکانی Gemini\n"
        "/ping — دڵنیابوونەوە لە کارکردن\n\n"
        "💬 **تێبینی:** من بە کوردی وەڵام دەدەمەوە، بەڵام دەتوانم بە ئینگلیزیش هاوکاریت بکەم!"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    about_text = (
        "ℹ️ **دەربارەی ژیرا**\n\n"
        "من ژیرییەکی دەستکردی پێشکەوتووم، بۆ خزمەتکردنی زمانی کوردی دروستکراوم.\n"
        "ئامانجم ئەوەیە وەڵامی پرسیارەکانت بە شێوەیەکی پوخت، ڕاست و کوردییەکی پەتی بدەمەوە.\n\n"
        "هیوادارم سوودبەخش بم بۆت! 🌹"
    )
    await update.message.reply_text(about_text, parse_mode="Markdown")


async def models_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all available Gemini models for this API key."""
    await update.message.chat.send_action("typing")
    response = await list_available_models()
    await update.message.reply_text(response, parse_mode="Markdown")


async def fact_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    fact = random.choice(FACTS_KURDISH)
    await update.message.reply_text(
        f"💎 **زانیاریی دانسقە**:\n\n{fact}", parse_mode="Markdown"
    )


async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("⚙️ سیستەم بە تەواوی کار دەکات! (Pong)")


# ── Keyboard button aliases ────────────────────────────────────────────────────

BUTTON_MAP = {
    "💎 زانیاریی دانسقە": fact_command,
    "ℹ️ دەربارەی ژیرا": about_command,
    "لایەنی تەکنیکی ⚙️": ping_command,
    "ڕێنمایی 📜": help_command,
}


# ── AI message handler ─────────────────────────────────────────────────────────

THINKING_FRAMES = [
    "🧠 ژیرا بیر دەکاتەوە",
    "🧠 ژیرا بیر دەکاتەوە.",
    "🧠 ژیرا بیر دەکاتەوە..",
    "🧠 ژیرا بیر دەکاتەوە...",
]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route all free-text messages through Gemini AI with thinking animation."""
    text = (update.message.text or "").strip()

    # Handle keyboard buttons
    if text in BUTTON_MAP:
        await BUTTON_MAP[text](update, context)
        return

    # Send thinking animation
    thinking_msg = await update.message.reply_text(THINKING_FRAMES[0])

    # Animate the dots while AI processes
    import asyncio
    ai_task = asyncio.create_task(ask_zheera(text))

    # Show animation frames while waiting
    frame_idx = 1
    while not ai_task.done():
        await asyncio.sleep(0.8)
        if not ai_task.done():
            try:
                await thinking_msg.edit_text(THINKING_FRAMES[frame_idx % len(THINKING_FRAMES)])
                frame_idx += 1
            except Exception:
                pass  # Ignore edit errors (e.g., same text)

    response = await ai_task
    logger.info("📨 User: %s | Response: %s chars", text[:80], len(response))

    # Replace thinking message with actual response
    try:
        await thinking_msg.edit_text(response)
    except Exception:
        # If edit fails (e.g., message too old), send new message
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
    app.add_handler(CommandHandler("models", models_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return app
