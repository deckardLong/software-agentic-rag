# Create document model

from sqlalchemy import String, Text, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, List
from app.db.base import Base, TimestampMixin

class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    # ======= Attributions =======
    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    url: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    title: Mapped[Optional[str]] = mapped_column(Text)
    doc_version: Mapped[Optional[str]] = mapped_column(String(50))          # Python 3.12, Redis latest, ...
    page_content_hash: Mapped[str] = mapped_column(String(32), nullable=False)
    crawled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_indexed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)   # the latest that chunk & embedding insert to DB
    need_reindex: Mapped[bool] = mapped_column(Boolean, default=False)      # get True if content doesn't change after re-crawl => Need to reindex

    # ======= Relationships =======
    chunks: Mapped[List["Chunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")    # type: ignore