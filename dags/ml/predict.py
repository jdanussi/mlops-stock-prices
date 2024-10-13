"""Module providing functions to make predictions."""

import logging
import os

import mlflow
import numpy as np
import pandas as pd
import sqlalchemy.exc
from mlflow.tracking import MlflowClient
from utils.models import StockPrediction
from utils.postgres_cli import PostgresClient

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s"
)


SQL_DB = os.environ.get("SQL_DB")


def save_prediction_to_db(df):
    """Function to save pandas dataframe to db."""
    sql_cli = PostgresClient(SQL_DB)

    # Create table if not exists
    sql_cli.create_table(StockPrediction)

    try:
        sql_cli.insert_from_frame(df, "stock_prediction")
        # print(f"Inserted {len(df)} records")
        logging.info("Inserted %s records", len(df))
    except sqlalchemy.exc.IntegrityError:
        # print("Data already exists! Nothing to do...")
        logging.info("Data already exists! Nothing to do...")


def run_predict(
    prediction_date,
    stock_symbol: str,
    sequence_length: int = 10,
    stage: str = "Production",
):
    """Function to make the predictions."""

    MODEL_NAME = f"stock-{stock_symbol}-xgboost"
    TRACKING_URI = os.environ.get("TRACKING_URI", "mlflow")

    mlflow.set_tracking_uri(TRACKING_URI)
    #mlflow.set_tracking_uri("http://mlflow:5000")
    client = MlflowClient()

    # Get the information for the latest version of the model in a given stage
    latest_version_info = client.get_latest_versions(MODEL_NAME, stages=[stage])
    latest_stage_version = latest_version_info[0].version

    # Get the model in the stage
    model_stage_uri = f"models:/{MODEL_NAME}/{latest_stage_version}"
    # print(f"model_stage_uri: {model_stage_uri}")
    logging.info("model_stage_uri: %s", model_stage_uri)

    # Load model as a PyFuncModel.
    model = mlflow.pyfunc.load_model(model_stage_uri)

    # Load data from db
    sql_cli = PostgresClient(SQL_DB)

    query = f"""
    SELECT t.adj_close
    FROM (SELECT date, adj_close
    FROM stock_ohlc
    WHERE symbol='{stock_symbol}' AND date < '{prediction_date}'
    ORDER BY date DESC
    LIMIT {sequence_length}) t
    ORDER BY t.date ASC
    """
    rs = sql_cli.to_frame(query)

    # Convert dataframe of shape (10, 1) to an array of shape (1, 10)
    rs = np.array(rs).reshape((1, -1))

    prediction = model.predict(rs)[0]
    # print(f"\nPredicted Stock Price: {prediction}")
    logging.info("Predicted Stock Price: %s", prediction)

    cols = ["date", "symbol", "prediction", "model"]
    data = [prediction_date, stock_symbol, prediction, model_stage_uri]
    df = pd.DataFrame([data], columns=cols)

    save_prediction_to_db(df)

    return f"{prediction:.2f}"
