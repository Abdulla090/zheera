"""
ZHEERA — Gemini AI Engine
Supports model selection and thinking mode toggle per user.

Specialised for Kurdish Sorani language responses.
"""

import os
import logging
from google import genai
from google.genai import types

logger = logging.getLogger("zheera.ai")

# ── Available models for user selection ────────────────────────────────────────
AVAILABLE_MODELS = {
    "gemini-2.5-flash":       "⚡ Gemini 2.5 Flash (خێرا و ژیر)",
    "gemini-2.5-pro":         "🧠 Gemini 2.5 Pro (زۆر ژیر)",
    "gemini-2.5-flash-lite":  "💨 Gemini 2.5 Flash-Lite (زۆر خێرا)",
    "gemini-2.0-flash":       "🔵 Gemini 2.0 Flash (جێگیر)",
}

DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_THINKING = True  # Thinking ON by default

# ── Per-user settings (in-memory, resets on cold start) ────────────────────────
_user_settings: dict[int, dict] = {}


def get_user_settings(user_id: int) -> dict:
    """Get or create user settings."""
    if user_id not in _user_settings:
        _user_settings[user_id] = {
            "model": DEFAULT_MODEL,
            "thinking": DEFAULT_THINKING,
        }
    return _user_settings[user_id]


def set_user_model(user_id: int, model: str) -> None:
    settings = get_user_settings(user_id)
    settings["model"] = model


def set_user_thinking(user_id: int, thinking: bool) -> None:
    settings = get_user_settings(user_id)
    settings["thinking"] = thinking


# ── Kurdish Sorani system prompt ───────────────────────────────────────────────
SYSTEM_PROMPT = """
تۆ (ژیرا)ی، یاریدەدەرێکی زیرەکی کوردیت.

ڕێنماییەکانت:
١. وەڵامەکانت بە **کوردیی سۆرانی** بنووسە.
٢. هەوڵ بدە وشەی بیانی (ئینگلیزی/عەرەبی) کەم بەکاربهێنیت، مەگەر پێویست بێت.
٣. شێوازی نووسینت با ڕێک و جوان بێت.
٤. وەڵامەکانت پوخت و بەسوود بن.
٥. ئەگەر بەکارهێنەر بە ئینگلیزی نووسی، بە ئینگلیزی وەڵام بدەرەوە.

ناوت: ژیرا
خەسڵەت: زیرەک، دڵسۆز، و کوردپەروەر.
"""

# ── Lazy client ────────────────────────────────────────────────────────────────
_client: genai.Client | None = None


def _get_client() -> genai.Client | None:
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            logger.error("❌ GEMINI_API_KEY is missing!")
            return None
        _client = genai.Client(api_key=api_key)
    return _client


# ── List available models from API ─────────────────────────────────────────────
async def list_available_models() -> str:
    """Query the API to find out which models are actually available."""
    client = _get_client()
    if not client:
        return "⚠️ API Key missing."

    try:
        model_list = []
        for m in client.models.list(config={"page_size": 100}):
            name = m.name or ""
            display = m.display_name or ""
            if "gemini" in name.lower():
                model_list.append(f"• `{name}` — {display}")

        if not model_list:
            return "⚠️ No Gemini models found."

        header = "📋 **Available Gemini Models:**\n\n"
        result = header + "\n".join(model_list)
        if len(result) > 4000:
            result = header + "\n".join(model_list[:30]) + f"\n\n... و {len(model_list) - 30} مۆدێلی دیکە"
        return result
    except Exception as e:
        logger.error("Failed to list models: %s", e)
        return f"⚠️ Error listing models: {e}"


# ── Main AI function ──────────────────────────────────────────────────────────
async def ask_zheera(user_message: str, user_id: int = 0) -> str:
    """
    Send a message to Gemini and return the response text.
    Uses the user's selected model and thinking preference.
    """
    client = _get_client()
    if not client:
        return "⚠️ کێشەیەک لە پەیوەندی بە ژیریی دەستکردەوە هەیە (API Key Missing)."

    settings = get_user_settings(user_id)
    model_name = settings["model"]
    thinking_on = settings["thinking"]

    # Build thinking config based on user preference
    # Thinking is supported on 2.5 and 3.x models
    thinking_config = None
    if model_name.startswith("gemini-2.5") or model_name.startswith("gemini-3"):
        if thinking_on:
            thinking_config = types.ThinkingConfig(thinking_budget=-1)  # Dynamic
        else:
            thinking_config = types.ThinkingConfig(thinking_budget=0)   # Off

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.7,
        max_output_tokens=1024,
        thinking_config=thinking_config,
    )

    # Try selected model first, then fallback
    fallback = "gemini-2.0-flash" if model_name != "gemini-2.0-flash" else "gemini-2.5-flash"
    models_to_try = [model_name, fallback]

    last_error = None
    for m in models_to_try:
        try:
            logger.info("🤖 [user=%s] model=%s thinking=%s", user_id, m, thinking_on)
            response = client.models.generate_content(
                model=m,
                contents=user_message,
                config=config,
            )
            text = response.text
            if not text:
                logger.warning("⚠️ Model %s returned empty text.", m)
                continue

            logger.info("✅ Response from %s: %s chars", m, len(text))
            return text

        except Exception as exc:
            logger.warning("⚠️ Model %s failed: %s — %s", m, type(exc).__name__, exc)
            last_error = exc
            # If thinking config caused the error, retry without it
            if thinking_config and m == model_name:
                config = types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.7,
                    max_output_tokens=1024,
                )
            continue

    logger.error("❌ All models failed. Last error: %s", last_error)
    return (
        "😔 ببورە، ئێستا کێشەی تەکنیکی هەیە.\n"
        "تکایە چەند خولەکێک چاوەڕێ بکە و دووبارە هەوڵ بدە."
    )
