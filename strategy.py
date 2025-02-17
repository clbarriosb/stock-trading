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
        """Compute True Momentum Oscillator (TMO) using vectorized operations."""
        
        # Resampling to hourly OHLC data
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)

        # Aggregate hourly open and close prices
        df_hourly = df.resample("h").agg({"open": "first", "close": "last"}).dropna()
        

        # Compute DataHour (+1, -1, 0)
        df_hourly["oHour"] = df_hourly["open"]
        df_hourly["cHour"] = df_hourly["close"]
        # df_hourly["dataHour"] = np.where(
        #     df_hourly["cHour"] > df_hourly["oHour"].shift(1), 1,
        #     np.where(df_hourly["cHour"] < df_hourly["oHour"].shift(1), -1, 0)
        # )


        df_hourly["dataHour"] = np.where(
        df_hourly["cHour"] > df_hourly["oHour"], 
        1,
        np.where(df_hourly["cHour"] < df_hourly["oHour"], -1, 0)
        ).cumsum()

        # Exponential Moving Average Function
        def ema(series, length):
            return series.ewm(span=length, adjust=False).mean()
        
        # Calculate EMAs
        df_hourly["EMA5hour"] = ema(df_hourly["dataHour"], self.calc_length)
        df_hourly["mainHour"] = ema(df_hourly["EMA5hour"], self.smooth_length)
        df_hourly["signalHour"] = ema(df_hourly["mainHour"], self.smooth_length)
        # print("df_hourly",df_hourly)
        return df_hourly["mainHour"], df_hourly["signalHour"]

# 3. Trade Signal Generation and Calculate the profie
    def generate_signals(self, df):
        """Generate trading signals"""
        main_line, signal_line = self.calculate_tmo(df)
        # print("main_line",main_line)
        # print("signal_line",signal_line)
        
        signals = pd.DataFrame(index=main_line.index)
        signals['main_line'] = main_line
        signals['signal_line'] = signal_line
        # print(signals)
    # Generate buy/sell signals
        signals['buy_signal'] = (main_line > signal_line) & (main_line.shift(1) <= signal_line.shift(1))
        signals['sell_signal'] = (main_line < signal_line) & (main_line.shift(1) >= signal_line.shift(1))
        
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
        
        # Add additional metrics for visualization
        # signals['trailing_stop'] = np.where(self.in_position, 
        #                                   self.highest_price * (1 - self.trailing_stop_percent/100),
        #                                   np.nan)
        # signals['profit_target'] = np.where(self.in_position,
        #                                   self.buy_price * (1 + self.profit_target_percent/100),
        #                                   np.nan)
        
        return signals
