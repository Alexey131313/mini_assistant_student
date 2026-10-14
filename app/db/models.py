"""ORM-модели.

TODO (M2): описать документ и чанк (поля и связь — в SPEC.md).
Ниже — заготовки с первичным ключом; остальные поля добавь сам.
"""

from datetime import datetime, UTC
from typing import ClassVar

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Document(Base):
    """TODO: поля title и created_at, связь с чанками."""

    __tablename__: ClassVar[str] = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default = datetime.now(UTC), nullable=False)


class Chunk(Base):
    """TODO: поля document_id, position, text, embedding и связь с документом."""

    __tablename__: ClassVar[str] = "chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list] = mapped_column(JSON, nullable=False)