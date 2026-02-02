from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 1, 1),
}


with DAG(
    dag_id='cleanse_dag',
    description='DAG to run the cleansing script',
    default_args=default_args,
    schedule=None,
    catchup=False,
    tags=['cleanse', 'silver'],
) as dag:
    
    cleanse_task = BashOperator(
        task_id='run_cleansing_script',
        bash_command='python /opt/airflow/scripts/cleansing.py',
    )