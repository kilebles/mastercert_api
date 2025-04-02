import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    APP_HOST = os.getenv('APP_HOST')
    APP_PORT = int(os.getenv('APP_PORT'))
    APP_URL = os.getenv('APP_URL')
    
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    SYSTEM_PROMPT = os.getenv('SYSTEM_PROMPT')
    
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASS = os.getenv('DB_PASS')
    
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = os.getenv('REDIS_PORT')
    
    EMAIL_ADRESS = os.getenv('EMAIL_ADRESS')
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASS = os.getenv("SMTP_PASS")

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


config = Config()