import os
import random
import time as tm

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackQueryHandler, CallbackContext, CommandHandler

from dotenv import load_dotenv
load_dotenv()

from model.hokkaido_values import *
from model.player.player_info import *


adapter = HitmanAdapter()
tg_token = os.getenv("TELEGRAM_TOKEN")

def create_user(player_lvl: int, completed_challenges: str, unlocked_disguises: str, unlocked_locations: str):
    """Создание объекта класса информации о пользователе"""
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
    return PlayerInfo(challenges=user_challenges, npcs=user_npcs, targets=user_targets, events=user_events, locations=user_locations, carry_on_items=['Удавка', 'Смертельный яд', 'Рвотный яд', 'Дешифровщик', 'Боевой нож', 'Монета'], player_lvl=player_lvl, completed_challenges=completed_challenges, unlocked_disguises=unlocked_disguises, unlocked_locations=unlocked_locations, items=user_items, disguises=user_disguises, player=Player(), loadout={'Начальная локация': None, 'Пистолет': None, 'Снаряжение 1': None, 'Снаряжение 2': None})

users = {i[0]: create_user(player_lvl=i[5], completed_challenges=i[6], unlocked_disguises=i[7], unlocked_locations=i[8]) for i in adapter.get_all('Users')}

#Начало создания ТГ бота
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def telegram_bot():
    """Запуск ТГ бота"""

    #Часто используемые функции

    def location_status(update: Update, context: CallbackContext, location: Location) -> str:
        """Вывод статуса локации"""
        user_id = update.callback_query.from_user['id']
        query = update.callback_query
        query.answer()
        result_string = f'{location.name}\n'
        location_npcs = find_location_npcs(update=update, context=context, location=location)
        location_disguises = []
        for i in location_npcs:
            location_disguises.append(i.disguise.name)
        if location_witnesses(update=update, context=context, location=location) > 0:
            result_string += '\nНа локации находятся:\n'
            for i in list(users[user_id].targets.values()):
                if i.move(users[user_id].time) == location.name:
                    result_string += f'\n{i.name}\n'
            if location.witnesses > 0:
                result_string += f'\n{location.witnesses} Пациент'
            for i in list(users[user_id].disguises.values()):
                if i.name in location_disguises:
                    result_string += f'\n{location_disguises.count(i.name)} {i.name}'
            if users[user_id].targets['Yuki Yamazaki'].alive == False and users[user_id].targets['Erich Soders'].alive == False and users[user_id].events['Все цели убиты'].completed == False:
                users[user_id].events['Все цели убиты'].completed = True
                result_string = 'Все цели убиты. Найдте выход с миссии.\n\n\n' + result_string
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

    #Меню в игре

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
        result_string += '\n\n\n\n' + location_status(update=update, context=context, location=users[user_id].player.current_location)
        query = update.callback_query
        query.answer()
        query.edit_message_text(text=result_string, reply_markup=(status_keyboard()))

    def challenges_menu(update: Update, context: CallbackContext):
        user_id = update.callback_query.from_user['id']
        query = update.callback_query
        text = ''
        completed_challenges = []
        for i in list(users[user_id].challenges.values()):
            if i.completed == False:
                text += i.name + '\n' + i.description + '\n\n'
            else:
                completed_challenges.append(i.name + ' (выполнено)')
        for i in completed_challenges:
            text += i + '\n\n'
        text = text[:-1]
        query.answer()
        query.edit_message_text(text='Испытания', reply_markup=challenges_keyboard())

    def assasinations_menu(update: Update, context: CallbackContext):
        user_id = update.callback_query.from_user['id']
        query = update.callback_query
        text = ''
        completed_challenges = []
        for i in list(users[user_id].challenges.values()):
            if i.type == 'Убийство':
                if i.completed == False:
                    text += i.name + '\n' + i.description + '\n\n'
                else:
                    completed_challenges.append(i.name + ' (выполнено)')
        for i in completed_challenges:
            text += i + '\n\n'
        text = text[:-1]
        query.answer()
        query.edit_message_text(text=text, reply_markup=challenges_section_keyboard())

    def feats_menu(update: Update, context: CallbackContext):
        user_id = update.callback_query.from_user['id']
        query = update.callback_query
        text = ''
        completed_challenges = []
        for i in list(users[user_id].challenges.values()):
            if i.type == 'Усложнение':
                if i.completed == False:
                    text += i.name + '\n' + i.description + '\n\n'
                else:
                    completed_challenges.append(i.name + ' (выполнено)')
        for i in completed_challenges:
            text += i + '\n\n'
        text = text[:-1]
        query.answer()
        query.edit_message_text(text=text, reply_markup=challenges_section_keyboard())

    def discovery_menu(update: Update, context: CallbackContext):
        user_id = update.callback_query.from_user['id']
        query = update.callback_query
        text = ''
        completed_challenges = []
        for i in list(users[user_id].challenges.values()):
            if i.type == 'Исследование':
                if i.completed == False:
                    text += i.name + '\n' + i.description + '\n\n'
                else:
                    completed_challenges.append(i.name + ' (выполнено)')
        for i in completed_challenges:
            text += i + '\n\n'
        text = text[:-1]
        query.answer()
        query.edit_message_text(text=text, reply_markup=challenges_section_keyboard())

    def classics_menu(update: Update, context: CallbackContext):
        user_id = update.callback_query.from_user['id']
        query = update.callback_query
        text = ''
        completed_challenges = []
        for i in list(users[user_id].challenges.values()):
            if i.type == 'Классика':
                if i.completed == False:
                    text += i.name + '\n' + i.description + '\n\n'
                else:
                    completed_challenges.append(i.name + ' (выполнено)')
        for i in completed_challenges:
            text += i + '\n\n'
        text = text[:-1]
        query.answer()
        query.edit_message_text(text=text, reply_markup=challenges_section_keyboard())
        
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
        for i in list(lvl_unlocks.values()):
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
        user_id = update.callback_query.from_user['id']
        users[user_id].time += 5
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='Выберите локацию', reply_markup=(move_keyboard(update=update, context=context)))

    def attack_menu(update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='Выберите действие', reply_markup=(attack_keyboard()))

    def hide_menu(update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='Выберите действие', reply_markup=(hide_keyboard()))

    def no_disguise_move_menu(update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='У вас нет подходящей маскировки. Переместиться на локацию?', reply_markup=(no_disguise_move_keyboard()))

    def loot_menu(update: Update, context: CallbackContext):
        user_id = update.callback_query.from_user['id']
        users[user_id].time += 10
        query = update.callback_query
        query.answer()
        users[user_id].player.inventory += users[user_id].player.current_location.items
        result_string = 'Найдены предметы:\n\n'
        if users[user_id].player.current_location.items == []:
            query.edit_message_text(text='На локации нет предметов', reply_markup=(choose_action_keyboard(update=update, context=context)))
        else:
            for i in list(users[user_id].items.values()):
                if i in users[user_id].player.current_location.items:
                    result_string += f'{i.name} ({users[user_id].player.current_location.items.count(i)})\n'
            if users[user_id].items['Пачка сигарет'] in users[user_id].player.inventory and users[user_id].events['Информация о сигаретах 1'].completed == False:
                users[user_id].events['Информация о сигаретах 1'].completed = True
                query.edit_message_text(text='Диана: Это пачка сигарет. Не территории клиники «Гама» курение строго запрещено, так что эти сигареты — явная контрабанда.')
                if users[user_id].challenges['Дайте ещё одну'].completed == False:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Дайте ещё одну'].achieved(update=update, context=context))
                    users[user_id].player_lvl += users[user_id].challenges['Дайте ещё одну'].xp
                context.bot.send_message(chat_id=update.effective_chat.id, text=result_string, reply_markup=(choose_action_keyboard(update=update, context=context)))
            elif users[user_id].items['Пульт от нейрочипа'] in users[user_id].player.inventory and users[user_id].events['Информация о чипе'].completed == False:
                users[user_id].events['Информация о чипе'].completed = True
                query.edit_message_text(text='Диана: Нейрочип для изменения настроения. Интересно...\n\nДоктор Каташи Ито, он же Куратор, проводит сейчас какое-то медицинское испытание. Занимательно.\n\nХранилище органов находится в ведении Куратора, а значит, у него точно есть доступ к сердцу, которое должны пересадить Содерсу. 47-й, я рекомендую найти отчёт сотрудника и выяснить, для чего нужен этот нейроимплантат. Может пригодиться.')
                if users[user_id].challenges['Изменение настроения'].completed == False:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Изменение настроения'].achieved(update=update, context=context))
                    users[user_id].player_lvl += users[user_id].challenges['Изменение настроения'].xp
                context.bot.send_message(chat_id=update.effective_chat.id, text=result_string, reply_markup=(choose_action_keyboard(update=update, context=context)))
            elif users[user_id].items['Стволовые клетки'] in users[user_id].player.inventory and users[user_id].events['Стволовые клетки'].completed == False:
                users[user_id].events['Стволовые клетки'].completed = True
                query.edit_message_text(text='Контейнер, заполненный заражёнными и ядовитыми стволовыми клетками. Попадание таких клеток в кровь крайне опасно для здоровья.')
                context.bot.send_message(chat_id=update.effective_chat.id, text=result_string, reply_markup=(choose_action_keyboard(update=update, context=context)))
            elif users[user_id].items['Яд рыбы Фугу'] in users[user_id].player.inventory and users[user_id].challenges['Запахло рыбой'].completed == False:
                query.edit_message_text(text=users[user_id].challenges['Запахло рыбой'].achieved(update=update, context=context))
                users[user_id].player_lvl += users[user_id].challenges['Запахло рыбой'].xp
                context.bot.send_message(chat_id=update.effective_chat.id, text=result_string, reply_markup=(choose_action_keyboard(update=update, context=context)))
            else:
                query.edit_message_text(text=result_string, reply_markup=(choose_action_keyboard(update=update, context=context)))
        users[user_id].player.current_location.items = []

    def inventory_menu(update: Update, context: CallbackContext):
        user_id = update.callback_query.from_user['id']
        query = update.callback_query
        result_string = f'Сейчас в руках: {users[user_id].player.item.name}'
        if users[user_id].player.inventory == []:
            result_string += '\n\nУ вас нет предметов'
        query.answer()
        query.edit_message_text(text=result_string, reply_markup=(inventory_keyboard(update=update, context=context)))

    def disguise_menu(update: Update, context: CallbackContext):
        user_id = update.callback_query.from_user['id']
        query = update.callback_query
        query.answer()
        query.edit_message_text(text=f'Текущая маскировка: {users[user_id].player.disguise.name}', reply_markup=(disguise_keyboard(update=update, context=context)))

    def choose_illegal_item_menu(update: Update, context: CallbackContext):
        user_id = update.callback_query.from_user['id']
        query = update.callback_query
        query.answer()
        if users[user_id].player.disguise.name != 'Охранник' and users[user_id].player.disguise.name != 'Телохранитель':
            users[user_id].illegal_item = query[:-4]
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
        users[user_id].time += 10
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
        query.edit_message_text(text='ВНИМАНИЕ: При выходе будут сохранены ваш текущий уровень и выполненные испытания, но не текущее продвижение по миссии.\n\nВы уверены, что хотите завершить игру?', reply_markup=(save_and_quit_confirm_keyboard()))

    def choose_equipment_menu(update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='Транспозиция органов\n\nХоккайдо, Япония', reply_markup=(choose_equipment_keyboard(update=update, context=context)))

    #Клавиатуры для меню

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
                    [InlineKeyboardButton('Брифинг', callback_data="briefing_1")],
                    [InlineKeyboardButton(options[0], callback_data="Выбор начальной локации"), InlineKeyboardButton(options[1], callback_data="Выбор пистолета")],
                    [InlineKeyboardButton(options[2], callback_data="Выбор снаряжения 1"), InlineKeyboardButton(options[3], callback_data="Выбор снаряжения 2")],
                    [InlineKeyboardButton('Начать миссию', callback_data="Начало игры")]
                ])
        return InlineKeyboardMarkup([
                    [InlineKeyboardButton('Брифинг', callback_data="briefing_1")],
                    [InlineKeyboardButton(options[0], callback_data="Выбор начальной локации")]
                    [InlineKeyboardButton('Начать миссию', callback_data="Начало игры")]
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
        if users[user_id].disguises['Охранник'] in users[user_id].player.found_disguises or users[user_id].disguises['Телохранитель'] in users[user_id].player.found_disguises:
            users[user_id].player.inventory.append(users[user_id].items['Bartoli 75R'])
        unlocked_disguises = 0
        for i in list(users[user_id].disguises.values()):
            if i.unlocked:
                unlocked_disguises += 1
        unlocked_locations = 0
        for i in list(users[user_id].locations.values()):
            if i.unlocked:
                unlocked_locations += 1
        if users[user_id].challenges['Хамелеон'].completed == False and unlocked_disguises == len(disguises):
            context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Хамелеон'].achieved(update=update, context=context))
            users[user_id].player_lvl += users[user_id].challenges['Хамелеон'].xp
        if users[user_id].challenges['Исследуйте Хоккайдо'].completed == False and unlocked_locations == len(locations):
            context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Исследуйте Хоккайдо'].achieved(update=update, context=context))
            users[user_id].player_lvl += users[user_id].challenges['Исследуйте Хоккайдо'].xp
        if users[user_id].events['Убийство в сауне'].completed == False and users[user_id].player.current_location.name == 'Водоснабжение спа':
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите действие', reply_markup=sauna_kill_keyboard_1())
        elif users[user_id].events['Все цели убиты'].completed == True and (users[user_id].player.current_location.name == 'Канатная дорога' or users[user_id].player.current_location.name == 'Гараж' or users[user_id].player.current_location.name == 'Вертолетная площадка' or users[user_id].player.current_location.name == 'Горная тропа'):
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите действие', reply_markup=(exit_mission_keyboard()))
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
    
    def challenges_keyboard():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Убийства", callback_data='Убийства'), InlineKeyboardButton("Усложнения", callback_data='Усложнения')],
            [InlineKeyboardButton("Исследование", callback_data='Исследование'), InlineKeyboardButton("Классика", callback_data='Классика')],
            [InlineKeyboardButton("Выйти", callback_data='Выбор действия')]
            ])
    
    def challenges_section_keyboard():
        return InlineKeyboardMarkup([[InlineKeyboardButton("Назад", callback_data='Испытания')]])
    
    def choose_start_location_keyboard(update: Update, context: CallbackContext):
        user_id = update.callback_query.from_user['id']
        options = []
        for i in range(1, 10):
            if i <= users[user_id].player_lvl // 6:
                options.append(lvl_unlocks[i][0])
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
        keyboard = []
        for i in range(len(location_npcs)):
            keyboard.append([InlineKeyboardButton(f"{location_disguises[i]}", callback_data=location_npcs[i] + 'KILL')])
        keyboard.append([InlineKeyboardButton(f"Отменить действие", callback_data=f"Взаимодействие")])
        return InlineKeyboardMarkup(keyboard)

    def knock_out_keyboard(update: Update, context: CallbackContext):
        user_id = update.callback_query.from_user['id']
        location_npcs = []
        location_disguises = []
        for i in find_location_npcs(update=update, context=context, location=users[user_id].player.current_location):
            location_disguises.append(i.disguise.name)
            location_npcs.append(i.name)
        keyboard = []
        for i in range(len(location_npcs)):
            keyboard.append([InlineKeyboardButton(f"{location_disguises[i]}", callback_data=location_npcs[i] + 'KNOCK')])
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

    def exit_mission_keyboard():
        return InlineKeyboardMarkup([[InlineKeyboardButton('Завершить миссию', callback_data='Завершить миссию'), InlineKeyboardButton('Назад', callback_data='Выбор действия')]])
    
    def destroy_servers_keyboard():
        return InlineKeyboardMarkup([[InlineKeyboardButton('Повредить серверы', callback_data='Повредить серверы'), InlineKeyboardButton('Назад', callback_data='Выбор действия')]])

    def sauna_kill_keyboard_1():
        return InlineKeyboardMarkup([[InlineKeyboardButton('Увеличить температуру воды', callback_data='УТВ')], [InlineKeyboardButton('Назад', callback_data='Выбор действия')]])
    
    def sauna_kill_keyboard_2():
        return InlineKeyboardMarkup([[InlineKeyboardButton('Запереть дверь в парилку', callback_data='ЗДП')], [InlineKeyboardButton('Назад', callback_data='Выбор действия')]])

    def robot_kill_keyboard_1():
        return InlineKeyboardMarkup([[InlineKeyboardButton('Взять управление', callback_data='Взять управление'), InlineKeyboardButton('Назад', callback_data='Выбор действия')]])
    
    def robot_kill_keyboard_2():
        return InlineKeyboardMarkup([[InlineKeyboardButton('Убить Эриха Содерса', callback_data='УЭС')], [InlineKeyboardButton('Назад', callback_data='Выбор действия')]])
    
    def surgeon_knock_out_keyboard_1():
        return InlineKeyboardMarkup([[InlineKeyboardButton('Пойти в комнату пилота', callback_data='ПКП')], [InlineKeyboardButton('Уйти', callback_data='Выбор действия')]])
    
    def surgeon_knock_out_keyboard_2():
        return InlineKeyboardMarkup([[InlineKeyboardButton('Усмирить главного хирурга', callback_data='УГХ')], [InlineKeyboardButton('Убить главного хирурга', callback_data='УГХсм')], [InlineKeyboardButton('Уйти', callback_data='Выбор действия')]])

    def yoga_kill_keyboard_1():
        return InlineKeyboardMarkup([[InlineKeyboardButton('Начать тренировку', callback_data='Начать тренировку')], [InlineKeyboardButton('Уйти', callback_data='Выбор действия')]])
    
    def yoga_kill_keyboard_2():
        return InlineKeyboardMarkup([[InlineKeyboardButton('Толкнуть Юки Ямадзаки', callback_data='ТЮЯ')], [InlineKeyboardButton('Завершить тренировку', callback_data='Выбор действия')]])
    
    def sushi_kill_keyboard_1(update: Update, context: CallbackContext):
        user_id = update.callback_query.from_user['id']
        if users[user_id].player.disguise.name == 'Шеф':
            return InlineKeyboardMarkup([[InlineKeyboardButton('Отравить роллы', callback_data='ОР')], [InlineKeyboardButton('Назад', callback_data='Выбор действия')]])
        else:
            return InlineKeyboardMarkup([[InlineKeyboardButton('Отравить роллы (3/10)', callback_data='ОР')], [InlineKeyboardButton('Назад', callback_data='Выбор действия')]])
    
    def sushi_kill_keyboard_2(update: Update, context: CallbackContext):
        user_id = update.callback_query.from_user['id']
        poisons = [users[user_id].items['Яд рыбы Фугу'], users[user_id].items['Крысиный яд'], users[user_id].items['Смертельный яд'], users[user_id].items['Рвотный яд']]
        gained_poisons = []
        for i in poisons:
            if i in users[user_id].player.inventory:
                gained_poisons.append(i.name)
        keyboard = make_keyboard(gained_poisons, 'ОСЮ')
        keyboard.append([InlineKeyboardButton('Назад', callback_data='Выбор действия')])
        return InlineKeyboardMarkup(keyboard)
    
    def sushi_kill_keyboard_3():
        return InlineKeyboardMarkup([[InlineKeyboardButton('Пойти за целью', callback_data='Пойти за целью')], [InlineKeyboardButton('Остаться', callback_data='Выбор действия')]])
    
    def sushi_kill_keyboard_4():
        return InlineKeyboardMarkup([[InlineKeyboardButton('Утопить цель', callback_data='Утопить цель')], [InlineKeyboardButton('Уйти', callback_data='Выбор действия')]])
    
    def cigar_kill_keyboard_1():
        return InlineKeyboardMarkup([[InlineKeyboardButton('Положить новую пачку', callback_data='ПНПС')], [InlineKeyboardButton('Назад', callback_data='Выбор действия')]])
    
    def cigar_kill_keyboard_2():
        return InlineKeyboardMarkup([[InlineKeyboardButton('Пойти на балкон', callback_data='ПНБ')], [InlineKeyboardButton('Назад', callback_data='Выбор действия')]])
    
    def cigar_kill_keyboard_3():
        return InlineKeyboardMarkup([[InlineKeyboardButton('Создать утечку газа', callback_data='СУГ')], [InlineKeyboardButton('Подождать Юки Ямадзаки', callback_data='ПЮЯ')], [InlineKeyboardButton('Уйти с балкона', callback_data='Выбор действия')]])
    
    def cigar_kill_keyboard_4():
        return InlineKeyboardMarkup([[InlineKeyboardButton('Уйти с балкона', callback_data='УСБ')]])
    
    def cigar_kill_keyboard_5():
        return InlineKeyboardMarkup([[InlineKeyboardButton('Толкнуть Юки Ямадзаки', callback_data='ТЮЯС')], [InlineKeyboardButton('Уйти с балкона', callback_data='Выбор действия')]])

    def briefing_keyboard_1(update: Update, context: CallbackContext):
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('hitman_tg_bot/assets/hokkaido.png', 'rb'), timeout=1000)
        return InlineKeyboardMarkup([[InlineKeyboardButton('Далее', callback_data='briefing_2')]])
    
    def briefing_keyboard_2(update: Update, context: CallbackContext):
        context.bot.send_photo(chat_id=update.effective_chat.id, photo='https://static.wikia.nocookie.net/hitman/images/2/2d/H2018-Erich-Soders-Intel-Card.png/revision/latest?cb=20220601174305')
        return InlineKeyboardMarkup([[InlineKeyboardButton('Далее', callback_data='briefing_3')]])
    
    def briefing_keyboard_3(update: Update, context: CallbackContext):
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('hitman_tg_bot/assets/equipment.png', 'rb'), timeout=1000)
        return InlineKeyboardMarkup([[InlineKeyboardButton('Далее', callback_data='briefing_4')]])
    
    def briefing_keyboard_4(update: Update, context: CallbackContext):
        context.bot.send_photo(chat_id=update.effective_chat.id, photo='https://static.wikia.nocookie.net/hitman/images/a/a8/H2018-Yuki-Yamazaki-Intel-Card.png/revision/latest?cb=20220601174346')
        return InlineKeyboardMarkup([[InlineKeyboardButton('Далее', callback_data='briefing_5')]])
    
    def briefing_keyboard_5(update: Update, context: CallbackContext):
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('hitman_tg_bot/assets/erich_yuki.png', 'rb'), timeout=1000)
        return InlineKeyboardMarkup([[InlineKeyboardButton('Далее', callback_data='briefing_6')]])
    
    def briefing_keyboard_6(update: Update, context: CallbackContext):
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('hitman_tg_bot/assets/clock.png', 'rb'), timeout=1000)
        return InlineKeyboardMarkup([[InlineKeyboardButton('Подготовка к миссии', callback_data='Выбор снаряжения')]])
    
    def start_keyboard():
        return InlineKeyboardMarkup([[InlineKeyboardButton('Управление', callback_data='help')], [InlineKeyboardButton('Начать игру', callback_data='begin')]])
    
    def knock_jason_portman_keyboard_1():
        return InlineKeyboardMarkup([[InlineKeyboardButton('Пойти в укромное место', callback_data='ВДП')], [InlineKeyboardButton('Уйти', callback_data='Выбор действия')]])
    
    def knock_jason_portman_keyboard_2():
        return InlineKeyboardMarkup([[InlineKeyboardButton('Усмирить Джейсона Портмана', callback_data='УДП')], [InlineKeyboardButton('Убить Джейсона Портмана', callback_data='УДПсм')], [InlineKeyboardButton('Уйти', callback_data='Выбор действия')]])
    
    def medical_checkup_keyboard():
        return InlineKeyboardMarkup([[InlineKeyboardButton('Проследовать за врачом', callback_data='ПЗВ')], [InlineKeyboardButton('Уйти', callback_data='Выбор действия')]])

    #Проверка query для меню

    def is_knock_jason_portman(query):
        return 'УДП' in query

    def is_choose_equipment(query):
        return 'choose_pistol' in query or 'choose_item_1' in query or 'choose_item_2' in query or 'CSL' in query or query == 'Выбор снаряжения'

    def is_basic_move(query):
        return 'basic_move' in query

    def is_safe_move(query):
        return 'SM' in query
    
    def is_npc_attack(query):
        return "НПД" in query

    def is_no_disguise_move(query):
        return 'ПРТ' in query

    def is_disguise_menu(query):
        return 'МАСК' in query

    def is_change_disguise(query):
        return 'МСК' in query

    def is_choose_legal_item(query):
        if query[:-4] in list(items.keys()):
            return items[query[:-4]].legal
        return False
    
    def is_choose_illegal_item(query):
        if query[:-4] in list(items.keys()):
            if items[query[:-4]].legal == False:
                return True
        return False
    
    def is_choose_weapon(query):
        return 'WP' in query
    
    def is_choose_weapon_action(query):
        return 'CWA' in query

    def is_interact_lethal(query):
        return 'ITR' in query and ('летально' in query or 'Выстрелить' in query or 'Задушить' in query)
    
    def is_interact_non_lethal(query):
        return 'ITR' in query and ('летально' in query or 'Выстрелить' in query or 'Задушить' in query or 'Использовать' in query or 'Бросить для отвлечения' in query) == False
    
    def is_distract(query):
        return 'Бросить для отвлечения' in query
    
    def is_kill(query):
        return 'KILL' in query
    
    def is_knock_out(query):
        return 'KNOCK' in query
    
    def is_distract_npc(query):
        return 'DIS' in query

    def is_confirm_kill(query):
        return 'con_kill' in query
    
    def is_confirm_knock(query):
        return 'con_knock' in query
    
    def is_confirm_distract_kill(query):
        return 'CDKL' in query
    
    def is_confirm_distract_knock(query):
        return 'CDKN' in query

    def is_use(query):
        return 'Использовать' in query
    
    def is_destroy_heart_2(query):
        return 'DH1' in query
    
    def is_destroy_heart(query):
        return 'DH2' in query

    def is_yoga_kill_2(query):
        return query == 'ТЮЯ'
    
    def is_surgeon_knock_out_2(query):
        return 'УГХ' in query

    def is_sushi_kill_2(query):
        return 'ОСЮ' in query

    #Сюжетные скрипты

    def stem_cells(update: Update, context: CallbackContext):
        user_id = update.callback_query.from_user['id']
        users[user_id].events['Отравить стволовые клетки'].completed = True
        users[user_id].player.inventory.remove(users[user_id].items['Стволовые клетки'])
        query = update.callback_query
        query.answer()
        if users[user_id].targets['Erich Soders'].alive:
            if users[user_id].challenges['Поцелуй смерти'].completed == False:
                query.edit_message_text(text=users[user_id].challenges['Поцелуй смерти'].achieved(update=update, context=context))
                users[user_id].player_lvl += users[user_id].challenges['Поцелуй смерти'].xp
                if users[user_id].challenges['Так можно и пораниться'].completed == False:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Так можно и пораниться'].achieved(update=update, context=context))
                    users[user_id].player_lvl += users[user_id].challenges['Так можно и пораниться'].xp
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
            query.edit_message_text(text=users[user_id].player.current_location.unlock(update=update, context=context))
            edit = False
        if users[user_id].challenges['Смена внешности'].completed == False:
            users[user_id].player_lvl += users[user_id].challenges['Смена внешности'].xp
            if edit:
                query.edit_message_text(text=users[user_id].challenges['Смена внешности'].achieved(update=update, context=context))
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Смена внешности'].achieved(update=update, context=context))
            edit = False
        if edit:
            query.edit_message_text(text=location_status(update=update, context=context, location=users[user_id].player.current_location) + '\n\nХирург: Я рад, что вы пришли, сначала я подготовлю инструменты, а потом мы приступим.', reply_markup=(choose_action_keyboard(update=update, context=context)))
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=location_status(update=update, context=context, location=users[user_id].player.current_location) + '\n\nХирург: Я рад, что вы пришли, сначала я подготовлю инструменты, а потом мы приступим.', reply_markup=(choose_action_keyboard(update=update, context=context)))

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
            query.edit_message_text(text=users[user_id].player.current_location.unlock(update=update, context=context))
            edit = False
        if edit:
            query.edit_message_text(text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=(knock_jason_portman_keyboard_2()))
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=(knock_jason_portman_keyboard_2()))

    def cigar_kill_6(update: Update, context: CallbackContext):
        user_id = update.callback_query.from_user['id']
        query = update.callback_query
        query.answer()
        if users[user_id].challenges['Курение убивает'].completed == False:
            query.edit_message_text(text=users[user_id].challenges['Курение убивает'].achieved(update=update, context=context))
            users[user_id].player_lvl += users[user_id].challenges['Курение убивает'].xp
            if users[user_id].challenges['Так можно и пораниться'].completed == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Так можно и пораниться'].achieved(update=update, context=context))
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
                query.edit_message_text(text=users[user_id].challenges['В клубах дыма'].achieved(update=update, context=context))
                users[user_id].player_lvl += users[user_id].challenges['В клубах дыма'].xp
                if users[user_id].challenges['Так можно и пораниться'].completed == False:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Так можно и пораниться'].achieved(update=update, context=context))
                    users[user_id].player_lvl += users[user_id].challenges['Так можно и пораниться'].xp
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
            query.edit_message_text(text=users[user_id].challenges['Не курить!'].achieved(update=update, context=context))
            users[user_id].player_lvl += users[user_id].challenges['Не курить!'].xp
            context.bot.send_message(chat_id=update.effective_chat.id, text='На балконе находится газовый обогреватель.', reply_markup=cigar_kill_keyboard_2())
        else:
            query.edit_message_text(text='На балконе находится газовый обогреватель.', reply_markup=cigar_kill_keyboard_2())

    def sushi_kill_4(update: Update, context: CallbackContext):
        user_id = update.callback_query.from_user['id']
        query = update.callback_query
        query.answer()
        if users[user_id].challenges['Подержи волосы'].completed == False:
            query.edit_message_text(text=users[user_id].challenges['Подержи волосы'].achieved(update=update, context=context))
            users[user_id].player_lvl += users[user_id].challenges['Подержи волосы'].xp
            if users[user_id].challenges['Без вкуса, без следа'].completed == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Без вкуса, без следа'].achieved(update=update, context=context))
                users[user_id].player_lvl += users[user_id].challenges['Без вкуса, без следа'].xp
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
                    query.edit_message_text(text=users[user_id].challenges['Приятного аппетита'].achieved(update=update, context=context))
                    users[user_id].player_lvl += users[user_id].challenges['Приятного аппетита'].xp
                    if users[user_id].challenges['Без вкуса, без следа'].completed == False:
                        context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Без вкуса, без следа'].achieved(update=update, context=context))
                        users[user_id].player_lvl += users[user_id].challenges['Без вкуса, без следа'].xp
                    context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].targets['Yuki Yamazaki'].kill(), reply_markup=choose_action_keyboard(update=update, context=context))
                else:
                    query.edit_message_text(text=users[user_id].targets['Yuki Yamazaki'].kill(), reply_markup=choose_action_keyboard(update=update, context=context))
            elif users[user_id].challenges['Без вкуса, без следа'].completed == False:
                query.edit_message_text(text=users[user_id].challenges['Без вкуса, без следа'].achieved(update=update, context=context))
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
                query.edit_message_text(text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=choose_action_keyboard(update=update, context=context))

    def yoga_kill_2(update: Update, context: CallbackContext):
        user_id = update.callback_query.from_user['id']
        query = update.callback_query
        query.answer()
        if users[user_id].challenges['Хорошая растяжка'].completed == False:
            query.edit_message_text(text=users[user_id].challenges['Хорошая растяжка'].achieved(update=update, context=context))
            users[user_id].player_lvl += users[user_id].challenges['Хорошая растяжка'].xp
            if users[user_id].challenges['Так можно и пораниться'].completed == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Так можно и пораниться'].achieved(update=update, context=context))
                users[user_id].player_lvl += users[user_id].challenges['Так можно и пораниться'].xp
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
        query = update.callback_query
        query.answer()
        if users[user_id].challenges['Личная встреча'].completed == False:
            users[user_id].player_lvl += users[user_id].challenges['Личная встреча'].xp
            query.edit_message_text(text=users[user_id].challenges['Личная встреча'].achieved(update=update, context=context))
            context.bot.send_message(chat_id=update.effective_chat.id, text='Главный хирург отвернулся от вас и начал принимать таблетки.', reply_markup=(surgeon_knock_out_keyboard_2()))
        else:
            query.edit_message_text(text='Главный хирург отвернулся от вас и начал принимать таблетки.', reply_markup=(surgeon_knock_out_keyboard_2()))

    def sauna_kill_2(update: Update, context: CallbackContext):
        user_id = update.callback_query.from_user['id']
        query = update.callback_query
        query.answer()
        if users[user_id].challenges['Убийство в парилке'].completed == False:
            query.edit_message_text(text=users[user_id].challenges['Убийство в парилке'].achieved(update=update, context=context))
            users[user_id].player_lvl += users[user_id].challenges['Убийство в парилке'].xp
            if users[user_id].challenges['Так можно и пораниться'].completed == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Так можно и пораниться'].achieved(update=update, context=context))
                users[user_id].player_lvl += users[user_id].challenges['Так можно и пораниться'].xp
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

    def robot_kill_2(update: Update, context: CallbackContext):
        user_id = update.callback_query.from_user['id']
        query = update.callback_query
        query.answer()
        if users[user_id].challenges['(Не) врачебная ошибка'].completed == False:
            query.edit_message_text(text=users[user_id].challenges['(Не) врачебная ошибка'].achieved(update=update, context=context))
            users[user_id].player_lvl += users[user_id].challenges['(Не) врачебная ошибка'].xp
            if users[user_id].challenges['Так можно и пораниться'].completed == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Так можно и пораниться'].achieved(update=update, context=context))
                users[user_id].player_lvl += users[user_id].challenges['Так можно и пораниться'].xp
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
            query.edit_message_text(text=users[user_id].challenges['Бессердечный'].achieved(update=update, context=context))
            users[user_id].player_lvl += users[user_id].challenges['Бессердечный'].xp
            context.bot.send_message(chat_id=update.effective_chat.id, text='Диана: 47-й, без сердца для пересадки Содерс не выживет. Ты смог от него избавиться даже не прикасаясь, изящный ход.', reply_markup=(choose_action_keyboard(update=update, context=context)))
        else:
            query.edit_message_text(text='Диана: 47-й, без сердца для пересадки Содерс не выживет. Ты смог от него избавиться даже не прикасаясь, изящный ход.', reply_markup=(choose_action_keyboard(update=update, context=context)))
    
    def destroy_servers(update: Update, context: CallbackContext):
        user_id = update.callback_query.from_user['id']
        users[user_id].targets['Erich Soders'].alive = False
        query = update.callback_query
        query.answer()
        if users[user_id].challenges['Призрак в машине'].completed == False:
            query.edit_message_text(text=users[user_id].challenges['Призрак в машине'].achieved(update=update, context=context))
            users[user_id].player_lvl += users[user_id].challenges['Призрак в машине'].xp
            if users[user_id].challenges['Так можно и пораниться'].completed == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Так можно и пораниться'].achieved(update=update, context=context))
                users[user_id].player_lvl += users[user_id].challenges['Так можно и пораниться'].xp
            context.bot.send_message(chat_id=update.effective_chat.id, text='Хирург: Что происходит с роботом?! Как его отключить?! Пациент сейчас умрет!\n\nДиана: Это было впечатляюще, агент. Эрих Содерс мертв.', reply_markup=(choose_action_keyboard(update=update, context=context)))
        else:
            query.edit_message_text(text='Хирург: Что происходит с роботом?! Как его отключить?! Пациент сейчас умрет!\n\nДиана: Это было впечатляюще, агент. Эрих Содерс мертв.', reply_markup=(choose_action_keyboard(update=update, context=context)))

    #Механики игры

    def save_and_quit(update: Update, context: CallbackContext):
        """Сохранение и выход из игры"""
        user_id = update.callback_query.from_user['id']
        query = update.callback_query
        query.answer()
        completed_challenges = []
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
        adapter.update_by_id("Users", f'completed_challenges={completed_challenges_str}', user_id)
        adapter.update_by_id("Users", f'unlocked_disguises={unlocked_disguises_str}', user_id)
        adapter.update_by_id("Users", f'unlocked_locations={unlocked_locations_str}', user_id)
        adapter.update_by_id("Users", f'player_lvl={users[user_id].player_lvl}', user_id)
        users[user_id] = create_user(player_lvl=users[user_id].player_lvl, completed_challenges=completed_challenges_str, unlocked_disguises=unlocked_disguises_str, unlocked_locations=unlocked_locations_str)
        query.edit_message_text(text='Данные сохранены.', reply_markup=start_keyboard())

    def use(update: Update, context: CallbackContext):
        """Использовать предмет"""
        user_id = update.callback_query.from_user['id']
        query = update.callback_query
        query.answer()
        if users[user_id].player.item.name == 'Пульт от нейрочипа' and users[user_id].events['Уничтожить сердце'].completed == False and users[user_id].player.current_location.name == 'Морг':
            users[user_id].events['Уничтожить сердце'].completed = True
            users[user_id].player.inventory.remove(users[user_id].player.item)
            users[user_id].player.item = users[user_id].items['Нет предмета']
            query.edit_message_text(text='Нейрочип подействовал на одного из работников морга и тот отправился в комнату, где хранится сердце, которое должны пересадить Эриху Содерсу.\n\nПоследовать за ним?', reply_markup=(destroy_heart_keyboard_1()))
        if users[user_id].player.item.name == 'Пульт от нейрочипа' and (users[user_id].events['Уничтожить сердце'].completed == True or users[user_id].player.current_location.name != 'Морг'):
            query.edit_message_text(text='Вне зоны действия', reply_markup=(choose_action_keyboard(update=update, context=context)))

    def distract_kill(update: Update, context: CallbackContext):
        """Убить после отвлечения"""
        user_id = update.callback_query.from_user['id']
        if users[user_id].player.item.name == 'Монета':
            users[user_id].player.current_location.items.append(users[user_id].player.item)
        users[user_id].player.inventory.remove(users[user_id].player.item)
        query = update.callback_query
        npc_name = query.data.replace('CDKL', '')
        users[user_id].kills += 1
        npc = users[user_id].npcs[npc_name]
        npc.alive = False
        users[user_id].player.found_disguises.append(npc.disguise)
        query.answer()
        query.edit_message_text(text=f'Вы устранили {npc.name}', reply_markup=(choose_action_keyboard(update=update, context=context)))

    def distract_knock_out(update: Update, context: CallbackContext):
        """Вырубить после отвлечения"""
        user_id = update.callback_query.from_user['id']
        if users[user_id].player.item.name == 'Монета':
            users[user_id].player.current_location.items.append(users[user_id].player.item)
        users[user_id].player.inventory.remove(users[user_id].player.item)
        query = update.callback_query
        npc = users[user_id].npcs[query.data.replace('CDKN', '')]
        npc.alive = False
        users[user_id].player.found_disguises.append(npc.disguise)
        query.answer()
        query.edit_message_text(text=f'Вы вырубили {npc.name}', reply_markup=(choose_action_keyboard(update=update, context=context)))

    def knock_out(update: Update, context: CallbackContext):
        """Вырубить предметом"""
        user_id = update.callback_query.from_user['id']
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
        if users[user_id].thrown_weapon:
            users[user_id].player.inventory.remove(users[user_id].player.item)
            users[user_id].thrown_weapon = False
        query = update.callback_query
        data = query.data.replace('con_knock', '')[:-1]
        chance = int(query.data.replace('con_knock', '')[-1])
        if data in list(users[user_id].npcs.keys()):
            target = users[user_id].npcs[data]
            users[user_id].player.found_disguises.append(target.disguise)
            users[user_id].kills += 1
        else:
            target = users[user_id].targets[data]
            if data == 'Erich Soders' and (users[user_id].player.item.name == 'Bartoli 75R' or users[user_id].player.item.name == 'ICA 19') and users[user_id].challenges['Личное прощание'].completed == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Личное прощание'].achieved(update=update, context=context))
                users[user_id].player_lvl += users[user_id].challenges['Личное прощание'].xp
            context.bot.send_message(chat_id=update.effective_chat.id, text=target.kill())
        target.alive = False
        if chance > 0:
            users[user_id].bodies += 1
            combat(update=update, context=context, start_string=f'Цель устранена: {target.name}\n\n', type='add')
        else:
            if data == 'Erich Soders' and (users[user_id].player.item.name == 'Bartoli 75R' or users[user_id].player.item.name == 'ICA 19'):
                context.bot.send_message(chat_id=update.effective_chat.id, text=f'Цель устранена: {target.name}', reply_markup=(choose_action_keyboard(update=update, context=context)))
            else:
                query.answer()
                query.edit_message_text(text=f'Цель устранена: {target.name}', reply_markup=(choose_action_keyboard(update=update, context=context)))

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
            combat(update=update, context=context, start_string=f'Цель устранена: {enemies[0].name}\n\n')
        else:
            if 'Бросить' in query.data:
                users[user_id].player.current_location.items.append(users[user_id].player.item)
                users[user_id].player.inventory.remove(users[user_id].player.item)
            users[user_id].player.health -= 25
            combat(update=update, context=context, start_string='Промах\n\n')

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
        if rating == 5 and users[user_id].suit_only == False:
            if users[user_id].challenges['Бесшумный убийца'].completed == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Бесшумный убийца'].achieved(update=update, context=context))
                users[user_id].player_lvl += users[user_id].challenges['Бесшумный убийца'].xp
        elif rating == 5 and users[user_id].suit_only:
            if users[user_id].challenges['Бесшумный убийца. Только костюм.'].completed == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Бесшумный убийца. Только костюм.'].achieved(update=update, context=context))
                users[user_id].player_lvl += users[user_id].challenges['Бесшумный убийца. Только костюм.'].xp
        elif users[user_id].suit_only:
            if users[user_id].challenges['Только костюм'].completed == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Только костюм'].achieved(update=update, context=context))
                users[user_id].player_lvl += users[user_id].challenges['Только костюм'].xp
        if users[user_id].bodies == 0:
            if users[user_id].challenges['Без улик'].completed == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Без улик'].achieved(update=update, context=context))
                users[user_id].player_lvl += users[user_id].challenges['Без улик'].xp
        if users[user_id].challenges['Точный выстрел'].completed == True and users[user_id].challenges['Подержи волосы'].completed == True and users[user_id].challenges['Пианист'].completed == True and users[user_id].challenges['Так можно и пораниться'].completed == True and users[user_id].challenges['Без вкуса, без следа'].completed == True and users[user_id].challenges['Мастер-убийца'].completed == False:
            context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Мастер-убийца'].achieved(update=update, context=context))
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
        adapter.update_by_id("Users", f'completed_challenges={completed_challenges_str}', user_id)
        adapter.update_by_id("Users", f'unlocked_disguises={unlocked_disguises_str}', user_id)
        adapter.update_by_id("Users", f'unlocked_locations={unlocked_locations_str}', user_id)
        adapter.update_by_id("Users", f'player_lvl={users[user_id].player_lvl}', user_id)
        users[user_id] = create_user(player_lvl=users[user_id].player_lvl, completed_challenges=completed_challenges_str, unlocked_disguises=unlocked_disguises_str, unlocked_locations=unlocked_locations_str)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Миссия выполнена.', reply_markup=start_keyboard())

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
            users[user_id].time = 0

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
        query.edit_message_text(text=f'Сейчас в руках: {users[user_id].player.item.name}', reply_markup=(choose_action_keyboard(update=update, context=context)))

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
            query.edit_message_text(text=users[user_id].player.disguise.unlock(update=update, context=context))
            if users[user_id].player.disguise.name == 'Директор клиники' and users[user_id].challenges['Новое руководство'].completed == False:
                users[user_id].player_lvl += users[user_id].challenges['Новое руководство'].xp
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Новое руководство'].achieved(update=update, context=context))
            if users[user_id].player.disguise.name == 'Инструктор по йоге' and users[user_id].challenges['Поза лотоса'].completed == False:
                users[user_id].player_lvl += users[user_id].challenges['Поза лотоса'].xp
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Поза лотоса'].achieved(update=update, context=context))
            if users[user_id].player.disguise.name == 'Пилот' and users[user_id].challenges['Включите автопилот'].completed == False:
                users[user_id].player_lvl += users[user_id].challenges['Включите автопилот'].xp
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Включите автопилот'].achieved(update=update, context=context))
            if users[user_id].player.disguise.name == 'Джейсон Портман' and users[user_id].challenges['Новое лицо'].completed == False:
                users[user_id].player_lvl += users[user_id].challenges['Новое лицо'].xp
                context.bot.send_message(chat_id=update.effective_chat.id, text=users[user_id].challenges['Новое лицо'].achieved(update=update, context=context))
            context.bot.send_message(chat_id=update.effective_chat.id, text=f'Текущая маскировка: {users[user_id].player.disguise.name}', reply_markup=(choose_action_keyboard(update=update, context=context)))
        else:
            query.edit_message_text(text=f'Текущая маскировка: {users[user_id].player.disguise.name}', reply_markup=(choose_action_keyboard(update=update, context=context)))

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

    def no_disguise_move(update: Update, context: CallbackContext):
        """Передвижение без необходимой маскировки"""
        user_id = update.callback_query.from_user['id']
        query = update.callback_query
        chance = int(query.data.replace('ПРТ', '').split(':')[0])
        move_to_location = users[user_id].locations[query.data.replace('ПРТ', '').split(':')[1]]
        edit = True
        if users[user_id].events['Информация о стволовых клетках'].completed == False and move_to_location.name == 'Операционная':
            query.edit_message_text(text='Руководство по проведению революционной терапии стволовыми клетками, разработанной доктором Лораном.\n\nОчевидно, стволовые клетки способны временно ускорять выздоровление тканей, что значительно повышает шансы пациента на выживание.\n\nСтволовые клетки забираются из специального сосуда и вливаются прямо в кровь пациента.')
            users[user_id].events['Информация о стволовых клетках'].completed = True
            edit = False
        if users[user_id].events['Джейсон Портман'].completed == False and move_to_location.name == 'Холл':
            query.edit_message_text(text='Диана: У меня есть сведения о пациенте в бинтах.\n\nТак-так, это уже интересно. Забинтованный пациент — Джейсон Портман, генеральный директор «Квантум лип».\n\nСогласно моим данным, ему сделали полную реконструкцию лица и сегодня снимают повязки. И вот что самое занятное — он хочет быть как две капли воды похожим на Хельмута Крюгера.')
            users[user_id].events['Джейсон Портман'].completed = True
            edit = False
        if users[user_id].events['Компьютер в морге'].completed == False and move_to_location.name == 'Морг':
            query.edit_message_text(text='Вы нашли файл на компьютере. Это заметки о Кураторе и его нейрочипе.\n\nВ них приводятся подробные сведения об устройстве чипа и принципе его работы, а также описание того, как изменение дозы влияет на настроение Куратора. Судя по всему, увеличение дозы приводит к улучшению его настроения, а уменьшение, напротив, возвращает его в привычное подавленное состояние.\n\nЧто любопытно, научный сотрудник, похоже, сам менял дозу Куратора без его ведома: для этого он использовал пульт управления чипом, который куратор хранит в своей спальне.')
            users[user_id].events['Компьютер в морге'].completed = True
            edit = False
        if users[user_id].events['Информация о сигаретах 2'].completed == False and move_to_location.name == 'Канатная дорога':
            query.edit_message_text(text='Диана: Значит, Юки Ямадзаки выронила свои сигареты по пути к клинике. Интересно.\n\nЮки Ямадзаки уронила свои сигареты, когда поднималась на фуникулере по прибытии в клинику. Если верить её охране, это её ужасно взбесило.\n\nМожет быть, тебе удастся утолить её «жажду», 47-й? Сигареты в «Гаме» запрещены, но не все следуют этому правилу...')
            users[user_id].events['Информация о сигаретах 2'].completed = True
            edit = False
        if users[user_id].events['Информация о суши'].completed == False and move_to_location.name == 'Ресторан':
            query.edit_message_text(text='Диана: Ядовитая Рыба фугу и адвокат в поисках острых ощущений — убийственная комбинация.\n\nНе так давно из-за ошибки повара один из пациентов отравился ядовитой рыбой, и с тех пор фугу здесь под строжайшим запретом. Но, судя по всему, Юки Ямадзаки пытается уговорить шеф-повара подать ей последнюю рыбу из его запасов.\n\nРазве мы вправе отказывает ей в таком удовольствии, 47-й?')
            users[user_id].events['Информация о суши'].completed = True
            edit = False
        if users[user_id].events['Расписание занятий по йоге'].completed == False and move_to_location.name == 'Зона отдыха':
            query.edit_message_text(text='Диана: Расписание занятий по йоге. Имя Юки Ямадзаки — в каждой графе. Что ж, судя по всему, Юки Ямадзаки — настоящий фанат йоги.\n\nИз расписания у горячего источника видно, что она заняла тренера на целый день. Готов размяться, 47-й?')
            users[user_id].events['Расписание занятий по йоге'].completed = True
            edit = False
        if users[user_id].events['Информация о пилоте'].completed == False and (move_to_location.name == 'Вертолетная площадка' or move_to_location.name == 'Комната пилота'):
            query.edit_message_text(text='Диана: 47-й, у меня есть сведения о пилоте. Мне удалось извлечь кое-какие данные из системы безопасности клиники.\n\nГлавный хирург, Николя Лоран, похоже, часто встречается с пилотом вертолёта у выхода из мед-комплекса. А если верить слухам, у главного хирурга дрожат руки.')
            users[user_id].events['Информация о пилоте'].completed = True
            edit = False
        if users[user_id].events['Информация об ИИ'].completed == False and move_to_location.name == 'Комната охраны':
            query.edit_message_text(text='Интересно. Руководство для KAI, искусственного интеллекта клиники «Гама». Значит, местный искусственный интеллект по имени KAI не только поддерживает работу систем здания, но и управляет роботом в операционной.\n\nИменно там сейчас находится Содерс. В руководстве говорится, что после остановки сердца пациента искусственный интеллект автоматически начинает его реанимацию, что очень некстати.\n\nОднако... У директора клиники есть доступ к главному компьютеру. Справишься с управлением целой клиникой, 47-й?')
            users[user_id].events['Информация об ИИ'].completed = True
            edit = False
        if move_to_location.unlocked == False:
            if edit:
                query.edit_message_text(text=move_to_location.unlock(update=update, context=context))
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text=move_to_location.unlock(update=update, context=context))
            edit = False
        if random.randrange(1, 11) <= chance:
            users[user_id].player.compromised_disguises.append(users[user_id].player.disguise)
            users[user_id].player.current_location = move_to_location
            query.answer()
            if edit:
                query.edit_message_text(text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=(choose_action_keyboard(update=update, context=context)))
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=(choose_action_keyboard(update=update, context=context)))
        else:
            locations_npcs = find_location_npcs(update=update, context=context, location=move_to_location)
            location_npc = locations_npcs[random.randrange(len(locations_npcs))]
            query.answer()
            if edit:
                query.edit_message_text(text=location_npc.suspicion(), reply_markup=attack_keyboard(location_npc, move_to_location))
                users[user_id].suspicion_count += 1
            else:
                context.bot.send_message(chat_id=update.effective_chat.id,text=location_npc.suspicion(), reply_markup=attack_keyboard(location_npc, move_to_location))
                users[user_id].suspicion_count += 1

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

    def move(update: Update, context: CallbackContext):
        """Передвижение по локациям"""
        user_id = update.callback_query.from_user['id']
        query = update.callback_query
        query.answer()
        move_to_location = users[user_id].locations[query.data.replace('basic_move', '')]
        edit = True
        if users[user_id].player.disguise in move_to_location.disguise:
            #Случай, когда маскировка игрока позволяет пройти на локацию
            if users[user_id].events['Информация о стволовых клетках'].completed == False and move_to_location.name == 'Операционная':
                query.edit_message_text(text='Руководство по проведению революционной терапии стволовыми клетками, разработанной доктором Лораном.\n\nОчевидно, стволовые клетки способны временно ускорять выздоровление тканей, что значительно повышает шансы пациента на выживание.\n\nСтволовые клетки забираются из специального сосуда и вливаются прямо в кровь пациента.')
                users[user_id].events['Информация о стволовых клетках'].completed = True
                edit = False
            if users[user_id].events['Джейсон Портман'].completed == False and move_to_location.name == 'Холл':
                query.edit_message_text(text='Диана: У меня есть сведения о пациенте в бинтах.\n\nТак-так, это уже интересно. Забинтованный пациент — Джейсон Портман, генеральный директор «Квантум лип».\n\nСогласно моим данным, ему сделали полную реконструкцию лица и сегодня снимают повязки. И вот что самое занятное — он хочет быть как две капли воды похожим на Хельмута Крюгера.')
                users[user_id].events['Джейсон Портман'].completed = True
                edit = False
            if users[user_id].events['Компьютер в морге'].completed == False and move_to_location.name == 'Морг':
                query.edit_message_text(text='Вы нашли файл на компьютере. Это заметки о Кураторе и его нейрочипе.\n\nВ них приводятся подробные сведения об устройстве чипа и принципе его работы, а также описание того, как изменение дозы влияет на настроение Куратора. Судя по всему, увеличение дозы приводит к улучшению его настроения, а уменьшение, напротив, возвращает его в привычное подавленное состояние.\n\nЧто любопытно, научный сотрудник, похоже, сам менял дозу Куратора без его ведома: для этого он использовал пульт управления чипом, который куратор хранит в своей спальне.')
                users[user_id].events['Компьютер в морге'].completed = True
                edit = False
            if users[user_id].events['Информация о сигаретах 2'].completed == False and move_to_location.name == 'Канатная дорога':
                query.edit_message_text(text='Диана: Значит, Юки Ямадзаки выронила свои сигареты по пути к клинике. Интересно.\n\nЮки Ямадзаки уронила свои сигареты, когда поднималась на фуникулере по прибытии в клинику. Если верить её охране, это её ужасно взбесило.\n\nМожет быть, тебе удастся утолить её «жажду», 47-й? Сигареты в «Гаме» запрещены, но не все следуют этому правилу...')
                users[user_id].events['Информация о сигаретах 2'].completed = True
                edit = False
            if users[user_id].events['Информация о суши'].completed == False and move_to_location.name == 'Ресторан':
                query.edit_message_text(text='Диана: Ядовитая Рыба фугу и адвокат в поисках острых ощущений — убийственная комбинация.\n\nНе так давно из-за ошибки повара один из пациентов отравился ядовитой рыбой, и с тех пор фугу здесь под строжайшим запретом. Но, судя по всему, Юки Ямадзаки пытается уговорить шеф-повара подать ей последнюю рыбу из его запасов.\n\nРазве мы вправе отказывает ей в таком удовольствии, 47-й?')
                users[user_id].events['Информация о суши'].completed = True
                edit = False
            if users[user_id].events['Расписание занятий по йоге'].completed == False and move_to_location.name == 'Зона отдыха':
                query.edit_message_text(text='Диана: Расписание занятий по йоге. Имя Юки Ямадзаки — в каждой графе. Что ж, судя по всему, Юки Ямадзаки — настоящий фанат йоги.\n\nИз расписания у горячего источника видно, что она заняла тренера на целый день. Готов размяться, 47-й?')
                users[user_id].events['Расписание занятий по йоге'].completed = True
                edit = False
            if users[user_id].events['Информация о пилоте'].completed == False and (move_to_location.name == 'Вертолетная площадка' or move_to_location.name == 'Комната пилота'):
                query.edit_message_text(text='Диана: 47-й, у меня есть сведения о пилоте. Мне удалось извлечь кое-какие данные из системы безопасности клиники.\n\nГлавный хирург, Николя Лоран, похоже, часто встречается с пилотом вертолёта у выхода из мед-комплекса. А если верить слухам, у главного хирурга дрожат руки.')
                users[user_id].events['Информация о пилоте'].completed = True
                edit = False
            if users[user_id].events['Информация об ИИ'].completed == False and move_to_location.name == 'Комната охраны':
                query.edit_message_text(text='Интересно. Руководство для KAI, искусственного интеллекта клиники «Гама». Значит, местный искусственный интеллект по имени KAI не только поддерживает работу систем здания, но и управляет роботом в операционной.\n\nИменно там сейчас находится Содерс. В руководстве говорится, что после остановки сердца пациента искусственный интеллект автоматически начинает его реанимацию, что очень некстати.\n\nОднако... У директора клиники есть доступ к главному компьютеру. Справишься с управлением целой клиникой, 47-й?')
                users[user_id].events['Информация об ИИ'].completed = True
                edit = False
            if move_to_location.unlocked == False:
                if edit:
                    query.edit_message_text(text=move_to_location.unlock(update=update, context=context))
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=move_to_location.unlock(update=update, context=context))
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
                        query.edit_message_text(text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=choose_action_keyboard(update=update, context=context))
                    else:
                        context.bot.send_message(chat_id=update.effective_chat.id, text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=choose_action_keyboard(update=update, context=context))
            elif users[user_id].player.item.legal == False:
                #Случай, когда в руках игрока нелегальный предмет
                if users[user_id].player.disguise.name != 'Охранник' and users[user_id].player.disguise.name != 'Телохранитель':
                    if find_location_npcs(update=update, context=context, location=users[user_id].player.current_location) != []:
                        location_npc = find_location_npcs(update=update, context=context, location=users[user_id].player.current_location)[random.randrange(len(find_location_npcs(update=update, context=context, location=users[user_id].player.current_location)))]
                        users[user_id].suspicion_count += 1
                        if edit:
                            query.edit_message_text(text=f'{location_npc.name} ({location_npc.disguise.name}): Он вооружен!', reply_markup=hide_keyboard(location_npc, users[user_id].player.current_location))
                        else:
                            context.bot.send_message(chat_id=update.effective_chat.id, text=f'{location_npc.name} ({location_npc.disguise.name}): Он вооружен!', reply_markup=hide_keyboard(location_npc, users[user_id].player.current_location))
                    else:
                        if edit:
                            query.edit_message_text(text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=choose_action_keyboard(update=update, context=context))
                        else:
                            context.bot.send_message(chat_id=update.effective_chat.id, text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=choose_action_keyboard(update=update, context=context))
                else:
                    if edit:
                        query.edit_message_text(text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=choose_action_keyboard(update=update, context=context))
                    else:
                        context.bot.send_message(chat_id=update.effective_chat.id, text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=choose_action_keyboard(update=update, context=context))
            else:
                if edit:
                    query.edit_message_text(text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=choose_action_keyboard(update=update, context=context))
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=choose_action_keyboard(update=update, context=context))
        else:
            #Случай, когда маскировка игрока не позволяет пройти на локацию
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
                            query.edit_message_text(text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=(choose_action_keyboard(update=update, context=context)))
                    else:
                        if users[user_id].targets['Erich Soders'].alive == True:
                            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите действие', reply_markup=(destroy_servers_keyboard()))
                        else:
                            context.bot.send_message(chat_id=update.effective_chat.id, text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=(choose_action_keyboard(update=update, context=context)))
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
                        query.edit_message_text(text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=(choose_action_keyboard(update=update, context=context)))
                    else:
                        context.bot.send_message(chat_id=update.effective_chat.id, text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=(choose_action_keyboard(update=update, context=context)))
                else:
                    if edit:
                        query.edit_message_text(text='Для входа необходима маскировка.', reply_markup=move_keyboard(update=update, context=context))
                    else:
                        context.bot.send_message(chat_id=update.effective_chat.id, text='Для входа необходима маскировка.', reply_markup=move_keyboard(update=update, context=context))
            else:
                chance = min(10, location_witnesses(update=update, context=context, location=users[user_id].player.current_location))
                query.edit_message_text(text='У вас нет подходящей маскировки. Переместиться на локацию?', reply_markup=(no_disguise_move_keyboard(chance=chance, location=move_to_location)))

    def combat(update: Update, context: CallbackContext, start_string='', type='edit'):
        """Бой"""
        user_id = update.callback_query.from_user['id']
        users[user_id].time += 10
        enemies = []
        query = update.callback_query

        for i in find_location_npcs(update=update, context=context, location=users[user_id].player.current_location):
            if i.guard:
                enemies.append(i)
        if type == 'edit':
            if users[user_id].player.health == 0:
                query.answer()
                query.edit_message_text(text='Вы умерли. Миссия провалена.')
                users[user_id].time = 0
            if enemies == []:
                users[user_id].player.health = 100
                query.answer()
                query.edit_message_text(text=start_string + f'Бой закончился.\n\nУбито невинных: {users[user_id].kills}\nНайдено тел: {users[user_id].bodies}', reply_markup=(choose_action_keyboard(update=update, context=context)))
            else:
                query.answer()
                query.edit_message_text(text=start_string + f'Выберите оружие', reply_markup=(choose_weapon_keyboard(update=update, context=context)))
        elif type == 'add':
            if users[user_id].player.health == 0:
                context.bot.send_message(chat_id=update.effective_chat.id, text='Вы умерли. Миссия провалена.')
                users[user_id].time = 0
            if enemies == []:
                users[user_id].player.health = 100
                context.bot.send_message(chat_id=update.effective_chat.id, text=start_string + f'Бой закончился.\n\nУбито невинных: {users[user_id].kills}\nНайдено тел: {users[user_id].bodies}', reply_markup=(choose_action_keyboard(update=update, context=context)))
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text=start_string + f'Выберите оружие', reply_markup=(choose_weapon_keyboard(update=update, context=context)))

    def safe_move(update: Update, context: CallbackContext):
        """Передвижение, не зависящее от маскировки"""
        user_id = update.callback_query.from_user['id']
        query = update.callback_query
        if users[user_id].player.item.name == 'Монета':
            users[user_id].player.current_location.items.append(users[user_id].player.item)
        users[user_id].player.inventory.remove(users[user_id].player.item)
        users[user_id].player.current_location = users[user_id].locations[query.data.replace('SM', '')]
        query.answer()
        query.edit_message_text(text=location_status(update=update, context=context, location=users[user_id].player.current_location), reply_markup=(choose_action_keyboard(update=update, context=context)))

    def spawn_player(update: Update, context: CallbackContext):
        """Задать начальные параметры для игрока"""
        user_id = update.callback_query.from_user['id']
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
        for i in list(lvl_unlocks.values()):
            if i[0] == users[user_id].player.current_location.name:
                start_disguise = users[user_id].disguises[i[1]]
        users[user_id].player.found_disguises = [start_disguise]
        users[user_id].player.item = users[user_id].items['Нет предмета']
        users[user_id].player.compromised_disguises = []
        users[user_id].player.disguise = start_disguise
        if users[user_id].player.disguise.name != 'VIP - пациент':
            users[user_id].suit_only = False
        text = 'Диана: Добро пожаловать на Хоккайдо, 47-й. Частная клиника «Гама» оказывает медицинские услуги высочайшего уровня представителям мировой элиты, выходя при необходимости за рамки закона\n\n Частично здание находится под управлением искусственного интеллекта — KAI. Система контролирует доступ пациентов в разные части клиники и даже принимает участие в ряде медицинских процедур.\n\nЭрих Содерс уже находится в операционной, где он проходит предварительную подготовку с применением стволовых клеток. Это крайне противоречивая процедура ещё не одобрена властями Японии.\n\nЮки Ямадзаки уже прибыла. Она находится либо в своём номере, либо в ресторане, либо в спа-зоне клиники. Содерсу скоро введут наркоз. Сделай так, чтобы он больше никогда не проснулся. Удачи, 47-й.'
        if users[user_id].player.current_location.name == 'Номер 47-го':
            query = update.callback_query
            query.answer()
            query.edit_message_text(text=text)
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите действие', reply_markup=(choose_action_keyboard(update=update, context=context)))
        else:
            query = update.callback_query
            query.answer()
            query.edit_message_text(text='Выберите действие', reply_markup=(choose_action_keyboard(update=update, context=context)))

    def briefing_1(update: Update, context: CallbackContext):
        """Брифинг к миссии"""
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='Диана: Доброе утро, 47-й. Совет директоров одобрил ликвидацию Эриха Содерса. После Колорадо мы решили пристально изучить личные дела Содерса и выяснили, что его недавно доставили в частную клинику «Гама» на японском острове Хоккайдо для срочной операции на сердце. Без «Провиденс» тут явно не обошлось.', reply_markup=(briefing_keyboard_1(update=update, context=context)))

    def briefing_2(update: Update, context: CallbackContext):
        """Брифинг к миссии"""
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='Диана: Доброе утро, 47-й. Совет директоров одобрил ликвидацию Эриха Содерса. После Колорадо мы решили пристально изучить личные дела Содерса и выяснили, что его недавно доставили в частную клинику «Гама» на японском острове Хоккайдо для срочной операции на сердце. Без «Провиденс» тут явно не обошлось.')
        context.bot.send_message(chat_id=update.effective_chat.id, text='Содерс страдает от редкой врожденной патологии — транспозиции органов: его внутренние органы в теле расположены зеркально. Для трансплантации ему необходимо правостороннее сердце, и он явно предал МКА, чтобы получить его. Его приняли прошлой ночью и сейчас он готовится к трёхэтапной операции.', reply_markup=(briefing_keyboard_2(update=update, context=context)))
    
    def briefing_3(update: Update, context: CallbackContext):
        """Брифинг к миссии"""
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='Содерс страдает от редкой врожденной патологии — транспозиции органов: его внутренние органы в теле расположены зеркально. Для трансплантации ему необходимо правостороннее сердце, и он явно предал МКА, чтобы получить его. Его приняли прошлой ночью и сейчас он готовится к трёхэтапной операции.')
        context.bot.send_message(chat_id=update.effective_chat.id, text='Под видом Тобиаса Рипера, крупного бизнесмена, ты отправляешься в «Гаму» для стандартного медицинского обследования, о формальностях мы уже позаботились. В таких условиях придётся импровизировать и самостоятельно добывать снаряжение.', reply_markup=(briefing_keyboard_3(update=update, context=context)))

    def briefing_4(update: Update, context: CallbackContext):
        """Брифинг к миссии"""
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='Под видом Тобиаса Рипера, крупного бизнесмена, ты отправляешься в «Гаму» для стандартного медицинского обследования, о формальностях мы уже позаботились. В таких условиях придётся импровизировать и самостоятельно добывать снаряжение.')
        context.bot.send_message(chat_id=update.effective_chat.id, text='Кроме того, тебе нужно ликвидировать Юки Ямадзаки — она адвокат из Токио, работает на «Провиденс». Содерс уже передал Ямадзаки доступ к нашей базе клиентов и согласился предоставить полный список оперативных сотрудников МКА после завершения операции. Этого допустить никак нельзя. Содерс должен заплатить за своё предательство — это послужит хорошим уроком его нанимателям.', reply_markup=(briefing_keyboard_4(update=update, context=context)))

    def briefing_5(update: Update, context: CallbackContext):
        """Брифинг к миссии"""
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='Кроме того, тебе нужно ликвидировать Юки Ямадзаки — она адвокат из Токио, работает на «Провиденс». Содерс уже передал Ямадзаки доступ к нашей базе клиентов и согласился предоставить полный список оперативных сотрудников МКА после завершения операции. Этого допустить никак нельзя. Содерс должен заплатить за своё предательство — это послужит хорошим уроком его нанимателям.')
        context.bot.send_message(chat_id=update.effective_chat.id, text='На кону будущее и репутация МКА. Какой бы властью и могуществом ни обладала «Провиденс», пора поставить их на место.', reply_markup=(briefing_keyboard_5(update=update, context=context)))

    def briefing_6(update: Update, context: CallbackContext):
        """Брифинг к миссии"""
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='На кону будущее и репутация МКА. Какой бы властью и могуществом ни обладала «Провиденс», пора поставить их на место.')
        context.bot.send_message(chat_id=update.effective_chat.id, text='Я оставлю тебя подготавливаться.', reply_markup=(briefing_keyboard_6(update=update, context=context)))

    #Команды бота

    def help(update: Update, context: CallbackContext):
        """Вывод инструкции к игре"""
        
        query = update.callback_query
        query.answer()
        query.edit_message_text(
            'Обучение:\n\nПередвежение – перемещение по локациям игры. Иногда данное действие требует некоторых условий, таких как нужной маскировки или небходимого предмета.\n\nВзаимодействие – использование текущего предмета. Может являться нелегальным действием.\n\nИнвентарь – открытие меню с вашими предметами и текущей маскировкой.\n\nОбыскать локацию – добавляет все предметы на текущей локации вам в инвентарь.\n\nСтатус – показывает нахождение целей задания, а также состояние текущей локации.\n\nИспытания – открывает список со всеми испытаниями. Выполненные испытания отмечаются отдельно.\n\nСохранить и выйти – завершает игру, сохраняя текущие выполненные испытания, а также уровень игрока.\n\nУровень игрока – за выполнение испытаний, а также прохождения уровня на высокий рейтинг у вас будут появляться новые стартовые локации, а также появится возможность брать с собой снаряжение.\n\nРейтинг задания – убийство невинных, количество найденных тел и раз, когда вас заметили – всё это снижает рейтинг прохождения.'
        )
        context.bot.send_message(chat_id=update.effective_chat.id, text='Добро пожаловать!', reply_markup=(start_keyboard()))

    def start(update: Update, context: CallbackContext):
        """Начало работы бота"""
        global users
        user_id = update.message.from_user['id']
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
            users[user_id] = create_user(player_lvl=10, completed_challenges='', unlocked_disguises='', unlocked_locations='')
        if update.message['message_id'] != users[user_id].message:
            users[user_id].message = update.message['message_id']
            updated = int(tm.time())

        adapter.update_by_id("Users", f'updated={updated}', user_id)

        users[user_id].message = update.message['message_id']

        context.bot.send_message(chat_id=update.effective_chat.id, text='Добро пожаловать!', reply_markup=(start_keyboard()))
        
    def begin(update: Update, context: CallbackContext):
        """Начало игры"""
        user_id = update.callback_query.from_user['id']
        if users[user_id].completed_challenges:
            for i in users[user_id].completed_challenges.split(';'):
                users[user_id].challenges[i].completed = True
        if users[user_id].unlocked_disguises:
            for i in users[user_id].unlocked_disguises.split(';'):
                users[user_id].disguises[i].unlocked = True
        if users[user_id].unlocked_locations:
            for i in users[user_id].unlocked_locations.split(';'):
                users[user_id].locations[i].unlocked = True
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='Транспозиция органов\n\nХоккайдо, Япония', reply_markup=choose_equipment_keyboard(update=update, context=context))

    def run_bot():
        """Работа бота"""
        updater = Updater(tg_token)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler('start', start))

        dispatcher.add_handler(CallbackQueryHandler(help, pattern='help'))
        dispatcher.add_handler(CallbackQueryHandler(begin, pattern='begin'))
        dispatcher.add_handler(CallbackQueryHandler(choose_action_menu, pattern='Выбор действия'))
        dispatcher.add_handler(CallbackQueryHandler(challenges_menu, pattern='Испытания'))
        dispatcher.add_handler(CallbackQueryHandler(status_menu, pattern='Статус'))
        dispatcher.add_handler(CallbackQueryHandler(choose_start_location_menu, pattern='Выбор начальной локации'))
        dispatcher.add_handler(CallbackQueryHandler(choose_pistol_menu, pattern='Выбор пистолета'))
        dispatcher.add_handler(CallbackQueryHandler(choose_start_item_menu_1, pattern='Выбор снаряжения 1'))
        dispatcher.add_handler(CallbackQueryHandler(choose_start_item_menu_2, pattern='Выбор снаряжения 2'))
        dispatcher.add_handler(CallbackQueryHandler(spawn_player, pattern='Начало игры'))
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
        dispatcher.add_handler(CallbackQueryHandler(briefing_1, pattern='briefing_1'))
        dispatcher.add_handler(CallbackQueryHandler(briefing_2, pattern='briefing_2'))
        dispatcher.add_handler(CallbackQueryHandler(briefing_3, pattern='briefing_3'))
        dispatcher.add_handler(CallbackQueryHandler(briefing_4, pattern='briefing_4'))
        dispatcher.add_handler(CallbackQueryHandler(briefing_5, pattern='briefing_5'))
        dispatcher.add_handler(CallbackQueryHandler(briefing_6, pattern='briefing_6'))
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


        updater.start_polling()
        updater.idle()

    run_bot()

telegram_bot()
