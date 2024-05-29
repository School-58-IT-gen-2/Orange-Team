import os
import random
import time as tm

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackQueryHandler, CallbackContext, CommandHandler

from dotenv import load_dotenv
load_dotenv()

from model.player.player_info import *
from query import *


adapter = HitmanAdapter()
tg_token = os.getenv("TELEGRAM_TOKEN")

def create_locations_values(challenges: dict, npcs: dict, targets: dict, events: dict, locations: dict, items: dict, disguises: dict) -> dict:
    "Создание словаря с данными о локации"
    challenges_values = list(challenges.values())
    user_challenges = {list(challenges.keys())[i]: Challenge(name=challenges_values[i].name, description=challenges_values[i].description, url=challenges_values[i].url, type=challenges_values[i].type, xp=challenges_values[i].xp) for i in range(len(challenges))}
    disguises_values = list(disguises.values())
    user_disguises = {list(disguises.keys())[i]: Disguise(name=disguises_values[i].name, url=disguises_values[i].url) for i in range(len(disguises))}
    items_values = list(items.values())
    user_items = {list(items.keys())[i]: Item(name=items_values[i].name, usage=items_values[i].usage, legal=items_values[i].legal, lethal=items_values[i].lethal, weapon=items_values[i].weapon) for i in range(len(items))}
    locations_values = list(locations.values())
    user_locations = {list(locations.keys())[i]: Location(name=locations_values[i].name, connetcted_locations=locations_values[i].connected_locations, disguise=[user_disguises[j.name] for j in locations_values[i].disguise], witnesses=locations_values[i].witnesses, items=[user_items[j.name] for j in locations_values[i].items], url=locations_values[i].url) for i in range(len(locations))}
    npcs_values = list(npcs.values())
    user_npcs = {list(npcs.keys())[i]: NPC(name=npcs_values[i].name, disguise=user_disguises[npcs_values[i].disguise.name], route=npcs_values[i].route, witness_chance=npcs_values[i].witness_chance, guard=npcs_values[i].guard) for i in range(len(npcs))}
    targets_values = list(targets.values())
    user_targets = {list(targets.keys())[i]: Target(name=targets_values[i].name, route=targets_values[i].route) for i in range(len(targets))}
    events_values = list(events.values())
    user_events = {list(events.keys())[i]: Event(name=events_values[i].name) for i in range(len(events))}
    return {'challenges': user_challenges, 'disguises': user_disguises, 'locations': user_locations, 'npcs': user_npcs, 'targets': user_targets, 'events': user_events, 'items': user_items}

def create_user(user_id: int) -> PlayerInfo:
    """Создание объекта класса информации о пользователе"""
    locations_values = {}
    saved_data = {}
    lst = list(adapter.get_by_id('users', user_id))[0]
    for i in missions:
        locations_values[i] = create_locations_values(missions[i]['challenges'], missions[i]['npcs'], missions[i]['targets'], missions[i]['events'], missions[i]['locations'], missions[i]['items'], missions[i]['disguises'])
    for j in range(6, len(lst), 3):
        saved_data[list(missions.keys())[(j - 6) // 3]] = {'challenges': lst[j], 'disguises': lst[j + 1], 'locations': lst[j + 2]}
    return PlayerInfo(carry_on_items=['Удавка', 'Смертельный яд', 'Рвотный яд', 'Дешифровщик', 'Боевой нож', 'Монета'], player_lvl=lst[5], saved_data=saved_data, player=Player(), loadout={'Начальная локация': None, 'Пистолет': None, 'Снаряжение 1': None, 'Снаряжение 2': None}, locations_values=locations_values)

users = {i[0]: create_user(user_id=i[0]) for i in adapter.get_all('users')}



#----------Начало создания ТГ бота----------

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)



#----------Часто используемые функции----------

def tg_text_convert(text: str) -> str:
    restricted_symbols = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for i in restricted_symbols:
        text = text.replace(i, '\\' + i)
    return text

def make_heading(string: str) -> str:
    """Создание заголовка для меню"""
    return f'*_\U00002E3A {string} \U00002E3A_*\n\n'


def location_status(update: Update, context: CallbackContext, location: Location) -> str:
    """Вывод статуса локации"""
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    result_string = make_heading(tg_text_convert(location.name))[:-1]
    location_npcs = find_location_npcs(update=update, context=context, location=location)
    location_disguises = []
    for i in location_npcs:
        location_disguises.append(i.disguise.name)
    if location_npcs != [] or location.witnesses != 0:
        result_string += '\nНа локации находятся:\n'
        for i in list(users[user_id].targets.values()):
            if i.move(users[user_id].time) == location.name:
                result_string += tg_text_convert(f'\n{i.name}\n')
        if location.witnesses > 0:
            if users[user_id].mission == 'hokkaido':
                result_string += f'\n{location.witnesses} Пациент'
            elif users[user_id].mission == 'ica':
                result_string += f'\n{location.witnesses} Гость'
        for i in list(users[user_id].disguises.values()):
            if i.name in location_disguises:
                if i.name in ['Джейсон Портман', 'Амос Декстер', 'Терри Норфолк']:
                    result_string += f'\n{i.name}'
                else:
                    result_string += f'\n{location_disguises.count(i.name)} {i.name}'
        if users[user_id].mission == 'hokkaido':
            if users[user_id].targets['Yuki Yamazaki'].alive == False and users[user_id].targets['Erich Soders'].alive == False and users[user_id].events['Все цели убиты'].completed == False:
                users[user_id].events['Все цели убиты'].completed = True
                result_string = tg_text_convert('Все цели убиты. Найдте выход с миссии.\n\n\n') + result_string
        elif users[user_id].mission == 'ica':
            if users[user_id].targets['Kalvin Ritter'].alive == False and users[user_id].events['Все цели убиты'].completed == False:
                users[user_id].events['Все цели убиты'].completed = True
                result_string = tg_text_convert('Все цели убиты. Найдте выход с миссии.\n\n\n') + result_string
        return result_string
    else:
        result_string += '\nНа локации никого нет'
        return result_string
    
def find_location_npcs(update: Update, context: CallbackContext, location: Location) -> list:
    """Вывод всех NPC на локации"""
    user_id = update.callback_query.from_user['id']
    location_npcs = []
    for i in list(users[user_id].npcs.values()):
        if i.move(users[user_id].time) == location.name and i.alive == True:
            location_npcs.append(i)
    return location_npcs

def location_witnesses(update: Update, context: CallbackContext, location: Location) -> int:
    """Вывод количества свидетелей на локации"""
    location_npcs = find_location_npcs(update=update, context=context, location=location)
    location_witnesses = location.witnesses
    for i in location_npcs:
        if random.randrange(11) <= i.witness_chance and i.alive == True:
            location_witnesses += 1
    return location_witnesses


def make_keyboard(options: list, func_name: str) -> list:
    """Создание клавиатуры для меню"""
    keyboard = []
    for i in range(len(options)):
        keyboard.append([InlineKeyboardButton(f"{options[i]}", callback_data=options[i] + func_name)])
    return keyboard

def make_keyboard_two_rows(options: list, func_name: str) -> list:
    """Создание клавиатуры с двумя колонками для меню"""
    keyboard = []
    if len(options) % 2 == 0:
        for i in range(0, len(options), 2):
            keyboard.append([InlineKeyboardButton(f'{options[i]}', callback_data=f'{options[i]}' + func_name), InlineKeyboardButton(f'{options[i + 1]}', callback_data=f'{options[i + 1]}' + func_name)])
    else:
        for i in range(0, len(options) - 1, 2):
            keyboard.append([InlineKeyboardButton(f'{options[i]}', callback_data=f'{options[i]}' + func_name), InlineKeyboardButton(f'{options[i + 1]}', callback_data=f'{options[i + 1]}' + func_name)])
        keyboard.append([InlineKeyboardButton(f'{options[-1]}', callback_data=f'{options[-1]}' + func_name)])
    return keyboard



#----------Меню в игре----------

def choose_action_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите действие', reply_markup=(choose_action_keyboard(update=update, context=context)))
    

def status_menu(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    result_string = ''
    for i in list(users[user_id].targets.values()):
        if i.alive == True:
            result_string += f'{i.name}: {i.move(users[user_id].time)}\n'
        else:
            result_string += f'{i.name}: Цель устранена\n'
    result_string += f'\nТекущая маскировка: {users[user_id].player.disguise.name}\n'
    result_string += f'Предмет в руках: {users[user_id].player.item.name}'
    if int(5-(users[user_id].bodies*0.5)-(users[user_id].kills*0.7)-(users[user_id].suspicion_count*0.2)) == 5:
        result_string += f'\n\nБесшумный убийца'
    result_string = make_heading('Статус') + tg_text_convert(result_string)
    result_string += '\n\n\n' + location_status(update=update, context=context, location=users[user_id].player.current_location)
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=result_string, reply_markup=(status_keyboard()), parse_mode='MarkdownV2')


def challenges_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=make_heading('Испытания')[:-2], reply_markup=challenges_keyboard(update=update, context=context), parse_mode='MarkdownV2')

