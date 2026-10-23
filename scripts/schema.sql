
CREATE TABLE IF NOT EXISTS customers (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS merchants (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS transactions (
    id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers(id),
    merchant_id BIGINT NOT NULL REFERENCES merchants(id),
    amount NUMERIC(12, 2) NOT NULL CHECK (amount > 0),
    currency CHAR(3) NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    status VARCHAR(20) NOT NULL,
    transaction_time TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_transactions_customer
    ON transactions(customer_id);

CREATE INDEX IF NOT EXISTS idx_transactions_merchant
    ON transactions(merchant_id);

CREATE INDEX IF NOT EXISTS idx_transactions_time
    ON transactions(transaction_time);

CREATE INDEX IF NOT EXISTS idx_transactions_status
    ON transactions(status);
