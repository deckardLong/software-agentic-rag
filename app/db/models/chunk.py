# Create chunk model

from sqlalchemy import String, Text, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from typing import Optional
from app.db.base import Base, TimestampMixin
from app.config import config

class Chunk(Base, TimestampMixin):
    __tablename__ = "chunks"

    # ======= Attributions =======
    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(Text)
    section_heading: Mapped[Optional[str]] = mapped_column(Text)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[Optional[int]] = mapped_column(Integer)
    embedding: Mapped[list] = mapped_column(Vector(config.embedding.dimension))
    content_hash: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)

    # ======= Relationships =======
    document: Mapped["Document"] = relationship(back_populates="chunks") # type: ignore