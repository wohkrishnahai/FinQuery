# FinQuery: AI Financial Data Analyst

FinQuery is an AI-assisted financial analytics application that lets
users ask questions about transaction data in natural language and
receive query results, visualizations, and concise business
explanations.

The core pipeline is:

**Natural language question → SQL generation → SQL validation →
PostgreSQL → results → visualization + explanation**

The project is designed around an important principle: **LLM output is
untrusted input; PostgreSQL remains the source of truth.**

## Features

-   Ask financial analytics questions in natural language.
-   Generate PostgreSQL queries using Gemini.
-   Validate generated SQL using an AST-based validator with `sqlglot`.
-   Allow only a single `SELECT` statement against approved tables.
-   Handle CTEs correctly during table authorization.
-   Execute queries using a PostgreSQL read-only role.
-   Apply a 5-second PostgreSQL statement timeout.
-   Serialize PostgreSQL `Decimal` and datetime values into JSON-safe
    values.
-   Display results in an interactive Streamlit dashboard.
-   Generate Plotly visualizations for suitable result sets.
-   Generate concise business-friendly explanations.
-   Provide a deterministic local fallback for common demo questions
    when the external LLM is unavailable.

## Architecture

``` text
                    ┌─────────────────┐
                    │   Streamlit UI  │
                    └────────┬────────┘
                             │
                             │ POST /query
                             ▼
                    ┌─────────────────┐
                    │     FastAPI     │
                    └────────┬────────┘
                             │
                  ┌──────────┴──────────┐
                  │                     │
                  ▼                     ▼
             Gemini / fallback    SQL Validator
                  │                     │
                  │ generated SQL       │ validated SQL
                  └──────────┬──────────┘
                             ▼
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │  read-only role │
                    └────────┬────────┘
                             │
                             ▼
                       Query result
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
              Visualization      Explanation
                    │                 │
                    └────────┬────────┘
                             ▼
                       Streamlit UI
```

## Tech Stack

  Layer                    Technology
  ------------------------ ---------------
  Frontend                 Streamlit
  Backend API              FastAPI
  LLM                      Google Gemini
  Database                 PostgreSQL
  SQL parsing/validation   sqlglot
  Data handling            Pandas
  Visualization            Plotly
  Language                 Python

## Database Schema

FinQuery uses three relational tables:

### `customers`

-   `id`
-   `name`
-   `city`
-   `country`
-   `created_at`

### `merchants`

-   `id`
-   `name`
-   `category`
-   `city`

### `transactions`

-   `id`
-   `customer_id` → `customers.id`
-   `merchant_id` → `merchants.id`
-   `amount`
-   `currency`
-   `payment_method`
-   `status`
-   `transaction_time`

The generated dataset contains:

-   1,000 customers
-   200 merchants
-   50,000 transactions

The transaction data covers approximately the previous year and uses
INR-denominated synthetic financial activity.

## Example Questions

FinQuery can answer analytical questions such as:

``` text
Which 5 merchants generated the highest revenue?

Show transaction volume by month.

What is the average transaction value by city?

What percentage of transactions failed?

Show customers with more than 10 transactions.

Show month over month revenue growth.
```

The final example uses a PostgreSQL CTE and window function:

``` sql
LAG(revenue) OVER (ORDER BY month)
```

to calculate month-over-month revenue growth.

## SQL Security

LLM-generated SQL is treated as **untrusted input**.

Before execution, FinQuery validates the generated SQL using `sqlglot`:

1.  Parse the SQL into an AST.
2.  Require exactly one statement.
3.  Require the root query to be a `SELECT`.
4.  Allow only approved physical tables.
5.  Distinguish CTE aliases from physical tables.
6.  Execute the validated query using a read-only PostgreSQL role.

The database connection also uses:

``` sql
SET statement_timeout = '5000';
```

This provides defense in depth:

``` text
LLM output
    ↓
AST validation
    ↓
Read-only database permissions
    ↓
Statement timeout
    ↓
PostgreSQL
```

The application therefore does not rely on the prompt alone as a
security boundary.

## Why PostgreSQL?

The data is structured relational transaction data, and the workload
consists primarily of:

-   joins
-   aggregation
-   grouping
-   filtering
-   date-based analysis
-   window functions

