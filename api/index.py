"""
ZHEERA — Vercel Entry Point (api/index.py)
FastAPI + python-telegram-bot v20+ webhook handler.

Environment variables (set in Vercel dashboard):
  BOT_TOKEN    — Telegram bot token
  WEBHOOK_URL  — https://zheera.vercel.app  (hardcoded as fallback)
  GEMINI_API_KEY — Google Gemini API key
"""

import os
import sys
import json
import logging
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import httpx
from fastapi import FastAPI, Request, Response
from telegram import Update
from bot.handlers import build_application

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s — %(message)s",
)
logger = logging.getLogger("zheera")

# ── Config ────────────────────────────────────────────────────────────────────
BOT_TOKEN: str = os.environ.get(
    "BOT_TOKEN", "8525301353:AAH5LjWolYzJUBO3K7r4181OIHhs_UoDzXE"
)
WEBHOOK_URL: str = os.environ.get(
    "WEBHOOK_URL", "https://zheera.vercel.app"
).rstrip("/")
WEBHOOK_PATH: str = f"/webhook/{BOT_TOKEN}"
FULL_WEBHOOK_URL: str = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
TG_API: str = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ── PTB Application ───────────────────────────────────────────────────────────
ptb_app = build_application(BOT_TOKEN)
_ptb_initialized = False


async def ensure_initialized() -> None:
    """Initialize PTB once per cold start."""
    global _ptb_initialized
    if not _ptb_initialized:
        await ptb_app.initialize()
        _ptb_initialized = True
        logger.info("✅ PTB app initialized")


# ── FastAPI ───────────────────────────────────────────────────────────────────
app = FastAPI(
    title="ZHEERA Bot",
    description="Kurdish Intelligent Telegram Bot — ژیرا",
    version="2.0.0",
)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "bot": "ZHEERA — Kurdish Intelligent Character 🌟",
        "status": "running",
        "webhook": FULL_WEBHOOK_URL,
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/set-webhook")
async def set_webhook():
    """
    Register the Telegram webhook using a direct httpx call.
    Visit this URL once after every deployment.
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Set the webhook
            set_resp = await client.post(
                f"{TG_API}/setWebhook",
                json={
                    "url": FULL_WEBHOOK_URL,
                    "drop_pending_updates": True,
                    "allowed_updates": ["message", "callback_query"],
                },
            )
            set_data = set_resp.json()
            logger.info("setWebhook response: %s", set_data)

            # Confirm
            info_resp = await client.get(f"{TG_API}/getWebhookInfo")
            info_data = info_resp.json()
            logger.info("getWebhookInfo: %s", info_data)

        registered_url = info_data.get("result", {}).get("url", "")
        return {
            "set_result": set_data,
            "webhook_url": registered_url,
            "target": FULL_WEBHOOK_URL,
            "success": registered_url == FULL_WEBHOOK_URL,
            "message": (
                "✅ Webhook registered! Open Telegram and send /start to ZHEERA 🌟"
                if registered_url == FULL_WEBHOOK_URL
                else "⚠️ Webhook set but URL mismatch — check logs"
            ),
        }
    except Exception as exc:
        logger.error("❌ Webhook registration failed: %s", exc)
        return {"error": str(exc), "target": FULL_WEBHOOK_URL}


@app.get("/webhook-info")
async def webhook_info():
    """Check current webhook status."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{TG_API}/getWebhookInfo")
            return resp.json()
    except Exception as exc:
        return {"error": str(exc)}


@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request) -> Response:
    """
    Telegram POSTs every update here.
    We process it fully before returning 200 (Telegram waits up to 60s).
    """
    try:
        body = await request.json()
    except Exception as exc:
        logger.error("Bad JSON body: %s", exc)
        return Response(content="bad request", status_code=200)

    try:
        await ensure_initialized()
        update = Update.de_json(data=body, bot=ptb_app.bot)
        logger.info(
            "📨 Update #%s from chat %s",
            update.update_id,
            update.effective_chat.id if update.effective_chat else "?",
        )
        # Await fully — Gemini is fast enough (< 5s) and Telegram waits 60s
        await ptb_app.process_update(update)
        logger.info("✅ Update #%s processed", update.update_id)
    except Exception as exc:
        logger.error("Error processing update: %s", exc, exc_info=True)

    # Always return 200 so Telegram doesn't retry
    return Response(content="ok", status_code=200)


# ── Local dev ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.index:app", host="0.0.0.0", port=8000, reload=True)
