#FROM apache/airflow:2.9.3
FROM apache/airflow:2.10.1

RUN pip install --upgrade pip
#RUN pip install pipenv

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt