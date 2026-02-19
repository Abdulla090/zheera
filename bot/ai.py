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
    "gemini-3-flash-preview": "🔥 Gemini 3 Flash (نوێترین - Preview)",
    "gemini-2.5-pro":         "🧠 Gemini 2.5 Pro (زۆر ژیر)",
    "gemini-2.5-flash-lite":  "💨 Gemini 2.5 Flash-Lite (زۆر خێرا)",
    "gemini-2.0-flash":       "🔵 Gemini 2.0 Flash (جێگیر)",
}

DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_THINKING = True

# ── Per-user settings & history (in-memory) ───────────────────────────────────
_user_settings: dict[int, dict] = {}
_user_history: dict[int, list] = {}  # {user_id: [{"role": "user", "parts": [...]}, ...]}


def get_user_settings(user_id: int) -> dict:
    """Get or create user settings."""
    if user_id not in _user_settings:
        _user_settings[user_id] = {
            "model": DEFAULT_MODEL,
            "thinking": DEFAULT_THINKING,
        }
    return _user_settings[user_id]


def get_user_history(user_id: int) -> list:
    """Get chat history for a user."""
    if user_id not in _user_history:
        _user_history[user_id] = []
    return _user_history[user_id]


def append_to_history(user_id: int, role: str, text: str) -> None:
    """Add a message to history and keep it within limits."""
    history = get_user_history(user_id)
    # Correct format for google-genai SDK: parts is a list of dicts with text
    history.append({"role": role, "parts": [{"text": text}]})
    
    # Keep last 30 messages to avoid indefinite growth
    if len(history) > 30:
        _user_history[user_id] = history[-30:]


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
    Send a message to Gemini with conversation history.
    """
    client = _get_client()
    if not client:
        return "⚠️ کێشەیەک لە پەیوەندی بە ژیریی دەستکردەوە هەیە (API Key Missing)."

    settings = get_user_settings(user_id)
    model_name = settings["model"]
    thinking_on = settings["thinking"]

    # Build thinking config
    thinking_config = None
    if model_name.startswith("gemini-2.5") or model_name.startswith("gemini-3"):
        if thinking_on:
            thinking_config = types.ThinkingConfig(thinking_budget=-1)  # Dynamic
        else:
            thinking_config = types.ThinkingConfig(thinking_budget=0)   # Off

    base_config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.7,
        max_output_tokens=1024,
    )
    
    # Config with thinking
    active_config = base_config
    if thinking_config:
        active_config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.7,
            max_output_tokens=1024,
            thinking_config=thinking_config,
        )

    # Prepare chat contents: History + Current Message
    history = get_user_history(user_id).copy()
    current_msg_obj = {"role": "user", "parts": [{"text": user_message}]}
    
    # Attempt 1: Full history
    contents = history + [current_msg_obj]

    # Try selected model first, then fallback
    fallback = "gemini-2.0-flash" if "gemini-2.0" not in model_name else "gemini-2.5-flash"
    models_to_try = [model_name, fallback]

    last_error = None
    
    for m in models_to_try:
        try:
            logger.info("🤖 [user=%s] model=%s thinking=%s history_len=%d", 
                        user_id, m, thinking_on, len(history))
            
            response = client.models.generate_content(
                model=m,
                contents=contents,
                config=active_config,
            )
            text = response.text
            if not text:
                logger.warning("⚠️ Model %s returned empty text.", m)
                continue

            # Success! Update history
            append_to_history(user_id, "user", user_message)
            append_to_history(user_id, "model", text)

            logger.info("✅ Response from %s: %s chars", m, len(text))
            return text

        except Exception as exc:
            logger.warning("⚠️ Model %s failed (Attempt 1): %s — %s", m, type(exc).__name__, exc)
            last_error = exc
            
            # ATTEMPT 2: Retry WITHOUT history (maybe history is corrupt/too long)
            # This is critical to prevent permanent breakage for a user
            try:
                logger.info("🔄 Retrying %s with NO HISTORY...", m)
                response = client.models.generate_content(
                    model=m,
                    contents=[current_msg_obj], # Just current message
                    config=active_config,
                )
                text = response.text
                if text:
                    # If this worked, our history was bad. Clear it.
                    _user_history[user_id] = [] 
                    append_to_history(user_id, "user", user_message)
                    append_to_history(user_id, "model", text)
                    logger.info("✅ Recovered %s with empty history.", m)
                    return text
            except Exception as exc2:
                logger.warning("⚠️ Model %s failed (Attempt 2 - No History): %s", m, exc2)
            
            # ATTEMPT 3: Retry with NO thinking config (if enabled)
            # Some models don't support it, or specific values
            if thinking_config:
                try:
                    logger.info("🔄 Retrying %s with NO THINKING...", m)
                    response = client.models.generate_content(
                        model=m,
                        contents=[current_msg_obj],
                        config=base_config, # Use config without thinking
                    )
                    text = response.text
                    if text:
                        _user_history[user_id] = []
                        append_to_history(user_id, "user", user_message)
                        append_to_history(user_id, "model", text)
                        logger.info("✅ Recovered %s with no thinking/history.", m)
                        return text
                except Exception as exc3:
                     logger.warning("⚠️ Model %s failed (Attempt 3 - No Thinking): %s", m, exc3)

            continue

    logger.error("❌ All models failed. Last error: %s", last_error)
    return (
        "😔 ببورە، ئێستا کێشەی تەکنیکی هەیە.\n"
        "تکایە چەند خولەکێک چاوەڕێ بکە و دووبارە هەوڵ بدە."
    )
