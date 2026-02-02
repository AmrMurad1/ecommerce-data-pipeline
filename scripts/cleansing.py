import logging
import pandas as pd
from sqlalchemy import create_engine
import os

logger = logging.getLogger(__name__)


def cleanse_to_silver():
    """
    Read from raw_sales, clean the data, and write to silver_cleaned_sales.
    """
    logger.info("=" * 80)
    logger.info("Starting Silver Layer Cleansing...")
    logger.info("=" * 80)

    DB_USER = os.getenv("DB_USER", "airflow_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "postgres")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "ecommerce")

    if not DB_PASSWORD:
        logger.error("ERROR: DB_PASSWORD environment variable is missing!")
        raise ValueError("DB_PASSWORD environment variable is required")

    connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    logger.info("[1/5] Connecting to PostgreSQL...")
    try:
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("✓ Connection successful")
    except Exception as e:
        logger.error(f"✗ ERROR connecting to DB: {e}")
        raise

    logger.info("[2/5] Reading from raw_sales...")
    try:
        df = pd.read_sql("SELECT * FROM raw_sales", engine)
        logger.info(f"✓ Loaded {len(df):,} rows")
    except Exception as e:
        logger.error(f"✗ ERROR reading raw_sales: {e}")
        raise

    logger.info("[3/5] Cleaning data...")

    original_count = len(df)

    # Remove negative or zero Quantity / UnitPrice
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
    logger.info(f"   Removed {original_count - len(df):,} rows with negative/zero Quantity or UnitPrice")
    original_count = len(df)

    # Remove missing CustomerID
    df = df.dropna(subset=['CustomerID'])
    logger.info(f"   Removed {original_count - len(df):,} rows with missing CustomerID")

    # Convert InvoiceDate to datetime
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')

    # Add TotalAmount column
    df['TotalAmount'] = df['Quantity'] * df['UnitPrice']
    logger.info("   Added TotalAmount column")

    # Remove duplicates
    df = df.drop_duplicates()
    logger.info(f"   Removed {original_count - len(df):,} duplicate rows")

    logger.info(f"✓ Final cleaned rows: {len(df):,}")

    # Write to silver_cleaned_sales
    logger.info("[4/5] Writing to silver_cleaned_sales...")
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
            logger.info(f"✓ Verified: {count:,} rows in silver_cleaned_sales")
    except Exception as e:
        logger.error(f"✗ ERROR writing to silver_cleaned_sales: {e}")
        raise

    logger.info("\n" + "=" * 80)
    logger.info("SILVER LAYER CLEANSING COMPLETED SUCCESSFULLY!")
    logger.info("=" * 80)
    logger.info("SILVER LAYER CLEANSING COMPLETED SUCCESSFULLY!")
    logger.info("=" * 80)