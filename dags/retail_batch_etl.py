from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from datetime import datetime, timedelta
import os
import sys

# Adding scripts directory to path to import data generator
sys.path.append(os.path.join(os.path.dirname(__file__), '../scripts'))
from data_generator import generate_batch_csv

# Default arguments for the DAG
default_args = {
    'owner': 'drubo_paul',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Configuration
PROJECT_ID = "your-gcp-project-id" # CHANGE THIS
BUCKET_NAME = "de-retail-raw-data" # CHANGE THIS
DATASET_ID = "retail_analytics"
STAGING_TABLE = "stg_sales"
FACT_TABLE = "fact_transactions"

with DAG(
    'retail_batch_etl',
    default_args=default_args,
    description='A batch ETL pipeline for retail data',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['retail', 'etl', 'gcp'],
) as dag:

    # 1. Generate Local CSV Data
    generate_data_task = PythonOperator(
        task_id='generate_local_csv',
        python_callable=generate_batch_csv,
        op_kwargs={'filename': '/tmp/daily_sales.csv', 'num_rows': 1000},
    )

    # 2. Upload to GCS Bucket
    upload_to_gcs = LocalFilesystemToGCSOperator(
        task_id='upload_to_gcs',
        src='/tmp/daily_sales.csv',
        dst='raw/{{ ds }}/daily_sales.csv',
        bucket=BUCKET_NAME,
        gcp_conn_id='google_cloud_default',
    )

    # 3. Load from GCS to BigQuery Staging (Schema auto-detection)
    load_to_bq_staging = GCSToBigQueryOperator(
        task_id='load_to_bq_staging',
        bucket=BUCKET_NAME,
        source_objects=['raw/{{ ds }}/daily_sales.csv'],
        destination_project_dataset_table=f"{PROJECT_ID}.{DATASET_ID}.{STAGING_TABLE}",
        write_disposition='WRITE_TRUNCATE',
        autodetect=True,
        gcp_conn_id='google_cloud_default',
    )

    # 4. Transform to Fact Table (Star Schema)
    transform_to_fact = BigQueryInsertJobOperator(
        task_id='transform_to_fact',
        configuration={
            "query": {
                "query": f"""
                INSERT INTO `{PROJECT_ID}.{DATASET_ID}.{FACT_TABLE}`
                SELECT 
                    transaction_id,
                    store_id,
                    product_id,
                    category,
                    price,
                    quantity,
                    CAST(timestamp AS TIMESTAMP) as transaction_time,
                    CURRENT_TIMESTAMP() as insertion_time
                FROM `{PROJECT_ID}.{DATASET_ID}.{STAGING_TABLE}`
                WHERE transaction_id IS NOT NULL;
                """,
                "useLegacySql": False,
            }
        },
        gcp_conn_id='google_cloud_default',
    )

    generate_data_task >> upload_to_gcs >> load_to_bq_staging >> transform_to_fact
