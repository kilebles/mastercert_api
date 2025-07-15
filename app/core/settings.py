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

    SYSTEM_PROMPT_FILE: str = "system_prompt.txt"
    SYSTEM_PROMPT: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix=""
    )

    def __post_init_post_parse__(self):
        try:
            prompt_path = Path(self.SYSTEM_PROMPT_FILE)
            if prompt_path.is_file():
                content = prompt_path.read_text(encoding="utf-8").strip()
                object.__setattr__(self, "SYSTEM_PROMPT", content)
                logger.info("Системный промпт успешно загружен")
            else:
                logger.warning(f"Файл {self.SYSTEM_PROMPT_FILE} не найден.")
        except Exception as e:
            logger.warning(f"Ошибка при загрузке system_prompt.txt: {e}")


config = Settings()
