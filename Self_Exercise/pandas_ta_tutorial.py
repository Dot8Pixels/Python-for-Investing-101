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

def get_ccxt_data(ls_tickers, api_key, api_secret, tf='1d', limit=365):

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
    
    ls_tickers = ['BTCUSDT', 'ETHUSDT']

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

    dfs_ticker[0].ta.supertrend(length = 14, multiplier = 3, append = True)
    df = dfs_ticker[0]
    # df.to_csv('./Self_Exercise/output.csv', header=True) 
    print(df)

    df = df.iloc[14:]
    print(df)
    df['signal'] = df.iloc[:,-3] == 1
    print(df)
    
