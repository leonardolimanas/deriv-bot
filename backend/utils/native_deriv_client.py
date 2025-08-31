import asyncio
import json
import time
import websockets
import logging
from typing import Optional, List, Dict, Any, Callable

# Configure logging
logger = logging.getLogger(__name__)

class NativeDerivClient:
    def __init__(self, app_id: str = None):
        # Import config here to avoid circular imports
        from utils.config import DERIV_APP_ID, DERIV_API_TOKEN
        
        self.app_id = app_id or DERIV_APP_ID
        self.token = DERIV_API_TOKEN
        

        
        # Get notification interval from database
        from database import db
        self.telegram_notification_interval = int(db.get_setting('telegram_notification_interval') or 30)
        self.websocket = None
        self.is_connected = False
        self.account_balance = None
        self.account_currency = None
        self.account_type = None
        self.login_id = None
        self.account_details = None
        self.active_symbols = []
        self.latest_ticks = []
        self.max_ticks = 1000
        self.current_symbol = None
        self.subscription_id = None
        self.tick_stream_available = False
        self.last_tick_time = time.time()
        
        # Callback for frontend updates
        self.frontend_callback: Optional[Callable] = None
        
        # Telegram bot for notifications
        self.telegram_bot = None
        self.last_telegram_notification = 0
        
        # WebSocket URL
        self.ws_url = "wss://ws.binaryws.com/websockets/v3?app_id=" + self.app_id

    def set_frontend_callback(self, callback: Callable):
        """Set callback function for frontend updates."""
        self.frontend_callback = callback
        logger.info("Frontend callback set")

    def set_telegram_bot(self, telegram_bot):
        """Set Telegram bot for notifications."""
        self.telegram_bot = telegram_bot
        logger.info("Telegram bot set for notifications")

    def set_main_loop(self, main_loop):
        """Set main event loop for async operations."""
        self.main_loop = main_loop
        logger.info("Main loop set for async operations")

    async def connect(self):
        """Connect to Deriv WebSocket API."""
        try:
            logger.info(f"🔌 Connecting to Deriv WebSocket: {self.ws_url}")
            self.websocket = await websockets.connect(self.ws_url)
            self.is_connected = True
            logger.info("✅ WebSocket connected successfully")
            
            # Start message handler
            asyncio.create_task(self._handle_messages())
            
            # Authorize connection
            await self._authorize()
            
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect: {e}")
            self.is_connected = False
            return False

    async def _authorize(self):
        """Authorize the connection."""
        if self.token:
            request = {
                "authorize": self.token
            }
        else:
            request = {
                "authorize": self.app_id
            }
        
        success = await self.send_request(request)
        if not success:
            logger.error("❌ Failed to send authorization request")

    async def _handle_messages(self):
        """Handle incoming WebSocket messages."""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._process_message(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding message: {e}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
            self.is_connected = False
        except Exception as e:
            logger.error(f"Message handler error: {e}")
            self.is_connected = False

    async def _process_message(self, data):
        """Process incoming messages."""
        msg_type = data.get("msg_type")
        
        if msg_type == "tick":
            await self._handle_tick(data)
        elif msg_type == "active_symbols":
            await self._handle_active_symbols(data)
        elif msg_type == "balance":
            await self._handle_balance(data)
        elif msg_type == "authorize":
            await self._handle_authorize(data)
        elif msg_type == "get_account_details":
            await self._handle_account_details(data)
        elif "error" in data:
            logger.error(f"API Error: {data['error']}")
        else:
            logger.debug(f"Unhandled message type: {msg_type}")

    async def _handle_tick(self, data):
        """Handle tick data."""
        tick_data = data.get("tick", {})
        
        if tick_data:
            # Convert epoch to timestamp if present
            if "epoch" in tick_data:
                tick_data["timestamp"] = int(tick_data["epoch"])
            elif "timestamp" not in tick_data:
                tick_data["timestamp"] = int(time.time())
            
            # Ensure required fields are present
            if "quote" not in tick_data:
                logger.warning("⚠️ Tick missing quote field, skipping")
                return
            
            # Set default values for optional fields
            if "bid" not in tick_data:
                tick_data["bid"] = tick_data["quote"]
            if "ask" not in tick_data:
                tick_data["ask"] = tick_data["quote"]
            
            # Update tick stream status
            self.tick_stream_available = True
            self.last_tick_time = time.time()
            
            # Store subscription ID if present
            if "subscription" in data and "id" in data["subscription"]:
                self.subscription_id = data["subscription"]["id"]
            
            # Add symbol to tick data if not present
            if "symbol" not in tick_data and self.current_symbol:
                tick_data["symbol"] = self.current_symbol
            
            # Add all ticks but mark if they're from the subscribed symbol
            tick_data["is_subscribed_symbol"] = (self.current_symbol and tick_data.get("symbol") == self.current_symbol)
            
            # Add to latest ticks
            self.latest_ticks.append(tick_data)
            if len(self.latest_ticks) > self.max_ticks:
                self.latest_ticks = self.latest_ticks[-self.max_ticks:]
            
            # Log tick received (reduced for performance)
            # Tick data received
            
            # Send Telegram notification
            self._send_telegram_notification(tick_data)
            
            # Trigger real-time update to frontend via callback
            self._trigger_frontend_update()
            


    def _trigger_frontend_update(self):
        """Trigger real-time update to frontend via callback."""
        try:
            # Get current ticks data
            ticks_data = self.get_latest_ticks()
            
            # Call frontend callback if set
            if self.frontend_callback:
                self.frontend_callback(ticks_data)
            else:
                logger.warning("⚠️ No frontend callback set")
                
        except Exception as e:
            logger.error(f"Error triggering frontend update: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

    def _send_telegram_notification(self, tick_data):
        """Send Telegram notification for new tick."""
        try:
            # Check if Telegram notifications are enabled
            from database import db
            telegram_enabled = db.get_setting('telegram_enabled')
            if telegram_enabled != 'true':
                # Telegram notifications disabled
                return
            
            if self.telegram_bot and self.telegram_bot.bot:
                # Check if enough time has passed since last notification
                current_time = time.time()
                if current_time - self.last_telegram_notification < self.telegram_notification_interval:
                    # Skipping Telegram notification (throttled)
                    return
                
                # Format the message
                symbol = tick_data.get('symbol', 'Unknown')
                quote = tick_data.get('quote', 'N/A')
                bid = tick_data.get('bid', 'N/A')
                ask = tick_data.get('ask', 'N/A')
                timestamp = tick_data.get('timestamp', time.time())
                
                # Convert timestamp to readable format
                time_str = time.strftime('%H:%M:%S', time.localtime(timestamp))
                
                message = f"""
📊 **Novo Tick Recebido**

**Símbolo:** {symbol}
**Quote:** {quote}
**Bid:** {bid}
**Ask:** {ask}
**Hora:** {time_str}

💰 **Saldo Atual:** {self.account_balance or 'N/A'} USD
                """.strip()
                
                # Send message using the main loop if available
                if hasattr(self, 'main_loop') and self.main_loop:
                    try:
                        future = asyncio.run_coroutine_threadsafe(
                            self.telegram_bot.send_message(message), 
                            self.main_loop
                        )
                        # Add callback to log success
                        def on_complete(future):
                            try:
                                future.result()  # This will raise any exception
                                logger.info(f"📱 Telegram notification sent for {symbol}")
                            except Exception as e:
                                logger.error(f"Error in Telegram notification: {e}")
                        
                        future.add_done_callback(on_complete)
                    except Exception as e:
                        logger.error(f"Error scheduling Telegram message: {e}")
                else:
                    logger.warning("📱 No main loop available for Telegram notification")
                
                self.last_telegram_notification = current_time
            else:
                # No Telegram bot configured for notifications
                pass
                
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

    async def _handle_active_symbols(self, data):
        """Handle active symbols response."""
        if "active_symbols" in data:
            self.active_symbols = data["active_symbols"]
            logger.info(f"Received {len(self.active_symbols)} active symbols")
    
    async def _handle_balance(self, data):
        """Handle balance response."""
        if "balance" in data:
            balance_data = data["balance"]
            if "balance" in balance_data:
                self.account_balance = balance_data["balance"]
                logger.info(f"Account balance: {self.account_balance}")
            else:
                logger.warning("Balance data structure unexpected")
        else:
            logger.warning("No balance data in response")
    
    async def _handle_account_details(self, data):
        """Handle account details response."""
        if "get_account_details" in data:
            self.account_details = data["get_account_details"]
            logger.info("Account details updated")
        else:
            logger.warning("No account details in response")
    

    
    async def _handle_authorize(self, data):
        """Handle authorization response."""
        if "error" in data:
            logger.error(f"Authorization failed: {data['error']}")
            return False
        
        if "authorize" in data:
            auth_data = data["authorize"]
            
            # Extract account information
            if "balance" in auth_data:
                self.account_balance = auth_data["balance"]
            
            if "currency" in auth_data:
                self.account_currency = auth_data["currency"]
            
            if "account_type" in auth_data:
                self.account_type = auth_data["account_type"]
            
            if "loginid" in auth_data:
                self.login_id = auth_data["loginid"]
            
            # Store complete account details
            self.account_details = auth_data
            
            logger.info(f"✅ Authorization successful. Balance: {self.account_balance} {self.account_currency}")
            return True
        else:
            logger.warning("Unexpected authorization response format")
            return False
    
    async def send_request(self, request):
        """Send a request to the API."""
        if not self.is_connected or not self.websocket:
            await self.connect()
        
        try:
            await self.websocket.send(json.dumps(request))
            return True
        except Exception as e:
            logger.error(f"❌ Failed to send request: {e}")
            return False
    
    async def get_active_symbols(self):
        """Get active symbols."""
        request = {
            "active_symbols": "brief",
            "product_type": "basic"
        }
        
        success = await self.send_request(request)
        if success:
            # Wait a bit for response and retry if needed
            for _ in range(5):  # Try up to 5 times
                await asyncio.sleep(1)
                if self.active_symbols:
                    # Sort by market and then by symbol name for better organization
                    self.active_symbols.sort(key=lambda x: (x.get("market", ""), x.get("display_name", "")))
                    
                    # Add a field to indicate which symbols are likely to have tick streams
                    for symbol in self.active_symbols:
                        market_type = symbol.get("market", "").lower()
                        symbol_code = symbol.get("symbol", "").lower()
                        
                        # Forex, major indices, and commodities usually have tick streams
                        if (market_type in ["forex", "indices", "commodities"] or 
                            any(prefix in symbol_code for prefix in ["frx", "r_", "wld", "1hZ"])):
                            symbol["has_tick_stream"] = True
                        else:
                            symbol["has_tick_stream"] = False
                    
                    return self.active_symbols
            
            # If we still don't have symbols, return empty list
            return []
        return []
    
    async def get_balance(self):
        """Get account balance."""
        # If we already have a balance from authorization, return it
        if self.account_balance is not None:
            return self.account_balance
        
        request = {
            "balance": 1
        }
        
        success = await self.send_request(request)
        if success:
            # Wait for response
            await asyncio.sleep(1)
            # The balance will be handled in _process_message
            return self.account_balance or 0
        else:
            logger.error("❌ Failed to send balance request")
            return 0
    
    async def get_account_details(self):
        """Get detailed account information."""
        request = {
            "get_account_details": 1
        }
        
        success = await self.send_request(request)
        if success:
            await asyncio.sleep(1)
            return self.account_details
        return {}
    

    
    async def subscribe_to_ticks(self, symbol):
        """Subscribe to tick updates for a specific symbol."""
        # Unsubscribe from any existing subscription
        await self.unsubscribe_from_ticks()
        
        # Clear previous ticks and set new symbol
        self.latest_ticks = []
        self.current_symbol = symbol
        self.tick_stream_available = False
        self.last_tick_time = time.time()
        
        logger.info(f"🔄 Switching to symbol: {symbol}")
        
        request = {
            "ticks": symbol,
            "subscribe": 1
        }
        
        success = await self.send_request(request)
        if success:
            logger.info(f"✅ Subscribed to ticks for {symbol}")
            return {"status": "subscribed", "symbol": symbol}
        else:
            logger.error(f"❌ Failed to subscribe to {symbol}")
            return {"status": "error", "message": f"Failed to subscribe to {symbol}"}
    
    async def unsubscribe_from_ticks(self):
        """Unsubscribe from current tick subscription."""
        logger.info(f"🔄 Starting unsubscribe process...")
        
        if self.subscription_id:
            logger.info(f"🔄 Unsubscribing from subscription ID: {self.subscription_id}")
            request = {
                "forget": self.subscription_id
            }
            success = await self.send_request(request)
            if success:
                logger.info(f"✅ Successfully unsubscribed from {self.subscription_id}")
            else:
                logger.error(f"❌ Failed to unsubscribe from {self.subscription_id}")
            self.subscription_id = None
        else:
            logger.warning("⚠️ No subscription ID found to unsubscribe")
        
        # Clear current symbol and ticks
        if self.current_symbol:
            logger.info(f"🔄 Clearing symbol: {self.current_symbol}")
        
        self.current_symbol = None
        self.latest_ticks = []
        self.tick_stream_available = False
        logger.info("🧹 Cleared all ticks and reset stream status")
        return {"status": "unsubscribed"}
    
    def get_latest_ticks(self):
        """Get the latest ticks."""
        try:
            # Check if the tick stream is still active
            if self.current_symbol and time.time() - self.last_tick_time > 10:
                self.tick_stream_available = False
            
            # Get max ticks display setting from database
            from database import db
            max_ticks_display = int(db.get_setting('max_ticks_display') or 100)
            
            # Filter ticks for current symbol only
            if self.current_symbol:
                filtered_ticks = [tick for tick in self.latest_ticks if tick.get('symbol') == self.current_symbol]
                filtered_ticks = filtered_ticks[-max_ticks_display:] if filtered_ticks else []
            else:
                filtered_ticks = self.latest_ticks[-max_ticks_display:] if self.latest_ticks else []
            
            # Log tick count for debug (reduced)
            if filtered_ticks:
                logger.debug(f"🔍 {self.current_symbol}: {len(filtered_ticks)} ticks")
            
            return {
                "symbol": self.current_symbol,
                "ticks": filtered_ticks,
                "available": self.tick_stream_available,
                "connection_status": "connected" if self.is_connected else "disconnected",
                "last_update": self.last_tick_time
            }
        except Exception as e:
            logger.error(f"Error in get_latest_ticks: {e}")
            return {
                "symbol": None,
                "ticks": [],
                "available": False,
                "connection_status": "error",
                "error": str(e)
            }
    
    async def close(self):
        """Close the WebSocket connection."""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            logger.info("WebSocket connection closed")