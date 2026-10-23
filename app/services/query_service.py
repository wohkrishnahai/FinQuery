from decimal import Decimal
from datetime import date, datetime

from app.db.connection import get_connection


def serialize_value(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if isinstance(value, Decimal):
        return float(value)

    return value


def execute_query(sql: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SET statement_timeout = '5000'")
            cur.execute(sql)

            columns = [description.name for description in cur.description]
            rows = cur.fetchall()

            return {
                "columns": columns,
                "rows": [
                    [serialize_value(value) for value in row]
                    for row in rows
                ],
            }
