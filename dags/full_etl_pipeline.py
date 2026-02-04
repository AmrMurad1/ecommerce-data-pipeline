
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys

sys.path.insert(0, '/opt/airflow/scripts')

# Import your functions
from ingest_raw import ingest_to_bronze
from cleansing import cleanse_to_silver
from build_gold_layers import (
    build_dim_date,
    build_dim_product,
    build_dim_customer,
    build_fact_sales
)

default_args = {
    'owner': 'data-engineer',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='ecommerce_full_etl_pipeline',
    description='Complete ETL: Bronze → Silver → Gold (Star Schema)',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    tags=['etl', 'ecommerce', 'full-pipeline'],
) as dag:

    # BRONZE LAYER
    ingest_task = PythonOperator(
        task_id='bronze_ingest_raw_data',
        python_callable=ingest_to_bronze,
        doc_md="""
        ## Bronze Layer: Ingest Raw Data
        - **Reads:** `Online Retail.xlsx`
        - **Writes:** `raw_sales` table
        - **Rows:** ~541,909
        - No transformations, just raw ingestion
        """
    )

    # SILVER LAYER
    cleanse_task = PythonOperator(
        task_id='silver_cleanse_data',
        python_callable=cleanse_to_silver,
        doc_md="""
        ## Silver Layer: Data Cleansing
        - **Reads:** `raw_sales`
        - **Writes:** `silver_cleaned_sales`
        - **Rows:** ~392,692
        - Removes: nulls, negatives, duplicates
        - Adds: `TotalAmount` column
        """
    )

    # GOLD LAYER: DIMENSIONS
    build_dim_date_task = PythonOperator(
        task_id='gold_build_dim_date',
        python_callable=build_dim_date,
        doc_md="""
        ## Gold Layer: dim_date
        - **Rows:** 1,096 dates (2010-2012)
        - **Columns:** year, month, quarter, day_of_week, is_weekend
        """
    )

    build_dim_product_task = PythonOperator(
        task_id='gold_build_dim_product',
        python_callable=build_dim_product,
        doc_md="""
        ## Gold Layer: dim_product
        - **Rows:** ~3,665 products
        - **Columns:** stock_code, description
        """
    )

    build_dim_customer_task = PythonOperator(
        task_id='gold_build_dim_customer',
        python_callable=build_dim_customer,
        doc_md="""
        ## Gold Layer: dim_customer
        - **Rows:** ~4,338 customers
        - **Columns:** customer_id, first/last purchase, total purchases, revenue
        """
    )

    # GOLD LAYER: FACT TABLE
    build_fact_sales_task = PythonOperator(
        task_id='gold_build_fact_sales',
        python_callable=build_fact_sales,
        doc_md="""
        ## Gold Layer: fact_sales
        - **Rows:** ~392,692 sales transactions
        - **Links:** dim_date, dim_product, dim_customer
        - **Measures:** quantity, unit_price, total_amount
        """
    )

   
    ingest_task >> cleanse_task >> [
        build_dim_date_task,
        build_dim_product_task,
        build_dim_customer_task
    ] >> build_fact_sales_task