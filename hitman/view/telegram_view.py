from telegram import InlineKeyboardButton, update, InlineKeyboardMarkup, Update
from view.player_view import PlayerView


class TelegramView(PlayerView):

    def __init__(self, update: Update=None, bot=None):
        self.__update = update
        self.__bot = bot

    def request(self, num=10):
        keyboard = []
        for i in range(1, num):
            keyboard.append([InlineKeyboardButton(f"{i}", callback_data=f"{i}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        self.__update.message.reply_text('Выберите номер ответа:', reply_markup=reply_markup)
        query = self.__update.callback_query
        return query

    def response(self, text):
        self.__update.message.reply_text(text)