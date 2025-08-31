from flask import Flask, render_template, jsonify, request
import asyncio  
import os
import sys
import threading
from flask_cors import CORS

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now we can import from utils
from utils.deriv_handler import DerivHandler  

app = Flask(__name__)  
# Enable CORS for all routes
CORS(app)

# Create a global event loop that runs in a background thread
loop = asyncio.new_event_loop()
deriv = None
deriv_lock = threading.Lock()

# Start the event loop in a background thread
def run_event_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

thread = threading.Thread(target=run_event_loop, args=(loop,), daemon=True)
thread.start()

def async_to_sync(coro):
    """Run a coroutine in the background event loop and wait for the result."""
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result()

def get_deriv_handler():
    """Get or create an authenticated DerivHandler instance."""
    global deriv
    with deriv_lock:
        if deriv is None:
            # Create the handler in the main thread
            deriv = DerivHandler()
            # Authenticate in the background event loop
            async_to_sync(deriv.authenticate())
        return deriv

@app.teardown_appcontext
def close_deriv_handler(exception=None):
    """Close the DerivHandler when the app context ends."""
    global deriv
    with deriv_lock:
        if deriv is not None:
            try:
                async_to_sync(deriv.close())
            except Exception as e:
                print(f"Error closing Deriv handler: {e}")
            finally:
                deriv = None

@app.route("/")  
def index():  
    return render_template("dashboard.html")  

@app.route("/stats")  
def get_stats():  
    handler = get_deriv_handler()
    balance = async_to_sync(handler.get_balance())
    return jsonify({"balance": balance})  

if __name__ == "__main__":  
    try:
        # Bind to all interfaces (0.0.0.0) to allow external access
        # Use port 5001 to avoid conflicts with port 5000
        print("Starting server on http://0.0.0.0:5001")
        app.run(host='0.0.0.0', port=5001, debug=True)
    finally:
        # Ensure the event loop is stopped when the app exits
        loop.call_soon_threadsafe(loop.stop)