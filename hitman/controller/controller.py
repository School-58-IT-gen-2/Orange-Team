import pickle
import sys
import random

from view.player_view import PlayerView
from model.player.player_info import *
from model.player.player import Player
from view.console_view import ConsoleView
from view.telegram_view import TelegramView
from model.hokkaido.hokkaido_locator import HokkaidoLocator
from model.common.npcs import Target

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup,ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, PollAnswerHandler, PollHandler


#Класс, описывающий контроллер
class PlayerController:

    def __init__(self,
                 player=Player(),
                 player_view: PlayerView=None,
                 locator=HokkaidoLocator()
                 ):
        self.player = player
        self.player_view = player_view
        if locator:
            self.locator = locator
    
    #Удаляет все предметы с локации и добавляяет их в инвентарь игрока, выводит добавленные предметы
    def search(self):
        self.player.inventory += self.player.current_location.get_items()
        result_string = 'Найдены предметы:\n\n'
        if self.player.current_location.get_items() == []:
            return self.player_view.response('На локации нет предметов')
        else:
            for i in self.locator.get_items().get_all():
                if i in self.player.current_location.get_items():
                    result_string += f'{i.name} ({self.player.current_location.get_items().count(i)})\n'
        self.player.current_location.set_items([])
        return self.player_view.response(result_string)
    
    #Выводит статус текущей локации или общий статус прохождения миссии
    def status(self):
        self.player_view.response(f'1. Статус {self.player.current_location.get_name()}\n2. Общий статус')
        request = self.player_view.request()
        while request.isdigit() == False:
            self.player_view.response('Введите номер ответа')
            request = self.player_view.request()
        request = int(request)
        if request == 2:
            result_string = ''
            for i in self.locator.get_targets().get_all():
                if i.alive == True:
                    result_string += f'{i.name}: {i.move()}\n'
                else:
                    result_string += f'{i.name}: Цель устранена\n'
            result_string += f'\n\nТекущая маскировка: {self.player.disguise}\n'
            result_string += f'Предмет в руках: {self.player.item.name}'
            if int(5-(bodies[0]*0.5)-(kills[0]*0.7)-(combat_count[0]*0.1)-(suspicion_count[0]*0.2)) == 5:
                result_string += f'\n\nБесшумный убийца'
            return self.player_view.response(result_string)
        else:
            return self.player_view.response(self.locator.location_status(self.player.current_location))
    
    #Выводит инвентарь игрока
    def inventory(self):
        inventory = []
        if self.player.inventory.count(self.player.item) == 0:
            self.player.item = self.locator.get_items().get_by_name('Нет предмета')
        result_string = ''
        for i in self.player.inventory:
            if i.name == 'Пистолет без глушителя' or i.name == 'Пистолет с глушителем':
                inventory.append(i.name + ' (1)')
            else:
                inventory.append(i.name + ' (' + str(self.player.inventory.count(i)) + ')')
        inventory = list(set(inventory))
        if inventory == []:
            result_string += 'У вас нет предметов\n'
        inventory.append('Убрать предмет из рук')
        inventory.append(self.player.disguise)
        inventory.append('Выйти из инвентаря')
        for i in range(len(inventory)-3):
            result_string += f'{str(i+1)}. {inventory[i]}\n'
        result_string += f'\nСейчас в руках: {self.player.item.name}\n'
        result_string += f'{len(inventory) - 2}. Убрать предмет из рук\n'
        result_string += f'\n{len(inventory) - 1}. {self.player.disguise}\n'
        result_string += f'\n{len(inventory)}. Выйти из инвентаря'
        self.player_view.response(result_string)
        request = self.player_view.request()
        while request.isdigit() == False:
            self.player_view.response('Введите номер ответа')
            request = self.player_view.request()
        request = int(request)

        #Открывает меню выбора маскировки
        if inventory[request - 1] == self.player.disguise:
            result_string = ''
            for i in range(len(self.player.found_disguises)):
                result_string += f'{str(i+1)}. {self.player.found_disguises[i]}\n'
            self.player_view.response(result_string)
            request = self.player_view.request()
            while request.isdigit() == False:
                self.player_view.response('Введите номер ответа')
                request = self.player_view.request()
            request = int(request)
            self.player.disguise = self.player.found_disguises[request - 1]
            return self.player_view.response(f'Текущая маскировка: {self.player.disguise}')
        
        #Заменяет текущий предмет на "Нет предмета"
        elif inventory[request - 1] == 'Убрать предмет из рук':
            self.player.item = self.locator.get_items().get_by_name('Нет предмета')
            return self.player_view.response(f'Сейчас в руках: {self.player.item.name}')
        
        #Закрывает инвентарь и возвращает статус локации
        elif inventory[request - 1] == 'Выйти из инвентаря':
            return self.player_view.response(self.locator.location_status(self.player.current_location))
        
        #Заменяет текущий предмет на выбранный игроком (предмет нелегален)
        elif self.locator.get_items().get_by_name(inventory[request - 1][:-4]).illegal:
            if self.player.disguise == 'Охранник' or self.player.disguise == 'Телохранитель':
                self.player.item = self.locator.get_items().get_by_name(inventory[request - 1][:-4])
                return self.player_view.response(f'Сейчас в руках: {self.player.item.name}')
            else:
                self.player_view.response(f'{inventory[request - 1][:-4]} -- это нелегальный предмет. Достать предмет?\n\n1. Да\n2. Нет')
                second_request = self.player_view.request()
                while second_request.isdigit() == False:
                    self.player_view.response('Введите номер ответа')
                    second_request = self.player_view.request()
                second_request = int(second_request)
                if second_request == 1:
                    self.player.item = self.locator.get_items().get_by_name(inventory[request - 1][:-4])
                    return self.player_view.response(f'Сейчас в руках: {self.player.item.name}')
                else:
                    return self.inventory()
        
        #Заменяет текущий предмет на выбранный игроком (предмет легален)
        else:
            self.player.item = self.locator.get_items().get_by_name(inventory[request - 1][:-4])
            return self.player_view.response(f'Сейчас в руках: {self.player.item.name}')
    
    #Выводит меню с испытаниями
    def see_challenges(self):
        result_string = ''
        for i in range(len(self.locator.get_challenges().get_all())):
            if self.locator.get_challenges().get_all()[i].completed == True:
                result_string += f"{i+1}. {self.locator.get_challenges().get_all()[i].name + ' (выполнено)'}\n"
            else:
                result_string += f'{i+1}. {self.locator.get_challenges().get_all()[i].name}\n'
        result_string += f'\n\n{len(self.locator.get_challenges().get_all()) + 1}. Выйти'
        self.player_view.response(result_string)
        request = self.player_view.request()
        while request.isdigit() == False:
            self.player_view.response('Введите номер ответа')
            request = self.player_view.request()
        request = int(request)
        if request > len(self.locator.get_challenges().get_all()):
            return self.player_view.response(self.locator.location_status(self.player.current_location))
        else:
            self.player_view.response(self.locator.get_challenges().get_all()[request-1].challenge_info())
            self.player_view.request()
            return(self.see_challenges())
    
    #Перемещение по локациям
    def move(self):
        global bodies
        global suspicion_count
        result_string = ''
        for i in range(len(self.player.current_location.get_connected_locations())):
            result_string += f"{str(i+1)+'. '+ str(self.player.current_location.get_connected_locations()[i + 1])}\n"
        result_string += f'\n{len(self.player.current_location.get_connected_locations()) + 1}. Отменить действие'
        self.player_view.response(result_string)
        request = self.player_view.request()
        while request.isdigit() == False:
            self.player_view.response('Введите номер ответа')
            request = self.player_view.request()
        request = int(request)

        #Закрывает меню если игрок отменил действие и возвращает статус локации
        if request == len(self.player.current_location.get_connected_locations()) + 1:
            return self.player_view.response(self.locator.location_status(self.player.current_location))
        for i in self.locator.get_locations():
            if i == self.player.current_location.get_connected_locations()[request]:
                move_to_location = self.locator.get_location_by_name(i)

        #Проверяет, чтобы у локации для перемещения не было особых условий для входа (например необходима особая маскировка или ключ-карта)
        if move_to_location.get_name() == 'Комната с серверами':
            if self.player.disguise == 'Директор клиники' or self.locator.get_items().get_by_name('Ключ-карта') in self.player.inventory or self.locator.get_items().get_by_name('Электронный дешифровщик') in self.player.inventory:
                self.player.current_location = move_to_location
                return self.player_view.response(f'{self.locator.location_status(self.player.current_location)}')
            else:
                return self.player_view.response('Для входа необходима маскировка директора клиники или ключ-карта')
        else:
            #Случай, когда маскировка игрока раскрыта
            if self.player.disguise in self.player.compromised_disguises:
                if self.locator.find_location_npcs(self.player.current_location.get_name()) != []:
                    location_npc = self.locator.find_location_npcs(self.player.current_location.get_name())[random.randrange(len(self.locator.find_location_npcs(self.player.current_location.get_name())))]
                    result_string = location_npc.suspicion()
                    result_string += '\n\n1. Напасть (3/10)\n2. Уйти'
                    self.player_view.response(result_string)
                    request = self.player_view.request()
                    while request.isdigit() == False:
                        self.player_view.response('Введите номер ответа')
                        request = self.player_view.request()
                    request = int(request)
                    if request == 2:
                        return self.player_view.response(f'{self.locator.location_status(self.player.current_location)}')
                    else:
                        if random.randrange(1, 11) <= 3:
                            location_npc.alive = False
                            self.player.found_disguises.append(location_npc.get_disguise())
                            self.player.current_location = move_to_location
                            result_string = f'Вам удалось тихо устранить {location_npc.get_name()}'
                            result_string += f'\n\n\n{self.locator.location_status(self.player.current_location)}'
                            return self.player_view.response(result_string)
                        else:
                            return self.combat()
                else:
                    self.player.current_location = move_to_location
                    return self.player_view.response(f'{self.locator.location_status(self.player.current_location.get_name())}')
            else:
                #Случай, когда в руках игрока нелегальный предмет
                if (self.player.item.illegal == True and self.locator.get_disguise_by_name(self.player.disguise) != 'Охранник' and self.locator.get_disguise_by_name(self.player.disguise) != 'Телохранитель'):
                    self.player.current_location = move_to_location
                    if self.locator.find_location_npcs(self.player.current_location.get_name()) != []:
                        location_npc = self.locator.find_location_npcs(self.player.current_location.get_name())[random.randrange(len(self.locator.find_location_npcs(self.player.current_location.get_name())))]
                        suspicion_count[0] += 1
                        result_string = f'{location_npc.get_name()}: Он вооружен!\n\n'
                        result_string += '1. Напасть (3/10)\n2. Скрыться (7/10)'
                        self.player_view.response(result_string)
                        request = self.player_view.request()
                        while request.isdigit() == False:
                            self.player_view.response('Введите номер ответа')
                            request = self.player_view.request()
                        request = int(request)
                        if request == 1:
                            if random.randrange(1, 11) <= 3:
                                location_npc.alive = False
                                return self.player_view.response(f'Вам удалось тихо устранить {location_npc.get_name()}')
                            else:
                                return self.combat()
                        else:
                            if random.randrange(1, 11) <= 7:
                                self.player.compromised_disguises.append(self.player.disguise)
                                result_string = 'Ваша маскировка раскрыта, при перемещении в любую локацию вас будут узнавать.\n'
                                result_string += f'\n\n{self.locator.location_status(self.player.current_location)}'
                                return self.player_view.response(result_string)
                            else:
                                return self.combat()
                else:
                    #Случай, когда маскировка игрока позволяет пройти на локацию
                    if self.locator.get_disguise_by_name(self.player.disguise) in move_to_location.get_disguise():
                        self.player.current_location = move_to_location
                        return self.player_view.response(f'{self.locator.location_status(self.player.current_location)}')
                    else:
                        #Случай, когда маскировка игрока не позволяет пройти на локацию
                        if self.locator.location_witnesses(self.player.current_location.get_name()) > 10:
                            chance = 10
                        else:
                            chance = self.locator.location_witnesses(self.player.current_location.get_name())
                        result_string = f'\n\nУ вас нет подходящей маскировки. Переместиться на локацию? ({10-chance}/10)\n\n1. Да\n2. Нет'
                        self.player_view.response(result_string)
                        request = self.player_view.request()
                        while request.isdigit() == False:
                            self.player_view.response('Введите номер ответа')
                            request = self.player_view.request()
                        request = int(request)
                        if request == 2:
                            return self.player_view.response(f'{self.locator.location_status(self.player.current_location)}')
                        else:
                            if random.randrange(1,11) <= 10-chance:
                                self.player.current_location = move_to_location
                                return self.player_view.response(f'{self.locator.location_status(self.player.current_location)}')
                            else:
                                if self.locator.find_location_npcs(self.player.current_location.get_name()) != []:
                                    location_npc = self.locator.find_location_npcs(move_to_location.get_name())[random.randrange(len(self.locator.find_location_npcs(move_to_location.get_name())))]
                                    result_string = location_npc.suspicion()
                                    result_string += '\n\n1. Напасть (3/10)\n2. Уйти'
                                    self.player_view.response(result_string)
                                    request = self.player_view.request()
                                    while request.isdigit() == False:
                                        self.player_view.response('Введите номер ответа')
                                        request = self.player_view.request()
                                    request = int(request)
                                    if request == 2:
                                        return self.player_view.response(f'{self.locator.location_status(self.player.current_location)}')
                                    else:
                                        if random.randrange(1, 11) <= 3:
                                            if self.locator.location_witnesses(move_to_location.get_name()) > 0:
                                                bodies[0] += 1
                                            location_npc.alive = False
                                            self.player.found_disguises.append(location_npc.get_disguise())
                                            self.player.current_location = move_to_location
                                            result_string = f'Вам удалось тихо устранить {location_npc.get_name()}'
                                            result_string += f'\n\n\n{self.locator.location_status(self.player.current_location)}'
                                            return self.player_view.response(result_string)
                                        else:
                                            return self.combat()
                                else:
                                    self.player.current_location = move_to_location
                                    return self.player_view.response(f'{self.locator.location_status(self.player.current_location)}')
    
    #Перемещение по локациям, не зависящие от маскировки или предмета в руках
    def safe_move(self):
        global time
        result_string = ''
        for i in range(len(self.player.current_location.get_connected_locations())):
            result_string += f"{str(i+1)+'. '+ str(self.player.current_location.get_connected_locations()[i + 1])}\n"
        self.player_view.response(result_string)
        request = self.player_view.request()
        while request.isdigit() == False:
            self.player_view.response('Введите номер ответа')
            request = self.player_view.request()
        request = int(request)
        self.player.current_location = self.locator.get_location_by_name(self.player.current_location.get_connected_locations()[request])
        return self.player_view.response(self.locator.location_status(self.player.current_location))

    #Использование предметов                      
    def interact(self):
        global bodies
        global kills
        witnesses = self.locator.location_witnesses(self.player.current_location.get_name())
        location_npcs = self.locator.find_location_npcs(self.player.current_location.get_name())
        if self.player.inventory.count(self.player.item) == 0:
            self.player.item = self.locator.get_items().get_by_name('Нет предмета')
        result_string = f'Действия видят {witnesses} человек\n\n'
        
        #Проверяет, есть ли действия с предметом
        if self.player.item.usage == []:
            return self.player_view.response('Нет действий с этим предметом')
        else:
            for i in range(len(self.player.item.usage)):
                result_string += f'{i + 1}. {self.player.item.usage[i]}\n'
            self.player_view.response(result_string)
            request = self.player_view.request()
            while request.isdigit() == False:
                self.player_view.response('Введите номер ответа')
                request = self.player_view.request()
            request = int(request)

            #Выстрел из огнестрельного оружия (смертельно)
            if self.player.item.usage[request - 1] == 'Выстрелить':
                for i in self.locator.get_targets().get_all():
                    if i.move() == self.player.current_location.get_name():
                        location_npcs = [i] + location_npcs
                if location_npcs == []:
                    return self.player_view.response('На локации никого нет')
                result_string = ''
                for i in range(len(location_npcs)):
                    result_string += f'{i+1}. Выстрелить в {location_npcs[i].get_name()}\n'
                self.player_view.response(result_string)
                request = self.player_view.request()
                while request.isdigit() == False:
                    self.player_view.response('Введите номер ответа')
                    request = self.player_view.request()
                request = int(request)
                location_npcs[request - 1].alive = False
                result_string = ''
                if isinstance(location_npcs[request - 1], Target):
                    self.player_view.response(self.locator.get_challenges().get_by_name('Точный выстрел').achieved())
                    if location_npcs[request - 1].get_name() == 'Эрих Содерс':
                        self.player_view.response(f'\n\n{self.locator.get_challenges().get_by_name('Личное прощание').achieved()}')
                    result_string += f'\n\nДиана: С {location_npcs[request - 1].get_name()} покончено, отличная работа.'
                    self.player_view.response(result_string)
                else:
                    kills[0] += 1
                    self.player.found_disguises.append(location_npcs[request - 1].get_disguise())
                if witnesses > 0:
                    bodies[0] += 1
                    return self.combat()
                else:
                    return self.player_view.response(self.locator.location_status(self.player.current_location))
            
            #Отмена действия и вывод статуса
            elif self.player.item.usage[request - 1] == 'Отменить действие':
                return self.player_view.response(self.locator.location_status(self.player.current_location))
            
            #Удар тупым предметом (несмертельно)
            elif self.player.item.usage[request - 1] == 'Ударить':
                if location_npcs == []:
                        return self.player_view.response('На локации никого нет')
                result_string = ''
                for i in range(len(location_npcs)):
                        result_string += f'{i+1}. Ударить {location_npcs[i].get_name()}\n'
                self.player_view.response(result_string)
                request = self.player_view.request()
                while request.isdigit() == False:
                    self.player_view.response('Введите номер ответа')
                    request = self.player_view.request()
                request = int(request)
                location_npcs[request - 1].alive = False
                self.player.found_disguises.append(location_npcs[request - 1].get_disguise())
                if witnesses > 0:
                    bodies[0] += 1
                    return self.combat()
                else:
                    return self.player_view.response(self.locator.location_status(self.player.current_location))
                
            #Бросок тупого предмета (несмертельно)
            elif self.player.item.usage[request - 1] == 'Бросить':
                if location_npcs == []:
                        return self.player_view.response('На локации никого нет')
                self.player.current_location.set_items(self.player.current_location.get_items() + [self.player.item])
                self.player.inventory.remove(self.player.item)
                result_string = ''
                for i in range(len(location_npcs)):
                        result_string += f'{i+1}. Бросить в {location_npcs[i].get_name()}\n'
                self.player_view.response(result_string)
                request = self.player_view.request()
                while request.isdigit() == False:
                    self.player_view.response('Введите номер ответа')
                    request = self.player_view.request()
                request = int(request)
                location_npcs[request - 1].alive = False
                self.player.found_disguises.append(location_npcs[request - 1].get_disguise())
                if witnesses > 0:
                    bodies[0] += 1
                    return self.combat()
                else:
                    return self.player_view.response(self.locator.location_status(self.player.current_location))
                
            #Удар острым предметом (смертельно)
            elif self.player.item.usage[request - 1] == 'Ударить (летально)':
                for i in self.locator.get_targets().get_all():
                    if i.move() == self.player.current_location.get_name():
                        if i.get_name() == 'Эрих Содерс':
                            pass
                        else:
                            location_npcs = [i] + location_npcs
                if location_npcs == []:
                    return self.player_view.response('На локации никого нет')
                result_string = ''
                for i in range(len(location_npcs)):
                    result_string += f'{i+1}. Ударить {location_npcs[i].get_name()}\n'
                self.player_view.response(result_string)
                request = self.player_view.request()
                while request.isdigit() == False:
                    self.player_view.response('Введите номер ответа')
                    request = self.player_view.request()
                request = int(request)
                location_npcs[request - 1].alive = False
                result_string = ''
                if isinstance(location_npcs[request - 1], Target):
                    result_string += f'Диана: С {location_npcs[request - 1].get_name()} покончено, отличная работа.'
                    self.player_view.response(result_string)
                else:
                    kills[0] += 1
                    self.player.found_disguises.append(location_npcs[request - 1].get_disguise())
                if witnesses > 0:
                    bodies[0] += 1
                    return self.combat()
                else:
                    return self.player_view.response(self.locator.location_status(self.player.current_location))
                
            #Бросок острого предмета (смертельно)
            elif self.player.item.usage[request - 1] == 'Бросить (летально)':
                self.player.current_location.set_items(self.player.current_location.get_items() + [self.player.item])
                self.player.inventory.remove(self.player.item)
                for i in self.locator.get_targets().get_all():
                    if i.move() == self.player.current_location.get_name():
                        if i.get_name() == 'Эрих Содерс':
                            pass
                        else:
                            location_npcs = [i] + location_npcs
                if location_npcs == []:
                    return self.player_view.response('На локации никого нет')
                result_string = ''
                for i in range(len(location_npcs)):
                    result_string += f'{i+1}. Бросить в {location_npcs[i].get_name()}\n'
                self.player_view.response(result_string)
                request = self.player_view.request()
                while request.isdigit() == False:
                    self.player_view.response('Введите номер ответа')
                    request = self.player_view.request()
                request = int(request)
                location_npcs[request - 1].alive = False
                result_string = ''
                if isinstance(location_npcs[request - 1], Target):
                    result_string += f'Диана: С {location_npcs[request - 1].get_name()} покончено, отличная работа.'
                    self.player_view.response(result_string)
                else:
                    kills[0] += 1
                    self.player.found_disguises.append(location_npcs[request - 1].get_disguise())
                if witnesses > 0:
                    bodies[0] += 1
                    return self.combat()
                else:
                    return self.player_view.response(self.locator.location_status(self.player.current_location))
            
            #Бросок предмета, отвлекающего NPC
            elif self.player.item.usage[request - 1] == 'Бросить для отвлечения':
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
            
            #Удушение при отстутствии предмета (несмертельно)
            elif self.player.item.usage[request - 1] == 'Усмирить':
                if location_npcs == []:
                        return self.player_view.response('На локации никого нет')
                result_string = ''
                for i in range(len(location_npcs)):
                        result_string += f'{i+1}. Усмирить {location_npcs[i].get_name()}\n'
                self.player_view.response(result_string)
                request = self.player_view.request()
                while request.isdigit() == False:
                    self.player_view.response('Введите номер ответа')
                    request = self.player_view.request()
                request = int(request)
                location_npcs[request - 1].alive = False
                self.player.found_disguises.append(location_npcs[request - 1].get_disguise())
                if witnesses > 0:
                    bodies[0] += 1
                    return self.combat()
                else:
                    return self.player_view.response(self.locator.location_status(self.player.current_location))
                
            #Использование особых предметов
            elif self.player.item.usage[request - 1] == 'Использовать':
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
                    
            #Удушение удавкой (смертельно)
            elif self.player.item.usage[request - 1] == 'Задушить':
                for i in self.locator.get_targets().get_all():
                    if i.move() == self.player.current_location.get_name():
                        if i.get_name() == 'Эрих Содерс':
                            pass
                        else:
                            location_npcs = [i] + location_npcs
                if location_npcs == []:
                    return self.player_view.response('На локации никого нет')
                result_string = ''
                for i in range(len(location_npcs)):
                    result_string += f'{i+1}. Задушить {location_npcs[i].get_name()}\n'
                self.player_view.response(result_string)
                request = self.player_view.request()
                while request.isdigit() == False:
                    self.player_view.response('Введите номер ответа')
                    request = self.player_view.request()
                request = int(request)
                location_npcs[request - 1].alive = False
                result_string = ''
                if isinstance(location_npcs[request - 1], Target):
                    result_string += f'Диана: С {location_npcs[request - 1].get_name()} покончено, отличная работа.'
                    self.player_view.response(result_string)
                else:
                    kills[0] += 1
                    self.player.found_disguises.append(location_npcs[request - 1].get_disguise())
                if witnesses > 0:
                    bodies[0] += 1
                    return self.combat()
                else:
                    return self.player_view.response(self.locator.location_status(self.player.current_location))

    #Определяет начальный инвентарь игрока и его маскировку, а также стартовую локацию
    def start(self):

        lvl_unlocks = {
            1: ['Номер 47-го', self.locator.get_location_by_name('Номер 47-го'), 'VIP - пациент'],
            2: ['Зона спа', self.locator.get_location_by_name('Зона спа'), 'VIP - пациент'],
            3: ['Горная тропа (в маскировке ниндзя)', self.locator.get_location_by_name('Горная тропа'), 'Ниндзя'],
            4: ['Ресторан', self.locator.get_location_by_name('Ресторан'), 'VIP - пациент'],
            5: ['Спальня персонала (в маскировке работника "ГАМА")', self.locator.get_location_by_name('Спальня персонала'), 'Работник "ГАМА"'],
            6: ['Кухня (в маскировке шефа)', self.locator.get_location_by_name('Кухня'), 'Шеф'],
            7: ['Внутренний сад (в маскировке работника "ГАМА")', self.locator.get_location_by_name('Внутренний сад'), 'Работник "ГАМА"'],
            8: ['Морг', self.locator.get_location_by_name('Морг'), 'VIP - пациент'],
            9: ['Оперционная (в маскировке хирурга)', self.locator.get_location_by_name('Операционная'), 'Хирург']
        }

        carry_on_items = [self.locator.get_items().get_by_name('Удавка'), self.locator.get_items().get_by_name('Смертельный яд'), self.locator.get_items().get_by_name('Рвотный яд'), self.locator.get_items().get_by_name('Электронный дешифровщик'), self.locator.get_items().get_by_name('Боевой нож'), self.locator.get_items().get_by_name('Монета')]

        self.player_view.response('Брифинг:\nДиана: Доброе утро, 47-й. Совет директоров одобрил ликвидацию Эриха Содерса. После Колорадо мы решили пристально изучить личные дела Содерса и выяснили, что его недавно доставили в частную клинику «Гама» на японском острове Хоккайдо для срочной операции на сердце. Без «Провиденс» тут явно не обошлось. Содерс страдает от редкой врожденной патологии — транспозиции органов: его внутренние органы в теле расположены зеркально. Для трансплантации ему необходимо правостороннее сердце, и он явно предал МКА, чтобы получить его. Его приняли прошлой ночью и сейчас он готовится к трёхэтапной операции. Под видом Тобиаса Рипера, крупного бизнесмена, ты отправляешься в «Гаму» для стандартного медицинского обследования, о формальностях мы уже позаботились. В таких условиях придётся импровизировать и самостоятельно добывать снаряжение. Кроме того, тебе нужно ликвидировать Юки Ямадзаки — она адвокат из Токио, работает на «Провиденс». Содерс уже передал Ямадзаки доступ к нашей базе клиентов и согласился предоставить полный список оперативных сотрудников МКА после завершения операции. Этого допустить никак нельзя. Содерс должен заплатить за своё предательство — это послужит хорошим уроком его нанимателям. На кону будущее и репутация МКА. Какой бы властью и могуществом ни обладала «Провиденс», пора поставить их на место. Я оставлю тебя подготавливаться.\n\nВведите любой символ, чтобы начать задание.')
        request = self.player_view.request()
        result_string = ''
        for i in range(1, 10):
            if i <= player_lvl[0] // 10:
                result_string += f'{i}. {lvl_unlocks[i][0]}\n'
        self.player_view.response(result_string)
        request = self.player_view.request()
        while request.isdigit() == False:
            self.player_view.response('Введите номер ответа')
            request = self.player_view.request()
        request = int(request)
        start_location = lvl_unlocks[request]
        start_inventory = []
        if player_lvl[0] // 10 > 9:
            self.player_view.response('Выберите пистолет:\n\n1. Пистолет с глушителем\n2. Пистолет без глушителя')
            request = self.player_view.request()
            while request.isdigit() == False:
                self.player_view.response('Введите номер ответа')
                request = self.player_view.request()
            request = int(request)
            if request == 1:
                start_inventory.append(self.locator.get_items().get_by_name('Пистолет с глушителем'))
            elif request == 2:
                start_inventory.append(self.locator.get_items().get_by_name('Пистолет без глушителя'))
            result_string = 'Выберите первый предмет сняряжения:\n\n'
            for i in range(len(carry_on_items)):
                if carry_on_items[i].name == 'Монета':
                    result_string += f'{i+1}. Монета (3)\n'
                else:
                    result_string += f'{i+1}. {carry_on_items[i].name} (1)\n'
            self.player_view.response(result_string)
            request = self.player_view.request()
            while request.isdigit() == False:
                self.player_view.response('Введите номер ответа')
                request = self.player_view.request()
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
            self.player_view.response(result_string)
            request = self.player_view.request()
            while request.isdigit() == False:
                self.player_view.response('Введите номер ответа')
                request = self.player_view.request()
            request = int(request)
            if carry_on_items[request - 1].name == 'Монета':
                start_inventory += [carry_on_items[request - 1], carry_on_items[request - 1]]
            start_inventory.append(carry_on_items[request - 1])
        self.player_view.response('Диана: Удачи, агент.')
        if start_location[1].get_name() == 'Номер 47-го':
            self.player_view.response('Диана: Добро пожаловать на Хоккайдо, 47-й. Частная клиника «Гама» оказывает медицинские услуги высочайшего уровня представителям мировой элиты, выходя при необходимости за рамки закона. Частично здание находится под управлением искусственного интеллекта — KAI. Система контролирует доступ пациентов в разные части клиники и даже принимает участие в ряде медицинских процедур. Эрих Содерс уже находится в операционной, где он проходит предварительную подготовку с применением стволовых клеток. Это крайне противоречивая процедура ещё не одобрена властями Японии. Юки Ямадзаки уже прибыла. Она находится либо в своём номере, либо в ресторане, либо в спа-зоне клиники. Содерсу скоро введут наркоз. Сделай так, чтобы он больше никогда не проснулся. Удачи, 47-й.')
        self.player.current_location = start_location[1]
        self.player.inventory = start_inventory
        self.player.health = 100
        self.player.found_disguises = [start_location[2]]
        self.player.item = self.locator.get_items().get_by_name('Нет предмета')
        self.player.compromised_disguises = []
        self.player.disguise = start_location[2]
        return True

    #Выводит результат миссии
    def rating(self):
        global player_lvl
        result_string = f'Тел найдено: {bodies[0]}\n'
        result_string += f'Убито невинных: {kills[0]}\n'
        result_string += f'Вы начали бой {combat_count[0]} раз\n'
        result_string += f'Вы были замечены {suspicion_count[0]} раз'
        rating = int(5-(bodies[0]*0.5)-(kills[0]*0.7)-(combat_count[0]*0.1)-(suspicion_count[0]*0.2))
        if rating < 0:
            rating = 0
        result_string += f'Ваш рейтинг: {rating}/5'
        self.player_view.response(result_string)
        if rating == 5 and so[0] == 1:
            self.player_view.response(f'{self.locator.get_challenges().get_by_name('Бесшумный убийца').achieved()}')
            result_string = 'Бесшумный убийца.'
            self.player_view.response(result_string)
        elif rating == 5 and so[0] == 0:
            self.player_view.response(f'{self.locator.get_challenges().get_by_name('Бесшумный убийца. Только костюм.').achieved()}')
            result_string = 'Бесшумный убийца.'
            self.player_view.response(result_string)
        elif so[0] == 0:
            self.player_view.response(self.locator.get_challenges().get_by_name('Только костюм').achieved())
        if bodies[0] == 0:
            self.player_view.response(self.locator.get_challenges().get_by_name('Без улик').achieved())
        if self.locator.get_challenges().get_by_name('Точный выстрел').completed == True and self.locator.get_challenges().get_by_name('Подержи волосы').completed == True and self.locator.get_challenges().get_by_name('Пианист').completed == True and self.locator.get_challenges().get_by_name('Так можно и пораниться').completed == True and self.locator.get_challenges().get_by_name('Без вкуса, без следа').completed == True:
            self.player_view.response(self.locator.get_challenges().get_by_name('Без улик').achieved())
        player_lvl[0] += rating
        result_string = ''
        for i in self.locator.get_challenges().get_all():
            if i.completed == True:
                result_string += f'{i.name}\n'
        self.player_view.response(result_string)
        with open('save_file.dat', 'wb') as f:
            pickle.dump([self.locator.get_challenges(), player_lvl], f, protocol=2)
        sys.exit()

    #Бой на локации
    def combat(self):
        global kills
        global bodies
        global player_lvl
        global combat_count
        current_kills = 0
        current_bodies = 0
        enemies = []

        for i in self.locator.find_location_npcs(self.player.current_location.get_name()):
            if i.guard == True:
                enemies.append(i)
        
        #Проверяет то, что на локации есть охранники
        if enemies == []:
            return True
        combat_count[0] += 1
        self.player_view.response(f'Начался бой\n\n1. Прятаться (5/10)\n2. Напасть')
        request = self.player_view.request()
        while request.isdigit() == False:
            self.player_view.response('Введите номер ответа')
            request = self.player_view.request()
        request = int(request)

        #Случай, когда игрок прячется
        if request == 1:
            if random.randrange(1, 11) <= 5:
                self.player_view.response('Ваша маскировка раскрыта, при перемещении в любую локацию вас будут узнавать.')
                self.player.compromised_disguises.append(self.player.disguise)
                return True
            else:
                with open('save_file.dat', 'wb') as f:
                    pickle.dump([self.locator.get_challenges(), player_lvl], f, protocol=2)
                self.player_view.response('Вы умерли. Миссия провалена.')
                return sys.exit()
        
        #Случай, когда игрок вступает в открытый бой
        elif request == 2:
            for enemy in enemies:
                while enemy.alive == True:
                    weapons = [self.locator.get_items().get_by_name('Нет предмета')]

                    #Определяет, какие предметы игрока являются оружием
                    for i in self.player.inventory:
                        if i.weapon == True:
                            weapons.append(i)
                    result_string = 'Выберите оружие:\n\n'
                    for i in range(len(weapons)):
                        result_string += f'{i + 1}. {weapons[i].name}\n'
                    self.player_view.response(result_string)
                    request = self.player_view.request()
                    while request.isdigit() == False:
                        self.player_view.response('Введите номер ответа')
                        request = self.player_view.request()
                    request = int(request)
                    current_weapon = weapons[request - 1]
                    actions = []
                    result_string = ''

                    #Выбор действия игрока
                    for i in range(len(current_weapon.usage) - 1):
                        if current_weapon.usage[i] == 'Выстрелить':
                            actions.append('Выстрелить (9/10)\n')
                        elif current_weapon.usage[i] == 'Ударить':
                            actions.append('Ударить (5/10)\n')
                        elif current_weapon.usage[i] == 'Бросить':
                            actions.append('Бросить (7/10)\n')
                        elif current_weapon.usage[i] == 'Ударить (летально)':
                            actions.append('Ударить (летально) (6/10)\n')
                        elif current_weapon.usage[i] == 'Бросить (летально)':
                            actions.append('Бросить (летально) (8/10)\n')
                        elif current_weapon.usage[i] == 'Усмирить':
                            actions.append('Усмирить (3/10)\n')
                        elif current_weapon.usage[i] == 'Задушить':
                            actions.append('Задушить (4/10)\n')
                    for i in range(len(actions)):
                        result_string += f'{i + 1}. {actions[i]}'
                    self.player_view.response(result_string)
                    request = self.player_view.request()
                    while request.isdigit() == False:
                        self.player_view.response('Введите номер ответа')
                        request = self.player_view.request()
                    request = int(request)

                    #Удаление предмета из инвентаря при броске
                    if actions[request - 1][:7] == 'Бросить':
                        self.player.inventory.remove(current_weapon)
                        self.player.current_location.set_items(self.player.current_location.get_items() + [self.player.item])

                    #Случай, когда игроку повезло
                    if random.randrange(11) <= int(actions[request - 1][-6]):
                        enemy.alive = False
                        if self.locator.location_witnesses(self.player.current_location.get_name()) > 0:
                            current_bodies += 1
                        if current_weapon.deadly == True:
                            current_kills += 1
                    
                    #Случай, когда игроку не повезло
                    else:
                        self.player.health -= 25
                        if self.player.health != 0:
                            self.player_view.response(f'{enemy.get_name()} нанес вам удар.')
                        else:
                            with open('save_file.dat', 'wb') as f:
                                pickle.dump([self.locator.get_challenges(), player_lvl], f, protocol=2)
                            self.player_view.response('Вы умерли. Миссия провалена.')
                            return sys.exit()
                self.player_view.response(f'{enemy.get_name()} обезврежен.')
            
            #Добавление убийтв невинных и найденных тел в основной счетчик
            bodies[0] += current_bodies
            kills[0] += current_kills
            self.player_view.response(f'Убийств невинных: {current_kills}\nТел найдено: {current_bodies}')
            return True