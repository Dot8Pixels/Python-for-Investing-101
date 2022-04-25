import secrets
import pandas as pd
import mplfinance as mpf
import numpy as np
from pandas_datareader import data as web
import yfinance as yf
yf.pdr_override()
import vectorbt as vbt
from datetime import datetime
from binance.client import Client
import os
import pandas_ta as ta

import sys
sys.path.append(r'C:\Users\gunsr\Desktop\Programming\Git_Remote\Investic\Python-for-Investing-101\Global_Config')
import api_key

bn_key = api_key.binance_api_key
bn_secret = api_key.binance_api_secret

column_names = ["ticker", "strategy", "condition", "parameters", "total_return", "max_drawdown", "winrate"]
global_log_df = pd.DataFrame(columns=column_names)

def get_data(ls_tickers, api_key, api_secret):
    
    client = Client(api_key, api_secret)
    
    ls_df = []
    
    for ticker in ls_tickers:
        klines = client.get_historical_klines(ticker, Client.KLINE_INTERVAL_1DAY, "2000 day ago UTC")
        data = pd.DataFrame(klines)
        data.columns = ['open_time', 
                        'Open', 
                        'High', 
                        'Low',
                        'Close', 
                        'Volume',
                        'close_time',
                        'quote_asset_volume',
                        'number_of_trades',
                        'taker_buy_base_asset_volume',
                        'take_buy_quote_asset_volume',
                        'can_be_ignored']
        
        data['Date'] = pd.to_datetime(data['open_time'], unit='ms')
        df = data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        df = df.astype({"Open": float, 
                        "High": float, 
                        "Low": float, 
                        "Close": float, 
                        "Volume": float})
        df = df.rename(columns = {  'Date': 'date',
                                    'Open': 'open', 
                                    'High': 'high', 
                                    'Low': 'low', 
                                    'Close': 'close',
                                    'Volume': 'volume'}, 
                                    inplace = False)
        df['chg'] = df['close'].pct_change() * 100
        ls_df.append(df)
        
    return ls_df

def backtest_vectorbt(df, str_detail):

    df = df.set_index('date')

    df.ta.tsignals(df.signal, asbool=True, append=True)
    
    df['action_price'] = df['open'].shift(-1)

    trades_table = df.iloc[: -5][df.TS_Trades != 0]
    trades_table['return'] = trades_table['action_price'].pct_change()
    
    trades_summary = trades_table.loc[trades_table.TS_Exits == True]

    print(str_detail)
    print(df)
    print(trades_summary)

    return df

def multi_macd_str(ticker , data_df, fast_macd, slow_macd):
    for i in fast_macd:
        for j in slow_macd:
            if i != j:
                df = data_df.copy()

                df.ta.macd(i, j, append=True)
                df['signal'] = df.iloc[:,-3] > df.iloc[:, -1]

                tsignal_df = backtest_vectorbt(df, f"MACD : Fast: {i}, Slow: {j}")

                get_return(ticker, tsignal_df, "MACD", "MACD > Signal", f"Fast: {i}, Slow: {j}")

def multi_action_zone_str(ticker , data_df, fast_macd, slow_macd):
    for i in fast_macd:
        for j in slow_macd:
            if i != j:
                df = data_df.copy()

                df.ta.macd(i, j, append=True)
                df['signal'] = df.iloc[:,-3] > 0

                tsignal_df = backtest_vectorbt(df, f"ActionZone : Fast: {i}, Slow: {j}")

                get_return(ticker, tsignal_df, "Action Zone", "MACD > 0", f"Fast: {i}, Slow: {j}")

def golden_death_cross(ticker, data_df):
    df = data_df.copy()

    # df.ta.ema(length = 50, append=True)
    # df.ta.ema(length = 200, append=True)
    # df['signal'] = df.iloc[:,-2] > df.iloc[:,-1]

    if len(df) > 200:

        df['signal'] = df.ta.ema(50, append=True) > df.ta.ema(200, append=True)

        tsignal_df = backtest_vectorbt(df, f"Golden Death Cross: Fast: 50, Slow: 200")

        get_return(ticker, tsignal_df, "Golden Death Cross", "EMA50 > EMA200", f"Fast: 50, Slow: 200")

    else:
        print("Dataframe length not enough")

