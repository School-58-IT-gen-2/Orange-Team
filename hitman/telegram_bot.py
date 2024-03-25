import pickle
import os
import sys
import random
import time as tm

from controller.controller import PlayerController
from model.hokkaido.hokkaido_events import HokkaidoEvents
from model.player.player import Player
from model.player.player_info import *
from model.hokkaido.hokkaido_locator import HokkaidoLocator
from model.hokkaido.hokkaido_challenges import HokkaidoChallenges
from view.telegram_view import TelegramView
from config.net_config import NetConfig
from view.player_view import PlayerView
from model.player.player_info import *
from model.player.player import Player
from view.console_view import ConsoleView
from view.telegram_view import TelegramView
from model.hokkaido.hokkaido_locator import HokkaidoLocator
from model.common.npcs import Target

from adapter.hitman_adapter import HitmanAdapter

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup,ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, PollAnswerHandler, PollHandler

from dotenv import load_dotenv
load_dotenv()

tg_token = os.getenv("TELEGRAM_TOKEN")

#Загрузка испытаний из файла сохранения
os.chdir('hitman')
if os.stat('save_file.dat').st_size != 0:
    with open('save_file.dat', 'rb') as f:
        challenges = pickle.load(f)
else:
    challenges = HokkaidoChallenges()

#Определение стандартных значений для старта игры
events = HokkaidoEvents()
locator = HokkaidoLocator(challenges)
player = Player(location=locator.get_location_by_name('Номер 47-го'),
                inventory=[],
                health=100,
                item=locator.get_items().get_by_name('Нет предмета'),
                compromised_disguises=[],
                disguise='VIP - пациент',
                found_disguises=['VIP - пациент'])

controller = PlayerController(player=player, locator=locator)
adapter = HitmanAdapter()

#Начало создания ТГ бота
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

users = {}

logger = logging.getLogger(__name__)
message = -1

