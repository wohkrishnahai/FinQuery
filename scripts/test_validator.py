from app.services.sql_validator import (
    validate_sql,
    SQLValidationError,
)


def test_valid_query():
    sql = """
    SELECT
        m.name,
        SUM(t.amount) AS revenue
    FROM merchants m
    JOIN transactions t
        ON m.id = t.merchant_id
    GROUP BY m.name
    ORDER BY revenue DESC
    LIMIT 5;
    """

    validated = validate_sql(sql)

    print("VALID QUERY PASSED")
    print(validated)


def test_delete_blocked():
    sql = "DELETE FROM transactions;"

    try:
        validate_sql(sql)
        print("ERROR: DELETE was not blocked")
    except SQLValidationError as exc:
        print("DELETE BLOCKED")
        print(exc)


def test_drop_blocked():
    sql = "DROP TABLE transactions;"

    try:
        validate_sql(sql)
        print("ERROR: DROP was not blocked")
    except SQLValidationError as exc:
        print("DROP BLOCKED")
        print(exc)


def test_unknown_table_blocked():
    sql = "SELECT * FROM users;"

    try:
        validate_sql(sql)
        print("ERROR: unknown table was not blocked")
    except SQLValidationError as exc:
        print("UNKNOWN TABLE BLOCKED")
        print(exc)


if __name__ == "__main__":
    test_valid_query()
    print()

    test_delete_blocked()
    print()

    test_drop_blocked()
    print()

    test_unknown_table_blocked()
