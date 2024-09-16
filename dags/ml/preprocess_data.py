"""Module for data preprocess."""

import os
import pickle
from typing import Any

import boto3
import numpy as np
from sklearn.model_selection import train_test_split
from utils.postgres_cli import PostgresClient

s3 = boto3.resource("s3")
# AWS_REGION = os.environ.get("AWS_REGION")
S3_BUCKET = os.environ.get("S3_BUCKET")


def dump_pickle(obj, filename: str):
    """Function to save to pikle file."""
    with open(filename, "wb") as f_out:
        return pickle.dump(obj, f_out)


# Preprocess data and create input sequences
def preprocess_data(data, sequence_length: int = 10):
    """
    Function to build the sequences of consecutive adjusted close prices.
    This sequences are the numerical features that will be used to train the model.
    """

    sequences = []
    for i in range(len(data) - sequence_length):
        sequence = data.iloc[i : i + sequence_length].values
        target = data.iloc[i + sequence_length]

        sequences.append((sequence, target))
    return sequences


def run_data_prep(stock_symbol: str, dest_path: str = "./data"):
    """Function to preprocess the data."""

    # Load data from dm
    SQL_DB = os.environ.get("SQL_DB")
    sql_cli = PostgresClient(SQL_DB)

    query = f"SELECT adj_close FROM stock_ohlc WHERE symbol='{stock_symbol}' ORDER BY date ASC"

    data = sql_cli.to_frame(query)
    data = data["adj_close"]

    sequences = preprocess_data(data)

    # We setup test_size to the last 10 records. We schedule the training dag every 2 weeks.
    train_data, test_data = train_test_split(sequences, test_size=10, shuffle=False)

    # Prepare training and test data
    X_train = np.array([item[0] for item in train_data])
    y_train = np.array([item[1] for item in train_data])
    X_test = np.array([item[0] for item in test_data])
    y_test = np.array([item[1] for item in test_data])

    # Create dest_path folder unless it already exists
    os.makedirs(dest_path, exist_ok=True)

    # Save artifacts
    # dump_pickle(
    #     (X_train, y_train), os.path.join(dest_path, f"train_{stock_symbol}.pkl")
    # )
    # dump_pickle((X_test, y_test), os.path.join(dest_path, f"test_{stock_symbol}.pkl"))

    # # Put the dataframes in S3 bucket also
    # put_object(
    #     os.path.join(dest_path, f"train_{stock_symbol}.pkl"),
    #     S3_BUCKET,
    #     f"data/train_{stock_symbol}.pkl",
    #     "Name",
    #     "data",
    # )
    # put_object(
    #     os.path.join(dest_path, f"test_{stock_symbol}.pkl"),
    #     S3_BUCKET,
    #     f"data/test_{stock_symbol}.pkl",
    #     "Name",
    #     "data",
    # )

    # Put the dataframes in S3 bucket
    pickle_byte_obj = pickle.dumps((X_train, y_train))
    s3.Object(S3_BUCKET, f"data/train_{stock_symbol}.pkl").put(Body=pickle_byte_obj)

    pickle_byte_obj = pickle.dumps((X_test, y_test))
    s3.Object(S3_BUCKET, f"data/test_{stock_symbol}.pkl").put(Body=pickle_byte_obj)
