import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# data
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')
df=df.tail(15)

df['change'] = df['AAPL.Close'] - df['AAPL.Open']
df_hi = df[df['change']>1.5]
df_lo = df[df['change']<-0.3]

not_hi = df[df.index.isin(df_hi.index)].index
not_lo = df[df.index.isin(df_lo.index)].index
df = df.drop(not_hi)
df = df.drop(not_lo)

# set up figure with values not high and not low
# include candlestick with rangeselector
fig = go.Figure(go.Candlestick(x=df['Date'],
                open=df['AAPL.Open'], high=df['AAPL.High'],
                low=df['AAPL.Low'], close=df['AAPL.Close']))

# set up trace with extreme highs
fig.add_traces(go.Candlestick(x=df_hi['Date'],
                open=df_hi['AAPL.Open'], high=df_hi['AAPL.High'],
                low=df_hi['AAPL.Low'], close=df_hi['AAPL.Close']))

# set up traces with extreme lows
fig.add_traces(go.Candlestick(x=df_lo['Date'],
                open=df_lo['AAPL.Open'], high=df_lo['AAPL.High'],
                low=df_lo['AAPL.Low'], close=df_lo['AAPL.Close']))


color_hi_fill = 'black'
color_hi_line = 'blue'

color_lo_fill = 'yellow'
color_lo_line = 'purple'

fig.data[1].increasing.fillcolor = color_hi_fill
fig.data[1].increasing.line.color = color_hi_line
fig.data[1].decreasing.fillcolor = 'rgba(0,0,0,0)'
fig.data[1].decreasing.line.color = 'rgba(0,0,0,0)'

fig.data[2].increasing.fillcolor = 'rgba(0,0,0,0)'
fig.data[2].increasing.line.color = 'rgba(0,0,0,0)'
fig.data[2].decreasing.fillcolor = color_lo_fill
fig.data[2].decreasing.line.color = color_lo_line

fig.show()