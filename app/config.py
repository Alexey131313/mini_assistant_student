"""Настройки приложения.

Заполнить по SPEC.md (веха M1): набор полей, чтение из .env/окружения,
превращение пустой строки в None для необязательного поля.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """TODO: объявить поля настроек (список — в SPEC.md)."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class Config:
    """TODO: хранить настройки и логгер, уметь останавливать логирование."""


def get_config() -> Config:
    """TODO: вернуть единственный экземпляр Config."""
    raise NotImplementedError


def reset_config() -> None:
    """TODO: сбросить singleton (нужно тестам)."""
    raise NotImplementedError
