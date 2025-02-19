import matplotlib.pyplot as plt
import yfinance as yf

symbol = 'SPY'
start_date = '2023-01-01'
end_date = '2023-03-31'
# data = yf.download(symbol, start=start_date, end=end_date, interval='1d' , timeout=10000)
weekly_data = yf.download("AAPL", start="2020-01-01", end="2021-01-01", interval="1wk")
print(weekly_data)
# print(data)