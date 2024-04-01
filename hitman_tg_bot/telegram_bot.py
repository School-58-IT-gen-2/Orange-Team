import pickle
import os
import sys
import random
import time as tm

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup,ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, PollAnswerHandler, PollHandler

from dotenv import load_dotenv
load_dotenv()

from model.hokkaido_values import *
from model.player.player_info import *
from model.player.player import Player


adapter = HitmanAdapter()
tg_token = os.getenv("TELEGRAM_TOKEN")


#Начало создания ТГ бота
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

users = {}
logger = logging.getLogger(__name__)
message = -1
player = Player()

def telegram_bot():
    """Запуск ТГ бота"""

    #Часто используемые функции

    def location_status(location: Location) -> str:
        result_string = f'{location.name}\n'
        location_npcs = find_location_npcs(location)
        location_disguises = []
        for i in location_npcs:
            location_disguises.append(i.disguise.name)
        if location_witnesses(location) > 0:
            result_string += '\nНа локации находятся:\n'
            for i in list(targets.values()):
                if i.move() == location.name:
                    result_string += f'\n{i.name}\n'
            if location.witnesses > 0:
                result_string += f'\n{location.witnesses} Пациент'
            for i in list(disguises.values()):
                if i.name in location_disguises:
                    result_string += f'\n{location_disguises.count(i.name)} {i.name}'
            return result_string
        else:
            result_string += '\nНа локации никого нет'
            return result_string
        
    def find_location_npcs(location: Location) -> list:
        location_npcs = []
        for i in list(npcs.values()):
            if i.move() == location.name and i.alive == True:
                location_npcs.append(i)
        return location_npcs

    def find_location_everyone(location: Location) -> list:
        location_npcs = []
        for i in list(npcs.values()):
            if i.move() == location.name and i.alive == True:
                location_npcs.append(i)
        for i in list(targets.values()):
            if i.move() == location.name and i.alive == True:
                location_npcs.append(i)
        return location_npcs

    def location_witnesses(location: Location) -> int:
        location_npcs = find_location_npcs(location)
        location_witnesses = location.witnesses
        for i in location_npcs:
            if random.randrange(11) <= i.witness_chance and i.alive == True:
                location_witnesses += 1
        return location_witnesses

    #Меню в игре

    def choose_action_menu(update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='Выберите действие', reply_markup=(choose_action_keyboard()))
        
    def status_menu(update: Update, context: CallbackContext):
        result_string = ''
        for i in list(targets.values()):
            if i.alive == True:
                result_string += f'{i.name}: {i.move()}\n'
            else:
                result_string += f'{i.name}: Цель устранена\n'
        result_string += f'\nТекущая маскировка: {player.disguise.name}\n'
        result_string += f'Предмет в руках: {player.item.name}'
        if int(5-(bodies[0]*0.5)-(kills[0]*0.7)-(combat_count[0]*0.1)-(suspicion_count[0]*0.2)) == 5:
            result_string += f'\n\nБесшумный убийца'
        result_string += '\n\n\n\n' + location_status(player.current_location)
        query = update.callback_query
        query.answer()
        query.edit_message_text(text=result_string, reply_markup=(status_keyboard()))

    def challenges_menu(update: Update, context: CallbackContext):
        query = update.callback_query
        text = ''
        for i in list(challenges.values()):
            if i.completed == False:
                text += i.name + '\n' + i.description + '\n\n'
            else:
                text += i.name + '(выполнено)' +'\n\n'
        text = text[:-1]
        query.answer()
        query.edit_message_text(text=text, reply_markup=challenges_keyboard())
        
    def choose_start_location_menu(update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='Выберите начальную локацию', reply_markup=(choose_start_location_keyboard()))
        
    def choose_start_item_menu_1(update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='Выберите первый предмет снаряжения', reply_markup=(choose_start_item_keyboard()))
        
    def choose_start_item_menu_2(update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='Выберите второй предмет снаряжения', reply_markup=(choose_start_item_keyboard()))
    
    def game_start_menu(update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='Выберите действие', reply_markup=(game_start_keyboard()))

    def choose_pistol_menu(update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='Выберите пистолет', reply_markup=(choose_pistol_keyboard()))

    def safe_move_menu(update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='Выберите локацию', reply_markup=(safe_move_keyboard()))

    def move_menu(update: Update, context: CallbackContext):
        global time
        time[0] += 0.5
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='Выберите локацию', reply_markup=(move_keyboard()))

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
        global time
        time[0] += 1
        query = update.callback_query
        player.inventory += player.current_location.items
        result_string = 'Найдены предметы:\n\n'
        if player.current_location.items == []:
            query.answer()
            query.edit_message_text(text='На локации нет предметов', reply_markup=(loot_keyboard()))
        else:
            for i in list(items.values()):
                if i in player.current_location.items:
                    result_string += f'{i.name} ({player.current_location.items.count(i)})\n'
            query.answer()
            query.edit_message_text(text=result_string, reply_markup=(loot_keyboard()))
        player.current_location.items = []

    def inventory_menu(update: Update, context: CallbackContext):
        query = update.callback_query
        result_string = f'Сейчас в руках: {player.item.name}'
        if player.inventory == []:
            result_string += '\n\nУ вас нет предметов'
        query.answer()
        query.edit_message_text(text=result_string, reply_markup=(inventory_keyboard()))

    def disguise_menu(update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text=f'Текущая маскировка: {player.disguise.name}', reply_markup=(disguise_keyboard()))

    def choose_illegal_item_menu(update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text=f'Вы собираетесь взять нелегальный предмет. Достать предмет?', reply_markup=(choose_illegal_item_keyboard()))

    def combat_start_menu(update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text=f'Начался бой.', reply_markup=(combat_start_keyboard()))

    def choose_weapon_menu(update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text=f'Выберите оружие', reply_markup=(choose_weapon_keyboard()))

    def choose_weapon_action_menu(update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text=f'Выберите действие', reply_markup=(choose_weapon_action_keyboard(query.data)))

    def interact_menu(update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        text = f'Действия видят {location_witnesses(player.current_location)} человек'
        if player.item.usage == []:
            text = '\n\nНет действий с этим предметом'
        else:
            text += '\n\nВыберите действие'
        query.edit_message_text(text=text, reply_markup=(interact_menu_keyboard()))

    def kill_menu(update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='Выберите цель', reply_markup=(kill_keyboard()))
        
    def knock_out_menu(update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='Выберите цель', reply_markup=(knock_out_keyboard()))

    #Клавиатуры для меню

    def safe_move_keyboard():
        keyboard = make_keyboard(player.current_location.connected_locations, 'safe_move')
        keyboard.append([InlineKeyboardButton("Отменить действие", callback_data='Выбор действия')])
        return InlineKeyboardMarkup(keyboard)
    
    def move_keyboard():
        keyboard = make_keyboard(player.current_location.connected_locations, 'basic_move')
        keyboard.append([InlineKeyboardButton("Отменить действие", callback_data='Выбор действия')])
        return InlineKeyboardMarkup(keyboard)

    def choose_pistol_keyboard():
        return InlineKeyboardMarkup(make_keyboard(['Пистолет с глушителем', 'Пистолет без глушителя'], 'choose_pistol'))

    def status_keyboard():
        return InlineKeyboardMarkup([[InlineKeyboardButton("Выйти", callback_data='Выбор действия')]])

    def choose_action_keyboard():
        actions = [
            "Передвижение",
            "Взаимодействие",
            "Инвентарь",
            "Обыскать локацию",
            "Статус",
            "Испытания",
            "Сохранить и выйти"
        ]
        return InlineKeyboardMarkup(make_keyboard(actions, ''))
    
    def challenges_keyboard():
        return InlineKeyboardMarkup([[InlineKeyboardButton("Выйти", callback_data='Выбор действия')]])
    
    def choose_start_location_keyboard():
        options = []
        for i in range(1, 10):
            if i <= player_lvl[0] // 10:
                options.append(lvl_unlocks[i][0])
        return InlineKeyboardMarkup(make_keyboard(options, 'choose_start_location'))
    
    def choose_start_item_keyboard():
        return InlineKeyboardMarkup(make_keyboard(carry_on_items, 'CSI'))
    
    def game_start_keyboard():
        return InlineKeyboardMarkup([[InlineKeyboardButton("Начать игру", callback_data="Начало игры")]])

    def attack_keyboard(npc=None, location=None):
        return InlineKeyboardMarkup([[InlineKeyboardButton(f"Напасть (3/10)", callback_data=f"НПД{npc.name}:{location.name}")], [InlineKeyboardButton("Уйти", callback_data=f"Выбор действия")]])
    
    def hide_keyboard(npc=None, location=None):
        return InlineKeyboardMarkup([[InlineKeyboardButton(f"Напасть (3/10)", callback_data=f"НПД{npc.name}:{location.name}")], [InlineKeyboardButton("Скрыться (7/10)", callback_data=f"Скрыться")]])

    def no_disguise_move_keyboard(chance, location):
        return InlineKeyboardMarkup([[InlineKeyboardButton(f"Да ({10-chance}/10)", callback_data=f"ПРТ{10 - chance}:{location.name}")], [InlineKeyboardButton("Нет", callback_data=f"Передвижение")]])

    def loot_keyboard():
        return InlineKeyboardMarkup([[InlineKeyboardButton(f"Выйти", callback_data=f"Выбор действия")]])

    def inventory_keyboard():
        inventory = []
        if player.inventory.count(player.item) == 0:
            player.item = items['Нет предмета']
        for i in player.inventory:
            if i.name == 'Пистолет без глушителя' or i.name == 'Пистолет с глушителем':
                inventory.append(i.name + ' (1)')
            else:
                inventory.append(i.name + ' (' + str(player.inventory.count(i)) + ')')
        inventory = list(set(inventory))
        inventory.append('Убрать предмет из рук')
        inventory.append(player.disguise.name)
        keyboard = make_keyboard(inventory, '')
        keyboard.append([InlineKeyboardButton(f"Выйти", callback_data=f"Выбор действия")])
        return InlineKeyboardMarkup(keyboard)

    def disguise_keyboard():
        return InlineKeyboardMarkup(make_keyboard([i.name for i in player.found_disguises], 'МСК'))

    def choose_illegal_item_keyboard():
        return InlineKeyboardMarkup([[InlineKeyboardButton('Да', callback_data='ВНО')], [InlineKeyboardButton(f"Нет", callback_data=f"Инвентарь")]])

    def choose_weapon_keyboard():
        weapons = ['Нет предмета']
        for i in player.inventory:
            if i.weapon:
                weapons.append(i.name)
        return InlineKeyboardMarkup(make_keyboard(weapons, 'WP'))

    def combat_start_keyboard():
        return InlineKeyboardMarkup([[InlineKeyboardButton('Прятаться (5/10)', callback_data='Прятаться')], [InlineKeyboardButton(f"Напасть", callback_data=f"Напасть")]])
    
    def choose_weapon_action_keyboard(item_name):
        actions = []
        current_weapon = items[item_name.replace('WP', '')]
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
        player.item = current_weapon
        keyboard = make_keyboard(actions, 'CWA')
        keyboard.append([InlineKeyboardButton('Назад', callback_data='Выбор оружия')])
        return InlineKeyboardMarkup(keyboard)

    def interact_menu_keyboard():
        keyboard = [[InlineKeyboardButton(f"Назад", callback_data=f"Выбор действия")]]
        if player.item.usage == []:
            return InlineKeyboardMarkup(keyboard)
        return InlineKeyboardMarkup(make_keyboard(player.item.usage, 'ITR') + keyboard)

    def kill_keyboard():
        location_npcs = []
        for i in find_location_everyone(player.current_location):
            location_npcs.append(i.name)
        keyboard = make_keyboard(location_npcs, 'KILL')
        keyboard.append([InlineKeyboardButton(f"Отменить действие", callback_data=f"Взаимодействие")])
        return InlineKeyboardMarkup(keyboard)

    def knock_out_keyboard():
        location_npcs = []
        for i in find_location_npcs(player.current_location):
            location_npcs.append(i.name)
        keyboard = make_keyboard(location_npcs, 'KNOCK')
        keyboard.append([InlineKeyboardButton(f"Отменить действие", callback_data=f"Взаимодействие")])
        return InlineKeyboardMarkup(keyboard)

    def make_keyboard(options, func_name):
        keyboard = []
        for i in range(len(options)):
            keyboard.append([InlineKeyboardButton(f"{options[i]}", callback_data=options[i] + func_name)])
        return keyboard

    #Проверка query для меню

    def is_basic_move(query):
        return 'basic_move' in query

    def is_start_location(query):

        global start_location
        global start_disguise

        location = False
        for i in list(lvl_unlocks.values()):
            if i[0] == query.replace('choose_start_location', ''):
                location = True
                start_location = i[1]
                start_disguise = i[2]
        return location
    
    def is_start_item_1(query):
        
        global start_items

        if 'CSI' in query:
            query = query.replace('CSI', '')
            if len(carry_on_items) == 6:
                start_items.append(items[query])
                if query == 'Монета':
                    start_items.append(items[query])
                    start_items.append(items[query])
                carry_on_items.remove(query)
                return True
        return False
    
    def is_start_item_2(query):
        
        global start_items

        if 'CSI' in query:
            query = query.replace('CSI', '')
            if len(carry_on_items) == 5:
                start_items.append(items[query])
                if query == 'Монета':
                    start_items.append(items[query])
                    start_items.append(items[query])
                carry_on_items.append(start_items[0].name)
                return True
        return False
    
    def is_pistol(query):
        if 'choose_pistol' in query:
            start_items.append(items[query.replace('choose_pistol', '')])
            return True
        return False

    def is_safe_move(query):
        return 'safe_move' in query
    
    def is_npc_attack(query):
        return "НПД" in query

    def is_hide(query):
        return query == 'Скрыться'

    def is_no_disguise_move(query):
        return 'ПРТ' in query

    def is_disguise_menu(query):
        return query == player.disguise.name

    def is_change_disguise(query):
        return 'МСК' in query

    def is_remove_item(query):
        return query == 'Убрать предмет из рук'
    
    def is_choose_legal_item(query):
        if query[:-4] in list(items.keys()):
            return items[query[:-4]].legal
        return False
    
    def is_choose_illegal_item(query):
        global illegal_item
        if query[:-4] in list(items.keys()):
            if items[query[:-4]].legal == False:
                illegal_item = query[:-4]
                return True
        return False
    
    def is_take_illegal_item(query):
        return query == 'ВНО'

    def is_hide_combat(query):
        return query == 'Прятаться'
    
    def is_attack_combat(query):
        return query == 'Напасть'
    
    def is_choose_weapon(query):
        return 'WP' in query
    
    def is_choose_weapon_action(query):
        return 'CWA' in query

    def is_interact_lethal(query):
        global thrown_weapon
        if 'Бросить' in query:
            thrown_weapon = True
        return 'ITR' in query and ('летально' in query or 'Выстрелить' in query or 'Задушить' in query)
    
    def is_interact_non_lethal(query):
        global thrown_weapon
        if 'Бросить' in query:
            thrown_weapon = True
        return 'ITR' in query and ('летально' in query or 'Выстрелить' in query or 'Задушить' in query) == False
    
    def is_kill(query):
        return 'KILL' in query
    
    def is_knock_out(query):
        return 'KNOCK' in query
    

    #Механики игры

    def knock_out(update: Update, context: CallbackContext):
        global bodies
        global thrown_weapon
        global time
        time[0] += 1
        query = update.callback_query
        data = query.data.replace('KNOCK', '')
        target = npcs[data]
        player.found_disguises.append(target.disguise)
        if thrown_weapon:
            player.inventory.remove(player.item)
            thrown_weapon = False
        target.alive = False
        if location_witnesses(player.current_location) > 0:
            bodies[0] += 1
            combat(update=update, context=context)
        else:
            query.answer()
            query.edit_message_text(text=f'Цель устранена: {target.name}', reply_markup=(choose_action_keyboard()))

    def kill(update: Update, context: CallbackContext):
        global kills
        global bodies
        global thrown_weapon
        global time
        time[0] += 1
        query = update.callback_query
        data = query.data.replace('KILL', '')
        if data in list(npcs.keys()):
            target = npcs[data]
            player.found_disguises.append(target.disguise)
            kills[0] += 1
        else:
            target = targets[data]
            if data == 'Erich Soders' and (player.item.name == 'Пистолет без глушителя' or player.item.name == 'Пистолет с глушителем'):
                context.bot.send_message(chat_id=update.effective_chat.id, text=challenges['Личное прощание'].achieved())
            context.bot.send_message(chat_id=update.effective_chat.id, text=target.kill())
        target.alive = False
        if location_witnesses(player.current_location) > 0:
            bodies[0] += 1
            combat(update=update, context=context)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f'Цель устранена: {target.name}', reply_markup=(choose_action_keyboard()))

    def combat_chance(update: Update, context: CallbackContext):
        global kills
        global bodies
        query = update.callback_query
        chance = int(query.data.replace('CWA', '')[-5])
        if random.randrange(1, 11) <= chance:
            if player.item.lethal:
                kills[0] += 1
            enemies = []
            for i in find_location_npcs(player.current_location):
                if i.guard:
                    enemies.append(i)
            if enemies != []:
                enemies[0].alive = False
            if location_witnesses(player.current_location) > 0:
                bodies[0] += 1
            if 'Бросить' in query.data:
                player.current_location.items.append(player.item)
                player.inventory.remove(player.item)
            combat(update=update, context=context)
        else:
            if 'Бросить' in query.data:
                player.current_location.items.append(player.item)
                player.inventory.remove(player.item)
            player.health -= 25
            combat(update=update, context=context)

    def hide_combat(update: Update, context: CallbackContext):
        global time
        query = update.callback_query
        if random.randrange(1, 11) <= 5:
            player.compromised_disguises.append(player.disguise)
            query.answer()
            query.edit_message_text(text='Ваша маскировка раскрыта, при перемещении в любую локацию вас будут узнавать.', reply_markup=(choose_action_keyboard()))
        else:
            query.answer()
            query.edit_message_text(text='Вы умерли. Миссия провалена.')
            time[0] = 0

    def choose_illegal_item(update: Update, context: CallbackContext):
        query = update.callback_query
        player.item = items[illegal_item]
        query.answer()
        query.edit_message_text(text=f'Сейчас в руках: {player.item.name}', reply_markup=(choose_action_keyboard()))

    def choose_legal_item(update: Update, context: CallbackContext):
        query = update.callback_query
        player.item = items[query.data[:-4]]
        query.answer()
        query.edit_message_text(text=f'Сейчас в руках: {player.item.name}', reply_markup=(choose_action_keyboard()))

    def remove_item(update: Update, context: CallbackContext):
        query = update.callback_query
        player.item = items['Нет предмета']
        query.answer()
        query.edit_message_text(text=f'Сейчас в руках: {player.item.name}', reply_markup=(choose_action_keyboard()))

    def change_disguise(update: Update, context: CallbackContext):
        query = update.callback_query
        disguise_choice = query.data.replace('МСК', '')
        player.disguise = disguises[disguise_choice]
        query.answer()
        query.edit_message_text(text=f'Текущая маскировка: {player.disguise.name}', reply_markup=(choose_action_keyboard()))

    def hide(update: Update, context: CallbackContext):
        query = update.callback_query
        if random.randrange(1, 11) <= 7:
            player.compromised_disguises.append(player.disguise)
            query.answer()
            query.edit_message_text(text='Ваша маскировка раскрыта, при перемещении в любую локацию вас будут узнавать.', reply_markup=(choose_action_keyboard()))
        else:
            query.answer()
            query.edit_message_text(text=f'Начался бой.', reply_markup=(combat_start_keyboard()))

    def no_disguise_move(update: Update, context: CallbackContext):
        query = update.callback_query
        chance = int(query.data.replace('ПРТ', '').split(':')[0])
        move_to_location = locations[query.data.replace('ПРТ', '').split(':')[1]]
        if random.randrange(1, 11) <= chance:
            player.compromised_disguises.append(player.disguise)
            player.current_location = move_to_location
            query.answer()
            query.edit_message_text(text=location_status(player.current_location), reply_markup=(choose_action_keyboard()))
        else:
            locations_npcs = find_location_npcs(move_to_location)
            location_npc = locations_npcs[random.randrange(len(locations_npcs))]
            query.answer()
            query.edit_message_text(text=location_npc.suspicion(), reply_markup=attack_keyboard(location_npc, move_to_location))

    def attack_npc(update: Update, context: CallbackContext):
        query = update.callback_query
        npc = npcs[query.data.replace('НПД', '').split(':')[0]]
        move_to_location = locations[query.data.replace('НПД', '').split(':')[1]]
        if random.randrange(1, 11) <= 3:
            player.current_location = move_to_location
            npc.alive = False
            player.found_disguises.append(npc.disguise)
            query.answer()
            query.edit_message_text(text=f'Вам удалось тихо устранить {npc.name}', reply_markup=(choose_action_keyboard()))
        else:
            query.answer()
            query.edit_message_text(text=f'Начался бой.', reply_markup=(combat_start_keyboard()))

    def move(update: Update, context: CallbackContext):
        query = update.callback_query
        move_to_location = locations[query.data.replace('basic_move', '')]
        #Случай, когда для входа нужна маскировка или ключ-карта
        if move_to_location.name == 'Комната с серверами':
            if player.disguise.name == 'Директор клиники' or items['Ключ-карта'] in player.inventory or items['Электронный дешифровщик'] in player.inventory:
                player.current_location = move_to_location
                query.answer()
                query.edit_message_text(text=location_status(player.current_location), reply_markup=(choose_action_keyboard()))
            else:
                query.answer()
                query.edit_message_text(text='Для входа необходима маскировка директора клиники или ключ-карта', reply_markup=move_keyboard())
        elif player.disguise in player.compromised_disguises:
            #Случай, когда маскировка игрока раскрыта
            locations_npcs = find_location_npcs(player.current_location)
            if locations_npcs != []:
                location_npc = locations_npcs[random.randrange(len(locations_npcs))]
                query.answer()
                query.edit_message_text(text=location_npc.suspicion(), reply_markup=attack_keyboard(location_npc, move_to_location))
            else:
                player.current_location = move_to_location
                query.answer()
                query.edit_message_text(text=location_status(player.current_location), reply_markup=choose_action_keyboard())
        elif (player.item.legal == False and player.disguise.name != 'Охранник' and player.disguise.name != 'Телохранитель'):
            #Случай, когда в руках игрока нелегальный предмет
            player.current_location = move_to_location
            if find_location_npcs(player.current_location) != []:
                location_npc = find_location_npcs(player.current_location)[random.randrange(len(find_location_npcs(player.current_location)))]
                suspicion_count[0] += 1
                query.answer()
                query.edit_message_text(text=f'{location_npc.name} ({location_npc.disguise.name}): Он вооружен!', reply_markup=hide_keyboard(location_npc, player.current_location))
        elif player.disguise in move_to_location.disguise:
            #Случай, когда маскировка игрока позволяет пройти на локацию
            player.current_location = move_to_location
            query.answer()
            query.edit_message_text(text=location_status(player.current_location), reply_markup=choose_action_keyboard())
        else:
            #Случай, когда маскировка игрока не позволяет пройти на локацию
            chance = min(10, location_witnesses(player.current_location))
            query.answer()
            query.edit_message_text(text='У вас нет подходящей маскировки. Переместиться на локацию?', reply_markup=(no_disguise_move_keyboard(chance=chance, location=move_to_location)))

    def combat(update: Update, context: CallbackContext):
        global kills
        global bodies
        global player_lvl
        global combat_count
        global time
        time[0] += 1
        combat_count[0] += 1
        enemies = []
        query = update.callback_query

        for i in find_location_npcs(player.current_location):
            if i.guard:
                enemies.append(i)
            
        if player.health == 0:
            query.answer()
            query.edit_message_text(text='Вы умерли. Миссия провалена.')
            time[0] = 0
        
        #Проверяет то, что на локации есть охранники
        if enemies == []:
            player.health = 100
            query.answer()
            query.edit_message_text(text=f'Бой закончился.\n\nУбито невинных: {kills[0]}\nНайдено тел: {bodies[0]}', reply_markup=(choose_action_keyboard()))
        else:
            query.answer()
            query.edit_message_text(text=f'Выберите оружие', reply_markup=(choose_weapon_keyboard()))

    def safe_move(update: Update, context: CallbackContext):
        query = update.callback_query
        player.current_location = locations[query.data.replace('safe_move', '')]
        query.answer()
        query.edit_message_text(text=location_status(player.current_location), reply_markup=(choose_action_keyboard()))

    def spawn_player(update: Update, context: CallbackContext):
        global start_location
        global start_items
        global start_disguise
        player.current_location = start_location
        player.inventory = start_items
        start_items = []
        player.found_disguises = [start_disguise]
        player.item = items['Нет предмета']
        player.compromised_disguises = []
        player.disguise = start_disguise
        start_disguise = ''
        text = 'Диана: Добро пожаловать на Хоккайдо, 47-й. Частная клиника «Гама» оказывает медицинские услуги высочайшего уровня представителям мировой элиты, выходя при необходимости за рамки закона\n\n Частично здание находится под управлением искусственного интеллекта — KAI. Система контролирует доступ пациентов в разные части клиники и даже принимает участие в ряде медицинских процедур.\n\nЭрих Содерс уже находится в операционной, где он проходит предварительную подготовку с применением стволовых клеток. Это крайне противоречивая процедура ещё не одобрена властями Японии.\n\nЮки Ямадзаки уже прибыла. Она находится либо в своём номере, либо в ресторане, либо в спа-зоне клиники. Содерсу скоро введут наркоз. Сделай так, чтобы он больше никогда не проснулся. Удачи, 47-й.'
        if start_location.name == 'Номер 47-го':
            query = update.callback_query
            query.answer()
            query.edit_message_text(text=text)
            context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите действие', reply_markup=(choose_action_keyboard()))
        else:
            query = update.callback_query
            query.answer()
            query.edit_message_text(text='Выберите действие', reply_markup=(choose_action_keyboard()))
        start_location = ''

    #Команды бота

    def help(update: Update, context: CallbackContext):

        global message

        if update.message['message_id'] != message:
            message = update.message['message_id']
            updated = int(tm.time())
            
        adapter.update_by_id("Users", f'updated={updated}', user_id)
        
        update.message.reply_text(
            'Обучение:\n\nПередвежение – перемещение по локациям игры. Иногда данное действие требует некоторых условий, таких как нужной маскировки или небходимого предмета.\n\nВзаимодействие – использование текущего предмета. Может являться нелегальным действием.\n\nИнвентарь – открытие меню с вашими предметами и текущей маскировкой.\n\nОбыскать локацию – добавляет все предметы на текущей локации вам в инвентарь.\n\nСтатус – показывает нахождение целей задания, а также состояние текущей локации.\n\nИспытания – открывает список со всеми испытаниями. Выполненные испытания отмечаются отдельно.\n\nСохранить и выйти – завершает игру, сохраняя текущие выполненные испытания, а также уровень игрока.\n\nУровень игрока – за выполнение испытаний, а также прохождения уровня на высокий рейтинг у вас будут появляться новые стартовые локации, а также появится возможность брать с собой снаряжение.\n\nРейтинг задания – убийство невинных, количество найденных тел и раз, когда вас заметили, а также когда вы вступили в бой – всё это снижает рейтинг прохождения.'
        )

    def start(update: Update, context: CallbackContext):
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
        
    def begin(update: Update, context: CallbackContext):

        global message

        if update.message['message_id'] != message:
            message = update.message['message_id']
            updated = int(tm.time())
            
        adapter.update_by_id("Users", f'updated={updated}', user_id)
        text = 'Брифинг:\n\nДиана: Доброе утро, 47-й. Совет директоров одобрил ликвидацию Эриха Содерса. После Колорадо мы решили пристально изучить личные дела Содерса и выяснили, что его недавно доставили в частную клинику «Гама» на японском острове Хоккайдо для срочной операции на сердце. Без «Провиденс» тут явно не обошлось.\n\nСодерс страдает от редкой врожденной патологии — транспозиции органов: его внутренние органы в теле расположены зеркально. Для трансплантации ему необходимо правостороннее сердце, и он явно предал МКА, чтобы получить его. Его приняли прошлой ночью и сейчас он готовится к трёхэтапной операции.\n\nПод видом Тобиаса Рипера, крупного бизнесмена, ты отправляешься в «Гаму» для стандартного медицинского обследования, о формальностях мы уже позаботились. В таких условиях придётся импровизировать и самостоятельно добывать снаряжение.\n\nКроме того, тебе нужно ликвидировать Юки Ямадзаки — она адвокат из Токио, работает на «Провиденс». Содерс уже передал Ямадзаки доступ к нашей базе клиентов и согласился предоставить полный список оперативных сотрудников МКА после завершения операции. Этого допустить никак нельзя. Содерс должен заплатить за своё предательство — это послужит хорошим уроком его нанимателям. На кону будущее и репутация МКА. Какой бы властью и могуществом ни обладала «Провиденс», пора поставить их на место. Я оставлю тебя подготавливаться.'
        update.message.reply_text(text=text, reply_markup=choose_start_location_keyboard())

    def run_bot():

        updater = Updater(tg_token)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler('start', start))
        dispatcher.add_handler(CommandHandler('help', help))
        dispatcher.add_handler(CommandHandler('begin', begin))

        dispatcher.add_handler(CallbackQueryHandler(choose_action_menu, pattern='Выбор действия'))
        dispatcher.add_handler(CallbackQueryHandler(challenges_menu, pattern='Испытания'))
        dispatcher.add_handler(CallbackQueryHandler(status_menu, pattern='Статус'))
        dispatcher.add_handler(CallbackQueryHandler(choose_start_location_menu, pattern='Выбор начальной локации'))
        dispatcher.add_handler(CallbackQueryHandler(choose_pistol_menu, pattern=is_start_location))
        dispatcher.add_handler(CallbackQueryHandler(choose_start_item_menu_1, pattern=is_pistol))
        dispatcher.add_handler(CallbackQueryHandler(choose_start_item_menu_2, pattern=is_start_item_1))
        dispatcher.add_handler(CallbackQueryHandler(game_start_menu, pattern=is_start_item_2))
        dispatcher.add_handler(CallbackQueryHandler(spawn_player, pattern='Начало игры'))
        dispatcher.add_handler(CallbackQueryHandler(safe_move, pattern=is_safe_move))
        dispatcher.add_handler(CallbackQueryHandler(move, pattern=is_basic_move))
        dispatcher.add_handler(CallbackQueryHandler(move_menu, pattern='Передвижение'))
        dispatcher.add_handler(CallbackQueryHandler(attack_menu, pattern='Выбор нападения'))
        dispatcher.add_handler(CallbackQueryHandler(attack_npc, pattern=is_npc_attack))
        dispatcher.add_handler(CallbackQueryHandler(hide_menu, pattern='Напасть или бежать'))
        dispatcher.add_handler(CallbackQueryHandler(hide, pattern=is_hide))
        dispatcher.add_handler(CallbackQueryHandler(no_disguise_move_menu, pattern='Перемещение без маскировки'))
        dispatcher.add_handler(CallbackQueryHandler(no_disguise_move, pattern=is_no_disguise_move))
        dispatcher.add_handler(CallbackQueryHandler(loot_menu, pattern='Обыскать локацию'))
        dispatcher.add_handler(CallbackQueryHandler(inventory_menu, pattern='Инвентарь'))
        dispatcher.add_handler(CallbackQueryHandler(disguise_menu, pattern=is_disguise_menu))
        dispatcher.add_handler(CallbackQueryHandler(change_disguise, pattern=is_change_disguise))
        dispatcher.add_handler(CallbackQueryHandler(remove_item, pattern=is_remove_item))
        dispatcher.add_handler(CallbackQueryHandler(choose_legal_item, pattern=is_choose_legal_item))
        dispatcher.add_handler(CallbackQueryHandler(choose_illegal_item_menu, pattern=is_choose_illegal_item))
        dispatcher.add_handler(CallbackQueryHandler(choose_illegal_item, pattern=is_take_illegal_item))
        dispatcher.add_handler(CallbackQueryHandler(combat_start_menu, pattern='Бой'))
        dispatcher.add_handler(CallbackQueryHandler(hide_combat, pattern=is_hide_combat))
        dispatcher.add_handler(CallbackQueryHandler(combat, pattern=is_attack_combat))
        dispatcher.add_handler(CallbackQueryHandler(choose_weapon_menu, pattern='Выбор оружия'))
        dispatcher.add_handler(CallbackQueryHandler(choose_weapon_action_menu, pattern=is_choose_weapon))
        dispatcher.add_handler(CallbackQueryHandler(combat_chance, pattern=is_choose_weapon_action))
        dispatcher.add_handler(CallbackQueryHandler(interact_menu, pattern='Взаимодействие'))
        dispatcher.add_handler(CallbackQueryHandler(kill_menu, pattern=is_interact_lethal))
        dispatcher.add_handler(CallbackQueryHandler(knock_out_menu, pattern=is_interact_non_lethal))
        dispatcher.add_handler(CallbackQueryHandler(kill, pattern=is_kill))
        dispatcher.add_handler(CallbackQueryHandler(knock_out, pattern=is_knock_out))

        updater.start_polling()
        updater.idle()

    run_bot()

