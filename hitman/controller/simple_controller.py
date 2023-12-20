from hitman.view.telegram_view import TelegramView


class SimpleController():
    def __init__(self, update, bot, type):
        self.__update = update
        self.__bot = bot
        if type == "tg":
            self.__view = TelegramView(update, bot)
        else:
            self.__view = TelegramView(update, bot)


    def answer_choice(self):
        self.__view.answer_choice(7)

    def answer_text(self, text):
        if text == '1':
            self.__view.answer_text('You killed with a car')

        if text == '2':
            self.__view.answer_text('You killed with a book')

        if text == '3':
            self.__view.answer_text('You killed with a laptop')

        else:
            self.__view.answer_text(f"well, nothing happened after you choose {text}")



