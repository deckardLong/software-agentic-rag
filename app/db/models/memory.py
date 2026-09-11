# Create memory models

from sqlalchemy import String, Text, Integer, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from datetime import datetime
from typing import Optional
from app.db.base import Base, TimestampMixin
from app.config import config

class ConversationShortTerm(Base, TimestampMixin):
    __tablename__ = "conversation_short_term"

    # ======= Attributions =======
    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    trace_id: Mapped[str] = mapped_column(String(50), nullable=False)
    turn_index: Mapped[int] = mapped_column(Integer, nullable=False)
    user_query: Mapped[str] = mapped_column(Text, nullable=False)
    final_answer: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

class ConversationLongTerm(Base, TimestampMixin):
    __tablename__ = "conversation_long_term"

    # ======= Attributions =======
    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    topic_summary: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list] = mapped_column(Vector(config.embedding.dimension))
    importance_score: Mapped[Optional[float]] = mapped_column(Float)    # score for long term save
    source_trace_id: Mapped[Optional[str]] = mapped_column(String(50))  # original trace_id 