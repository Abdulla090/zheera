"""
ZHEERA — Gemini AI Engine
Primary:  gemini-3-flash-preview  (Gemini 3 Flash)
Fallback: gemini-2.5-flash        (Gemini 2.5 Flash)

Specialised for Kurdish Sorani language responses.
"""

import os
import logging
from google import genai
from google.genai import types

logger = logging.getLogger("zheera.ai")

# ── Model priority list ────────────────────────────────────────────────────────
# Using the latest stable Generative AI model available (Gemini 2.5 Flash - GA June 2025)
MODELS_TO_TRY = [
    "gemini-2.5-flash",        # Latest stable release
    "gemini-2.0-flash-exp",    # Fallback only
]

# ── Kurdish Sorani system prompt ───────────────────────────────────────────────
SYSTEM_PROMPT = """
تۆ (ژیرا)ی، یاریدەدەرێکی زیرەکی کوردیت.

ڕێنماییەکانت:
١. وەڵامەکانت بە **کوردیی سۆرانی** بنووسە.
٢. هەوڵ بدە وشەی بیانی (ئینگلیزی/عەرەبی) کەم بەکاربهێنیت، مەگەر پێویست بێت.
٣. شێوازی نووسینت با ڕێک و جوان بێت.
٤. وەڵامەکانت پوخت و بەسوود بن.

ناوت: ژیرا
خەسڵەت: زیرەک، دڵsoz، و کوردپەروەر.
"""

# ── Lazy client (initialised once per cold start) ──────────────────────────────
_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        # Fallback if env var is missing/empty
        if not api_key:
            logger.error("❌ GEMINI_API_KEY is missing!")
            return None
        _client = genai.Client(api_key=api_key)
    return _client


async def list_available_models() -> str:
    """
    Query the API to find out which models are actually available to this key.
    Returns a formatted string list.
    """
    client = _get_client()
    if not client:
        return "⚠️ API Key missing."

    try:
        model_list = []
        for m in client.models.list(config={"page_size": 100}):
            name = m.name or ""
            display = m.display_name or ""
            # Only show gemini models (skip embedding, etc.)
            if "gemini" in name.lower():
                model_list.append(f"• `{name}` — {display}")

        if not model_list:
            return "⚠️ No Gemini models found."

        # Split into chunks if too long for Telegram (4096 char limit)
        header = "📋 **Available Gemini Models:**\n\n"
        result = header + "\n".join(model_list)
        if len(result) > 4000:
            result = header + "\n".join(model_list[:30]) + f"\n\n... و {len(model_list) - 30} مۆدێلی دیکە"
        return result
    except Exception as e:
        logger.error("Failed to list models: %s", e)
        return f"⚠️ Error listing models: {e}"


async def ask_zheera(user_message: str) -> str:
    """
    Send a message to Gemini and return the response text.
    Iterates through MODELS_TO_TRY until one succeeds.
    """
    client = _get_client()
    if not client:
        return "⚠️ کێشەیەک لە پەیوەندی بە ژیریی دەستکردەوە هەیە (API Key Missing)."

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.7,  # Reverted to 0.7 for better creativity/stability
        max_output_tokens=1024,
    )

    last_error = None

    for model_name in MODELS_TO_TRY:
        try:
            logger.info("🤖 Sending to model: %s", model_name)
            response = client.models.generate_content(
                model=model_name,
                contents=user_message,
                config=config,
            )
            text = response.text
            if not text:
                logger.warning("⚠️ Model %s returned empty text.", model_name)
                continue

            logger.info("✅ Response from %s: %s chars", model_name, len(text))
            return text

        except Exception as exc:
            logger.warning(
                "⚠️ Model %s failed: %s — %s",
                model_name,
                type(exc).__name__,
                exc,
            )
            last_error = exc
            continue

    # If all models failed
    logger.error("❌ All models failed. Last error: %s", last_error)
    return (
        "😔 ببورە، ئێستا کێشەی تەکنیکی هەیە.\n"
        "تکایە چەند خولەکێک چاوەڕێ بکە و دووبارە هەوڵ بدە."
    )