def assasinations_menu(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    text = make_heading('Убийства')
    completed_challenges = []
    for i in list(users[user_id].challenges.values()):
        if i.type == 'Убийство':
            if i.completed == False:
                text += '*_' + tg_text_convert(i.name) + '_*\n' + tg_text_convert(i.description) + '\n\n'
            else:
                completed_challenges.append(f'{i.name} (выполнено)')
    for i in completed_challenges:
        text += '*_' + tg_text_convert(i) + '_*\n\n'
    text = text[:-1]
    query.answer()
    query.edit_message_text(text=text, reply_markup=challenges_section_keyboard(), parse_mode='MarkdownV2')

def feats_menu(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    text = make_heading('Усложнение')
    completed_challenges = []
    for i in list(users[user_id].challenges.values()):
        if i.type == 'Усложнение':
            if i.completed == False:
                text += '*_' + tg_text_convert(i.name) + '_*\n' + tg_text_convert(i.description) + '\n\n'
            else:
                completed_challenges.append(f'{i.name} (выполнено)')
    for i in completed_challenges:
        text += '*_' + tg_text_convert(i) + '_*\n\n'
    text = text[:-1]
    query.answer()
    query.edit_message_text(text=text, reply_markup=challenges_section_keyboard(), parse_mode='MarkdownV2')

def discovery_menu(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    text = make_heading('Исследование')
    completed_challenges = []
    for i in list(users[user_id].challenges.values()):
        if i.type == 'Исследование':
            if i.completed == False:
                text += '*_' + tg_text_convert(i.name) + '_*\n' + tg_text_convert(i.description) + '\n\n'
            else:
                completed_challenges.append(f'{i.name} (выполнено)')
    for i in completed_challenges:
        text += '*_' + tg_text_convert(i) + '_*\n\n'
    text = text[:-1]
    query.answer()
    query.edit_message_text(text=text, reply_markup=challenges_section_keyboard(), parse_mode='MarkdownV2')

def classics_menu(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    text = make_heading('Классика')
    completed_challenges = []
    for i in list(users[user_id].challenges.values()):
        if i.type == 'Классика':
            if i.completed == False:
                text += '*_' + tg_text_convert(i.name) + '_*\n' + tg_text_convert(i.description) + '\n\n'
            else:
                completed_challenges.append(f'{i.name} (выполнено)')
    for i in completed_challenges:
        text += '*_' + tg_text_convert(i) + '_*\n\n'
    text = text[:-1]
    query.answer()
    query.edit_message_text(text=text, reply_markup=challenges_section_keyboard(), parse_mode='MarkdownV2')


def choose_start_location_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите начальную локацию', reply_markup=(choose_start_location_keyboard(update=update, context=context)))
    
def choose_start_item_menu_1(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите первый предмет снаряжения', reply_markup=(choose_start_item_keyboard_1(update=update, context=context)))
    
def choose_start_item_menu_2(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите второй предмет снаряжения', reply_markup=(choose_start_item_keyboard_2(update=update, context=context)))

def choose_pistol_menu(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    if users[user_id].mission == 'hokkaido':
        for i in list(hokkaido_lvl_unlocks.values()):
            if i[0] == query.data.replace('CSL', ''):
                users[user_id].start_location = i[0]
                users[user_id].start_disguise = i[1]
    query.answer()
    if users[user_id].player_lvl >= 100:
        query.edit_message_text(text='Выберите пистолет', reply_markup=choose_pistol_keyboard())
    else:
        spawn_player(update=update, context=context)


def safe_move_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите локацию', reply_markup=(safe_move_keyboard(update=update, context=context)))

def move_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите локацию', reply_markup=(move_keyboard(update=update, context=context)))

def no_disguise_move_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='У вас нет подходящей маскировки. Переместиться на локацию?', reply_markup=(no_disguise_move_keyboard()))


def attack_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите действие', reply_markup=(attack_keyboard()))

def hide_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите действие', reply_markup=(hide_keyboard()))


def loot_menu(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    users[user_id].time += 5
    query = update.callback_query
    query.answer()
    users[user_id].player.inventory += users[user_id].player.current_location.items
    result_string = ''
    if users[user_id].player.current_location.items == []:
        query.edit_message_text(text='На локации нет предметов', reply_markup=(choose_action_keyboard(update=update, context=context)))
    else:
        for i in list(users[user_id].items.values()):
            if i in users[user_id].player.current_location.items:
                result_string += f'{i.name} ({users[user_id].player.current_location.items.count(i)})\n'
        result_string = '*_Найдены предметы:_*\n\n' + tg_text_convert(result_string)
        if users[user_id].mission == 'hokkaido':
            if users[user_id].items['Пачка сигарет'] in users[user_id].player.inventory and users[user_id].events['Информация о сигаретах 1'].completed == False:
                users[user_id].events['Информация о сигаретах 1'].completed = True
                query.edit_message_text(text=make_heading('Пачка сигарет') + tg_text_convert('Диана: Это пачка сигарет. Не территории клиники «Гама» курение строго запрещено, так что эти сигареты — явная контрабанда.'), parse_mode='MarkdownV2')
                if users[user_id].challenges['Дайте ещё одну'].completed == False:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Дайте ещё одну'].achieved(update=update, context=context), parse_mode='MarkdownV2')
                    users[user_id].player_lvl += users[user_id].challenges['Дайте ещё одну'].xp
                context.bot.send_message(chat_id=update.effective_chat.id, text=result_string, reply_markup=(choose_action_keyboard(update=update, context=context)), parse_mode='MarkdownV2')
            elif users[user_id].items['Пульт от нейрочипа'] in users[user_id].player.inventory and users[user_id].events['Информация о чипе'].completed == False:
                users[user_id].events['Информация о чипе'].completed = True
                query.edit_message_text(text=make_heading('Пульт от нейрочипа') + tg_text_convert('Диана: Нейрочип для изменения настроения. Интересно...\n\nДоктор Каташи Ито, он же Куратор, проводит сейчас какое-то медицинское испытание. Занимательно.\n\nХранилище органов находится в ведении Куратора, а значит, у него точно есть доступ к сердцу, которое должны пересадить Содерсу. 47-й, я рекомендую найти отчёт сотрудника и выяснить, для чего нужен этот нейроимплантат. Может пригодиться.'), parse_mode='MarkdownV2')
                if users[user_id].challenges['Изменение настроения'].completed == False:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Изменение настроения'].achieved(update=update, context=context), parse_mode='MarkdownV2')
                    users[user_id].player_lvl += users[user_id].challenges['Изменение настроения'].xp
                context.bot.send_message(chat_id=update.effective_chat.id, text=result_string, reply_markup=(choose_action_keyboard(update=update, context=context)), parse_mode='MarkdownV2')
            elif users[user_id].items['Стволовые клетки'] in users[user_id].player.inventory and users[user_id].events['Стволовые клетки'].completed == False:
                users[user_id].events['Стволовые клетки'].completed = True
                query.edit_message_text(text=make_heading('Зараженные стволовые клетки') + tg_text_convert('Контейнер, заполненный заражёнными и ядовитыми стволовыми клетками. Попадание таких клеток в кровь крайне опасно для здоровья.'), parse_mode='MarkdownV2')
                context.bot.send_message(chat_id=update.effective_chat.id, text=result_string, reply_markup=(choose_action_keyboard(update=update, context=context)), parse_mode='MarkdownV2')
            elif users[user_id].items['Яд рыбы Фугу'] in users[user_id].player.inventory and users[user_id].challenges['Запахло рыбой'].completed == False:
                query.edit_message_text(text=users[user_id].challenges['Запахло рыбой'].achieved(update=update, context=context), parse_mode='MarkdownV2')
                users[user_id].player_lvl += users[user_id].challenges['Запахло рыбой'].xp
                context.bot.send_message(chat_id=update.effective_chat.id, text=result_string, reply_markup=(choose_action_keyboard(update=update, context=context)), parse_mode='MarkdownV2')
            else:
                query.edit_message_text(text=result_string, reply_markup=(choose_action_keyboard(update=update, context=context)), parse_mode='MarkdownV2')
        elif users[user_id].mission == 'ica':
            if users[user_id].items['Крысиный яд'] in users[user_id].player.inventory and users[user_id].challenges['Беречь от детей'].completed == False:
                query.edit_message_text(text=users[user_id].challenges['Беречь от детей'].achieved(update=update, context=context), parse_mode='MarkdownV2')
                users[user_id].player_lvl += users[user_id].challenges['Беречь от детей'].xp
                context.bot.send_message(chat_id=update.effective_chat.id, text=result_string, reply_markup=(choose_action_keyboard(update=update, context=context)), parse_mode='MarkdownV2')
            else:
                query.edit_message_text(text=result_string, reply_markup=(choose_action_keyboard(update=update, context=context)), parse_mode='MarkdownV2')
        else:
            query.edit_message_text(text=result_string, reply_markup=(choose_action_keyboard(update=update, context=context)), parse_mode='MarkdownV2')
    users[user_id].player.current_location.items = []


def inventory_menu(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    result_string = make_heading('Инвентарь')
    result_string += f'Сейчас в руках: {users[user_id].player.item.name}'
    if users[user_id].player.inventory == []:
        result_string += '\n\nУ вас нет предметов'
    query.answer()
    query.edit_message_text(text=result_string, reply_markup=(inventory_keyboard(update=update, context=context)), parse_mode='MarkdownV2')

def disguise_menu(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f'Текущая маскировка: {users[user_id].player.disguise.name}', reply_markup=(disguise_keyboard(update=update, context=context)))

def choose_illegal_item_menu(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    if users[user_id].mission == 'hokkaido':
        if users[user_id].player.disguise.name != 'Охранник' and users[user_id].player.disguise.name != 'Телохранитель':
            users[user_id].illegal_item = query.data[:-4]
            query.edit_message_text(text=f'Вы собираетесь взять нелегальный предмет. Достать предмет?', reply_markup=(choose_illegal_item_keyboard()))
        else:
            query.edit_message_text(text=f'Сейчас в руках: {users[user_id].player.item.name}', reply_markup=(choose_action_keyboard(update=update, context=context)))
    elif users[user_id].mission == 'ica':
        if users[user_id].player.disguise.name != 'Охранник яхты' and users[user_id].player.disguise.name != 'Телохранитель':
            users[user_id].illegal_item = query.data[:-4]
            query.edit_message_text(text=f'Вы собираетесь взять нелегальный предмет. Достать предмет?', reply_markup=(choose_illegal_item_keyboard()))
        else:
            query.edit_message_text(text=f'Сейчас в руках: {users[user_id].player.item.name}', reply_markup=(choose_action_keyboard(update=update, context=context)))


def combat_start_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f'Начался бой.', reply_markup=(combat_start_keyboard()))

def choose_weapon_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f'Выберите оружие', reply_markup=(choose_weapon_keyboard(update=update, context=context)))

def choose_weapon_action_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f'Выберите действие', reply_markup=(choose_weapon_action_keyboard(update=update, context=context, item_name=query.data)))


def interact_menu(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    if users[user_id].player.item.usage == []:
        text = 'Нет действий с этим предметом'
    else:
        text = 'Выберите действие'
    query.edit_message_text(text=text, reply_markup=(interact_menu_keyboard(update=update, context=context)))

def kill_menu(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    if 'Бросить' in query.data:
        users[user_id].thrown_weapon = True
    query.answer()
    if find_location_npcs(update=update, context=context, location=users[user_id].player.current_location):
        query.edit_message_text(text='Выберите цель', reply_markup=(kill_keyboard(update=update, context=context)))
    else:
        query.edit_message_text(text='На локации никого нет', reply_markup=(choose_action_keyboard(update=update, context=context)))
    
def knock_out_menu(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    if 'Бросить' in query.data:
        users[user_id].thrown_weapon = True
    query.answer()
    if find_location_npcs(update=update, context=context, location=users[user_id].player.current_location):
        query.edit_message_text(text='Выберите цель', reply_markup=(knock_out_keyboard(update=update, context=context)))
    else:
        query.edit_message_text(text='На локации никого нет', reply_markup=(choose_action_keyboard(update=update, context=context)))

def distract_menu(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    text = 'Выберите, кого вы хотите отвлечь'
    if find_location_npcs(update=update, context=context, location=users[user_id].player.current_location) == []:
        text = 'На локации никого нет'
    if len(find_location_npcs(update=update, context=context, location=users[user_id].player.current_location)) > 3:
        text = 'На локации слишком много людей'
    query.edit_message_text(text=text, reply_markup=(distract_keyboard(update=update, context=context)))

def confirm_kill_menu(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    npc_name = query.data.replace('KILL', '')
    witnesses = min(location_witnesses(update=update, context=context, location=users[user_id].player.current_location), 9)
    if npc_name in list(users[user_id].npcs.keys()):
        npc = users[user_id].npcs[npc_name]
        query.answer()
        query.edit_message_text(text=f'Действия видят {witnesses} человек\n\n{npc.name} ({npc.disguise.name})', reply_markup=(confirm_kill_keyboard(query.data, witnesses)))
    else:
        npc = users[user_id].targets[npc_name]
        query.answer()
        query.edit_message_text(text=f'Действия видят {witnesses} человек\n\n{npc.name}', reply_markup=(confirm_kill_keyboard(query.data, witnesses)))

def confirm_knock_menu(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    npc = users[user_id].npcs[query.data.replace('KNOCK', '')]
    query.answer()
    witnesses = min(location_witnesses(update=update, context=context, location=users[user_id].player.current_location), 9)
    query.edit_message_text(text=f'Действия видят {witnesses} человек\n\n{npc.name} ({npc.disguise.name})', reply_markup=(confirm_knock_keyboard(query.data, witnesses)))

def confirm_distract_menu(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    npc = users[user_id].npcs[query.data.replace('DIS', '')]
    query.answer()
    query.edit_message_text(text=f'{npc.name} ({npc.disguise.name})', reply_markup=(confirm_distract_keyboard(query.data)))


def destroy_heart_menu_2(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите действие', reply_markup=(destroy_heart_keyboard_2()))


def save_and_quit_confirm_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='*ВНИМАНИЕ*: При выходе будут сохранены ваш текущий уровень и выполненные испытания, но не текущее продвижение по миссии\.\n\nВы уверены, что хотите завершить игру\?', reply_markup=(save_and_quit_confirm_keyboard()), parse_mode='MarkdownV2')


def choose_equipment_menu(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    if users[user_id].mission == 'hokkaido':
        query.edit_message_text(text='*_Транспозиция органов\n\nХоккайдо, Япония_*', reply_markup=(choose_equipment_keyboard(update=update, context=context)), parse_mode='MarkdownV2')

def choose_tutorial_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите миссию', reply_markup=choose_tutorial_keyboard())


def skip_choose_action_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data.replace('SKIP', '')
    if data == 'sauna':
        query.edit_message_text(text='Выберите действие', reply_markup=skip_choose_action_keyboard(update=update, context=context, skip_sauna=True))
    elif data == 'hokkaido_exit':
        query.edit_message_text(text='Выберите действие', reply_markup=skip_choose_action_keyboard(update=update, context=context, skip_hokkaido_exit=True))
    elif data == 'sushi':
        query.edit_message_text(text='Выберите действие', reply_markup=skip_choose_action_keyboard(update=update, context=context, skip_sushi=True))
    elif data == 'cigars_1':
        query.edit_message_text(text='Выберите действие', reply_markup=skip_choose_action_keyboard(update=update, context=context, skip_cigars_1=True))
    elif data == 'cigars_2':
        query.edit_message_text(text='Выберите действие', reply_markup=skip_choose_action_keyboard(update=update, context=context, skip_cigars_2=True))
    elif data == 'cells':
        query.edit_message_text(text='Выберите действие', reply_markup=skip_choose_action_keyboard(update=update, context=context, skip_cells=True))
    elif data == 'operation':
        query.edit_message_text(text='Выберите действие', reply_markup=skip_choose_action_keyboard(update=update, context=context, skip_operation=True))
    elif data == 'lifeboat':
        query.edit_message_text(text='Выберите действие', reply_markup=skip_choose_action_keyboard(update=update, context=context, skip_lifeboat=True))
    elif data == 'ica_exit':
        query.edit_message_text(text='Выберите действие', reply_markup=skip_choose_action_keyboard(update=update, context=context, skip_ica_exit=True))
    elif data == 'drink':
        query.edit_message_text(text='Выберите действие', reply_markup=skip_choose_action_keyboard(update=update, context=context, skip_drink=True))
        
        


#----------Клавиатуры для меню----------

def stem_cells_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Да', callback_data='PSC'), InlineKeyboardButton('Нет', callback_data='Выбор действия')]])

def choose_equipment_keyboard(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    data = update.callback_query.data
    if 'CSL' in data:
        users[user_id].loadout['Начальная локация'] = data.replace('CSL', '')
    if 'choose_pistol' in data:
        users[user_id].loadout['Пистолет'] = data.replace('choose_pistol', '')
    if 'choose_item_1' in data:
        users[user_id].loadout['Снаряжение 1'] = data.replace('choose_item_1', '')
        if users[user_id].loadout['Снаряжение 1'] == users[user_id].loadout['Снаряжение 2']:
            users[user_id].loadout['Снаряжение 2'] = None
    if 'choose_item_2' in data:
        users[user_id].loadout['Снаряжение 2'] = data.replace('choose_item_2', '')
        if users[user_id].loadout['Снаряжение 1'] == users[user_id].loadout['Снаряжение 2']:
            users[user_id].loadout['Снаряжение 1'] = None
    start_location=users[user_id].loadout['Начальная локация']
    pistol=users[user_id].loadout['Пистолет']
    equipment_1=users[user_id].loadout['Снаряжение 1']
    equipment_2=users[user_id].loadout['Снаряжение 2']
    options = []
    if start_location:
        options.append(start_location)
    else:
        options.append('Начальная локация')
    if users[user_id].player_lvl >= 60:
        if pistol:
            options.append(pistol)
        else:
            options.append('Пистолет')
        if equipment_1:
            options.append(equipment_1)
        else:
            options.append('Снаряжение 1')
        if equipment_2:
            options.append(equipment_2)
        else:
            options.append('Снаряжение 2')
        return InlineKeyboardMarkup([
                [InlineKeyboardButton('Брифинг', callback_data="hokkaido_briefing_1")],
                [InlineKeyboardButton(options[0], callback_data="Выбор начальной локации"), InlineKeyboardButton(options[1], callback_data="Выбор пистолета")],
                [InlineKeyboardButton(options[2], callback_data="Выбор снаряжения 1"), InlineKeyboardButton(options[3], callback_data="Выбор снаряжения 2")],
                [InlineKeyboardButton('Начать миссию', callback_data="НАЧИХоккЯП")]
            ])
    return InlineKeyboardMarkup([
                [InlineKeyboardButton('Брифинг', callback_data="hokkaido_briefing_1")],
                [InlineKeyboardButton(options[0], callback_data="Выбор начальной локации")],
                [InlineKeyboardButton('Начать миссию', callback_data="НАЧИХоккЯП")]
            ])

def safe_move_keyboard(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    if len(users[user_id].player.current_location.connected_locations) > 3:
        keyboard = make_keyboard_two_rows(users[user_id].player.current_location.connected_locations, 'SM')
    else:
        keyboard = make_keyboard(users[user_id].player.current_location.connected_locations, 'SM')
    keyboard.append([InlineKeyboardButton("Отменить действие", callback_data='Взаимодействие')])
    return InlineKeyboardMarkup(keyboard)

def move_keyboard(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    if len(users[user_id].player.current_location.connected_locations) > 3:
        keyboard = make_keyboard_two_rows(users[user_id].player.current_location.connected_locations, 'basic_move')
    else:
        keyboard = make_keyboard(users[user_id].player.current_location.connected_locations, 'basic_move')
    keyboard.append([InlineKeyboardButton("Отменить действие", callback_data='Выбор действия')])
    return InlineKeyboardMarkup(keyboard)

def choose_pistol_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("ICA 19", callback_data="ICA 19choose_pistol"), InlineKeyboardButton("Bartoli 75R", callback_data="Bartoli 75Rchoose_pistol")], [InlineKeyboardButton("Не брать пистолет", callback_data="choose_pistol")]])

def status_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("Выйти", callback_data='Выбор действия')]])

def choose_action_keyboard(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    if users[user_id].mission == 'hokkaido':
        if users[user_id].disguises['Охранник'] in users[user_id].player.found_disguises or users[user_id].disguises['Телохранитель'] in users[user_id].player.found_disguises:
            users[user_id].player.inventory.append(users[user_id].items['Bartoli 75R'])
    elif users[user_id].mission == 'ica':
        if users[user_id].disguises['Охранник яхты'] in users[user_id].player.found_disguises or users[user_id].disguises['Телохранитель'] in users[user_id].player.found_disguises:
            users[user_id].player.inventory.append(users[user_id].items['Bartoli 75R'])
    unlocked_disguises = 0
    for i in list(users[user_id].disguises.values()):
        if i.unlocked:
            unlocked_disguises += 1
    unlocked_locations = 0
    for i in list(users[user_id].locations.values()):
        if i.unlocked:
            unlocked_locations += 1
    if users[user_id].mission == 'hokkaido':
        if users[user_id].challenges['Хамелеон'].completed == False and unlocked_disguises == len(users[user_id].disguises):
            context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Хамелеон'].achieved(update=update, context=context), parse_mode='MarkdownV2')
            users[user_id].player_lvl += users[user_id].challenges['Хамелеон'].xp
        if users[user_id].challenges['Исследуйте Хоккайдо'].completed == False and unlocked_locations == len(users[user_id].locations):
            context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Исследуйте Хоккайдо'].achieved(update=update, context=context), parse_mode='MarkdownV2')
            users[user_id].player_lvl += users[user_id].challenges['Исследуйте Хоккайдо'].xp
        if users[user_id].events['Убийство в сауне'].completed == False and users[user_id].player.current_location.name == 'Водоснабжение спа':
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите действие', reply_markup=sauna_kill_keyboard_1())
        elif users[user_id].events['Все цели убиты'].completed == True and (users[user_id].player.current_location.name == 'Канатная дорога' or users[user_id].player.current_location.name == 'Гараж' or users[user_id].player.current_location.name == 'Вертолетная площадка' or users[user_id].player.current_location.name == 'Горная тропа'):
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите действие', reply_markup=(exit_mission_keyboard(update=update, context=context)))
        elif users[user_id].events['Вырубить Джейсона'].completed == False and users[user_id].player.current_location.name == 'Холл' and users[user_id].player.disguise.name == 'VIP - пациент' and users[user_id].npcs['Jason Portman'].alive:
            users[user_id].events['Вырубить Джейсона'].completed = True
            context.bot.send_message(chat_id=update.effective_chat.id, text='Джейсон Портман: Эй, ты! Думаешь ты такой же фанат Хельмута, как и я?', reply_markup=(knock_jason_portman_keyboard_1()))
        elif  users[user_id].player.current_location.name == 'Холл' and users[user_id].player.disguise.name == 'Джейсон Портман':
            context.bot.send_message(chat_id=update.effective_chat.id, text='Врач: Наконец-то я вас нашла! Джейсон Портман, пожалуйста, проходите. Врач уже вас ожидает.', reply_markup=(medical_checkup_keyboard()))
        elif (users[user_id].items['Яд рыбы Фугу'] in users[user_id].player.inventory or users[user_id].items['Крысиный яд'] in users[user_id].player.inventory or users[user_id].items['Смертельный яд'] in users[user_id].player.inventory or users[user_id].items['Рвотный яд'] in users[user_id].player.inventory) and users[user_id].player.current_location.name == 'Ресторан' and users[user_id].events['Убийство ядом'].completed == False and users[user_id].targets['Yuki Yamazaki'].alive:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите действие', reply_markup=(sushi_kill_keyboard_1(update=update, context=context)))
        elif users[user_id].player.current_location.name == 'Номер Юки Ямадзаки':
            if users[user_id].events['Сигареты на столе'].completed == False and users[user_id].items['Пачка сигарет'] in users[user_id].player.inventory:
                context.bot.send_message(chat_id=update.effective_chat.id, text='На столе находится пустая пачка сигарет.', reply_markup=(cigar_kill_keyboard_1()))
            elif users[user_id].events['Сигареты на столе'].completed and users[user_id].targets['Yuki Yamazaki'].alive:
                users[user_id].player.inventory.append(users[user_id].items['Пачка сигарет'])
                cigar_kill_1(update=update, context=context)
            else:
                return InlineKeyboardMarkup([
                [InlineKeyboardButton("Передвижение", callback_data="Передвижение"), InlineKeyboardButton("Взаимодействие", callback_data="Взаимодействие")],
                [InlineKeyboardButton("Инвентарь", callback_data="Инвентарь"), InlineKeyboardButton("Обыскать локацию", callback_data="Обыскать локацию")],
                [InlineKeyboardButton("Статус", callback_data="Статус"), InlineKeyboardButton("Испытания", callback_data="Испытания")],
                [InlineKeyboardButton("Сохранить и выйти", callback_data="Сохранить и выйти")]
            ])
        elif users[user_id].events['Отравить стволовые клетки'].completed == False and users[user_id].player.current_location.name == 'Операционная' and users[user_id].items['Стволовые клетки'] in users[user_id].player.inventory:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Ввести смертельные стволовые клетки?', reply_markup=stem_cells_keyboard())
        elif users[user_id].events['Убийство в операционной'].completed == False and users[user_id].player.current_location.name == 'Операционная' and users[user_id].player.disguise.name == 'Главный хирург' and users[user_id].targets['Erich Soders'].alive:
            context.bot.send_message(chat_id=update.effective_chat.id, text='В операционной находится пульт управления робо-руками, проводящими операцию.', reply_markup=robot_kill_keyboard_1())
        elif users[user_id].events['Устранение главного хирурга'].completed == False and users[user_id].player.current_location.name == 'Вертолетная площадка' and users[user_id].player.disguise.name == 'Пилот' and users[user_id].npcs['Nicholas Laurent'].alive:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Главный хирург вышел из мед-комплекса\n\nГлавный хирург: У тебя еще остались те таблетки?\n47-й: Конечно, следуй за мной.', reply_markup=surgeon_knock_out_keyboard_1())
            users[user_id].events['Устранение главного хирурга'].completed = True
        elif users[user_id].events['Убийство во время йоги'].completed == False and users[user_id].player.current_location.name == 'Зона отдыха' and users[user_id].player.disguise.name == 'Инструктор по йоге' and users[user_id].targets['Yuki Yamazaki'].alive:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Юки Ямадзаки: Наконец-то, сколько можно вас ждать!', reply_markup=yoga_kill_keyboard_1())
            users[user_id].events['Убийство во время йоги'].completed = True
        else:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton("Передвижение", callback_data="Передвижение"), InlineKeyboardButton("Взаимодействие", callback_data="Взаимодействие")],
                [InlineKeyboardButton("Инвентарь", callback_data="Инвентарь"), InlineKeyboardButton("Обыскать локацию", callback_data="Обыскать локацию")],
                [InlineKeyboardButton("Статус", callback_data="Статус"), InlineKeyboardButton("Испытания", callback_data="Испытания")],
                [InlineKeyboardButton("Сохранить и выйти", callback_data="Сохранить и выйти")]
            ])
    elif users[user_id].mission == 'ica':
        if users[user_id].events['Сбросить шлюпку'].completed == False and users[user_id].player.current_location.name == 'Капитанский мостик':
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите действие', reply_markup=lifeboat_kill_keyboard_1())
        elif users[user_id].events['Все цели убиты'].completed == True and (users[user_id].player.current_location.name == 'Пирс' or users[user_id].player.current_location.name == 'Капитанский мостик'):
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите действие', reply_markup=(exit_mission_keyboard(update=update, context=context)))
        elif users[user_id].events['Встреча'].completed == False and users[user_id].player.current_location.name == users[user_id].targets['Kalvin Ritter'].move(users[user_id].time) and users[user_id].player.disguise.name == 'Терри Норфолк' and users[user_id].targets['Kalvin Ritter'].alive:
            context.bot.send_message(chat_id=update.effective_chat.id, text='47-й: Мистер Риттер, я Терри Норфолк.\nКэлвин Риттер: Мистер Норфолк! Наконец-то мы встретились. Пройдемте за мной.', reply_markup=private_meeting_keyboard_1())
            users[user_id].events['Встреча'].completed = True
        elif users[user_id].items['Крысиный яд'] in users[user_id].player.inventory and users[user_id].player.current_location.name == 'Бар' and users[user_id].events['Отравить напиток'].completed == False and users[user_id].targets['Kalvin Ritter'].alive:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите действие', reply_markup=(drink_kill_keyboard_1(update=update, context=context)))
        else:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton("Передвижение", callback_data="Передвижение"), InlineKeyboardButton("Взаимодействие", callback_data="Взаимодействие")],
                [InlineKeyboardButton("Инвентарь", callback_data="Инвентарь"), InlineKeyboardButton("Обыскать локацию", callback_data="Обыскать локацию")],
                [InlineKeyboardButton("Статус", callback_data="Статус"), InlineKeyboardButton("Испытания", callback_data="Испытания")],
                [InlineKeyboardButton("Сохранить и выйти", callback_data="Сохранить и выйти")]
            ])

def skip_choose_action_keyboard(update: Update, context: CallbackContext, skip_sauna=False, skip_hokkaido_exit=False, skip_sushi=False, skip_cigars_1=False, skip_cigars_2=False, skip_cells=False, skip_operation=False, skip_lifeboat=False, skip_ica_exit=False, skip_drink=False):
    user_id = update.callback_query.from_user['id']
    if users[user_id].mission == 'hokkaido':
        if users[user_id].disguises['Охранник'] in users[user_id].player.found_disguises or users[user_id].disguises['Телохранитель'] in users[user_id].player.found_disguises:
            users[user_id].player.inventory.append(users[user_id].items['Bartoli 75R'])
    elif users[user_id].mission == 'ica':
        if users[user_id].disguises['Охранник яхты'] in users[user_id].player.found_disguises or users[user_id].disguises['Телохранитель'] in users[user_id].player.found_disguises:
            users[user_id].player.inventory.append(users[user_id].items['Bartoli 75R'])
    unlocked_disguises = 0
    for i in list(users[user_id].disguises.values()):
        if i.unlocked:
            unlocked_disguises += 1
    unlocked_locations = 0
    for i in list(users[user_id].locations.values()):
        if i.unlocked:
            unlocked_locations += 1
    if users[user_id].mission == 'hokkaido':
        if users[user_id].challenges['Хамелеон'].completed == False and unlocked_disguises == len(users[user_id].disguises):
            context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Хамелеон'].achieved(update=update, context=context), parse_mode='MarkdownV2')
            users[user_id].player_lvl += users[user_id].challenges['Хамелеон'].xp
        if users[user_id].challenges['Исследуйте Хоккайдо'].completed == False and unlocked_locations == len(users[user_id].locations):
            context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Исследуйте Хоккайдо'].achieved(update=update, context=context), parse_mode='MarkdownV2')
            users[user_id].player_lvl += users[user_id].challenges['Исследуйте Хоккайдо'].xp
        if users[user_id].events['Убийство в сауне'].completed == False and users[user_id].player.current_location.name == 'Водоснабжение спа' and skip_sauna == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите действие', reply_markup=sauna_kill_keyboard_1())
        elif users[user_id].events['Все цели убиты'].completed == True and (users[user_id].player.current_location.name == 'Канатная дорога' or users[user_id].player.current_location.name == 'Гараж' or users[user_id].player.current_location.name == 'Вертолетная площадка' or users[user_id].player.current_location.name == 'Горная тропа') and skip_hokkaido_exit == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите действие', reply_markup=(exit_mission_keyboard(update=update, context=context)))
        elif users[user_id].events['Вырубить Джейсона'].completed == False and users[user_id].player.current_location.name == 'Холл' and users[user_id].player.disguise.name == 'VIP - пациент' and users[user_id].npcs['Jason Portman'].alive:
            users[user_id].events['Вырубить Джейсона'].completed = True
            context.bot.send_message(chat_id=update.effective_chat.id, text='Джейсон Портман: Эй, ты! Думаешь ты такой же фанат Хельмута, как и я?', reply_markup=(knock_jason_portman_keyboard_1()))
        elif  users[user_id].player.current_location.name == 'Холл' and users[user_id].player.disguise.name == 'Джейсон Портман' and users[user_id].events['Обследование'].completed == False:
            users[user_id].events['Обследование'].completed = True
            context.bot.send_message(chat_id=update.effective_chat.id, text='Врач: Наконец-то я вас нашла! Джейсон Портман, пожалуйста, проходите. Врач уже вас ожидает.', reply_markup=(medical_checkup_keyboard()))
        elif (users[user_id].items['Яд рыбы Фугу'] in users[user_id].player.inventory or users[user_id].items['Крысиный яд'] in users[user_id].player.inventory or users[user_id].items['Смертельный яд'] in users[user_id].player.inventory or users[user_id].items['Рвотный яд'] in users[user_id].player.inventory) and users[user_id].player.current_location.name == 'Ресторан' and users[user_id].events['Убийство ядом'].completed == False and users[user_id].targets['Yuki Yamazaki'].alive and skip_sushi == False:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите действие', reply_markup=(sushi_kill_keyboard_1(update=update, context=context)))
        elif users[user_id].player.current_location.name == 'Номер Юки Ямадзаки':
            if users[user_id].events['Сигареты на столе'].completed == False and users[user_id].items['Пачка сигарет'] in users[user_id].player.inventory and skip_cigars_1 == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text='На столе находится пустая пачка сигарет.', reply_markup=(cigar_kill_keyboard_1()))
            elif users[user_id].events['Сигареты на столе'].completed and users[user_id].targets['Yuki Yamazaki'].alive and skip_cigars_2 == False:
                users[user_id].player.inventory.append(users[user_id].items['Пачка сигарет'])
                cigar_kill_1(update=update, context=context)
            else:
                return InlineKeyboardMarkup([
                [InlineKeyboardButton("Передвижение", callback_data="Передвижение"), InlineKeyboardButton("Взаимодействие", callback_data="Взаимодействие")],
                [InlineKeyboardButton("Инвентарь", callback_data="Инвентарь"), InlineKeyboardButton("Обыскать локацию", callback_data="Обыскать локацию")],
                [InlineKeyboardButton("Статус", callback_data="Статус"), InlineKeyboardButton("Испытания", callback_data="Испытания")],
                [InlineKeyboardButton("Сохранить и выйти", callback_data="Сохранить и выйти")]
            ])
        elif users[user_id].events['Отравить стволовые клетки'].completed == False and users[user_id].player.current_location.name == 'Операционная' and users[user_id].items['Стволовые клетки'] in users[user_id].player.inventory and skip_cells == False:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Ввести смертельные стволовые клетки?', reply_markup=stem_cells_keyboard())
        elif users[user_id].events['Убийство в операционной'].completed == False and users[user_id].player.current_location.name == 'Операционная' and users[user_id].player.disguise.name == 'Главный хирург' and users[user_id].targets['Erich Soders'].alive and skip_operation == False:
            context.bot.send_message(chat_id=update.effective_chat.id, text='В операционной находится пульт управления робо-руками, проводящими операцию.', reply_markup=robot_kill_keyboard_1())
        elif users[user_id].events['Устранение главного хирурга'].completed == False and users[user_id].player.current_location.name == 'Вертолетная площадка' and users[user_id].player.disguise.name == 'Пилот' and users[user_id].npcs['Nicholas Laurent'].alive:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Главный хирург вышел из мед-комплекса\n\nГлавный хирург: У тебя еще остались те таблетки?\n47-й: Конечно, следуй за мной.', reply_markup=surgeon_knock_out_keyboard_1())
            users[user_id].events['Устранение главного хирурга'].completed = True
        elif users[user_id].events['Убийство во время йоги'].completed == False and users[user_id].player.current_location.name == 'Зона отдыха' and users[user_id].player.disguise.name == 'Инструктор по йоге' and users[user_id].targets['Yuki Yamazaki'].alive:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Юки Ямадзаки: Наконец-то, сколько можно вас ждать!', reply_markup=yoga_kill_keyboard_1())
            users[user_id].events['Убийство во время йоги'].completed = True
        else:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton("Передвижение", callback_data="Передвижение"), InlineKeyboardButton("Взаимодействие", callback_data="Взаимодействие")],
                [InlineKeyboardButton("Инвентарь", callback_data="Инвентарь"), InlineKeyboardButton("Обыскать локацию", callback_data="Обыскать локацию")],
                [InlineKeyboardButton("Статус", callback_data="Статус"), InlineKeyboardButton("Испытания", callback_data="Испытания")],
                [InlineKeyboardButton("Сохранить и выйти", callback_data="Сохранить и выйти")]
            ])
    elif users[user_id].mission == 'ica':
        if users[user_id].events['Сбросить шлюпку'].completed == False and users[user_id].player.current_location.name == 'Капитанский мостик' and skip_lifeboat == False:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите действие', reply_markup=lifeboat_kill_keyboard_1())
        elif users[user_id].events['Все цели убиты'].completed == True and (users[user_id].player.current_location.name == 'Пирс' or users[user_id].player.current_location.name == 'Капитанский мостик') and skip_ica_exit == False:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите действие', reply_markup=(exit_mission_keyboard(update=update, context=context)))
        elif users[user_id].events['Встреча'].completed == False and users[user_id].player.current_location.name == users[user_id].targets['Kalvin Ritter'].move(users[user_id].time) and users[user_id].player.disguise.name == 'Терри Норфолк' and users[user_id].targets['Kalvin Ritter'].alive:
            context.bot.send_message(chat_id=update.effective_chat.id, text='47-й: Мистер Риттер, я Терри Норфолк.\nКэлвин Риттер: Мистер Норфолк! Наконец-то мы встретились. Пройдемте за мной.', reply_markup=private_meeting_keyboard_1())
            users[user_id].events['Встреча'].completed = True
        elif users[user_id].items['Крысиный яд'] in users[user_id].player.inventory and users[user_id].player.current_location.name == 'Бар' and users[user_id].events['Отравить напиток'].completed == False and users[user_id].targets['Kalvin Ritter'].alive and skip_drink == False:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите действие', reply_markup=(drink_kill_keyboard_1(update=update, context=context)))
        else:
            return InlineKeyboardMarkup([
                [InlineKeyboardButton("Передвижение", callback_data="Передвижение"), InlineKeyboardButton("Взаимодействие", callback_data="Взаимодействие")],
                [InlineKeyboardButton("Инвентарь", callback_data="Инвентарь"), InlineKeyboardButton("Обыскать локацию", callback_data="Обыскать локацию")],
                [InlineKeyboardButton("Статус", callback_data="Статус"), InlineKeyboardButton("Испытания", callback_data="Испытания")],
                [InlineKeyboardButton("Сохранить и выйти", callback_data="Сохранить и выйти")]
            ])

def challenges_keyboard(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    if users[user_id].mission == 'hokkaido':
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Убийства", callback_data='Убийства'), InlineKeyboardButton("Усложнения", callback_data='Усложнения')],
            [InlineKeyboardButton("Исследование", callback_data='Исследование'), InlineKeyboardButton("Классика", callback_data='Классика')],
            [InlineKeyboardButton("Выйти", callback_data='Выбор действия')]
            ])
    elif users[user_id].mission == 'ica':
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Убийства", callback_data='Убийства'), InlineKeyboardButton("Усложнения", callback_data='Усложнения')],
            [InlineKeyboardButton("Выйти", callback_data='Выбор действия')]
            ])

def challenges_section_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='Испытания')]])

