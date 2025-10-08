import backtrader as bt
import pandas as pd
from load_model import load_model

class XGBStrategy(bt.Strategy):
    def __init__(self):
        self.model = load_model()
        self.dataclose = self.datas[0].close
        self.order = None
        self.position_size = 0.15
        self.max_loss = 0.05
        self.entry_price = None

    def next(self):
        if self.order:
            return

        features = [self.data.open[0], self.data.high[0], self.data.low[0], self.data.close[0], self.data.volume[0]]
        prediction = self.model.predict([features])[0]

        if not self.position:
            if prediction == 1:
                self.order = self.buy(size=self.position_size)
                self.entry_price = self.dataclose[0]
            elif prediction == 0:
                self.order = self.sell(size=self.position_size)
                self.entry_price = self.dataclose[0]
        else:
            if self.entry_price:
                change = (self.dataclose[0] - self.entry_price) / self.entry_price
                if self.position.size > 0 and change < -self.max_loss:
                    self.close()
                elif self.position.size < 0 and change > self.max_loss:
                    self.close()

# Load data
df = pd.read_csv('data/amzn_5min.csv', index_col='timestamp', parse_dates=True)
df = df[['open', 'high', 'low', 'close', 'volume']]
data = bt.feeds.PandasData(dataname=df)

# Run backtest
cerebro = bt.Cerebro()
cerebro.addstrategy(XGBStrategy)
cerebro.adddata(data)
cerebro.run()
cerebro.plot()
