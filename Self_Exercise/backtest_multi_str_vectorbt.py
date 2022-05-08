import os
import pandas as pd
import pandas_ta as ta
import numpy as np
import vectorbt as vbt
from datetime import datetime
from binance.client import Client
import pathlib

import sys
sys.path.append(r'C:\Users\gunsr\Desktop\Programming\Git_Remote\Investic\Python-for-Investing-101\Global_Config')
import api_key

bn_key = api_key.binance_api_key
bn_secret = api_key.binance_api_secret

column_names = ["ticker", "strategy", "condition", "parameters", "total_return", "max_drawdown", "winrate"]
global_log_df = pd.DataFrame(columns=column_names)

current_file_path = pathlib.Path(__file__).parent.resolve()

def get_data(ls_tickers, api_key="", api_secret=""):
    
    client = Client(api_key, api_secret)
    
    ls_df = []
    
    for ticker in ls_tickers:
        klines = client.get_historical_klines(ticker, Client.KLINE_INTERVAL_1DAY, "120 day ago UTC")
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



def multi_macd_str(ticker , data_df, fast_macd, slow_macd):
    
    for i in fast_macd:
        
        for j in slow_macd:
            
            if i != j:
                
                df = data_df.copy()

                df.ta.macd(i, j, append=True)
                df['signal'] = df.iloc[:,-3] > df.iloc[:, -1] # [-3] MACD, [-1] Signal Line

                tsignal_df = backtest_vectorbt(df)

                get_return(ticker, tsignal_df, "MACD", "MACD > Signal", f"Fast: {i}, Slow: {j}")



def multi_action_zone_str(ticker , data_df, fast_macd, slow_macd):
    
    for i in fast_macd:
        
        for j in slow_macd:
            
            if i != j:
                
                df = data_df.copy()

                df.ta.macd(i, j, append=True)
                df['signal'] = df.iloc[:,-3] > 0 # [-3] MACD

                tsignal_df = backtest_vectorbt(df)

                get_return(ticker, tsignal_df, "Action Zone", "MACD > 0", f"Fast: {i}, Slow: {j}")



def golden_death_cross(ticker, data_df):

    df = data_df.copy()

    if len(df) > 200:
        
        df['signal'] = df.ta.ema(50, append=True) > df.ta.ema(200, append=True)

        tsignal_df = backtest_vectorbt(df)

        get_return(ticker, tsignal_df, "Golden Death Cross", "EMA50 > EMA200", f"Fast: 50, Slow: 200")

    else:
        print("Dataframe length not enough")

        

def multi_bollinger_bands_str(ticker, data_df, bbands_length, bbands_std, mode='sma'):
    
    for i in bbands_length:
        
        for j in bbands_std:
            
            df = data_df.copy()
            df.ta.bbands(length=i, std=j, mode=mode,append=True)

            # df.loc[df.close < df.iloc[:,-4], 'signal'] = True # [-4] middle
            # df.loc[(df.close > df.iloc[:,-4]) & (df.close > df.iloc[:,-3]), 'signal'] = False # [-4] middle, [-3] upper
            # df['signal'] = df['signal'].replace(np.nan, False) # wrong, waiting fix
            
            df['signal'] = df.close < df['BBM_' + str(i) + '_' + str(float(j))]
            
            tsignal_df = backtest_vectorbt(df)

            get_return(ticker, tsignal_df, "Bollinger Bands", "Close < Middle", f"Length: {i}, STD: {j}")
    


def multi_rsi_str(ticker, data_df, lower, upper, length=[14]):
    
    for i in length:
        
        for j in lower:
            
            for k in upper:
                
                df = data_df.copy()
                # df.ta.rsi(close='close', length=i, append=True, signal_indicators=True, xa=60, xb=40)
                df.ta.rsi(close='close', length=i, append=True)
                #df['TS_Entries'] = df.iloc[:,-1] < j
                #df['TS_Exits'] = df.iloc[:,-2] > k
                df['TS_Entries'] = df['RSI_'+str(i)] < j
                df['TS_Exits'] = df['RSI_'+str(i)] > k
                
                tsignal_df = backtest_vectorbt(df, enable_tsignals=False)

                get_return(ticker, tsignal_df, "RSI", "Lower-Buy, Upper-Sell", f"Lower: {j}, Upper: {k}")
                


def backtest_vectorbt(df, enable_tsignals=True):

    df = df.set_index('date')

    if (enable_tsignals):

        df.ta.tsignals(df.signal, asbool=True, append=True)
        
        df['action_price'] = df['open'].shift(-1)

        trades_table = df.iloc[: -5][df.TS_Trades != 0]
        trades_table['return'] = trades_table['action_price'].pct_change()
        
        trades_summary = trades_table.loc[trades_table.TS_Exits == True]

    else: pass
    
    return df



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
    print(f"{strategy_name}, {parameters_detail}")
    print(port_stats)
    print("-------------------------------------------------------")

    # port.plot().show()

    logs_path = os.path.realpath(os.path.join(current_file_path, '..', 'logs', 'backtest_log.txt'))

    with open(logs_path, 'a+') as f:
        f.write(str(datetime.now()) + "\n")
        f.write(f"Ticker: {ticker}\n")
        f.write(f"Strategy: {strategy_name}\n")
        f.write(f"Condition: {condition}\n")
        f.write(str(parameters_detail)+"\n")
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

    logs_path = os.path.realpath(os.path.join(current_file_path, '..', 'logs', 'backtest_df_log.csv'))

    log_df.to_csv(logs_path, header=True, mode="w+")
    
    return log_df



if __name__ == "__main__":

    ls_tickers = ['BTCBUSD', 'ETHBUSD', 'DOGEBUSD', 'UNIBUSD', 'LUNABUSD', 'NEARBUSD', 'GALABUSD']
    # ls_tickers = ['BTCUSDT']
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

        fast_macd = [5,12,21,26]
        slow_macd = [5,12,21,26]

        # fast_macd = [12]
        # slow_macd = [26]

        multi_macd_str(ticker, data_df, fast_macd, slow_macd)

        multi_action_zone_str(ticker, data_df, fast_macd, slow_macd)
        
        golden_death_cross(ticker, data_df)

        bbands_length = [5, 7, 20]
        bbands_std = [2,3,5]
        multi_bollinger_bands_str(ticker, data_df, bbands_length, bbands_std)

        rsi_lower = [30, 40]
        rsi_upper = [50, 60, 70]
        multi_rsi_str(ticker, data_df, lower=rsi_lower, upper=rsi_upper)
    
    global_log_df = export_log_df_to_csv(global_log_df)
        
    print(global_log_df)

    print("=======================================================")
    print(" --- Backtest has Done ---")