def choose_start_location_keyboard(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    options = []
    if users[user_id].mission == 'hokkaido':
        for i in range(1, 10):
            if i <= users[user_id].player_lvl // 6:
                options.append(hokkaido_lvl_unlocks[i][0])
    return InlineKeyboardMarkup(make_keyboard_two_rows(options, 'CSL'))

def choose_start_item_keyboard_1(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    keyboard = make_keyboard_two_rows(users[user_id].carry_on_items, 'choose_item_1')
    keyboard.append([InlineKeyboardButton("Не брать снаряжение 1", callback_data="choose_item_1")])
    return InlineKeyboardMarkup(keyboard)

def choose_start_item_keyboard_2(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    keyboard = make_keyboard_two_rows(users[user_id].carry_on_items, 'choose_item_2')
    keyboard.append([InlineKeyboardButton("Не брать снаряжение 2", callback_data="choose_item_2")])
    return InlineKeyboardMarkup(keyboard)

def attack_keyboard(npc=None, location=None):
    return InlineKeyboardMarkup([[InlineKeyboardButton(f"Напасть (3/10)", callback_data=f"НПД{npc.name}:{location.name}"), InlineKeyboardButton("Уйти", callback_data=f"Выбор действия")]])

def hide_keyboard(npc=None, location=None):
    return InlineKeyboardMarkup([[InlineKeyboardButton(f"Напасть (3/10)", callback_data=f"НПД{npc.name}:{location.name}"), InlineKeyboardButton("Скрыться (7/10)", callback_data=f"Скрыться")]])

def no_disguise_move_keyboard(chance, location):
    return InlineKeyboardMarkup([[InlineKeyboardButton(f"Да ({10-chance}/10)", callback_data=f"ПРТ{10 - chance}:{location.name}"), InlineKeyboardButton("Нет", callback_data=f"Передвижение")]])

def inventory_keyboard(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    inventory = []
    if users[user_id].player.inventory.count(users[user_id].player.item) == 0:
        users[user_id].player.item = users[user_id].items['Нет предмета']
    for i in users[user_id].player.inventory:
        if i.name == 'Bartoli 75R' or i.name == 'ICA 19':
            inventory.append(i.name + ' (1)')
        else:
            inventory.append(i.name + ' (' + str(users[user_id].player.inventory.count(i)) + ')')
    inventory = list(set(inventory))
    if len(inventory) > 3:
        keyboard = make_keyboard_two_rows(inventory, '')
    else:
        keyboard = make_keyboard(inventory, '')
    if users[user_id].player.item.name != 'Нет предмета':
        keyboard.append([InlineKeyboardButton('Убрать предмет из рук', callback_data='Убрать предмет из рук')])
    keyboard.append([InlineKeyboardButton('Сменить маскировку', callback_data='МАСК')])
    keyboard.append([InlineKeyboardButton(f"Выйти", callback_data=f"Выбор действия")])
    return InlineKeyboardMarkup(keyboard)

def disguise_keyboard(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    return InlineKeyboardMarkup(make_keyboard([i.name for i in users[user_id].player.found_disguises], 'МСК'))

def choose_illegal_item_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Да', callback_data='ВНО'), InlineKeyboardButton(f"Нет", callback_data=f"Инвентарь")]])

def choose_weapon_keyboard(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    weapons = ['Нет предмета']
    for i in users[user_id].player.inventory:
        if i.weapon:
            weapons.append(i.name)
    if len(weapons) > 3:
        return InlineKeyboardMarkup(make_keyboard_two_rows(weapons, 'WP'))
    else:
        return InlineKeyboardMarkup(make_keyboard(weapons, 'WP'))

def combat_start_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Прятаться (5/10)', callback_data='Прятаться'), InlineKeyboardButton(f"Напасть", callback_data=f"Напасть")]])

def choose_weapon_action_keyboard(update: Update, context: CallbackContext, item_name: str):
    user_id = update.callback_query.from_user['id']
    actions = []
    current_weapon = users[user_id].items[item_name.replace('WP', '')]
    for i in current_weapon.usage:
        if i == 'Выстрелить':
            actions.append('Выстрелить (9/10)')
        elif i == 'Ударить':
            actions.append('Ударить (5/10)')
        elif i == 'Бросить':
            actions.append('Бросить (7/10)')
        elif i == 'Ударить (летально)':
            actions.append('Ударить (летально) (6/10)')
        elif i == 'Бросить (летально)':
            actions.append('Бросить (летально) (8/10)')
        elif i == 'Усмирить':
            actions.append('Усмирить (3/10)')
        elif i == 'Задушить':
            actions.append('Задушить (4/10)')
    users[user_id].player.item = current_weapon
    keyboard = make_keyboard(actions, 'CWA')
    keyboard.append([InlineKeyboardButton('Назад', callback_data='Выбор оружия')])
    return InlineKeyboardMarkup(keyboard)

def interact_menu_keyboard(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    keyboard = [[InlineKeyboardButton(f"Назад", callback_data=f"Выбор действия")]]
    if users[user_id].player.item.usage == []:
        return InlineKeyboardMarkup(keyboard)
    return InlineKeyboardMarkup(make_keyboard(users[user_id].player.item.usage, 'ITR') + keyboard)

def kill_keyboard(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    location_npcs = []
    location_disguises = []
    for i in find_location_npcs(update=update, context=context, location=users[user_id].player.current_location):
        location_disguises.append(i.disguise.name)
        location_npcs.append(i.name)
    for i in list(users[user_id].targets.values()):
        if i.move(users[user_id].time) == users[user_id].player.current_location.name and i.alive == True:
            location_disguises.append(i.name)
            location_npcs.append(i.name)
    npc_disguises = {}
    for i in location_disguises:
        npc_disguises[i] = 1
    npcs = []
    npc_values = []
    for i in range(len(location_npcs)):
        if location_disguises[i] in ['Джейсон Портман', 'Амос Декстер', 'Терри Норфолк'] or location_disguises[i] in list(users[user_id].targets.keys()):
            npcs.append(f"{location_disguises[i]}")
        else:
            npcs.append(f"{location_disguises[i]} {npc_disguises[location_disguises[i]]}")
        npc_disguises[location_disguises[i]] += 1
        npc_values.append(location_npcs[i])
    keyboard = []
    if len(npcs) > 3:
        if len(npcs) % 2 == 0:
            for i in range(0, len(npcs), 2):
                keyboard.append([InlineKeyboardButton(f'{npcs[i]}', callback_data=f'{npc_values[i]}' + 'KILL'), InlineKeyboardButton(f'{npcs[i + 1]}', callback_data=f'{npc_values[i + 1]}' + 'KILL')])
        else:
            for i in range(0, len(npcs) - 1, 2):
                keyboard.append([InlineKeyboardButton(f'{npcs[i]}', callback_data=f'{npc_values[i]}' + 'KILL'), InlineKeyboardButton(f'{npcs[i + 1]}', callback_data=f'{npc_values[i + 1]}' + 'KILL')])
            keyboard.append([InlineKeyboardButton(f'{npcs[-1]}', callback_data=f'{npc_values[-1]}' + 'KILL')])
    else:
        for i in range(len(npcs)):
            keyboard.append([InlineKeyboardButton(f"{npcs[i]}", callback_data=npc_values[i] + 'KILL')])
    keyboard.append([InlineKeyboardButton(f"Отменить действие", callback_data=f"Взаимодействие")])
    return InlineKeyboardMarkup(keyboard)

def knock_out_keyboard(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    location_npcs = []
    location_disguises = []
    for i in find_location_npcs(update=update, context=context, location=users[user_id].player.current_location):
        location_disguises.append(i.disguise.name)
        location_npcs.append(i.name)
    npc_disguises = {}
    for i in location_disguises:
        npc_disguises[i] = 1
    npcs = []
    npc_values = []
    for i in range(len(location_npcs)):
        if location_disguises[i] in ['Джейсон Портман', 'Амос Декстер', 'Терри Норфолк']:
            npcs.append(f"{location_disguises[i]}")
        else:
            npcs.append(f"{location_disguises[i]} {npc_disguises[location_disguises[i]]}")
        npc_disguises[location_disguises[i]] += 1
        npc_values.append(location_npcs[i])
    keyboard = []
    if len(npcs) > 3:
        if len(npcs) % 2 == 0:
            for i in range(0, len(npcs), 2):
                keyboard.append([InlineKeyboardButton(f'{npcs[i]}', callback_data=f'{npc_values[i]}' + 'KNOCK'), InlineKeyboardButton(f'{npcs[i + 1]}', callback_data=f'{npc_values[i + 1]}' + 'KNOCK')])
        else:
            for i in range(0, len(npcs) - 1, 2):
                keyboard.append([InlineKeyboardButton(f'{npcs[i]}', callback_data=f'{npc_values[i]}' + 'KNOCK'), InlineKeyboardButton(f'{npcs[i + 1]}', callback_data=f'{npc_values[i + 1]}' + 'KNOCK')])
            keyboard.append([InlineKeyboardButton(f'{npcs[-1]}', callback_data=f'{npc_values[-1]}' + 'KNOCK')])
    else:
        for i in range(len(npcs)):
            keyboard.append([InlineKeyboardButton(f"{npcs[i]}", callback_data=npc_values[i] + 'KNOCK')])
    keyboard.append([InlineKeyboardButton(f"Отменить действие", callback_data=f"Взаимодействие")])
    return InlineKeyboardMarkup(keyboard)

def distract_keyboard(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    if find_location_npcs(update=update, context=context, location=users[user_id].player.current_location) == []:
            return InlineKeyboardMarkup([[InlineKeyboardButton("Выйти", callback_data='Взаимодействие')]])
    elif len(find_location_npcs(update=update, context=context, location=users[user_id].player.current_location)) > 3:
        return InlineKeyboardMarkup([[InlineKeyboardButton("Отвлечь для перемещения", callback_data='safe_move')], [InlineKeyboardButton("Отменить действие", callback_data='Взаимодействие')]])
    else:
        location_npcs = []
        location_disguises = []
        for i in find_location_npcs(update=update, context=context, location=users[user_id].player.current_location):
            location_disguises.append(i.disguise.name)
            location_npcs.append(i.name)
        keyboard = []
        for i in range(len(location_npcs)):
            keyboard.append([InlineKeyboardButton(f"{location_disguises[i]}", callback_data=location_npcs[i] + 'DIS')])
        keyboard.append([InlineKeyboardButton("Отвлечь для перемещения", callback_data='safe_move')])
        return InlineKeyboardMarkup(keyboard)
    
def confirm_kill_keyboard(npc, witnesses):
    return InlineKeyboardMarkup([[InlineKeyboardButton('Убить', callback_data=npc.replace('KILL', f'con_kill{witnesses}'))], [InlineKeyboardButton('Назад', callback_data=f"Взаимодействие")]])

def confirm_knock_keyboard(npc, witnesses):
    return InlineKeyboardMarkup([[InlineKeyboardButton('Вырубить', callback_data=npc.replace('KNOCK', f'con_knock{witnesses}'))], [InlineKeyboardButton('Назад', callback_data=f"Взаимодействие")]])

def confirm_distract_keyboard(npc):
    return InlineKeyboardMarkup([[InlineKeyboardButton('Вырубить', callback_data=npc.replace('DIS', 'CDKN')), InlineKeyboardButton('Убить', callback_data=npc.replace('DIS', 'CDKL'))], [InlineKeyboardButton('Назад', callback_data=f"Взаимодействие")]])

def save_and_quit_confirm_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Да', callback_data='Конец игры'), InlineKeyboardButton('Нет', callback_data='Выбор действия')]])

def destroy_heart_keyboard_1():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Да', callback_data='DH1'), InlineKeyboardButton('Нет', callback_data='Выбор действия')]])

def destroy_heart_keyboard_2():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Повредить сердце', callback_data='DH2')], [InlineKeyboardButton('Уйти', callback_data='Выбор действия')]])

def exit_mission_keyboard(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    return InlineKeyboardMarkup([[InlineKeyboardButton('Завершить миссию', callback_data='Завершить миссию')], [InlineKeyboardButton('Назад', callback_data='SKIP' + users[user_id].mission + '_exit')]])

def destroy_servers_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Повредить серверы', callback_data='Повредить серверы'), InlineKeyboardButton('Назад', callback_data='Выбор действия')]])

def lifeboat_kill_keyboard_1():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Сбросить шлюпку', callback_data='СБШР')], [InlineKeyboardButton('Назад', callback_data='SKIPlifeboat')]])

def sauna_kill_keyboard_1():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Увеличить температуру воды', callback_data='УТВ')], [InlineKeyboardButton('Назад', callback_data='SKIPsauna')]])

def sauna_kill_keyboard_2():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Запереть дверь в парилку', callback_data='ЗДП')], [InlineKeyboardButton('Назад', callback_data='Выбор действия')]])

def robot_kill_keyboard_1():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Взять управление', callback_data='Взять управление'), InlineKeyboardButton('Назад', callback_data='SKIPoperation')]])

def robot_kill_keyboard_2():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Убить Эриха Содерса', callback_data='УЭС')], [InlineKeyboardButton('Назад', callback_data='SKIPoperation')]])

def surgeon_knock_out_keyboard_1():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Пойти в комнату пилота', callback_data='ПКП')], [InlineKeyboardButton('Уйти', callback_data='Выбор действия')]])

def surgeon_knock_out_keyboard_2():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Усмирить главного хирурга', callback_data='УГХ')], [InlineKeyboardButton('Убить главного хирурга', callback_data='УГХсм')], [InlineKeyboardButton('Уйти', callback_data='Выбор действия')]])

def private_meeting_keyboard_1():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Пойти в офис Риттера', callback_data='ПВОР')], [InlineKeyboardButton('Уйти', callback_data='Выбор действия')]])

def private_meeting_keyboard_2():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Задушить цель удавкой', callback_data='ЗЦУ')], [InlineKeyboardButton('Застрелить цель из пистолета', callback_data='ЗЦИП')], [InlineKeyboardButton('Уйти', callback_data='Выбор действия')]])

def yoga_kill_keyboard_1():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Начать тренировку', callback_data='Начать тренировку')], [InlineKeyboardButton('Уйти', callback_data='Выбор действия')]])

def yoga_kill_keyboard_2():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Толкнуть Юки Ямадзаки', callback_data='ТЮЯ')], [InlineKeyboardButton('Завершить тренировку', callback_data='Выбор действия')]])

def sushi_kill_keyboard_1(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    if users[user_id].player.disguise.name == 'Шеф':
        return InlineKeyboardMarkup([[InlineKeyboardButton('Отравить роллы', callback_data='ОР')], [InlineKeyboardButton('Назад', callback_data='SKIPsushi')]])
    else:
        return InlineKeyboardMarkup([[InlineKeyboardButton('Отравить роллы (3/10)', callback_data='ОР')], [InlineKeyboardButton('Назад', callback_data='SKIPsushi')]])

def sushi_kill_keyboard_2(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    poisons = [users[user_id].items['Яд рыбы Фугу'], users[user_id].items['Крысиный яд'], users[user_id].items['Смертельный яд'], users[user_id].items['Рвотный яд']]
    gained_poisons = []
    for i in poisons:
        if i in users[user_id].player.inventory:
            gained_poisons.append(i.name)
    keyboard = make_keyboard(gained_poisons, 'ОСЮ')
    keyboard.append([InlineKeyboardButton('Назад', callback_data='SKIPsushi')])
    return InlineKeyboardMarkup(keyboard)

def sushi_kill_keyboard_3():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Пойти за целью', callback_data='Пойти за целью')], [InlineKeyboardButton('Остаться', callback_data='Выбор действия')]])

def sushi_kill_keyboard_4():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Утопить цель', callback_data='Утопить цель')], [InlineKeyboardButton('Уйти', callback_data='Выбор действия')]])

def drink_kill_keyboard_1(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    if users[user_id].player.disguise.name == 'Экипаж яхты':
        return InlineKeyboardMarkup([[InlineKeyboardButton('Отравить напиток', callback_data='ОНАП')], [InlineKeyboardButton('Назад', callback_data='SKIPdrink')]])
    else:
        return InlineKeyboardMarkup([[InlineKeyboardButton('Отравить роллы (3/10)', callback_data='ОНАП')], [InlineKeyboardButton('Назад', callback_data='SKIPdrink')]])

def drink_kill_keyboard_2():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Пойти за целью', callback_data='Пойти за Кэлвином')], [InlineKeyboardButton('Остаться', callback_data='Выбор действия')]])

def drink_kill_keyboard_3():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Утопить цель', callback_data='Утопить Кэлвина')], [InlineKeyboardButton('Уйти', callback_data='Выбор действия')]])

def cigar_kill_keyboard_1():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Положить новую пачку', callback_data='ПНПС')], [InlineKeyboardButton('Назад', callback_data='SKIPcigars_1')]])

def cigar_kill_keyboard_2():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Пойти на балкон', callback_data='ПНБ')], [InlineKeyboardButton('Назад', callback_data='SKIPcigars_2')]])

def cigar_kill_keyboard_3():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Создать утечку газа', callback_data='СУГ')], [InlineKeyboardButton('Подождать Юки Ямадзаки', callback_data='ПЮЯ')], [InlineKeyboardButton('Уйти с балкона', callback_data='Выбор действия')]])

def cigar_kill_keyboard_4():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Уйти с балкона', callback_data='УСБ')]])

def cigar_kill_keyboard_5():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Толкнуть Юки Ямадзаки', callback_data='ТЮЯС')], [InlineKeyboardButton('Уйти с балкона', callback_data='Выбор действия')]])

def hokkaido_briefing_keyboard_1(update: Update, context: CallbackContext):
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('hitman_tg_bot/assets/hokkaido.png', 'rb'), timeout=1000)
    return InlineKeyboardMarkup([[InlineKeyboardButton('Далее', callback_data='hokkaido_briefing_2')]])

def hokkaido_briefing_keyboard_2(update: Update, context: CallbackContext):
    context.bot.send_photo(chat_id=update.effective_chat.id, photo='https://static.wikia.nocookie.net/hitman/images/2/2d/H2018-Erich-Soders-Intel-Card.png/revision/latest?cb=20220601174305')
    return InlineKeyboardMarkup([[InlineKeyboardButton('Далее', callback_data='hokkaido_briefing_3')]])

def hokkaido_briefing_keyboard_3(update: Update, context: CallbackContext):
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('hitman_tg_bot/assets/equipment.png', 'rb'), timeout=1000)
    return InlineKeyboardMarkup([[InlineKeyboardButton('Далее', callback_data='hokkaido_briefing_4')]])

def hokkaido_briefing_keyboard_4(update: Update, context: CallbackContext):
    context.bot.send_photo(chat_id=update.effective_chat.id, photo='https://static.wikia.nocookie.net/hitman/images/a/a8/H2018-Yuki-Yamazaki-Intel-Card.png/revision/latest?cb=20220601174346')
    return InlineKeyboardMarkup([[InlineKeyboardButton('Далее', callback_data='hokkaido_briefing_5')]])

def hokkaido_briefing_keyboard_5(update: Update, context: CallbackContext):
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('hitman_tg_bot/assets/erich_yuki.png', 'rb'), timeout=1000)
    return InlineKeyboardMarkup([[InlineKeyboardButton('Далее', callback_data='hokkaido_briefing_6')]])

def hokkaido_briefing_keyboard_6(update: Update, context: CallbackContext):
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('hitman_tg_bot/assets/clock.png', 'rb'), timeout=1000)
    return InlineKeyboardMarkup([[InlineKeyboardButton('Подготовка к миссии', callback_data='Выбор снаряжения')]])

def start_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Комплекс МКА, ЗАСЕКРЕЧЕНО', callback_data='МКАЗАС')], [InlineKeyboardButton('Хоккайдо, Япония', callback_data='ХоккЯП')]])

def choose_tutorial_keyboard():
    #[InlineKeyboardButton('Тренировка под наблюдением', callback_data='ТПН')], 
    return InlineKeyboardMarkup([[InlineKeyboardButton('Свободная тренировка', callback_data='СТ')]])

def start_tutorial_keyboard_1():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Брифинг', callback_data='ica_briefing_1')], [InlineKeyboardButton('Начать игру', callback_data='НАЧИТПН')]])

def start_tutorial_keyboard_2():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Брифинг', callback_data='ica_briefing_2')], [InlineKeyboardButton('Начать игру', callback_data='НАЧИСТ')]])

def ica_briefing_keyboard_1(update: Update, context: CallbackContext):
    context.bot.send_photo(chat_id=update.effective_chat.id, photo='https://static.wikia.nocookie.net/hitman/images/2/21/H2018-Kalvin-Ritter-Intel-Card.png/revision/latest?cb=20220601175436')
    return InlineKeyboardMarkup([[InlineKeyboardButton('Начать игру', callback_data='НАЧИТПН')]])

def ica_briefing_keyboard_2(update: Update, context: CallbackContext):
    context.bot.send_photo(chat_id=update.effective_chat.id, photo='https://static.wikia.nocookie.net/hitman/images/2/21/H2018-Kalvin-Ritter-Intel-Card.png/revision/latest?cb=20220601175436')
    return InlineKeyboardMarkup([[InlineKeyboardButton('Начать игру', callback_data='НАЧИСТ')]])

def knock_jason_portman_keyboard_1():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Пойти в укромное место', callback_data='ВДП')], [InlineKeyboardButton('Уйти', callback_data='Выбор действия')]])

def knock_jason_portman_keyboard_2():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Усмирить Джейсона Портмана', callback_data='УДП')], [InlineKeyboardButton('Убить Джейсона Портмана', callback_data='УДПсм')], [InlineKeyboardButton('Уйти', callback_data='Выбор действия')]])

def medical_checkup_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Проследовать за врачом', callback_data='ПЗВ')], [InlineKeyboardButton('Уйти', callback_data='Выбор действия')]])

def tutorial_keyboard_1():
    return InlineKeyboardMarkup([
            [InlineKeyboardButton("Передвижение", callback_data="pass"), InlineKeyboardButton("Взаимодействие", callback_data="pass")],
            [InlineKeyboardButton("Инвентарь", callback_data="pass"), InlineKeyboardButton("Обыскать локацию", callback_data="pass")],
            [InlineKeyboardButton("Статус", callback_data="tutorial_1"), InlineKeyboardButton("Испытания", callback_data="pass")],
            [InlineKeyboardButton("Сохранить и выйти", callback_data="pass")]
        ])

def accept_tutorial_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Да', callback_data='ТПН'), InlineKeyboardButton('Нет', callback_data='Отмена обучения')]])




#----------Пошаговое обучение----------

def tutorial_1(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    result_string = ''
    for i in list(users[user_id].targets.values()):
        if i.alive == True:
            result_string += f'{i.name}: {i.move(users[user_id].time)}\n'
        else:
            result_string += f'{i.name}: Цель устранена\n'
    result_string += f'\nТекущая маскировка: {users[user_id].player.disguise.name}\n'
    result_string += f'Предмет в руках: {users[user_id].player.item.name}'
    if int(5-(users[user_id].bodies*0.5)-(users[user_id].kills*0.7)-(users[user_id].suspicion_count*0.2)) == 5:
        result_string += f'\n\nБесшумный убийца'
    result_string = make_heading('Статус') + tg_text_convert(result_string)
    result_string += '\n\n\n' + location_status(update=update, context=context, location=users[user_id].player.current_location)
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Используя статус вы можете увидеть, где находится ваша цель, ваши текущие маскировку и предмет в руках, сохранён ли у вас статус бесшемного убийцы (статус прохождения на максимальный рейтинг) и состояние локации.')
    context.bot.send_message(chat_id=update.effective_chat.id, text=result_string, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Выйти", callback_data="tutorial_2")]
        ]), parse_mode='MarkdownV2')

def tutorial_2(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Диана: Отлично\, теперь постарайся найти для себя что\-нибудь полезное\.\n\n_Используйте Обыскать локацию\, чтобы подобрать все предметы на текущей локации\._', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Передвижение", callback_data="pass"), InlineKeyboardButton("Взаимодействие", callback_data="pass")],
            [InlineKeyboardButton("Инвентарь", callback_data="pass"), InlineKeyboardButton("Обыскать локацию", callback_data="tutorial_3")],
            [InlineKeyboardButton("Статус", callback_data="pass"), InlineKeyboardButton("Испытания", callback_data="pass")],
            [InlineKeyboardButton("Сохранить и выйти", callback_data="pass")]
        ]), parse_mode='MarkdownV2')
    
def tutorial_3(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = update.callback_query.from_user['id']
    users[user_id].time += 5
    query = update.callback_query
    query.answer()
    users[user_id].player.inventory += users[user_id].player.current_location.items
    result_string = ''
    if users[user_id].player.current_location.items == []:
        query.edit_message_text(text='На локации нет предметов\n', reply_markup=(choose_action_keyboard(update=update, context=context)))
    else:
        for i in list(users[user_id].items.values()):
            if i in users[user_id].player.current_location.items:
                result_string += f'{i.name} ({users[user_id].player.current_location.items.count(i)})\n'
        result_string = '*_Найдены предметы:_*\n\n' + tg_text_convert(result_string)
    result_string += '\nДиана: А ты быстро учишься\, теперь постарайся попасть в гараж\.'
    query.edit_message_text(text='Найденные предметы отображаются в виде списка и автоматически добавляются к вам в инвентарь.')
    context.bot.send_message(chat_id=update.effective_chat.id, text=result_string, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Передвижение", callback_data="tutorial_4"), InlineKeyboardButton("Взаимодействие", callback_data="pass")],
            [InlineKeyboardButton("Инвентарь", callback_data="pass"), InlineKeyboardButton("Обыскать локацию", callback_data="pass")],
            [InlineKeyboardButton("Статус", callback_data="pass"), InlineKeyboardButton("Испытания", callback_data="pass")],
            [InlineKeyboardButton("Сохранить и выйти", callback_data="pass")]
        ]), parse_mode='MarkdownV2')

def tutorial_4(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите локацию', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Гараж", callback_data="tutorial_5"), InlineKeyboardButton("Грузовой отсек", callback_data="pass")],
            [InlineKeyboardButton("Нижняя палуба", callback_data="pass"), InlineKeyboardButton("Главная палуба", callback_data="pass")],
            [InlineKeyboardButton("Отменить действие", callback_data="pass")]
        ]), parse_mode='MarkdownV2')

def tutorial_5(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Некоторые действия выполняются только с определенным шансом, написанным в скобках рядом с ним. Например сейчас вас никто не видит, поэтому шанс составляет 10/10, то есть вы без опаски можете переместиться на другую локацию.')
    context.bot.send_message(chat_id=update.effective_chat.id, text='У вас нет подходящей маскировки. Переместиться на локацию?', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Да (10/10)", callback_data="tutorial_6"), InlineKeyboardButton("Нет", callback_data="pass")]
        ]))
    
def tutorial_6(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    users[user_id].player.current_location = users[user_id].locations['Гараж']
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Используйте Взаимодействие, чтобы использовать тот предмет, который находится у вас в руках. Если в руках ничего нет, то вы сможете усмирить (нелетально) NPC на текущей локаци\._')
    context.bot.send_message(chat_id=update.effective_chat.id, text=location_status(users[user_id].player.current_location) + '\n\nДиана: Хорошо\, теперь устрани того механика\.', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Передвижение", callback_data="pass"), InlineKeyboardButton("Взаимодействие", callback_data="tutorial_7")],
            [InlineKeyboardButton("Инвентарь", callback_data="pass"), InlineKeyboardButton("Обыскать локацию", callback_data="pass")],
            [InlineKeyboardButton("Статус", callback_data="pass"), InlineKeyboardButton("Испытания", callback_data="pass")],
            [InlineKeyboardButton("Сохранить и выйти", callback_data="pass")]
        ]), parse_mode='MarkdownV2')
    
def tutorial_7(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите действие', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Усмирить", callback_data="tutorial_8")],
            [InlineKeyboardButton("Назад", callback_data="pass")]
        ]), parse_mode='MarkdownV2')

