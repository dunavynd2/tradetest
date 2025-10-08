from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from load_model import load_model
import pandas as pd
import datetime

API_KEY = "YOUR_API_KEY"
API_SECRET = "YOUR_API_SECRET"
client = TradingClient(API_KEY, API_SECRET, paper=True)
data_client = StockHistoricalDataClient(API_KEY, API_SECRET)

model = load_model()

def fetch_latest_data():
    request_params = StockBarsRequest(
        symbol_or_symbols=["AMZN"],
        timeframe=TimeFrame.Minute,
        start=datetime.datetime.now() - datetime.timedelta(minutes=15),
        end=datetime.datetime.now()
    )
    bars = data_client.get_stock_bars(request_params).df
    bars = bars[bars['symbol'] == 'AMZN']
    bars = bars[['open', 'high', 'low', 'close', 'volume']]
    return bars.iloc[-1]

def trade():
    latest = fetch_latest_data()
    features = latest.values.tolist()
    prediction = model.predict([features])[0]

    position_size = 0.15
    if prediction == 1:
        order = MarketOrderRequest(symbol="AMZN", qty=1, side=OrderSide.BUY, time_in_force=TimeInForce.DAY)
        client.submit_order(order)
    elif prediction == 0:
        order = MarketOrderRequest(symbol="AMZN", qty=1, side=OrderSide.SELL, time_in_force=TimeInForce.DAY)
        client.submit_order(order)

trade()
