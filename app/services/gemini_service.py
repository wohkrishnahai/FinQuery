import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")


client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.6-flash"


def generate_sql(question: str) -> str:
    prompt = f"""
You are a PostgreSQL SQL generation assistant.

Your job is to convert a user's natural-language question
into a PostgreSQL SQL query.

Database schema:

TABLE customers (
    id BIGINT PRIMARY KEY,
    name VARCHAR(100),
    city VARCHAR(100),
    country VARCHAR(100),
    created_at TIMESTAMP
);

TABLE merchants (
    id BIGINT PRIMARY KEY,
    name VARCHAR(150),
    category VARCHAR(100),
    city VARCHAR(100)
);

TABLE transactions (
    id BIGINT PRIMARY KEY,
    customer_id BIGINT,
    merchant_id BIGINT,
    amount NUMERIC(12,2),
    currency CHAR(3),
    payment_method VARCHAR(30),
    status VARCHAR(20),
    transaction_time TIMESTAMP
);

Relationships:

transactions.customer_id → customers.id
transactions.merchant_id → merchants.id

Important rules:

1. Generate PostgreSQL SQL.
2. Generate only one SQL query.
3. Generate only SELECT queries.
4. Never generate INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, or CREATE.
5. Use only the tables and columns provided above.
6. Do not invent columns.
7. Return ONLY the SQL query.
8. Do not use markdown code fences.
9. For questions asking for a list of results, use LIMIT 20 unless the user explicitly requests another limit.

User question:

{question}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    return response.text.strip()
