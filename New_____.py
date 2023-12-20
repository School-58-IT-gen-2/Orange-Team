import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
class Pepe():
    def __init__(self,x='ddd'):
        self.x=x
    def dey(self):
        if True:
            return self.x
class TelegramView(Pepe):
    def __init__(self):
        self.updater = Updater("6357433531:AAHzxBRRtQpni7aFLcjRcbh2FFRxyFSIr0o", use_context=True)
        self.dispatcher = self.updater.dispatcher  
    def request(self,update: Update, context: CallbackContext) -> None:
        user_id = update.effective_chat.id                
        context.bot.send_message(chat_id=user_id, text=self.x)
result = Pepe(x='dsdsd') 
bot = result.request()
bot.updater.start_polling()

