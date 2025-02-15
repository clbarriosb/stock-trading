import os
from dotenv import load_dotenv
from strategy import TMOStrategy

load_dotenv()

api_key = os.getenv("ALPACA_API_KEY")
secret_key = os.getenv("ALPACA_SECRET_KEY")
symbols = os.getenv("ALPACA_SYMBOLS")

print("API Key:", api_key)
print("Secret Key:", secret_key)

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime

stock_client = StockHistoricalDataClient(api_key=api_key,secret_key=secret_key)

symbols = "SPY"
opening_bar = stock_client.get_stock_bars(StockBarsRequest(
                                  symbol_or_symbols=symbols,
                                  timeframe=TimeFrame.Minute,
                                  start=datetime(2023, 11, 2,11),
                                  end=datetime(2023, 11, 4,11),
                                  )).df.reset_index('timestamp')
# open_prices = opening_bar.open

# print(opening_bar.open)
# print(opening_bar.close)

print(opening_bar)

# Initialize and run strategy
strategy = TMOStrategy()

signals = strategy.run_strategy(opening_bar)

# Print trade signals
trades = signals[signals['order'].notna()]
print(signals)
print("\nTrade Signals:")
print(trades[['order']])

