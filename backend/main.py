import asyncio
import threading
import time
import json
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
import os
import sys
import logging
from utils.native_deriv_client import NativeDerivClient
from utils.telegram_bot import TelegramBot
from database import db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('deriv_bot.log')
    ]
)

# Create Flask app for API only
app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"])  # Allow Vite dev server

# Global variables
main_loop = None
deriv = None
deriv_lock = asyncio.Lock()
ticks_cache = {"last_response": None, "last_update": 0}
connected_clients = set()  # Set to store connected SSE clients
message_queue = []  # Queue for pending messages

def broadcast_tick_update(ticks_data):
    """Broadcast tick updates to all connected SSE clients."""
    if connected_clients:
        message = {
            'type': 'tick_update',
            'data': ticks_data,
            'timestamp': time.time()
        }
        message_queue.append(message)
        print(f"📡 Broadcasting to {len(connected_clients)} clients - {len(ticks_data.get('ticks', []))} ticks")
    else:
        print(f"⚠️ No connected clients to broadcast to")




# API routes
@app.route("/api/stats")
def get_stats():
    """Get account balance and statistics."""
    global main_loop
    if main_loop and deriv:
        try:
            # Get balance
            future = asyncio.run_coroutine_threadsafe(deriv.get_balance(), main_loop)
            balance = future.result(timeout=5)  # Add timeout to prevent hanging
            return jsonify({"balance": balance})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Service not ready"}), 503

@app.route("/api/markets")
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

@app.route("/api/subscribe", methods=["POST"])
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

@app.route("/api/unsubscribe", methods=["POST"])
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

@app.route("/api/ticks")
def get_ticks():
    """Get the latest ticks (fallback for polling)."""
    global deriv
    if deriv and hasattr(deriv, 'get_latest_ticks'):
        try:
            ticks = deriv.get_latest_ticks()
            return jsonify(ticks)
        except Exception as e:
            print(f"❌ GET /api/ticks - Error: {e}")
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Service not ready"}), 503

@app.route("/api/subscription/status")
def get_subscription_status():
    """Get current subscription status."""
    global deriv
    if deriv:
        try:
            status = {
                "is_subscribed": deriv.current_symbol is not None,
                "current_symbol": deriv.current_symbol,
                "subscription_id": deriv.subscription_id,
                "tick_stream_available": deriv.tick_stream_available,
                "last_tick_time": deriv.last_tick_time,
                "total_ticks": len(deriv.latest_ticks)
            }
            return jsonify(status)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Service not ready"}), 503

@app.route("/api/subscription/cleanup", methods=["POST"])
def cleanup_subscription():
    """Cleanup subscription when frontend is closed/reloaded."""
    global deriv
    if deriv:
        try:
            # Run unsubscribe in the main loop
            if main_loop:
                future = asyncio.run_coroutine_threadsafe(deriv.unsubscribe_from_ticks(), main_loop)
                result = future.result(timeout=5)
                return jsonify({"status": "cleaned", "result": result})
            else:
                return jsonify({"error": "Main loop not available"}), 503
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Service not ready"}), 503

