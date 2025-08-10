# dockerized stock data

This project uses Airflow to automatically fetch stock prices every day from the Alpha Vantage API, clean them, and save them into a postgreSQL database.

docker-compose.yml - information about docker

.env - required environment variables

airflow -
dags/stock_dag.py - for scheduling fetching steps
scripts/fetch_data.py - to get the stock data and put in database

requirements.txt - list of requirements

---

# Setup instructions

1. Clone your repo and `cd` into the folder.

2. Fill your Alpha Vantage API key:
```bash
cp .env .env
```
3. then edit `.env` and set `API_KEY= your_api_key`
```bash
docker-compose up --build
```
This will
- start PostgreSQL on port 5432
- start Airflow webserver on port 8080 (http://localhost:8080)
- (username : admin | password : admin)

4. Enable and trigger the DAG `stock_data_pipeline` or wait for the schedule (daily)

To open a psql shell inside the postgres container:
```bash
docker exec -it postgres psql -U postgres -d stocks
```
Then run:
```sql
SELECT * FROM stock_data;
```

---

