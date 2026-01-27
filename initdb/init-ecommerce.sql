CREATE USER airflow_user WITH PASSWORD 'amoory2003';
CREATE DATABASE ecommerce;
GRANT ALL PRIVILEGES ON DATABASE ecommerce TO airflow_user;

-- Switch to ecommerce database and grant schema permissions
\c ecommerce

GRANT ALL ON SCHEMA public TO airflow_user;
