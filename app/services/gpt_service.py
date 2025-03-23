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

    async def generate_gpt_response(self, user_message: str, context: str = "") -> str:
        try:
            user_message_clean = user_message.strip().lower()

            
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
            full_prompt = f"{self.system_prompt}\n\n{language_instruction}"

            messages = [
                {"role": "system", "content": full_prompt},
            ]

            if context:
                messages.append({"role": "user", "content": f"Контекст из базы знаний:\n{context}"})

            messages.append({"role": "user", "content": user_message})

            stream = await self.client.chat.completions.create(
                model="gpt-4o",
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
