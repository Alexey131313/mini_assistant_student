"""Настройки приложения.

Заполнить по SPEC.md (веха M1): набор полей, чтение из .env/окружения,
превращение пустой строки в None для необязательного поля.
"""
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from logging_setup import setup_logging

class Settings(BaseSettings):
    """TODO: объявить поля настроек (список — в SPEC.md)."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    database_url: str = "postgresql+psycopg://mini:mini@localhost:5432/mini_assistant"
    test_database_url: str | None = None
    llm_base_url: str = "http://localhost:8000/v1"
    llm_model: str = "qwen2.5-1.5b-instruct"
    llm_api_key: str = "dummy"
    llm_timeout: float = 60.0
    embed_backend: Literal["fake", "sentence-transformers"] = "fake"
    embed_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 3
    log_level: str = "INFO"

    @field_validator("test_database_url", mode="before")
    @classmethod
    def none_test_database_url(cls, value: str | None) -> str | None:
        """Преобразовать пустую строку в None для необязательного поля."""
        if value is None or not value.strip():
            return None
        return value


class Config:
    """TODO: хранить настройки и логгер, уметь останавливать логирование."""
    __instance = None
    _settings = None
    _logger = None

    def __new__(cls, settings: Settings):
        if cls.__instance is None:
            instance = super().__new__(cls)
            instance._settings = settings
            instance._logger = None
            cls.__instance = instance
        return cls.__instance
    
    '''def __del__(self):
        Config.__instance = None'''

    def start_logging(self) -> None:
        if self._logger is None:
            self._logger = setup_logging(self._settings.log_level)

    def stop_logging(self) -> None:
        if self._logger is not None:
            for handler in self._logger.handlers[:]:
                handler.close()
                self._logger.removeHandler(handler)
            self._logger = None


def get_config() -> Config:
    """TODO: вернуть единственный экземпляр Config."""
    return Config(Settings())


def reset_config() -> None:
    """TODO: сбросить singleton (нужно тестам)."""
    Config.__del__()
