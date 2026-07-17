"""Base model with common columns."""
from datetime import datetime

from sqlalchemy import Column, DateTime, func

from app.core.database import Base


class TimestampMixin:
    """Mixin that adds created_at / updated_at columns."""

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