def tutorial_8(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите цель', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Механик", callback_data="tutorial_9")],
            [InlineKeyboardButton("Отменить действие", callback_data="pass")]
        ]), parse_mode='MarkdownV2')
    
def tutorial_9(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Действия видят 0 человек\n\nEwan Roberts (Механик)', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Вырубить", callback_data="tutorial_10")],
            [InlineKeyboardButton("Назад", callback_data="pass")]
        ]), parse_mode='MarkdownV2')
    
def tutorial_10(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    users[user_id].player.found_disguises.append(users[user_id].npcs['Ewan Roberts'].disguise)
    users[user_id].npcs['Ewan Roberts'].alive = False
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Используйте Инвентарь, чтобы открыть инвентарь и Сменить маскировку, чтобы сменить текущую маскировку на одну из тех, которые вы уже находили.')
    context.bot.send_message(chat_id=update.effective_chat.id, text='Цель устранена: Ewan Roberts', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Передвижение", callback_data="pass"), InlineKeyboardButton("Взаимодействие", callback_data="pass")],
            [InlineKeyboardButton("Инвентарь", callback_data="tutorial_11"), InlineKeyboardButton("Обыскать локацию", callback_data="pass")],
            [InlineKeyboardButton("Статус", callback_data="pass"), InlineKeyboardButton("Испытания", callback_data="pass")],
            [InlineKeyboardButton("Сохранить и выйти", callback_data="pass")]
        ]), parse_mode='MarkdownV2')
    
def tutorial_11(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    result_string = make_heading('Инвентарь')
    result_string += f'Сейчас в руках: {users[user_id].player.item.name}'
    query.edit_message_text(text=result_string, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("ICA 19 (1)", callback_data="pass")],
            [InlineKeyboardButton("Удавка (1)", callback_data="pass")],
            [InlineKeyboardButton("Монета (3)", callback_data="pass")],
            [InlineKeyboardButton("Сменить маскировку", callback_data="tutorial_12")],
            [InlineKeyboardButton("Выйти", callback_data="pass")]
        ]))
    
def tutorial_12(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Текущая маскировка: Тактическая водолазка', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Тактическая водолазка", callback_data="pass")],
            [InlineKeyboardButton("Механик", callback_data="tutorial_13")],
        ]), parse_mode='MarkdownV2')

def tutorial_13(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    users[user_id].player.disguise = users[user_id].disguises['Механик']
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Текущая маскировка: Механик\n\nДиана: Переоделся в механика? Интересно... Что ж, это позволит тебе пробраться на судно. Пройди через грузовой отсек и выйди на главную палубу.', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Передвижение", callback_data="tutorial_14"), InlineKeyboardButton("Взаимодействие", callback_data="pass")],
            [InlineKeyboardButton("Инвентарь", callback_data="pass"), InlineKeyboardButton("Обыскать локацию", callback_data="pass")],
            [InlineKeyboardButton("Статус", callback_data="pass"), InlineKeyboardButton("Испытания", callback_data="pass")],
            [InlineKeyboardButton("Сохранить и выйти", callback_data="pass")]
        ]))

def tutorial_14(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите локацию', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Пирс", callback_data="pass")],
            [InlineKeyboardButton("Грузовой отсек", callback_data="tutorial_15")],
            [InlineKeyboardButton("Отменить действие", callback_data="pass")]
        ]), parse_mode='MarkdownV2')
    
def tutorial_15(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    users[user_id].player.current_location = users[user_id].locations['Грузовой отсек']
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=location_status(users[user_id].player.current_location), reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Передвижение", callback_data="tutorial_16"), InlineKeyboardButton("Взаимодействие", callback_data="pass")],
            [InlineKeyboardButton("Инвентарь", callback_data="pass"), InlineKeyboardButton("Обыскать локацию", callback_data="pass")],
            [InlineKeyboardButton("Статус", callback_data="pass"), InlineKeyboardButton("Испытания", callback_data="pass")],
            [InlineKeyboardButton("Сохранить и выйти", callback_data="pass")]
        ]), parse_mode='MarkdownV2')

def tutorial_16(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите локацию', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Пирс", callback_data="pass"), InlineKeyboardButton("Гараж", callback_data="pass")],
            [InlineKeyboardButton("Моторный отсек", callback_data="pass"), InlineKeyboardButton("Главная палуба", callback_data="tutorial_17")],
            [InlineKeyboardButton("Отменить действие", callback_data="pass")]
        ]), parse_mode='MarkdownV2')
    
def tutorial_17(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    users[user_id].player.current_location = users[user_id].locations['Главная палуба']
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=location_status(users[user_id].player.current_location) + '\n\nДиана: Похоже дальше охрана тебя не пропустит\, может ещё раз сделаешь этот трюк с переодеванием\? Мне кажется на кухне есть тот\, кто тебе нужен\.', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Передвижение", callback_data="tutorial_18"), InlineKeyboardButton("Взаимодействие", callback_data="pass")],
            [InlineKeyboardButton("Инвентарь", callback_data="pass"), InlineKeyboardButton("Обыскать локацию", callback_data="pass")],
            [InlineKeyboardButton("Статус", callback_data="pass"), InlineKeyboardButton("Испытания", callback_data="pass")],
            [InlineKeyboardButton("Сохранить и выйти", callback_data="pass")]
        ]), parse_mode='MarkdownV2')

def tutorial_18(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите локацию', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Пирс", callback_data="pass"), InlineKeyboardButton("Грузовой отсек", callback_data="pass")],
            [InlineKeyboardButton("Нижняя палуба", callback_data="pass"), InlineKeyboardButton("Кухня", callback_data="tutorial_19")],
            [InlineKeyboardButton("Бар", callback_data="pass"), InlineKeyboardButton("Верхняя палуба", callback_data="pass")],
            [InlineKeyboardButton("Отменить действие", callback_data="pass")]
        ]), parse_mode='MarkdownV2')
    
def tutorial_19(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    users[user_id].player.current_location = users[user_id].locations['Кухня']
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=location_status(users[user_id].player.current_location), reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Передвижение", callback_data="pass"), InlineKeyboardButton("Взаимодействие", callback_data="tutorial_20")],
            [InlineKeyboardButton("Инвентарь", callback_data="pass"), InlineKeyboardButton("Обыскать локацию", callback_data="pass")],
            [InlineKeyboardButton("Статус", callback_data="pass"), InlineKeyboardButton("Испытания", callback_data="pass")],
            [InlineKeyboardButton("Сохранить и выйти", callback_data="pass")]
        ]), parse_mode='MarkdownV2')
    
def tutorial_20(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите действие', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Усмирить", callback_data="tutorial_21")],
            [InlineKeyboardButton("Назад", callback_data="pass")]
        ]), parse_mode='MarkdownV2')

def tutorial_21(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите цель', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Экпипаж яхты", callback_data="tutorial_22")],
            [InlineKeyboardButton("Отменить действие", callback_data="pass")]
        ]), parse_mode='MarkdownV2')
    
def tutorial_22(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Действия видят 0 человек\n\nJames Potts (Экипаж яхты)', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Вырубить", callback_data="tutorial_23")],
            [InlineKeyboardButton("Назад", callback_data="pass")]
        ]), parse_mode='MarkdownV2')
    
def tutorial_23(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    users[user_id].player.found_disguises.append(users[user_id].npcs['James Potts'].disguise)
    users[user_id].npcs['James Potts'].alive = False
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Цель устранена: Ewan Roberts\n\nДиана: Вижу ты уже привык к этому\, переодевайся и отправляйся на верхнюю палубу\.', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Передвижение", callback_data="pass"), InlineKeyboardButton("Взаимодействие", callback_data="pass")],
            [InlineKeyboardButton("Инвентарь", callback_data="tutorial_24"), InlineKeyboardButton("Обыскать локацию", callback_data="pass")],
            [InlineKeyboardButton("Статус", callback_data="pass"), InlineKeyboardButton("Испытания", callback_data="pass")],
            [InlineKeyboardButton("Сохранить и выйти", callback_data="pass")]
        ]), parse_mode='MarkdownV2')

def tutorial_24(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    result_string = make_heading('Инвентарь')
    result_string += f'Сейчас в руках: {users[user_id].player.item.name}'
    query.edit_message_text(text=result_string, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("ICA 19 (1)", callback_data="pass")],
            [InlineKeyboardButton("Удавка (1)", callback_data="pass")],
            [InlineKeyboardButton("Монета (3)", callback_data="pass")],
            [InlineKeyboardButton("Сменить маскировку", callback_data="tutorial_25")],
            [InlineKeyboardButton("Выйти", callback_data="pass")]
        ]))
    
def tutorial_25(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Текущая маскировка: Тактическая водолазка', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Тактическая водолазка", callback_data="pass")],
            [InlineKeyboardButton("Механик", callback_data="pass")],
            [InlineKeyboardButton("Экипаж яхты", callback_data="tutorial_26")]
        ]), parse_mode='MarkdownV2')

def tutorial_26(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    users[user_id].player.disguise = users[user_id].disguises['Экипаж яхты']
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Текущая маскировка: Экипаж яхты', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Передвижение", callback_data="tutorial_27"), InlineKeyboardButton("Взаимодействие", callback_data="pass")],
            [InlineKeyboardButton("Инвентарь", callback_data="pass"), InlineKeyboardButton("Обыскать локацию", callback_data="pass")],
            [InlineKeyboardButton("Статус", callback_data="pass"), InlineKeyboardButton("Испытания", callback_data="pass")],
            [InlineKeyboardButton("Сохранить и выйти", callback_data="pass")]
        ]))

def tutorial_27(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите локацию', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Главная палуба", callback_data="tutorial_28")],
            [InlineKeyboardButton("Отменить действие", callback_data="pass")]
        ]), parse_mode='MarkdownV2')
    
def tutorial_28(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    users[user_id].player.current_location = users[user_id].locations['Главная палуба']
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=location_status(users[user_id].player.current_location), reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Передвижение", callback_data="tutorial_29"), InlineKeyboardButton("Взаимодействие", callback_data="pass")],
            [InlineKeyboardButton("Инвентарь", callback_data="pass"), InlineKeyboardButton("Обыскать локацию", callback_data="pass")],
            [InlineKeyboardButton("Статус", callback_data="pass"), InlineKeyboardButton("Испытания", callback_data="pass")],
            [InlineKeyboardButton("Сохранить и выйти", callback_data="pass")]
        ]), parse_mode='MarkdownV2')

def tutorial_29(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите локацию', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Пирс", callback_data="pass"), InlineKeyboardButton("Грузовой отсек", callback_data="pass")],
            [InlineKeyboardButton("Нижняя палуба", callback_data="pass"), InlineKeyboardButton("Кухня", callback_data="pass")],
            [InlineKeyboardButton("Бар", callback_data="pass"), InlineKeyboardButton("Верхняя палуба", callback_data="tutorial_30")],
            [InlineKeyboardButton("Отменить действие", callback_data="pass")]
        ]), parse_mode='MarkdownV2')
    
def tutorial_30(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    users[user_id].player.current_location = users[user_id].locations['Верхняя палуба']
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Для того, чтобы попасть в запретную зону, не меняя маскировку, можно использовать монеты, если конечно они есть у вас в инвентаре.')
    context.bot.send_message(chat_id=update.effective_chat.id, text=location_status(users[user_id].player.current_location) + '\n\nДиана: А ты хорош\, но как ты попадешь в офис Риттера\?', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Передвижение", callback_data="pass"), InlineKeyboardButton("Взаимодействие", callback_data="pass")],
            [InlineKeyboardButton("Инвентарь", callback_data="tutorial_31"), InlineKeyboardButton("Обыскать локацию", callback_data="pass")],
            [InlineKeyboardButton("Статус", callback_data="pass"), InlineKeyboardButton("Испытания", callback_data="pass")],
            [InlineKeyboardButton("Сохранить и выйти", callback_data="pass")]
        ]), parse_mode='MarkdownV2')

def tutorial_31(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    result_string = make_heading('Инвентарь')
    result_string += f'Сейчас в руках: {users[user_id].player.item.name}'
    query.edit_message_text(text=result_string, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("ICA 19 (1)", callback_data="pass")],
            [InlineKeyboardButton("Удавка (1)", callback_data="pass")],
            [InlineKeyboardButton("Монета (3)", callback_data="tutorial_32")],
            [InlineKeyboardButton("Сменить маскировку", callback_data="pass")],
            [InlineKeyboardButton("Выйти", callback_data="pass")]
        ]))
    
def tutorial_32(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Сейчас в руках: Монета', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Передвижение", callback_data="pass"), InlineKeyboardButton("Взаимодействие", callback_data="tutorial_33")],
            [InlineKeyboardButton("Инвентарь", callback_data="pass"), InlineKeyboardButton("Обыскать локацию", callback_data="pass")],
            [InlineKeyboardButton("Статус", callback_data="pass"), InlineKeyboardButton("Испытания", callback_data="pass")],
            [InlineKeyboardButton("Сохранить и выйти", callback_data="pass")]
        ]), parse_mode='MarkdownV2')

def tutorial_33(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите действие', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Бросить для отвлечения", callback_data="tutorial_34")],
            [InlineKeyboardButton("Назад", callback_data="pass")]
        ]), parse_mode='MarkdownV2')
    
def tutorial_34(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='На локации слишком много людей', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Отвлечь для перемещения", callback_data="tutorial_35")],
            [InlineKeyboardButton("Отменить действие", callback_data="pass")]
        ]), parse_mode='MarkdownV2')
    
def tutorial_35(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите локацию', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Главная палуба", callback_data="pass")],
            [InlineKeyboardButton("Офис Риттера", callback_data="tutorial_36")],
            [InlineKeyboardButton("Капитанский мостик", callback_data="pass")],
            [InlineKeyboardButton("Отменить действие", callback_data="pass")]
        ]), parse_mode='MarkdownV2')

def tutorial_36(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    users[user_id].player.current_location = users[user_id].locations['Верхняя палуба']
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=make_heading('Офис Риттера') + '\nНа локации находятся:\n\nKalvin Ritter\n\nДиана: Поразительно... Он в твоём полном расположении\, может задущищь его удавкой\?', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Передвижение", callback_data="pass"), InlineKeyboardButton("Взаимодействие", callback_data="pass")],
            [InlineKeyboardButton("Инвентарь", callback_data="tutorial_37"), InlineKeyboardButton("Обыскать локацию", callback_data="pass")],
            [InlineKeyboardButton("Статус", callback_data="pass"), InlineKeyboardButton("Испытания", callback_data="pass")],
            [InlineKeyboardButton("Сохранить и выйти", callback_data="pass")]
        ]), parse_mode='MarkdownV2')

def tutorial_37(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    result_string = make_heading('Инвентарь')
    result_string += f'Сейчас в руках: {users[user_id].player.item.name}'
    query.edit_message_text(text=result_string, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("ICA 19 (1)", callback_data="pass")],
            [InlineKeyboardButton("Удавка (1)", callback_data="tutorial_38")],
            [InlineKeyboardButton("Монета (3)", callback_data="pass")],
            [InlineKeyboardButton("Сменить маскировку", callback_data="pass")],
            [InlineKeyboardButton("Выйти", callback_data="pass")]
        ]))
    
def tutorial_38(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Сейчас в руках: Удавка', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Передвижение", callback_data="pass"), InlineKeyboardButton("Взаимодействие", callback_data="tutorial_39")],
            [InlineKeyboardButton("Инвентарь", callback_data="pass"), InlineKeyboardButton("Обыскать локацию", callback_data="pass")],
            [InlineKeyboardButton("Статус", callback_data="pass"), InlineKeyboardButton("Испытания", callback_data="pass")],
            [InlineKeyboardButton("Сохранить и выйти", callback_data="pass")]
        ]), parse_mode='MarkdownV2')
    
def tutorial_39(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите цель', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Kalvin Ritter", callback_data="tutorial_40")],
            [InlineKeyboardButton("Отменить действие", callback_data="pass")]
        ]), parse_mode='MarkdownV2')
    
def tutorial_40(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Действия видят 0 человек\n\nKalvin Ritter', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Убить", callback_data="tutorial_41")],
            [InlineKeyboardButton("Назад", callback_data="pass")]
        ]), parse_mode='MarkdownV2')
    
def tutorial_41(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    users[user_id].targets['Kalvin Ritter'].alive = False
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Диана: Kalvin Ritter больше нас не побеспокоит. Отличная работа 47-й.')
    context.bot.send_message(chat_id=update.effective_chat.id, text='Цель устранена: Kalvin Ritter\n\nДиана: Что ж\, ты устранил цель\, осталось покинуть зону задания\. Спустись на пирс через главную палубу\.', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Передвижение", callback_data="tutorial_42"), InlineKeyboardButton("Взаимодействие", callback_data="pass")],
            [InlineKeyboardButton("Инвентарь", callback_data="pass"), InlineKeyboardButton("Обыскать локацию", callback_data="pass")],
            [InlineKeyboardButton("Статус", callback_data="pass"), InlineKeyboardButton("Испытания", callback_data="pass")],
            [InlineKeyboardButton("Сохранить и выйти", callback_data="pass")]
        ]), parse_mode='MarkdownV2')

def tutorial_42(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите локацию', reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Верхняя палуба", callback_data="tutorial_43")],
            [InlineKeyboardButton("Отменить действие", callback_data="pass")]
        ]), parse_mode='MarkdownV2')
    
def tutorial_43(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    users[user_id].player.current_location = users[user_id].locations['Верхняя палуба']
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=location_status(users[user_id].player.current_location), reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Передвижение", callback_data="pass"), InlineKeyboardButton("Взаимодействие", callback_data="pass")],
            [InlineKeyboardButton("Инвентарь", callback_data="tutorial_31"), InlineKeyboardButton("Обыскать локацию", callback_data="pass")],
            [InlineKeyboardButton("Статус", callback_data="pass"), InlineKeyboardButton("Испытания", callback_data="pass")],
            [InlineKeyboardButton("Сохранить и выйти", callback_data="pass")]
        ]), parse_mode='MarkdownV2')



#----------Сюжетные скрипты----------

def stem_cells(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    users[user_id].events['Отравить стволовые клетки'].completed = True
    users[user_id].player.inventory.remove(users[user_id].items['Стволовые клетки'])
    query = update.callback_query
    query.answer()
    if users[user_id].targets['Erich Soders'].alive:
        if users[user_id].challenges['Поцелуй смерти'].completed == False:
            query.edit_message_text(text=users[user_id].challenges['Поцелуй смерти'].achieved(update=update, context=context), parse_mode='MarkdownV2')
            users[user_id].player_lvl += users[user_id].challenges['Поцелуй смерти'].xp
            if users[user_id].challenges['Так можно и пораниться'].completed == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Так можно и пораниться'].achieved(update=update, context=context), parse_mode='MarkdownV2')
                users[user_id].player_lvl += users[user_id].challenges['Так можно и пораниться'].xp
            context.bot.send_animation(chat_id=update.effective_chat.id, animation=open('hitman_tg_bot/assets/stem_cells_kill.mp4', 'rb'))
            context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].targets['Erich Soders'].kill(), reply_markup=(choose_action_keyboard(update=update, context=context)))
        else:
            query.edit_message_text(text=users[user_id].targets['Erich Soders'].kill(), reply_markup=(choose_action_keyboard(update=update, context=context)))
    else:
        query.edit_message_text(text='Выберите действие:', reply_markup=(choose_action_keyboard(update=update, context=context)))


def medical_checkup(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    users[user_id].player.current_location = users[user_id].locations['Приёмная']
    edit = True
    if users[user_id].player.current_location.unlocked == False:
        query.edit_message_text(text=users[user_id].player.current_location.unlock(update=update, context=context), parse_mode='MarkdownV2')
        edit = False
    if users[user_id].challenges['Смена внешности'].completed == False:
        users[user_id].player_lvl += users[user_id].challenges['Смена внешности'].xp
        if edit:
            query.edit_message_text(text=users[user_id].challenges['Смена внешности'].achieved(update=update, context=context), parse_mode='MarkdownV2')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Смена внешности'].achieved(update=update, context=context), parse_mode='MarkdownV2')
        edit = False
    if edit:
        query.edit_message_text(text=location_status(update=update, context=context, location=users[user_id].player.current_location) + tg_text_convert('\n\nХирург: Я рад, что вы пришли, сначала я подготовлю инструменты, а потом мы приступим.'), reply_markup=(choose_action_keyboard(update=update, context=context)), parse_mode='MarkdownV2')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=location_status(update=update, context=context, location=users[user_id].player.current_location) + tg_text_convert('\n\nХирург: Я рад, что вы пришли, сначала я подготовлю инструменты, а потом мы приступим.'), reply_markup=(choose_action_keyboard(update=update, context=context)), parse_mode='MarkdownV2')


