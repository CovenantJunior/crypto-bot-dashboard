# data_fetcher.py - Fetches market data from Bybit

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import logging
from bot import config

# Set up logging
logging.basicConfig(
    filename='logs/data_fetcher.log',  # Separate log file for data fetching operations
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def fetch_historical_prices(pair, limit=20):
    """Fetch historical closing prices for a given pair."""
    try:
        response = config.session.get_kline(
            category="linear",
            symbol=pair.replace("/", ""),
            interval=5,  # 5-minute candles
            limit=limit
        )
        
        if "result" in response and "list" in response["result"]:
            return [float(candle[4]) for candle in response["result"]["list"]]  # Extract close prices
        else:
            logger.warning(f"No historical data found for {pair}")
            return []
    except Exception as e:
        logger.error(f"Error fetching historical prices for {pair}: {e}")
        return []

def calculate_volatility(ticker_data):
    """Calculate volatility based on 5-minute high-low price range."""
    try:
        # Fetch the latest 5-minute candle
        response = config.session.get_kline(
            category="linear",
            symbol=ticker_data["symbol"],
            interval=5,
            limit=1
        )
        candle = response["result"]["list"][0]
        high = float(candle[2])  # 5-min high
        low = float(candle[3])   # 5-min low
        last = float(ticker_data["lastPrice"])  # Use ticker's last price as reference
        return ((high - low) / last) * 100  # Volatility percentage
    except Exception as e:
        logger.error(f"Error calculating volatility: {e}")
        return 0

def calculate_momentum(ticker_data):
    """Estimate momentum based on 5-minute price change."""
    try:
        # Fetch the last two 5-minute candles
        response = config.session.get_kline(
            category="linear",
            symbol=ticker_data["symbol"],
            interval=5,
            limit=2
        )
        candles = response["result"]["list"]
        current_close = float(candles[0][4])  # Latest 5-min close
        prev_close = float(candles[1][4])     # Previous 5-min close
        return ((current_close - prev_close) / prev_close) * 100  # Convert to %
    except Exception as e:
        logger.error(f"Error calculating momentum: {e}")
        return 0

def calculate_momentum_1h(ticker_data):
    """Calculate momentum based on 1H price change."""
    try:
        last_price = float(ticker_data["lastPrice"])
        prev_price_1h = float(ticker_data["prevPrice1h"])
        return ((last_price - prev_price_1h) / prev_price_1h) * 100
    except Exception as e:
        logger.error(f"Error calculating momentum: {e}")
        return 0

def fetch_price_data(pair, long_window=None):
    """Fetch price and trend data for a given pair. If long_window is provided, 
    include historical price data for that window."""
    try:
        response = config.session.get_tickers(category="linear", symbol=pair.replace("/", ""))
        
        if response["result"]["list"]:
            ticker_data = response["result"]["list"][0]
            
            current_price = float(ticker_data["lastPrice"])
            previous_1h = float(ticker_data.get("prevPrice1h", current_price))
            previous_24h = float(ticker_data.get("prevPrice24h", current_price))
            high_24h = float(ticker_data.get("highPrice24h", current_price))
            low_24h = float(ticker_data.get("lowPrice24h", current_price))
            bid_price = float(ticker_data.get("bid1Price", current_price))
            ask_price = float(ticker_data.get("ask1Price", current_price))
            spread = ask_price - bid_price
            open_interest = float(ticker_data.get("openInterest", 0))
            volume_24h = float(ticker_data.get("volume24h", 0))
            price_change_24h = float(ticker_data.get("price24hPcnt", 0)) * 100
            uptrend = price_change_24h > 0

            # Determine previous trend based on price movement
            previous_trend = "up" if current_price > previous_1h else "down" if current_price < previous_1h else "neutral"

            volatility = calculate_volatility(ticker_data)
            momentum = calculate_momentum(ticker_data)

            price_data = {
                "current": current_price,
                "previous_1h": previous_1h,
                "previous_24h": previous_24h,
                "high_24h": high_24h,
                "low_24h": low_24h,
                "bid": bid_price,
                "ask": ask_price,
                "spread": spread,
                "open_interest": open_interest,
                "volume_24h": volume_24h,
                "dip": price_change_24h,
                "uptrend": uptrend,
                "previous_trend": previous_trend,
                "volatility": volatility,
                "momentum": momentum
            }

            # If long_window is provided, fetch historical data
            if long_window:
                price_data["historical_prices"] = fetch_historical_prices(pair, long_window)

            return price_data
        else:
            logger.warning(f"No ticker data available for {pair}")
            return {}
    except Exception as e:
        logger.error(f"Error fetching data for {pair}: {e}")
        return {}