DROP TABLE IF EXISTS dim_date CASCADE;

CREATE TABLE dim_date (
    date_key        SERIAL PRIMARY KEY,
    full_date       DATE UNIQUE NOT NULL,
    year            INT NOT NULL,
    month           INT NOT NULL,
    day             INT NOT NULL,
    quarter         INT NOT NULL,
    day_of_week     INT NOT NULL,
    day_name        VARCHAR(10) NOT NULL,
    month_name      VARCHAR(10) NOT NULL,
    is_weekend      BOOLEAN NOT NULL
);

CREATE INDEX idx_dim_date_full_date ON dim_date(full_date);
CREATE INDEX idx_dim_date_year_month ON dim_date(year, month);

INSERT INTO dim_date (
    full_date, year, month, day, quarter, day_of_week, day_name, month_name, is_weekend
)
SELECT
    date_val AS full_date,
    EXTRACT(YEAR FROM date_val)::INT AS year,
    EXTRACT(MONTH FROM date_val)::INT AS month,
    EXTRACT(DAY FROM date_val)::INT AS day,
    EXTRACT(QUARTER FROM date_val)::INT AS quarter,
    EXTRACT(DOW FROM date_val)::INT AS day_of_week,
    TRIM(TO_CHAR(date_val, 'Day')) AS day_name,
    TRIM(TO_CHAR(date_val, 'Month')) AS month_name,
    CASE WHEN EXTRACT(DOW FROM date_val) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend
FROM generate_series('2010-01-01'::DATE, '2012-12-31'::DATE, '1 day'::INTERVAL) AS date_val;

SELECT COUNT(*) as total_dates FROM dim_date;
