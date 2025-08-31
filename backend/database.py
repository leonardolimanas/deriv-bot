import sqlite3
import os
from typing import Dict, Any, Optional

class Database:
    def __init__(self, db_path: str = "deriv_bot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert default settings
            default_settings = [
                # Interface settings
                ('show_debug_panel', 'true', 'Exibir painel de debug no dashboard'),
                ('auto_refresh_interval', '5000', 'Intervalo de atualização automática (ms)'),
                ('max_ticks_display', '100', 'Número máximo de ticks exibidos na tabela'),
                ('enable_notifications', 'true', 'Habilitar notificações'),
                ('theme', 'dark', 'Tema da interface (dark/light)'),
                
                # Telegram settings
                ('telegram_enabled', 'true', 'Habilitar notificações do Telegram'),
                ('telegram_notification_interval', '30', 'Intervalo entre notificações do Telegram (segundos)'),
                ('telegram_bot_token', '7467682243:AAHs7tUE1oi0VzbE3N62z9muDhfnA9s0M4w', 'Token do bot do Telegram'),
                ('telegram_chat_id', '-4716814208', 'ID do chat do Telegram'),
                
                # Deriv API settings
                ('deriv_app_id', '67203', 'ID da aplicação Deriv'),
                ('deriv_api_token', 'zROkbTwuOHdTIIw', 'Token da API Deriv'),
                ('deriv_api_token_real', 'av7RmoC7wwtUFNT', 'Token real da API Deriv'),
                
                # Market settings
                ('default_market', 'R_100', 'Ativo selecionado por padrão no dashboard')
            ]
            
            for key, value, description in default_settings:
                cursor.execute('''
                    INSERT OR IGNORE INTO user_settings (key, value, description)
                    VALUES (?, ?, ?)
                ''', (key, value, description))
            
            conn.commit()
    
    def get_setting(self, key: str) -> Optional[str]:
        """Get a setting value by key."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM user_settings WHERE key = ?', (key,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def set_setting(self, key: str, value: str, description: str = None):
        """Set a setting value."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if description:
                cursor.execute('''
                    INSERT OR REPLACE INTO user_settings (key, value, description, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (key, value, description))
            else:
                cursor.execute('''
                    UPDATE user_settings 
                    SET value = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE key = ?
                ''', (value, key))
            conn.commit()
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings as a dictionary."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT key, value, description FROM user_settings')
            settings = {}
            for row in cursor.fetchall():
                key, value, description = row
                # Convert string values to appropriate types
                if value.lower() in ('true', 'false'):
                    settings[key] = value.lower() == 'true'
                elif value.isdigit():
                    settings[key] = int(value)
                else:
                    settings[key] = value
            return settings
    
    def delete_setting(self, key: str):
        """Delete a setting."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM user_settings WHERE key = ?', (key,))
            conn.commit()

# Global database instance
db = Database()