@app.route("/api/ticks/stream")
def stream_ticks():
    """Server-Sent Events endpoint for real-time tick updates."""
    def generate():
        # Add this client to the connected clients set
        client_id = id(generate)
        connected_clients.add(client_id)
        print(f"📡 Client {client_id} connected to SSE stream")
        
        try:
            # Send initial connection message
            initial_message = {'type': 'connected', 'message': 'SSE connection established'}
            yield f"data: {json.dumps(initial_message)}\n\n"
            
            # Keep connection alive and send updates
            while True:
                # Check for new messages in queue
                if message_queue:
                    message = message_queue.pop(0)
                    yield f"data: {json.dumps(message)}\n\n"
                
                time.sleep(0.1)  # Check every 100ms
        except GeneratorExit:
            # Client disconnected
            connected_clients.discard(client_id)
            print(f"📡 Client {client_id} disconnected from SSE stream")
    
    response = Response(generate(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Cache-Control'
    return response

@app.route("/api/debug/native-test")
async def debug_native_test():
    """Debug endpoint to test native Deriv client."""
    try:
        from utils.native_deriv_client import NativeDerivClient
        
        # Create native client
        native_client = NativeDerivClient()
        
        # Connect
        connected = await native_client.connect()
        if not connected:
            return jsonify({
                "error": "Failed to connect to Deriv WebSocket",
                "suggestion": "Check network connectivity and app_id"
            }), 500
        
        # Wait a moment for connection to stabilize
        await asyncio.sleep(1)
        
        # Subscribe to R_100 ticks
        subscription_result = await native_client.subscribe_to_ticks("R_100")
        
        # Wait for some ticks
        await asyncio.sleep(5)
        
        # Get tick data
        tick_data = native_client.get_latest_ticks()
        
        # Close connection
        await native_client.close()
        
        return jsonify({
            "native_test": {
                "connection": "success" if connected else "failed",
                "subscription": subscription_result,
                "tick_data": tick_data,
                "comparison_notes": [
                    "Compare these ticks with Deriv website",
                    "Check if timestamps and values match",
                    "This uses direct WebSocket connection"
                ]
            }
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Native test failed: {e}",
            "suggestion": "Check if websockets library is installed"
        }), 500

@app.route("/api/debug/websocket-test")
def debug_websocket_test():
    """Debug endpoint to test direct websocket connection."""
    try:
        import websocket
        import json
        import threading
        import time
        
        # Store results
        test_results = {
            "connection_status": "testing",
            "raw_responses": [],
            "errors": [],
            "suggestions": []
        }
        
        def on_message(ws, message):
            try:
                data = json.loads(message)
                test_results["raw_responses"].append({
                    "timestamp": time.time(),
                    "message": data
                })
                if len(test_results["raw_responses"]) >= 3:  # Limit to 3 responses
                    ws.close()
            except Exception as e:
                test_results["errors"].append(f"Error parsing message: {e}")
        
        def on_error(ws, error):
            test_results["errors"].append(f"WebSocket error: {error}")
            test_results["connection_status"] = "error"
        
        def on_close(ws, close_status_code, close_msg):
            test_results["connection_status"] = "closed"
        
        def on_open(ws):
            test_results["connection_status"] = "connected"
            # Subscribe to R_100 ticks
            subscribe_message = {
                "ticks": "R_100",
                "subscribe": 1
            }
            ws.send(json.dumps(subscribe_message))
        
        # Test connection
        websocket.enableTrace(False)
        ws = websocket.WebSocketApp(
            "wss://ws.derivws.com/websockets/v3?app_id=67203",
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
        # Run in thread with timeout
        def run_ws():
            ws.run_forever()
        
        thread = threading.Thread(target=run_ws)
        thread.daemon = True
        thread.start()
        
        # Wait for results (max 10 seconds)
        for _ in range(20):  # 20 * 0.5 = 10 seconds
            time.sleep(0.5)
            if test_results["connection_status"] == "closed" or len(test_results["raw_responses"]) >= 3:
                break
        
        ws.close()
        
        # Add suggestions based on results
        if test_results["raw_responses"]:
            test_results["suggestions"].append("✅ WebSocket connection successful")
            test_results["suggestions"].append("Compare timestamps and values with Deriv website")
        else:
            test_results["suggestions"].append("❌ No tick data received")
            test_results["suggestions"].append("Check if R_100 symbol is correct")
            test_results["suggestions"].append("Verify app_id 67203 is valid")
        
        return jsonify({
            "websocket_test": test_results,
            "instructions": [
                "1. Compare the 'quote' values with Deriv website",
                "2. Check if timestamps match (convert epoch to local time)",
                "3. Verify if we're getting the same symbol data",
                "4. Consider testing with production app_id if using demo"
            ]
        })
        
    except Exception as e:
        return jsonify({
            "error": f"WebSocket test failed: {e}",
            "suggestions": [
                "Install websocket-client: pip install websocket-client",
                "Check network connectivity",
                "Verify app_id is valid"
            ]
        }), 500

@app.route("/api/debug/ticks")
def debug_ticks():
    """Debug endpoint to get detailed tick information."""
    if deriv:
        try:
            ticks_data = deriv.get_latest_ticks()
            
            # Add debug information
            import time
            debug_info = {
                "current_symbol": ticks_data.get("symbol"),
                "deriv_current_symbol": deriv.current_symbol,
                "total_ticks": len(ticks_data.get("ticks", [])),
                "stream_available": ticks_data.get("available"),
                "connection_status": ticks_data.get("connection_status"),
                "last_tick_time": deriv.last_tick_time,
                "current_time": int(time.time()),
                "time_diff": int(time.time()) - deriv.last_tick_time if deriv.last_tick_time else 0,
                "recent_ticks": []
            }
            
            # Get last 5 ticks with detailed info
            recent_ticks = ticks_data.get("ticks", [])[-5:]
            for i, tick in enumerate(recent_ticks):
                # Debug log to check tick structure
                print(f"DEBUG TICK {i+1}: {tick}")
                
                tick_debug = {
                    "index": i + 1,
                    "symbol": tick.get("symbol"),
                    "is_subscribed_symbol": tick.get("is_subscribed_symbol", False),
                    "timestamp": tick.get("timestamp"),
                    "local_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tick.get("timestamp", 0))) if tick.get("timestamp") else "N/A",
                    "quote": tick.get("quote"),
                    "bid": tick.get("bid"),
                    "ask": tick.get("ask"),
                    "epoch": tick.get("epoch"),
                    "pip_size": tick.get("pip_size"),
                    "tick_size": tick.get("tick_size"),
                    "raw_tick": tick
                }
                debug_info["recent_ticks"].append(tick_debug)
            
            # Debug log for filtered ticks
            print(f"DEBUG INFO - Current Symbol: {debug_info['deriv_current_symbol']}")
            print(f"DEBUG INFO - Total ticks in response: {len(ticks_data.get('ticks', []))}")
            print(f"DEBUG INFO - Recent ticks for debug: {len(debug_info['recent_ticks'])}")
            
            return jsonify({
                "ticks_data": ticks_data,
                "debug_info": debug_info,
                "client_type": "NativeDerivClient"
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Service not ready"}), 503

# Settings endpoints
@app.route("/api/settings", methods=["GET"])
def get_settings():
    """Get all user settings."""
    try:
        settings = db.get_all_settings()
        return jsonify({"settings": settings})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/settings/<key>", methods=["GET"])
def get_setting(key):
    """Get a specific setting by key."""
    try:
        value = db.get_setting(key)
        if value is None:
            return jsonify({"error": "Setting not found"}), 404
        return jsonify({"key": key, "value": value})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/settings/<key>", methods=["PUT"])
def update_setting(key):
    """Update a specific setting."""
    try:
        data = request.get_json()
        if not data or "value" not in data:
            return jsonify({"error": "Value is required"}), 400
        
        value = str(data["value"])
        db.set_setting(key, value)
        return jsonify({"key": key, "value": value, "message": "Setting updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/settings", methods=["POST"])
def create_setting():
    """Create a new setting."""
    try:
        data = request.get_json()
        if not data or "key" not in data or "value" not in data:
            return jsonify({"error": "Key and value are required"}), 400
        
        key = data["key"]
        value = str(data["value"])
        description = data.get("description", "")
        
        db.set_setting(key, value, description)
        return jsonify({"key": key, "value": value, "message": "Setting created successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/settings/<key>", methods=["DELETE"])
def delete_setting(key):
    """Delete a setting."""
    try:
        db.delete_setting(key)
        return jsonify({"message": f"Setting '{key}' deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health")
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "deriv-bot-api"})

@app.route("/api/debug/ticks-status")
def debug_ticks_status():
    """Debug endpoint to check current ticks status."""
    global main_loop, deriv
    if main_loop and deriv:
        try:
            # get_latest_ticks is not async, so we can call it directly
            ticks_data = deriv.get_latest_ticks()
            
            return jsonify({
                "ticks_status": {
                    "current_symbol": deriv.current_symbol,
                    "total_ticks_in_memory": len(deriv.latest_ticks),
                    "filtered_ticks": len(ticks_data.get('ticks', [])),
                    "tick_stream_available": deriv.tick_stream_available,
                    "last_tick_time": deriv.last_tick_time,
                    "time_since_last_tick": time.time() - deriv.last_tick_time if deriv.last_tick_time else None,
                    "is_connected": deriv.is_connected,
                    "subscription_id": deriv.subscription_id,
                    "latest_ticks_data": ticks_data
                }
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Service not ready"}), 503

@app.route("/api/debug/account-status")
def debug_account_status():
    """Debug endpoint to check account authorization status."""
    global deriv
    if deriv:
        try:
            return jsonify({
                "account_status": {
                    "is_connected": deriv.is_connected,
                    "account_balance": deriv.account_balance,
                    "account_currency": deriv.account_currency,
                    "account_type": deriv.account_type,
                    "login_id": deriv.login_id,
                    "app_id": deriv.app_id,
                    "token_configured": bool(deriv.token),
                    "account_details": deriv.account_details
                }
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Service not ready"}), 503

@app.route("/api/debug/test-sse")
def debug_test_sse():
    """Debug endpoint to test SSE connection."""
    try:
        # Create test message
        test_message = {
            'type': 'test',
            'data': {
                'message': 'SSE test message',
                'timestamp': time.time(),
                'test': True
            },
            'timestamp': time.time()
        }
        
        # Broadcast test message
        broadcast_tick_update(test_message['data'])
        
        return jsonify({
            "sse_test": {
                "message": "Test SSE message sent",
                "connected_clients": len(connected_clients),
                "message_queue_length": len(message_queue),
                "test_message": test_message
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/debug/test-broadcast")
def debug_test_broadcast():
    """Debug endpoint to test SSE broadcast."""
    try:
        # Create test tick data
        test_ticks = [
            {
                "symbol": "R_100",
                "quote": 1234.56,
                "bid": 1234.50,
                "ask": 1234.60,
                "timestamp": int(time.time()),
                "epoch": int(time.time())
            }
        ]
        
        test_data = {
            "symbol": "R_100",
            "ticks": test_ticks,
            "available": True,
            "connection_status": "connected",
            "last_update": time.time()
        }
        
        # Broadcast test data
        broadcast_tick_update(test_data)
        
        return jsonify({
            "test_broadcast": {
                "message": "Test broadcast sent",
                "connected_clients": len(connected_clients),
                "message_queue_length": len(message_queue),
                "test_data": test_data
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/debug/telegram-status")
def debug_telegram_status():
    """Debug endpoint to check Telegram bot status."""
    global deriv
    if deriv and deriv.telegram_bot:
        return jsonify({
            "telegram_status": {
                "bot_initialized": deriv.telegram_bot.bot is not None,
                "token_configured": bool(db.get_setting('telegram_bot_token')),
                "chat_id_configured": bool(db.get_setting('telegram_chat_id')),
                "notifications_enabled": db.get_setting('telegram_enabled') == 'true',
                "notification_interval": db.get_setting('telegram_notification_interval')
            }
        })
    else:
        return jsonify({"error": "Telegram bot not configured"}), 503

@app.route("/api/debug/test-telegram", methods=["POST"])
def debug_test_telegram():
    """Debug endpoint to test Telegram notification."""
    global deriv, main_loop
    if deriv and deriv.telegram_bot and deriv.telegram_bot.bot:
        try:
            # Create test tick data
            test_tick = {
                "symbol": "TEST",
                "quote": 1234.56,
                "bid": 1234.50,
                "ask": 1234.60,
                "timestamp": time.time()
            }
            
            # Send test notification using main loop
            if main_loop:
                future = asyncio.run_coroutine_threadsafe(
                    deriv.telegram_bot.send_message(f"""
📊 **Notificação de Teste**

**Símbolo:** {test_tick['symbol']}
**Quote:** {test_tick['quote']}
**Bid:** {test_tick['bid']}
**Ask:** {test_tick['ask']}
**Hora:** {time.strftime('%H:%M:%S')}

💰 **Saldo Atual:** {deriv.account_balance or 'N/A'} USD
                    """.strip()),
                    main_loop
                )
                # Wait for the result
                future.result(timeout=10)
            else:
                # Fallback: send directly
                deriv._send_telegram_notification(test_tick)
            
            return jsonify({
                "message": "Test Telegram notification sent",
                "test_data": test_tick
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Telegram bot not configured"}), 503



async def setup_services():
    """Initialize and connect the native Deriv client."""
    global deriv, main_loop
    async with deriv_lock:
        deriv = NativeDerivClient()
        
        # Set up frontend callback
        deriv.set_frontend_callback(broadcast_tick_update)
        
        # Set up main loop for async operations
        deriv.set_main_loop(main_loop)
        
        # Set up Telegram bot for notifications
        from utils.telegram_bot import TelegramBot
        telegram_bot = TelegramBot()
        deriv.set_telegram_bot(telegram_bot)
        
        # Connect to WebSocket instead of authenticate
        connected = await deriv.connect()
        if not connected:
            raise Exception("Failed to connect to Deriv WebSocket")
        return deriv

async def send_telegram_notification(bot, deriv):
    """Send a notification with the current balance via Telegram."""
    if not bot or not bot.bot:
        print("⚠️ Telegram bot not available for notifications")
        return
    
    try:
        balance = await deriv.get_balance()
        success = await bot.send_message(f"Saldo Atual: {balance} USD")
        if success:
            print("✅ Telegram notification sent successfully")
        else:
            print("❌ Failed to send Telegram notification")
    except Exception as e:
        print(f"❌ Error sending Telegram notification: {e}")

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
        
        # Start Flask API server in a separate thread
        server_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False))
        server_thread.daemon = True
        server_thread.start()
        
        print("🚀 Deriv Bot API running at http://0.0.0.0:5001")
        print("📊 Frontend should be running at http://localhost:5173")
        print("🤖 Telegram notifications enabled")
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
