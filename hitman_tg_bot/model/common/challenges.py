from telegram import Update
from telegram.ext import CallbackContext


class Challenge:
    """Класс, описывающий испытания на локации"""
    def __init__(self, name, description, url, type, xp, completed=False):
        self.name = name
        self.description = description
        self.url = url
        self.type = type
        self.xp = xp
        self.completed = completed

    def achieved(self, update: Update, context: CallbackContext):
        """Уведомление о выполнении условий испытания"""
        self.completed = True
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=self.url)
        return f'Испытание выполнено: {self.name}'
