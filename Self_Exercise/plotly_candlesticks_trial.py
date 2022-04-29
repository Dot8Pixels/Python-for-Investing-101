from turtle import color
from matplotlib.pyplot import title
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import pandas_ta as ta
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

    # print(df)

    df['chg'] = df['close'].pct_change() * 100

    # print(df)

    df.ta.macd(12, 26, append=True)


    str_signal = "ActionZone"
    df['signal'] = df.iloc[:,-3] > 0

    # print(df)

    # print(df[df["signal"]==True])
    # print(df[df["signal"]==False])

    increase_color = 'green'
    decrease_color = 'red'

    bar_colors = [increase_color if x > 0 else decrease_color for x in df['chg']]

    # markers = ['^' if x == True else 'v' for x in df['signal']]

    df_plot = df.copy()
    df_plot['helper'] = df_plot['signal'].shift(1)
    df_plot = df_plot.iloc[1:]
    df_plot['drop_condition'] = df_plot['signal'] == df_plot['helper']
    # print(df_plot[df_plot['drop_condition']==False])
    df_plot = df_plot[df_plot.drop_condition == False]
    print(df_plot)

    color_markers = ['green' if x == True else 'red' for x in df_plot['signal']]
    df_plot.loc[df_plot['signal'] == True, 'marker_positions'] = df_plot['low'] * 0.95
    df_plot.loc[df_plot['signal'] == False, 'marker_positions'] = df_plot['high'] * 1.05

    
    # fig = make_subplots(specs=[[{"secondary_y": True}]])
##    fig = make_subplots(rows=3, cols=2, 
##                        # shared_xaxes=True,
##                        specs=[[{"rowspan":2, "colspan": 2}, None],
##                                [None, None],
##                                [{"colspan": 2}, None]],
##                        print_grid=False)

    # fig = make_subplots(rows=3, cols=2, 
    #                     # shared_xaxes=True,
    #                     specs=[[{"colspan":2}, {}],
    #                             [{"colspan":2}, {}],
    #                             [{"colspan":2}, {}]],
    #                     print_grid=False)

    fig = make_subplots(rows=6, cols=2, 
                        # shared_xaxes=True,
                        specs=[[{"rowspan":4,"colspan":2}, {}],
                                [None,None],
                                [None,None],
                                [None,None],
                                [{"colspan":2}, {}],
                                [{"colspan":2}, {}]],
                        print_grid=False)
    

    fig.add_trace(go.Candlestick(x=df['date'],
                                open=df['open'], 
                                high=df['high'],
                                low=df['low'], 
                                close=df['close'],
                                increasing_line_color= 'green', 
                                decreasing_line_color= 'red',
                                name="candles"), 
                                row=1, col=1)

    fig.add_trace(go.Scatter(x=df_plot['date'], 
                            y=df_plot['marker_positions'],
                            mode='markers',
                            marker=dict(size=8,
                            line=dict(color='DarkSlateGrey',width=2)),
                            marker_color= color_markers,
                            name=str_signal), 
                            row=1, col=1)
    
    fig.add_trace(go.Bar(x=df['date'], 
                        y=df['volume'], 
                        marker=dict(color=bar_colors),
                        name="volume"),
                        row=5, col=1)


    df_rsi = dfs_ticker[0]
    df_rsi.ta.rsi(append=True)

    fig.add_trace(go.Scatter(x=df_rsi['date'], 
                            y=df_rsi.iloc[:,-1],
                            mode='lines',
                            name="RSI"),
                            row=6, col=1)

    fig.add_trace(go.Scatter(
            name='RSI=30',
            x = [df['date'].min(), df['date'].max()],
            y = [30, 30],
            mode = "lines",
            marker = dict(color = 'rgb(243, 156, 18)')
        ),row=6, col=1)

    fig.add_trace(go.Scatter(
            name='RSI=70',
            x = [df['date'].min(), df['date'].max()],
            y = [70, 70],
            mode = "lines",
            marker = dict(color = 'rgb(243, 156, 18)')
        ),row=6, col=1)

    fig.update_layout(xaxis_rangeslider_visible=False, 
                        title_text="<b>" + ls_tickers[0] + "</b>",
                        title_font=dict(color='black',
                                        family='Verdena',
                                        size=48),
                        title_xanchor="auto",
                        title_yanchor="auto")


    fig.update_xaxes(matches='x')
    fig.show()
