from datetime import datetime, timedelta

# New imports for Airflow 3.x
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator


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
    dag_id='sample_ecommerce_dag',
    default_args=default_args,
    description='Sample DAG for ecommerce pipeline',
    schedule='@daily',  # ← هنا التغيير المهم: schedule بدل schedule_interval
    catchup=False,
    tags=['ecommerce', 'sample'],
) as dag:

    task_hello = PythonOperator(
        task_id='hello_world',
        python_callable=hello_world,
    )

    task_date = BashOperator(
        task_id='print_date',
        bash_command='date',
    )

    # Task dependency
    task_hello >> task_date