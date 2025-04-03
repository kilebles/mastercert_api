import re
import httpx
import logging

from langdetect import detect
from openai import AsyncOpenAI

from app.core.config import config

logger = logging.getLogger(__name__)


def detect_language(text: str) -> str:
    text_clean = text.strip().lower()

    known_greetings = {
        "hi": "en", "hello": "en", "hey": "en", "yo": "en", "helo": "en",
        "прив": "ru", "ку": "ru", "привет": "ru", "здравствуй": "ru", "здравствуйте": "ru",
    }

    if text_clean in known_greetings:
        return known_greetings[text_clean]

    if re.search(r"[а-яё]", text_clean, re.IGNORECASE):
        return "ru"
    
    if re.search(r"[ґєії]", text_clean, re.IGNORECASE):
        return "uk"

    try:
        detected = detect(text_clean)
        detected = detected.split("-")[0].lower()
    except Exception:
        detected = "unknown"

    if detected == "unknown" or len(text_clean) <= 3:
        if re.search(r"[а-яё]", text_clean, re.IGNORECASE):
            return "ru"
        else:
            return "en"

    if detected in {"mk", "bg", "sr"}:
        if re.search(r"[а-яё]", text_clean, re.IGNORECASE):
            return "ru"

    return detected


class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=config.OPENAI_API_KEY,
            http_client=httpx.AsyncClient(),
        )
        self.system_prompt = config.SYSTEM_PROMPT

    async def generate_gpt_response(self, conversation: list[dict], context: str = "") -> str:
        try:
            last_user_message = ""
            for msg in reversed(conversation):
                if msg["role"] == "user":
                    text = msg["content"].strip()
                    if (
                        len(text) < 5 or
                        re.fullmatch(r"[^@]+@[^@]+\.[^@]+", text) or
                        re.fullmatch(r"\+?\d[\d\s\-\(\)]+", text)
                    ):
                        continue
                    last_user_message = text
                    break

            if not last_user_message:
                logger.warning("⚠️ No suitable user message found for language detection. Defaulting to English.")
                lang = "en"
            else:
                lang = detect_language(last_user_message)

            lang_verbose_map = {
                "ru": "Russian",
                "en": "English",
                "uk": "Ukrainian",
                "be": "Belarusian",
                "kk": "Kazakh",
                "uz": "Uzbek",
                "zh": "Chinese",
                "de": "German",
                "fr": "French",
                "es": "Spanish",
                "it": "Italian",
                "pl": "Polish",
                "ro": "Romanian",
                "bg": "Bulgarian",
                "sr": "Serbian",
                "mk": "Macedonian",
            }
            lang_verbose = lang_verbose_map.get(lang, "English")

            language_instruction = (
                f"The current user language is: {lang_verbose}.\n"
                "You must respond in the same language."
            )
            knowledge_block = (
                f"\n\nUse the following knowledge base when relevant:\n{context}"
                if context else ""
            )

            base_prompt = f"{self.system_prompt.strip()}\n\n{language_instruction}{knowledge_block}"

            logger.info("🔎 Detected language: %s (%s)", lang, lang_verbose)
            logger.info("🧠 SYSTEM PROMPT (first 800 chars):\n%s", base_prompt[:800])

            messages = [{"role": "system", "content": base_prompt}]
            for msg in conversation:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

            stream = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                stream=True,
                temperature=0.7
            )

            full_response = ""
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content

            return full_response

        except Exception as e:
            logger.exception("❌ Error during GPT response generation")
            return f"Error: {str(e)}"

    async def get_embedding(self, text: str) -> list[float]:
        try:
            response = await self.client.embeddings.create(
                input=text,
                model="text-embedding-ada-002",
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            raise RuntimeError(f"Error while get embedding: {e}")


openai_service = OpenAIService()
