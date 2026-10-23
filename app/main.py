from fastapi import FastAPI
from pydantic import BaseModel

from app.services.gemini_service import generate_sql
from app.services.query_service import execute_query
from app.services.sql_validator import (
    validate_sql,
    SQLValidationError,
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
    sql = generate_sql(request.question)
    
    validated_sql = validate_sql(sql)

    result = execute_query(validated_sql)

    return {
        "question": request.question,
        "sql": validated_sql,
        "result": result,
    }
