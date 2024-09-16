"""Module providing functions to train models."""

import json
import logging
import os
import pickle

import boto3
import mlflow
import xgboost as xgb
from mlflow.tracking import MlflowClient
from sklearn.metrics import mean_squared_error

s3 = boto3.resource("s3")
S3_BUCKET = os.environ.get("S3_BUCKET")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s"
)


def load_pickle(filename: str):
    """Function to load from pickle file."""
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)


def load_json(filename: str):
    """Function to load from json file."""
    with open(filename, "r", encoding="utf-8") as f_in:
        return json.load(f_in)


def transition_to_stage(
    client: MlflowClient,
    model_name: str,
    model_version: str,
    new_stage: str,
    archive: bool,
) -> None:
    """
    Transitions a model to a defined stage.
    """

    # Transition the model to the stage
    client.transition_model_version_stage(
        name=model_name,
        version=model_version,
        stage=new_stage,
        archive_existing_versions=archive,
    )

    print(
        "Version '%s' of the model '%s' has been transitioned to '%s'.",
        model_version,
        model_name,
        new_stage,
    )
    print("\n")


def run_train(stock_symbol, best_params, parent_run_id, data_path: str = "./data"):
    """Function for training the model."""

    EXPERIMENT_NAME = f"stock-{stock_symbol}-xgboost"
    MODEL_NAME = EXPERIMENT_NAME
    DEVELOPER = os.environ.get("DEVELOPER", "Jorge Danussi")

    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment(experiment_name=EXPERIMENT_NAME)

    with mlflow.start_run(run_id=parent_run_id):

        # mlflow.autolog()
        mlflow.set_tag("model", MODEL_NAME)
        mlflow.set_tag("developer", DEVELOPER)

        # X_train, y_train = load_pickle(
        #     os.path.join(data_path, f"train_{stock_symbol}.pkl")
        # )
        # X_test, y_test = load_pickle(
        #     os.path.join(data_path, f"test_{stock_symbol}.pkl")
        # )

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

        best_params["max_depth"] = int(best_params["max_depth"])

        mlflow.log_params(best_params)

        model = xgb.train(
            params=best_params,
            dtrain=train,
            num_boost_round=50,
            evals=[(valid, "validation")],
            early_stopping_rounds=10,
        )
        y_pred = model.predict(valid)
        rmse = mean_squared_error(y_test, y_pred, squared=False)
        mlflow.log_metric("rmse", rmse)

        mlflow.xgboost.log_model(model, artifact_path=MODEL_NAME)

        # Register the model
        run_id = mlflow.active_run().info.run_id
        model_uri = f"runs:/{run_id}/{EXPERIMENT_NAME}"
        model_details = mlflow.register_model(model_uri=model_uri, name=MODEL_NAME)

        logging.info("Model details: %s", model_details)

        return model_details.name, model_details.version, rmse


def model_to_production(
    model_name, model_version, model_rmse, stock_symbol, data_path: str = "./data"
):
    """Function for register the model."""

    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow_client = MlflowClient()

    # X_test, y_test = load_pickle(os.path.join(data_path, f"test_{stock_symbol}.pkl"))

    X_test, y_test = pickle.loads(
        s3.Bucket(S3_BUCKET)
        .Object(f"data/test_{stock_symbol}.pkl")
        .get()["Body"]
        .read()
    )

    # Transition the model to Staging
    transition_to_stage(mlflow_client, model_name, model_version, "Staging", False)

    model_staging_rmse = model_rmse

    try:
        # Load the production model, predict with the new data and calculate its RMSE

        # Get the information for the latest version of the model in a given stage
        latest_version_info = mlflow_client.get_latest_versions(
            model_name, stages=["Production"]
        )
        latest_stage_version = latest_version_info[0].version

        # Get the model in the stage
        model_stage_uri = f"models:/{model_name}/{latest_stage_version}"
        logging.info("model_stage_uri: %s", model_stage_uri)

        model_production = mlflow.pyfunc.load_model(model_stage_uri)
        model_production_predictions = model_production.predict(X_test)
        model_production_rmse = mean_squared_error(
            y_test, model_production_predictions, squared=False
        )
        logging.info("model_production_rmse: %s", model_production_rmse)

    except Exception:  # pylint: disable=broad-exception-caught
        logging.exception("No model in production stage. The current is promoted.")
        model_production_rmse = None

    # Compare RMSEs
    # If there is a model in production stage already
    if model_production_rmse:

        # If the staging model's RMSE is lower than or equal to the production model's
        # RMSE, transition the former model to production stage, and delete the previous
        # production model.
        if model_staging_rmse <= model_production_rmse:

            try:
                latest_stage_version = mlflow_client.get_latest_versions(
                    model_name, stages=["Archived"]
                )[0].version

                mlflow_client.delete_model_version(
                    name=model_name,
                    version=latest_stage_version,
                )
            except Exception:  # pylint: disable=broad-exception-caught
                logging.info("There is no 'Archived' version to delete.")

            transition_to_stage(
                mlflow_client,
                model_name,
                model_version,
                "Production",
                True,
            )

    else:
        # If there is not any model in production stage already, transition the staging
        # model to production
        transition_to_stage(
            mlflow_client,
            model_name,
            model_version,
            "Production",
            False,
        )

    return model_name, model_version
