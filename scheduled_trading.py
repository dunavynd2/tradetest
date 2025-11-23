"""
Scheduled Trading Bot
Runs the trading bot at configurable intervals using the schedule library.
"""
import os
import time
import logging
import schedule
import datetime
from datetime import datetime as dt
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from load_model import load_model

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
API_KEY = os.getenv('ALPACA_API_KEY', 'YOUR_API_KEY')
API_SECRET = os.getenv('ALPACA_API_SECRET', 'YOUR_API_SECRET')
PAPER_TRADING = os.getenv('ALPACA_PAPER', 'true').lower() == 'true'
TRADING_SYMBOL = os.getenv('TRADING_SYMBOL', 'AMZN')
POSITION_SIZE = float(os.getenv('POSITION_SIZE', '0.15'))
MAX_LOSS = float(os.getenv('MAX_LOSS', '0.05'))
TRADING_INTERVAL = int(os.getenv('TRADING_INTERVAL', '5'))

# Initialize clients
client = TradingClient(API_KEY, API_SECRET, paper=PAPER_TRADING)
data_client = StockHistoricalDataClient(API_KEY, API_SECRET)

# Load model
model = load_model()
logger.info(f"Model loaded successfully. Trading {TRADING_SYMBOL} every {TRADING_INTERVAL} minutes.")

def fetch_latest_data():
    """Fetch the latest market data for the trading symbol."""
    try:
        request_params = StockBarsRequest(
            symbol_or_symbols=[TRADING_SYMBOL],
            timeframe=TimeFrame.Minute,
            start=dt.now() - datetime.timedelta(minutes=15),
            end=dt.now()
        )
        bars = data_client.get_stock_bars(request_params).df
        bars = bars[bars['symbol'] == TRADING_SYMBOL]
        bars = bars[['open', 'high', 'low', 'close', 'volume']]
        
        if bars.empty:
            logger.warning("No data retrieved from Alpaca API")
            return None
            
        return bars.iloc[-1]
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return None

def get_current_position():
    """Get current position for the trading symbol."""
    try:
        positions = client.get_all_positions()
        for position in positions:
            if position.symbol == TRADING_SYMBOL:
                return position
        return None
    except Exception as e:
        logger.error(f"Error getting position: {e}")
        return None

def trade():
    """Execute trading logic based on model predictions."""
    try:
        logger.info(f"Running trading logic at {dt.now()}")
        
        # Fetch latest data
        latest = fetch_latest_data()
        if latest is None:
            logger.warning("No data available, skipping this cycle")
            return
        
        # Prepare features
        features = latest.values.tolist()
        prediction = model.predict([features])[0]
        
        logger.info(f"Model prediction: {prediction} (1=Buy, 0=Sell)")
        
        # Get current position
        current_position = get_current_position()
        
        # Execute trades based on prediction
        if prediction == 1 and current_position is None:
            logger.info(f"BUY signal - Submitting buy order for {TRADING_SYMBOL}")
            order = MarketOrderRequest(
                symbol=TRADING_SYMBOL,
                qty=1,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY
            )
            response = client.submit_order(order)
            logger.info(f"Buy order submitted: {response}")
            
        elif prediction == 0 and current_position is not None:
            logger.info(f"SELL signal - Submitting sell order for {TRADING_SYMBOL}")
            order = MarketOrderRequest(
                symbol=TRADING_SYMBOL,
                qty=1,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.DAY
            )
            response = client.submit_order(order)
            logger.info(f"Sell order submitted: {response}")
        else:
            logger.info("No action taken - position or prediction doesn't warrant trade")
            
    except Exception as e:
        logger.error(f"Error in trading logic: {e}", exc_info=True)

def run_scheduled_bot():
    """Run the bot with scheduled execution."""
    logger.info(f"Starting scheduled trading bot (interval: {TRADING_INTERVAL} minutes)")
    logger.info(f"Paper trading: {PAPER_TRADING}")
    
    # Schedule the trading function
    schedule.every(TRADING_INTERVAL).minutes.do(trade)
    
    # Run immediately on startup
    trade()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run_scheduled_bot()
