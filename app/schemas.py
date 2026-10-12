"""Pydantic-модели запросов и ответов.

TODO (M0–M4): заполнить поля по таблице моделей в SPEC.md.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class HealthResponse(BaseModel):
    status: str = Field(default="OK", description="Статус сервиса")
    version: str = Field(default="1.0.0", description="Версия сервиса")
    timestamp: datetime = Field(default_factory = datetime.utcnow)


class DocumentCreate(BaseModel):
    """Модель запроса на создание документа."""
    title: str = Field(..., min_length=1, max_length=255, description="Название документа")
    content: str = Field(..., min_length=1, description="Содержимое документа")
    metadata: Optional[dict] = Field(default=None, description="Дополнительные метаданные документа")


class DocumentOut(BaseModel):
    """Модель ответа на создание документа."""
    id: int = Field(..., description = "Уникальный ид документа")
    title: str = Field(..., min_length=1, max_length=255, description = "Название документа")
    content: str = Field(..., min_length=1, description = "Содержимое документа")
    metadata: Optional[dict] = Field(default=None, description = "Дополнительные метаданные документа")
    created_at: datetime = Field(..., description = "Дата и время создания документа")


class AskRequest(BaseModel):
    request: str = Field(..., min_length=1, description="Запрос пользователя")
    chat_id: Optional[str] = Field(default=None, description="Идентификатор чата для контекста")
    context: Optional[str] = Field(default=None, description="Контекст запроса")
    user_id: Optional[str] = Field(default=None, description="Идентификатор пользователя")


class SourceOut(BaseModel):
    doc_id: int = Field(..., description="Идентификатор документа")
    title: str= Field(..., min_length=1, max_length=255, description="Название документа")
    segment: str = Field(..., min_length=1, description="Сегмент документа, из которого получен ответ")
    score: float = Field(..., description="Оценка релевантности сегмента документа")


class AskResponse(BaseModel):
    answer: str = Field(..., min_length = 1, description = "Ответ на запрос пользователя")
    sources: list[SourceOut] = Field(default = [], description = "Список источников, из которых получен ответ")
    chat_id: Optional[str] = Field(default = None, description = "Идентификатор чата для контекста")


class ErrorResponse(BaseModel):
    code: int = Field(..., description="Код ошибки")
    error_description: str = Field(..., description="Описание ошибки")
    timmestamp: datetime = Field(default_factory = datetime.utcnow)
