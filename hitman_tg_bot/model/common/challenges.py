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
        restricted_symbols = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        text = self.name
        for i in restricted_symbols:
            text = text.replace(i, '\\' + i)
        return f'*_Испытание выполнено: {text}_*'
