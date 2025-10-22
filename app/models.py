# app/models.py
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text
from sqlalchemy.types import JSON
from .database import Base
import datetime

class AnalyzedString(Base):
    __tablename__ = "strings"
    id = Column(String, primary_key=True, index=True)  # sha256 hash
    value = Column(Text, unique=True, nullable=False)
    length = Column(Integer, nullable=False)
    is_palindrome = Column(Boolean, nullable=False)
    unique_characters = Column(Integer, nullable=False)
    word_count = Column(Integer, nullable=False)
    sha256_hash = Column(String, nullable=False, unique=True, index=True)
    character_frequency_map = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.now(), onupdate=datetime.datetime.now(datetime.timezone.utc))