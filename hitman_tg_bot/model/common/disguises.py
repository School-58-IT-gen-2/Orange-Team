from telegram import Update
from telegram.ext import CallbackContext


class Disguise():
    """Класс, описывающий маскировки"""
    def __init__(self, name, url, unlocked=False):
        self.name = name
        self.url = url
        self.unlocked = unlocked

    def unlock(self, update: Update, context: CallbackContext):
        """Уведомление об открытии новой маскировки"""
        self.unlocked = True
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=self.url)
        restricted_symbols = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        text = self.name
        for i in restricted_symbols:
            text = text.replace(i, '\\' + i)
        return f'*_Открыта новая маскировка: {text}_*'