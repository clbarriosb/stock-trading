import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("ALPACA_API_KEY")
secret_key = os.getenv("ALPACA_SECRET_KEY")
symbols = os.getenv("ALPACA_SYMBOLS")

print("API Key:", api_key)
print("Secret Key:", secret_key)

from alpaca.data.historical import StockHistoricalDataClient

stock_client = StockHistoricalDataClient(api_key=api_key,secret_key=secret_key)

from alpaca.data.timeframe import TimeFrame
from datetime import datetime , timedelta
from alpaca.data.requests import StockBarsRequest

import pytz

# Create EST timezone object
est = pytz.timezone('US/Eastern')

# Convert datetime to EST
start_time = datetime(2025, 2, 2, 11).replace(tzinfo=pytz.UTC).astimezone(est)
end_time = datetime.now(est)

symbols = "SPY"
opening_bar = stock_client.get_stock_bars(StockBarsRequest(
        symbol_or_symbols=symbols,
        timeframe=TimeFrame.Hour,
        start=datetime(2025, 2, 3, 9).replace(tzinfo=pytz.UTC).astimezone(est),
        end_time = datetime.now(pytz.UTC).astimezone(est) - timedelta(hours=2),
    )).df.reset_index('timestamp')
opening_bar['timestamp'] = opening_bar['timestamp'].dt.tz_convert('US/Eastern')

open_prices = opening_bar.open
# print(opening_bar)
current_est = datetime.now(pytz.timezone('EST')) - timedelta(hours=2)
print('current_est->' , current_est)


import pandas as pd
import json
from datetime import datetime

def save_to_json(df):

    df = df.reset_index()
    df['timestamp'] = df['timestamp'].astype(str)
    data_dict = df.to_dict('records')
    with open('market_data.json', 'w') as f:
        json.dump(data_dict, f, indent=4)

save_to_json(opening_bar)

