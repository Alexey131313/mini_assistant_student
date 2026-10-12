"""Pydantic-модели запросов и ответов.

TODO (M0–M4): заполнить поля по таблице моделей в SPEC.md.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class HealthResponse(BaseModel):
    message: str = Field(default="Healthy", description="Сообщение о состоянии сервиса")


class DocumentCreate(BaseModel):
    """Модель запроса на создание документа."""
    title: str = Field(..., min_length=1, max_length=255, description="Название документа")
    text: str = Field(..., min_length=1, description="Содержимое документа")


class DocumentOut(BaseModel):
    """Модель ответа на создание документа."""
    id: int = Field(..., description = "Уникальный ид документа")
    title: str = Field(..., min_length=1, max_length=255, description = "Название документа")
    created_at: datetime = Field(..., description = "Дата и время создания документа")
    chunks: int = Field(..., description = "Количество сегментов документа")


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Запрос пользователя")
    k: Optional[str] = Field(default=None, description="Идентификатор чата для контекста")


class SourceOut(BaseModel):
    chunk_id: int = Field(..., description="Идентификатор сегмента документа")
    document_id: int = Field(..., description="Идентификатор документа")
    score: float = Field(..., description="Оценка релевантности сегмента документа")
    text: str = Field(..., description="Содержимое сегмента документа")


class AskResponse(BaseModel):
    answer: str = Field(..., min_length = 1, description = "Ответ на запрос пользователя")
    sources: list[SourceOut] = Field(default = [], description = "Список источников, из которых получен ответ")


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Описание ошибки")
