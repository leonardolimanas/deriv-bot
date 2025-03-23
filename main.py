import asyncio
import threading
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
import sys
from utils.deriv_handler import DerivHandler  
from utils.telegram_bot import TelegramBot  

# Create Flask app
app = Flask(__name__, 
            template_folder=os.path.join('web', 'templates'),
            static_folder=os.path.join('web', 'static'))
CORS(app)

# Global variables
deriv = None
deriv_lock = threading.Lock()
main_loop = None  # Store reference to main event loop

# Flask routes
@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/stats")
def get_stats():
    # Use the stored main event loop instead of trying to get the current one
    global main_loop
    if main_loop and deriv:
        try:
            # Run the coroutine in the main event loop and wait for the result
            future = asyncio.run_coroutine_threadsafe(deriv.get_balance(), main_loop)
            balance = future.result(timeout=5)  # Add timeout to prevent hanging
            return jsonify({"balance": balance})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Service not ready"}), 503

@app.route("/markets")
def get_markets():
    """Get list of available markets/symbols."""
    global main_loop
    if main_loop and deriv:
        try:
            future = asyncio.run_coroutine_threadsafe(deriv.get_active_symbols(), main_loop)
            markets = future.result(timeout=10)  # Longer timeout for market data
            return jsonify({"markets": markets})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Service not ready"}), 503

@app.route("/subscribe", methods=["POST"])
def subscribe_to_ticks():
    """Subscribe to tick updates for a specific symbol."""
    global main_loop
    if main_loop and deriv:
        try:
            data = request.get_json()
            if not data or "symbol" not in data:
                return jsonify({"error": "Symbol is required"}), 400
                
            symbol = data["symbol"]
            future = asyncio.run_coroutine_threadsafe(deriv.subscribe_to_ticks(symbol), main_loop)
            result = future.result(timeout=5)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Service not ready"}), 503

@app.route("/unsubscribe", methods=["POST"])
def unsubscribe_from_ticks():
    """Unsubscribe from current tick subscription."""
    global main_loop
    if main_loop and deriv:
        try:
            future = asyncio.run_coroutine_threadsafe(deriv.unsubscribe_from_ticks(), main_loop)
            result = future.result(timeout=5)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Service not ready"}), 503

@app.route("/ticks")
def get_ticks():
    """Get the latest ticks."""
    if deriv:
        try:
            # This is a synchronous method, no need for coroutine
            ticks = deriv.get_latest_ticks()
            return jsonify(ticks)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Service not ready"}), 503

async def setup_services():
    """Initialize and authenticate the Deriv handler."""
    global deriv
    with deriv_lock:
        deriv = DerivHandler()
        await deriv.authenticate()
        return deriv

async def send_telegram_notification(bot, deriv):
    """Send a notification with the current balance via Telegram."""
    balance = await deriv.get_balance()
    await bot.send_message(f"Saldo Atual: {balance} USD")

async def main():
    # Store reference to the main event loop
    global main_loop
    main_loop = asyncio.get_running_loop()
    
    # Initialize services
    bot = TelegramBot()
    
    try:
        # Setup Deriv handler
        await setup_services()
        
        # Send initial Telegram notification
        await send_telegram_notification(bot, deriv)
        
        # Start Flask server in a separate thread
        server_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False))
        server_thread.daemon = True
        server_thread.start()
        
        print("Server running at http://0.0.0.0:5001")
        print("Press Ctrl+C to exit")
        
        # Keep the main event loop running
        while True:
            await asyncio.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        # Ensure resources are properly closed
        if deriv:
            await deriv.close()
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
