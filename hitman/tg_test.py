import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, \
    PollAnswerHandler, PollHandler

from hitman.controller.simple_controller import SimpleController

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

users = {}

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Введите `/begin` для начала игры'
    )


def begin(update: Update, context: CallbackContext) -> None:
    users[update.effective_chat.id] = SimpleController(update, context.bot, "tg")
    update.message.reply_text(
        'Добро пожаловать в игру! Вы были зарегистрированы'
    )
    users[update.effective_chat.id].answer_choice()

def answer(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    users[update.effective_chat.id].answer_text(query.data)
    users[update.effective_chat.id].answer_choice()



def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("6888049809:AAHz_UR4dfMVGgtJrWmDjtSZGad08wZFFss")
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('begin', begin))
    dispatcher.add_handler(CallbackQueryHandler(answer))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
