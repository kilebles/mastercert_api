import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self):
        self.APP_HOST = os.getenv("APP_HOST")
        self.APP_PORT = int(os.getenv("APP_PORT", 8000))
        self.APP_URL = os.getenv("APP_URL")

        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

        prompt_file = os.getenv("SYSTEM_PROMPT_FILE", "system_prompt.txt")
        if os.path.exists(prompt_file):
            with open(prompt_file, "r", encoding="utf-8") as f:
                self.SYSTEM_PROMPT = f.read()
        else:
            self.SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "")

        self.DB_HOST = os.getenv("DB_HOST")
        self.DB_PORT = os.getenv("DB_PORT")
        self.DB_NAME = os.getenv("DB_NAME")
        self.DB_USER = os.getenv("DB_USER")
        self.DB_PASS = os.getenv("DB_PASS")

        self.REDIS_HOST = os.getenv("REDIS_HOST")
        self.REDIS_PORT = os.getenv("REDIS_PORT")

        self.EMAIL_ADRESS = os.getenv("EMAIL_ADRESS")
        self.SMTP_USER = os.getenv("SMTP_USER")
        self.SMTP_PASS = os.getenv("SMTP_PASS")

    @property
    def DATABASE_URL(self):
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


config = Config()
