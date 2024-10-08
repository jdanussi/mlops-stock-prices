"""Model training dag."""

import logging
import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from ml import hpo, preprocess_data
from ml.train_model import model_to_production, run_train
from utils.models import StockPrediction
from utils.postgres_cli import PostgresClient

# Database access
SQL_DB = os.environ.get("SQL_DB")

# STOCKS = {"google": "goog", "amazon": "amzn", "microsoft": "msft"}
STOCKS = {"google": "goog"}


logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)


def _create_table_if_not_exists():
    sql_cli = PostgresClient(SQL_DB)
    sql_cli.create_table(StockPrediction)


def _data_preprocess(stock_symbol):
    """data_preprocess logic."""

    try:
        logger.info("data_preprocess")
        preprocess_data.run_data_prep(stock_symbol, dest_path="./data")
    except Exception as err:
        logger.exception(err)
        raise err


def _hyperparameter_tuning(stock_symbol, **context):
    """hyperparameter_tuning logic."""

    scheduled_date = context["execution_date"].strftime("%Y-%m-%d")

    try:
        logger.info("hyperparameter_tuning")
        best_params, parent_run_id = hpo.run_optimization(scheduled_date, stock_symbol)
        return best_params, parent_run_id
    except Exception as err:
        logger.exception(err)
        raise err


def _model_training(stock_symbol, **context):
    """model_training logic."""

    task_instance = context["ti"]
    try:
        logger.info("model_training")

        # Get best model details from XCom
        best_params, parent_run_id = task_instance.xcom_pull(
            task_ids=f"hyperparameter_tuning_{company}"
        )

        # Get model details from XCom
        model_name, model_version, model_rmse = run_train(
            stock_symbol, best_params, parent_run_id
        )

        return model_name, model_version, model_rmse

    except Exception as err:
        logger.exception(err)
        raise err


def _register_model(stock_symbol, **context):
    """register_model logic."""

    task_instance = context["ti"]
    try:
        logger.info("register_model")

        # Get model details from XCom
        model_name, model_version, model_rmse = task_instance.xcom_pull(
            task_ids=f"model_training_{company}"
        )

        model_to_production(
            model_name, model_version, model_rmse, stock_symbol, data_path="./data"
        )

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
    dag_id="model_training",
    default_args=default_args,
    schedule_interval="0 2 */14 * *",
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

    # Create several task in loop to preprocess stock data
    data_preprocess = {}
    for company, symbol in STOCKS.items():
        data_preprocess[company] = PythonOperator(
            task_id=f"data_preprocess_{company}",
            op_args=[symbol],
            op_kwargs=dag.default_args,
            python_callable=_data_preprocess,
        )

    hyperparameter_tuning = {}
    for company, symbol in STOCKS.items():
        hyperparameter_tuning[company] = PythonOperator(
            task_id=f"hyperparameter_tuning_{company}",
            op_args=[symbol],
            op_kwargs=dag.default_args,
            provide_context=True,
            python_callable=_hyperparameter_tuning,
        )

    model_training = {}
    for company, symbol in STOCKS.items():
        model_training[company] = PythonOperator(
            task_id=f"model_training_{company}",
            op_args=[symbol],
            op_kwargs=dag.default_args,
            provide_context=True,
            python_callable=_model_training,
        )

    register_model_task = {}
    for company, symbol in STOCKS.items():
        register_model_task[company] = PythonOperator(
            task_id=f"register_model_task_{company}",
            op_args=[symbol],
            op_kwargs=dag.default_args,
            provide_context=True,
            python_callable=_register_model,
        )

    task_end = EmptyOperator(
        task_id="end",
    )

    for company in STOCKS:
        (
            task_start
            >> create_table_if_not_exists
            >> data_preprocess[company]
            >> hyperparameter_tuning[company]
        )
        (
            hyperparameter_tuning[company]
            >> model_training[company]
            >> register_model_task[company]
            >> task_end
        )
