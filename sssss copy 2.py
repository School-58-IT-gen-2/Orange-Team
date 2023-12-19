import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

class TelegramView():
    def __init__(self,y=0,text=''):
        self.updater = Updater("6357433531:AAHzxBRRtQpni7aFLcjRcbh2FFRxyFSIr0o", use_context=True)
        self.dispatcher = self.updater.dispatcher
        start_handler =CommandHandler('start', self.start)
        request_handler = CommandHandler('request',self.request)
        request_handler = CommandHandler('response',self.response)
        response_handler=CallbackQueryHandler(self.response)
        self.dispatcher.add_handler(start_handler)  
        self.dispatcher.add_handler(request_handler)
        self.dispatcher.add_handler(response_handler)
        self.y=y
        self.text=text
        
    def start(self,update, _):
        update.message.reply_text(
            'Введите `/request`,`/response` для участия в бою,' 
        )   
    def request(self,update: Update, context: CallbackContext) -> None:
        user_id = update.effective_chat.id                
        context.bot.send_message(chat_id=user_id, text=self.text)
    def response(self,update: Update, context: CallbackContext) -> None:
        keyboard = []  
        for i in range(1,self.y+1):
            keyboard.append([InlineKeyboardButton(f"Option {i}", callback_data=f"{i}")])
                    
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Please choose an action:', reply_markup=reply_markup)
        query = update.callback_query
        query.answer()      
        if query.data=='1':
            print('You killed with a car')
                        
        if query.data=='2':
            print('You killed with a book')
                                
        if query.data=='3':
            print('You killed with a laptop')
bot = TelegramView(y=6,text='PEpe') 
bot.updater.start_polling()