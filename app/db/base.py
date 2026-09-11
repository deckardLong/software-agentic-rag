# Define base class

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func
from datetime import datetime

class Base(DeclarativeBase):
    """Base class for all models"""
    pass

class TimestampMixin:
    """Don't repeat yourself"""
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
