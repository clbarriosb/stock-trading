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
from datetime import datetime , timedelta

stock_client = StockHistoricalDataClient(api_key=api_key,secret_key=secret_key)

from alpaca.data.enums import Adjustment

symbols = "SPY"


import pytz

# Create EST timezone object
est = pytz.timezone('US/Eastern')

symbols = "SPY"
opening_bar = stock_client.get_stock_bars(StockBarsRequest(
        symbol_or_symbols=symbols,
        timeframe=TimeFrame.Hour,
        start=datetime(2025, 1, 27,11).replace(tzinfo=pytz.UTC).astimezone(est),
        end_time = datetime.now(pytz.UTC).astimezone(est),
    )).df.reset_index('timestamp')
opening_bar['timestamp'] = opening_bar['timestamp'].dt.tz_convert('US/Eastern')


# open_prices = opening_bar.open

# print(opening_bar.open)
# print(opening_bar.close)

# print(opening_bar)

# Initialize and run strategy
strategy = TMOStrategy()

signals = strategy.run_strategy(opening_bar)

# Print trade signals
trades = signals[signals['order'].notna()]
# print(signals)
# print("\nTrade Signals:")
# print(trades[['order']])

import pandas as pd
import json
from datetime import datetime

# Assuming your data is in a DataFrame called 'df'
def save_to_json(df):
    # Reset index to make 'symbol' a column
    df = df.reset_index()
    
    # Convert timestamp to string format
    df['timestamp'] = df['timestamp'].astype(str)
    
    # Convert DataFrame to dictionary format
    data_dict = df.to_dict('records')
    
    # Save to JSON file
    with open('signal.json', 'w') as f:
        json.dump(data_dict, f, indent=4)

save_to_json(trades)

