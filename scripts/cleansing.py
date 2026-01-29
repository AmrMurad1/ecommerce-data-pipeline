
import pandas as pd
from sqlalchemy import create_engine
import os
import sys

print("=" * 80)
print("Starting Silver Layer Cleansing...")
print("=" * 80)

DB_USER = os.getenv("DB_USER", "airflow_user")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ecommerce")

if not DB_PASSWORD:
    print("ERROR: DB_PASSWORD environment variable is missing!")
    sys.exit(1)

connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print("[1/5] Connecting to PostgreSQL...")
try:
    engine = create_engine(connection_string)
    with engine.connect() as conn:
        conn.execute("SELECT 1")
    print("✓ Connection successful")
except Exception as e:
    print(f"✗ ERROR connecting to DB: {e}")
    sys.exit(1)

print("[2/5] Reading from raw_sales...")
try:
    df = pd.read_sql("SELECT * FROM raw_sales", engine)
    print(f"✓ Loaded {len(df):,} rows")
except Exception as e:
    print(f"✗ ERROR reading raw_sales: {e}")
    sys.exit(1)

print("[3/5] Cleaning data...")

original_count = len(df)

# Remove negative or zero Quantity / UnitPrice
df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
print(f"   Removed {original_count - len(df):,} rows with negative/zero Quantity or UnitPrice")
original_count = len(df)

# Remove missing CustomerID
df = df.dropna(subset=['CustomerID'])
print(f"   Removed {original_count - len(df):,} rows with missing CustomerID")

# Convert InvoiceDate to datetime
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')

# Add TotalAmount column
df['TotalAmount'] = df['Quantity'] * df['UnitPrice']
print("   Added TotalAmount column")

# Remove duplicates
df = df.drop_duplicates()
print(f"   Removed {original_count - len(df):,} duplicate rows")

print(f"✓ Final cleaned rows: {len(df):,}")

# 5. Write to silver_cleaned_sales
print("[4/5] Writing to silver_cleaned_sales...")
try:
    df.to_sql(
        name='silver_cleaned_sales',
        con=engine,
        if_exists='replace',
        index=False,
        method='multi',
        chunksize=10000
    )
    
    # Verify count after write
    with engine.connect() as conn:
        count = conn.execute("SELECT COUNT(*) FROM silver_cleaned_sales").scalar()
        print(f"✓ Verified: {count:,} rows in silver_cleaned_sales")
except Exception as e:
    print(f"✗ ERROR writing to silver_cleaned_sales: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("SILVER LAYER CLEANSING COMPLETED SUCCESSFULLY!")
print("Next steps:")
print("  - Check table: SELECT COUNT(*) FROM silver_cleaned_sales;")
print("  - Sample: SELECT * FROM silver_cleaned_sales LIMIT 5;")
print("=" * 80)