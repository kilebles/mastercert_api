import re
import httpx
import logging

from openai import AsyncOpenAI
from app.core.config import config

logger = logging.getLogger(__name__)


class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=config.OPENAI_API_KEY,
            http_client=httpx.AsyncClient(),
        )
        self.system_prompt = config.SYSTEM_PROMPT

    async def generate_gpt_response(
        self,
        conversation: list[dict],
        context: str = "",
        lang: str = "en"
    ) -> str:
        try:
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

            logger.info("🔎 Using language: %s (%s)", lang, lang_verbose)
            logger.info("🧠 SYSTEM PROMPT (first 800 chars):\n%s", base_prompt[:800])

            messages = [{"role": "system", "content": base_prompt}]

            messages.extend(conversation)

            stream = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                stream=True,
                temperature=0.7
            )

            full_response = ""
            async for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    full_response += delta.content

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
