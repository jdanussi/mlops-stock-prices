"""Module for monitoring the model performance."""

import logging
import os

import numpy as np
import pandas as pd
import sqlalchemy.exc
from evidently import ColumnMapping
from evidently.metric_preset import (
    DataDriftPreset,
    DataQualityPreset,
    RegressionPreset,
    TargetDriftPreset,
)
from evidently.metrics import ColumnDriftMetric, DatasetDriftMetric
from evidently.report import Report
from utils.postgres_cli import PostgresClient

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s"
)


SQL_DB = os.environ.get("SQL_DB")


def save_metrics_to_db(df):
    """Function to save to pandas dataframe to db."""

    sql_cli = PostgresClient(SQL_DB)

    # Insert prediction into db
    SQL_TABLE = "evidently_metrics"

    try:
        sql_cli.insert_from_frame(df, SQL_TABLE)
        # print(f"Inserted {len(df)} records")
        logging.info("Inserted %s records", len(df))
    except sqlalchemy.exc.IntegrityError:
        # print("Data already exists! Nothing to do...")
        logging.info("Data already exists! Nothing to do...")


def preprocess_data(data, sequence_length):
    """
    Function to build the sequneces that evidently needs to create reports
    and calculate the performance metrics.
    """

    sequences = []
    data = data.reset_index()
    adj_close = data["adj_close"]
    prediction = data["prediction"]

    for i in range(len(adj_close) - sequence_length):
        adj_close_sequence = adj_close.iloc[i : i + sequence_length + 1].values
        target_prediction = prediction.iloc[i + sequence_length]
        sequence = np.append(adj_close_sequence, target_prediction)
        sequences.append(sequence)

    return sequences


def calculate_metrics(
    execution_date, stock_symbol, sequence_length: int = 10, dest_path: str = "./data"
):
    """
    Creates and saves evidently dashboards as html.
    Calculates and saves evidently metrics.
    """

    # Load data from db
    sql_cli = PostgresClient(SQL_DB)

    query = f"""
    SELECT s.adj_close, p.prediction
    FROM stock_ohlc s INNER JOIN stock_prediction p
    ON to_char(s.date::timestamp, 'YYYYMMDD') = to_char(p.date::timestamp, 'YYYYMMDD')
    AND s.symbol = p.symbol
    WHERE s.date < '{execution_date}'
    AND s.symbol = '{stock_symbol}'
    ORDER BY s.date ASC;
    """

    df = sql_cli.to_frame(query)
    df = df[["adj_close", "prediction"]]

    # sequence_length = 10
    data_sequences = preprocess_data(df, sequence_length)
    raw_data = pd.DataFrame(data_sequences)
    raw_data.rename(
        columns={
            0: "10",
            1: "9",
            2: "8",
            3: "7",
            4: "6",
            5: "5",
            6: "4",
            7: "3",
            8: "2",
            9: "1",
            10: "target",
            11: "prediction",
        },
        inplace=True,
    )

    reference_data = raw_data[:-sequence_length]
    current_data = raw_data[-sequence_length:]

    num_features = ["10", "9", "8", "7", "6", "5", "4", "3", "2", "1"]

    column_mapping = ColumnMapping(
        prediction="prediction",
        numerical_features=num_features,
        target="target",
        task="regression",
    )

    # Presets Metrics to calculate
    preset_report = Report(
        metrics=[
            DataDriftPreset(),
            DataQualityPreset(),
            TargetDriftPreset(),
            RegressionPreset(),
        ]
    )
    preset_report.run(
        reference_data=reference_data,
        current_data=current_data,
        column_mapping=column_mapping,
    )

    # Create dest_path folder unless it already exists
    os.makedirs(dest_path, exist_ok=True)

    # Save report to file
    with open(
        f"{dest_path}/preset_report_{stock_symbol}.html", "w", encoding="utf-8"
    ) as f:
        preset_report.save_html(f)

    # Custom Metrics to calculate
    custom_report = Report(
        metrics=[
            ColumnDriftMetric(column_name="prediction"),
            DatasetDriftMetric(),
        ]
    )
    custom_report.run(
        reference_data=reference_data,
        current_data=current_data,
        column_mapping=column_mapping,
    )

    result = custom_report.as_dict()

    prediction_drift = float(result["metrics"][0]["result"]["drift_score"])
    num_drifted_columns = result["metrics"][1]["result"]["number_of_drifted_columns"]

    # convert the tuple of tuples to a Pandas DataFrame
    columns = ["date", "symbol", "prediction_drift", "num_drifted_columns"]

    evidently_df = pd.DataFrame(
        [[execution_date, stock_symbol, prediction_drift, num_drifted_columns]],
        columns=columns,
    )
    print(evidently_df)

    save_metrics_to_db(evidently_df)

    return result
