"""Pydantic-модели запросов и ответов.

TODO (M0–M4): заполнить поля по таблице моделей в SPEC.md.
"""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    ...


class DocumentCreate(BaseModel):
    ...


class DocumentOut(BaseModel):
    ...


class AskRequest(BaseModel):
    ...


class SourceOut(BaseModel):
    ...


class AskResponse(BaseModel):
    ...


class ErrorResponse(BaseModel):
    ...
