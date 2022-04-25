import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# data
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')

# Create figure with secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])

# include candlestick with rangeselector
fig.add_trace(go.Candlestick(x=df['Date'],
                open=df['AAPL.Open'], high=df['AAPL.High'],
                low=df['AAPL.Low'], close=df['AAPL.Close']),
               secondary_y=True)

# include a go.Bar trace for volumes
fig.add_trace(go.Bar(x=df['Date'], y=df['AAPL.Volume']),
               secondary_y=False)

fig.layout.yaxis2.showgrid=False
fig.show()