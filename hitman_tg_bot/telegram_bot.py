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
                text += i.name + ' (выполнено)' +'\n\n'
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

    def distract_menu(update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        text = 'Выберите, кого вы хотите отвлечь'
        if find_location_npcs(player.current_location) == []:
            text = 'На локации никого нет'
        if location_witnesses(player.current_location) > 3:
            text = 'На локации слишком много свидетелей'
        query.edit_message_text(text=text, reply_markup=(distract_keyboard()))

    def confirm_kill_menu(update: Update, context: CallbackContext):
        query = update.callback_query
        npc_name = query.data.replace('KILL', '')
        if npc_name in list(npcs.keys()):
            npc = npcs[npc_name]
            query.answer()
            query.edit_message_text(text=f'{npc.name} ({npc.disguise.name})', reply_markup=(confirm_kill_keyboard(query.data)))
        else:
            npc = targets[npc_name]
            query.answer()
            query.edit_message_text(text=f'{npc.name}', reply_markup=(confirm_kill_keyboard(query.data)))

    def confirm_knock_menu(update: Update, context: CallbackContext):
        query = update.callback_query
        npc = npcs[query.data.replace('KNOCK', '')]
        query.answer()
        query.edit_message_text(text=f'{npc.name} ({npc.disguise.name})', reply_markup=(confirm_knock_keyboard(query.data)))

    def confirm_distract_menu(update: Update, context: CallbackContext):
        query = update.callback_query
        npc = npcs[query.data.replace('DIS', '')]
        query.answer()
        query.edit_message_text(text=f'{npc.name} ({npc.disguise.name})', reply_markup=(confirm_distract_keyboard(query.data)))

    def destroy_heart_menu_1(update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='Нейрочип подействовал на одного из работников морга и тот отправился в комнату, где хранится сердце, которое должны пересадить Эриху Содерсу.\n\nПоследовать за ним?', reply_markup=(destroy_heart_keyboard_1()))

    def destroy_heart_menu_2(update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='Выберите действие', reply_markup=(destroy_heart_keyboard_2()))

    #Клавиатуры для меню

    def safe_move_keyboard():
        keyboard = make_keyboard(player.current_location.connected_locations, 'SM')
        keyboard.append([InlineKeyboardButton("Отменить действие", callback_data='Взаимодействие')])
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
        location_disguises = []
        for i in find_location_npcs(player.current_location):
            location_disguises.append(i.disguise.name)
            location_npcs.append(i.name)
        for i in list(targets.values()):
            if i.move() == player.current_location.name and i.alive == True:
                location_disguises.append(i.name)
                location_npcs.append(i.name)
        keyboard = []
        for i in range(len(location_npcs)):
            keyboard.append([InlineKeyboardButton(f"{location_disguises[i]}", callback_data=location_npcs[i] + 'KILL')])
        keyboard.append([InlineKeyboardButton(f"Отменить действие", callback_data=f"Взаимодействие")])
        return InlineKeyboardMarkup(keyboard)

    def knock_out_keyboard():
        location_npcs = []
        location_disguises = []
        for i in find_location_npcs(player.current_location):
            location_disguises.append(i.disguise.name)
            location_npcs.append(i.name)
        keyboard = []
        for i in range(len(location_npcs)):
            keyboard.append([InlineKeyboardButton(f"{location_disguises[i]}", callback_data=location_npcs[i] + 'KNOCK')])
        keyboard.append([InlineKeyboardButton(f"Отменить действие", callback_data=f"Взаимодействие")])
        return InlineKeyboardMarkup(keyboard)

    def distract_keyboard():
        if find_location_npcs(player.current_location) == []:
                return InlineKeyboardMarkup([[InlineKeyboardButton("Выйти", callback_data='Взаимодействие')]])
        elif location_witnesses(player.current_location) > 3:
            return InlineKeyboardMarkup([[InlineKeyboardButton("Отвлечь для перемещения", callback_data='safe_move')], [InlineKeyboardButton("Отменить действие", callback_data='Взаимодействие')]])
        else:
            location_npcs = []
            location_disguises = []
            for i in find_location_npcs(player.current_location):
                location_disguises.append(i.disguise.name)
                location_npcs.append(i.name)
            keyboard = []
            for i in range(len(location_npcs)):
                keyboard.append([InlineKeyboardButton(f"{location_disguises[i]}", callback_data=location_npcs[i] + 'DIS')])
            keyboard.append([InlineKeyboardButton("Отвлечь для перемещения", callback_data='safe_move')])
            return InlineKeyboardMarkup(keyboard)
        
    def confirm_kill_keyboard(npc):
        return InlineKeyboardMarkup([[InlineKeyboardButton('Убить', callback_data=npc.replace('KILL', 'con_kill'))], [InlineKeyboardButton('Отменить действие', callback_data=f"Взаимодействие")]])
    
    def confirm_knock_keyboard(npc):
        return InlineKeyboardMarkup([[InlineKeyboardButton('Вырубить', callback_data=npc.replace('KNOCK', 'con_knock'))], [InlineKeyboardButton('Отменить действие', callback_data=f"Взаимодействие")]])
    
    def confirm_distract_keyboard(npc):
        return InlineKeyboardMarkup([[InlineKeyboardButton('Вырубить', callback_data=npc.replace('DIS', 'CDKL'))], [InlineKeyboardButton('Убить', callback_data=npc.replace('DIS', 'CDKN'))], [InlineKeyboardButton('Отменить действие', callback_data=f"Взаимодействие")]])
    
    def destroy_heart_keyboard_1():
        return InlineKeyboardMarkup([[InlineKeyboardButton('Да', callback_data='DH1')], [InlineKeyboardButton('Нет', callback_data='Выбор действия')]])
    
    def destroy_heart_keyboard_2():
        return InlineKeyboardMarkup([[InlineKeyboardButton('Повредить сердце', callback_data='DH2')], [InlineKeyboardButton('Уйти', callback_data='Выбор действия')]])

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
        return 'SM' in query
    
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
            if items[query[:-4]].legal == False and player.disguise.name != 'Охранник' and player.disguise.name != 'Телохранитель':
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
    
    def is_destroy_heart_1(query):
        if is_use(query) and player.item.name == 'Пульт для управления нейрочипом' and events['Уничтожить сердце'].completed == False and player.current_location.name == 'Морг':
            events['Уничтожить сердце'].completed = True
            player.inventory.remove(player.item)
            player.item = items['Нет предмета']
            return True
        return False
    
    def is_use_neurochip(query):
        return is_use(query) and player.item.name == 'Пульт для управления нейрочипом' and (events['Уничтожить сердце'].completed == True or player.current_location.name != 'Морг')
    
    def is_destroy_heart_2(query):
        return 'DH1' in query
    
    def is_destroy_heart(query):
        return 'DH2' in query

    #Механики игры

    def rating(update: Update, context: CallbackContext):
        global player_lvl
        query = update.callback_query
        query.answer()
        result_string = f'Тел найдено: {bodies[0]}\n'
        result_string += f'Убито невинных: {kills[0]}\n'
        result_string += f'Вы начали бой {combat_count[0]} раз\n'
        result_string += f'Вы были замечены {suspicion_count[0]} раз'
        rating = max(int(5-(bodies[0]*0.5)-(kills[0]*0.7)-(combat_count[0]*0.1)-(suspicion_count[0]*0.2)), 0)
        result_string += f'Ваш рейтинг: {rating}/5'
        query.edit_message_text(text=result_string)
        if rating == 5 and so[0] == 1:
            if challenges['Бесшумный убийца'].completed == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text=challenges['Бесшумный убийца'].achieved())
        elif rating == 5 and so[0] == 0:
            if challenges['Бесшумный убийца. Только костюм.'].completed == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text=challenges['Бесшумный убийца. Только костюм.'].achieved())
        elif so[0] == 0:
            if challenges['Только костюм'].completed == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text=challenges['Только костюм'].achieved())
        if bodies[0] == 0:
            if challenges['Без улик'].completed == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text=challenges['Без улик'].achieved())
        if challenges['Точный выстрел'].completed == True and challenges['Подержи волосы'].completed == True and challenges['Пианист'].completed == True and challenges['Так можно и пораниться'].completed == True and challenges['Без вкуса, без следа'].completed == True and challenges['Мастер-убийца'].completed == False:
            context.bot.send_message(chat_id=update.effective_chat.id, text=challenges['Мастер-убийца'].achieved())
        player_lvl[0] += rating

    def use_neurochip(update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()
        query.edit_message_text(text='Вне зоны действия', reply_markup=(choose_action_keyboard()))

    def destroy_heart(update: Update, context: CallbackContext):
        targets['Erich Soders'].alive = False
        query = update.callback_query
        query.answer()
        if challenges['Бессердечный'].completed == False:
            query.edit_message_text(text=challenges['Бессердечный'].achieved())
            context.bot.send_message(chat_id=update.effective_chat.id, text='Диана: 47-й, без сердца для пересадки Содерс не выживет. Ты смог от него избавиться даже не прикасаясь, изящный ход.', reply_markup=(choose_action_keyboard()))
        else:
            query.edit_message_text(text='Диана: 47-й, без сердца для пересадки Содерс не выживет. Ты смог от него избавиться даже не прикасаясь, изящный ход.', reply_markup=(choose_action_keyboard()))

    def distract_kill(update: Update, context: CallbackContext):
        global kills
        if player.item.name == 'Монета':
            player.current_location.items.append(player.item)
        player.inventory.remove(player.item)
        query = update.callback_query
        npc_name = query.data.replace('CDKL', '')
        if npc_name in list(npcs.keys()):
            kills[0] += 1
            npc = npcs[npc_name]
            npc.alive = False
            player.found_disguises.append(npc.disguise)
            query.answer()
            query.edit_message_text(text=f'Вы устранили {npc.name}', reply_markup=(choose_action_keyboard()))
        else:
            npc = targets[npc_name]
            npc.alive = False
            query.answer()
            query.edit_message_text(text=npc.kill(), reply_markup=(choose_action_keyboard()))

    def distract_knock_out(update: Update, context: CallbackContext):
        if player.item.name == 'Монета':
            player.current_location.items.append(player.item)
        player.inventory.remove(player.item)
        query = update.callback_query
        npc = npcs[query.data.replace('CDKN', '')]
        npc.alive = False
        player.found_disguises.append(npc.disguise)
        query.answer()
        query.edit_message_text(text=f'Вы вырубили {npc.name}', reply_markup=(confirm_knock_keyboard(query.data)))

    def knock_out(update: Update, context: CallbackContext):
        global bodies
        global thrown_weapon
        global time
        time[0] += 1
        query = update.callback_query
        data = query.data.replace('con_knock', '')
        target = npcs[data]
        player.found_disguises.append(target.disguise)
        if thrown_weapon:
            player.inventory.remove(player.item)
            thrown_weapon = False
        target.alive = False
        if location_witnesses(player.current_location) > 0:
            bodies[0] += 1
            combat(update=update, context=context, start_string=f'Цель устранена: {target.name}\n\n')
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
        data = query.data.replace('con_kill', '')
        if data in list(npcs.keys()):
            target = npcs[data]
            player.found_disguises.append(target.disguise)
            kills[0] += 1
        else:
            target = targets[data]
            if data == 'Erich Soders' and (player.item.name == 'Пистолет без глушителя' or player.item.name == 'Пистолет с глушителем') and challenges['Личное прощание'].completed == False:
                context.bot.send_message(chat_id=update.effective_chat.id, text=challenges['Личное прощание'].achieved())
            context.bot.send_message(chat_id=update.effective_chat.id, text=target.kill())
        target.alive = False
        if location_witnesses(player.current_location) > 0:
            bodies[0] += 1
            combat(update=update, context=context, start_string=f'Цель устранена: {target.name}\n\n', type='add')
        else:
            if data == 'Erich Soders' and (player.item.name == 'Пистолет без глушителя' or player.item.name == 'Пистолет с глушителем'):
                context.bot.send_message(chat_id=update.effective_chat.id, text=f'Цель устранена: {target.name}', reply_markup=(choose_action_keyboard()))
            else:
                query.answer()
                query.edit_message_text(text=f'Цель устранена: {target.name}', reply_markup=(choose_action_keyboard()))

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
            combat(update=update, context=context, start_string=f'Цель устранена: {enemies[0].name}\n\n')
        else:
            if 'Бросить' in query.data:
                player.current_location.items.append(player.item)
                player.inventory.remove(player.item)
            player.health -= 25
            combat(update=update, context=context, start_string='Промах\n\n')

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
        query.answer()
        move_to_location = locations[query.data.replace('basic_move', '')]
        edit = True
        if events['Компьютер в морге'].completed == False and move_to_location.name == 'Морг':
            query.edit_message_text(text='Вы нашли файл на компьютере. Это заметки о Кураторе и его нейрочипе.\n\nВ них приводятся подробные сведения об устройстве чипа и принципе его работы, а также описание того, как изменение дозы влияет на настроение Куратора. Судя по всему, увеличение дозы приводит к улучшению его настроения, а уменьшение, напротив, возвращает его в привычное подавленное состояние.\n\nЧто любопытно, научный сотрудник, похоже, сам менял дозу Куратора без его ведома: для этого он использовал пульт управления чипом, который куратор хранит в своей спальне.')
            events['Компьютер в морге'].completed = True
            edit = False
        #Случай, когда для входа нужна маскировка или ключ-карта
        if move_to_location.name == 'Комната с серверами':
            if player.disguise.name == 'Директор клиники' or items['Ключ-карта'] in player.inventory or items['Электронный дешифровщик'] in player.inventory:
                player.current_location = move_to_location
                if edit:
                    query.edit_message_text(text=location_status(player.current_location), reply_markup=(choose_action_keyboard()))
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=location_status(player.current_location), reply_markup=(choose_action_keyboard()))
            else:
                if edit:
                    query.edit_message_text(text='Для входа необходима маскировка директора клиники или ключ-карта', reply_markup=move_keyboard())
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text='Для входа необходима маскировка директора клиники или ключ-карта', reply_markup=move_keyboard())

        elif player.disguise in player.compromised_disguises:
            #Случай, когда маскировка игрока раскрыта
            locations_npcs = find_location_npcs(player.current_location)
            if locations_npcs != []:
                location_npc = locations_npcs[random.randrange(len(locations_npcs))]
                if edit:
                    query.edit_message_text(text=location_npc.suspicion(), reply_markup=attack_keyboard(location_npc, move_to_location))
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=location_npc.suspicion(), reply_markup=attack_keyboard(location_npc, move_to_location))
            else:
                player.current_location = move_to_location
                if edit:
                    query.edit_message_text(text=location_status(player.current_location), reply_markup=choose_action_keyboard())
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=location_status(player.current_location), reply_markup=choose_action_keyboard())
        elif (player.item.legal == False and player.disguise.name != 'Охранник' and player.disguise.name != 'Телохранитель'):
            #Случай, когда в руках игрока нелегальный предмет
            player.current_location = move_to_location
            if find_location_npcs(player.current_location) != []:
                location_npc = find_location_npcs(player.current_location)[random.randrange(len(find_location_npcs(player.current_location)))]
                suspicion_count[0] += 1
                if edit:
                    query.edit_message_text(text=f'{location_npc.name} ({location_npc.disguise.name}): Он вооружен!', reply_markup=hide_keyboard(location_npc, player.current_location))
                else:
                    context.bot.send_message(chat_id=update.effective_chat.id, text=f'{location_npc.name} ({location_npc.disguise.name}): Он вооружен!', reply_markup=hide_keyboard(location_npc, player.current_location))
        elif player.disguise in move_to_location.disguise:
            #Случай, когда маскировка игрока позволяет пройти на локацию
            player.current_location = move_to_location
            if edit:
                query.edit_message_text(text=location_status(player.current_location), reply_markup=choose_action_keyboard())
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text=location_status(player.current_location), reply_markup=choose_action_keyboard())
        else:
            #Случай, когда маскировка игрока не позволяет пройти на локацию
            chance = min(10, location_witnesses(player.current_location))
            if edit:
                query.edit_message_text(text='У вас нет подходящей маскировки. Переместиться на локацию?', reply_markup=(no_disguise_move_keyboard(chance=chance, location=move_to_location)))
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text='У вас нет подходящей маскировки. Переместиться на локацию?', reply_markup=(no_disguise_move_keyboard(chance=chance, location=move_to_location)))

    def combat(update: Update, context: CallbackContext, start_string='', type='edit'):
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
        if type == 'edit':
            if player.health == 0:
                query.answer()
                query.edit_message_text(text='Вы умерли. Миссия провалена.')
                time[0] = 0
            if enemies == []:
                player.health = 100
                query.answer()
                query.edit_message_text(text=start_string + f'Бой закончился.\n\nУбито невинных: {kills[0]}\nНайдено тел: {bodies[0]}', reply_markup=(choose_action_keyboard()))
            else:
                query.answer()
                query.edit_message_text(text=start_string + f'Выберите оружие', reply_markup=(choose_weapon_keyboard()))
        elif type == 'add':
            if player.health == 0:
                context.bot.send_message(chat_id=update.effective_chat.id, text='Вы умерли. Миссия провалена.')
                time[0] = 0
            if enemies == []:
                player.health = 100
                context.bot.send_message(chat_id=update.effective_chat.id, text=start_string + f'Бой закончился.\n\nУбито невинных: {kills[0]}\nНайдено тел: {bodies[0]}', reply_markup=(choose_action_keyboard()))
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text=start_string + f'Выберите оружие', reply_markup=(choose_weapon_keyboard()))

    def safe_move(update: Update, context: CallbackContext):
        query = update.callback_query
        player.current_location = locations[query.data.replace('SM', '')]
        if player.item.name == 'Монета':
            player.current_location.items.append(player.item)
        player.inventory.remove(player.item)
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
        dispatcher.add_handler(CallbackQueryHandler(use_neurochip, pattern=is_use_neurochip))
        dispatcher.add_handler(CallbackQueryHandler(destroy_heart_menu_1, pattern=is_destroy_heart_1))
        dispatcher.add_handler(CallbackQueryHandler(destroy_heart_menu_2, pattern=is_destroy_heart_2))
        dispatcher.add_handler(CallbackQueryHandler(destroy_heart, pattern=is_destroy_heart))

        updater.start_polling()
        updater.idle()

    run_bot()

