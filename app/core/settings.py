from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


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

    SYSTEM_PROMPT_FILE: str = "app/system_prompt.txt"
    SYSTEM_PROMPT: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix=""
    )


def load_system_prompt(settings: Settings) -> Settings:
    try:
        prompt_path = Path(settings.SYSTEM_PROMPT_FILE)
        if prompt_path.is_file():
            settings.SYSTEM_PROMPT = prompt_path.read_text(encoding="utf-8").strip()
            logger.info("Системный промпт успешно загружен.")
        else:
            logger.warning(f"Файл {settings.SYSTEM_PROMPT_FILE} не найден.")
    except Exception as e:
        logger.warning(f"Ошибка при загрузке system_prompt.txt: {e}")
    return settings


config = load_system_prompt(Settings())
