from deriv_api import DerivAPI
from flask import current_app
import asyncio
import time
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class DerivService:
    """Service for handling Deriv API operations."""
    
    def __init__(self):
        self.api = None
        self.active_symbols = []
        self.tick_subscription = None
        self.subscription_callback = None
        self.latest_ticks = []
        self.max_ticks = 1000
        self.current_symbol = None
        self.tick_stream_available = False
        self.last_tick_time = 0
        self.tick_timeout = 10
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the Deriv API connection."""
        try:
            app_id = current_app.config['DERIV_APP_ID']
            self.api = DerivAPI(app_id=app_id)
            
            # Authenticate
            token = current_app.config['DERIV_API_TOKEN']
            response = await self.api.authorize(token)
            
            if response.get('error'):
                raise Exception(f"Authentication failed: {response['error']['message']}")
            
            self.is_initialized = True
            logger.info("Deriv API initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Deriv API: {e}")
            raise
    
    async def get_balance(self) -> float:
        """Get account balance."""
        if not self.is_initialized:
            raise Exception("Service not initialized")
        
        try:
            response = await self.api.balance()
            balance = response.get("balance", {}).get("balance", 0)
            logger.debug(f"Balance retrieved: {balance}")
            return balance
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            raise
    
    async def get_timestamp(self) -> int:
        """Get current timestamp."""
        return int(time.time())
    
    async def get_active_symbols(self) -> List[Dict]:
        """Get list of active symbols/markets."""
        if not self.is_initialized:
            raise Exception("Service not initialized")
        
        try:
            # Fetch detailed market information
            request = {
                "active_symbols": "full",
                "product_type": "basic"
            }
            response = await self.api.send(request)
            
            if "active_symbols" in response:
                self.active_symbols = response["active_symbols"]
                # Sort by market and symbol name
                self.active_symbols.sort(key=lambda x: (x.get("market", ""), x.get("display_name", "")))
                
                # Add tick stream availability and process additional info
                for symbol in self.active_symbols:
                    market_type = symbol.get("market", "").lower()
                    symbol_code = symbol.get("symbol", "").lower()
                    
                    # Determine if symbol has tick stream
                    if (market_type in ["forex", "indices", "commodities"] or 
                        any(prefix in symbol_code for prefix in ["frx", "r_", "wld", "1hZ"])):
                        symbol["has_tick_stream"] = True
                    else:
                        symbol["has_tick_stream"] = False
                    
                    # Process additional market information
                    # Ensure numeric values are properly typed
                    if "pip" in symbol:
                        symbol["pip"] = float(symbol["pip"]) if symbol["pip"] else None
                    if "min_stake" in symbol:
                        symbol["min_stake"] = float(symbol["min_stake"]) if symbol["min_stake"] else None
                    if "max_stake" in symbol:
                        symbol["max_stake"] = float(symbol["max_stake"]) if symbol["max_stake"] else None
                    if "spot" in symbol:
                        symbol["spot"] = float(symbol["spot"]) if symbol["spot"] else None
                
                logger.info(f"Retrieved {len(self.active_symbols)} active symbols")
                return self.active_symbols
            else:
                logger.warning("No active symbols in response")
                return self.active_symbols or []
                
        except Exception as e:
            logger.error(f"Error fetching active symbols: {e}")
            return self.active_symbols or []
    
    async def subscribe_to_ticks(self, symbol: str) -> Dict:
        """Subscribe to tick updates for a specific symbol."""
        if not self.is_initialized:
            raise Exception("Service not initialized")
        
        # Unsubscribe from any existing subscription
        await self.unsubscribe_from_ticks()
        
        # Clear previous ticks
        self.latest_ticks = []
        self.current_symbol = symbol
        self.tick_stream_available = False
        self.last_tick_time = time.time()
        
        # Create subscription
        request = {
            "ticks": symbol,
            "subscribe": 1
        }
        
        try:
            # Subscribe to ticks
            observable = await self.api.subscribe(request)
            
            # Define callback function
            def process_tick(response):
                if "tick" in response:
                    tick = response["tick"]
                    # Add timestamp if not present
                    if "timestamp" not in tick:
                        tick["timestamp"] = int(time.time())
                    
                    # Update status
                    self.tick_stream_available = True
                    self.last_tick_time = time.time()
                    
                    # Add to latest ticks
                    self.latest_ticks.append(tick)
                    if len(self.latest_ticks) > self.max_ticks:
                        self.latest_ticks = self.latest_ticks[-self.max_ticks:]
                    
                    # Detailed logging for debugging
                    logger.info(f"🔍 TICK DEBUG - Symbol: {symbol}")
                    logger.info(f"   Raw Response: {response}")
                    logger.info(f"   Tick Data: {tick}")
                    logger.info(f"   Quote: {tick.get('quote', 'N/A')}")
                    logger.info(f"   Bid: {tick.get('bid', 'N/A')}")
                    logger.info(f"   Ask: {tick.get('ask', 'N/A')}")
                    logger.info(f"   Epoch: {tick.get('epoch', 'N/A')}")
                    logger.info(f"   Pip Size: {tick.get('pip_size', 'N/A')}")
                    logger.info(f"   Tick Size: {tick.get('tick_size', 'N/A')}")
                    logger.info(f"   Timestamp: {tick.get('timestamp', 'N/A')}")
                    logger.info(f"   Local Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tick.get('timestamp', time.time())))}")
                    
                elif "error" in response:
                    logger.error(f"Tick stream error for {symbol}: {response['error']['message']}")
                    self.tick_stream_available = False
            
            # Subscribe to observable
            self.subscription_callback = observable.subscribe(
                on_next=process_tick,
                on_error=lambda error: self._handle_subscription_error(error, symbol),
                on_completed=lambda: logger.info(f"Tick subscription completed for {symbol}")
            )
            
            # Store observable
            self.tick_subscription = observable
            
            # Start monitoring
            asyncio.create_task(self._monitor_tick_stream())
            
            logger.info(f"Successfully subscribed to ticks for {symbol}")
            return {"status": "subscribed", "symbol": symbol}
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error subscribing to ticks for {symbol}: {error_msg}")
            
            # Provide specific error messages
            if "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
                return {"status": "error", "message": f"Symbol {symbol} is not available for tick streaming", "code": "SYMBOL_NOT_FOUND"}
            elif "not authorized" in error_msg.lower() or "permission" in error_msg.lower():
                return {"status": "error", "message": "You are not authorized to access this market", "code": "UNAUTHORIZED"}
            else:
                return {"status": "error", "message": f"Failed to subscribe to {symbol}: {error_msg}", "code": "SUBSCRIPTION_FAILED"}
    
    def _handle_subscription_error(self, error, symbol):
        """Handle errors from tick subscription."""
        logger.error(f"Tick subscription error for {symbol}: {error}")
        self.tick_stream_available = False
    
    async def _monitor_tick_stream(self):
        """Monitor tick stream for timeouts."""
        while self.tick_subscription:
            await asyncio.sleep(1)
            
            # Check for recent ticks
            if time.time() - self.last_tick_time > self.tick_timeout:
                if self.tick_stream_available:
                    logger.warning(f"Tick stream timeout for {self.current_symbol}")
                    self.tick_stream_available = False
            
            # Check for no ticks after 30 seconds
            if time.time() - self.last_tick_time > 30 and self.latest_ticks == []:
                logger.warning(f"No ticks received for {self.current_symbol}, stream appears unavailable")
                self.tick_stream_available = False
                # Add dummy tick
                self.latest_ticks.append({
                    "timestamp": int(time.time()),
                    "symbol": self.current_symbol,
                    "status": "unavailable",
                    "message": "This market does not provide real-time tick data"
                })
                break
    
    async def unsubscribe_from_ticks(self) -> Dict:
        """Unsubscribe from current tick subscription."""
        if self.subscription_callback:
            try:
                self.subscription_callback.dispose()
                self.subscription_callback = None
                logger.info("Successfully unsubscribed from tick stream")
            except Exception as e:
                logger.error(f"Error disposing subscription callback: {e}")
        
        self.tick_subscription = None
        self.current_symbol = None
        self.tick_stream_available = False
        return {"status": "unsubscribed"}
    
    def get_latest_ticks(self) -> Dict:
        """Get the latest ticks."""
        # Check if stream is still active
        if self.current_symbol and time.time() - self.last_tick_time > self.tick_timeout:
            self.tick_stream_available = False
        
        return {
            "symbol": self.current_symbol,
            "ticks": self.latest_ticks,
            "available": self.tick_stream_available,
            "count": len(self.latest_ticks)
        }
    
    async def close(self):
        """Close the API connection."""
        try:
            await self.unsubscribe_from_ticks()
            
            if hasattr(self.api, 'close'):
                await self.api.close()
            elif hasattr(self.api, 'disconnect'):
                await self.api.disconnect()
            elif hasattr(self.api, 'shutdown'):
                await self.api.shutdown()
                
            logger.info("Deriv API connection closed")
        except Exception as e:
            logger.error(f"Error closing Deriv API connection: {e}")
