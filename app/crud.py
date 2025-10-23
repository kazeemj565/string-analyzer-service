from sqlalchemy.orm import Session
from . import models
from typing import List, Dict


def get_by_id(db: Session, string_id: str):
    """Fetch an analyzed string by SHA256 hash (id)."""
    return db.query(models.AnalyzedString).filter(models.AnalyzedString.id == string_id).first()


def get_by_value(db: Session, value: str):
    """Fetch an analyzed string by its text value."""
    return db.query(models.AnalyzedString).filter(models.AnalyzedString.value == value).first()


def create_analyzed_string(db: Session, string_id: str, value: str, props: Dict):
    """Insert a new analyzed string record."""
    obj = models.AnalyzedString(
        id=string_id,
        sha256_hash=string_id,
        value=value,
        length=props["length"],
        is_palindrome=props["is_palindrome"],
        unique_characters=props["unique_characters"],
        word_count=props["word_count"],
        character_frequency_map=props["character_frequency_map"],
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def list_with_filters(db: Session, filters: Dict) -> List[models.AnalyzedString]:
    """List strings based on applied filters."""
    query = db.query(models.AnalyzedString)

    if "is_palindrome" in filters:
        query = query.filter(models.AnalyzedString.is_palindrome == filters["is_palindrome"])

    if "min_length" in filters:
        query = query.filter(models.AnalyzedString.length >= filters["min_length"])

    if "max_length" in filters:
        query = query.filter(models.AnalyzedString.length <= filters["max_length"])

    if "word_count" in filters:
        query = query.filter(models.AnalyzedString.word_count == filters["word_count"])

    if "contains_character" in filters:
        char = filters["contains_character"].lower()
        query = query.filter(models.AnalyzedString.value.ilike(f"%{char}%"))

    return query.all()


def delete_by_value(db: Session, value: str) -> bool:
    """Delete a record by its text value."""
    obj = get_by_value(db, value)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True






