from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime


class AnalyzeProperties(BaseModel):
    length: int
    is_palindrome: bool
    unique_characters: int
    word_count: int
    sha256_hash: str
    character_frequency_map: Dict[str, int]


class StringCreate(BaseModel):
    value: str = Field(..., example="racecar")


class StringResponse(BaseModel):
    id: str
    value: str
    properties: AnalyzeProperties
    created_at: str
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