def knock_jason_portman_2(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    users[user_id].npcs['Jason Portman'].alive = False
    users[user_id].player.found_disguises.append(users[user_id].npcs['Jason Portman'].disguise)
    if query.data == 'УДПсм':
        users[user_id].kills += 1
    query.edit_message_text(text='Вы устранили Джейсона Портмана.', reply_markup=(choose_action_keyboard(update=update, context=context)))

def knock_jason_portman_1(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    users[user_id].player.current_location = users[user_id].locations['Уборная']
    edit = True
    if users[user_id].player.current_location.unlocked == False:
        query.edit_message_text(text=users[user_id].player.current_location.unlock(update=update, context=context), parse_mode='MarkdownV2')
        edit = False
    if edit:
        query.edit_message_text(text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=(knock_jason_portman_keyboard_2()), parse_mode='MarkdownV2')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=(knock_jason_portman_keyboard_2()), parse_mode='MarkdownV2')


def cigar_kill_6(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    if users[user_id].challenges['Курение убивает'].completed == False:
        query.edit_message_text(text=users[user_id].challenges['Курение убивает'].achieved(update=update, context=context), parse_mode='MarkdownV2')
        users[user_id].player_lvl += users[user_id].challenges['Курение убивает'].xp
        if users[user_id].challenges['Так можно и пораниться'].completed == False:
            context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Так можно и пораниться'].achieved(update=update, context=context), parse_mode='MarkdownV2')
            users[user_id].player_lvl += users[user_id].challenges['Так можно и пораниться'].xp
        context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].targets['Yuki Yamazaki'].kill(), reply_markup=(choose_action_keyboard(update=update, context=context)))
    else:
        query.edit_message_text(text=users[user_id].targets['Yuki Yamazaki'].kill(), reply_markup=(choose_action_keyboard(update=update, context=context)))

