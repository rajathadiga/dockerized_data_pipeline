# Dockerized Stock Data Pipeline (Airflow + PostgreSQL)

## Overview
This pipeline fetches stock data from Alpha Vantage API daily, processes it, and stores it in a PostgreSQL database. It is orchestrated by Apache Airflow and fully Dockerized.

---

## Project Structure
```
stock_pipeline/
├── docker-compose.yml
├── .env.example
├── airflow/
│   ├── dags/
│   │   └── stock_dag.py
│   ├── scripts/
│   │   └── fetch_data.py
│   └── requirements.txt
└── README.md
```

---

## Setup Instructions

### 1. Prerequisites
- Docker (version compatible with Compose)
- Docker Compose

### 2. Clone or copy project
If you received this as a zip, unzip it. Otherwise clone your repo and `cd` into the folder.

### 3. Create `.env` file
Copy the example and fill in your Alpha Vantage API key:
```bash
cp .env.example .env
```
then edit `.env` and set `API_KEY=your_real_key`

### 4. Run Docker Compose
```bash
docker-compose up --build
```

This will:
- Start PostgreSQL on port 5432
- Start Airflow webserver on port 8080 (username/password: admin/admin)

### 5. Airflow UI
Open: http://localhost:8080  
Login with:
```
username: admin
password: admin
```

Enable and trigger the DAG `stock_data_pipeline` or wait for the schedule (daily).

### 6. Inspecting data in Postgres
To open a psql shell inside the postgres container:
```bash
docker exec -it postgres psql -U postgres -d stocks
```
Then run:
```sql
SELECT * FROM stock_data ORDER BY timestamp DESC LIMIT 20;
```

---

## Notes & Tips
- The DAG uses a simple PythonOperator to call `fetch_data.fetch_and_store_stock_data`.
- Change the stock SYMBOL inside `fetch_data.py` to fetch other tickers.
- Alpha Vantage has API rate limits; consider spacing requests or using a different provider if needed.
- All sensitive credentials are read from environment variables (the `.env` file).

---

## Files of interest
- `airflow/scripts/fetch_data.py` — the script that calls the API and saves to Postgres.
- `airflow/dags/stock_dag.py` — the Airflow DAG that schedules the job.
- `docker-compose.yml` — spins up Postgres and Airflow.

Good luck! If you want, I can:
- Add more features (multi-symbol support, incremental updates only)
- Swap to Dagster instead of Airflow
- Add pgAdmin or Adminer for easy DB browsing
