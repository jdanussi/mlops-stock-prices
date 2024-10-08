"""Model monitoring dag."""

import logging
import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from ml.evidently_metrics import calculate_metrics
from utils.models import EvidentlyMetrics
from utils.postgres_cli import PostgresClient

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

# Database access
SQL_DB = os.environ.get("SQL_DB")

# STOCKS = {"google": "goog", "amazon": "amzn", "microsoft": "msft"}
STOCKS = {"google": "goog"}


def _create_table_if_not_exists():
    sql_cli = PostgresClient(SQL_DB)
    sql_cli.create_table(EvidentlyMetrics)


def _metrics_calculations(stock_symbol, **context):
    """metrics_calculations logic."""

    # date = datetime.strptime(context["ds"], "%Y-%m-%d")
    scheduled_date = context["execution_date"].strftime("%Y-%m-%d")

    try:
        logger.info("metrics_calculations")
        calculate_metrics(scheduled_date, stock_symbol, dest_path="./reports")
    except Exception as err:
        logger.exception(err)
        raise err


default_args = {
    "owner": "Jorge Danussi",
    "email": ["jdanussi@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime(2024, 10, 1),
    # "end_date": datetime(2024, 8, 18),
}

with DAG(
    dag_id="model_monitoring",
    default_args=default_args,
    schedule_interval="0 1 * * 6",
    catchup=True,
    max_active_runs=1,
) as dag:
    task_start = EmptyOperator(
        task_id="start",
    )

    create_table_if_not_exists = PythonOperator(
        task_id="create_table_if_not_exists",
        python_callable=_create_table_if_not_exists,
    )

    # Create several task in loop to monitor company models
    metrics_calculations = {}
    for company, symbol in STOCKS.items():
        metrics_calculations[company] = PythonOperator(
            task_id=f"metrics_calculations_{company}",
            op_args=[symbol],
            op_kwargs=dag.default_args,
            python_callable=_metrics_calculations,
        )

    task_end = EmptyOperator(
        task_id="end",
    )

    for company in STOCKS:
        (
            task_start
            >> create_table_if_not_exists
            >> metrics_calculations[company]
            >> task_end
        )
