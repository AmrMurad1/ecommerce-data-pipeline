import pandas as pd
from sqlalchemy import create_engine, text
import os
import sys

DB_USER = os.getenv("DB_USER", "airflow_user")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ecommerce")

if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD environment variable is required!")

connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Define the file path 
excel_file = "/opt/airflow/data/Online Retail.xlsx"

print("=" * 80)
print("Starting data ingestion script...")
print("=" * 80)

# Check if file exists
print(f"\n[1/5] Checking file path: {excel_file}")
if not os.path.exists(excel_file):
    print(f"✗ ERROR: File not found at {excel_file}")
    print("  → Make sure the file is in ./data/raw/ on your host machine")
    sys.exit(1)

print("✓ File found!")

#Read the Excel file
print(f"\n[2/5] Reading Excel file...")
try:
    df = pd.read_excel(excel_file)
    print(f"✓ Successfully read {len(df)} rows")
    print(f"   Columns: {list(df.columns)}")
except Exception as e:
    print(f"✗ ERROR reading Excel file: {e}")
    print("  → Make sure openpyxl is installed in the container")
    sys.exit(1)

# Connect to PostgreSQL
print(f"\n[3/5] Connecting to PostgreSQL...")
try:
    engine = create_engine(connection_string)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("✓ Connection successful!")
except Exception as e:
    print(f"✗ ERROR connecting to database: {e}")
    print(f"   Connection string used: {connection_string}")
    sys.exit(1)

# Load data into raw_sales table
print(f"\n[4/5] Writing data to 'raw_sales' table...")
try:
    # Redirect stderr to suppress library debug output
    from io import StringIO
    old_stderr = sys.stderr
    sys.stderr = StringIO()
    
    # Use 'replace' for testing - change to 'append' later if needed
    df.to_sql(
        name='raw_sales',
        con=engine,
        if_exists='replace',
        index=False,
        method='multi',
        chunksize=10000
    )
    
    sys.stderr = old_stderr

    # Verify insertion
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM raw_sales")).scalar()
        print(f"✓ Successfully inserted {count} rows into raw_sales")
except Exception as e:
    sys.stderr = old_stderr
    print(f"✗ ERROR during insertion: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("✓ INGESTION COMPLETED SUCCESSFULLY!")
print("Check the table with:")
print("  SELECT COUNT(*) FROM raw_sales;")
print("=" * 80)