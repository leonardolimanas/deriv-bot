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
    DERIV_API_TOKEN = os.environ.get('DERIV_API_TOKEN', 'your_deriv_api_token_here')
    DERIV_API_TOKEN_REAL = os.environ.get('DERIV_API_TOKEN_REAL', 'your_deriv_real_token_here')
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'your_telegram_bot_token_here')
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', 'your_telegram_chat_id_here')

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
