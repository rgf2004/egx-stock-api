import re
from threading import Lock

import requests
import yfinance as yf
from datetime import date

from flask import Flask, Response, render_template
from cachetools import cached, TTLCache
from yfinance import Search

app = Flask(__name__)

# Cache with a TTL of 60 seconds and a max size of 1024
cache = TTLCache(maxsize=1024, ttl=60)
cache_lock = Lock()

# A ticker (ABUK) or an ISIN (EGS...): letters and digits only. Anything else is
# rejected before it can reach Yahoo, so random input cannot bypass the cache
# and cost two upstream requests per call.
TICKER_RE = re.compile(r'^[A-Za-z0-9]{1,12}$')

TV_SCAN_URL = "https://scanner.tradingview.com/egypt/scan"

def fetch_tradingview_price(ticker):
    """
    Fetch the latest EGX price from TradingView's public scanner (15-minute
    delayed). Yahoo only publishes end-of-day data for EGX, so this is the
    primary source. Returns None on any failure so callers can fall back.
    """
    try:
        r = requests.post(
            TV_SCAN_URL,
            json={"symbols": {"tickers": [f"EGX:{ticker}"]}, "columns": ["close"]},
            timeout=5,
        )
        r.raise_for_status()
        data = r.json().get("data") or []
        if data and data[0]["d"][0] is not None:
            return float(data[0]["d"][0])
    except Exception:
        return None
    return None

def fetch_stock_data_with_suffix(symbol):
    """Helper function to fetch stock data for a given symbol."""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="5d")
        if not hist.empty:
            return hist['Close'].iloc[-1]
    except Exception:
        # Catch exceptions from yfinance if the ticker is invalid
        return None
    return None

def find_cairo_ticker_via_yf_search(query):
    """
    Search Yahoo for an ISIN/Name and return the best ticker
    specifically from the Cairo Stock Exchange (CAI).
    """
    try:
        search = Search(query, max_results=10)

        # Filter the list for Egyptian exchange (CAI)
        cairo_results = [s for s in search.quotes if s.get('exchange') == 'CAI']

        if cairo_results:
            # Pick the symbol from the first valid Cairo result
            found_ticker = cairo_results[0]['symbol']
            return found_ticker

    except Exception:
        # Catch any exceptions during the search
        return None
    return None

@cached(cache, lock=cache_lock)
def get_price_for_ticker(ticker):
    """
    Main logic to fetch stock price.
    1. Tries TradingView (15-minute delayed).
    2. Falls back to Yahoo with the .CA suffix (end-of-day).
    3. If that fails, uses Yahoo search to find the correct symbol on CAI exchange.
    Results are cached.
    """
    upper_ticker = ticker.upper()
    symbol_with_ca = f"{upper_ticker}.CA"

    # 1. TradingView has intraday EGX data; Yahoo is end-of-day only
    tv_price = fetch_tradingview_price(upper_ticker)
    if tv_price is not None:
        return str(round(tv_price, 2))

    # 2. Fall back to Yahoo with .CA first as it's for EGX stocks
    price = fetch_stock_data_with_suffix(symbol_with_ca)
    if price is not None:
        return str(round(price, 2))

    # 3. If no data, try to find the correct symbol via yf.Search
    found_symbol = find_cairo_ticker_via_yf_search(upper_ticker)
    if found_symbol:
        price_from_search = fetch_stock_data_with_suffix(found_symbol)
        if price_from_search is not None:
            return str(round(price_from_search, 2))

    # 4. If all attempts fail, return None
    return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/EGX/<ticker>')
def get_stock_price(ticker):
    if not TICKER_RE.fullmatch(ticker):
        return "No Data Found", 404
    try:
        price = get_price_for_ticker(ticker)
        if price:
            return price
        else:
            return "No Data Found", 404
    except Exception as e:
        return "An error occurred while fetching data.", 500

@app.route('/sitemap.xml')
def sitemap():
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        '  <url><loc>https://stocks.one23.fyi/</loc>'
        f'<lastmod>{date.today().isoformat()}</lastmod></url>\n'
        '</urlset>\n'
    )
    return Response(xml, mimetype='application/xml')

# Google Verification File Routes
@app.route('/google06da84292227ed11.html')
def google_verification_1():
    return render_template('google06da84292227ed11.html')

@app.route('/googlef7033425e346341c.html')
def google_verification_2():
    return render_template('googlef7033425e346341c.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

