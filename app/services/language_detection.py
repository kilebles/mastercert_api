from langdetect import detect_langs
import re

def detect_language_with_fallback(user_text: str, current_lang: str = None) -> str:
    text_clean = user_text.strip().lower()

    if len(text_clean) < 5:
        return current_lang or "en"

    try:

        langs = detect_langs(text_clean)
        best = langs[0]
        detected_lang = best.lang
        confidence = best.prob
    except Exception:
        detected_lang = "unknown"
        confidence = 0.0

    if confidence < 1:
        return current_lang or "en"

    if detected_lang in {"mk", "bg", "sr"}:
        return current_lang or "ru"

    return detected_lang