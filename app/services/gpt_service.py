import httpx
from openai import AsyncOpenAI
from app.core.config import config


class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=config.OPENAI_API_KEY,
            http_client=httpx.AsyncClient(),
        )
    
        self.system_prompt = config.SYSTEM_PROMPT

    async def generate_gpt_response(self, user_message: str) -> str:
        try:
            stream = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "assistant", "content": "Привет! Я могу помочь с вопросами о Mastercert."},
                    {"role": "user", "content": user_message},
                ],
                stream=True,
            )
            
            full_response = ""
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                
            return full_response
        
        except Exception as e:
            return f"Error: {str(e)}"
        

openai_service = OpenAIService()