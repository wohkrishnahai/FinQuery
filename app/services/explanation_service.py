import os
import time

from dotenv import load_dotenv
from google import genai


load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")


client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.6-flash"


def generate_explanation(question: str, columns: list, rows: list) -> str:

    prompt = f"""
You are a financial data analyst.

A user asked:

{question}

The database returned the following result.

Columns:
{columns}

Rows:
{rows}

Explain the result briefly in 2-4 sentences.

Important rules:

1. Use ONLY the information present in the database result.
2. Do not invent numbers.
3. Do not make claims that cannot be supported by the result.
4. Do not mention SQL, Gemini, or the database.
5. Keep the explanation concise and business-friendly.
"""

    max_retries = 3

    for attempt in range(max_retries):

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )

            return response.text.strip()

        except Exception:
            if attempt == max_retries - 1:
                raise

            delay = 2 ** attempt
            time.sleep(delay)


def generate_fallback_explanation(
    question: str,
    columns: list,
    rows: list,
) -> str:

    if not rows:
        return "No matching records were found for this question."

    question_lower = question.lower()

    if "5 merchants" in question_lower:
        return (
            "The results show the five merchants with the highest "
            "total transaction revenue in the dataset."
        )

    if "transaction volume by month" in question_lower:
        return (
            "The chart shows how total transaction volume changed "
            "across the months in the dataset."
        )

    if "average transaction" in question_lower:
        return (
            "The results compare the average transaction value "
            "across the available cities."
        )

    if "failed transaction" in question_lower:
        return (
            "The result shows the percentage of transactions "
            "that failed."
        )

    if "more than 10 transactions" in question_lower:
        return (
            "The results identify customers who completed more "
            "than 10 transactions."
        )

    if "month over month" in question_lower:
        return (
            "The results show monthly revenue together with the "
            "percentage change from the previous month."
        )

    return "The query returned results from the financial transaction dataset."
