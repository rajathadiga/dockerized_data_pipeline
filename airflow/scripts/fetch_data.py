import os
import requests
import psycopg2
from datetime import datetime
import time

def fetch_and_store_stock_data():
    API_KEY = os.getenv("API_KEY")
    DB_HOST = os.getenv("DB_HOST", "postgres")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS = os.getenv("DB_PASS", "postgres")
    DB_NAME = os.getenv("DB_NAME", "stocks")
    DB_PORT = int(os.getenv("DB_PORT", 5432))

    SYMBOL = os.getenv("SYMBOL", "AAPL")
    # alpha Vantage link to get the data for the given symbol
    URL = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={SYMBOL}&apikey={API_KEY}"

    if not API_KEY:
        raise ValueError("API_KEY environment variable is not set.")

    try:
        resp = requests.get(URL, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return

    if not isinstance(data, dict):
        print("[ERROR] Unexpected API response format.")
        return

    # checking the error message for api
    if 'Error Message' in data:
        print(f"[ERROR] API Error Message: {data.get('Error Message')}")
        return
    if 'Note' in data:
        print(f"[WARN] API Note (likely rate limit): {data.get('Note')}")
        # rate limited by alpha vantage
        return

    time_series = data.get('Time Series (Daily)')
    if not time_series:
        print("[ERROR] Time Series (Daily) not found in response.")
        return

    # retries to connect postgres 
    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASS,
                dbname=DB_NAME,
                port=DB_PORT,
                connect_timeout=10
            )
            break
        except Exception as e:
            print(f"[WARN] Postgres connection attempt {attempt} failed: {e}")
            if attempt == max_retries:
                print("[ERROR] Could not connect to Postgres after retries.")
                return
            time.sleep(2 ** attempt)

    cur = conn.cursor()
    # create table if not exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS stock_data (
            id SERIAL PRIMARY KEY,
            symbol TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            open NUMERIC,
            high NUMERIC,
            low NUMERIC,
            close NUMERIC,
            volume BIGINT,
            UNIQUE(symbol, timestamp)
        );
    """)
    inserted = 0
    for date_str, values in time_series.items():
        try:
            timestamp = datetime.strptime(date_str, "%Y-%m-%d")
            open_price = float(values.get("1. open") or 0)
            high_price = float(values.get("2. high") or 0)
            low_price = float(values.get("3. low") or 0)
            close_price = float(values.get("4. close") or 0)
            volume = int(values.get("5. volume") or 0)

            cur.execute(
                """INSERT INTO stock_data (symbol, timestamp, open, high, low, close, volume)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)
                   ON CONFLICT (symbol, timestamp) DO NOTHING;
                """, (SYMBOL, timestamp, open_price, high_price, low_price, close_price, volume)
            )
            inserted += cur.rowcount
        except Exception as e:
            print(f"[ERROR] Failed to process row {date_str}: {e}")
            continue

    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {inserted} new rows for {SYMBOL}.")
