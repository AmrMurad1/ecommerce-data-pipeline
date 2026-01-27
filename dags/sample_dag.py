"""
Sample DAG for testing Airflow setup
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


def hello_world():
    """Simple Python task"""
    print("Hello from Airflow DAG!")
    return "DAG executed successfully"


default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 1, 1),
}

with DAG(
    'sample_ecommerce_dag',
    default_args=default_args,
    description='Sample DAG for ecommerce pipeline',
    schedule_interval='@daily',
    catchup=False,
) as dag:
    task_hello = PythonOperator(
        task_id='hello_world',
        python_callable=hello_world,
    )

    task_date = BashOperator(
        task_id='print_date',
        bash_command='date',
    )

    task_hello >> task_date
