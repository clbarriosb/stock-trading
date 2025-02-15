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
from datetime import datetime
from alpaca.data.requests import StockBarsRequest


# Set request parameters
request_params = StockBarsRequest(
    symbol_or_symbols=["AMD" , "NVDA" , "TSLA"],
    timeframe=TimeFrame.Day,
    start=datetime(2025, 1, 1),
    end=datetime(2025, 1, 2)
)

# stock_bars = stock_client.get_stock_bars(request_params)

# print(stock_bars.df)

from alpaca.data.requests import StockTradesRequest

# Set request parameters
trades_request = StockTradesRequest(
    symbol_or_symbols="AMD",
    start=datetime(2023, 11, 2,11),
    end=datetime(2023, 11, 2,12)
)

# Fetch trades
# stock_trades = stock_client.get_stock_trades(trades_request)

# Display trades
# print(stock_trades.df)


from alpaca.data.requests import StockQuotesRequest

# Set request parameters
quotes_request = StockQuotesRequest(
    symbol_or_symbols="AMD",
    start=datetime(2023, 11, 2,11),
    end=datetime(2023, 11, 2,12)
)

# Fetch quotes
# stock_quotes = stock_client.get_stock_quotes(quotes_request)

# Display quotes
# print(stock_quotes.df)


symbols = "SPY"
opening_bar = stock_client.get_stock_bars(StockBarsRequest(
                                  symbol_or_symbols=symbols,
                                  timeframe=TimeFrame.Minute,
                                  start=datetime(2025, 2, 13,11),
                                  end=datetime(2025, 2, 14,11),
                                  )).df.reset_index('timestamp')
open_prices = opening_bar.open
print(opening_bar)



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
    with open('market_data.json', 'w') as f:
        json.dump(data_dict, f, indent=4)

save_to_json(opening_bar)