def multi_bollinger_bands_str(ticker, data_df, bbands_length, bbands_std, mode='sma'):
    df = data_df.copy()

    for i in bbands_length:
        for j in bbands_std:
            df.ta.bbands(length=i, std=j, mode=mode,append=True)
            
            df.loc[df.close < df.iloc[:,-4], 'signal'] = True
            df.loc[(df.close > df.iloc[:,-4]) & (df.close > df.iloc[:,-3]), 'signal'] = False
            df['signal'] = df['signal'].replace(np.nan, False) 

            tsignal_df = backtest_vectorbt(df, f"Bollinger Bands: Length: {i}, STD: {j}")

            get_return(ticker, tsignal_df, "Bollinger Bands", "Close < Middle", f"Length: {i}, STD: {j}")
    

def get_return(ticker, df, strategy_name, condition, parameters_detail):

    global global_log_df

    port = vbt.Portfolio.from_signals(df.close,
                                    entries=df.TS_Entries,
                                    exits=df.TS_Exits,
                                    freq="D",
                                    init_cash=100000,
                                    fees=0.0025,
                                    sl_trail = 0.20,
                                    slippage=0.0025)

    port_stats = port.stats()

    with open('logs/backtest_log.txt', 'a+') as f:
        f.write(f"Ticker: {ticker}\n")
        f.write(f"Strategy: {strategy_name}\n")
        f.write(f"Condition: {condition}\n")
        f.write(parameters_detail+"\n")
        f.write(f"Total Return [%]: {port_stats[5]}\n")
        f.write(f"Max Drawdown [%]: {port_stats[9]}\n")
        f.write(f"Win Rate [%]: {port_stats[15]}\n")
        f.write("------------------------------------------------\n")

        input_df = pd.DataFrame({"ticker": [ticker],
                                "strategy": [strategy_name],
                                "condition": [condition],
                                "parameters": [parameters_detail],
                                "total_return": [port_stats[5]], 
                                 "max_drawdown": [port_stats[9]], 
                                 "winrate": [port_stats[15]]})

        global_log_df = global_log_df.append(input_df, ignore_index=True)

def export_log_df_to_csv(log_df):
    log_df = log_df.sort_values(by=['ticker',
                                    'total_return', 
                                    'max_drawdown', 
                                    'winrate'], 
                                ascending=[True,
                                            False, 
                                            True,
                                            False])   

    log_df = log_df.reset_index(drop=True)
    log_df.index = log_df.index + 1
    log_df.to_csv("./logs/backtest_df_log.csv", header=True, mode="w+")
    
    return log_df


if __name__ == "__main__":

    # ls_tickers = ['BTCBUSD', 'ETHBUSD', 'DOGEBUSD', 'UNIBUSD', 'LUNABUSD', 'NEARBUSD']
    ls_tickers = ['BTCUSDT']
    # ls_tickers = ['UNIBUSD', 'LUNABUSD', 'NEARBUSD']

    ls_df = get_data(ls_tickers, bn_key, bn_key)

    fast_macd = 12
    slow_macd = 26

    for idx, data_df in enumerate(ls_df):
        ticker = ls_tickers[idx]
        print(ticker)
        # print(data_df)
        
        # fast_macd = [*range(5, 27, 1)]
        # slow_macd = [*range(5, 27, 1)]

        # fast_macd = [5,12,21,26]
        # slow_macd = [5,12,21,26]

        fast_macd = [12]
        slow_macd = [26]

        multi_macd_str(ticker, data_df, fast_macd, slow_macd)

        # multi_action_zone_str(ticker, data_df, fast_macd, slow_macd)
        
        # golden_death_cross(ticker, data_df)

        bbands_length = [5, 7, 20]
        bbands_std = [2,3,5]

        # multi_bollinger_bands_str(ticker, data_df, bbands_length, bbands_std)

    
    
    global_log_df = export_log_df_to_csv(global_log_df)
        
    print(global_log_df)

    print(" --- Process Done ---")



