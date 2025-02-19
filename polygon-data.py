import os
from polygon import RESTClient
from dotenv import load_dotenv
from datetime import datetime , timedelta
from polygon.rest.models import (
    Agg,
)
import io
import csv
load_dotenv()

api_key = os.getenv("POLYGON_API_KEY")
client = RESTClient(api_key=api_key)

aggs = []
for a in client.list_aggs(
    "SPY",
    1,
    "hour",
    datetime(2025, 2, 3, 9),
    datetime.now(),
    limit=50000,
):       
    aggs.append(a)

headers = [
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "vwap",
    "transactions",
    "otc",
]

# creating the csv string
csv_string = io.StringIO()
writer = csv.DictWriter(csv_string, fieldnames=headers)
writer.writeheader()

for agg in aggs:
    # verify this is an agg
    if isinstance(agg, Agg):
        # verify this is an int
        if isinstance(agg.timestamp, int):
            writer.writerow(
                {
                    "timestamp": datetime.fromtimestamp(agg.timestamp / 1000),
                    "open": agg.open,
                    "high": agg.high,
                    "low": agg.low,
                    "close": agg.close,
                    "volume": agg.volume,
                    "vwap": agg.vwap,
                    "transactions": agg.transactions,
                    "otc": agg.otc,
                }
            )

# printing the csv string
result = csv_string.getvalue()

import pandas as pd
from datetime import datetime
import pytz
# Read the data into a DataFrame
from io import StringIO

df = pd.read_csv(StringIO(result), parse_dates=['timestamp'])

# Convert to EST timezone
est = pytz.timezone('US/Eastern')
# df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert(est)

# Create the formatted list of dictionaries
formatted_data = []
for _, row in df.iterrows():
    formatted_data.append({
        "symbol": "SPY",
        "timestamp": row['timestamp'].strftime('%Y-%m-%d %H:%M:%S%z'),
        "open": row['open'],
        "high": row['high'],
        "low": row['low'],
        "close": row['close'],
        "volume": row['volume'],
        "trade_count": row['transactions'],
        "vwap": row['vwap']
    })

# print(formatted_data)

import json
with open('polygon.json', 'w') as f:
    json.dump(formatted_data, f, indent=4)

print("current_time_in_polygon-->" , datetime.now())
import time

timezone_name = time.tzname[0]
print("local_time_zone----->" , timezone_name)