def cigar_kill_5(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    if users[user_id].targets['Yuki Yamazaki'].alive:
        query.edit_message_text(text='Юки Ямадзаки: Пачка сиграрет? Как я могла ее не заметить!\n\nЮки Ямадзаки вышла на балкон и начала курить.', reply_markup=(cigar_kill_keyboard_5()))
    else:
        query.edit_message_text(text='Выберите действие', reply_markup=(choose_action_keyboard(update=update, context=context)))

def cigar_kill_4(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    text = 'Юки Ямадзаки: Пачка сиграрет? Как я могла ее не заметить!\n\nЮки Ямадзаки вышла на балкон и воспользовалась зажигалкой, что привело к взрыву.\n\nДиана: Это было умно, 47-й. Юки Ямадзаки больше нас не побеспокоит.'
    if users[user_id].targets['Yuki Yamazaki'].alive:
        users[user_id].targets['Yuki Yamazaki'].alive = False
        if users[user_id].challenges['В клубах дыма'].completed == False:
            query.edit_message_text(text=users[user_id].challenges['В клубах дыма'].achieved(update=update, context=context), parse_mode='MarkdownV2')
            users[user_id].player_lvl += users[user_id].challenges['В клубах дыма'].xp
            if users[user_id].challenges['Так можно и пораниться'].completed == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Так можно и пораниться'].achieved(update=update, context=context), parse_mode='MarkdownV2')
                users[user_id].player_lvl += users[user_id].challenges['Так можно и пораниться'].xp
            context.bot.send_animation(chat_id=update.effective_chat.id, animation=open('hitman_tg_bot/assets/smoking_kill.mp4', 'rb'))
            context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=(choose_action_keyboard(update=update, context=context)))
        else:
            query.edit_message_text(text=text, reply_markup=(choose_action_keyboard(update=update, context=context)))
    else:
        query.edit_message_text(text='Выберите действие', reply_markup=(choose_action_keyboard(update=update, context=context)))

def cigar_kill_3(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    if users[user_id].items['Гаечный ключ'] in users[user_id].player.inventory:
        query.edit_message_text(text='Вы находитесь в радиусе взрыва.', reply_markup=(cigar_kill_keyboard_4()))
    else:
        query.edit_message_text(text='У вас нет гаечного ключа.', reply_markup=(cigar_kill_keyboard_3()))

def cigar_kill_2(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите действие', reply_markup=(cigar_kill_keyboard_3()))

def cigar_kill_1(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    users[user_id].events['Сигареты на столе'].completed = True
    users[user_id].player.inventory.remove(users[user_id].items['Пачка сигарет'])
    if users[user_id].challenges['Не курить!'].completed == False:
        query.edit_message_text(text=users[user_id].challenges['Не курить!'].achieved(update=update, context=context), parse_mode='MarkdownV2')
        users[user_id].player_lvl += users[user_id].challenges['Не курить!'].xp
        context.bot.send_message(chat_id=update.effective_chat.id, text='На балконе находится газовый обогреватель.', reply_markup=cigar_kill_keyboard_2())
    else:
        query.edit_message_text(text='На балконе находится газовый обогреватель.', reply_markup=cigar_kill_keyboard_2())


def sushi_kill_4(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    if users[user_id].challenges['Подержи волосы'].completed == False:
        query.edit_message_text(text=users[user_id].challenges['Подержи волосы'].achieved(update=update, context=context), parse_mode='MarkdownV2')
        users[user_id].player_lvl += users[user_id].challenges['Подержи волосы'].xp
        if users[user_id].challenges['Без вкуса, без следа'].completed == False:
            context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Без вкуса, без следа'].achieved(update=update, context=context), parse_mode='MarkdownV2')
            users[user_id].player_lvl += users[user_id].challenges['Без вкуса, без следа'].xp
        context.bot.send_animation(chat_id=update.effective_chat.id, animation=open('hitman_tg_bot/assets/sushi_kill.mp4', 'rb'))
        context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].targets['Yuki Yamazaki'].kill(), reply_markup=choose_action_keyboard(update=update, context=context))
    else:
        query.edit_message_text(text=users[user_id].targets['Yuki Yamazaki'].kill(), reply_markup=choose_action_keyboard(update=update, context=context))

def sushi_kill_3(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите действие', reply_markup=(sushi_kill_keyboard_4()))

def sushi_kill_2(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    users[user_id].events['Убийство ядом'].completed = True
    poison = users[user_id].items[query.data.replace('ОСЮ', '')]
    users[user_id].player.inventory.remove(poison)
    if poison.lethal:
        if poison.name == 'Яд рыбы Фугу':
            if users[user_id].challenges['Приятного аппетита'].completed == False:
                query.edit_message_text(text=users[user_id].challenges['Приятного аппетита'].achieved(update=update, context=context), parse_mode='MarkdownV2')
                users[user_id].player_lvl += users[user_id].challenges['Приятного аппетита'].xp
                if users[user_id].challenges['Без вкуса, без следа'].completed == False:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Без вкуса, без следа'].achieved(update=update, context=context), parse_mode='MarkdownV2')
                    users[user_id].player_lvl += users[user_id].challenges['Без вкуса, без следа'].xp
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].targets['Yuki Yamazaki'].kill(), reply_markup=choose_action_keyboard(update=update, context=context))
            else:
                query.edit_message_text(text=users[user_id].targets['Yuki Yamazaki'].kill(), reply_markup=choose_action_keyboard(update=update, context=context))
        elif users[user_id].challenges['Без вкуса, без следа'].completed == False:
            query.edit_message_text(text=users[user_id].challenges['Без вкуса, без следа'].achieved(update=update, context=context), parse_mode='MarkdownV2')
            users[user_id].player_lvl += users[user_id].challenges['Без вкуса, без следа'].xp
            context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].targets['Yuki Yamazaki'].kill(), reply_markup=choose_action_keyboard(update=update, context=context))
        else:
            query.edit_message_text(text=users[user_id].targets['Yuki Yamazaki'].kill(), reply_markup=choose_action_keyboard(update=update, context=context))
    else:
        query.edit_message_text(text='Юки Ямадзаки стало плохо и она направилась в ванную.', reply_markup=sushi_kill_keyboard_3())

def sushi_kill_1(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    if users[user_id].player.disguise.name == 'Шеф' or random.randrange(11) <= 3:
        query.edit_message_text(text='Выберите яд', reply_markup=(sushi_kill_keyboard_2(update=update, context=context)))
    else:
        if find_location_npcs(update=update, context=context, location=users[user_id].player.current_location) != []:
            location_npc = find_location_npcs(update=update, context=context, location=users[user_id].player.current_location)[random.randrange(len(find_location_npcs(update=update, context=context, location=users[user_id].player.current_location)))]
            users[user_id].suspicion_count += 1
            query.edit_message_text(text=f'{location_npc.name} ({location_npc.disguise.name}): Эй, ты что делаешь?', reply_markup=hide_keyboard(location_npc, users[user_id].player.current_location))
        else:
            query.edit_message_text(text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=choose_action_keyboard(update=update, context=context), parse_mode='MarkdownV2')


def drink_kill_3(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    if users[user_id].challenges['Ирония'].completed == False:
        query.edit_message_text(text=users[user_id].challenges['Ирония'].achieved(update=update, context=context), parse_mode='MarkdownV2')
        users[user_id].player_lvl += users[user_id].challenges['Ирония'].xp
        context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].targets['Kalvin Ritter'].kill(), reply_markup=choose_action_keyboard(update=update, context=context))
    else:
        query.edit_message_text(text=users[user_id].targets['Yuki Yamazaki'].kill(), reply_markup=choose_action_keyboard(update=update, context=context))

def drink_kill_2(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Выберите действие', reply_markup=(drink_kill_keyboard_3()))

def drink_kill_1(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    if users[user_id].player.disguise.name == 'Экипаж яхты' or random.randrange(11) <= 3:
        users[user_id].events['Отравить напиток'].completed = True
        if users[user_id].challenges['Не употреблять в пищу'].completed == False:
            query.edit_message_text(text=users[user_id].challenges['Не употреблять в пищу'].achieved(update=update, context=context), parse_mode='MarkdownV2')
            users[user_id].player_lvl += users[user_id].challenges['Не употреблять в пищу'].xp
            context.bot.send_message(chat_id=update.effective_chat.id, text='Цели стало плохо и она направилась в ванную.', reply_markup=(drink_kill_keyboard_2()))
        else:
            query.edit_message_text(text='Цели стало плохо и она направилась в ванную.', reply_markup=(drink_kill_keyboard_2()))
    else:
        if find_location_npcs(update=update, context=context, location=users[user_id].player.current_location) != []:
            location_npc = find_location_npcs(update=update, context=context, location=users[user_id].player.current_location)[random.randrange(len(find_location_npcs(update=update, context=context, location=users[user_id].player.current_location)))]
            users[user_id].suspicion_count += 1
            query.edit_message_text(text=f'{location_npc.name} ({location_npc.disguise.name}): Эй, ты что делаешь?', reply_markup=hide_keyboard(location_npc, users[user_id].player.current_location))
        else:
            query.edit_message_text(text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=choose_action_keyboard(update=update, context=context), parse_mode='MarkdownV2')


def yoga_kill_2(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    if users[user_id].challenges['Хорошая растяжка'].completed == False:
        query.edit_message_text(text=users[user_id].challenges['Хорошая растяжка'].achieved(update=update, context=context), parse_mode='MarkdownV2')
        users[user_id].player_lvl += users[user_id].challenges['Хорошая растяжка'].xp
        if users[user_id].challenges['Так можно и пораниться'].completed == False:
            context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Так можно и пораниться'].achieved(update=update, context=context), parse_mode='MarkdownV2')
            users[user_id].player_lvl += users[user_id].challenges['Так можно и пораниться'].xp
        context.bot.send_animation(chat_id=update.effective_chat.id, animation=open('hitman_tg_bot/assets/yoga_kill.mov.mp4', 'rb'))
        context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].targets['Yuki Yamazaki'].kill(), reply_markup=(choose_action_keyboard(update=update, context=context)))
    else:
        query.edit_message_text(text=users[user_id].targets['Yuki Yamazaki'].kill(), reply_markup=(choose_action_keyboard(update=update, context=context)))

def yoga_kill_1(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Агент 47: Приступим, эта тренировка смертельно вам понравится.\n\nЮки Ямадзаки отозвала всю охрану и вывела всех людей из зоны отдыха', reply_markup=(yoga_kill_keyboard_2()))


def surgeon_knock_out_2(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    users[user_id].npcs['Nicholas Laurent'].alive = False
    users[user_id].player.found_disguises.append(users[user_id].npcs['Nicholas Laurent'].disguise)
    if query.data == 'УГХсм':
        users[user_id].kills += 1
    query.edit_message_text(text='Вы устранили главного хирурга.', reply_markup=(choose_action_keyboard(update=update, context=context)))

def surgeon_knock_out_1(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    users[user_id].player.current_location = users[user_id].locations['Комната пилота']
    edit = True
    query = update.callback_query
    query.answer()
    if users[user_id].player.current_location.unlocked == False:
        query.edit_message_text(text=users[user_id].player.current_location.unlock(update=update, context=context), parse_mode='MarkdownV2')
        edit = False
    if users[user_id].challenges['Личная встреча'].completed == False:
        users[user_id].player_lvl += users[user_id].challenges['Личная встреча'].xp
        if edit:
            query.edit_message_text(text=users[user_id].challenges['Личная встреча'].achieved(update=update, context=context), parse_mode='MarkdownV2')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Личная встреча'].achieved(update=update, context=context), parse_mode='MarkdownV2')
        context.bot.send_message(chat_id=update.effective_chat.id, text='Главный хирург отвернулся от вас и начал принимать таблетки.', reply_markup=(surgeon_knock_out_keyboard_2()))
    else:
        if edit:
            query.edit_message_text(text='Главный хирург отвернулся от вас и начал принимать таблетки.', reply_markup=(surgeon_knock_out_keyboard_2()))
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Главный хирург отвернулся от вас и начал принимать таблетки.', reply_markup=(surgeon_knock_out_keyboard_2()))


def private_meeting_2(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    edit = True
    if query.data == 'ЗЦУ':
        if users[user_id].challenges['Классический убийца'].completed == False:
            users[user_id].player_lvl += users[user_id].challenges['Классический убийца'].xp
            query.edit_message_text(text=users[user_id].challenges['Классический убийца'].achieved(update=update, context=context), parse_mode='MarkdownV2')
    if edit:
        query.edit_message_text(text=users[user_id].targets['Kalvin Ritter'].kill(), reply_markup=(choose_action_keyboard(update=update, context=context)))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].targets['Kalvin Ritter'].kill(), reply_markup=(choose_action_keyboard(update=update, context=context)))

def private_meeting_1(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    users[user_id].player.current_location = users[user_id].locations['Офис Риттера']
    edit = True
    query = update.callback_query
    query.answer()
    if users[user_id].player.current_location.unlocked == False:
        query.edit_message_text(text=users[user_id].player.current_location.unlock(update=update, context=context), parse_mode='MarkdownV2')
        edit = False
    if users[user_id].challenges['Частная встреча'].completed == False:
        users[user_id].player_lvl += users[user_id].challenges['Частная встреча'].xp
        if edit:
            query.edit_message_text(text=users[user_id].challenges['Частная встреча'].achieved(update=update, context=context), parse_mode='MarkdownV2')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Частная встреча'].achieved(update=update, context=context), parse_mode='MarkdownV2')
        context.bot.send_message(chat_id=update.effective_chat.id, text='Кэлвин Риттер: Ты пока можешь осмотреться, мне нужно кое-что сделать на компьютере.', reply_markup=(private_meeting_keyboard_2()))
    else:
        if edit:
            query.edit_message_text(text='Кэлвин Риттер: Ты пока можешь осмотреться, мне нужно кое-что сделать на компьютере.', reply_markup=(surgeon_knock_out_keyboard_2()))
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Кэлвин Риттер: Ты пока можешь осмотреться, мне нужно кое-что сделать на компьютере.', reply_markup=(surgeon_knock_out_keyboard_2()))


def sauna_kill_2(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    if users[user_id].challenges['Убийство в парилке'].completed == False:
        query.edit_message_text(text=users[user_id].challenges['Убийство в парилке'].achieved(update=update, context=context), parse_mode='MarkdownV2')
        users[user_id].player_lvl += users[user_id].challenges['Убийство в парилке'].xp
        if users[user_id].challenges['Так можно и пораниться'].completed == False:
            context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Так можно и пораниться'].achieved(update=update, context=context), parse_mode='MarkdownV2')
            users[user_id].player_lvl += users[user_id].challenges['Так можно и пораниться'].xp
        context.bot.send_animation(chat_id=update.effective_chat.id, animation=open('hitman_tg_bot/assets/sauna_kill.mp4', 'rb'))
        context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].targets['Yuki Yamazaki'].kill(), reply_markup=(choose_action_keyboard(update=update, context=context)))
    else:
        query.edit_message_text(text=users[user_id].targets['Yuki Yamazaki'].kill(), reply_markup=(choose_action_keyboard(update=update, context=context)))

def sauna_kill_1(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    users[user_id].events['Убийство в сауне'].completed = True
    query = update.callback_query
    query.answer()
    if users[user_id].targets['Yuki Yamazaki'].alive:
        query.edit_message_text(text=f'Все люди вышли из бани из-за высокой температуры.\n\nЮки Ямадзаки: Наконец-то парилка свободна!\nЮки Ямадзаки вошла в баню', reply_markup=(sauna_kill_keyboard_2()))
    else:
        query.edit_message_text(text=f'Все люди вышли из бани из-за высокой температуры.', reply_markup=(choose_action_keyboard(update=update, context=context)))


def lifeboat_kill_1(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    if users[user_id].items['Лом'] in users[user_id].player.inventory:
        users[user_id].events['Сбросить шлюпку'].completed = True
        if users[user_id].targets['Kalvin Ritter'].alive:
            if users[user_id].challenges['Использовать только при ЧП'].completed == False:
                query.edit_message_text(text=users[user_id].challenges['Использовать только при ЧП'].achieved(update=update, context=context), parse_mode='MarkdownV2')
                users[user_id].player_lvl += users[user_id].challenges['Использовать только при ЧП'].xp
                context.bot.send_animation(chat_id=update.effective_chat.id, animation=open('hitman_tg_bot/assets/lifeboat_kill.mp4', 'rb'))
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].targets['Kalvin Ritter'].kill(), reply_markup=(choose_action_keyboard(update=update, context=context)))
            else:
                query.edit_message_text(text=users[user_id].targets['Kalvin Ritter'].kill(), reply_markup=(choose_action_keyboard(update=update, context=context)))
        else:
            query.edit_message_text(text='Выберите действие', reply_markup=(choose_action_keyboard(update=update, context=context)))
    else:
        query.edit_message_text(text='У вас нет лома', reply_markup=(skip_choose_action_keyboard(update=update, context=context, skip_lifeboat=True)))


def robot_kill_2(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    if users[user_id].challenges['(Не) врачебная ошибка'].completed == False:
        query.edit_message_text(text=users[user_id].challenges['(Не) врачебная ошибка'].achieved(update=update, context=context), parse_mode='MarkdownV2')
        users[user_id].player_lvl += users[user_id].challenges['(Не) врачебная ошибка'].xp
        if users[user_id].challenges['Так можно и пораниться'].completed == False:
            context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Так можно и пораниться'].achieved(update=update, context=context), parse_mode='MarkdownV2')
            users[user_id].player_lvl += users[user_id].challenges['Так можно и пораниться'].xp
        context.bot.send_animation(chat_id=update.effective_chat.id, animation=open('hitman_tg_bot/assets/operation_kill.mp4', 'rb'))
        context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].targets['Erich Soders'].kill(), reply_markup=(choose_action_keyboard(update=update, context=context)))
    else:
        query.edit_message_text(text=users[user_id].targets['Erich Soders'].kill(), reply_markup=(choose_action_keyboard(update=update, context=context)))

def robot_kill_1(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    users[user_id].events['Убийство в операционной'].completed = True
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f'Диана: Эрих Содерс находится в твоем полном расположении. Умно, 47-й.', reply_markup=(robot_kill_keyboard_2()))


def destroy_heart(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    users[user_id].targets['Erich Soders'].alive = False
    query = update.callback_query
    query.answer()
    if users[user_id].challenges['Бессердечный'].completed == False:
        query.edit_message_text(text=users[user_id].challenges['Бессердечный'].achieved(update=update, context=context), parse_mode='MarkdownV2')
        users[user_id].player_lvl += users[user_id].challenges['Бессердечный'].xp
        context.bot.send_animation(chat_id=update.effective_chat.id, animation=open('hitman_tg_bot/assets/heart_kill.mp4', 'rb'))
        context.bot.send_message(chat_id=update.effective_chat.id, text='Диана: 47-й, без сердца для пересадки Содерс не выживет. Ты смог от него избавиться даже не прикасаясь, изящный ход.', reply_markup=(choose_action_keyboard(update=update, context=context)))
    else:
        query.edit_message_text(text='Диана: 47-й, без сердца для пересадки Содерс не выживет. Ты смог от него избавиться даже не прикасаясь, изящный ход.', reply_markup=(choose_action_keyboard(update=update, context=context)))


def destroy_servers(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user['id']
    users[user_id].targets['Erich Soders'].alive = False
    query = update.callback_query
    query.answer()
    if users[user_id].challenges['Призрак в машине'].completed == False:
        query.edit_message_text(text=users[user_id].challenges['Призрак в машине'].achieved(update=update, context=context), parse_mode='MarkdownV2')
        users[user_id].player_lvl += users[user_id].challenges['Призрак в машине'].xp
        if users[user_id].challenges['Так можно и пораниться'].completed == False:
            context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Так можно и пораниться'].achieved(update=update, context=context), parse_mode='MarkdownV2')
            users[user_id].player_lvl += users[user_id].challenges['Так можно и пораниться'].xp
        context.bot.send_animation(chat_id=update.effective_chat.id, animation=open('hitman_tg_bot/assets/kai_kill.mp4', 'rb'))
        context.bot.send_message(chat_id=update.effective_chat.id, text='Хирург: Что происходит с роботом?! Как его отключить?! Пациент сейчас умрет!\n\nДиана: Это было впечатляюще, агент. Эрих Содерс мертв.', reply_markup=(choose_action_keyboard(update=update, context=context)))
    else:
        query.edit_message_text(text='Хирург: Что происходит с роботом?! Как его отключить?! Пациент сейчас умрет!\n\nДиана: Это было впечатляюще, агент. Эрих Содерс мертв.', reply_markup=(choose_action_keyboard(update=update, context=context)))



#----------Механики игры----------

def reject_turorial(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Вы можете вернуться к обучению позже.')

def save_and_quit(update: Update, context: CallbackContext):
    """Сохранение и выход из игры"""
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    completed_challenges = []
    for i in list(users[user_id].challenges.values()):
        if i.completed:
            completed_challenges.append(i.name)
    unlocked_disguises = []
    for i in list(users[user_id].disguises.values()):
        if i.unlocked:
            unlocked_disguises.append(i.name)
    unlocked_locations = []
    for i in list(users[user_id].locations.values()):
        if i.unlocked:
            unlocked_locations.append(i.name)
    completed_challenges_str = ';'.join(completed_challenges)
    unlocked_disguises_str = ';'.join(unlocked_disguises)
    unlocked_locations_str = ';'.join(unlocked_locations)
    adapter.update_by_id("users", f'{users[user_id].mission}_completed_challenges={completed_challenges_str}', user_id)
    adapter.update_by_id("users", f'{users[user_id].mission}_unlocked_disguises={unlocked_disguises_str}', user_id)
    adapter.update_by_id("users", f'{users[user_id].mission}_unlocked_locations={unlocked_locations_str}', user_id)
    adapter.update_by_id("users", f'player_lvl={users[user_id].player_lvl}', user_id)
    users[user_id] = create_user(user_id=user_id)
    query.edit_message_text(text='Данные сохранены.')


def use(update: Update, context: CallbackContext):
    """Использовать предмет"""
    user_id = update.callback_query.from_user['id']
    users[user_id].time += 5
    query = update.callback_query
    query.answer()
    if users[user_id].player.item.name == 'Пульт от нейрочипа' and users[user_id].events['Уничтожить сердце'].completed == False and users[user_id].player.current_location.name == 'Морг':
        users[user_id].events['Уничтожить сердце'].completed = True
        users[user_id].player.inventory.remove(users[user_id].player.item)
        users[user_id].player.item = users[user_id].items['Нет предмета']
        query.edit_message_text(text='Нейрочип подействовал на одного из работников морга и тот отправился в комнату, где хранится сердце, которое должны пересадить Эриху Содерсу.\n\nПоследовать за ним?', reply_markup=(destroy_heart_keyboard_1()))
    if users[user_id].player.item.name == 'Пульт от нейрочипа' and (users[user_id].events['Уничтожить сердце'].completed == True or users[user_id].player.current_location.name != 'Морг'):
        query.edit_message_text(text='Вне зоны действия', reply_markup=(choose_action_keyboard(update=update, context=context)))

def choose_illegal_item(update: Update, context: CallbackContext):
    """Выбор нелегального предмета"""
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    users[user_id].player.item = users[user_id].items[users[user_id].illegal_item]
    query.answer()
    query.edit_message_text(text=f'Сейчас в руках: {users[user_id].player.item.name}', reply_markup=(choose_action_keyboard(update=update, context=context)))

def choose_legal_item(update: Update, context: CallbackContext):
    """Выбор легального предмета"""
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    users[user_id].player.item = users[user_id].items[query.data[:-4]]
    query.answer()
    query.edit_message_text(text=f'Сейчас в руках: {users[user_id].player.item.name}', reply_markup=(choose_action_keyboard(update=update, context=context)))

def remove_item(update: Update, context: CallbackContext):
    """Убрать предмет из рук"""
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    users[user_id].player.item = users[user_id].items['Нет предмета']
    query.answer()
    query.edit_message_text(text=f'Сейчас в руках: {users[user_id].player.item.name}', reply_markup=(inventory_keyboard(update=update, context=context)))

def change_disguise(update: Update, context: CallbackContext):
    """Смена маскировки"""
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    disguise_choice = query.data.replace('МСК', '')
    users[user_id].player.disguise = users[user_id].disguises[disguise_choice]
    if users[user_id].player.disguise.name != 'VIP - пациент':
        users[user_id].suit_only = False
    if users[user_id].player.disguise.unlocked == False:
        query.edit_message_text(text=users[user_id].player.disguise.unlock(update=update, context=context), parse_mode='MarkdownV2')
        if users[user_id].mission == 'hokkaido':
            if users[user_id].player.disguise.name == 'Директор клиники' and users[user_id].challenges['Новое руководство'].completed == False:
                users[user_id].player_lvl += users[user_id].challenges['Новое руководство'].xp
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Новое руководство'].achieved(update=update, context=context), parse_mode='MarkdownV2')
            if users[user_id].player.disguise.name == 'Инструктор по йоге' and users[user_id].challenges['Поза лотоса'].completed == False:
                users[user_id].player_lvl += users[user_id].challenges['Поза лотоса'].xp
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Поза лотоса'].achieved(update=update, context=context), parse_mode='MarkdownV2')
            if users[user_id].player.disguise.name == 'Пилот' and users[user_id].challenges['Включите автопилот'].completed == False:
                users[user_id].player_lvl += users[user_id].challenges['Включите автопилот'].xp
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Включите автопилот'].achieved(update=update, context=context), parse_mode='MarkdownV2')
            if users[user_id].player.disguise.name == 'Джейсон Портман' and users[user_id].challenges['Новое лицо'].completed == False:
                users[user_id].player_lvl += users[user_id].challenges['Новое лицо'].xp
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Новое лицо'].achieved(update=update, context=context), parse_mode='MarkdownV2')
        elif users[user_id].mission == 'ica':
            if users[user_id].player.disguise.name == 'Охранник яхты' and users[user_id].challenges['Проверено охраной'].completed == False:
                users[user_id].player_lvl += users[user_id].challenges['Проверено охраной'].xp
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Проверено охраной'].achieved(update=update, context=context), parse_mode='MarkdownV2')
            if users[user_id].player.disguise.name == 'Экипаж яхты' and users[user_id].challenges['Свистать всех наверх'].completed == False:
                users[user_id].player_lvl += users[user_id].challenges['Свистать всех наверх'].xp
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Свистать всех наверх'].achieved(update=update, context=context), parse_mode='MarkdownV2')
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Текущая маскировка: {users[user_id].player.disguise.name}', reply_markup=(choose_action_keyboard(update=update, context=context)))
    else:
        query.edit_message_text(text=f'Текущая маскировка: {users[user_id].player.disguise.name}', reply_markup=(choose_action_keyboard(update=update, context=context)))


def distract_kill(update: Update, context: CallbackContext):
    """Убить после отвлечения"""
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    edit = True
    if users[user_id].player.item.name == 'Монета':
        users[user_id].player.current_location.items.append(users[user_id].player.item)
        if users[user_id].mission == 'ica':
            if users[user_id].challenges['Разменная монета'].completed == False:
                users[user_id].player_lvl += users[user_id].challenges['Разменная монета'].xp
                query.edit_message_text(text=users[user_id].challenges['Разменная монета'].achieved(update=update, context=context), parse_mode='MarkdownV2')
                edit = False
    users[user_id].player.inventory.remove(users[user_id].player.item)
    npc_name = query.data.replace('CDKL', '')
    users[user_id].kills += 1
    npc = users[user_id].npcs[npc_name]
    npc.alive = False
    users[user_id].player.found_disguises.append(npc.disguise)
    if edit:
        query.edit_message_text(text=f'Вы устранили {npc.name}', reply_markup=(choose_action_keyboard(update=update, context=context)))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Вы устранили {npc.name}', reply_markup=(choose_action_keyboard(update=update, context=context)))

def distract_knock_out(update: Update, context: CallbackContext):
    """Вырубить после отвлечения"""
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    edit = True
    if users[user_id].player.item.name == 'Монета':
        users[user_id].player.current_location.items.append(users[user_id].player.item)
        if users[user_id].mission == 'ica':
            if users[user_id].challenges['Разменная монета'].completed == False:
                users[user_id].player_lvl += users[user_id].challenges['Разменная монета'].xp
                query.edit_message_text(text=users[user_id].challenges['Разменная монета'].achieved(update=update, context=context), parse_mode='MarkdownV2')
                edit = False
    users[user_id].player.inventory.remove(users[user_id].player.item)
    npc = users[user_id].npcs[query.data.replace('CDKN', '')]
    npc.alive = False
    users[user_id].player.found_disguises.append(npc.disguise)
    if edit:
        query.edit_message_text(text=f'Вы вырубили {npc.name}', reply_markup=(choose_action_keyboard(update=update, context=context)))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Вы вырубили {npc.name}', reply_markup=(choose_action_keyboard(update=update, context=context)))


def knock_out(update: Update, context: CallbackContext):
    """Вырубить предметом"""
    user_id = update.callback_query.from_user['id']
    users[user_id].time += 5
    query = update.callback_query
    data = query.data.replace('con_knock', '')[:-1]
    chance = int(query.data.replace('con_knock', '')[-1])
    target = users[user_id].npcs[data]
    users[user_id].player.found_disguises.append(target.disguise)
    if users[user_id].thrown_weapon:
        users[user_id].player.inventory.remove(users[user_id].player.item)
        users[user_id].thrown_weapon = False
    target.alive = False
    if chance > 0:
        users[user_id].bodies += 1
        combat(update=update, context=context, start_string=f'Цель устранена: {target.name}\n\n')
    else:
        query.answer()
        query.edit_message_text(text=f'Цель устранена: {target.name}', reply_markup=(choose_action_keyboard(update=update, context=context)))

def kill(update: Update, context: CallbackContext):
    """Убить предметом"""
    user_id = update.callback_query.from_user['id']
    users[user_id].time += 5
    if users[user_id].thrown_weapon:
        users[user_id].player.inventory.remove(users[user_id].player.item)
        users[user_id].thrown_weapon = False
    query = update.callback_query
    data = query.data.replace('con_kill', '')[:-1]
    chance = int(query.data.replace('con_kill', '')[-1])
    edit = True
    if data in list(users[user_id].npcs.keys()):
        target = users[user_id].npcs[data]
        users[user_id].player.found_disguises.append(target.disguise)
        users[user_id].kills += 1
    else:
        target = users[user_id].targets[data]
        if users[user_id].mission == 'hokkaido':
            if data == 'Erich Soders' and (users[user_id].player.item.name == 'Bartoli 75R' or users[user_id].player.item.name == 'ICA 19') and users[user_id].challenges['Личное прощание'].completed == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Личное прощание'].achieved(update=update, context=context), parse_mode='MarkdownV2')
                users[user_id].player_lvl += users[user_id].challenges['Личное прощание'].xp
        edit = False
        context.bot.send_message(chat_id=update.effective_chat.id, text=target.kill())
    target.alive = False
    if chance > 0:
        users[user_id].bodies += 1
        if edit:
            combat(update=update, context=context, start_string=f'Цель устранена: {target.name}\n\n')
        else:
            combat(update=update, context=context, start_string=f'Цель устранена: {target.name}\n\n', type='add')
    else:
        if users[user_id].mission == 'hokkaido':
            if data == 'Erich Soders' and (users[user_id].player.item.name == 'Bartoli 75R' or users[user_id].player.item.name == 'ICA 19'):
                context.bot.send_message(chat_id=update.effective_chat.id, text=f'Цель устранена: {target.name}', reply_markup=(choose_action_keyboard(update=update, context=context)))
            else:
                query.answer()
                query.edit_message_text(text=f'Цель устранена: {target.name}', reply_markup=(choose_action_keyboard(update=update, context=context)))
        else:
            query.answer()
            query.edit_message_text(text=f'Цель устранена: {target.name}', reply_markup=(choose_action_keyboard(update=update, context=context)))


def move(update: Update, context: CallbackContext):
    """Передвижение по локациям"""
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    users[user_id].time += 5
    query.answer()
    move_to_location = users[user_id].locations[query.data.replace('basic_move', '')]
    edit = True
    if users[user_id].player.disguise in move_to_location.disguise:
        #Случай, когда маскировка игрока позволяет пройти на локацию
        if users[user_id].mission == 'hokkaido':
            if users[user_id].events['Информация о стволовых клетках'].completed == False and move_to_location.name == 'Операционная':
                query.edit_message_text(text=make_heading('Руководство по стволовым клеткам') + tg_text_convert('Руководство по проведению революционной терапии стволовыми клетками, разработанной доктором Лораном.\n\nОчевидно, стволовые клетки способны временно ускорять выздоровление тканей, что значительно повышает шансы пациента на выживание.\n\nСтволовые клетки забираются из специального сосуда и вливаются прямо в кровь пациента.'), parse_mode='MarkdownV2')
                users[user_id].events['Информация о стволовых клетках'].completed = True
                edit = False
            if users[user_id].events['Джейсон Портман'].completed == False and move_to_location.name == 'Холл':
                query.edit_message_text(text=make_heading('Пациент в бинтах') + tg_text_convert('Диана: У меня есть сведения о пациенте в бинтах.\n\nТак-так, это уже интересно. Забинтованный пациент — Джейсон Портман, генеральный директор «Квантум лип».\n\nСогласно моим данным, ему сделали полную реконструкцию лица и сегодня снимают повязки. И вот что самое занятное — он хочет быть как две капли воды похожим на Хельмута Крюгера.'), parse_mode='MarkdownV2')
                users[user_id].events['Джейсон Портман'].completed = True
                edit = False
            if users[user_id].events['Компьютер в морге'].completed == False and move_to_location.name == 'Морг':
                query.edit_message_text(text=make_heading('Компьютер в морге') + tg_text_convert('Вы нашли файл на компьютере. Это заметки о Кураторе и его нейрочипе.\n\nВ них приводятся подробные сведения об устройстве чипа и принципе его работы, а также описание того, как изменение дозы влияет на настроение Куратора. Судя по всему, увеличение дозы приводит к улучшению его настроения, а уменьшение, напротив, возвращает его в привычное подавленное состояние.\n\nЧто любопытно, научный сотрудник, похоже, сам менял дозу Куратора без его ведома: для этого он использовал пульт управления чипом, который куратор хранит в своей спальне.'), parse_mode='MarkdownV2')
                users[user_id].events['Компьютер в морге'].completed = True
                edit = False
            if users[user_id].events['Информация о сигаретах 2'].completed == False and move_to_location.name == 'Канатная дорога':
                query.edit_message_text(text=make_heading('Разговор телохранителей') + tg_text_convert('Диана: Значит, Юки Ямадзаки выронила свои сигареты по пути к клинике. Интересно.\n\nЮки Ямадзаки уронила свои сигареты, когда поднималась на фуникулере по прибытии в клинику. Если верить её охране, это её ужасно взбесило.\n\nМожет быть, тебе удастся утолить её «жажду», 47-й? Сигареты в «Гаме» запрещены, но не все следуют этому правилу...'), parse_mode='MarkdownV2')
                users[user_id].events['Информация о сигаретах 2'].completed = True
                edit = False
            if users[user_id].events['Информация о суши'].completed == False and move_to_location.name == 'Ресторан':
                query.edit_message_text(text=make_heading('Рыба фугу') + tg_text_convert('Диана: Ядовитая Рыба фугу и адвокат в поисках острых ощущений — убийственная комбинация.\n\nНе так давно из-за ошибки повара один из пациентов отравился ядовитой рыбой, и с тех пор фугу здесь под строжайшим запретом. Но, судя по всему, Юки Ямадзаки пытается уговорить шеф-повара подать ей последнюю рыбу из его запасов.\n\nРазве мы вправе отказывает ей в таком удовольствии, 47-й?'), parse_mode='MarkdownV2')
                users[user_id].events['Информация о суши'].completed = True
                edit = False
            if users[user_id].events['Расписание занятий по йоге'].completed == False and move_to_location.name == 'Зона отдыха':
                query.edit_message_text(text=make_heading('Расписание занятий по йоге') + tg_text_convert('Диана: Расписание занятий по йоге. Имя Юки Ямадзаки — в каждой графе. Что ж, судя по всему, Юки Ямадзаки — настоящий фанат йоги.\n\nИз расписания у горячего источника видно, что она заняла тренера на целый день. Готов размяться, 47-й?'), parse_mode='MarkdownV2')
                users[user_id].events['Расписание занятий по йоге'].completed = True
                edit = False
            if users[user_id].events['Информация о пилоте'].completed == False and (move_to_location.name == 'Вертолетная площадка' or move_to_location.name == 'Комната пилота'):
                query.edit_message_text(text=make_heading('Сведения о пилоте') + tg_text_convert('Диана: 47-й, у меня есть сведения о пилоте. Мне удалось извлечь кое-какие данные из системы безопасности клиники.\n\nГлавный хирург, Николя Лоран, похоже, часто встречается с пилотом вертолёта у выхода из мед-комплекса. А если верить слухам, у главного хирурга дрожат руки.'), parse_mode='MarkdownV2')
                users[user_id].events['Информация о пилоте'].completed = True
                edit = False
            if users[user_id].events['Информация об ИИ'].completed == False and move_to_location.name == 'Комната охраны':
                query.edit_message_text(text=make_heading('Руководство для KAI') + tg_text_convert('Интересно. Руководство для KAI, искусственного интеллекта клиники «Гама». Значит, местный искусственный интеллект по имени KAI не только поддерживает работу систем здания, но и управляет роботом в операционной.\n\nИменно там сейчас находится Содерс. В руководстве говорится, что после остановки сердца пациента искусственный интеллект автоматически начинает его реанимацию, что очень некстати.\n\nОднако... У директора клиники есть доступ к главному компьютеру. Справишься с управлением целой клиникой, 47-й?'), parse_mode='MarkdownV2')
                users[user_id].events['Информация об ИИ'].completed = True
                edit = False
        if move_to_location.unlocked == False:
            if edit:
                query.edit_message_text(text=move_to_location.unlock(update=update, context=context), parse_mode='MarkdownV2')
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text=move_to_location.unlock(update=update, context=context), parse_mode='MarkdownV2')
            edit = False
        users[user_id].player.current_location = move_to_location
        if users[user_id].player.disguise in users[user_id].player.compromised_disguises:
            #Случай, когда маскировка игрока раскрыта
            locations_npcs = find_location_npcs(update=update, context=context, location=users[user_id].player.current_location)
            if locations_npcs != []:
                location_npc = locations_npcs[random.randrange(len(locations_npcs))]
                if edit:
                    query.edit_message_text(text=location_npc.suspicion(), reply_markup=attack_keyboard(location_npc, move_to_location))
                    users[user_id].suspicion_count += 1
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=location_npc.suspicion(), reply_markup=attack_keyboard(location_npc, move_to_location))
                    users[user_id].suspicion_count += 1
            else:
                if edit:
                    query.edit_message_text(text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=choose_action_keyboard(update=update, context=context), parse_mode='MarkdownV2')
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=choose_action_keyboard(update=update, context=context), parse_mode='MarkdownV2')
        elif users[user_id].player.item.legal == False:
            #Случай, когда в руках игрока нелегальный предмет
            if (users[user_id].player.disguise.name != 'Охранник' and users[user_id].player.disguise.name != 'Телохранитель' and users[user_id].mission == 'hokkaido') or (users[user_id].player.disguise.name != 'Охранник яхты' and users[user_id].player.disguise.name != 'Телохранитель' and users[user_id].mission == 'ica'):
                if find_location_npcs(update=update, context=context, location=users[user_id].player.current_location) != []:
                    location_npc = find_location_npcs(update=update, context=context, location=users[user_id].player.current_location)[random.randrange(len(find_location_npcs(update=update, context=context, location=users[user_id].player.current_location)))]
                    users[user_id].suspicion_count += 1
                    if edit:
                        query.edit_message_text(text=f'{location_npc.name} ({location_npc.disguise.name}): Он вооружен!', reply_markup=hide_keyboard(location_npc, users[user_id].player.current_location))
                    else:
                        context.bot.send_message(chat_id=update.effective_chat.id, text=f'{location_npc.name} ({location_npc.disguise.name}): Он вооружен!', reply_markup=hide_keyboard(location_npc, users[user_id].player.current_location))
                else:
                    if edit:
                        query.edit_message_text(text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=choose_action_keyboard(update=update, context=context), parse_mode='MarkdownV2')
                    else:
                        context.bot.send_message(chat_id=update.effective_chat.id, text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=choose_action_keyboard(update=update, context=context), parse_mode='MarkdownV2')
            else:
                if edit:
                    query.edit_message_text(text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=choose_action_keyboard(update=update, context=context), parse_mode='MarkdownV2')
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=choose_action_keyboard(update=update, context=context), parse_mode='MarkdownV2')
        else:
            if edit:
                query.edit_message_text(text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=choose_action_keyboard(update=update, context=context), parse_mode='MarkdownV2')
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=choose_action_keyboard(update=update, context=context), parse_mode='MarkdownV2')
    else:
        #Случай, когда маскировка игрока не позволяет пройти на локацию
        if users[user_id].mission == 'hokkaido':
            if move_to_location.name == 'Комната с серверами':
                if users[user_id].items['Ключ-карта'] in users[user_id].player.inventory or users[user_id].items['Дешифровщик'] in users[user_id].player.inventory:
                    if move_to_location.unlocked == False:
                        if edit:
                            query.edit_message_text(text=move_to_location.unlock(update=update, context=context))
                        else:
                            context.bot.send_message(chat_id=update.effective_chat.id, text=move_to_location.unlock(update=update, context=context))
                        edit = False
                    users[user_id].player.current_location = move_to_location
                    if edit:
                        if users[user_id].targets['Erich Soders'].alive == True:
                            query.edit_message_text(text='Выберите действие', reply_markup=(destroy_servers_keyboard()))
                        else:
                            query.edit_message_text(text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=(choose_action_keyboard(update=update, context=context)), parse_mode='MarkdownV2')
                    else:
                        if users[user_id].targets['Erich Soders'].alive == True:
                            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите действие', reply_markup=(destroy_servers_keyboard()))
                        else:
                            context.bot.send_message(chat_id=update.effective_chat.id, text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=(choose_action_keyboard(update=update, context=context)), parse_mode='MarkdownV2')
                else:
                    if edit:
                        query.edit_message_text(text='Для входа необходима маскировка директора клиники или ключ-карта', reply_markup=move_keyboard(update=update, context=context))
                    else:
                        context.bot.send_message(chat_id=update.effective_chat.id, text='Для входа необходима маскировка директора клиники или ключ-карта', reply_markup=move_keyboard(update=update, context=context))
            elif move_to_location.name == 'Хранилище':
                if users[user_id].items['Дешифровщик'] in users[user_id].player.inventory:
                    if move_to_location.unlocked == False:
                        if edit:
                            query.edit_message_text(text=move_to_location.unlock(update=update, context=context))
                        else:
                            context.bot.send_message(chat_id=update.effective_chat.id, text=move_to_location.unlock(update=update, context=context))
                        edit = False
                    users[user_id].player.current_location = move_to_location
                    if edit:
                        query.edit_message_text(text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=(choose_action_keyboard(update=update, context=context)), parse_mode='MarkdownV2')
                    else:
                        context.bot.send_message(chat_id=update.effective_chat.id, text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=(choose_action_keyboard(update=update, context=context)), parse_mode='MarkdownV2')
                else:
                    if edit:
                        query.edit_message_text(text='Для входа необходима маскировка.', reply_markup=move_keyboard(update=update, context=context))
                    else:
                        context.bot.send_message(chat_id=update.effective_chat.id, text='Для входа необходима маскировка.', reply_markup=move_keyboard(update=update, context=context))
            else:
                chance = min(10, location_witnesses(update=update, context=context, location=users[user_id].player.current_location))
                query.edit_message_text(text='У вас нет подходящей маскировки. Переместиться на локацию?', reply_markup=(no_disguise_move_keyboard(chance=chance, location=move_to_location)))
        else:
            chance = min(10, location_witnesses(update=update, context=context, location=users[user_id].player.current_location))
            query.edit_message_text(text='У вас нет подходящей маскировки. Переместиться на локацию?', reply_markup=(no_disguise_move_keyboard(chance=chance, location=move_to_location)))

def safe_move(update: Update, context: CallbackContext):
    """Передвижение, не зависящее от маскировки"""
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    edit  = True
    if users[user_id].player.item.name == 'Монета':
        users[user_id].player.current_location.items.append(users[user_id].player.item)
        if users[user_id].mission == 'ica':
            if users[user_id].challenges['Разменная монета'].completed == False:
                users[user_id].player_lvl += users[user_id].challenges['Разменная монета'].xp
                query.edit_message_text(text=users[user_id].challenges['Разменная монета'].achieved(update=update, context=context), parse_mode='MarkdownV2')
                edit = False
    users[user_id].player.inventory.remove(users[user_id].player.item)
    move_to_location = users[user_id].locations[query.data.replace('SM', '')]
    users[user_id].player.current_location = move_to_location
    if users[user_id].mission == 'hokkaido':
        if users[user_id].events['Информация о стволовых клетках'].completed == False and move_to_location.name == 'Операционная':
            query.edit_message_text(text=make_heading('Руководство по стволовым клеткам') + tg_text_convert('Руководство по проведению революционной терапии стволовыми клетками, разработанной доктором Лораном.\n\nОчевидно, стволовые клетки способны временно ускорять выздоровление тканей, что значительно повышает шансы пациента на выживание.\n\nСтволовые клетки забираются из специального сосуда и вливаются прямо в кровь пациента.'), parse_mode='MarkdownV2')
            users[user_id].events['Информация о стволовых клетках'].completed = True
            edit = False
        if users[user_id].events['Джейсон Портман'].completed == False and move_to_location.name == 'Холл':
            query.edit_message_text(text=make_heading('Пациент в бинтах') + tg_text_convert('Диана: У меня есть сведения о пациенте в бинтах.\n\nТак-так, это уже интересно. Забинтованный пациент — Джейсон Портман, генеральный директор «Квантум лип».\n\nСогласно моим данным, ему сделали полную реконструкцию лица и сегодня снимают повязки. И вот что самое занятное — он хочет быть как две капли воды похожим на Хельмута Крюгера.'), parse_mode='MarkdownV2')
            users[user_id].events['Джейсон Портман'].completed = True
            edit = False
        if users[user_id].events['Компьютер в морге'].completed == False and move_to_location.name == 'Морг':
            query.edit_message_text(text=make_heading('Компьютер в морге') + tg_text_convert('Вы нашли файл на компьютере. Это заметки о Кураторе и его нейрочипе.\n\nВ них приводятся подробные сведения об устройстве чипа и принципе его работы, а также описание того, как изменение дозы влияет на настроение Куратора. Судя по всему, увеличение дозы приводит к улучшению его настроения, а уменьшение, напротив, возвращает его в привычное подавленное состояние.\n\nЧто любопытно, научный сотрудник, похоже, сам менял дозу Куратора без его ведома: для этого он использовал пульт управления чипом, который куратор хранит в своей спальне.'), parse_mode='MarkdownV2')
            users[user_id].events['Компьютер в морге'].completed = True
            edit = False
        if users[user_id].events['Информация о сигаретах 2'].completed == False and move_to_location.name == 'Канатная дорога':
            query.edit_message_text(text=make_heading('Разговор телохранителей') + tg_text_convert('Диана: Значит, Юки Ямадзаки выронила свои сигареты по пути к клинике. Интересно.\n\nЮки Ямадзаки уронила свои сигареты, когда поднималась на фуникулере по прибытии в клинику. Если верить её охране, это её ужасно взбесило.\n\nМожет быть, тебе удастся утолить её «жажду», 47-й? Сигареты в «Гаме» запрещены, но не все следуют этому правилу...'), parse_mode='MarkdownV2')
            users[user_id].events['Информация о сигаретах 2'].completed = True
            edit = False
        if users[user_id].events['Информация о суши'].completed == False and move_to_location.name == 'Ресторан':
            query.edit_message_text(text=make_heading('Рыба фугу') + tg_text_convert('Диана: Ядовитая Рыба фугу и адвокат в поисках острых ощущений — убийственная комбинация.\n\nНе так давно из-за ошибки повара один из пациентов отравился ядовитой рыбой, и с тех пор фугу здесь под строжайшим запретом. Но, судя по всему, Юки Ямадзаки пытается уговорить шеф-повара подать ей последнюю рыбу из его запасов.\n\nРазве мы вправе отказывает ей в таком удовольствии, 47-й?'), parse_mode='MarkdownV2')
            users[user_id].events['Информация о суши'].completed = True
            edit = False
        if users[user_id].events['Расписание занятий по йоге'].completed == False and move_to_location.name == 'Зона отдыха':
            query.edit_message_text(text=make_heading('Расписание занятий по йоге') + tg_text_convert('Диана: Расписание занятий по йоге. Имя Юки Ямадзаки — в каждой графе. Что ж, судя по всему, Юки Ямадзаки — настоящий фанат йоги.\n\nИз расписания у горячего источника видно, что она заняла тренера на целый день. Готов размяться, 47-й?'), parse_mode='MarkdownV2')
            users[user_id].events['Расписание занятий по йоге'].completed = True
            edit = False
        if users[user_id].events['Информация о пилоте'].completed == False and (move_to_location.name == 'Вертолетная площадка' or move_to_location.name == 'Комната пилота'):
            query.edit_message_text(text=make_heading('Сведения о пилоте') + tg_text_convert('Диана: 47-й, у меня есть сведения о пилоте. Мне удалось извлечь кое-какие данные из системы безопасности клиники.\n\nГлавный хирург, Николя Лоран, похоже, часто встречается с пилотом вертолёта у выхода из мед-комплекса. А если верить слухам, у главного хирурга дрожат руки.'), parse_mode='MarkdownV2')
            users[user_id].events['Информация о пилоте'].completed = True
            edit = False
        if users[user_id].events['Информация об ИИ'].completed == False and move_to_location.name == 'Комната охраны':
            query.edit_message_text(text=make_heading('Руководство для KAI') + tg_text_convert('Интересно. Руководство для KAI, искусственного интеллекта клиники «Гама». Значит, местный искусственный интеллект по имени KAI не только поддерживает работу систем здания, но и управляет роботом в операционной.\n\nИменно там сейчас находится Содерс. В руководстве говорится, что после остановки сердца пациента искусственный интеллект автоматически начинает его реанимацию, что очень некстати.\n\nОднако... У директора клиники есть доступ к главному компьютеру. Справишься с управлением целой клиникой, 47-й?'), parse_mode='MarkdownV2')
            users[user_id].events['Информация об ИИ'].completed = True
            edit = False
    if move_to_location.unlocked == False:
        if edit:
            query.edit_message_text(text=move_to_location.unlock(update=update, context=context), parse_mode='MarkdownV2')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=move_to_location.unlock(update=update, context=context), parse_mode='MarkdownV2')
        edit = False
    if edit:
        query.edit_message_text(text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=(choose_action_keyboard(update=update, context=context)), parse_mode='MarkdownV2')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=(choose_action_keyboard(update=update, context=context)), parse_mode='MarkdownV2')

