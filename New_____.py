from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from controller import request,response

class   PlayerView:
    def __init__(self,token):
        self.updater = Updater(token=token)
        self.dispatcher = self.updater.dispatcher
        
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        
        self.dispatcher.add_handler(CallbackQueryHandler(self.button_pressed))
        
    def request(self,request, update, context):
        self.request=request
        update.message.reply_text(text=request)
        
    def response(self,response, update, context):
        self.response=response
        keyboard = []
        for i in range(1,self.y+1):
            keyboard.append([InlineKeyboardButton(f"Option {i}", callback_data=f"{i}")])
        reply_markup=InlineKeyboardMarkup(keyboard)
        update.message.reply_text(response, reply_markup=reply_markup)
        
    def button_pressed(self, update, context):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text=f'Нажата кнопка: {query.data}, вы выбрали тототото')
        
    def start(self, update, context):
        update.message.reply_text('проверка звука')
        
    def run(self):
        self.updater.start_polling()
        self.updater.idle()
        
console_view = ConsoleView("6357433531:AAHzxBRRtQpni7aFLcjRcbh2FFRxyFSIr0o")

console_view.run()
