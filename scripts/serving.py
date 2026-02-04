import logging
import os
from sqlalchemy import create_engine, text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_db_engine():
    """Create database engine from environment variables"""
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
        logger.error("✗ ERROR: Missing required environment variables")
        logger.error(f"   DB_USER: {DB_USER}")
        logger.error(f"   DB_PASSWORD: {'***' if DB_PASSWORD else 'MISSING'}")
        logger.error(f"   DB_HOST: {DB_HOST}")
        logger.error(f"   DB_PORT: {DB_PORT}")
        logger.error(f"   DB_NAME: {DB_NAME}")
        raise ValueError("Required environment variables are missing")

    connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    logger.info(f"Connecting to: {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}")
    return create_engine(connection_string)


def execute_sql_file(engine, sql_file_path, layer_name):
    """Execute SQL file and log results"""
    logger.info(f"\n{'=' * 60}")
    logger.info(f"Building {layer_name}...")
    logger.info(f"{'=' * 60}")
    
    if not os.path.exists(sql_file_path):
        logger.error(f"✗ SQL file not found: {sql_file_path}")
        raise FileNotFoundError(f"SQL file not found: {sql_file_path}")
    
    logger.info(f"Reading SQL from: {sql_file_path}")
    
    with open(sql_file_path, 'r') as f:
        sql_content = f.read()
    
    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
    
    logger.info(f"Executing {len(statements)} SQL statements...")
    
    with engine.begin() as conn:
        for i, statement in enumerate(statements, 1):
            if statement.strip():
                try:
                    result = conn.execute(text(statement))
                    
                    if statement.strip().upper().startswith('SELECT'):
                        rows = result.fetchall()
                        if rows:
                            logger.info(f"   Query {i} returned {len(rows)} rows:")
                            for row in rows[:5]:  # Show first 5 rows only
                                logger.info(f"      {dict(row._mapping)}")
                            if len(rows) > 5:
                                logger.info(f"      ... and {len(rows) - 5} more rows")
                except Exception as e:
                    logger.error(f"✗ Error executing statement {i}: {e}")
                    logger.error(f"   Statement: {statement[:100]}...")
                    raise
    
    logger.info(f"✓ {layer_name} completed successfully!")


def build_dim_date():
    """Build dim_date table"""
    engine = get_db_engine()
    sql_file = "/opt/airflow/sql/create_dim_date.sql"
    execute_sql_file(engine, sql_file, "dim_date")


def build_dim_product():
    engine = get_db_engine()
    sql_file = "/opt/airflow/sql/create_dim_product.sql"
    execute_sql_file(engine, sql_file, "dim_product")


def build_dim_customer():
    engine = get_db_engine()
    sql_file = "/opt/airflow/sql/create_dim_customer.sql"
    execute_sql_file(engine, sql_file, "dim_customer")


def build_fact_sales():
    engine = get_db_engine()
    sql_file = "/opt/airflow/sql/create_fact_sales.sql"
    execute_sql_file(engine, sql_file, "fact_sales")


def build_all_gold_layers():
    logger.info("\n" + "=" * 80)
    logger.info("STARTING GOLD LAYER BUILD")
    logger.info("=" * 80)
    
    try:
        # Order matters: dimensions first, then fact
        build_dim_date()
        build_dim_product()
        build_dim_customer()
        build_fact_sales()
        
        logger.info("\n" + "=" * 80)
        logger.info("GOLD LAYER BUILD COMPLETED SUCCESSFULLY!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"\n✗ GOLD LAYER BUILD FAILED: {e}")
        raise

if __name__ == "__main__":
    import sys
    try:
        build_all_gold_layers()
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)