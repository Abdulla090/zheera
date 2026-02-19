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
PRIMARY_MODEL  = "gemini-3-flash-preview"
FALLBACK_MODEL = "gemini-2.5-flash"

# ── Kurdish Sorani system prompt ───────────────────────────────────────────────
SYSTEM_PROMPT = """
تۆ ژیرایی — یاریدەرێکی زیرەکی کوردی کە بە زمانی کوردی سۆرانی قسە دەکات.

پەیامەکانت دەبێت:
- بە کوردی سۆرانی بن بە شێوەیەکی سروشتی و خۆشەویستانە
- کورت و ئامادە بن بەبێ درێژخستنی زۆر
- گەر بەکارهێنەر بە ئینگلیزی بنووسێ، وەڵامی بدەرەوە بە ئینگلیزی
- کاراکتەری کوردی هەبێت — گەرم، زیرەک، شادمان
- لەسەر موضووعەکانی کولتووری، مێژووی، و ئەدەبی کوردی زانیاری هەبێ
- ئەگەر پرسیار فەرمانێکە (start, help, fact, etc.) وەڵامی نادەی، ئەو فەرمانانە لایەنی دیکە دەیانگرنەوە

ناوت: ژیرا 🌟
خوویەکانت: گەرم، زیرەک، کوردپەرور، یاریدەری باش
"""

# ── Lazy client (initialised once per cold start) ──────────────────────────────
_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable is not set!")
        _client = genai.Client(api_key=api_key)
    return _client


async def ask_zheera(user_message: str) -> str:
    """
    Send a message to Gemini and return the response text.
    Tries PRIMARY_MODEL first; if it fails, falls back to FALLBACK_MODEL.
    """
    client = _get_client()
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.8,
        max_output_tokens=1024,
    )

    for model_name in (PRIMARY_MODEL, FALLBACK_MODEL):
        try:
            logger.info("🤖 Sending to model: %s", model_name)
            response = client.models.generate_content(
                model=model_name,
                contents=user_message,
                config=config,
            )
            text = response.text or "ببورە، وەڵامم نەبوو. تکایە دووبارە بکەرەوە. 🙏"
            logger.info("✅ Response from %s: %s chars", model_name, len(text))
            return text

        except Exception as exc:
            logger.warning(
                "⚠️  Model %s failed: %s — %s",
                model_name,
                type(exc).__name__,
                exc,
            )
            if model_name == FALLBACK_MODEL:
                # Both models failed
                logger.error("❌ All models failed.")
                return (
                    "😔 ببورە، ئێستا کێشەی تەکنیکی هەیە.\n"
                    "تکایە چەند خولەکێک چاوەڕێ بکە و دووبارە هەوڵ بدە."
                )
            logger.info("🔄 Falling back to %s ...", FALLBACK_MODEL)
            continue
