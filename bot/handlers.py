"""
ZHEERA Bot — Handlers
Commands + AI routing + user settings (model & thinking toggle).
"""

import random
import asyncio
import logging
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from bot.ai import (
    ask_zheera,
    list_available_models,
    AVAILABLE_MODELS,
    get_user_settings,
    set_user_model,
    set_user_thinking,
)

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
    [["💎 زانیاریی دانسقە", "ℹ️ دەربارەی ژیرا"], ["⚙️ ڕێکخستنەکان", "ڕێنمایی 📜"]],
    resize_keyboard=True,
    input_field_placeholder="پرسیارێک بنووسە...",
)


# ── Settings keyboard builder ─────────────────────────────────────────────────
def build_settings_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Build inline keyboard showing current model & thinking status."""
    settings = get_user_settings(user_id)
    current_model = settings["model"]
    thinking_on = settings["thinking"]

    rows = []

    # Model selection buttons
    rows.append([InlineKeyboardButton("── 🤖 مۆدێل هەڵبژێرە ──", callback_data="noop")])
    for model_id, label in AVAILABLE_MODELS.items():
        check = " ✅" if model_id == current_model else ""
        rows.append([InlineKeyboardButton(
            f"{label}{check}",
            callback_data=f"model:{model_id}",
        )])

    # Thinking toggle
    thinking_label = "🟢 بیرکردنەوە: چالاکە" if thinking_on else "🔴 بیرکردنەوە: ناچالاکە"
    rows.append([InlineKeyboardButton("── 🧠 بیرکردنەوە ──", callback_data="noop")])
    rows.append([InlineKeyboardButton(thinking_label, callback_data="toggle_thinking")])

    return InlineKeyboardMarkup(rows)


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
        "/settings — ڕێکخستنی مۆدێل و بیرکردنەوە\n"
        "/models — بینینی هەموو مۆدێلەکانی Gemini\n"
        "/fact — زانیارییەکی سەرنجڕاکێش\n"
        "/about — ناسینی ژیرا\n"
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


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show settings panel with model selection and thinking toggle."""
    user_id = update.effective_user.id
    settings = get_user_settings(user_id)
    current_model = settings["model"]
    model_label = AVAILABLE_MODELS.get(current_model, current_model)
    thinking_status = "چالاک ✅" if settings["thinking"] else "ناچالاک ❌"

    text = (
        "⚙️ **ڕێکخستنەکانی ژیرا**\n\n"
        f"🤖 **مۆدێلی ئێستا:** {model_label}\n"
        f"🧠 **بیرکردنەوە:** {thinking_status}\n\n"
        "لە خوارەوە هەڵبژاردنەکانت بگۆڕە:"
    )
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=build_settings_keyboard(user_id),
    )


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
    user_id = update.effective_user.id
    settings = get_user_settings(user_id)
    model_label = AVAILABLE_MODELS.get(settings["model"], settings["model"])
    thinking = "✅" if settings["thinking"] else "❌"
    await update.message.reply_text(
        f"⚙️ سیستەم کار دەکات! (Pong)\n\n"
        f"🤖 مۆدێل: {model_label}\n"
        f"🧠 بیرکردنەوە: {thinking}"
    )


# ── Callback handler for inline buttons ────────────────────────────────────────

async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline button presses for settings."""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if data == "noop":
        return

    if data.startswith("model:"):
        model_id = data.split(":", 1)[1]
        if model_id in AVAILABLE_MODELS:
            set_user_model(user_id, model_id)
            model_label = AVAILABLE_MODELS[model_id]
            logger.info("👤 User %s switched to model: %s", user_id, model_id)

    elif data == "toggle_thinking":
        settings = get_user_settings(user_id)
        new_val = not settings["thinking"]
        set_user_thinking(user_id, new_val)
        logger.info("👤 User %s toggled thinking: %s", user_id, new_val)

    # Update the settings message with new state
    settings = get_user_settings(user_id)
    current_model = settings["model"]
    model_label = AVAILABLE_MODELS.get(current_model, current_model)
    thinking_status = "چالاک ✅" if settings["thinking"] else "ناچالاک ❌"

    text = (
        "⚙️ **ڕێکخستنەکانی ژیرا**\n\n"
        f"🤖 **مۆدێلی ئێستا:** {model_label}\n"
        f"🧠 **بیرکردنەوە:** {thinking_status}\n\n"
        "لە خوارەوە هەڵبژاردنەکانت بگۆڕە:"
    )
    try:
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=build_settings_keyboard(user_id),
        )
    except Exception:
        pass  # Message unchanged


# ── Keyboard button aliases ────────────────────────────────────────────────────

BUTTON_MAP = {
    "💎 زانیاریی دانسقە": fact_command,
    "ℹ️ دەربارەی ژیرا": about_command,
    "⚙️ ڕێکخستنەکان": settings_command,
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

    user_id = update.effective_user.id

    # Send thinking animation
    thinking_msg = await update.message.reply_text(THINKING_FRAMES[0])

    # Start AI task
    ai_task = asyncio.create_task(ask_zheera(text, user_id=user_id))

    # Animate dots while waiting
    frame_idx = 1
    while not ai_task.done():
        await asyncio.sleep(0.8)
        if not ai_task.done():
            try:
                await thinking_msg.edit_text(THINKING_FRAMES[frame_idx % len(THINKING_FRAMES)])
                frame_idx += 1
            except Exception:
                pass

    response = await ai_task
    logger.info("📨 User %s: %s | Response: %s chars", user_id, text[:80], len(response))

    # Replace thinking message with actual response
    try:
        await thinking_msg.edit_text(response)
    except Exception:
        await update.message.reply_text(response)


# ── Application builder ────────────────────────────────────────────────────────

def build_application(token: str) -> Application:
    """Build PTB Application in webhook mode (no polling)."""
    app = Application.builder().token(token).updater(None).build()

    app.add_handler(CommandHandler("start",    start_command))
    app.add_handler(CommandHandler("help",     help_command))
    app.add_handler(CommandHandler("about",    about_command))
    app.add_handler(CommandHandler("fact",     fact_command))
    app.add_handler(CommandHandler("ping",     ping_command))
    app.add_handler(CommandHandler("models",   models_command))
    app.add_handler(CommandHandler("settings", settings_command))
    app.add_handler(CallbackQueryHandler(settings_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return app
