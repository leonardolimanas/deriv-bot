import os
from database import db

def get_config_value(key: str, default: str = "") -> str:
    """Get configuration value from database or environment variable."""
    # First try database
    db_value = db.get_setting(key)
    if db_value is not None:
        return str(db_value)
    
    # Fallback to environment variable
    env_key = key.upper()
    env_value = os.getenv(env_key)
    if env_value is not None:
        return env_value
    
    # Final fallback to default
    return default

# Configurações da API Deriv  
DERIV_API_TOKEN = get_config_value("deriv_api_token", "zROkbTwuOHdTIIw")
DERIV_APP_ID = get_config_value("deriv_app_id", "67203")  
DERIV_API_TOKEN_REAL = get_config_value("deriv_api_token_real", "av7RmoC7wwtUFNT")

# Configurações do Telegram  
TELEGRAM_BOT_TOKEN = get_config_value("telegram_bot_token", "7467682243:AAHs7tUE1oi0VzbE3N62z9muDhfnA9s0M4w")
TELEGRAM_CHAT_ID = get_config_value("telegram_chat_id", "-4716814208")