def no_disguise_move(update: Update, context: CallbackContext):
    """Передвижение без необходимой маскировки"""
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    chance = int(query.data.replace('ПРТ', '').split(':')[0])
    move_to_location = users[user_id].locations[query.data.replace('ПРТ', '').split(':')[1]]
    edit = True
    if users[user_id].mission == 'hokkaido':
        if users[user_id].events['Информация о стволовых клетках'].completed == False and move_to_location.name == 'Операционная':
            query.edit_message_text(text=make_heading('Руководство по стволовым клеткам') + tg_text_convert('Руководство по проведению революционной терапии стволовыми клетками, разработанной доктором Лораном.\n\nОчевидно, стволовые клетки способны временно ускорять выздоровление тканей, что значительно повышает шансы пациента на выживание.\n\nСтволовые клетки забираются из специального сосуда и вливаются прямо в кровь пациента.'), parse_mode='MarkdownV2')
            users[user_id].events['Информация о стволовых клетках'].completed = True
            edit = False
        if users[user_id].events['Джейсон Портман'].completed == False and move_to_location.name == 'Холл':
            query.edit_message_text(text=make_heading('Пациент в бинтах') + tg_text_convert('Диана: У меня есть сведения о пациенте в бинтах.\n\nТак-так, это уже интересно. Забинтованный пациент — Джейсон Портман, генеральный директор «Квантум лип».\n\nСогласно моим данным, ему сделали полную реконструкцию лица и сегодня снимают повязки. И вот что самое занятное — он хочет быть как две капли воды похожим на Хельмута Крюгера.'), parse_mode='MarkdownV2')
            users[user_id].events['Джейсон Портман'].completed = True
            edit = False
        if users[user_id].events['Компьютер в морге'].completed == False and move_to_location.name == 'Морг':
            query.edit_message_text(text=make_heading('Компьютер в морге') + tg_text_convert('Вы нашли файл на компьютере. Это заметки о Кураторе и его нейрочипе.\n\nВ них приводятся подробные сведения об устройстве чипа и принципе его работы, а также описание того, как изменение дозы влияет на настроение Куратора. Судя по всему, увеличение дозы приводит к улучшению его настроения, а уменьшение, напротив, возвращает его в привычное подавленное состояние.\n\nЧто любопытно, научный сотрудник, похоже, сам менял дозу Куратора без его ведома: для этого он использовал пульт управления чипом, который куратор хранит в своей спальне.'), parse_mode='MarkdownV2')
            users[user_id].events['Компьютер в морге'].completed = True
            edit = False
        if users[user_id].events['Информация о сигаретах 2'].completed == False and move_to_location.name == 'Канатная дорога':
            query.edit_message_text(text=make_heading('Разговор телохранителей') + tg_text_convert('Диана: Значит, Юки Ямадзаки выронила свои сигареты по пути к клинике. Интересно.\n\nЮки Ямадзаки уронила свои сигареты, когда поднималась на фуникулере по прибытии в клинику. Если верить её охране, это её ужасно взбесило.\n\nМожет быть, тебе удастся утолить её «жажду», 47-й? Сигареты в «Гаме» запрещены, но не все следуют этому правилу...'), parse_mode='MarkdownV2')
            users[user_id].events['Информация о сигаретах 2'].completed = True
            edit = False
        if users[user_id].events['Информация о суши'].completed == False and move_to_location.name == 'Ресторан':
            query.edit_message_text(text=make_heading('Рыба фугу') + tg_text_convert('Диана: Ядовитая Рыба фугу и адвокат в поисках острых ощущений — убийственная комбинация.\n\nНе так давно из-за ошибки повара один из пациентов отравился ядовитой рыбой, и с тех пор фугу здесь под строжайшим запретом. Но, судя по всему, Юки Ямадзаки пытается уговорить шеф-повара подать ей последнюю рыбу из его запасов.\n\nРазве мы вправе отказывает ей в таком удовольствии, 47-й?'), parse_mode='MarkdownV2')
            users[user_id].events['Информация о суши'].completed = True
            edit = False
        if users[user_id].events['Расписание занятий по йоге'].completed == False and move_to_location.name == 'Зона отдыха':
            query.edit_message_text(text=make_heading('Расписание занятий по йоге') + tg_text_convert('Диана: Расписание занятий по йоге. Имя Юки Ямадзаки — в каждой графе. Что ж, судя по всему, Юки Ямадзаки — настоящий фанат йоги.\n\nИз расписания у горячего источника видно, что она заняла тренера на целый день. Готов размяться, 47-й?'), parse_mode='MarkdownV2')
            users[user_id].events['Расписание занятий по йоге'].completed = True
            edit = False
        if users[user_id].events['Информация о пилоте'].completed == False and (move_to_location.name == 'Вертолетная площадка' or move_to_location.name == 'Комната пилота'):
            query.edit_message_text(text=make_heading('Сведения о пилоте') + tg_text_convert('Диана: 47-й, у меня есть сведения о пилоте. Мне удалось извлечь кое-какие данные из системы безопасности клиники.\n\nГлавный хирург, Николя Лоран, похоже, часто встречается с пилотом вертолёта у выхода из мед-комплекса. А если верить слухам, у главного хирурга дрожат руки.'), parse_mode='MarkdownV2')
            users[user_id].events['Информация о пилоте'].completed = True
            edit = False
        if users[user_id].events['Информация об ИИ'].completed == False and move_to_location.name == 'Комната охраны':
            query.edit_message_text(text=make_heading('Руководство для KAI') + tg_text_convert('Интересно. Руководство для KAI, искусственного интеллекта клиники «Гама». Значит, местный искусственный интеллект по имени KAI не только поддерживает работу систем здания, но и управляет роботом в операционной.\n\nИменно там сейчас находится Содерс. В руководстве говорится, что после остановки сердца пациента искусственный интеллект автоматически начинает его реанимацию, что очень некстати.\n\nОднако... У директора клиники есть доступ к главному компьютеру. Справишься с управлением целой клиникой, 47-й?'), parse_mode='MarkdownV2')
            users[user_id].events['Информация об ИИ'].completed = True
            edit = False
    if move_to_location.unlocked == False:
        if edit:
            query.edit_message_text(text=move_to_location.unlock(update=update, context=context), parse_mode='MarkdownV2')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=move_to_location.unlock(update=update, context=context), parse_mode='MarkdownV2')
        edit = False
    if random.randrange(1, 11) <= chance:
        users[user_id].player.current_location = move_to_location
        query.answer()
        if edit:
            query.edit_message_text(text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=(choose_action_keyboard(update=update, context=context)), parse_mode='MarkdownV2')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=(choose_action_keyboard(update=update, context=context)), parse_mode='MarkdownV2')
    else:
        users[user_id].player.compromised_disguises.append(users[user_id].player.disguise)
        locations_npcs = find_location_npcs(update=update, context=context, location=users[user_id].player.current_location)
        location_npc = locations_npcs[random.randrange(len(locations_npcs))]
        query.answer()
        if edit:
            query.edit_message_text(text=location_npc.suspicion(), reply_markup=attack_keyboard(location_npc, move_to_location))
            users[user_id].suspicion_count += 1
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,text=location_npc.suspicion(), reply_markup=attack_keyboard(location_npc, move_to_location))
            users[user_id].suspicion_count += 1


def combat(update: Update, context: CallbackContext, start_string='', type='edit'):
    """Бой"""
    start_string = make_heading('Бой') + start_string
    user_id = update.callback_query.from_user['id']
    users[user_id].time += 5
    enemies = []
    query = update.callback_query

    for i in find_location_npcs(update=update, context=context, location=users[user_id].player.current_location):
        if i.guard:
            enemies.append(i)
    if type == 'edit':
        if users[user_id].player.health == 0:
            query.answer()
            query.edit_message_text(text='Вы умерли. Миссия провалена.', parse_mode='MarkdownV2')
        if enemies == []:
            users[user_id].player.health = 100
            query.answer()
            query.edit_message_text(text=start_string + f'*_Бой закончился_*\.\n\nУбито невинных: {users[user_id].kills}\nНайдено тел: {users[user_id].bodies}', reply_markup=(choose_action_keyboard(update=update, context=context)), parse_mode='MarkdownV2')
        else:
            query.answer()
            query.edit_message_text(text=start_string + f'Выберите оружие', reply_markup=(choose_weapon_keyboard(update=update, context=context)), parse_mode='MarkdownV2')
    elif type == 'add':
        if users[user_id].player.health == 0:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Вы умерли. Миссия провалена.', parse_mode='MarkdownV2')
        if enemies == []:
            users[user_id].player.health = 100
            context.bot.send_message(chat_id=update.effective_chat.id, text=start_string + f'*_Бой закончился_*\.\n\nУбито невинных: {users[user_id].kills}\nНайдено тел: {users[user_id].bodies}', reply_markup=(choose_action_keyboard(update=update, context=context)), parse_mode='MarkdownV2')
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=start_string + f'Выберите оружие', reply_markup=(choose_weapon_keyboard(update=update, context=context)), parse_mode='MarkdownV2')

def combat_chance(update: Update, context: CallbackContext):
    """Проверка вероятности во время боя"""
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    chance = int(query.data.replace('CWA', '')[-5])
    if random.randrange(1, 11) <= chance:
        if users[user_id].player.item.lethal:
            users[user_id].kills += 1
        enemies = []
        for i in find_location_npcs(update=update, context=context, location=users[user_id].player.current_location):
            if i.guard:
                enemies.append(i)
        if enemies != []:
            enemies[0].alive = False
        if location_witnesses(update=update, context=context, location=users[user_id].player.current_location) > 0:
            users[user_id].bodies += 1
        if 'Бросить' in query.data:
            users[user_id].player.current_location.items.append(users[user_id].player.item)
            users[user_id].player.inventory.remove(users[user_id].player.item)
        combat(update=update, context=context, start_string=f'Противник устранён: {enemies[0].name}\n\n')
    else:
        if 'Бросить' in query.data:
            users[user_id].player.current_location.items.append(users[user_id].player.item)
            users[user_id].player.inventory.remove(users[user_id].player.item)
        users[user_id].player.health -= 25
        combat(update=update, context=context, start_string='Промах\n\n')

def hide_combat(update: Update, context: CallbackContext):
    """Скрыться во время боя"""
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    if random.randrange(1, 11) <= 5:
        users[user_id].player.compromised_disguises.append(users[user_id].player.disguise)
        query.answer()
        query.edit_message_text(text='Ваша маскировка раскрыта, при перемещении в любую локацию вас будут узнавать.', reply_markup=(choose_action_keyboard(update=update, context=context)))
    else:
        query.answer()
        query.edit_message_text(text='Вы умерли. Миссия провалена.')

def hide(update: Update, context: CallbackContext):
    """Скрыться после того, как вас заметили"""
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    if random.randrange(1, 11) <= 7:
        users[user_id].player.compromised_disguises.append(users[user_id].player.disguise)
        query.answer()
        query.edit_message_text(text='Ваша маскировка раскрыта, при перемещении в любую локацию вас будут узнавать.', reply_markup=(choose_action_keyboard(update=update, context=context)))
    else:
        query.answer()
        query.edit_message_text(text=f'Начался бой.', reply_markup=(combat_start_keyboard()))

def attack_npc(update: Update, context: CallbackContext):
    """Нападение на NPC, когда вас заметили"""
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    npc = users[user_id].npcs[query.data.replace('НПД', '').split(':')[0]]
    move_to_location = users[user_id].locations[query.data.replace('НПД', '').split(':')[1]]
    if random.randrange(1, 11) <= 3:
        users[user_id].player.current_location = move_to_location
        npc.alive = False
        users[user_id].player.found_disguises.append(npc.disguise)
        query.answer()
        query.edit_message_text(text=f'Вам удалось тихо устранить {npc.name}', reply_markup=(choose_action_keyboard(update=update, context=context)))
    else:
        query.answer()
        query.edit_message_text(text=f'Начался бой.', reply_markup=(combat_start_keyboard()))


def spawn_player(update: Update, context: CallbackContext):
    """Задать начальные параметры для игрока"""
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    if 'ХоккЯП' in query.data:
        users[user_id].change_mission('hokkaido')
    elif 'СТ' in query.data or 'ТПН' in query.data:
        users[user_id].change_mission('ica')
    if users[user_id].completed_challenges:
        for i in users[user_id].completed_challenges.split(';'):
            users[user_id].challenges[i].completed = True
    if users[user_id].unlocked_disguises:
        for i in users[user_id].unlocked_disguises.split(';'):
            users[user_id].disguises[i].unlocked = True
    if users[user_id].unlocked_locations:
        for i in users[user_id].unlocked_locations.split(';'):
            users[user_id].locations[i].unlocked = True
    if users[user_id].mission == 'hokkaido':
        if users[user_id].loadout['Начальная локация']:
            users[user_id].player.current_location = users[user_id].locations[users[user_id].loadout['Начальная локация']]
        else:
            users[user_id].player.current_location = users[user_id].locations['Номер 47-го']
        users[user_id].player.inventory = []
        if users[user_id].loadout['Пистолет']:
            users[user_id].player.inventory.append(users[user_id].items[users[user_id].loadout['Пистолет']])
        if users[user_id].loadout['Снаряжение 1']:
            users[user_id].player.inventory.append(users[user_id].items[users[user_id].loadout['Снаряжение 1']])
            if users[user_id].loadout['Снаряжение 1'] == 'Монета':
                users[user_id].player.inventory.append(users[user_id].items[users[user_id].loadout['Снаряжение 1']])
                users[user_id].player.inventory.append(users[user_id].items[users[user_id].loadout['Снаряжение 1']])
        if users[user_id].loadout['Снаряжение 2']:
            users[user_id].player.inventory.append(users[user_id].items[users[user_id].loadout['Снаряжение 2']])
            if users[user_id].loadout['Снаряжение 2'] == 'Монета':
                users[user_id].player.inventory.append(users[user_id].items[users[user_id].loadout['Снаряжение 2']])
                users[user_id].player.inventory.append(users[user_id].items[users[user_id].loadout['Снаряжение 2']])
        for i in list(hokkaido_lvl_unlocks.values()):
            if i[0] == users[user_id].player.current_location.name:
                start_disguise = users[user_id].disguises[i[1]]
        users[user_id].player.found_disguises = [start_disguise]
        users[user_id].player.item = users[user_id].items['Нет предмета']
        users[user_id].player.compromised_disguises = []
        users[user_id].player.disguise = start_disguise
        if users[user_id].player.disguise.name != 'VIP - пациент':
            users[user_id].suit_only = False
        text = make_heading('Добро пожаловать на Хоккайдо') + tg_text_convert('Диана: Добро пожаловать на Хоккайдо, 47-й. Частная клиника «Гама» оказывает медицинские услуги высочайшего уровня представителям мировой элиты, выходя при необходимости за рамки закона\n\n Частично здание находится под управлением искусственного интеллекта — KAI. Система контролирует доступ пациентов в разные части клиники и даже принимает участие в ряде медицинских процедур.\n\nЭрих Содерс уже находится в операционной, где он проходит предварительную подготовку с применением стволовых клеток. Это крайне противоречивая процедура ещё не одобрена властями Японии.\n\nЮки Ямадзаки уже прибыла. Она находится либо в своём номере, либо в ресторане, либо в спа-зоне клиники. Содерсу скоро введут наркоз. Сделай так, чтобы он больше никогда не проснулся. Удачи, 47-й.')
        if users[user_id].player.current_location.name == 'Номер 47-го':
            query.edit_message_text(text=text, parse_mode='MarkdownV2')
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите действие', reply_markup=(choose_action_keyboard(update=update, context=context)))
        else:
            query.edit_message_text(text='Выберите действие', reply_markup=(choose_action_keyboard(update=update, context=context)))
    elif users[user_id].mission == 'ica':
        users[user_id].player.found_disguises = [users[user_id].disguises['Тактическая водолазка']]
        users[user_id].player.item = users[user_id].items['Нет предмета']
        users[user_id].player.compromised_disguises = []
        users[user_id].player.current_location = users[user_id].locations['Пирс']
        users[user_id].player.disguise = users[user_id].disguises['Тактическая водолазка']
        users[user_id].player.inventory = [users[user_id].items['ICA 19'], users[user_id].items['Удавка']]
        if 'СТ' in query.data:
            query.edit_message_text(text='Диана: Снова здравствуй. Агенты МКА способны любое задание выполнить разными способами.\n\nПовтори упражнение, но теперь используй другой подход. Импровизируй, меняй стратегию.\n\nМы будем следить за тобой.')
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите действие', reply_markup=(choose_action_keyboard(update=update, context=context)))
        elif 'ТПН' in query.data:
            query.edit_message_text(text='Диана: Добро пожаловать на тренировку повышенной сложности. Прототипом этого задания стала операция в Сиднее.\n\nЦелью был Кэлвин Риттер, знаменитый грабитель по прозвищу Воробей. Тебе нужно проникнуть на яхту, изолировать, а затем устранить цель и скрыться — всё незаметно.\n\nЗапомни: ты агент МКА, самый опасный человек в любой ситуации. Но грубой силой в нашем деле многого не добьёшься, а настоящий профессионал никогда не привлекает внимания.\n\nУдачи, новичок.')
            context.bot.send_message(chat_id=update.effective_chat.id, text='Диана: Я думаю для начала тебе стоит осмотреться\.\n\n_Используйте Статус\, чтобы посмотреть состояние миссии и текущей локации\._', reply_markup=tutorial_keyboard_1(), parse_mode='MarkdownV2')

def rating(update: Update, context: CallbackContext):
    """Вывод статистики, сохранение и выход"""
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    result_string = f'Тел найдено: {users[user_id].bodies}\n'
    result_string += f'Убито невинных: {users[user_id].kills}\n'
    result_string += f'Вы были замечены {users[user_id].suspicion_count} раз\n\n'
    rating = max(int(5-(users[user_id].bodies*0.5)-(users[user_id].kills*0.7)-(users[user_id].suspicion_count*0.2)), 0)
    result_string += f'Ваш рейтинг: {rating}/5'
    query.edit_message_text(text=result_string)
    if users[user_id].mission == 'hokkaido':
        if rating == 5 and users[user_id].suit_only == False:
            if users[user_id].challenges['Бесшумный убийца'].completed == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Бесшумный убийца'].achieved(update=update, context=context), parse_mode='MarkdownV2')
                users[user_id].player_lvl += users[user_id].challenges['Бесшумный убийца'].xp
        if rating == 5 and users[user_id].suit_only:
            if users[user_id].challenges['Бесшумный убийца. Только костюм.'].completed == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Бесшумный убийца. Только костюм.'].achieved(update=update, context=context), parse_mode='MarkdownV2')
                users[user_id].player_lvl += users[user_id].challenges['Бесшумный убийца. Только костюм.'].xp
        if users[user_id].suit_only:
            if users[user_id].challenges['Только костюм'].completed == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Только костюм'].achieved(update=update, context=context), parse_mode='MarkdownV2')
                users[user_id].player_lvl += users[user_id].challenges['Только костюм'].xp
        if users[user_id].bodies == 0:
            if users[user_id].challenges['Без улик'].completed == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Без улик'].achieved(update=update, context=context), parse_mode='MarkdownV2')
                users[user_id].player_lvl += users[user_id].challenges['Без улик'].xp
        if users[user_id].challenges['Точный выстрел'].completed == True and users[user_id].challenges['Подержи волосы'].completed == True and users[user_id].challenges['Пианист'].completed == True and users[user_id].challenges['Так можно и пораниться'].completed == True and users[user_id].challenges['Без вкуса, без следа'].completed == True and users[user_id].challenges['Мастер-убийца'].completed == False:
            context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Мастер-убийца'].achieved(update=update, context=context), parse_mode='MarkdownV2')
            users[user_id].player_lvl += users[user_id].challenges['Мастер-убийца'].xp
    users[user_id].player_lvl += rating
    completed_challenges = []
    for i in list(users[user_id].challenges.values()):
        if i.completed:
            completed_challenges.append(i.name)
    unlocked_disguises = []
    for i in list(users[user_id].disguises.values()):
        if i.unlocked:
            unlocked_disguises.append(i.name)
    unlocked_locations = []
    for i in list(users[user_id].locations.values()):
        if i.unlocked:
            unlocked_locations.append(i.name)
    completed_challenges_str = ';'.join(completed_challenges)
    unlocked_disguises_str = ';'.join(unlocked_disguises)
    unlocked_locations_str = ';'.join(unlocked_locations)
    adapter.update_by_id("users", f'{users[user_id].mission}_completed_challenges={completed_challenges_str}', user_id)
    adapter.update_by_id("users", f'{users[user_id].mission}_unlocked_disguises={unlocked_disguises_str}', user_id)
    adapter.update_by_id("users", f'{users[user_id].mission}_unlocked_locations={unlocked_locations_str}', user_id)
    adapter.update_by_id("users", f'player_lvl={users[user_id].player_lvl}', user_id)
    users[user_id] = create_user(user_id=user_id)
    context.bot.send_message(chat_id=update.effective_chat.id, text='*_Миссия выполнена\._*', parse_mode='MarkdownV2')



#----------Брифинг----------

