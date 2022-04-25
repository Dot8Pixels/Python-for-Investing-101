import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from binance.client import Client
import numpy as np
from datetime import datetime
import ccxt

import sys

from pyparsing import col
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
    
    # ls_tickers = ['BTCUSDT', 'ETHUSDT']
    ls_tickers = ['BTCBUSD']

    dfs_ticker = []

    dfs_ticker = get_ccxt_data(ls_tickers, bn_key, bn_secret, tf='1d')

    df = dfs_ticker[0]

    print(df)

    # fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig = make_subplots(specs=[[{"secondary_y": True}]])

# include candlestick with rangeselector
    fig.add_trace(go.Candlestick(x=df['date'],
                    open=df['open'], high=df['high'],
                    low=df['low'], close=df['close']),
                secondary_y=True)

    # include a go.Bar trace for volumes
    fig.add_trace(go.Bar(x=df['date'], y=df['volume']),
                secondary_y=False)

    fig.layout.yaxis2.showgrid=False
    # fig.update_layout(xaxis_rangeslider_visible=False)
    fig.show()