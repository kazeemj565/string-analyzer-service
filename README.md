# 🧠 String Analyzer Service (Stage 1 Task)

This is the **Stage 1 Backend Project** — a RESTful API that analyzes strings and stores their computed properties.  
Built with **FastAPI** and **SQLite (via SQLAlchemy)**, it provides endpoints to create, query, filter, and delete analyzed strings, including natural language query support.

---

## 🚀 Features

✅ Analyze strings and compute:
- **length** — total number of characters  
- **is_palindrome** — case-insensitive palindrome check  
- **unique_characters** — count of distinct characters  
- **word_count** — number of whitespace-separated words  
- **sha256_hash** — secure identifier for each string  
- **character_frequency_map** — frequency of each character  

✅ Endpoints:
- `POST /strings` — analyze and store a string  
- `GET /strings/{string_value}` — retrieve one string  
- `GET /strings` — list all strings with filters (palindrome, length, word count, etc.)  
- `GET /strings/filter-by-natural-language?query=...` — filter via plain English (e.g., “all single word palindromic strings”)  
- `DELETE /strings/{string_value}` — remove a string  

✅ Full error handling & consistent JSON responses  
✅ Automatic interactive docs (Swagger + ReDoc)  
✅ Includes tests, setup instructions, and deployment guide  

---

## 🧩 Tech Stack
- **Backend:** FastAPI + Python 3.10+
- **Database:** SQLite (default) or PostgreSQL (optional)
- **ORM:** SQLAlchemy  
- **Testing:** Pytest + HTTPX  
- **Hosting:** Railway / Render / Heroku / AWS (no Vercel)  

---

## ⚙️ Setup (Quick Start)
```bash
git clone https://github.com/kazeemj565/string-analyzer-service.git
cd string-analyzer-service
python -m venv venv
source venv/bin/activate    # (or .\venv\Scripts\activate on Windows)
pip install -r requirements.txt
uvicorn app.main:app --reload




