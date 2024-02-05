from telegram import InlineKeyboardButton, update, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from view.player_view import PlayerView


#Класс, описывающий выввод и ввод в ТГ боте
class TelegramView(PlayerView):

    def __init__(self, update: Update=None):
        self.__update = update

    def request(self, num=10):
        keyboard = []
        for i in range(1, num):
            keyboard.append([InlineKeyboardButton(f"{i}", callback_data=f"{i}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        self.__update.message.reply_text('Выберите номер ответа:', reply_markup=reply_markup)

    def response(self, text):
        if text != '':
            self.__update.message.reply_text(text)
            print(text)