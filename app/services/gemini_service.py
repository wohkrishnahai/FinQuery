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
You are a PostgreSQL expert.

Convert the user's question into a single SQL SELECT query.

Database schema:

customers(
    id,
    name,
    city,
    country,
    created_at
)

merchants(
    id,
    name,
    category,
    city
)

transactions(
    id,
    customer_id,
    merchant_id,
    amount,
    currency,
    payment_method,
    status,
    transaction_time
)

Rules:

1. Return ONLY SQL.
2. Only SELECT queries are allowed.
3. Do not use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, or TRUNCATE.
4. Only use the tables provided above.
5. Use PostgreSQL syntax.
6. Do not wrap the SQL in markdown code fences.

User question:

{question}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    return response.text.strip()
