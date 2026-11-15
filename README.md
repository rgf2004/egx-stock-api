# EGX Stock API
A simple Flask API to fetch Egyptian Exchange stock prices using `yfinance`.

## How to Run (Local)
1. `pip install -r requirements.txt`
2. `python app/app.py` (development) or `cd app && gunicorn app:app`
3. Tests: `pip install pytest && pytest`

## How to Run (Docker)
1. `docker build -t egx-api .`
2. `docker run -p 5000:5000 egx-api`

## Usage
`GET /EGX/ABUK` -> Returns 85.50


Tickers must be letters and digits only (1 to 12 characters, a ticker or an ISIN); anything else returns 404 without calling Yahoo.
