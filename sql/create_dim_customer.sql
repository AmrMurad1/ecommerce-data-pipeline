DROP TABLE IF EXISTS dim_customer CASCADE;

CREATE TABLE dim_customer (
    customer_key        SERIAL PRIMARY KEY,
    customer_id         DOUBLE PRECISION UNIQUE NOT NULL,
    first_purchase_date DATE,
    last_purchase_date  DATE,
    total_purchases     INT,
    total_revenue       DECIMAL(10,2)
);

CREATE INDEX idx_dim_customer_customer_id ON dim_customer(customer_id);

INSERT INTO dim_customer (
    customer_id, first_purchase_date, last_purchase_date, total_purchases, total_revenue
)
SELECT 
    "CustomerID" as customer_id,
    MIN(DATE("InvoiceDate")) as first_purchase_date,
    MAX(DATE("InvoiceDate")) as last_purchase_date,
    COUNT(DISTINCT "InvoiceNo") as total_purchases,
    ROUND(SUM("TotalAmount")::numeric, 2) as total_revenue
FROM silver_cleaned_sales
WHERE "CustomerID" IS NOT NULL
GROUP BY "CustomerID"
ORDER BY "CustomerID";

SELECT COUNT(*) as total_customers FROM dim_customer;
