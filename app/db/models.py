"""ORM-модели.

TODO (M2): описать документ и чанк (поля и связь — в SPEC.md).
Ниже — заготовки с первичным ключом; остальные поля добавь сам.
"""

from typing import ClassVar

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Document(Base):
    """TODO: поля title и created_at, связь с чанками."""

    __tablename__: ClassVar[str] = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class Chunk(Base):
    """TODO: поля document_id, position, text, embedding и связь с документом."""

    __tablename__: ClassVar[str] = "chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
