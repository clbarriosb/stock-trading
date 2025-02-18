import numpy as np
import pandas as pd

class TMOStrategy:
# 1. initialize strategy parameters
    def __init__(self, length=14, calc_length=5, smooth_length=3, 
                 trailing_stop_percent=3.0, profit_target_percent=5.0):
        self.length = length
        self.calc_length = calc_length
        self.smooth_length = smooth_length
        self.trailing_stop_percent = trailing_stop_percent
        self.profit_target_percent = profit_target_percent
        
        # Initialize tracking variables
        self.highest_price = 0
        self.buy_price = 0
        self.in_position = False

    def calculate_ema(self, data, period):
        """Calculate Exponential Moving Average"""
        return data.ewm(span=period, adjust=False).mean()
    
# 2. Hourly TMO calculation
    def calculate_tmo(self, df):
    # Resampling to hourly OHLC data
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)
        
        # Aggregate hourly open and close prices
        df_hourly = df.resample("h").agg({"open": "first", "close": "last"}).dropna()
        
        # Calculate dataHour using the fold operation equivalent
        data_hour = np.zeros(len(df_hourly))
        for i in range(len(df_hourly)):
            sum_value = 0
            for j in range(min(self.length, i + 1)):
                if df_hourly['close'].iloc[i] > df_hourly['open'].iloc[i-j]:
                    sum_value += 1
                elif df_hourly['close'].iloc[i] < df_hourly['open'].iloc[i-j]:
                    sum_value -= 1
            data_hour[i] = sum_value
        
        # Exponential Moving Average calculations
        df_hourly['dataHour'] = data_hour
        df_hourly['EMA5hour'] = df_hourly['dataHour'].ewm(span=self.calc_length, adjust=False).mean()
        df_hourly['mainHour'] = df_hourly['EMA5hour'].ewm(span=self.smooth_length, adjust=False).mean()
        df_hourly['signalHour'] = df_hourly['mainHour'].ewm(span=self.smooth_length, adjust=False).mean()
        
        return df_hourly['mainHour'], df_hourly['signalHour']

# 3. Trade Signal Generation and Calculate the profie
    def generate_signals(self, df):
        """Generate trading signals"""
        main_line, signal_line = self.calculate_tmo(df)
        
        signals = pd.DataFrame(index=main_line.index)
        signals['main_line'] = main_line
        signals['signal_line'] = signal_line

        # Add trading hours filter
        signals['trading_hours'] = (signals.index.time >= pd.Timestamp('09:30').time()) & \
                                (signals.index.time <= pd.Timestamp('16:00').time())

        # Generate buy/sell signals with trading hours restriction
        signals['buy_signal'] = (main_line > signal_line) & \
                            (main_line.shift(1) <= signal_line.shift(1)) & \
                            signals['trading_hours']

        signals['sell_signal'] = (main_line < signal_line) & \
                                (main_line.shift(1) >= signal_line.shift(1)) & \
                                signals['trading_hours']
        
        test_profit = 0

    # Calculate trailing stop and profit target
        for i in range(len(signals)):
            current_price = df['close'].iloc[i]
            
            if signals['buy_signal'].iloc[i] and not self.in_position:
                self.buy_price = current_price
                self.highest_price = current_price
                self.in_position = True
                signals.loc[signals.index[i], 'order'] = 'BUY'

            
            elif self.in_position:
                self.highest_price = max(self.highest_price, current_price)
                trailing_stop = self.highest_price * (1 - self.trailing_stop_percent/100)
                profit_target = self.buy_price * (1 + self.profit_target_percent/100)

                test_profit += (current_price - self.buy_price) * 10000
                
                # Check for exit conditions
                if (current_price <= trailing_stop or 
                    current_price >= profit_target or 
                    signals['sell_signal'].iloc[i]):
                    signals.loc[signals.index[i], 'order'] = 'SELL'
                    self.in_position = False
                    self.highest_price = 0
                    self.buy_price = 0
        print(signals)
        print("test_profit",test_profit)
        return signals

    def run_strategy(self, df):
        """Execute the strategy on historical data"""
        signals = self.generate_signals(df)
        return signals