telegram_bot()
def f():
    if self.player.item.name == 'Пульт для управления нейрочипом':
        if self.player.current_location.get_name() == 'Морг':
            self.player.inventory.remove(self.player.item)
            self.player_view.response('Нейрочип подействовал на одного из работников морга и тот отправился в комнату, где хранится сердце, которое должны пересадить Эриху Содерсу. Последовать за ним?\n\n1. Да\n2. Нет')
            request = self.player_view.request()
            while request.isdigit() == False:
                self.player_view.response('Введите номер ответа')
                request = self.player_view.request()
            request = int(request)
            if request == 2:
                return self.player_view.response(self.locator.location_status(self.player.current_location))
            elif request == 1:
                self.player_view.response('\n\n1. Выйти\n2. Повредить сердце')
                request = self.player_view.request()
                while request.isdigit() == False:
                    self.player_view.response('Введите номер ответа')
                    request = self.player_view.request()
                request = int(request)
                if request == 1:
                    return self.player_view.response(self.locator.location_status(self.player.current_location))
                elif request == 2:
                    self.locator.get_targets().get_by_name('Эрих Содерс').alive = False
                    self.player_view.response(f'{self.locator.get_challenges().get_by_name('Бессердечный').achieved()}')
                    result_string = 'Диана: 47-й, без сердца для пересадки Содерс не выживет. Ты смог от него избавиться даже не прикасаясь, изящный ход.'
                    self.player_view.response(result_string)
                    return self.player_view.response(self.locator.location_status(self.player.current_location))
        else:
            return self.player_view.response('Вне зоны действия')
        
