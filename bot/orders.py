# orders.py - Handles order placement
import logging
# Set up logging
logging.basicConfig(filename='logs/trading_bot.log', level=logging.INFO)

from bot import config

def get_available_balance(symbol):
    """Fetch available balance for a given asset."""
    try:
        response = config.session.get_wallet_balance(accountType="UNIFIED")
        assets = response.get("result", {}).get("list", [])[0].get("coin", [])

        for asset in assets:
            if asset["coin"] == symbol.replace("USDT", "").replace("/", ""):  # Convert pair to coin symbol (e.g., BTC/USDT → BTC)
                return float(asset["walletBalance"])

        return 0.0  # Default to 0 if balance is not found
    except Exception as e:
        logging.error(f"Error fetching balance for {symbol}: {e}")
        print(f"Error fetching balance for {symbol}: {e}")
        return 0.0
    
def truncate(value, decimals=4):
    value = f"{float(value):.{decimals+5}f}"  # Convert to a normal decimal string first
    return float(value[: value.index(".") + decimals + 1])

import requests

def get_instrument_info(symbol):
    instrument_info = config.session.get_instruments_info(
        category="spot",
        symbol=symbol.replace("/", ""),
    )
    return instrument_info


def get_base_precision(symbol, instrument_info):
    """Fetches the required precision for a trading pair from the exchange."""
    try:
        if instrument_info["retCode"] == 0 and "list" in instrument_info["result"]:
            for item in instrument_info["result"]["list"]:
                if item["symbol"] == symbol.replace("/", ""):
                    precision_str = item["lotSizeFilter"]["basePrecision"]
                    return len(precision_str.split(".")[1]) if "." in precision_str else 0
        
        print(f"Precision data not found for {symbol}, using default 4 decimal places.")
        return 4  # Default fallback
    except Exception as e:
        print(f"Error fetching precision for {symbol}: {e}")
        return 4  # Default fallback


def place_order(pair, amount, side, category="spot", precision=None, attempt=0, max_attempts=5):
    """Places a buy or sell order on Bybit, selling all balance if requested. Retries with lower precision if needed."""


    if attempt == 0:  # Only fetch precision on the first attempt
        instrument_info = get_instrument_info(pair)
        precision = get_base_precision(pair, instrument_info)

    if side == "Sell":
        available_balance = get_available_balance(pair)
        logging.info(f"Available balance for {pair}: {available_balance}")
        print(f"Available balance for {pair}: {available_balance}")

        print(f"Quantity precision for {pair}: {precision} decimal places")

        # Sell all available balance instead of a fixed amount
        amount = truncate(available_balance, precision)  
        
        if amount <= 0:
            logging.error(f"No balance available to sell for {pair}.")
            print(f"Error: No balance available to sell for {pair}.")
            return None
        
        logging.info(f"Selling all available balance: {amount} {pair}")
        print(f"Selling all available balance: {amount} {pair}")

    try:
        logging.info(f"Placing {side} order for {amount} {pair} in {category} category...")
        print(f"Placing {side} order for {amount} {pair} in {category} category...")
        amount = truncate(amount, precision)  
        order = config.session.place_order(
            category=category,
            symbol=pair.replace("/", ""),
            side=side,
            orderType="Market",
            qty=str(amount)
        )
        order_id = order["result"]["orderId"]
        logging.info(f"Order placed: {side} {amount} of {pair} - Order ID: {order_id}")
        print(f"Order placed: {side} {amount} of {pair} - Order ID: {order_id}")
        return order_id

    except Exception as e:
        error_message = str(e)
        logging.error(f"Error placing order for {pair}: {e}")
        print(f"Error placing order for {pair}: {e}")

        if "Order quantity has too many decimals." in error_message and precision > 0 and attempt < max_attempts:
            new_precision = precision - 1
            logging.warning(f"Retrying with reduced precision: {new_precision} decimal places...")
            print(f"Retrying with reduced precision: {new_precision} decimal places...")
            return place_order(pair, amount, side, category, new_precision, attempt + 1, max_attempts)

        return None

