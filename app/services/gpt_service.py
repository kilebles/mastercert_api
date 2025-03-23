import re
import httpx

from langdetect import detect
from openai import AsyncOpenAI

from app.core.config import config


class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=config.OPENAI_API_KEY,
            http_client=httpx.AsyncClient(),
        )
        self.system_prompt = config.SYSTEM_PROMPT

        self.known_greetings = {
            "hi": "en",
            "hello": "en",
            "hey": "en",
            "yo": "en",
            "helo": "en",
            "прив": "ru",
            "ку": "ru",
            "привет": "ru",
            "здравствуй": "ru",
            "здравствуйте": "ru",
        }

    async def generate_gpt_response(self, conversation: list[dict], context: str = "") -> str:
        try:
            
            last_user_message = ""
            for msg in reversed(conversation):
                if msg["role"] == "user":
                    last_user_message = msg["content"]
                    break

            user_message_clean = last_user_message.strip().lower()
            
            if user_message_clean in self.known_greetings:
                lang = self.known_greetings[user_message_clean]
            else:
                try:
                    detected = detect(user_message_clean)
                except Exception:
                    detected = "unknown"

                if detected != "unknown":
                    detected = detected.split("-")[0].lower()

                if len(user_message_clean) <= 2 or detected == "unknown":
                    
                    if re.search(r'[а-яё]', user_message_clean):
                        lang = "ru"
                    else:
                        lang = "en"
                else:
                    lang = detected

            language_instruction = f"The user is speaking in {lang}. You must respond in {lang}."
            base_prompt = f"{self.system_prompt}\n\n{language_instruction}"

            if context:
                base_prompt += f"\n\nAdditional knowledge base context:\n{context}"

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
