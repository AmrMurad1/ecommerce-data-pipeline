"""
Step 1: Import all necessary libraries
"""
import pandas as pd
from sqlalchemy import create_engine, text
import os
import sys

# Step 2: Define the database connection string
DB_USER = "airflow_user"
DB_PASSWORD = "amoory2003"
DB_HOST = "postgres"          # Docker service name (internal network)
DB_PORT = "5432"
DB_NAME = "ecommerce"

connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Step 3: Define the file path (inside the container)
excel_file = "/opt/airflow/data/Online Retail.xlsx"

print("=" * 80)
print("Starting data ingestion script...")
print("=" * 80)

# Step 4: Check if file exists
print(f"\n[1/5] Checking file path: {excel_file}")
if not os.path.exists(excel_file):
    print(f"✗ ERROR: File not found at {excel_file}")
    print("  → Make sure the file is in ./data/raw/ on your host machine")
    sys.exit(1)

print("✓ File found!")

# Step 5: Read the Excel file
print(f"\n[2/5] Reading Excel file...")
try:
    df = pd.read_excel(excel_file)
    print(f"✓ Successfully read {len(df)} rows")
    print(f"   Columns: {list(df.columns)}")
except Exception as e:
    print(f"✗ ERROR reading Excel file: {e}")
    print("  → Make sure openpyxl is installed in the container")
    sys.exit(1)

# Step 6: Connect to PostgreSQL
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

# Step 7: Load data into raw_sales table
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