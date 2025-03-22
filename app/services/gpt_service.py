import httpx

from openai import AsyncOpenAI
from langdetect import detect

from app.core.config import config


class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=config.OPENAI_API_KEY,
            http_client=httpx.AsyncClient(),
        )
    
        self.system_prompt = config.SYSTEM_PROMPT

    async def generate_gpt_response(self, user_message: str, context: str = "") -> str:
        try:
            try:
                lang = detect(user_message)
            except Exception:
                lang = "unknown"

            language_instruction = "Respond in the same language as the question."
            full_prompt = f"{self.system_prompt}\n{language_instruction}"

            messages = [{"role": "system", "content": full_prompt}]

            if context:
                messages.append({"role": "user", "content": f"Контекст из базы знаний:\n{context}"})

            messages.append({"role": "user", "content": user_message})

            stream = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=True,
            )

            full_response = ""
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content

            return full_response

        except Exception as e:
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
            raise RuntimeError(f"Error while get embedding: {e}")
        

openai_service = OpenAIService()