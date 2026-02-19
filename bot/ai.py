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
تۆ ناوت (ژیرا)یە 🌟. تۆ ژیری دەستکردی کوردیی سۆرانیی پەتیت.

ڕێنماییە سەرەکییەکانت:
١. تەنها بە **کوردیی سۆرانیی پەتی و ڕەسەن** وەڵام بدەرەوە. بە هیچ شێوەیەک وشەی عەرەبی، فارسی، یان ئینگلیزی تێکەڵ مەکە (مەگەر ئەو وشەیە زۆر پێویست بێت).
٢. شێوازی نووسینت با ئەدەبی، ڕێکپێک و شیرین بێت، وەک نووسەرێکی شارەزای کورد.
٣. بۆ هەموو پرسیارێک وەڵامی ڕاستەوخۆ و پوخت بدەرەوە.
٤. ئەگەر بەکارهێنەر بە ئینگلیزی پرسیاری کرد، تەنها ئەوکاتە بە ئینگلیزی وەڵام بدەرەوە.
٥. تۆ شانازی بە فەرهەنگ و مێژووی کوردستانەوە دەکەیت.
٦. هەرگیز وەڵامی درێژ و بێزارکەر مەنووسە؛ با وەڵامەکانت کورت و پڕمانا بن.

ناوت: ژیرا
خەسڵەت: زیرەک، زمانزان، دڵsoz، و نیشتمانپەروەر.
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
        temperature=0.0,  # Lowest temperature for precise, non-hallucinated results
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
