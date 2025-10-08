# XGBoost AMZN Equity Pipeline

## Overview
This project trains an XGBoost model to predict short-term price movements for AMZN using 5-minute data. It includes:

- Model training with GridSearchCV
- Backtesting with Backtrader
- Live trading via Alpaca API
- Logging and risk management

## Setup

1. Install dependencies:
   pip install -r requirements.txt

2. Add your 5-minute AMZN CSV data to `data/amzn_5min.csv`.

3. Train the model:
   python train_model.py

4. Backtest the strategy:
   python backtest.py

5. Set environment variables for Alpaca:
   - ALPACA_API_KEY
   - ALPACA_API_SECRET
   - ALPACA_PAPER=true (or false for live trading)

6. Run live trading:
   python live_trading.py
# tradetest
