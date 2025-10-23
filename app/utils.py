import hashlib
from collections import Counter
import re
from datetime import datetime
from typing import Dict, Any
import json
import re

def sha256_of(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def character_frequency(value: str) -> Dict[str, int]:
    return dict(Counter(value))

def word_count(value: str) -> int:
    return len(re.findall(r"\S+", value))

def is_palindrome_case_insensitive(value: str) -> bool:
    s = value.lower()
    return s == s[::-1]

def analyze_string(value: str) -> Dict[str, Any]:
    """Return the properties dict for a string."""
    prop = {
        "length": len(value),
        "is_palindrome": is_palindrome_case_insensitive(value),
        "unique_characters": len(set(value)),
        "word_count": word_count(value),
        "sha256_hash": sha256_of(value),
        "character_frequency_map": character_frequency(value),
    }
    return prop


def parse_natural_language_query(query: str) -> dict:
    q = query.lower().strip()
    if not q:
        raise ValueError("Empty query")

    parsed = {}
    if "palindrom" in q:  
        parsed["is_palindrome"] = True

    if "single word" in q or "one word" in q or "single-word" in q:
        parsed["word_count"] = 1

    m = re.search(r"longer than (\d+)", q)
    if m:
        n = int(m.group(1))
        parsed["min_length"] = n + 1

    m = re.search(r"shorter than (\d+)", q)
    if m:
        n = int(m.group(1))
        parsed["max_length"] = max(0, n - 1)

    m = re.search(r"(?:length of|of length) (\d+)", q)
    if m:
        n = int(m.group(1))
        parsed["min_length"] = n
        parsed["max_length"] = n

    m = re.search(r"letter\s+([a-zA-Z0-9])", q)
    if m:
        parsed["contains_character"] = m.group(1)

    m = re.search(r"contain(?:s|ing)?\s+(?:the\s+)?([a-zA-Z0-9])", q)
    if m and "contains_character" not in parsed:
        parsed["contains_character"] = m.group(1)

    if "first vowel" in q:
        parsed["contains_character"] = "a"

    m = re.search(r"containing.*letter\s+([a-zA-Z0-9])", q)
    if m:
        parsed["contains_character"] = m.group(1)

    if "containing the letter" in q:
        m = re.search(r"containing the letter\s+([a-zA-Z0-9])", q)
        if m:
            parsed["contains_character"] = m.group(1)

    if not parsed:
        m = re.search(r"containing\s+([a-zA-Z0-9])", q)
        if m:
            parsed["contains_character"] = m.group(1)

    if not parsed:
        raise ValueError("Unable to parse natural language query")

    if "contains_character" in parsed and len(parsed["contains_character"]) != 1:
        raise ValueError("contains_character must be a single character")

    if "contains_character" in parsed:
        parsed["contains_character"] = parsed["contains_character"].lower()

    if ("min_length" in parsed) and ("max_length" in parsed):
        if parsed["min_length"] > parsed["max_length"]:
            raise ValueError("Conflicting length filters parsed (min > max)")

    return parsed
