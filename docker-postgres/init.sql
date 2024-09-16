-- Create the 'airflow' database, the user and asign grants
CREATE DATABASE airflow;
CREATE USER airflow WITH PASSWORD 'airflow';
GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;

-- Create the 'mlflow' database, the user and asign grants
CREATE DATABASE mlflow;
CREATE USER mlflow WITH PASSWORD 'mlflow';
GRANT ALL PRIVILEGES ON DATABASE mlflow TO mlflow;

-- Create the 'stocks' database
CREATE DATABASE stocks;

-- Connect to the 'stocks' database
\c stocks;

-- Create the table 'stock_ohlc' in the 'stocks' database
CREATE TABLE IF NOT EXISTS stock_ohlc (
    id serial PRIMARY KEY,
    date timestamp without time zone,
    symbol varchar(10),
    open double precision,
    high double precision,
    low double precision,
    close double precision,
    adj_close double precision,
    volume int,
    timestamp timestamp without time zone DEFAULT now(),
    CONSTRAINT unique_stock_ohlc UNIQUE (date, symbol)
);

-- Create the table 'stock_prediction' in the 'stocks' database
CREATE TABLE IF NOT EXISTS stock_prediction (
    id serial PRIMARY KEY,
    date timestamp without time zone,
    symbol varchar(10),
    prediction double precision,
    model varchar,
    timestamp timestamp without time zone DEFAULT now(),
    CONSTRAINT unique_stock_prediction UNIQUE (date, symbol)
);

-- Create the table 'evidently_metrics' in the 'stocks' database
CREATE TABLE IF NOT EXISTS evidently_metrics (
    id serial PRIMARY KEY,
    date timestamp without time zone,
    symbol varchar(10),
    prediction_drift double precision,
    num_drifted_columns int,
    timestamp timestamp without time zone DEFAULT now(),
    CONSTRAINT unique_evidently_metrics UNIQUE (date, symbol)
);
