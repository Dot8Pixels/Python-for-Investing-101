import ccxt
import numpy as np
import time
from datetime import datetime
import schedule
import pandas as pd
import pandas_ta as ta
import sys
pd.set_option('display.max_rows', None)

sys.path.append(r'C:\Users\gunsr\Desktop\Programming\Git_Remote\Investic\Python-for-Investing-101\Global_Config')
import api_key
bn_key = api_key.binance_api_key
bn_secret = api_key.binance_api_secret

exchange = ccxt.binance({
    'apiKey' : bn_key,
    'secret' : bn_secret
})

def strategy(df):
    df['ema'] = ta.ema(df['close'], length=5)
    df['sma'] = ta.sma(df['close'], length=5)
    df['signal'] = df['ema'] > df['sma']

def get_realtime(coin='DOGE/USDT', tf='1m', initial_bar=20, fetch_new=True):

    global bars, df, new_df

    bars = exchange.fetch_ohlcv(coin, timeframe=tf, limit=initial_bar)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = df[:19]
    print(df)
    strategy(df)

    # fetch_new = True

    if fetch_new == True:
        bars2 = exchange.fetch_ohlcv(coin, timeframe=tf, limit=1)
        data = pd.DataFrame(bars2, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
        new_df = pd.concat([df, data])

        new_df['ema'].iloc[-1] = ta.ema(new_df['close'][-5:], length=5).iloc[-1]
        new_df['sma'].iloc[-1] = ta.sma(new_df['close'][-5:], length=5).iloc[-1]
        new_df['signal'].iloc[-1] = new_df['ema'].iloc[-1] > new_df['sma'].iloc[-1]

        signal = new_df.iloc[-1, -1]
        pre_sig = new_df.iloc[-2, -1]

        if (signal == True) & (pre_sig == False):
            print('buy successful')
            # exchange.create_order('DOGE/USDT', 'market', 'buy', 35)
            print(f"'DOGE/USDT', 'market', 'buy', 35")

        elif (signal == False) & (pre_sig == True):
            print('sell successful')
            # exchange.create_order('DOGE/USDT', 'market', 'sell', 35)
            print(f"'DOGE/USDT', 'market', 'sell', 35")


schedule.every(5).seconds.do(get_realtime)

while False:
    schedule.run_pending()
    time.sleep(1)

bars = exchange.fetch_ohlcv('BTCUSDT', timeframe='1h', limit=20)
df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
# print(df)
df = df[:19]
print(df)
strategy(df)
print(df)

bars2 = exchange.fetch_ohlcv('BTCUSDT', timeframe='1h', limit=1)
data = pd.DataFrame(bars2, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
print(data)

new_df = pd.concat([df, data])
print(new_df)

print(new_df['close'][-5:])
print(ta.ema(new_df['close'][-5:], length=5).iloc[-1])
new_df['ema'].iloc[-1] = ta.ema(new_df['close'][-5:], length=5).iloc[-1]
print(new_df)

print(new_df['close'][-5:])
print(ta.sma(new_df['close'][-5:], length=5).iloc[-1])
new_df['sma'].iloc[-1] = ta.sma(new_df['close'][-5:], length=5).iloc[-1]
print(new_df)

new_df['signal'].iloc[-1] = new_df['ema'].iloc[-1] > new_df['sma'].iloc[-1]
print(new_df)

signal = new_df.iloc[-1, -1]
pre_sig = new_df.iloc[-2, -1]

print(f"pre-signal: {pre_sig}, signal: {signal}")

if (signal == True) & (pre_sig == False):
    print('buy successful')

elif (signal == False) & (pre_sig == True):
    print('sell successful')

else:
    print('no action')