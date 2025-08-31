import os
from datetime import timedelta

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')
    
    # Deriv API Configuration
    DERIV_API_TOKEN = os.environ.get('DERIV_API_TOKEN')
    DERIV_APP_ID = os.environ.get('DERIV_APP_ID', '67203')
    DERIV_API_TOKEN_REAL = os.environ.get('DERIV_API_TOKEN_REAL')
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
    
    # API Configuration
    API_TITLE = 'Deriv Bot API'
    API_VERSION = 'v1'
    API_DESCRIPTION = 'Trading bot API for Deriv platform'
    
    # Rate Limiting
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/deriv_bot.log'
    
    # Cache Configuration
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # Security
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    
    # Development-specific settings
    CORS_ORIGINS = ['http://localhost:5173', 'http://127.0.0.1:5173', 'http://localhost:5174']
    
    # Use demo tokens for development if not provided
    DERIV_API_TOKEN = os.environ.get('DERIV_API_TOKEN', 'zROkbTwuOHdTIIw')
    DERIV_API_TOKEN_REAL = os.environ.get('DERIV_API_TOKEN_REAL', 'av7RmoC7wwtUFNT')
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '7467682243:AAHs7tUE1oi0VzbE3N62z9muDhfnA9s0M4w')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '-4716814208')

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    
    # Production-specific settings
    SESSION_COOKIE_SECURE = True
    LOG_LEVEL = 'WARNING'
    
    # Require environment variables in production
    @classmethod
    def validate_config(cls):
        required_vars = [
            'DERIV_API_TOKEN',
            'DERIV_API_TOKEN_REAL',
            'TELEGRAM_BOT_TOKEN',
            'TELEGRAM_CHAT_ID',
            'SECRET_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    
    # Use test tokens
    DERIV_API_TOKEN = 'test_token'
    DERIV_API_TOKEN_REAL = 'test_real_token'
    TELEGRAM_BOT_TOKEN = 'test_bot_token'
    TELEGRAM_CHAT_ID = 'test_chat_id'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
