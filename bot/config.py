# config.py - Stores API keys & settings for Bybit
import os
import pytz
from datetime import datetime
from dotenv import load_dotenv
from pybit.unified_trading import HTTP

# Set timezone to New York (for US) or London (for Europe)
# Change to "Europe/London" if needed
timezone = pytz.timezone("America/New_York")
current_time = datetime.now(timezone)

print(f"Current Time ({timezone}):",
      current_time.strftime("%Y-%m-%d %H:%M:%S"))

# Load environment variables
print("Loading environment variables...")
load_dotenv()

# API Keys (Loaded Securely)
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
TESTNET = os.getenv("TESTNET", "True").lower() == "true"
print(f"API Key Loaded: {'Yes' if API_KEY else 'No'}")
print(f"Using Testnet: {TESTNET}")

# Assign strategy to pairs
""" STRATEGY_MAP = {
    # "BTC/USDT": "swing_trading",
    # "ETH/USDT": "trend_following",
    # "SOL/USDT": "scalping",
    # "DOGE/USDT": "scalping",
    # "XRP/USDT": "momentum_trading",
    # "BNB/USDT": "trend_following",
    # "ADA/USDT": "trend_following",
    # "MATIC/USDT": "momentum_trading",
    # "AVAX/USDT": "scalping",
    # "DOT/USDT": "trend_following",
    # "LINK/USDT": "momentum_trading",
    # "UNI/USDT": "scalping",
    # "BCH/USDT": "swing_trading",
    # "FIL/USDT": "trend_following",
    # "TRX/USDT": "scalping",
    # "BAT/USDT": "momentum_trading",
} """

# All scalping gagang
""" STRATEGY_MAP = {
    "BTC/USDT": "scalping",
    "SOL/USDT": "scalping",
    "DOGE/USDT": "scalping",
    "SHIB/USDT": "scalping",
    "TRX/USDT": "scalping",
    "AVAX/USDT": "scalping",
    "UNI/USDT": "scalping",
    "APT/USDT": "scalping",
    "ARB/USDT": "scalping",
    "MATIC/USDT": "scalping",
    "RUNE/USDT": "scalping",
    "PEPE/USDT": "scalping",
} """

# Low capital pairs for $100 and $20 per trade on Bybit
STRATEGY_MAP = {
    "ADA/USDT": "scalping",
    "APT/USDT": "scalping",
    "ARB/USDT": "scalping",
    "AVAX/USDT": "scalping",
    # "BNB/USDT": "scalping",
    "ETH/USDT": "scalping",
    "IP/USDT" : "scalping",
    "LINK/USDT": "scalping",
    "LTC/USDT": "scalping",
    "MATIC/USDT": "scalping",
    "PEPE/USDT": "scalping",
    "RUNE/USDT": "scalping",
    "SOL/USDT": "scalping",
    "TRX/USDT": "scalping", 
    "UNI/USDT": "scalping",
    "XRP/USDT": "scalping",
}

# High liquidity pairs 
""" STRATEGY_MAP = {
    "SOL/USDT": "scalping",
    "MATIC/USDT": "scalping",
    "ARB/USDT": "scalping",
    "APT/USDT": "scalping",
    "LINK/USDT": "scalping",
    "TRX/USDT": "scalping"
} """


# Risk factor to adjust stop-loss or trade volume, for example
RISK_FACTOR = 0.01  # 1% of total capital for risk per trade

SLEEP_INTERVAL = int(os.getenv("SLEEP_INTERVAL", 300))  # Sleep interval in seconds

TRADES_PER_DAY = int(os.getenv("TRADES_PER_DAY", 500))  # Max trades per day

# Trading Settings
TRADING_PAIRS = list(STRATEGY_MAP.keys())
QUOTE_CURRENCY = os.getenv("QUOTE_CURRENCY", "USDT")

# Trading volume settings
# Default trade amount in quote currency
TRADE_AMOUNT = float(os.getenv("TRADE_AMOUNT", 100))
# Minimum trade volume in quote currency
MIN_TRADE_AMOUNT = float(os.getenv("MIN_TRADE_AMOUNT", 20))
# Maximum trade volume in quote currency
MAX_TRADE_AMOUNT = float(os.getenv("MAX_TRADE_AMOUNT", 1000))

# Risk management settings
STOP_LOSS_PERCENT = float(os.getenv("STOP_LOSS_PERCENT", 1.01))  # Stop loss percentage

TAKE_PROFIT_PERCENT = float(os.getenv("TAKE_PROFIT_PERCENT", 1.10))  # Take profit percentage

# Enable trailing stop-loss for dynamic protection
TRAILING_STOP = os.getenv("TRAILING_STOP", "True").lower() == "true"

MAX_DAILY_LOSS = float(os.getenv("MAX_DAILY_LOSS", 0.10))  # Avoid over-trading losses


# Initialize Bybit API session
print("Initializing Bybit API session...")
session = HTTP(
    demo=True,
    testnet=TESTNET,
    api_key=API_KEY,
    api_secret=API_SECRET,
    recv_window=10000  # Increase recv_window to handle timestamp mismatch
)

print(
    f"Bybit API session initialized successfully with {len(TRADING_PAIRS)} trading pairs: {TRADING_PAIRS}")
print("[INFO] Trade amount per order:", TRADE_AMOUNT)
print("[INFO] Stop loss percent:", STOP_LOSS_PERCENT)
print("[INFO] Take profit percent:", TAKE_PROFIT_PERCENT)
print("[INFO] Trailing stop:", TRAILING_STOP)
print("[INFO] Max daily loss:", MAX_DAILY_LOSS)
