from email import header
import pandas as pd
import pandas_ta as ta
from binance.client import Client
import numpy as np
from datetime import datetime
import ccxt

import sys
sys.path.append(r'C:\Users\gunsr\Desktop\Programming\Git_Remote\Investic\Python-for-Investing-101\Global_Config')
import api_key
bn_key = api_key.binance_api_key
bn_secret = api_key.binance_api_secret

def get_ccxt_data(ls_tickers, api_key, api_secret, tf='1d', limit=2000):

    exchange = ccxt.binance({
    'apiKey' : api_key,
    'secret' : api_secret
    })

    ls_df = []

    for ticker in ls_tickers:
        data = exchange.fetch_ohlcv(ticker, timeframe=tf, limit=limit)
        df = pd.DataFrame(data, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        df['date'] = pd.to_datetime(df['date'], unit='ms')

        ls_df.append(df)

    return ls_df


if __name__ == '__main__':
    
    # ls_tickers = ['BTCUSDT', 'ETHUSDT']
    ls_tickers = ['NEARBUSD']

    dfs_ticker = []

    dfs_ticker = get_ccxt_data(ls_tickers, bn_key, bn_secret, tf='1d')
    # print(ls_tickers[0])
    # print(dfs_ticker[0])

    df = pd.DataFrame()

    # print(df.ta.indicators())

    # print(help(ta.stoch))

    # dfs_ticker[0].ta.stoch(append = True)
    # print(dfs_ticker[0])

    # print(help(ta.supertrend))
    # print(help(ta.stoch))
    # print(help(ta.bbands))

    # # dfs_ticker[0].ta.supertrend(length = 14, multiplier = 3, append = True)

    # dfs_ticker[0].ta.ema(length = 50, append=True)
    # dfs_ticker[0].ta.ema(length = 200, append=True)

    # df = dfs_ticker[0]
    # # df.to_csv('./logs/output.csv', header=True, mode="w+") 
    # print(df)

    # df = df.iloc[14:]
    # print(df)
    # df['signal'] = df.iloc[:,-3] == 1
    # print(df)
    
    df = dfs_ticker[0]
    df.ta.bbands(length=3, std=3, append = True)
    # df['signal'] =  (df.close < df.iloc[:,-4]) & (df.close <  df.iloc[:,-3])
    # df['signal'] =  (df.close < df.iloc[:,-4])
    print(df)
    df.loc[df.close < df.iloc[:,-4], 'signal'] = 'True' 
    df.loc[(df.close > df.iloc[:,-4]) & (df.close > df.iloc[:,-3]), 'signal'] = 'False'
    df['signal'] = df['signal'].replace(np.nan, 'False') 
    df = df.iloc[:,-8:]
    print(df)
    # print(help(ta.bbands))


    

