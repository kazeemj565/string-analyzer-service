# # app/main.py
# from fastapi import FastAPI, HTTPException, Depends, Query
# from sqlalchemy.orm import Session
# from .database import SessionLocal, engine, Base
# from . import models, schemas, crud, utils
# from typing import Optional, List, Dict
# from datetime import datetime
# import json

# # create db tables
# Base.metadata.create_all(bind=engine)

# app = FastAPI(
#     title="String Analyzer Service - Stage 1",
#     version="1.0.0",
#     docs_url="/docs",           # Swagger UI
#     redoc_url="/redoc",         # ReDoc
#     openapi_url="/openapi.json" # Schema endpoint
# )

# @app.get("/")
# def root():
#     return {"message": "Welcome to String Analyzer API!"}

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# def model_to_response(obj: models.AnalyzedString) -> dict:
#     props = {
#         "length": obj.length,
#         "is_palindrome": obj.is_palindrome,
#         "unique_characters": obj.unique_characters,
#         "word_count": obj.word_count,
#         "sha256_hash": obj.sha256_hash,
#         "character_frequency_map": obj.character_frequency_map,
#     }
#     created_iso = obj.created_at.replace(microsecond=0).isoformat() + "Z"
#     return {
#         "id": obj.id,
#         "value": obj.value,
#         "properties": props,
#         "created_at": created_iso,
#     }

# @app.post("/strings", status_code=201, response_model=schemas.StringResponse)
# def create_string(payload: schemas.StringCreate, db: Session = Depends(get_db)):
#     if payload.value is None:
#         raise HTTPException(status_code=400, detail="Missing 'value' field")
#     if not isinstance(payload.value, str):
#         raise HTTPException(status_code=422, detail="'value' must be a string")
#     props = utils.analyze_string(payload.value)
#     existing = crud.get_by_id(db, props["sha256_hash"])
#     if existing:
#         raise HTTPException(status_code=409, detail="String already exists in the system")
#     obj = crud.create_analyzed_string(db, props["sha256_hash"], payload.value, props)
#     return model_to_response(obj)

# @app.get("/strings/{string_value}", response_model=schemas.StringResponse)
# def get_string(string_value: str, db: Session = Depends(get_db)):
#     obj = crud.get_by_value(db, string_value)
#     if not obj:
#         raise HTTPException(status_code=404, detail="String does not exist in the system")
#     return model_to_response(obj)

# @app.get("/strings")
# def list_strings(
#     is_palindrome: Optional[bool] = Query(None),
#     min_length: Optional[int] = Query(None, ge=0),
#     max_length: Optional[int] = Query(None, ge=0),
#     word_count: Optional[int] = Query(None, ge=0),
#     contains_character: Optional[str] = Query(None, min_length=1, max_length=1),
#     db: Session = Depends(get_db),
# ):
#     # validate min/max if both provided
#     if min_length is not None and max_length is not None and min_length > max_length:
#         raise HTTPException(status_code=400, detail="min_length cannot be greater than max_length")

#     filters = {}
#     if is_palindrome is not None:
#         filters["is_palindrome"] = is_palindrome
#     if min_length is not None:
#         filters["min_length"] = min_length
#     if max_length is not None:
#         filters["max_length"] = max_length
#     if word_count is not None:
#         filters["word_count"] = word_count
#     if contains_character is not None:
#         if len(contains_character) != 1:
#             raise HTTPException(status_code=400, detail="contains_character must be a single character")
#         filters["contains_character"] = contains_character.lower()

#     results = crud.list_with_filters(db, filters)
#     data = [model_to_response(r) for r in results]
#     return {"data": data, "count": len(data), "filters_applied": filters}

# @app.get("/strings/filter-by-natural-language")
# def filter_by_nl(query: str = Query(..., min_length=1), db: Session = Depends(get_db)):
#     try:
#         parsed = utils.parse_natural_language_query(query)
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))

#     # check for internal conflicts (e.g., min>max)
#     if ("min_length" in parsed) and ("max_length" in parsed) and parsed["min_length"] > parsed["max_length"]:
#         raise HTTPException(status_code=422, detail="Parsed filters conflict (min_length > max_length)")

#     results = crud.list_with_filters(db, parsed)
#     data = [model_to_response(r) for r in results]
#     return {
#         "data": data,
#         "count": len(data),
#         "interpreted_query": {
#             "original": query,
#             "parsed_filters": parsed
#         }
#     }

# @app.delete("/strings/{string_value}", status_code=204)
# def delete_string(string_value: str, db: Session = Depends(get_db)):
#     deleted = crud.delete_by_value(db, string_value)
#     if not deleted:
#         raise HTTPException(status_code=404, detail="String does not exist in the system")
#     return None


# app/main.py
from fastapi import FastAPI, HTTPException, Depends, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_422_UNPROCESSABLE_ENTITY
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from . import models, schemas, crud, utils
from typing import Optional, List, Dict
from datetime import datetime

