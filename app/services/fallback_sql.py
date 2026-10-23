def generate_fallback_sql(question: str) -> str:
    question_lower = question.lower()

    if "5 merchants" in question_lower and "highest revenue" in question_lower:
        return """
        SELECT
            m.name,
            SUM(t.amount) AS total_revenue
        FROM merchants m
        JOIN transactions t
            ON m.id = t.merchant_id
        GROUP BY m.name
        ORDER BY total_revenue DESC
        LIMIT 5;
        """

    if "transaction volume by month" in question_lower:
        return """
        SELECT
            DATE_TRUNC('month', transaction_time) AS month,
            SUM(amount) AS transaction_volume
        FROM transactions
        GROUP BY month
        ORDER BY month;
        """

    if "average transaction" in question_lower and "city" in question_lower:
        return """
        SELECT
            c.city,
            AVG(t.amount) AS average_transaction_value
        FROM customers c
        JOIN transactions t
            ON c.id = t.customer_id
        GROUP BY c.city
        ORDER BY average_transaction_value DESC;
        """

    if "failed" in question_lower and "transaction" in question_lower:
        return """
        SELECT
            COUNT(*) FILTER (WHERE status = 'failed') * 100.0
            / COUNT(*) AS failed_transaction_percentage
        FROM transactions;
        """

    if "more than 10 transactions" in question_lower:
        return """
        SELECT
            c.id,
            c.name,
            COUNT(t.id) AS transaction_count
        FROM customers c
        JOIN transactions t
            ON c.id = t.customer_id
        GROUP BY c.id, c.name
        HAVING COUNT(t.id) > 10
        ORDER BY transaction_count DESC;
        """

    if (
        "month over month" in question_lower
        or "month-over-month" in question_lower
        or "monthly growth" in question_lower
        or "revenue growth" in question_lower
    ):
        return """
        WITH monthly AS (
            SELECT
                DATE_TRUNC('month', transaction_time) AS month,
                SUM(amount) AS revenue
            FROM transactions
            GROUP BY month
        )
        SELECT
            month,
            revenue,
            LAG(revenue) OVER (ORDER BY month) AS previous_month_revenue,
            ROUND(
                (revenue - LAG(revenue) OVER (ORDER BY month))
                * 100.0
                / NULLIF(LAG(revenue) OVER (ORDER BY month), 0),
                2
            ) AS growth_percentage
        FROM monthly
        ORDER BY month;
        """

    raise ValueError(
        "Gemini is currently unavailable and this question "
        "does not have a local fallback."
    )
