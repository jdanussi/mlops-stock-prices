"""Data Ingestion dag."""

import json
import logging
import os
from datetime import datetime, timedelta

import pandas as pd
import sqlalchemy.exc
import yfinance as yf
from airflow.exceptions import AirflowSkipException
from airflow.macros import ds_add
from airflow.models import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from ingestion.data_transform import transform
from ml import predict
from utils.models import StockOHLC
from utils.postgres_cli import PostgresClient

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

# Database access
SQL_DB = os.environ.get("SQL_DB")
SQL_TABLE = "stock_ohlc"

# STOCKS = {"google": "goog", "amazon": "amzn", "microsoft": "msft"}
STOCKS = {"google": "goog"}


def _check_weekday(ds):
    day_of_week = datetime.strptime(ds, "%Y-%m-%d").weekday()
    if day_of_week >= 5:  # 5 is Saturday, 6 is Sunday
        raise AirflowSkipException("Weekend detected. Skipping this DAG run.")


def _create_table_if_not_exists():
    sql_cli = PostgresClient(SQL_DB)
    sql_cli.create_table(StockOHLC)


def _get_stock_data(stock_symbol, **context):
    start_date = context["ds"]
    end_date = ds_add(start_date, 1)

    print("Getting data from Yahoo! Finance's API....")
    data = yf.download(stock_symbol, start=start_date, end=end_date, period="1d")
    data.reset_index(inplace=True)
    data["Date"] = data["Date"].astype(str)

    print(data)
    return data.to_json(orient="records")


def _transform_stock_data(**context):
    task_instance = context["ti"]
    dfs = []

    # Get xcom for each upstream task
    for comp, ticker in STOCKS.items():
        data = json.loads(task_instance.xcom_pull(task_ids=f"get_daily_data_{comp}"))
        df = transform(data, ticker)
        dfs.append(df)

    df = pd.concat(dfs, axis=0)
    df = df.reset_index()
    return df.to_json(orient="records")


def _insert_daily_data(**context):
    task_instance = context["ti"]

    df = pd.read_json(task_instance.xcom_pull(task_ids="transform_daily_data"))
    sql_cli = PostgresClient(SQL_DB)
    try:
        sql_cli.insert_from_frame(df, SQL_TABLE)
        print(f"Inserted {len(df)} records")
    except sqlalchemy.exc.IntegrityError:
        print("Data already exists! Nothing to do...")


def _predict_stock_close_price(stock_symbol, **context):
    """predict_stock_close_price."""

    prediction_date = datetime.strptime(context["ds"], "%Y-%m-%d") + timedelta(days=1)

    # Setup the prediction_date to the next bussiness day during weekend runs
    if prediction_date.weekday() == 5:  # Check if it's Saturday (5)
        prediction_date = prediction_date + timedelta(days=2)
    elif prediction_date.weekday() == 6:  # Check if it's Sunday (6)
        prediction_date = prediction_date + timedelta(days=1)

    try:
        logger.info("predict_stock_close_price")
        prediction = predict.run_predict(prediction_date, stock_symbol)
        return prediction_date.strftime("%Y-%m-%d"), prediction
    except Exception as err:
        print("There is no deployed model to get the prediction.")
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
    "start_date": datetime(2024, 7, 1),
    # "end_date": datetime(2024, 8, 18),
}


with DAG(
    "data_ingestion",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=True,
    max_active_runs=1,
) as dag:

    check_weekday_task = PythonOperator(
        task_id="check_weekday_task",
        python_callable=_check_weekday,
    )

    task_start = EmptyOperator(
        task_id="start",
    )

    create_table_if_not_exists = PythonOperator(
        task_id="create_table_if_not_exists",
        python_callable=_create_table_if_not_exists,
    )

    # Create several task in loop to get stock data
    get_data_task = {}
    for company, symbol in STOCKS.items():
        get_data_task[company] = PythonOperator(
            task_id=f"get_daily_data_{company}",
            python_callable=_get_stock_data,
            op_args=[symbol],
        )

    # Transform stock data
    transform_daily_data = PythonOperator(
        task_id="transform_daily_data", python_callable=_transform_stock_data
    )

    # Insert stock data
    insert_daily_data = PythonOperator(
        task_id="insert_daily_data", python_callable=_insert_daily_data
    )

    # Predict next close price
    predict_stock_close_price = {}
    for company, symbol in STOCKS.items():
        predict_stock_close_price[company] = PythonOperator(
            task_id=f"predict_stock_close_price_{company}",
            op_kwargs=dag.default_args,
            provide_context=True,
            python_callable=_predict_stock_close_price,
            op_args=[symbol],
        )

    task_end = EmptyOperator(
        task_id="end",
    )

    for company in STOCKS:
        (
            check_weekday_task
            >> task_start
            >> create_table_if_not_exists
            >> get_data_task[company]
            >> transform_daily_data
        )
        (
            transform_daily_data
            >> insert_daily_data
            >> predict_stock_close_price[company]
            >> task_end
        )
