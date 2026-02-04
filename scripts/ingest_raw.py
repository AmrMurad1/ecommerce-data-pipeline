import logging
import pandas as pd
from sqlalchemy import create_engine, text
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def ingest_to_bronze():
    
    logger.info("=" * 80)
    logger.info("Starting Bronze Layer Ingestion...")
    logger.info("=" * 80)

    # Get database credentials from environment (.env file)
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    # Validate required environment variables
    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
        logger.error("✗ ERROR: Missing required environment variables")
        logger.error(f"   DB_USER: {DB_USER}")
        logger.error(f"   DB_PASSWORD: {'***' if DB_PASSWORD else 'MISSING'}")
        logger.error(f"   DB_HOST: {DB_HOST}")
        logger.error(f"   DB_PORT: {DB_PORT}")
        logger.error(f"   DB_NAME: {DB_NAME}")
        raise ValueError("Required environment variables are missing. Check your .env file.")

    connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # File path
    excel_file = "/opt/airflow/data/Online Retail.xlsx"

    # Check if file exists
    logger.info(f"[1/5] Checking file path: {excel_file}")
    if not os.path.exists(excel_file):
        logger.error(f"✗ ERROR: File not found at {excel_file}")
        raise FileNotFoundError(f"File not found: {excel_file}")
    logger.info("✓ File found!")

    # Read Excel file
    logger.info("[2/5] Reading Excel file...")
    try:
        df = pd.read_excel(excel_file)
        logger.info(f"✓ Successfully read {len(df):,} rows")
        logger.info(f"   Columns: {list(df.columns)}")
    except Exception as e:
        logger.error(f"✗ ERROR reading Excel file: {e}")
        raise

    # Connect to PostgreSQL
    logger.info(f"[3/5] Connecting to PostgreSQL at {DB_HOST}:{DB_PORT}/{DB_NAME}")
    try:
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✓ Connection successful!")
    except Exception as e:
        logger.error(f"✗ ERROR connecting to database: {e}")
        raise

    # Load data into raw_sales table
    logger.info("[4/5] Writing data to 'raw_sales' table...")
    try:
        df.to_sql(
            name='raw_sales',
            con=engine,
            if_exists='replace',
            index=False,
            method='multi',
            chunksize=10000
        )

        # Verify insertion
        with engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM raw_sales")).scalar()
            logger.info(f"✓ Successfully inserted {count:,} rows into raw_sales")
    except Exception as e:
        logger.error(f"✗ ERROR during insertion: {e}")
        raise

    logger.info("\n" + "=" * 80)
    logger.info("✓ BRONZE LAYER INGESTION COMPLETED SUCCESSFULLY!")
    logger.info("=" * 80)


if __name__ == "__main__":
    try:
        ingest_to_bronze()
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)