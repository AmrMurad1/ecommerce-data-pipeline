
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 1, 1),
}

# Define the DAG
with DAG(
    dag_id='ingest_only_dag',
    description='Simple DAG to run the raw data ingestion script',
    default_args=default_args,
    schedule=None,
    catchup=False,
    tags=['ingest', 'bronze'],
) as dag:
    
    # Task: Run the ingestion script
    ingest_task = BashOperator(
        task_id='run_ingestion_script',
        bash_command='python /opt/airflow/scripts/ingest_raw.py',
    )