# create db tables (if not created)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="String Analyzer Service - Stage 1",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# --- Custom handler: convert missing 'value' field -> 400, otherwise 422 ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Inspect the errors to see if 'value' field is missing.
    for err in exc.errors():
        loc = err.get("loc", [])
        err_type = err.get("type", "")
        # Accept several possible 'missing' error types
        if (("value" in loc) and
            (err_type == "value_error.missing" or err_type == "missing" or "missing" in err_type)):
            return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"detail": "Missing 'value' field"})
    # For other validation errors return 422 with details
    return JSONResponse(status_code=HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": exc.errors()})


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# def model_to_response(obj: models.AnalyzedString) -> dict:
#     props = {
#         "length": obj.length,
#         "is_palindrome": obj.is_palindrome,
#         "unique_characters": obj.unique_characters,
#         "word_count": obj.word_count,
#         "sha256_hash": obj.sha256_hash,
#         "character_frequency_map": obj.character_frequency_map,
#     }
#     created_iso = obj.created_at.replace(microsecond=0).isoformat() + "Z"
#     return {
#         "id": obj.id,
#         "value": obj.value,
#         "properties": props,
#         "created_at": created_iso,
#     }

def model_to_response(obj: models.AnalyzedString) -> dict:
    # Ensure sha256 is taken from id (primary key) to avoid AttributeError
    sha256 = getattr(obj, "id", None) or getattr(obj, "sha256_hash", None)

    props = {
        "length": obj.length,
        "is_palindrome": obj.is_palindrome,
        "unique_characters": obj.unique_characters,
        "word_count": obj.word_count,
        "sha256_hash": sha256,
        "character_frequency_map": obj.character_frequency_map,
    }

    created_iso = None
    updated_iso = None
    if getattr(obj, "created_at", None):
        created_iso = obj.created_at.replace(microsecond=0).isoformat() + "Z"
    if getattr(obj, "updated_at", None):
        updated_iso = obj.updated_at.replace(microsecond=0).isoformat() + "Z"

    response = {
        "id": sha256,
        "value": obj.value,
        "properties": props,
        "created_at": created_iso,
    }
    # include updated_at if present (schemas expect optional updated_at)
    if updated_iso:
        response["updated_at"] = updated_iso
    else:
        response["updated_at"] = None

    return response


@app.get("/")
def root():
    return {"message": "Welcome to String Analyzer API!"}


# -----------------------
# POST /strings (create/analyze)
# -----------------------
@app.post("/strings", status_code=201, response_model=schemas.StringResponse)
def create_string(payload: schemas.StringCreate, db: Session = Depends(get_db)):
    # payload validation handled by Pydantic, missing 'value' mapped to 400 by our handler above.
    if not isinstance(payload.value, str):
        # If payload exists but type is wrong
        raise HTTPException(status_code=422, detail="'value' must be a string")

    props = utils.analyze_string(payload.value)
    # Check for existing by sha256 id
    existing = crud.get_by_id(db, props["sha256_hash"])
    if existing:
        raise HTTPException(status_code=409, detail="String already exists in the system")

    obj = crud.create_analyzed_string(db, props["sha256_hash"], payload.value, props)
    return model_to_response(obj)


# -----------------------
# GET /strings/{string_value}
# -----------------------
@app.get("/strings/{string_value}", response_model=schemas.StringResponse)
def get_string(string_value: str, db: Session = Depends(get_db)):
    obj = crud.get_by_value(db, string_value)
    if not obj:
        raise HTTPException(status_code=404, detail="String does not exist in the system")
    return model_to_response(obj)


# -----------------------
# GET /strings with filters (returns wrapper as spec)
# -----------------------
@app.get("/strings")
def list_strings(
    is_palindrome: Optional[bool] = Query(None),
    min_length: Optional[int] = Query(None, ge=0),
    max_length: Optional[int] = Query(None, ge=0),
    word_count: Optional[int] = Query(None, ge=0),
    contains_character: Optional[str] = Query(None, min_length=1, max_length=1),
    db: Session = Depends(get_db),
):
    # Validate min/max length
    if min_length is not None and max_length is not None and min_length > max_length:
        raise HTTPException(status_code=400, detail="min_length cannot be greater than max_length")

    filters = {}
    if is_palindrome is not None:
        filters["is_palindrome"] = is_palindrome
    if min_length is not None:
        filters["min_length"] = min_length
    if max_length is not None:
        filters["max_length"] = max_length
    if word_count is not None:
        filters["word_count"] = word_count
    if contains_character is not None:
        if len(contains_character) != 1:
            raise HTTPException(status_code=400, detail="contains_character must be a single character")
        filters["contains_character"] = contains_character.lower()

    results = crud.list_with_filters(db, filters)
    data = [model_to_response(r) for r in results]
    return {"data": data, "count": len(data), "filters_applied": filters}


# -----------------------
# GET /strings/filter-by-natural-language?query=...
# Accept both ?query=... and ?q=...
# -----------------------
@app.get("/strings/filter-by-natural-language")
def filter_by_nl(
    query: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    # accept either ?query= or ?q=
    raw = query or q
    if not raw:
        raise HTTPException(status_code=400, detail="Missing 'query' parameter")

    try:
        parsed = utils.parse_natural_language_query(raw)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # check for internal conflicts (e.g., min>max)
    if ("min_length" in parsed) and ("max_length" in parsed) and parsed["min_length"] > parsed["max_length"]:
        raise HTTPException(status_code=422, detail="Parsed filters conflict (min_length > max_length)")

    results = crud.list_with_filters(db, parsed)
    data = [model_to_response(r) for r in results]
    return {
        "data": data,
        "count": len(data),
        "interpreted_query": {
            "original": raw,
            "parsed_filters": parsed
        }
    }


# -----------------------
# DELETE /strings/{string_value}
# Return 200 with JSON detail
# -----------------------
@app.delete("/strings/{string_value}", status_code=204)
def delete_string(string_value: str, db: Session = Depends(get_db)):
    deleted = crud.delete_by_value(db, string_value)
    if not deleted:
        raise HTTPException(status_code=404, detail="String does not exist in the system")
    # 204 No Content must return empty body
    return Response(status_code=status.HTTP_204_NO_CONTENT)



