from app.db.connection import get_connection


def execute_query(sql: str):
    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("SET statement_timeout = '5000'")

            cur.execute(sql)

            columns = [description.name for description in cur.description]
            rows = cur.fetchall()

            return {
                "columns": columns,
                "rows": [list(row) for row in rows],
            }
