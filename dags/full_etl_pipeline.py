"""
Complete ETL Pipeline: Bronze → Silver → Gold
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator

default_args = {
    'owner': 'data-engineer',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='ecommerce_full_etl_pipeline',
    description='Complete ETL Pipeline: Bronze → Silver → Gold',
    default_args=default_args,
    schedule=None,  # Changed from schedule_interval
    catchup=False,
    tags=['etl', 'ecommerce', 'full-pipeline'],
) as dag:

    ingest = BashOperator(
        task_id='bronze_ingest',
        bash_command='python /opt/airflow/scripts/ingest_raw.py',
    )

    cleanse = BashOperator(
        task_id='silver_cleanse',
        bash_command='python /opt/airflow/scripts/cleansing.py',
    )

    gold = BashOperator(
        task_id='gold_build',
        bash_command='python /opt/airflow/scripts/serving.py',
    )

    ingest >> cleanse >> gold
