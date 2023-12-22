player_lvl = 5
class Challenge:

    def __init__(self, name, description, completed):
        self.name = name
        self.description = description
        self.completed = completed

    def achieved(self):
        global player_lvl
        if self.completed == False:
            self.completed = True
            player_lvl += 5
            return f'Испытание выполнено: {self.name}'
        return ''
    
    def challenge_info(self):
        result_string = f'{self.name}\n\n{self.description}\n\n1. Назад'
        return(result_string)

smoking_kills = Challenge('Курение убивает', 'Убейте Юки Ямадзаки во время того, как она курит сигареты.', False)
stretch = Challenge('Хорошая растяжка', 'Убейте Юки Ямадзаки, подстроив несчастный случай во время занятий йогой.', False)
personal_goodbye = Challenge('Личное прощание', 'Убейте Эриха Содерса выстрелом из пистолета.', False)
no_smoking = Challenge('Не курить!', 'Положите пачку сигарет в номере Юки Ямадзаки.', False)
human_error = Challenge('(Не) врачебная ошибка', 'Убейте Эриха Содерса, самостоятельно проведя операцию.', False)
suit_only = Challenge('Только костюм', '1. Завершите миссию\n2. Сделайте это в маскировке VIP - пациента', False)
silent_assasin = Challenge('Бесшумный убийца', '1. Завершите миссию\n2. Убивайте только цели\n3. Ни одно тело не должно быть обнаружено\n 4. Не дайте себя заметить', False)
sauna_assasination = Challenge('Убийство в парилке', 'Убейте Юки Ямадзаки, заперев ее в парилке.', False)
sushi = Challenge('Приятного аппетита', 'Отравите роллы Юки Ямадзаки ядом рыбы фугу.', False)
heartless = Challenge('Бессердечный', 'Повредите сердце Эриха содерса.', False)
silent_assasin_suit_only = Challenge('Бесшумный убйца. Только костюм.', '1. Завершите миссию\n2. Убивайте только цели\n3. Ни одно тело не должно быть обнаружено\n 4. Не дайте себя заметить\n5. Сделайте это в маскировке VIP - пациента', False)
no_evidence = Challenge('Без улик', 'Завершите миссию, не давая обнаружить тела.', False)
ghost_machine = Challenge('Призрак в машине', 'Повредите сервера KAI.', False)
straight_shot = Challenge('Точный выстрел', 'Убейте цель выстрелом из пистолета.', False)
hold_hair = Challenge('Подержи волосы', 'Убейте цель, утопив ее.', False)
piano_man = Challenge('Пианист', 'Убейте цель при помощи удавки.', False)
hurt_oneself = Challenge('Так можно и пораниться', 'Убейте цель, подстроив несчастный случай.', False)
tasteless = Challenge('Без вкуса, без следа', 'Устраните цель, отравив ее.', False)
master_assasin = Challenge('Мастер-убийца', f'1. Выполните {straight_shot.name}\n2. Выполните {hold_hair.name}\n3. Выполните {piano_man.name}\n4. Выполните {hurt_oneself.name}\n5. Выполните {tasteless.name}', False)

hokkaido_challenges = [smoking_kills, stretch, personal_goodbye, no_smoking, human_error, suit_only, silent_assasin, sauna_assasination, sushi, heartless, silent_assasin_suit_only, no_evidence, ghost_machine, straight_shot, hold_hair, piano_man, hurt_oneself, tasteless, master_assasin]
some_list = []
for i in hokkaido_challenges:
    some_list.append(str(i.completed))
another_list = ["1","2","3"]
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup,ReplyKeyboardMarkup, Update,KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, \
    PollAnswerHandler, PollHandler


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

users = {}

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    keyboard = []
    keyboard.append([KeyboardButton(f"/save", callback_data=f"")])
    keyboard.append([KeyboardButton("/download_progress", callback_data=f"")])
    keyboard.append([KeyboardButton("/move", callback_data=f"")])
    keyboard.append([KeyboardButton("/status", callback_data=f"")])
    keyboard.append([KeyboardButton("инвентарь", callback_data=f"")])
    keyboard.append([KeyboardButton("испытания", callback_data=f"")])
    reply_markup = ReplyKeyboardMarkup(keyboard)
    update.message.reply_text('gooo', reply_markup=reply_markup)

def move():
    controller.move()

def status():
    controller.status()
def save(update: Update, context: CallbackContext):
    print("here")
    f = open('information.txt')
    lines = f.readlines()
    lines = [line.rstrip() for line in lines]
    print(lines)
    f.close()
    user_id = str(update.effective_chat.id)
    if user_id not in lines:
        with open('information.txt', 'a') as f:
            f.write(str(user_id))
            f.write('\n')
            f.write('-'.join(some_list))
            f.write('\n')
            f.write('-'.join(another_list))

            f.write('\n')
        update.message.reply_text('ваш прогресс сохранен' )
        return 0 
    else:
        #update.message.reply_text('хотите заменить прошлое созранение?' )
        #проверка нужна

        update.message.reply_text('обновляем данные...' )
        with open("information.txt", "w") as f:
            pass
        lines[lines.index(user_id) + 1] = '-'.join(some_list)
        lines[lines.index(user_id) + 2] = '-'.join(another_list)
        with open('information.txt', 'a') as f:
            for i in lines:
                f.write(i)
                f.write("\n")
        update.message.reply_text('обновили информацию!!!' )


def download_progress(update: Update, context: CallbackContext):
    f = open('information.txt')
    lines = f.readlines()
    lines = [line.rstrip() for line in lines]
    info = []
    user_id = str(update.effective_chat.id)
    if user_id in lines:
        for i in range(1,3):
            info.append(lines[lines.index(user_id) + i].split('-'))
        print(info)
        return info
    else:
        update.message.reply_text("нет сохранения")
        return []



def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("6940674100:AAGD6JEpmnSsVWevH28jwV5wMikyeszH2m8")
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('save', save))
    dispatcher.add_handler(CommandHandler('download_progress', download_progress))
    dispatcher.add_handler(CommandHandler('move', save))
    dispatcher.add_handler(CommandHandler('status', download_progress))



    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()