# app/crud.py
from sqlalchemy.orm import Session
from . import models
from datetime import datetime, timezone

def get_by_id(db: Session, id: str):
    return db.query(models.AnalyzedString).filter(models.AnalyzedString.id == id).first()

def get_by_value(db: Session, value: str):
    return db.query(models.AnalyzedString).filter(models.AnalyzedString.value == value).first()

def create_analyzed_string(db: Session, id: str, value: str, props: dict):
    created_at = datetime.now(timezone.utc)
    obj = models.AnalyzedString(
        id=id,
        value=value,
        length=props["length"],
        is_palindrome=props["is_palindrome"],
        unique_characters=props["unique_characters"],
        word_count=props["word_count"],
        sha256_hash=props["sha256_hash"],
        character_frequency_map=props["character_frequency_map"],
        created_at=created_at,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def delete_by_value(db: Session, value: str):
    obj = get_by_value(db, value)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True

def list_with_filters(db: Session, filters: dict):
    q = db.query(models.AnalyzedString)
    if "is_palindrome" in filters:
        q = q.filter(models.AnalyzedString.is_palindrome == filters["is_palindrome"])
    if "min_length" in filters:
        q = q.filter(models.AnalyzedString.length >= filters["min_length"])
    if "max_length" in filters:
        q = q.filter(models.AnalyzedString.length <= filters["max_length"])
    if "word_count" in filters:
        q = q.filter(models.AnalyzedString.word_count == filters["word_count"])
    if "contains_character" in filters:
        # simple substring check on value (case-insensitive)
        ch = filters["contains_character"]
        q = q.filter(models.AnalyzedString.value.ilike(f"%{ch}%"))
    results = q.all()
    return results



