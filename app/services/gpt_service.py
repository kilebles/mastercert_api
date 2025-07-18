import httpx
import logging

from openai import AsyncOpenAI
from app.core.settings import config

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
        context: str = ""
    ) -> str:
        try:
            knowledge_block = f"\n\n{context}" if context else ""

            base_prompt = f"{self.system_prompt.strip()}{knowledge_block}"
            messages = [
                {"role": "system", "content": self.system_prompt.strip()},
            ]
            if context:
                messages.append({"role": "system", "content": f"Полезная информация для ответа:\n{context}"})
            messages.extend(conversation)

            logger.warning("=== SYSTEM PROMPT ===")
            logger.warning(self.system_prompt[:1000])
            if context:
                logger.warning("=== CONTEXT BLOCK ===")
                logger.warning(context[:1000])

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
                model="text-embedding-3-small",
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.exception("❌ Error generating embedding")
            raise


openai_service = OpenAIService()
