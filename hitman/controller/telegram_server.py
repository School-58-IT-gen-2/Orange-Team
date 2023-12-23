import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, \
    PollAnswerHandler, PollHandler

from controller.controller import PlayerController, TelegramView


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

users = {}

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    users[update.effective_chat.id] = PlayerController(update=Update, bot=CallbackContext, player_view=TelegramView(Update, CallbackContext))
    update.message.reply_text(
        'Введите `/begin` для начала игры'
    )

def answer(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

def run_bot() -> None:

    updater = Updater("6930836802:AAEBOokIV7Xo3WOHdtrsP5KrvV5oYM_3dxY")
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(answer))

    updater.start_polling()

    updater.idle()
