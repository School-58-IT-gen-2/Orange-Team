from telegram import Update
from telegram.ext import CallbackContext


class Location:
    """Класс, описывающий локации на миссии"""
    def __init__(self, name, connetcted_locations, disguise, witnesses, items, url, unlocked=False):
        self.name = name
        self.connected_locations = connetcted_locations
        self.disguise = disguise
        self.witnesses = witnesses
        self.items = items
        self.url = url
        self.unlocked = unlocked

    def unlock(self, update: Update, context: CallbackContext):
        """Уведомление об открытии новой локации"""
        self.unlocked = True
        if 'http' in self.url:
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=self.url)
        else:
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(self.url, 'rb'), timeout=1000)
        restricted_symbols = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        text = self.name
        for i in restricted_symbols:
            text = text.replace(i, '\\' + i)
        return f'*_Открыта новая локация: {text}_*'
