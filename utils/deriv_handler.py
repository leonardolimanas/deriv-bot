from deriv_api import DerivAPI  
from utils.config import DERIV_API_TOKEN, DERIV_APP_ID  
import asyncio
import time

class DerivHandler:  
    def __init__(self):  
        self.api = DerivAPI(app_id=DERIV_APP_ID)
        self.active_symbols = []
        self.tick_subscription = None
        self.subscription_callback = None
        self.latest_ticks = []
        self.max_ticks = 50  # Store up to 50 latest ticks
        self.current_symbol = None
        self.tick_stream_available = False
        self.last_tick_time = 0
        self.tick_timeout = 10  # Consider stream dead if no ticks for 10 seconds

    async def authenticate(self):  
        response = await self.api.authorize(DERIV_API_TOKEN)  
        return response  

    async def get_balance(self):  
        response = await self.api.balance()  
        return response.get("balance", {}).get("balance", 0)
    
    async def get_active_symbols(self):
        """Get list of active symbols/markets."""
        try:
            # Always fetch fresh data to ensure we have the latest available markets
            request = {
                "active_symbols": "brief",
                "product_type": "basic"
            }
            response = await self.api.send(request)
            if "active_symbols" in response:
                self.active_symbols = response["active_symbols"]
                # Sort by market and then by symbol name for better organization
                self.active_symbols.sort(key=lambda x: (x.get("market", ""), x.get("display_name", "")))
                
                # Add a field to indicate which symbols are likely to have tick streams
                # Based on common patterns, most forex, indices, and commodities have tick streams
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
        except Exception as e:
            print(f"Error fetching active symbols: {e}")
            return self.active_symbols or []
    
    async def subscribe_to_ticks(self, symbol):
        """Subscribe to tick updates for a specific symbol."""
        # Unsubscribe from any existing subscription
        await self.unsubscribe_from_ticks()
        
        # Clear previous ticks
        self.latest_ticks = []
        self.current_symbol = symbol
        self.tick_stream_available = False
        self.last_tick_time = time.time()
        
        # Create a new subscription
        request = {
            "ticks": symbol,
            "subscribe": 1
        }
        
        try:
            # Subscribe to ticks with a callback function
            observable = await self.api.subscribe(request)
            
            # Define the callback function to process ticks
            def process_tick(response):
                if "tick" in response:
                    tick = response["tick"]
                    # Add timestamp if not present
                    if "timestamp" not in tick:
                        tick["timestamp"] = int(time.time())
                    
                    # Update tick stream status
                    self.tick_stream_available = True
                    self.last_tick_time = time.time()
                    
                    # Add to latest ticks, keeping only the most recent ones
                    self.latest_ticks.append(tick)
                    if len(self.latest_ticks) > self.max_ticks:
                        self.latest_ticks = self.latest_ticks[-self.max_ticks:]
                elif "error" in response:
                    print(f"Tick stream error for {symbol}: {response['error']['message']}")
                    self.tick_stream_available = False
            
            # Subscribe to the observable
            self.subscription_callback = observable.subscribe(
                on_next=process_tick,
                on_error=lambda error: self._handle_subscription_error(error, symbol),
                on_completed=lambda: print(f"Tick subscription completed for {symbol}")
            )
            
            # Store the observable for later unsubscription
            self.tick_subscription = observable
            
            # Start a background task to monitor for tick timeouts
            asyncio.create_task(self._monitor_tick_stream())
            
            return {"status": "subscribed", "symbol": symbol}
        except Exception as e:
            error_msg = str(e)
            print(f"Error subscribing to ticks for {symbol}: {error_msg}")
            
            # Provide more specific error messages
            if "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
                return {"status": "error", "message": f"Symbol {symbol} is not available for tick streaming", "code": "SYMBOL_NOT_FOUND"}
            elif "not authorized" in error_msg.lower() or "permission" in error_msg.lower():
                return {"status": "error", "message": "You are not authorized to access this market", "code": "UNAUTHORIZED"}
            else:
                return {"status": "error", "message": f"Failed to subscribe to {symbol}: {error_msg}", "code": "SUBSCRIPTION_FAILED"}
    
    def _handle_subscription_error(self, error, symbol):
        """Handle errors from the tick subscription."""
        print(f"Tick subscription error for {symbol}: {error}")
        self.tick_stream_available = False
    
    async def _monitor_tick_stream(self):
        """Monitor the tick stream and mark it as unavailable if no ticks are received for a while."""
        while self.tick_subscription:
            await asyncio.sleep(1)
            
            # Check if we've received any ticks recently
            if time.time() - self.last_tick_time > self.tick_timeout:
                if self.tick_stream_available:
                    print(f"Tick stream timeout for {self.current_symbol}")
                    self.tick_stream_available = False
            
            # If we haven't received any ticks after 30 seconds, consider the stream dead
            if time.time() - self.last_tick_time > 30 and self.latest_ticks == []:
                print(f"No ticks received for {self.current_symbol}, stream appears to be unavailable")
                self.tick_stream_available = False
                # Add a dummy tick to indicate the stream is unavailable
                self.latest_ticks.append({
                    "timestamp": int(time.time()),
                    "symbol": self.current_symbol,
                    "status": "unavailable",
                    "message": "This market does not provide real-time tick data"
                })
                # Stop monitoring
                break
    
    async def unsubscribe_from_ticks(self):
        """Unsubscribe from current tick subscription."""
        if self.subscription_callback:
            try:
                # Unsubscribe from the observable
                self.subscription_callback.dispose()
                self.subscription_callback = None
            except Exception as e:
                print(f"Error disposing subscription callback: {e}")
        
        self.tick_subscription = None
        self.current_symbol = None
        self.tick_stream_available = False
        return {"status": "unsubscribed"}
    
    def get_latest_ticks(self):
        """Get the latest ticks."""
        # Check if the tick stream is still active
        if self.current_symbol and time.time() - self.last_tick_time > self.tick_timeout:
            self.tick_stream_available = False
        
        return {
            "symbol": self.current_symbol,
            "ticks": self.latest_ticks,
            "available": self.tick_stream_available
        }
        
    async def close(self):
        """Close the API connection and release resources."""
        try:
            # Unsubscribe from any active subscriptions
            await self.unsubscribe_from_ticks()
            
            # Try different common method names for closing connections
            if hasattr(self.api, 'close'):
                await self.api.close()
            elif hasattr(self.api, 'disconnect'):
                await self.api.disconnect()
            elif hasattr(self.api, 'shutdown'):
                await self.api.shutdown()
        except Exception as e:
            print(f"Error closing Deriv API connection: {e}")