def hokkaido_briefing_1(update: Update, context: CallbackContext):
    """Брифинг к миссии"""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Диана: Доброе утро, 47-й. Совет директоров одобрил ликвидацию Эриха Содерса. После Колорадо мы решили пристально изучить личные дела Содерса и выяснили, что его недавно доставили в частную клинику «Гама» на японском острове Хоккайдо для срочной операции на сердце. Без «Провиденс» тут явно не обошлось.', reply_markup=(hokkaido_briefing_keyboard_1(update=update, context=context)))

def hokkaido_briefing_2(update: Update, context: CallbackContext):
    """Брифинг к миссии"""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Диана: Доброе утро, 47-й. Совет директоров одобрил ликвидацию Эриха Содерса. После Колорадо мы решили пристально изучить личные дела Содерса и выяснили, что его недавно доставили в частную клинику «Гама» на японском острове Хоккайдо для срочной операции на сердце. Без «Провиденс» тут явно не обошлось.')
    context.bot.send_message(chat_id=update.effective_chat.id, text='Содерс страдает от редкой врожденной патологии — транспозиции органов: его внутренние органы в теле расположены зеркально. Для трансплантации ему необходимо правостороннее сердце, и он явно предал МКА, чтобы получить его. Его приняли прошлой ночью и сейчас он готовится к трёхэтапной операции.', reply_markup=(hokkaido_briefing_keyboard_2(update=update, context=context)))

def hokkaido_briefing_3(update: Update, context: CallbackContext):
    """Брифинг к миссии"""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Содерс страдает от редкой врожденной патологии — транспозиции органов: его внутренние органы в теле расположены зеркально. Для трансплантации ему необходимо правостороннее сердце, и он явно предал МКА, чтобы получить его. Его приняли прошлой ночью и сейчас он готовится к трёхэтапной операции.')
    context.bot.send_message(chat_id=update.effective_chat.id, text='Под видом Тобиаса Рипера, крупного бизнесмена, ты отправляешься в «Гаму» для стандартного медицинского обследования, о формальностях мы уже позаботились. В таких условиях придётся импровизировать и самостоятельно добывать снаряжение.', reply_markup=(hokkaido_briefing_keyboard_3(update=update, context=context)))

def hokkaido_briefing_4(update: Update, context: CallbackContext):
    """Брифинг к миссии"""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Под видом Тобиаса Рипера, крупного бизнесмена, ты отправляешься в «Гаму» для стандартного медицинского обследования, о формальностях мы уже позаботились. В таких условиях придётся импровизировать и самостоятельно добывать снаряжение.')
    context.bot.send_message(chat_id=update.effective_chat.id, text='Кроме того, тебе нужно ликвидировать Юки Ямадзаки — она адвокат из Токио, работает на «Провиденс». Содерс уже передал Ямадзаки доступ к нашей базе клиентов и согласился предоставить полный список оперативных сотрудников МКА после завершения операции. Этого допустить никак нельзя. Содерс должен заплатить за своё предательство — это послужит хорошим уроком его нанимателям.', reply_markup=(hokkaido_briefing_keyboard_4(update=update, context=context)))

def hokkaido_briefing_5(update: Update, context: CallbackContext):
    """Брифинг к миссии"""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Кроме того, тебе нужно ликвидировать Юки Ямадзаки — она адвокат из Токио, работает на «Провиденс». Содерс уже передал Ямадзаки доступ к нашей базе клиентов и согласился предоставить полный список оперативных сотрудников МКА после завершения операции. Этого допустить никак нельзя. Содерс должен заплатить за своё предательство — это послужит хорошим уроком его нанимателям.')
    context.bot.send_message(chat_id=update.effective_chat.id, text='На кону будущее и репутация МКА. Какой бы властью и могуществом ни обладала «Провиденс», пора поставить их на место.', reply_markup=(hokkaido_briefing_keyboard_5(update=update, context=context)))

def hokkaido_briefing_6(update: Update, context: CallbackContext):
    """Брифинг к миссии"""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='На кону будущее и репутация МКА. Какой бы властью и могуществом ни обладала «Провиденс», пора поставить их на место.')
    context.bot.send_message(chat_id=update.effective_chat.id, text='Я оставлю тебя подготавливаться.', reply_markup=(hokkaido_briefing_keyboard_6(update=update, context=context)))


def ica_briefing_1(update: Update, context: CallbackContext):
    """Брифинг к миссии"""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Диана: Добро пожаловать на тренировку повышенной сложности. Прототипом этого задания стала операция в Сиднее.\n\nЦелью был Кэлвин Риттер, знаменитый грабитель по прозвищу Воробей. Тебе нужно проникнуть на яхту, изолировать, а затем устранить цель и скрыться — всё незаметно.\n\nЗапомни: ты агент МКА, самый опасный человек в любой ситуации. Но грубой силой в нашем деле многого не добьёшься, а настоящий профессионал никогда не привлекает внимания.\n\nУдачи, новичок.', reply_markup=(ica_briefing_keyboard_1(update=update, context=context)))

def ica_briefing_2(update: Update, context: CallbackContext):
    """Брифинг к миссии"""
    query = update.callback_query
    query.answer()
    query.edit_message_text(text='Диана: Снова здравствуй. Агенты МКА способны любое задание выполнить разными способами.\n\nПовтори упражнение, но теперь используй другой подход. Импровизируй, меняй стратегию.\n\nМы будем следить за тобой.', reply_markup=(ica_briefing_keyboard_2(update=update, context=context)))


#----------Команды бота----------

def help(update: Update, context: CallbackContext):
    """Вывод инструкции к игре"""
    context.bot.send_photo(chat_id=update.effective_chat.id, photo='https://media.hitmaps.com/img/hitman3/story/background_season2.jpg')
    context.bot.send_message(chat_id=update.effective_chat.id, text=make_heading('Обучение') + '*_Передвежение_* – перемещение по локациям игры\. Иногда данное действие требует некоторых условий, таких как нужной маскировки или небходимого предмета\.\n\n*_Взаимодействие_* – использование текущего предмета\. Может являться нелегальным действием\.\n\n*_Инвентарь_* – открытие меню с вашими предметами и текущей маскировкой\.\n\n*_Обыскать локацию_* – добавляет все предметы на текущей локации вам в инвентарь\.\n\n*_Статус_* – показывает нахождение целей задания, а также состояние текущей локации\.\n\n*_Испытания_* – открывает список со всеми испытаниями\. Выполненные испытания отмечаются отдельно\.\n\n*_Сохранить и выйти_* – завершает игру, сохраняя текущие выполненные испытания, а также уровень игрока\.\n\n*_Уровень игрока_* – за выполнение испытаний, а также прохождения уровня на высокий рейтинг у вас будут появляться новые стартовые локации, и появится возможность брать с собой снаряжение\.\n\n*_Рейтинг задания_* – убийство невинных, количество найденных тел и раз, когда вас заметили – всё это снижает рейтинг прохождения\.\n\n*_Система шансов_* – успех некоторых действий зависит от пределенного шанса, написанного в скобках рядом с ним\. Шанс является вероятностью выполнения действия, то есть десйствие с шансом "\(7/10\)" будет выполняться с вероятностью 0,7\.', parse_mode='MarkdownV2')
    #context.bot.send_message(chat_id=update.effective_chat.id, text='Пройти обучающий уровень?', reply_markup=accept_tutorial_keyboard())

def support(update: Update, context: CallbackContext):
    """Вывод поддержки авторов"""
    context.bot.send_photo(chat_id=update.effective_chat.id, photo='https://4kwallpapers.com/images/wallpapers/agent-47-hitman-3840x2160-13948.jpeg')
    context.bot.send_message(chat_id=update.effective_chat.id, text=make_heading('Поддержать авторов') + 'Рады\, что вам понравилась наша игра\.\n\nОтправьте нам донат: `4817760323535330` \(Виолетта\)', parse_mode='MarkdownV2')

def stats(update: Update, context: CallbackContext):
    """Вывод статистики игрока"""
    user_id = update.message.from_user['id']
    text = make_heading('Карьера')
    text += f'*_Текущий уровень: {users[user_id].player_lvl // 6}_*\n\n'
    text_check = make_heading('Карьера') + f'*_Текущий уровень: {users[user_id].player_lvl // 6}_*\n\n' + make_heading('Свободная тренировка')
    users[user_id].change_mission('ica')
    text += make_heading('Свободная тренировка')
    if users[user_id].completed_challenges:
        text += '*_Выполненные испытания:_*\n\n'
        for i in users[user_id].completed_challenges.split(';'):
            text += tg_text_convert(users[user_id].challenges[i].name) + '\n'
        text += '\n'
    if users[user_id].unlocked_disguises:
        text += '*_Открытые маскировки:_*\n\n'
        for i in users[user_id].unlocked_disguises.split(';'):
            text += tg_text_convert(users[user_id].disguises[i].name) + '\n'
        text += '\n'
    if users[user_id].unlocked_locations:
        text += '*_Открытые локации:_*\n\n'
        for i in users[user_id].unlocked_locations.split(';'):
            text += tg_text_convert(users[user_id].locations[i].name) + '\n'
        text += '\n'
    if text == text_check:
        text += 'Пока у вас нет достижений\n\n'
    users[user_id].change_mission('hokkaido')
    text_2 = make_heading('Транспозиция органов')
    text_check_2 = make_heading('Транспозиция органов')
    if users[user_id].completed_challenges:
        text_2 += '*_Выполненные испытания:_*\n\n'
        for i in users[user_id].completed_challenges.split(';'):
            text_2 += tg_text_convert(users[user_id].challenges[i].name) + '\n'
        text_2 += '\n'
    if users[user_id].unlocked_disguises:
        text_2 += '*_Открытые маскировки:_*\n\n'
        for i in users[user_id].unlocked_disguises.split(';'):
            text_2 += tg_text_convert(users[user_id].disguises[i].name) + '\n'
        text_2 += '\n'
    if users[user_id].unlocked_locations:
        text_2 += '*_Открытые локации:_*\n\n'
        for i in users[user_id].unlocked_locations.split(';'):
            text_2 += tg_text_convert(users[user_id].locations[i].name) + '\n'
        text_2 += '\n'
    if text_2 == text_check_2:
        text_2 += 'Пока у вас нет достижений\n\n'
    users[user_id].change_mission('ica')
    text += text_2 + '\n'
    text += '||Здесь отображаются только сохранённые достижения\. Новые достижения появятся после завершения миссии\.||'
    context.bot.send_photo(chat_id=update.effective_chat.id, photo='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS6aeydIURHFfHBqGd1-qU9CXxHZfbRw44wTVqkuF09Rg&s')
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode='MarkdownV2')

def start(update: Update, context: CallbackContext):
    """Начало работы бота"""
    global users
    user_id = update.message.from_user['id']
    user_nickname = str(update.message.from_user['username'])
    chat_id = int(update.effective_chat.id)
    created = int(tm.time())
    if adapter.search('users', f'id={user_id}') == 0:
        adapter.insert('users', [
            f'id={user_id}',
            f'chat_id={chat_id}',
            f'created={created}',
            f'user_nickname={user_nickname}',
            f'updated={created}'
        ])
        users[user_id] = create_user(user_id=user_id)
    if update.message['message_id'] != users[user_id].message:
        users[user_id].message = update.message['message_id']
        updated = int(tm.time())
    adapter.update_by_id("users", f'updated={updated}', user_id)
    users[user_id].message = update.message['message_id']
    context.bot.send_message(chat_id=update.effective_chat.id, text='*_Добро пожаловать\!_*\n\nИспользуйте меню, чтобы начать игру\.', parse_mode='MarkdownV2')

def new_game(update: Update, context: CallbackContext):
    """Начало новой игры"""
    user_id = update.message.from_user['id']
    if users[user_id].time != 0:
        completed_challenges = []
        for i in list(users[user_id].challenges.values()):
            if i.completed:
                completed_challenges.append(i.name)
        unlocked_disguises = []
        for i in list(users[user_id].disguises.values()):
            if i.unlocked:
                unlocked_disguises.append(i.name)
        unlocked_locations = []
        for i in list(users[user_id].locations.values()):
            if i.unlocked:
                unlocked_locations.append(i.name)
        completed_challenges_str = ';'.join(completed_challenges)
        unlocked_disguises_str = ';'.join(unlocked_disguises)
        unlocked_locations_str = ';'.join(unlocked_locations)
        adapter.update_by_id("users", f'{users[user_id].mission}_completed_challenges={completed_challenges_str}', user_id)
        adapter.update_by_id("users", f'{users[user_id].mission}_unlocked_disguises={unlocked_disguises_str}', user_id)
        adapter.update_by_id("users", f'{users[user_id].mission}_unlocked_locations={unlocked_locations_str}', user_id)
        adapter.update_by_id("users", f'player_lvl={users[user_id].player_lvl}', user_id)
        users[user_id] = create_user(user_id=user_id)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите место назначения', reply_markup=(start_keyboard()))
    
def begin(update: Update, context: CallbackContext):
    """Начало игры"""
    user_id = update.callback_query.from_user['id']
    query = update.callback_query
    query.answer()
    if query.data == 'ХоккЯП':
        users[user_id].change_mission('hokkaido')
        query.edit_message_text(text='*_Транспозиция органов\n\nХоккайдо, Япония_*', reply_markup=choose_equipment_keyboard(update=update, context=context), parse_mode='MarkdownV2')
    elif query.data == 'СТ':
        query.edit_message_text(text='*_Свободная тренировка\n\nКомплекс МКА, ЗАСЕКРЕЧЕНО_*', reply_markup=start_tutorial_keyboard_2(), parse_mode='MarkdownV2')
    elif query.data == 'ТПН':
        query.edit_message_text(text='*_Тренировка под наблюдением\n\nКомплекс МКА, ЗАСЕКРЕЧЕНО_*', reply_markup=start_tutorial_keyboard_1(), parse_mode='MarkdownV2')

def run_bot():
    """Работа бота"""
    updater = Updater(tg_token)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('support', support))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('stats', stats))
    dispatcher.add_handler(CommandHandler('new_game', new_game))

    dispatcher.add_handler(CallbackQueryHandler(begin, pattern=is_begin))
    dispatcher.add_handler(CallbackQueryHandler(choose_action_menu, pattern='Выбор действия'))
    dispatcher.add_handler(CallbackQueryHandler(challenges_menu, pattern='Испытания'))
    dispatcher.add_handler(CallbackQueryHandler(status_menu, pattern='Статус'))
    dispatcher.add_handler(CallbackQueryHandler(choose_start_location_menu, pattern='Выбор начальной локации'))
    dispatcher.add_handler(CallbackQueryHandler(choose_pistol_menu, pattern='Выбор пистолета'))
    dispatcher.add_handler(CallbackQueryHandler(choose_start_item_menu_1, pattern='Выбор снаряжения 1'))
    dispatcher.add_handler(CallbackQueryHandler(choose_start_item_menu_2, pattern='Выбор снаряжения 2'))
    dispatcher.add_handler(CallbackQueryHandler(spawn_player, pattern=is_spawn_player))
    dispatcher.add_handler(CallbackQueryHandler(safe_move, pattern=is_safe_move))
    dispatcher.add_handler(CallbackQueryHandler(move, pattern=is_basic_move))
    dispatcher.add_handler(CallbackQueryHandler(move_menu, pattern='Передвижение'))
    dispatcher.add_handler(CallbackQueryHandler(attack_menu, pattern='Выбор нападения'))
    dispatcher.add_handler(CallbackQueryHandler(attack_npc, pattern=is_npc_attack))
    dispatcher.add_handler(CallbackQueryHandler(hide_menu, pattern='Напасть или бежать'))
    dispatcher.add_handler(CallbackQueryHandler(hide, pattern='Скрыться'))
    dispatcher.add_handler(CallbackQueryHandler(no_disguise_move_menu, pattern='Перемещение без маскировки'))
    dispatcher.add_handler(CallbackQueryHandler(no_disguise_move, pattern=is_no_disguise_move))
    dispatcher.add_handler(CallbackQueryHandler(loot_menu, pattern='Обыскать локацию'))
    dispatcher.add_handler(CallbackQueryHandler(inventory_menu, pattern='Инвентарь'))
    dispatcher.add_handler(CallbackQueryHandler(disguise_menu, pattern=is_disguise_menu))
    dispatcher.add_handler(CallbackQueryHandler(change_disguise, pattern=is_change_disguise))
    dispatcher.add_handler(CallbackQueryHandler(remove_item, pattern='Убрать предмет из рук'))
    dispatcher.add_handler(CallbackQueryHandler(choose_legal_item, pattern=is_choose_legal_item))
    dispatcher.add_handler(CallbackQueryHandler(choose_illegal_item_menu, pattern=is_choose_illegal_item))
    dispatcher.add_handler(CallbackQueryHandler(choose_illegal_item, pattern='ВНО'))
    dispatcher.add_handler(CallbackQueryHandler(combat_start_menu, pattern='Бой'))
    dispatcher.add_handler(CallbackQueryHandler(hide_combat, pattern='Прятаться'))
    dispatcher.add_handler(CallbackQueryHandler(combat, pattern='Напасть'))
    dispatcher.add_handler(CallbackQueryHandler(choose_weapon_menu, pattern='Выбор оружия'))
    dispatcher.add_handler(CallbackQueryHandler(choose_weapon_action_menu, pattern=is_choose_weapon))
    dispatcher.add_handler(CallbackQueryHandler(combat_chance, pattern=is_choose_weapon_action))
    dispatcher.add_handler(CallbackQueryHandler(interact_menu, pattern='Взаимодействие'))
    dispatcher.add_handler(CallbackQueryHandler(kill_menu, pattern=is_interact_lethal))
    dispatcher.add_handler(CallbackQueryHandler(knock_out_menu, pattern=is_interact_non_lethal))
    dispatcher.add_handler(CallbackQueryHandler(confirm_kill_menu, pattern=is_kill))
    dispatcher.add_handler(CallbackQueryHandler(confirm_knock_menu, pattern=is_knock_out))
    dispatcher.add_handler(CallbackQueryHandler(kill, pattern=is_confirm_kill))
    dispatcher.add_handler(CallbackQueryHandler(knock_out, pattern=is_confirm_knock))
    dispatcher.add_handler(CallbackQueryHandler(safe_move_menu, pattern='safe_move'))
    dispatcher.add_handler(CallbackQueryHandler(safe_move, pattern=is_safe_move))
    dispatcher.add_handler(CallbackQueryHandler(distract_menu, pattern=is_distract))
    dispatcher.add_handler(CallbackQueryHandler(confirm_distract_menu, pattern=is_distract_npc))
    dispatcher.add_handler(CallbackQueryHandler(distract_kill, pattern=is_confirm_distract_kill))
    dispatcher.add_handler(CallbackQueryHandler(distract_knock_out, pattern=is_confirm_distract_knock))
    dispatcher.add_handler(CallbackQueryHandler(destroy_heart_menu_2, pattern=is_destroy_heart_2))
    dispatcher.add_handler(CallbackQueryHandler(destroy_heart, pattern=is_destroy_heart))
    dispatcher.add_handler(CallbackQueryHandler(rating, pattern='Завершить миссию'))
    dispatcher.add_handler(CallbackQueryHandler(destroy_servers, pattern='Повредить серверы'))
    dispatcher.add_handler(CallbackQueryHandler(sauna_kill_1, pattern='УТВ'))
    dispatcher.add_handler(CallbackQueryHandler(sauna_kill_2, pattern='ЗДП'))
    dispatcher.add_handler(CallbackQueryHandler(robot_kill_1, pattern='Взять управление'))
    dispatcher.add_handler(CallbackQueryHandler(robot_kill_2, pattern='УЭС'))
    dispatcher.add_handler(CallbackQueryHandler(surgeon_knock_out_1, pattern='ПКП'))
    dispatcher.add_handler(CallbackQueryHandler(surgeon_knock_out_2, pattern=is_surgeon_knock_out_2))
    dispatcher.add_handler(CallbackQueryHandler(yoga_kill_1, pattern='Начать тренировку'))
    dispatcher.add_handler(CallbackQueryHandler(yoga_kill_2, pattern=is_yoga_kill_2))
    dispatcher.add_handler(CallbackQueryHandler(use, pattern=is_use))
    dispatcher.add_handler(CallbackQueryHandler(save_and_quit_confirm_menu, pattern='Сохранить и выйти'))
    dispatcher.add_handler(CallbackQueryHandler(save_and_quit, pattern='Конец игры'))
    dispatcher.add_handler(CallbackQueryHandler(sushi_kill_1, pattern='ОР'))
    dispatcher.add_handler(CallbackQueryHandler(sushi_kill_2, pattern=is_sushi_kill_2))
    dispatcher.add_handler(CallbackQueryHandler(sushi_kill_3, pattern='Пойти за целью'))
    dispatcher.add_handler(CallbackQueryHandler(sushi_kill_4, pattern='Утопить цель'))
    dispatcher.add_handler(CallbackQueryHandler(cigar_kill_1, pattern='ПНПС'))
    dispatcher.add_handler(CallbackQueryHandler(cigar_kill_2, pattern='ПНБ'))
    dispatcher.add_handler(CallbackQueryHandler(cigar_kill_3, pattern='СУГ'))
    dispatcher.add_handler(CallbackQueryHandler(cigar_kill_4, pattern='УСБ'))
    dispatcher.add_handler(CallbackQueryHandler(hokkaido_briefing_1, pattern='hokkaido_briefing_1'))
    dispatcher.add_handler(CallbackQueryHandler(hokkaido_briefing_2, pattern='hokkaido_briefing_2'))
    dispatcher.add_handler(CallbackQueryHandler(hokkaido_briefing_3, pattern='hokkaido_briefing_3'))
    dispatcher.add_handler(CallbackQueryHandler(hokkaido_briefing_4, pattern='hokkaido_briefing_4'))
    dispatcher.add_handler(CallbackQueryHandler(hokkaido_briefing_5, pattern='hokkaido_briefing_5'))
    dispatcher.add_handler(CallbackQueryHandler(hokkaido_briefing_6, pattern='hokkaido_briefing_6'))
    dispatcher.add_handler(CallbackQueryHandler(choose_equipment_menu, pattern=is_choose_equipment))
    dispatcher.add_handler(CallbackQueryHandler(knock_jason_portman_1, pattern='ВДП'))
    dispatcher.add_handler(CallbackQueryHandler(knock_jason_portman_2, pattern=is_knock_jason_portman))
    dispatcher.add_handler(CallbackQueryHandler(medical_checkup, pattern='ПЗВ'))
    dispatcher.add_handler(CallbackQueryHandler(stem_cells, pattern='PSC'))
    dispatcher.add_handler(CallbackQueryHandler(assasinations_menu, pattern='Убийства'))
    dispatcher.add_handler(CallbackQueryHandler(feats_menu, pattern='Усложнения'))
    dispatcher.add_handler(CallbackQueryHandler(discovery_menu, pattern='Исследование'))
    dispatcher.add_handler(CallbackQueryHandler(classics_menu, pattern='Классика'))
    dispatcher.add_handler(CallbackQueryHandler(cigar_kill_5, pattern='ПЮЯ'))
    dispatcher.add_handler(CallbackQueryHandler(cigar_kill_6, pattern='ТЮЯС'))
    dispatcher.add_handler(CallbackQueryHandler(choose_tutorial_menu, pattern='МКАЗАС'))
    dispatcher.add_handler(CallbackQueryHandler(ica_briefing_1, pattern='ica_briefing_1'))
    dispatcher.add_handler(CallbackQueryHandler(ica_briefing_2, pattern='ica_briefing_2'))
    dispatcher.add_handler(CallbackQueryHandler(reject_turorial, pattern='Отмена обучения'))
    dispatcher.add_handler(CallbackQueryHandler(lifeboat_kill_1, pattern='СБШР'))
    dispatcher.add_handler(CallbackQueryHandler(private_meeting_1, pattern='ПВОР'))
    dispatcher.add_handler(CallbackQueryHandler(private_meeting_2, pattern=is_private_meeting_kill))
    dispatcher.add_handler(CallbackQueryHandler(drink_kill_1, pattern='ОНАП'))
    dispatcher.add_handler(CallbackQueryHandler(drink_kill_2, pattern='Пойти за Кэлвином'))
    dispatcher.add_handler(CallbackQueryHandler(drink_kill_3, pattern='Утопить Кэлвина'))
    dispatcher.add_handler(CallbackQueryHandler(skip_choose_action_menu, pattern=is_skip))

    updater.start_polling()
    updater.idle()

run_bot()
