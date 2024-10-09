"""Module for Hyperparameter tuning."""

import os
import pickle
from typing import IO

import boto3
import mlflow
import numpy as np
import xgboost as xgb
from hyperopt import STATUS_OK, Trials, fmin, hp, tpe
from hyperopt.pyll import scope
from sklearn.metrics import mean_squared_error

s3 = boto3.resource("s3")
S3_BUCKET = os.environ.get("S3_BUCKET")


def load_pickle(filename: str):
    """Function to load pickle from file."""
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)


def run_optimization(
    run_date, stock_symbol, data_path: str = "./data", num_trials: int = 5
):
    """Function to find the best hyperparameters for XGBoost regressor."""

    EXPERIMENT_NAME = f"stock-{stock_symbol}-xgboost"
    MODEL_NAME = EXPERIMENT_NAME
    DEVELOPER = os.environ.get("DEVELOPER", "Jorge Danussi")

    mlflow.set_tracking_uri("http://ec2-54-165-190-18.compute-1.amazonaws.com:5000")
    #mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment(experiment_name=EXPERIMENT_NAME)

    # X_train, y_train = load_pickle(os.path.join(data_path, f"train_{stock_symbol}.pkl"))
    # X_test, y_test = load_pickle(os.path.join(data_path, f"test_{stock_symbol}.pkl"))

    X_train, y_train = pickle.loads(
        s3.Bucket(S3_BUCKET)
        .Object(f"data/train_{stock_symbol}.pkl")
        .get()["Body"]
        .read()
    )
    X_test, y_test = pickle.loads(
        s3.Bucket(S3_BUCKET)
        .Object(f"data/test_{stock_symbol}.pkl")
        .get()["Body"]
        .read()
    )

    train = xgb.DMatrix(X_train, label=y_train)
    valid = xgb.DMatrix(X_test, label=y_test)

    mlflow.start_run(run_name=run_date)
    parent_run_id = mlflow.active_run().info.run_id

    def objective(params):

        with mlflow.start_run(nested=True):

            # mlflow.autolog()
            mlflow.set_tag("model", MODEL_NAME)
            mlflow.set_tag("developer", DEVELOPER)

            mlflow.log_params(params)

            model = xgb.train(
                params=params,
                dtrain=train,
                num_boost_round=50,
                evals=[(valid, "validation")],
                early_stopping_rounds=10,
            )
            y_pred = model.predict(valid)
            rmse = mean_squared_error(y_test, y_pred, squared=False)
            mlflow.log_metric("rmse", rmse)

            return {"loss": rmse, "status": STATUS_OK}

    search_space = {
        "max_depth": scope.int(hp.quniform("max_depth", 4, 100, 1)),
        "learning_rate": hp.loguniform("learning_rate", -3, 0),
        "reg_alpha": hp.loguniform("reg_alpha", -5, -1),
        "reg_lambda": hp.loguniform("reg_lambda", -6, -1),
        "min_child_weight": hp.loguniform("min_child_weight", -1, 3),
        "objective": "reg:linear",
        "seed": 42,
    }

    rstate = np.random.default_rng(42)  # for reproducible results
    best_params = fmin(
        fn=objective,
        space=search_space,
        algo=tpe.suggest,
        max_evals=num_trials,
        trials=Trials(),
        rstate=rstate,
    )

    mlflow.end_run()

    return best_params, parent_run_id
