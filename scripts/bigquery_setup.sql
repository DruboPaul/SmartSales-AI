-- 1. Create Dataset (Run in BigQuery Console or CLI)
-- CREATE SCHEMA IF NOT EXISTS `your-project.retail_analytics`;

-- 2. Staging Table (Auto-created by Airflow, but defined here for reference)
-- This table is truncated and reloaded daily.
CREATE OR REPLACE TABLE `your-project.retail_analytics.stg_sales` (
    transaction_id STRING,
    store_id STRING,
    product_id STRING,
    category STRING,
    price FLOAT64,
    quantity INT64,
    timestamp STRING
);

-- 3. Fact Table (Permanent storage with time-stamping)
CREATE TABLE IF NOT EXISTS `your-project.retail_analytics.fact_transactions` (
    transaction_id STRING,
    store_id STRING,
    product_id STRING,
    category STRING,
    price FLOAT64,
    quantity INT64,
    transaction_time TIMESTAMP,
    insertion_time TIMESTAMP
)
PARTITION BY DATE(transaction_time)
CLUSTER BY category, store_id;

-- 4. Example Transformation View (For BI)
CREATE OR REPLACE VIEW `your-project.retail_analytics.daily_revenue_by_category` AS
SELECT 
    DATE(transaction_time) as sale_date,
    category,
    SUM(price * quantity) as total_revenue,
    COUNT(DISTINCT transaction_id) as total_transactions
FROM `your-project.retail_analytics.fact_transactions`
GROUP BY 1, 2;