def f():
    #Бросок предмета, отвлекающего NPC
    if self.player.item.usage[request - 1] == 'Бросить для отвлечения':
        if location_npcs == []:
                return self.player_view.response('На локации никого нет')
        if witnesses > 3:
            self.player_view.response('На локации слишком много свидетелей\n\n1. Отвлечь для перемещения\n2. Отменить действие')
            request = self.player_view.request()
            while request.isdigit() == False:
                self.player_view.response('Введите номер ответа')
                request = self.player_view.request()
            request = int(request)
            if request == 1:
                self.player.inventory.remove(self.player.item)
                if self.player.item == self.locator.get_items().get_by_name('Монета'):
                    self.player.current_location.set_items(self.player.current_location.get_items() + [self.player.item])
                return self.safe_move()
            else:
                return self.player_view.response(self.locator.location_status(self.player.current_location))
        if self.player.item == self.locator.get_items().get_by_name('Монета'):
            self.player.current_location.set_items(self.player.current_location.get_items() + [self.player.item])
        self.player.inventory.remove(self.player.item)
        result_string = ''
        for i in range(len(location_npcs)):
                result_string += f'{i+1}. Отвлечь {location_npcs[i].get_name()}\n'
        result_string += f'{len(location_npcs)+1}. Отвлечь для перемещения'
        self.player_view.response(result_string)
        request = self.player_view.request()
        while request.isdigit() == False:
            self.player_view.response('Введите номер ответа')
            request = self.player_view.request()
        request = int(request)
        if request > len(location_npcs):
            return self.safe_move()
        else:
            self.player_view.response(f'1. Вырубить {location_npcs[request - 1].get_name()}\n2. Убить {location_npcs[request - 1].get_name()}')
            second_request = self.player_view.request()
            while second_request.isdigit() == False:
                self.player_view.response('Введите номер ответа')
                second_request = self.player_view.request()
            second_request = int(second_request)
            self.player.found_disguises.append(location_npcs[request - 1].get_disguise())
            location_npcs[request - 1].alive = False
            if second_request == 1:
                return self.player_view.response(self.locator.location_status(self.player.current_location))
            elif second_request == 2:
                kills[0] += 1
                return self.player_view.response(self.locator.location_status(self.player.current_location))