PostgreSQL provides these capabilities directly without introducing the
complexity of a distributed analytics system for a dataset of this size.

## Why an LLM?

The LLM is used as a natural-language interface to the database.

It does **not** act as the source of truth or directly control the
database.

The responsibility is separated as follows:

-   **LLM:** translate natural language into SQL.
-   **Validator:** decide whether the generated SQL is allowed.
-   **PostgreSQL:** execute the query and provide authoritative results.
-   **Application:** visualize and explain those results.

## Reliability During Development

A small deterministic SQL fallback exists for common demo questions.
This allows the application to remain demonstrable when the external
Gemini service is temporarily unavailable or quota-limited.

The fallback is not intended to replace the LLM in the general case.

## Project Structure

``` text
finquery/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── ui.py
│   ├── db/
│   │   ├── __init__.py
│   │   └── connection.py
│   └── services/
│       ├── explanation_service.py
│       ├── fallback_sql.py
│       ├── gemini_service.py
│       ├── query_service.py
│       └── sql_validator.py
├── scripts/
│   ├── generate_data.py
│   ├── schema.sql
│   └── test_validator.py
├── tests/
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```

> `.env` is intentionally excluded from version control and should
> contain local credentials such as `DATABASE_URL` and `GEMINI_API_KEY`.

## Setup

### 1. Clone the repository

``` bash
git clone https://github.com/wohkrishnahai/FinQuery.git
cd finquery
```

### 2. Create and activate a virtual environment

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

``` bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

``` env
DATABASE_URL=postgresql://finquery_readonly:finquery_readonly_password@localhost/finquery
GEMINI_API_KEY=your_gemini_api_key
```

Never commit `.env` or expose the API key publicly.

### 5. Create the database

Create the PostgreSQL database and schema using the SQL in:

``` text
scripts/schema.sql
```

Then generate the synthetic dataset:

``` bash
python -m scripts.generate_data
```

### 6. Start the FastAPI backend

``` bash
uvicorn app.main:app --reload
```

The API runs at:

``` text
http://127.0.0.1:8000
```

### 7. Start the Streamlit frontend

In another terminal:

``` bash
streamlit run app/ui.py
```

Open the local Streamlit URL shown by the command.

## API

### `GET /health`

Checks whether the API is running.

### `POST /query`

Example request:

``` json
{
  "question": "Which 5 merchants generated the highest revenue?"
}
```

The response contains:

-   original question
-   validated SQL
-   result columns
-   result rows
-   business explanation

## Testing

Basic validation tests can be run with:

``` bash
python -m scripts.test_validator
```

Python compilation can be checked with:

``` bash
python -m compileall app scripts
```

The application was manually tested end-to-end through the Streamlit
interface using the six example analytical questions listed above.

## Design Decisions

### Explicit control flow instead of an agent framework

The workflow is intentionally simple and deterministic:

``` text
generate SQL → validate → execute → explain
```

An agent framework would add abstraction without solving a requirement
of this application.

### Relational database instead of a vector database

The problem involves structured transaction data rather than
unstructured document retrieval. SQL is therefore a more natural
interface than semantic vector search.

### Defense in depth

Prompt instructions alone are not considered a security mechanism. SQL
validation, database permissions, and query timeouts provide independent
safeguards.

## Limitations

-   The dataset is synthetic and relatively small.
-   The fallback SQL generator supports only a predefined set of demo
    questions.
-   The application depends on an external LLM for general
    natural-language-to-SQL generation.
-   The SQL validator enforces structural safety, but a production
    system would require additional controls such as query-cost/resource
    policies, authentication/authorization, auditing, and more
    comprehensive testing.
-   The current visualization logic is intentionally generic rather than
    domain-specific for every possible query shape.

## Future Improvements

Possible production-oriented improvements include:

-   Query result caching.
-   Better query-cost controls.
-   Authentication and authorization.
-   Audit logging.
-   More comprehensive SQL validation and test coverage.
-   Better visualization selection based on result semantics.
-   Evaluation against a larger ground-truth natural-language query set.
-   Monitoring of query latency and LLM accuracy.

## Key Engineering Takeaways

FinQuery was built around three principles:

1.  **The LLM is an interface, not the source of truth.**
2.  **Model-generated SQL must be treated as untrusted input.**
3.  **Security should be enforced in multiple layers.**
