DROP TABLE IF EXISTS dim_product CASCADE;

CREATE TABLE dim_product (
    product_key     SERIAL PRIMARY KEY,
    stock_code      VARCHAR(50) UNIQUE NOT NULL,
    description     TEXT
);

CREATE INDEX idx_dim_product_stock_code ON dim_product(stock_code);

INSERT INTO dim_product (stock_code, description)
SELECT 
    "StockCode" as stock_code,
    MIN("Description") as description
FROM silver_cleaned_sales
WHERE "StockCode" IS NOT NULL
GROUP BY "StockCode"
ORDER BY "StockCode";

SELECT COUNT(*) as total_products FROM dim_product;
