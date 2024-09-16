black ./dags
isort ./dags
pylint --recursive=y ./dags
pytest tests/
