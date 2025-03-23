from aiogram import Bot, Dispatcher, types  
from aiogram.types import BotCommand  
from utils.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

class TelegramBot:  
    def __init__(self):  
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)  
        self.dp = Dispatcher()

    async def send_message(self, message):  
        await self.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        
    async def close(self):
        """Close the bot session and release resources."""
        try:
            # In aiogram v3, we need to close the bot session
            if hasattr(self.bot, 'session') and hasattr(self.bot.session, 'close'):
                await self.bot.session.close()
            elif hasattr(self.bot, 'close'):
                await self.bot.close()
        except Exception as e:
            print(f"Error closing Telegram bot session: {e}")