#Функция, которая запускает сервер с ТГ ботом
def telegram_bot():
    def start(update: Update, context: CallbackContext):
        global controller
        global user_id
        global message

        user_id = int(update.message.from_user['id'])
        user_nickname = str(update.message.from_user['username'])
        chat_id = int(update.effective_chat.id)
        created = int(tm.time())
        if adapter.search('Users', f'user_id={user_id}') == 0:
            adapter.insert('Users', [
                f'user_id={user_id}',
                f'chat_id={chat_id}',
                f'created={created}',
                f'user_nickname={user_nickname}',
                f'updated={created}'
            ])
        if update.message['message_id'] != message:
            message = update.message['message_id']
            updated = int(tm.time())

        adapter.update_by_id("Users", f'updated={updated}', user_id)

        message = update.message['message_id']

        update.message.reply_text(
            'Добро пожаловать в игру!\n\nКоманда /help покажет вам управление. Команда /begin начнет игру.'
        )
        controller = PlayerController(player=player, locator=locator, player_view=TelegramView(update))

    def get_request(update: Update, context: CallbackContext):

        global message

        if update.message['message_id'] != message:
            message = update.message['message_id']
            updated = int(tm.time())
            
        adapter.update_by_id("Users", f'updated={updated}', user_id)
        
        query = update.callback_query
        users[update.effective_chat.id].answer_text(query.data)
        users[update.effective_chat.id].answer_choice()
        print(query)
        return query

    def start_game(update: Update):

        global message

        if update.message['message_id'] != message:
            message = update.message['message_id']
            updated = int(tm.time())
            
        adapter.update_by_id("Users", f'updated={updated}', user_id)
        
        
        lvl_unlocks = {
            1: ['Номер 47-го', controller.locator.get_location_by_name('Номер 47-го'), 'VIP - пациент'],
            2: ['Зона спа', controller.locator.get_location_by_name('Зона спа'), 'VIP - пациент'],
            3: ['Горная тропа (в маскировке ниндзя)', controller.locator.get_location_by_name('Горная тропа'), 'Ниндзя'],
            4: ['Ресторан', controller.locator.get_location_by_name('Ресторан'), 'VIP - пациент'],
            5: ['Спальня персонала (в маскировке работника "ГАМА")', controller.locator.get_location_by_name('Спальня персонала'), 'Работник "ГАМА"'],
            6: ['Кухня (в маскировке шефа)', controller.locator.get_location_by_name('Кухня'), 'Шеф'],
            7: ['Внутренний сад (в маскировке работника "ГАМА")', controller.locator.get_location_by_name('Внутренний сад'), 'Работник "ГАМА"'],
            8: ['Морг', controller.locator.get_location_by_name('Морг'), 'VIP - пациент'],
            9: ['Оперционная (в маскировке хирурга)', controller.locator.get_location_by_name('Операционная'), 'Хирург']
        }

        carry_on_items = [controller.locator.get_items().get_by_name('Удавка'), controller.locator.get_items().get_by_name('Смертельный яд'), controller.locator.get_items().get_by_name('Рвотный яд'), controller.locator.get_items().get_by_name('Электронный дешифровщик'), controller.locator.get_items().get_by_name('Боевой нож'), controller.locator.get_items().get_by_name('Монета')]

        controller.player_view.response('Брифинг:\nДиана: Доброе утро, 47-й. Совет директоров одобрил ликвидацию Эриха Содерса. После Колорадо мы решили пристально изучить личные дела Содерса и выяснили, что его недавно доставили в частную клинику «Гама» на японском острове Хоккайдо для срочной операции на сердце. Без «Провиденс» тут явно не обошлось. Содерс страдает от редкой врожденной патологии — транспозиции органов: его внутренние органы в теле расположены зеркально. Для трансплантации ему необходимо правостороннее сердце, и он явно предал МКА, чтобы получить его. Его приняли прошлой ночью и сейчас он готовится к трёхэтапной операции. Под видом Тобиаса Рипера, крупного бизнесмена, ты отправляешься в «Гаму» для стандартного медицинского обследования, о формальностях мы уже позаботились. В таких условиях придётся импровизировать и самостоятельно добывать снаряжение. Кроме того, тебе нужно ликвидировать Юки Ямадзаки — она адвокат из Токио, работает на «Провиденс». Содерс уже передал Ямадзаки доступ к нашей базе клиентов и согласился предоставить полный список оперативных сотрудников МКА после завершения операции. Этого допустить никак нельзя. Содерс должен заплатить за своё предательство — это послужит хорошим уроком его нанимателям. На кону будущее и репутация МКА. Какой бы властью и могуществом ни обладала «Провиденс», пора поставить их на место. Я оставлю тебя подготавливаться.\n\nВведите любой символ, чтобы начать задание.')
        controller.player_view.request()
        result_string = ''
        for i in range(1, 10):
            if i <= player_lvl[0] // 10:
                result_string += f'{i}. {lvl_unlocks[i][0]}\n'
        controller.player_view.response(result_string)
        controller.player_view.request()
        while request.isdigit() == False:
            controller.player_view.response('Введите номер ответа')
            controller.player_view.request()
            request = get_request(update)
        request = int(request)
        start_location = lvl_unlocks[request]
        start_inventory = []
        if player_lvl[0] // 10 > 9:
            controller.player_view.response('Выберите пистолет:\n\n1. Пистолет с глушителем\n2. Пистолет без глушителя')
            controller.player_view.request()
            request = get_request(update)
            while request.isdigit() == False:
                controller.player_view.response('Введите номер ответа')
                controller.player_view.request()
                request = get_request(update)
            request = int(request)
            if request == 1:
                start_inventory.append(controller.locator.get_items().get_by_name('Пистолет с глушителем'))
            elif request == 2:
                start_inventory.append(controller.locator.get_items().get_by_name('Пистолет без глушителя'))
            result_string = 'Выберите первый предмет сняряжения:\n\n'
            for i in range(len(carry_on_items)):
                if carry_on_items[i].name == 'Монета':
                    result_string += f'{i+1}. Монета (3)\n'
                else:
                    result_string += f'{i+1}. {carry_on_items[i].name} (1)\n'
            controller.player_view.response(result_string)
            controller.player_view.request()
            request = get_request(update)
            while request.isdigit() == False:
                controller.player_view.response('Введите номер ответа')
                controller.player_view.request()
                request = get_request(update)
            request = int(request)
            if carry_on_items[request - 1].name == 'Монета':
                start_inventory += [carry_on_items[request - 1], carry_on_items[request - 1]]
            start_inventory.append(carry_on_items[request - 1])
            carry_on_items.remove(carry_on_items[request - 1])
            result_string = 'Выберите второй предмет сняряжения:\n\n'
            for i in range(len(carry_on_items)):
                if carry_on_items[i].name == 'Монета':
                    result_string += f'{i+1}. Монета (3)\n'
                else:
                    result_string += f'{i+1}. {carry_on_items[i].name} (1)\n'
            controller.player_view.response(result_string)
            controller.player_view.request()
            request = get_request(update)
            while request.isdigit() == False:
                controller.player_view.response('Введите номер ответа')
                controller.player_view.request()
                request = get_request(update)
            request = int(request)
            if carry_on_items[request - 1].name == 'Монета':
                start_inventory += [carry_on_items[request - 1], carry_on_items[request - 1]]
            start_inventory.append(carry_on_items[request - 1])
        controller.player_view.response('Диана: Удачи, агент.')
        if start_location[1].get_name() == 'Номер 47-го':
            controller.player_view.response('Диана: Добро пожаловать на Хоккайдо, 47-й. Частная клиника «Гама» оказывает медицинские услуги высочайшего уровня представителям мировой элиты, выходя при необходимости за рамки закона. Частично здание находится под управлением искусственного интеллекта — KAI. Система контролирует доступ пациентов в разные части клиники и даже принимает участие в ряде медицинских процедур. Эрих Содерс уже находится в операционной, где он проходит предварительную подготовку с применением стволовых клеток. Это крайне противоречивая процедура ещё не одобрена властями Японии. Юки Ямадзаки уже прибыла. Она находится либо в своём номере, либо в ресторане, либо в спа-зоне клиники. Содерсу скоро введут наркоз. Сделай так, чтобы он больше никогда не проснулся. Удачи, 47-й.')
        controller.player.current_location = start_location[1]
        controller.player.inventory = start_inventory
        controller.player.health = 100
        controller.player.found_disguises = [start_location[2]]
        controller.player.item = controller.locator.get_items().get_by_name('Нет предмета')
        controller.player.compromised_disguises = []
        controller.player.disguise = start_location[2]
        return True


    def begin(update: Update, context: CallbackContext):

        global message

        if update.message['message_id'] != message:
            message = update.message['message_id']
            updated = int(tm.time())
            
        adapter.update_by_id("Users", f'updated={updated}', user_id)
        
        keyboard = []
        keyboard.append([KeyboardButton(f"Сохранить и выйти", callback_data=f"q")])
        keyboard.append([KeyboardButton("Взаимодействие", callback_data=f"f")])
        keyboard.append([KeyboardButton("Передвижение", callback_data=f"w")])
        keyboard.append([KeyboardButton("Статус", callback_data=f"s")])
        keyboard.append([KeyboardButton("Инвентарь", callback_data=f"i")])
        keyboard.append([KeyboardButton("Испытания", callback_data=f"c")])
        keyboard.append([KeyboardButton("Обыскать локацию", callback_data=f"e")])
        reply_markup = ReplyKeyboardMarkup(keyboard)
        update.message.reply_text('Выберите номер ответа:', reply_markup=reply_markup)
        start_game(update)

    def help(update: Update, context: CallbackContext):

        global message

        if update.message['message_id'] != message:
            message = update.message['message_id']
            updated = int(tm.time())
            
        adapter.update_by_id("Users", f'updated={updated}', user_id)
        
        update.message.reply_text(
            'Обучение:\n\nИнвентарь можно открыть при вводе «і» или «І», там будут сохранятся подобранные вами предметы, которые можно использовать для выполнения миссии. Чтобы пополнять инвентарь, необходимо обыскивать комнаты, это можно сделать нажав "е" или "Е" при нахождении в комнате, предметы автоматически добавятся в ваш инвентарь, если комната уже пустая, вы лишь пропустите небольшой промежуток времени. При вводе «w» или «W» откроется меню выбора локации, в которую вы хотите переместиться. "S" или "S" показывает статус локации, а также вашей цели. При нахождении новых маскировок можно будет попасть в локации, в которых ранее была запретная зона. Несмотря на это, вы может проникнуть в них и без маскировки, но тогда велик шанс обнаружения. Некоторые действия в игре выполняются с неким шансом от 1 до 10, который будет писаться рядом с ним, неудача может привести к непредсказуемым результатам и даже к провалу операции. Используя "f" или "F" вы можете взаимодействовать с локацией. После завершения операции вы увидите свой рейтинг (от 0 до 5). Чтобы получить максимальный рейтинг необходимо выполнить задание так, чтобы не было убито невиновных, не было найдено тел, а также вы не были замечены в запретной зоне или с нелегальным предметом в руках. Помимо этого, за прохождение миссии вы получаете уровень, который может открывать различные награды. Чтобы быстрее повышать уровень, выполняйте испытания, "c" или "C" открывает меню с испытаниями. Выбор вариантов осуществляется вводом его номера. "q" или "Q" завершает игру.'
        )

    def run_bot():

        updater = Updater(tg_token)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler('start', start))
        dispatcher.add_handler(CommandHandler('help', help))
        dispatcher.add_handler(CommandHandler('begin', begin))
        dispatcher.add_handler(CallbackQueryHandler(get_request))
        updater.start_polling()
        updater.idle()

    run_bot()

telegram_bot()