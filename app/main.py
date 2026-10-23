from fastapi import FastAPI
from pydantic import BaseModel

from app.services.fallback_sql import generate_fallback_sql
from app.services.gemini_service import generate_sql
from app.services.sql_validator import (
    validate_sql,
    SQLValidationError,
)
from app.services.query_service import execute_query
from app.services.explanation_service import (
    generate_explanation,
    generate_fallback_explanation,
)


app = FastAPI(
    title="FinQuery API",
    description="Natural-language financial analytics backend",
    version="0.2.0",
)


class QueryRequest(BaseModel):
    question: str


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/query")
def execute_question(request: QueryRequest):

    try:
        sql = generate_sql(request.question)
    except Exception as exc:
        print(f"Gemini unavailable: {exc}")
        sql = generate_fallback_sql(request.question)

    validated_sql = validate_sql(sql)

    try:
        result = execute_query(validated_sql)
    except Exception as exc:
        print(f"DATABASE ERROR: {exc}")
        raise

    try:
        explanation = generate_explanation(
            request.question,
            result["columns"],
            result["rows"],
        )
    except Exception as exc:
        print(f"Gemini explanation unavailable: {exc}")
        explanation = generate_fallback_explanation(
            request.question,
            result["columns"],
            result["rows"],
        )

    return {
        "question": request.question,
        "sql": validated_sql,
        "result": result,
        "explanation": explanation,
    }
