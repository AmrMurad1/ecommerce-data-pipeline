CREATE USER airflow_user WITH PASSWORD 'amoory2003';
CREATE DATABASE ecommerce;
GRANT ALL PRIVILEGES ON DATABASE ecommerce TO airflow_user;
\c ecommerce  -- switch to ecommerce DB
GRANT ALL ON SCHEMA public TO airflow_user;