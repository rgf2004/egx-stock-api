import yfinance as yf
from flask import Flask, render_template
from cachetools import cached, TTLCache

app = Flask(__name__)

# Cache with a TTL of 300 seconds (5 minutes) and a max size of 1024
cache = TTLCache(maxsize=1024, ttl=300)

def fetch_stock_data_with_suffix(symbol):
    """Helper function to fetch stock data for a given symbol."""
    stock = yf.Ticker(symbol)
    hist = stock.history(period="5d")
    if not hist.empty:
        return hist['Close'].iloc[-1]
    return None

@cached(cache)
def get_price_for_ticker(ticker):
    """
    Main logic to fetch stock price. It first tries the ticker as is,
    then tries with a .CA suffix. Results are cached.
    """
    upper_ticker = ticker.upper()

    # 1. Try the ticker symbol as is
    price = fetch_stock_data_with_suffix(upper_ticker)
    if price is not None:
        return str(round(price, 2))

    # 2. If no data, try with .CA suffix
    price_with_suffix = fetch_stock_data_with_suffix(f"{upper_ticker}.CA")
    if price_with_suffix is not None:
        return str(round(price_with_suffix, 2))

    # 3. If still no data, return None
    return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/EGX/<ticker>')
def get_stock_price(ticker):
    try:
        price = get_price_for_ticker(ticker)
        if price:
            return price
        else:
            return "No Data Found", 404
    except Exception as e:
        # Log the exception for debugging if you have a logging setup
        # current_app.logger.error(f"Error fetching price for {ticker}: {e}")
        return "An error occurred while fetching data.", 500

# Google Verification File Routes
@app.route('/google06da84292227ed11.html')
def google_verification_1():
    return render_template('google06da84292227ed11.html')

@app.route('/googlef7033425e346341c.html')
def google_verification_2():
    return render_template('googlef7033425e346341c.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
