"""
ZHEERA — Vercel Entry Point (api/index.py)
FastAPI + python-telegram-bot v20+ webhook handler.

Environment variables required (set in Vercel dashboard):
  BOT_TOKEN    — Telegram bot token
  WEBHOOK_URL  — Full public URL of this deployment (no trailing slash)
                 e.g. https://zheera.vercel.app
"""

import os
import sys
import logging
import asyncio

# Make the project root importable when running on Vercel
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI, Request, Response, HTTPException
from telegram import Update
from telegram.error import TelegramError

from bot.handlers import build_application

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s — %(message)s",
)
logger = logging.getLogger("zheera")

# ── Config ────────────────────────────────────────────────────────────────────
BOT_TOKEN: str = os.environ.get("BOT_TOKEN", "8525301353:AAH5LjWolYzJUBO3K7r4181OIHhs_UoDzXE")
WEBHOOK_URL: str = os.environ.get("WEBHOOK_URL", "").rstrip("/")
WEBHOOK_PATH: str = f"/webhook/{BOT_TOKEN}"

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is not set!")

# ── PTB Application (module-level singleton) ──────────────────────────────────
ptb_app = build_application(BOT_TOKEN)

# ── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="ZHEERA Bot",
    description="Kurdish Intelligent Telegram Bot — ژیرا",
    version="1.0.0",
)


# ── Webhook Registration Helper ───────────────────────────────────────────────
async def register_webhook() -> None:
    """
    Called once on startup.
    Sets the Telegram webhook to <WEBHOOK_URL>/webhook/<BOT_TOKEN>.
    Skips if WEBHOOK_URL is not configured (e.g. during local dev).
    """
    if not WEBHOOK_URL:
        logger.warning("WEBHOOK_URL not set — skipping webhook registration.")
        return

    full_url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
    try:
        await ptb_app.initialize()
        await ptb_app.bot.set_webhook(
            url=full_url,
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,
        )
        info = await ptb_app.bot.get_webhook_info()
        logger.info("✅ Webhook set → %s (pending: %s)", info.url, info.pending_update_count)
    except TelegramError as exc:
        logger.error("❌ Failed to set webhook: %s", exc)


# ── Lifespan Events ───────────────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup() -> None:
    logger.info("🚀 ZHEERA starting up …")
    await register_webhook()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    logger.info("🛑 ZHEERA shutting down …")
    try:
        await ptb_app.shutdown()
    except Exception:
        pass


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    """Health check / landing."""
    return {
        "bot": "ZHEERA — Kurdish Intelligent Character 🌟",
        "status": "running",
        "webhook_path": WEBHOOK_PATH,
    }


@app.get("/health")
async def health():
    """Lightweight health probe for Vercel."""
    return {"status": "ok"}


@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request) -> Response:
    """
    Telegram sends POST requests here for every update.
    We parse the JSON body into a PTB Update object and
    process it through the application's dispatcher.
    """
    try:
        body = await request.json()
    except Exception as exc:
        logger.error("Failed to parse Telegram update body: %s", exc)
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    try:
        update = Update.de_json(data=body, bot=ptb_app.bot)
        # Process the update asynchronously without blocking the HTTP response
        asyncio.ensure_future(ptb_app.process_update(update))
    except Exception as exc:
        logger.error("Error processing update: %s", exc)
        raise HTTPException(status_code=500, detail="Update processing error")

    # Always return 200 quickly so Telegram doesn't retry
    return Response(content="ok", status_code=200)


@app.get("/set-webhook")
async def manual_set_webhook():
    """
    Manual trigger to (re-)register the webhook.
    Useful after a new deployment if auto-registration didn't fire.
    """
    if not WEBHOOK_URL:
        raise HTTPException(status_code=400, detail="WEBHOOK_URL env var not set.")

    await register_webhook()
    info = await ptb_app.bot.get_webhook_info()
    return {
        "message": "Webhook registered successfully!",
        "webhook_url": info.url,
        "pending_updates": info.pending_update_count,
    }


# ── Local Dev Entry ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.index:app", host="0.0.0.0", port=8000, reload=True)
