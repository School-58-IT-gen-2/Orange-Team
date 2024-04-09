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
        return f'Открыта новая маскировка: {self.name}'
