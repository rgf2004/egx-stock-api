# EGX Stock API
A simple Flask API to fetch Egyptian Exchange stock prices using `yfinance`.

## How to Run (Local)
1. `pip install -r requirements.txt`
2. `python app/main.py`

## How to Run (Docker)
1. `docker build -t egx-api .`
2. `docker run -p 5000:5000 egx-api`

## Usage
`GET /EGX/ABUK` -> Returns 85.50

