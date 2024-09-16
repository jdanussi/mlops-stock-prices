FROM python:3.10-slim

# Set up the working directory
WORKDIR /mlflow

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

# Set up the SQLite database URI as environment variable
ENV BACKEND_URI=postgresql://mlflow:mlflow@postgres/mlflow
ENV ARTIFACT_URI=s3://mlflow-artifacts-remote-jad

# Expose the port the app runs on
EXPOSE 5000

ENTRYPOINT sleep 10 && mlflow server --backend-store-uri $BACKEND_URI --default-artifact-root $ARTIFACT_URI --host 0.0.0.0 --port 5000
