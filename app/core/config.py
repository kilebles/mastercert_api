import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    APP_HOST = os.getenv('APP_HOST')
    APP_PORT = int(os.getenv('APP_PORT'))
    APP_URL = os.getenv('APP_URL')
    
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    SYSTEM_PROMPT = os.getenv('SYSTEM_PROMPT')
    

config = Config()