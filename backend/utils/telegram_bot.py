from aiogram import Bot, Dispatcher, types  
from aiogram.types import BotCommand  
from utils.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from database import db

class TelegramBot:  
    def __init__(self):  
        # Get token from database or use default
        token = db.get_setting('telegram_bot_token') or TELEGRAM_BOT_TOKEN
        
        # Validate token
        if not token or token.strip() == '':
            self.bot = None
            self.dp = None
            print("⚠️ Telegram bot token not configured")
            return
        
        try:
            self.bot = Bot(token=token)  
            self.dp = Dispatcher()
            print("✅ Telegram bot initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing Telegram bot: {e}")
            self.bot = None
            self.dp = None

    async def send_message(self, message):  
        if not self.bot:
            print("⚠️ Telegram bot not initialized")
            return False
        
        try:
            # Get chat ID from database or use default
            chat_id = db.get_setting('telegram_chat_id') or TELEGRAM_CHAT_ID
            
            if not chat_id or chat_id.strip() == '':
                print("⚠️ Telegram chat ID not configured")
                return False
            
            await self.bot.send_message(chat_id=chat_id, text=message)
            return True
        except Exception as e:
            print(f"❌ Error sending Telegram message: {e}")
            return False
        
    async def close(self):
        """Close the bot session and release resources."""
        if not self.bot:
            return
            
        try:
            # In aiogram v3, we need to close the bot session
            if hasattr(self.bot, 'session') and hasattr(self.bot.session, 'close'):
                await self.bot.session.close()
            elif hasattr(self.bot, 'close'):
                await self.bot.close()
        except Exception as e:
            print(f"Error closing Telegram bot session: {e}")