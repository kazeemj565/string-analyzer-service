# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

def test_create_get_delete_string():
    payload = {"value": "Abba"}
    r = client.post("/strings", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["value"] == "Abba"
    assert body["properties"]["is_palindrome"] is True
    # GET
    r2 = client.get("/strings/Abba")
    assert r2.status_code == 200
    # Delete
    r3 = client.delete("/strings/Abba")
    assert r3.status_code == 204
    # GET after delete
    r4 = client.get("/strings/Abba")
    assert r4.status_code == 404

def test_post_duplicate_conflict():
    client.post("/strings", json={"value": "duplicate-test"})
    r = client.post("/strings", json={"value": "duplicate-test"})
    assert r.status_code == 409

def test_filters_and_nl_parser():
    client.post("/strings", json={"value": "racecar"})
    client.post("/strings", json={"value": "zoo"})
    r = client.get("/strings?is_palindrome=true")
    assert r.status_code == 200
    assert isinstance(r.json()["data"], list)
    # natural language
    r2 = client.get("/strings/filter-by-natural-language", params={"query": "all single word palindromic strings"})
    assert r2.status_code == 200
    parsed = r2.json()["interpreted_query"]["parsed_filters"]
    assert parsed["word_count"] == 1
    assert parsed["is_palindrome"] == True
