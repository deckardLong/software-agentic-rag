# Create log models

from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey, ARRAY, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, List
from app.db.base import Base, TimestampMixin

class QueryLog(Base, TimestampMixin):
    __tablename__ = "query_log"

    # ======= Attributions =======
    id: Mapped[int] = mapped_column(primary_key=True)
    trace_id: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), index=True)
    user_query: Mapped[str] = mapped_column(Text, nullable=False)
    route: Mapped[Optional[str]] = mapped_column(String(20))
    final_answer: Mapped[Optional[str]] = mapped_column(Text)
    input_guardrail_result: Mapped[Optional[str]] = mapped_column(String(10))
    output_guardrail_result: Mapped[Optional[str]] = mapped_column(String(10))
    grounding_grade: Mapped[Optional[str]] = mapped_column(String(10))
    total_retry_count: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer)
    llm_tokens_in: Mapped[Optional[int]] = mapped_column(Integer)
    llm_tokens_out: Mapped[Optional[int]] = mapped_column(Integer)

    # ======= Relationships =======
    retrieval_attempts: Mapped[List["RetrievalLog"]] = relationship(back_populates="query", cascade="all, delete-orphan")

class RetrievalLog(Base, TimestampMixin):
    __tablename__ = "retrieval_log"

    # ======= Attributions =======
    id: Mapped[int] = mapped_column(primary_key=True)
    trace_id: Mapped[str] = mapped_column(String(50), ForeignKey("query_log.trace_id", ondelete="CASCADE"), nullable=False, unique=True)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    rewritten_query: Mapped[Optional[str]] = mapped_column(Text)
    retrieved_chunk_ids: Mapped[Optional[List[int]]] = mapped_column(ARRAY(Integer))
    retrieval_scores: Mapped[Optional[List[float]]] = mapped_column(ARRAY(Float))
    retrieval_grade: Mapped[Optional[str]] = mapped_column(String(20))
    retrieval_grade_score: Mapped[Optional[float]] = mapped_column(Float)

    # ======= Relationships =======
    query: Mapped["QueryLog"] = relationship(back_populates="retrieval_attempts")