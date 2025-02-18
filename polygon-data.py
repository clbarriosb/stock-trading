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
    "AAPL",
    1,
    "hour",
    datetime(2025, 2, 3, 9),
    datetime(2025, 2, 4, 9),
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
print(csv_string.getvalue())