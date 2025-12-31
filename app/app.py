import yfinance as yf
from flask import Flask, render_template, send_from_directory, current_app

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/EGX/<ticker>')
def get_stock_price(ticker):
    try:
        # Append .CA if not provided by the user
        symbol = ticker.upper() if ticker.endswith(".CA") else f"{ticker.upper()}.CA"

        stock = yf.Ticker(symbol)
        # Use 5d to ensure we get data even on weekends
        hist = stock.history(period="5d")

        if not hist.empty:
            # Get the very last closing price
            price = hist['Close'].iloc[-1]
            return str(round(price, 2)) # Returns just the number as text
        else:
            return "No Data", 404

    except Exception as e:
        return f"Error: {str(e)}", 500

# Google Verification File Route
@app.route('/google06da84292227ed11.html')
def google_verification_1():
    return render_template('google06da84292227ed11.html')

@app.route('/googlef7033425e346341c.html')
def google_verification_2():
    return render_template('googlef7033425e346341c.html')

if __name__ == '__main__':
    # Run on port 5000
    app.run(host='0.0.0.0', port=5000)

