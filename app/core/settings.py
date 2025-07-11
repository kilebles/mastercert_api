from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    APP_HOST: str
    APP_PORT: int
    APP_URL: str

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DATABASE_URL: str

    REDIS_HOST: str
    REDIS_PORT: int

    OPENAI_API_KEY: str

    SYSTEM_PROMPT_FILE: str = "system_prompt.txt"
    SYSTEM_PROMPT: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix=""
    )

    def __init__(self, **data):
        super().__init__(**data)
        prompt_path = Path(self.SYSTEM_PROMPT_FILE)
        if prompt_path.exists():
            self.SYSTEM_PROMPT = prompt_path.read_text(encoding="utf-8")
        else:
            self.SYSTEM_PROMPT = ""


config = Settings()
