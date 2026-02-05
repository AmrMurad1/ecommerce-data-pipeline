E-Commerce Data Pipeline
ETL pipeline that processes 540K+ e-commerce transactions into a star schema for analytics.

<img width="2923" height="937" alt="image" src="https://github.com/user-attachments/assets/87a9b215-e98d-4dfb-842e-fb9e4fbe0c1c" />

Architecture
Medallion Layers
Bronze Layer (Raw)

Source: Online Retail.xlsx
Table: raw_sales
Rows: 541,909

Silver Layer (Cleaned)

Removed nulls, negatives, duplicates
Added TotalAmount column
Table: silver_cleaned_sales
Rows: 392,692

Gold Layer (Star Schema)

dim_date - 1,096 rows
dim_product - 3,665 rows
dim_customer - 4,338 rows
fact_sales - 392,692 rows
