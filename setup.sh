# From https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html

# Get Docker compose
#version='2.1.3'
#version='2.9.3'
#curl -LfO "https://airflow.apache.org/docs/apache-airflow/$version/docker-compose.yaml"

# Create dags logs and plugins folders
mkdir -p ./dags ./logs ./models ./data ./reports

# Set user
echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env

# Init airflow db metadata
docker compose up airflow-init

# Run airflow
docker compose up -d

# Go to localhost:8080 with user/pass: airflow
