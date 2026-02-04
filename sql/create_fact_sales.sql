DROP TABLE IF EXISTS fact_sales CASCADE;

CREATE TABLE fact_sales (
    sale_key        SERIAL PRIMARY KEY,
    invoice_no      VARCHAR(50) NOT NULL,
    date_key        INT NOT NULL,
    product_key     INT NOT NULL,
    customer_key    INT NOT NULL,
    quantity        INT NOT NULL,
    unit_price      DECIMAL(10,2) NOT NULL,
    total_amount    DECIMAL(10,2) NOT NULL,
    invoice_date    TIMESTAMP NOT NULL,
    
    CONSTRAINT fk_date FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    CONSTRAINT fk_product FOREIGN KEY (product_key) REFERENCES dim_product(product_key),
    CONSTRAINT fk_customer FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key)
);

CREATE INDEX idx_fact_sales_date_key ON fact_sales(date_key);
CREATE INDEX idx_fact_sales_product_key ON fact_sales(product_key);
CREATE INDEX idx_fact_sales_customer_key ON fact_sales(customer_key);
CREATE INDEX idx_fact_sales_invoice_no ON fact_sales(invoice_no);

INSERT INTO fact_sales (
    invoice_no, date_key, product_key, customer_key, quantity, unit_price, total_amount, invoice_date
)
SELECT 
    s."InvoiceNo" as invoice_no,
    d.date_key,
    p.product_key,
    c.customer_key,
    s."Quantity" as quantity,
    s."UnitPrice" as unit_price,
    s."TotalAmount" as total_amount,
    s."InvoiceDate" as invoice_date
FROM silver_cleaned_sales s
INNER JOIN dim_date d ON DATE(s."InvoiceDate") = d.full_date
INNER JOIN dim_product p ON s."StockCode" = p.stock_code
INNER JOIN dim_customer c ON s."CustomerID" = c.customer_id;

SELECT COUNT(*) as total_sales FROM fact_sales;
