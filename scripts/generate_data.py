import random
from datetime import datetime, timedelta

import psycopg
from faker import Faker


DATABASE_URL = "postgresql://localhost/finquery"

fake = Faker("en_IN")

random.seed(42)
Faker.seed(42)


CITIES = [
    "Delhi",
    "Mumbai",
    "Bangalore",
    "Hyderabad",
    "Chennai",
    "Pune",
    "Kolkata",
    "Ahmedabad",
]

MERCHANT_CATEGORIES = [
    "Food",
    "Travel",
    "Shopping",
    "Entertainment",
    "Healthcare",
    "Electronics",
    "Groceries",
    "Utilities",
]

PAYMENT_METHODS = [
    "UPI",
    "Credit Card",
    "Debit Card",
    "Net Banking",
    "Wallet",
]

STATUSES = [
    "SUCCESS",
    "SUCCESS",
    "SUCCESS",
    "SUCCESS",
    "FAILED",
    "PENDING",
]


def generate_customers(conn, count=1000):
    customers = []

    for _ in range(count):
        customers.append(
            (
                fake.name(),
                random.choice(CITIES),
                "India",
                fake.date_time_between(
                    start_date="-2y",
                    end_date="now",
                ),
            )
        )

    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO customers
                (name, city, country, created_at)
            VALUES
                (%s, %s, %s, %s)
            """,
            customers,
        )

    conn.commit()


def generate_merchants(conn, count=200):
    merchants = []

    for _ in range(count):
        category = random.choice(MERCHANT_CATEGORIES)

        merchants.append(
            (
                fake.company(),
                category,
                random.choice(CITIES),
            )
        )

    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO merchants
                (name, category, city)
            VALUES
                (%s, %s, %s)
            """,
            merchants,
        )

    conn.commit()


def generate_transactions(conn, count=50000):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM customers")
        customer_ids = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT id FROM merchants")
        merchant_ids = [row[0] for row in cur.fetchall()]

    start_date = datetime.now() - timedelta(days=365)

    transactions = []

    for _ in range(count):
        transaction_time = start_date + timedelta(
            seconds=random.randint(
                0,
                365 * 24 * 60 * 60,
            )
        )

        transactions.append(
            (
                random.choice(customer_ids),
                random.choice(merchant_ids),
                round(random.uniform(50, 50000), 2),
                "INR",
                random.choice(PAYMENT_METHODS),
                random.choice(STATUSES),
                transaction_time,
            )
        )

    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO transactions
                (
                    customer_id,
                    merchant_id,
                    amount,
                    currency,
                    payment_method,
                    status,
                    transaction_time
                )
            VALUES
                (%s, %s, %s, %s, %s, %s, %s)
            """,
            transactions,
        )

    conn.commit()


def main():
    with psycopg.connect(DATABASE_URL) as conn:
        print("Generating customers...")
        generate_customers(conn)

        print("Generating merchants...")
        generate_merchants(conn)

        print("Generating transactions...")
        generate_transactions(conn)

        print("Done!")


if __name__ == "__main__":
    main()
