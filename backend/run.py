#!/usr/bin/env python3
"""
Deriv Bot - Main Application Entry Point
"""

import os
import sys
import asyncio
import threading
from app import create_app
from app.services.deriv_service import DerivService
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main application entry point."""
    try:
        # Determine configuration
        config_name = os.environ.get('FLASK_ENV', 'development')
        
        # Create Flask app
        app = create_app(config_name)
        
        # Initialize services
        with app.app_context():
            # Validate configuration in production
            if config_name == 'production':
                from config import ProductionConfig
                ProductionConfig.validate_config()
            
            logger.info(f"Starting Deriv Bot in {config_name} mode")
            
            # Start Flask ser`ve`r in a separate thread
            def run_flask():
                app.run(
                    host='0.0.0.0',
                    port=5001,
                    debug=app.config.get('DEBUG', False),
                    use_reloader=False
                )
            
            server_thread = threading.Thread(target=run_flask, daemon=True)
            server_thread.start()
            
            logger.info("🚀 Deriv Bot API running at http://0.0.0.0:5001")
            logger.info("📊 Frontend should be running at http://localhost:5173")
            logger.info("🤖 Telegram notifications enabled")
            logger.info("Press Ctrl+C to exit")
            
            # Keep main thread alive
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
