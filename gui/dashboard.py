import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging
# Set up logging
logging.basicConfig(filename='logs/trading_bot.log', level=logging.INFO)

from flask import Flask, jsonify, render_template, request
from bot.config import session, TRADING_PAIRS
from bot.data_fetcher import fetch_price_data
from bot.orders import place_order, get_available_balance
import threading
import time

app = Flask(__name__)

# Function to fetch market data
def fetch_market_data():
    market_data = {}
    for pair in TRADING_PAIRS:
        market_data[pair] = price_data(pair)
    return market_data

def price_data(pair):
    return fetch_price_data(pair, 5)

# Background function to update trade history
trade_history = []

def update_trade_history():
    global trade_history
    while True:
        time.sleep(10)
        try:
            response = session.get_order_history(category="spot")
            if response.get("result", {}).get("list", []):
                trade_history = [
                    {
                        "pair": trade["symbol"],
                        "action": trade["side"],
                        "price": trade.get("execPrice", 0),
                        "amount": trade.get("execQty", 0)
                    }
                    for trade in response["result"]["list"]
                ]
            else:
                logging.info("No trade history found.")
                trade_history = []
        except Exception as e:
            error_message = f"Error fetching trade history: {e}"
            print(error_message)
            logging.info(error_message)
            trade_history = []

def get_trade_history():
    return trade_history

# Start the background thread to update trade history
threading.Thread(target=update_trade_history, daemon=True).start()

# Background function to fetch account balance
def get_account_balance():
    """Fetches the total account balance in USDT."""
    try:
        response = session.get_wallet_balance(accountType="UNIFIED")
        # print(response)  # Debugging line to print the response structure
        for asset in response.get("result", {}).get("list", []):
            for coin in asset.get("coin", []):
                if coin["coin"] == "USDT":
                    return float(coin.get("walletBalance", 0))  # Use .get() to avoid KeyError
    except Exception as e:
        print(f"Error fetching account balance: {e}")
    return None

def get_trading_pairs():
    return TRADING_PAIRS

# Route to display dashboard
def start_dashboard():
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/market-data")
    def market_data():
        return jsonify(fetch_market_data())

    @app.route("/trade-history")
    def trade_history():
        return jsonify(get_trade_history())
    
    @app.route("/account-balance")
    def account_balance():
        return jsonify(get_account_balance())
    
    @app.route("/trading-pairs")
    def get_trading_pairs_route():
        return jsonify(get_trading_pairs())

    @app.route("/trade", methods=["POST"])
    def trade():
        # print(request.json);
        action = request.args.get("action")
        pair = request.args.get("pair")
        amount = get_available_balance(pair)  # Use available balance for now
        
        if not action or not pair or not amount:
            return jsonify({"error": "Missing parameters"}), 400
        
        try:
            return place_order(pair, amount, action)
        except Exception as e:
            error_message = f"Error placing trade: {e}"
            print(error_message)
            logging.error(error_message)
            return jsonify({"error": error_message}), 500

    app.run(debug=True, use_reloader=False)


if __name__ == "__main__":
    start_dashboard()
