import yfinance as yf


# Fetch historical data 
symbol = 'QQQ' 
start_date = '2015-01-01' 
end_date = '2022-12-31' 
data = yf.download(symbol, start=start_date, end=end_date)

# Calculating the RSI 
def rsi(data, period): 
  delta = data.diff().dropna() 
  gain = delta.where(delta > 0, 0) 
  loss = -delta.where(delta < 0, 0) 
  avg_gain = gain.rolling(window=period).mean() 
  avg_loss = loss.rolling(window=period).mean() 
  rs = avg_gain / avg_loss 
  return 100 - (100 / (1 + rs)) # Calculate the 14-day RSI data['RSI'] = rsi(data['Close'], 14)

# 4. Implementing the trading strategy
data['Signal'] = 0 
data.loc[data['RSI'] < 30, 'Signal'] = 1 
data.loc[data['RSI'] > 70, 'Signal'] = -1

# 5. Backtesting the strategy and comparing it with SPY
data['Daily_Return'] = data['Close'].pct_change() 
data['Strategy_Return'] = data['Daily_Return'] * data['Signal'].shift(1) 
data['Cumulative_Return'] = (1 + data['Strategy_Return']).cumprod()

# 7. connecting to Alpaca
from alpaca_trade_api import REST 
api_key = 'YOUR_API_KEY' 
api_secret = 'YOUR_SECRET_KEY' 
base_url = 'https://paper-api.alpaca.markets' # Use the paper trading URL for testing 
api = REST(api_key, api_secret, base_url)

# 6. Plotting the  results
# Fetch historical data for SPY 
import matplotlib.pyplot as plt
spy_data = yf.download('SPY', start=start_date, end=end_date)
# Calculate daily returns and cumulative returns for SPY 
spy_data['Daily_Return'] = spy_data['Close'].pct_change() 
spy_data['Cumulative_Return'] = (1 + spy_data['Daily_Return']).cumprod()
# Plot both cumulative returns on the same chart 
plt.figure(figsize=(12, 6)) 
plt.plot(data.index, data['Cumulative_Return'], label='SMA Strategy') 
plt.plot(spy_data.index, spy_data['Cumulative_Return'], label='SPY') 
plt.xlabel('Date') 
plt.ylabel('Cumulative Returns') 
plt.legend() 
plt.show()

# 8. Implementing the trading algorithm for live trading
import time
def check_positions(symbol): 
  positions = api.list_positions() 
  for position in positions: 
    if position.symbol == symbol: 
      return int(position.qty) 
    return 0

def trade(symbol, qty): 
  current_rsi = rsi(yf.download(symbol, start=start_date, end=end_date, interval='1d')['Close'], 14)[-1] 
  position_qty = check_positions(symbol)

if current_rsi < 30 and position_qty == 0: 
  api.submit_order( symbol=symbol, qty=qty, side='buy', type='market', time_in_force='gtc' ) 
  print("Buy order placed for", symbol) 
elif current_rsi > 70 and position_qty > 0: 
  api.submit_order( symbol=symbol, qty=position_qty, side='sell', type='market', time_in_force='gtc' ) 
  print("Sell order placed for", symbol) 
else: print("Holding", symbol)

# 9. Runining the algorithm
symbol = 'QQQ' 
qty = 10 
while True: 
  trade(symbol, qty) 
  time.sleep(86400)