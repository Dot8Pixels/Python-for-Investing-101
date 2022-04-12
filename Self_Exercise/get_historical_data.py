import pandas as pd
import pandas_ta as ta
from binance.client import Client
import ccxt
import numpy as np
from datetime import datetime

import sys
sys.path.append(r'C:\Users\gunsr\Desktop\Programming\Git Remote\Investic\Python-for-Investing-101\Global_Config')
import api_key
bn_key = api_key.binance_api_key
bn_secret = api_key.binance_api_secret


def get_binance_data(ls_tickers, api_key, api_secret):
    
    client = Client(api_key, api_secret)
    
    ls_df = []
    
    for ticker in ls_tickers:
        klines = client.get_historical_klines(ticker, Client.KLINE_INTERVAL_1HOUR, "30 day ago UTC")
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
        
        # data['Date'] = data['open_time'].apply(lambda timestamp: datetime.fromtimestamp(int(str(timestamp)[:10])))
        data['date'] = pd.to_datetime(data['open_time'], unit='ms')
        df = data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        df = df.astype({"open": float, "high": float, "low": float, "close": float, "volume": float})
        ls_df.append(df)
        
    return ls_df

def get_ccxt_data(ls_tickers, api_key, api_secret, tf='1d', limit=100):

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

    dfs_ticker = get_ccxt_data(ls_tickers, bn_key, bn_secret, tf='1h')
    print(ls_tickers[0])
    print(dfs_ticker[0])