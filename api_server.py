"""
REST API Server for Trading Bot
Provides HTTP endpoints to monitor and control the trading bot remotely.
Similar to how IDE extensions can access and control services.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from load_model import load_model

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for web-based interfaces

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_KEY = os.getenv('ALPACA_API_KEY', 'YOUR_API_KEY')
API_SECRET = os.getenv('ALPACA_API_SECRET', 'YOUR_API_SECRET')
PAPER_TRADING = os.getenv('ALPACA_PAPER', 'true').lower() == 'true'

# Initialize clients
try:
    client = TradingClient(API_KEY, API_SECRET, paper=PAPER_TRADING)
    model = load_model()
    logger.info("API server initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize API server: {e}")
    client = None
    model = None


@app.route('/', methods=['GET'])
def home():
    """API home endpoint"""
    return jsonify({
        "name": "Trading Bot API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy" if client and model else "unhealthy",
        "model_loaded": model is not None,
        "client_connected": client is not None,
        "timestamp": datetime.now().isoformat()
    })


@app.route('/status', methods=['GET'])
def get_status():
    """Get bot status and configuration"""
    if not client:
        return jsonify({"error": "Client not initialized"}), 500
    
    try:
        account = client.get_account()
        return jsonify({
            "status": "running",
            "paper_trading": PAPER_TRADING,
            "account_status": account.status,
            "buying_power": float(account.buying_power),
            "portfolio_value": float(account.portfolio_value),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/positions', methods=['GET'])
def get_positions():
    """Get current positions"""
    if not client:
        return jsonify({"error": "Client not initialized"}), 500
    
    try:
        positions = client.get_all_positions()
        result = []
        for pos in positions:
            result.append({
                "symbol": pos.symbol,
                "qty": float(pos.qty),
                "market_value": float(pos.market_value),
                "cost_basis": float(pos.cost_basis),
                "unrealized_pl": float(pos.unrealized_pl),
                "unrealized_plpc": float(pos.unrealized_plpc),
                "current_price": float(pos.current_price)
            })
        return jsonify({"positions": result, "count": len(result)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/orders', methods=['GET'])
def get_orders():
    """Get recent orders"""
    if not client:
        return jsonify({"error": "Client not initialized"}), 500
    
    try:
        orders = client.get_orders()
        result = []
        for order in orders[:20]:  # Last 20 orders
            result.append({
                "id": str(order.id),
                "symbol": order.symbol,
                "qty": float(order.qty),
                "side": order.side.value,
                "type": order.type.value,
                "status": order.status.value,
                "created_at": order.created_at.isoformat() if order.created_at else None,
                "filled_at": order.filled_at.isoformat() if order.filled_at else None,
                "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else None
            })
        return jsonify({"orders": result, "count": len(result)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/predict', methods=['POST'])
def predict():
    """Make a prediction with the model"""
    if not model:
        return jsonify({"error": "Model not loaded"}), 500
    
    try:
        data = request.get_json()
        features = data.get('features', [])
        
        if not features or len(features) == 0:
            return jsonify({"error": "No features provided"}), 400
        
        prediction = model.predict([features])[0]
        return jsonify({
            "prediction": int(prediction),
            "signal": "BUY" if prediction == 1 else "SELL",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/trade', methods=['POST'])
def manual_trade():
    """Execute a manual trade"""
    if not client:
        return jsonify({"error": "Client not initialized"}), 500
    
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'AMZN')
        side = data.get('side', 'buy').upper()
        qty = data.get('qty', 1)
        
        from alpaca.trading.requests import MarketOrderRequest
        from alpaca.trading.enums import OrderSide, TimeInForce
        
        order_side = OrderSide.BUY if side == 'BUY' else OrderSide.SELL
        order_request = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=order_side,
            time_in_force=TimeInForce.DAY
        )
        
        response = client.submit_order(order_request)
        
        return jsonify({
            "message": "Order submitted successfully",
            "order_id": str(response.id),
            "symbol": response.symbol,
            "qty": float(response.qty),
            "side": response.side.value,
            "status": response.status.value
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/model/info', methods=['GET'])
def model_info():
    """Get model information"""
    if not model:
        return jsonify({"error": "Model not loaded"}), 500
    
    try:
        return jsonify({
            "model_type": type(model).__name__,
            "n_features": model.n_features_in_ if hasattr(model, 'n_features_in_') else None,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/logs', methods=['GET'])
def get_logs():
    """Get recent log entries"""
    try:
        log_file = 'trading_bot.log'
        if not os.path.exists(log_file):
            return jsonify({"logs": [], "message": "No log file found"})
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
            # Return last 50 lines
            recent_lines = lines[-50:] if len(lines) > 50 else lines
        
        return jsonify({
            "logs": [line.strip() for line in recent_lines],
            "count": len(recent_lines)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('API_PORT', '5000'))
    debug = os.getenv('API_DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting Trading Bot API server on port {port}")
    logger.info(f"Paper trading: {PAPER_TRADING}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
