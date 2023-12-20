from telegram import InlineKeyboardButton, update, InlineKeyboardMarkup, Update


class TelegramView():
    def __init__(self, update: Update, bot):
        self.__update = update
        self.__bot = bot

    def answer_choice(self, num):
        keyboard = []
        for i in range(1, num):
            keyboard.append([InlineKeyboardButton(f"Option {i}", callback_data=f"{i}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        self.__update.message.reply_text('Пожалуйста, выберите:', reply_markup=reply_markup)

    def answer_text(self, text):
        self.__update.message.reply_text(text)