#!/bin/bash
# Database initialization script with environment variable support

set -e

# Use environment variables with defaults
DB_USER="${DB_USER:-airflow_user}"
DB_PASSWORD="${DB_PASSWORD:-airflow}"
DB_NAME="${DB_NAME:-ecommerce}"

echo "Creating database user and permissions..."
echo "  - User: $DB_USER"
echo "  - Database: $DB_NAME"

# Create the SQL dynamically
psql -v ON_ERROR_STOP=1 <<EOF
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
CREATE DATABASE $DB_NAME;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Switch to ecommerce database and grant schema permissions
\c $DB_NAME

GRANT ALL ON SCHEMA public TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;

-- Create initial tables
CREATE TABLE IF NOT EXISTS raw_sales (
    id SERIAL PRIMARY KEY,
    order_date DATE,
    product_id INT,
    quantity INT,
    price DECIMAL(10, 2),
    customer_id INT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS silver_cleaned_sales (
    id SERIAL PRIMARY KEY,
    order_date DATE,
    product_id INT,
    quantity INT,
    price DECIMAL(10, 2),
    customer_id INT,
    total_amount DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;

EOF

echo "Database initialization completed successfully!"