telegram_bot()

def f():
    if events['Компьютер в морге'].completed == False and player.current_location.get_name() == 'Морг':
        controller.player_view.response('Вы нашли файл на компьютере. Это заметки о Кураторе и его нейрочипе. В них приводятся подробные сведения об устройстве чипа и принципе его работы, а также описание того, как изменение дозы влияет на настроение Куратора. Судя по всему, увеличение дозы приводит к улучшению его настроения, а уменьшение, напротив, возвращает его в привычное подавленное состояние. Что любопытно, научный сотрудник, похоже, сам менял дозу Куратора без его ведома: для этого он использовал пульт управления чипом, который куратор хранит в своей спальне.')
        events.get_by_name('Компьютер в морге').completed = True

    if player.disguise != 'VIP - пациент':
        so[0] = 1

    if events.get_by_name('Информация о сигаретах 1').completed == False and locator.get_items().get_by_name('Пачка сигарет') in player.inventory:
        controller.player_view.response('Диана: Это пачка сигарет. Не территории клиники «Гама» курение строго запрещено, так что эти сигареты — явная контрабанда.')
        events.get_by_name('Информация о сигаретах 1').completed = True

    if events.get_by_name('Информация о сигаретах 2').completed == False and player.current_location.get_name() == 'Канатная дорога':
        controller.player_view.response('Диана: Значит, Юки Ямадзаки выронила свои сигареты по пути к клинике. Интересно. Юки Ямадзаки уронила свои сигареты, когда поднималась на фуникулере по прибытии в клинику. Если верить её охране, это её ужасно взбесило. Может быть, тебе удастся утолить её «жажду», 47-й? Сигареты в «Гаме» запрещены, но не все следуют этому правилу...')
        events.get_by_name('Информация о сигаретах 2').completed = True

    if events.get_by_name('Информация о суши').completed == False and player.current_location.get_name() == 'Ресторан':
        controller.player_view.response('Диана: Ядовитая Рыба фугу и адвокат в поисках острых ощущений — убийственная комбинация. Не так давно из-за ошибки повара один из пациентов отравился ядовитой рыбой, и с тех пор фугу здесь под строжайшим запретом. Но, судя по всему, Юки Ямадзаки пытается уговорить шеф-повара подать ей последнюю рыбу из его запасов. Разве мы вправе отказывает ей в таком удовольствии, 47-й?')
        events.get_by_name('Информация о суши').completed = True

    if events.get_by_name('Информация о чипе').completed == False and locator.get_items().get_by_name('Пульт для управления нейрочипом') in player.inventory:
        controller.player_view.response('Диана: Нейрочип для изменения настроения. Интересно... Доктор Каташи Ито, он же Куратор, проводит сейчас какое-то медицинское испытание. Интересно. Хранилище органов находится в ведении Куратора, а значит, у него точно есть доступ к сердцу, которое должны пересадить Содерсу. 47-й, я рекомендую найти отчёт сотрудника и выяснить, для чего нужен этот нейроимплантат. Может пригодиться.')
        events.get_by_name('Информация о чипе').completed = True

    if events.get_by_name('Расписание занятий по йоге').completed == False and player.current_location.get_name() == 'Зона отдыха':
        controller.player_view.response('Диана: Расписание занятий по йоге. Имя Юки Ямадзаки — в каждой графе. Что ж, судя по всему, Юки Ямадзаки — настоящий фанат йоги. Из расписания у горячего источника видно, что она заняла тренера на целый день. Готов размяться, 47-й?')
        events.get_by_name('Расписание занятий по йоге').completed = True

    if locator.get_targets().get_by_name('Юки Ямадзаки').alive == False and locator.get_targets().get_by_name('Эрих Содерс').alive == False and events.get_by_name('Все цели убиты').completed == False:
        controller.player_view.response('Все цели убиты. Найдте выход с миссии.')
        events.get_by_name('Все цели убиты').completed = True

    if events.get_by_name('Все цели убиты').completed == True and (player.current_location.get_name() == 'Канатная дорога' or player.current_location.get_name() == 'Гараж' or player.current_location.get_name() == 'Вертолетная площадка' or player.current_location.get_name() == 'Горная тропа'):
        controller.player_view.response('1. Завершить миссию')
        controller.player_view.request()
        controller.player_view.response('Диана: Миссия выполнена, хорошая работа, 47-ой.')
        controller.rating()

    if (locator.get_items().get_by_name('Яд рыбы Фугу') in player.inventory or locator.get_items().get_by_name('Крысиный яд') in player.inventory or locator.get_items().get_by_name('Смертельный яд') in player.inventory or locator.get_items().get_by_name('Рвотный яд') in player.inventory) and player.disguise == 'Шеф' and player.current_location.get_name() == 'Ресторан' and events.get_by_name('Убийство ядом').completed == False:
        controller.player_view.response('1. Отравить роллы\n2. Не отравлять роллы')
        request = controller.player_view.request()
        while request.isdigit() == False:
            controller.player_view.response('Введите номер ответа')
            request = controller.player_view.request()
        request = int(request)
        if request == 2:
            controller.player_view.response(locator.location_status(player.current_location))
        elif request == 1:
            events.get_by_name('Убийство ядом').completed = True
            poisons = [locator.get_items().get_by_name('Яд рыбы Фугу'), locator.get_items().get_by_name('Крысиный яд'), locator.get_items().get_by_name('Смертельный яд'), locator.get_items().get_by_name('Рвотный яд')]
            result_string = ''
            for i in range(len(poisons)):
                if poisons[i] in player.inventory:
                    result_string += f'{i+1}. {poisons[i].name}\n'
            controller.player_view.response(result_string)
            request = controller.player_view.request()
            while request.isdigit() == False:
                controller.player_view.response('Введите номер ответа')
                request = controller.player_view.request()
            request = int(request)
            player.inventory.remove(poisons[request - 1])
            if poisons[request - 1].deadly == True:
                result_string = ''
                if poisons[request - 1] == locator.get_items().get_by_name('Яд рыбы Фугу'):
                    controller.player_view.response(f'{locator.get_challenges().get_by_name("Приятного аппетита").achieved()}')
                locator.get_targets().get_by_name('Юки Ямадзаки').alive = False
                controller.player_view.response(locator.get_challenges().get_by_name('Без вкуса, без следа').achieved())
                result_string += '\n\nДиана: Грамотный ход 47-ой. С Юки Ямадзаки покончено.'
                controller.player_view.response(result_string)
            else:
                controller.player_view.response('Цели стало плохо и она направилась в ванную. Пойти за ней?\n\n1. Да\n2. Нет')
                request = controller.player_view.request()
                while request.isdigit() == False:
                    controller.player_view.response('Введите номер ответа')
                    request = controller.player_view.request()
                request = int(request)
                if request == 1:
                    controller.player_view.response('1. Утопить цель\n2. Уйти')
                    request = controller.player_view.request()
                    while request.isdigit() == False:
                        controller.player_view.response('Введите номер ответа')
                        request = controller.player_view.request()
                    request = int(request)
                    if request == 2:
                        controller.player_view.response(locator.location_status(player.current_location))
                    elif request == 1:
                        controller.player_view.response(f'{locator.get_challenges().get_by_name("Подержи волосы").achieved()}')
                        controller.player_view.response(f'{locator.get_challenges().get_by_name('Так можно и пораниться').achieved()}')
                        result_string = 'Диана: Цель убита. Хорошая работа.'
                        locator.get_targets().get_by_name('Юки Ямадзаки').alive = False
                        controller.player_view.response(result_string)
                elif request == 2:
                    controller.player_view.response(locator.location_status(player.current_location))

    if player.current_location.get_name() == 'Комната управления системой водоснабжения спа' and events.get_by_name('Убийство в сауне').completed == False:
        controller.player_view.response('1. Увеличить температуру в бане\n2. Уйти')
        request = controller.player_view.request()
        while request.isdigit() == False:
            controller.player_view.response('Введите номер ответа')
            request = controller.player_view.request()
        request = int(request)
        if request == 1:
            events.get_by_name('Убийство в сауне').completed = True
            controller.player_view.response('Все люди вышли из бани из-за высокой температуры.')
            if locator.get_targets().get_by_name('Юки Ямадзаки').alive == True:
                controller.player_view.response('Юки Ямадзаки: Наконец-то парилка свободна!\nЮки Ямадзаки вошла в баню\n\n1. Запереть дверь в парилку\n2. Уйти')
                request = controller.player_view.request()
                while request.isdigit() == False:
                    controller.player_view.response('Введите номер ответа')
                    request = controller.player_view.request()
                request = int(request)
                if request == 1:
                    locator.get_targets().get_by_name('Юки Ямадзаки').alive = False
                    controller.player_view.response(f'{locator.get_challenges().get_by_name('Убийство в парилке').achieved()}')
                    controller.player_view.response(f'{locator.get_challenges().get_by_name('Так можно и пораниться').achieved()}')
                    result_string = 'Диана: С Юки Ямадзаки покончено. Отличная работа, агент.'
                    controller.player_view.response(result_string)
                elif request == 2:
                    controller.player_view.response(locator.location_status(player.current_location))
            else:
                controller.player_view.response(locator.location_status(player.current_location))
        elif request == 2:
            controller.player_view.response(locator.location_status(player.current_location))

    if player.disguise == 'Инструктор по йоге' and events.get_by_name('Убийство во время йоги').completed == False and player.current_location == 'Зона отдыха' and locator.get_targets().get_by_name('Юки Ямадзаки').alive == True:
        events.get_by_name('Убийство во время йоги').completed = True
        controller.player_view.response('Юки Ямадзаки: Наконец-то, сколько можно вас ждать!\n\n1. Начать тренировку по йоге\n2. Уйти')
        request = controller.player_view.request()
        while request.isdigit() == False:
            controller.player_view.response('Введите номер ответа')
            request = controller.player_view.request()
        request = int(request)
        if request == 1:
            controller.player_view.response('Агент 47: Приступим, эта тренировка смертельно вам понравится.\nЮки Ямадзаки отозвала всю охрану и вывела всех людей из зоны отдыха\n\n1. Толкнуть Юки Ямадзаки с горы\n2. Завершить тренировку')
            request = controller.player_view.request()
            while request.isdigit() == False:
                controller.player_view.response('Введите номер ответа')
                request = controller.player_view.request()
            request = int(request)
            if request == 1:
                locator.get_targets().get_by_name('Юки Ямадзаки').alive = False
                controller.player_view.response(f'{locator.get_challenges().get_by_name('Хорошая растяжка').achieved()}')
                controller.player_view.response(f'{locator.get_challenges().get_by_name('Так можно и пораниться').achieved()}')
                result_string = 'Диана: Отлично сработано. Юки Ямадзаки нас больше не побеспокоит.'
                controller.player_view.response(result_string)
            if request == 2:
                controller.player_view.response(locator.location_status(player.current_location))

    if player.current_location.get_name() == 'Номер Юки Ямадзаки' and locator.get_items().get_by_name('Пачка сигарет') in player.inventory and events.get_by_name('Сигареты на столе').completed == False:
        controller.player_view.response('1. Положить пачку сигарет\n2. Оставить пачку сигарет')
        request = controller.player_view.request()
        while request.isdigit() == False:
            controller.player_view.response('Введите номер ответа')
            request = controller.player_view.request()
        request = int(request)
        if request == 1:
            player.inventory.remove(locator.get_items().get_by_name('Пачка сигарет'))
            controller.player_view.response(f'{locator.get_challenges().get_by_name('Не курить!').achieved()}')
            result_string = '1. Выйти из номера\n2. Пойти на балкон'
            controller.player_view.response(result_string)
            events.get_by_name('Сигареты на столе').completed = True
            request = controller.player_view.request()
            while request.isdigit() == False:
                controller.player_view.response('Введите номер ответа')
                request = controller.player_view.request()
            request = int(request)
            if request == 1:
                player.current_location = locator.get_location_by_name('Холл')
                controller.player_view.response(locator.location_status(player.current_location))
            elif request == 2:
                controller.player_view.response('1. Создать утечку газа у обогревателя\n2. Уйти из номера')
                request = controller.player_view.request()
                while request.isdigit() == False:
                    controller.player_view.response('Введите номер ответа')
                    request = controller.player_view.request()
                request = int(request)
                if request == 1:
                    if locator.get_items().get_by_name('Гаечный ключ') in player.inventory:
                        controller.player_view.response('1. Выйти из номера')
                        controller.player_view.request()
                        player.current_location = locator.get_location_by_name('Холл')
                        if locator.get_targets().get_by_name('Юки Ямадзаки').alive == True:
                            locator.get_targets().get_by_name('Юки Ямадзаки').alive = False
                            controller.player_view.response(f'{locator.get_challenges().get_by_name('Курение убивает').achieved()}')
                            controller.player_view.response(f'{locator.get_challenges().get_by_name('Так можно и пораниться').achieved()}')
                            result_string = 'Юки Ямадзаки: Пачка сиграрет? Как я могла ее не заметить!\nЮки Ямадзаки вышла на балкон и воспользовалась зажигалкой, что привело к взрыву.\n\nДиана: Это было умно, 47-й. Юки Ямадзаки больше нас не побеспокоит.'
                            controller.player_view.response(result_string)
                    else:
                        controller.player_view.response('У вас нет гаечного ключа')
                elif request == 2:
                    player.current_location = locator.get_location_by_name('Холл')
                    controller.player_view.response(locator.location_status(player.current_location))
        elif request == 2:
            player.current_location = locator.get_location_by_name('Холл')
            controller.player_view.response(locator.location_status(player.current_location))

    if player.current_location.get_name() == 'Номер Юки Ямадзаки' and events.get_by_name('Сигареты на столе').completed == True:
        controller.player_view.response('1. Выйти из номера\n2. Пойти на балкон')
        request = controller.player_view.request()
        while request.isdigit() == False:
            controller.player_view.response('Введите номер ответа')
            request = controller.player_view.request()
        request = int(request)
        if request == 1:
            player.current_location = locator.get_location_by_name('Холл')
            controller.player_view.response(locator.location_status(player.current_location))
        elif request == 2:
            controller.player_view.response('1. Создать утечку газа у обогревателя\n2. Уйти из номера')
            while request.isdigit() == False:
                controller.player_view.response('Введите номер ответа')
                request = controller.player_view.request()
            request = int(request)
            if request == 1:
                if locator.get_items().get_by_name('Гаечный ключ') in player.inventory:
                        controller.player_view.response('1. Выйти из номера')
                        controller.player_view.request()
                        player.current_location = locator.get_location_by_name('Холл')
                        if locator.get_targets().get_by_name('Юки Ямадзаки').alive == True:
                            locator.get_targets().get_by_name('Юки Ямадзаки').alive = False
                            controller.player_view.response(f'{locator.get_challenges().get_by_name('Курение убивает').achieved()}')
                            controller.player_view.response(f'{locator.get_challenges().get_by_name('Так можно и пораниться').achieved()}')
                            result_string = 'Юки Ямадзаки: Пачка сиграрет? Как я могла ее не заметить!\nЮки Ямадзаки вышла на балкон и воспользовалась зажигалкой, что привело к взрыву.\n\nДиана: Это было умно, 47-й. Юки Ямадзаки больше нас не побеспокоит.'
                            controller.player_view.response(result_string)
                else:
                    controller.player_view.response('У вас нет гаечного ключа')
            elif request == 2:
                player.current_location = locator.get_location_by_name('Холл')
                controller.player_view.response(locator.location_status(player.current_location))

    if (player.current_location.get_name() == 'Комната пилота' or player.current_location.get_name() == 'Вертолетная площадка') and events.get_by_name('Информация о пилоте').completed == False:
        events.get_by_name('Информация о пилоте').completed = True
        controller.player_view.response('Диана: 47-й, у меня есть сведения о пилоте. Мне удалось извлечь кое-какие данные из системы безопасности клиники. Главный хирург, Николя Лоран, похоже, часто встречается с пилотом вертолёта у выхода из мед-комплекса. А если верить слухам, у главного хирурга дрожат руки.')

    if player.disguise == 'Пилот' and player.current_location.get_name() == 'Вертолетная площадка' and locator.get_npcs().get_by_name('Nicholas Laurent').alive == True and events.get_by_name('Устранение главного хирурга').completed == False:
        events.get_by_name('Устранение главного хирурга').completed = True
        controller.player_view.response('Главный хирург вышел из мед-комплекса\nГлавный хирург: У тебя еще остались те таблетки?\n47-й: Конечно, следуй за мной.\n\n1. Пойти в комнату пилота\n2. Уйти')
        request = controller.player_view.request()
        while request.isdigit() == False:
            controller.player_view.response('Введите номер ответа')
            request = controller.player_view.request()
        request = int(request)
        if request == 2:
            controller.player_view.response(locator.location_status(player.current_location))
        elif request == 1:
            player.current_location = locator.get_location_by_name('Комната пилота')
            controller.player_view.response('1. Усмирить главного хирурга\n2. Уйти')
            request = controller.player_view.request()
            while request.isdigit() == False:
                controller.player_view.response('Введите номер ответа')
                request = controller.player_view.request()
            request = int(request)
            if request == 2:
                controller.player_view.response(locator.location_status(player.current_location))
            if request == 1:
                locator.get_npcs().get_by_name('Nicholas Laurent').alive = False
                player.found_disguises.append('Главный хирург')
                controller.player_view.response(locator.location_status(player.current_location))

    if player.current_location.get_name() == 'Операционная' and player.disguise == 'Главный хирург' and events.get_by_name('Убийство в операционной').completed == False and locator.get_targets().get_by_name('Эрих Содерс').alive == True:
        controller.player_view.response('1. Управлять операционным роботом\n2. Не управлять')
        request = controller.player_view.request()
        while request.isdigit() == False:
            controller.player_view.response('Введите номер ответа')
            request = controller.player_view.request()
        request = int(request)
        if request == 1:
            controller.player_view.response('1. Убить Эриха Содерса\n2. Уйти')
            request = controller.player_view.request()
            while request.isdigit() == False:
                controller.player_view.response('Введите номер ответа')
                request = controller.player_view.request()
            request = int(request)
            if request == 1:
                locator.get_targets().get_by_name('Эрих Содерс').alive = False
                controller.player_view.response(f'{locator.get_challenges().get_by_name('(Не) врачебная ошибка').achieved()}')
                controller.player_view.response(f'{locator.get_challenges().get_by_name('Так можно и пораниться').achieved()}')
                result_string = 'Диана: Умно, 47-й. С Содерсом покончено.'
                controller.player_view.response(result_string)
                events.get_by_name('Убийство в операционной').completed = True
            if request == 2:
                controller.player_view.response(locator.location_status(player.current_location))
        elif request == 2:
            controller.player_view.response(locator.location_status(player.current_location))

    if 'Охранник' in player.found_disguises or 'Телохранитель' in player.found_disguises:
        player.inventory.append(locator.get_items().get_by_name('Пистолет без глушителя'))

    if player.current_location.get_name() == 'Комната с серверами' and locator.get_targets().get_by_name('Эрих Содерс').alive == True:
        controller.player_view.response('1. Повредить серверы\n2. Не повреждать')
        request = controller.player_view.request()
        while request.isdigit() == False:
            controller.player_view.response('Введите номер ответа')
            request = controller.player_view.request()
        request = int(request)
        if request == 1:
            locator.get_targets().get_by_name('Эрих Содерс').alive = False
            controller.player_view.response(f'{locator.get_challenges().get_by_name('Призрак в машине').achieved()}')
            controller.player_view.response(f'{locator.get_challenges().get_by_name('Так можно и пораниться').achieved()}')
            result_string = 'Хирург: Что происходит с роботом?! Как его отключить?! Пациент сейчас умрет!\n\nДиана: Это было впечатляюще, агент. Эрих Содерс мертв.'
            controller.player_view.response(result_string)
        if request == 2:
            controller.player_view.response(locator.location_status(player.current_location))

    if player.current_location.get_name() == 'Комната охраны' and events.get_by_name('Информация об ИИ').completed == False:
        events.get_by_name('Информация об ИИ').completed = True
        controller.player_view.response('Интересно. Руководство для KAI, искусственного интеллекта клиники «Гама». Значит, местный искусственный интеллект по имени KAI не только поддерживает работу систем здания, но и управляет роботом в операционной. Именно там сейчас находится Содерс. В руководстве говорится, что после остановки сердца пациента искусственный интеллект автоматически начинает его реанимацию, что очень некстати. Однако... У директора клиники есть доступ к главному компьютеру. Справишься с управлением целой клиникой, 47-й?')