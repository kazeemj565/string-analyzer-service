from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.types import JSON
from .database import Base
from datetime import datetime, timezone


class AnalyzedString(Base):
    __tablename__ = "strings"

    id = Column(String, primary_key=True, index=True)  # SHA256 hash used as ID
    value = Column(String, unique=True, nullable=False)
    length = Column(Integer, nullable=False)
    sha256_hash = Column(String, nullable=False, unique=True, index=True)
    is_palindrome = Column(Boolean, nullable=False)
    unique_characters = Column(Integer, nullable=False)
    word_count = Column(Integer, nullable=False)
    character_frequency_map = Column(JSON, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc), nullable=False)
