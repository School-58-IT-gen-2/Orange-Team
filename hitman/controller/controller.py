import pickle
import sys
import random

from view.player_view import PlayerView
from model.player.player_info import *
from model.player.player import Player
from view.console_view import ConsoleView
from model.hokkaido.hokkaido_locator import HokkaidoLocator
from model.common.npcs import Target


class PlayerController():

    def __init__(self,
                 player=Player(),
                 player_view:PlayerView=None,
                 locator=HokkaidoLocator()):
        
        if player_view:
            self.player_view = player_view
        else:
            self.player_view = ConsoleView()
        if locator:
            self.__locator = locator
        self.player = player
    
    def search(self):
        self.player.inventory += self.player.current_location.get_items()
        result_string = 'Найдены предметы:\n\n'
        if self.player.current_location.get_items() == []:
            return self.player_view.response('На локации нет предметов')
        else:
            for i in self.__locator.get_items().get_all():
                if i in self.player.current_location.get_items():
                    result_string += f'{i.name} ({self.player.current_location.get_items().count(i)})\n'
        self.player.current_location.set_items([])
        return self.player_view.response(result_string)
    
    def status(self):
        self.player_view.response(f'1. Статус {self.player.current_location.get_name()}\n2. Общий статус')
        request = self.player_view.request()
        while request.isdigit() == False:
            self.player_view.response('Введите номер ответа')
            request = self.player_view.request()
        request = int(request)
        if request == 2:
            result_string = ''
            for i in self.__locator.get_targets().get_all():
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
            return self.player_view.response(self.__locator.location_status(self.player.current_location))
    
    def inventory(self):
        inventory = []
        if self.player.inventory.count(self.player.item) == 0:
            self.player.item = self.__locator.get_items().get_by_name('Нет предмета')
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
        elif inventory[request - 1] == 'Убрать предмет из рук':
            self.player.item = self.__locator.get_items().get_by_name('Нет предмета')
            return self.player_view.response(f'Сейчас в руках: {self.player.item.name}')
        elif inventory[request - 1] == 'Выйти из инвентаря':
            return self.player_view.response(self.__locator.location_status(self.player.current_location))
        elif self.__locator.get_items().get_by_name(inventory[request - 1][:-4]).illegal:
            if self.player.disguise == 'Охранник' or self.player.disguise == 'Телохранитель':
                self.player.item = self.__locator.get_items().get_by_name(inventory[request - 1][:-4])
                return self.player_view.response(f'Сейчас в руках: {self.player.item.name}')
            else:
                self.player_view.response(f'{inventory[request - 1][:-4]} -- это нелегальный предмет. Достать предмет?\n\n1. Да\n2. Нет')
                second_request = self.player_view.request()
                while second_request.isdigit() == False:
                    self.player_view.response('Введите номер ответа')
                    second_request = self.player_view.request()
                second_request = int(second_request)
                if second_request == 1:
                    self.player.item = self.__locator.get_items().get_by_name(inventory[request - 1][:-4])
                    return self.player_view.response(f'Сейчас в руках: {self.player.item.name}')
                else:
                    return self.inventory()
        else:
            self.player.item = self.__locator.get_items().get_by_name(inventory[request - 1][:-4])
            return self.player_view.response(f'Сейчас в руках: {self.player.item.name}')
    
    def see_challenges(self):
        result_string = ''
        for i in range(len(self.__locator.get_challenges().get_all())):
            if self.__locator.get_challenges().get_all()[i].completed == True:
                result_string += f"{i+1}. {self.__locator.get_challenges().get_all()[i].name + ' (выполнено)'}\n"
            else:
                result_string += f'{i+1}. {self.__locator.get_challenges().get_all()[i].name}\n'
        result_string += f'\n\n{len(self.__locator.get_challenges().get_all()) + 1}. Выйти'
        self.player_view.response(result_string)
        request = self.player_view.request()
        while request.isdigit() == False:
            self.player_view.response('Введите номер ответа')
            request = self.player_view.request()
        request = int(request)
        if request > len(self.__locator.get_challenges().get_all()):
            return self.player_view.response(self.__locator.location_status(self.player.current_location))
        else:
            self.player_view.response(self.__locator.get_challenges().get_all()[request-1].challenge_info())
            self.player_view.request()
            return(self.see_challenges())
        
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
        if request == len(self.player.current_location.get_connected_locations()) + 1:
            return self.player_view.response(self.__locator.location_status(self.player.current_location))
        for i in self.__locator.get_locations():
            if i == self.player.current_location.get_connected_locations()[request]:
                move_to_location = self.__locator.get_location_by_name(i)
        if move_to_location.get_name() == 'Комната с серверами':
            if self.player.disguise == 'Директор клиники' or self.__locator.get_items().get_by_name('Ключ-карта') in self.player.inventory or self.__locator.get_items().get_by_name('Электронный дешифровщик') in self.player.inventory:
                self.player.current_location = move_to_location
                return self.player_view.response(f'{self.__locator.location_status(self.player.current_location)}')
            else:
                return self.player_view.response('Для входа необходима маскировка директора клиники или ключ-карта')
        else:
            if self.player.disguise in self.player.compromised_disguises:
                if self.__locator.find_location_npcs(self.player.current_location.get_name()) != []:
                    location_npc = self.__locator.find_location_npcs(self.player.current_location.get_name())[random.randrange(len(self.__locator.find_location_npcs(self.player.current_location.get_name())))]
                    result_string = location_npc.suspicion()
                    result_string += '\n\n1. Напасть (3/10)\n2. Уйти'
                    self.player_view.response(result_string)
                    request = self.player_view.request()
                    while request.isdigit() == False:
                        self.player_view.response('Введите номер ответа')
                        request = self.player_view.request()
                    request = int(request)
                    if request == 2:
                        return self.player_view.response(f'{self.__locator.location_status(self.player.current_location)}')
                    else:
                        if random.randrange(1, 11) <= 3:
                            location_npc.alive = False
                            self.player.found_disguises.append(location_npc.get_disguise())
                            self.player.current_location = move_to_location
                            result_string = f'Вам удалось тихо устранить {location_npc.get_name()}'
                            result_string += f'\n\n\n{self.__locator.location_status(self.player.current_location)}'
                            return self.player_view.response(result_string)
                        else:
                            return self.combat()
                else:
                    self.player.current_location = move_to_location
                    return self.player_view.response(f'{self.__locator.location_status(self.player.current_location.get_name())}')
            else:
                if (self.player.item.illegal == True and self.__locator.get_disguise_by_name(self.player.disguise) != 'Охранник' and self.__locator.get_disguise_by_name(self.player.disguise) != 'Телохранитель'):
                    self.player.current_location = move_to_location
                    if self.__locator.find_location_npcs(self.player.current_location.get_name()) != []:
                        location_npc = self.__locator.find_location_npcs(self.player.current_location.get_name())[random.randrange(len(self.__locator.find_location_npcs(self.player.current_location.get_name())))]
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
                                result_string += f'\n\n{self.__locator.location_status(self.player.current_location)}'
                                return self.player_view.response(result_string)
                            else:
                                return self.combat()
                else:
                    if self.__locator.get_disguise_by_name(self.player.disguise) in move_to_location.get_disguise():
                        self.player.current_location = move_to_location
                        return self.player_view.response(f'{self.__locator.location_status(self.player.current_location)}')
                    else:
                        if self.__locator.location_witnesses(self.player.current_location.get_name()) > 10:
                            chance = 10
                        else:
                            chance = self.__locator.location_witnesses(self.player.current_location.get_name())
                        result_string = f'\n\nУ вас нет подходящей маскировки. Переместиться на локацию? ({10-chance}/10)\n\n1. Да\n2. Нет'
                        self.player_view.response(result_string)
                        request = self.player_view.request()
                        while request.isdigit() == False:
                            self.player_view.response('Введите номер ответа')
                            request = self.player_view.request()
                        request = int(request)
                        if request == 2:
                            return self.player_view.response(f'{self.__locator.location_status(self.player.current_location)}')
                        else:
                            if random.randrange(1,11) <= 10-chance:
                                self.player.current_location = move_to_location
                                return self.player_view.response(f'{self.__locator.location_status(self.player.current_location)}')
                            else:
                                if self.__locator.find_location_npcs(self.player.current_location.get_name()) != []:
                                    location_npc = self.__locator.find_location_npcs(move_to_location.get_name())[random.randrange(len(self.__locator.find_location_npcs(move_to_location.get_name())))]
                                    result_string = location_npc.suspicion()
                                    result_string += '\n\n1. Напасть (3/10)\n2. Уйти'
                                    self.player_view.response(result_string)
                                    request = self.player_view.request()
                                    while request.isdigit() == False:
                                        self.player_view.response('Введите номер ответа')
                                        request = self.player_view.request()
                                    request = int(request)
                                    if request == 2:
                                        return self.player_view.response(f'{self.__locator.location_status(self.player.current_location)}')
                                    else:
                                        if random.randrange(1, 11) <= 3:
                                            if self.__locator.location_witnesses(move_to_location.get_name()) > 0:
                                                bodies[0] += 1
                                            location_npc.alive = False
                                            self.player.found_disguises.append(location_npc.get_disguise())
                                            self.player.current_location = move_to_location
                                            result_string = f'Вам удалось тихо устранить {location_npc.get_name()}'
                                            result_string += f'\n\n\n{self.__locator.location_status(self.player.current_location)}'
                                            return self.player_view.response(result_string)
                                        else:
                                            return self.combat()
                                else:
                                    self.player.current_location = move_to_location
                                    return self.player_view.response(f'{self.__locator.location_status(self.player.current_location)}')
    
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
        self.player.current_location = self.__locator.get_location_by_name(self.player.current_location.get_connected_locations()[request])
        return self.player_view.response(self.__locator.location_status(self.player.current_location))
                                
    def interact(self):
        global bodies
        global kills
        witnesses = self.__locator.location_witnesses(self.player.current_location.get_name())
        location_npcs = self.__locator.find_location_npcs(self.player.current_location.get_name())
        if self.player.inventory.count(self.player.item) == 0:
            self.player.item = self.__locator.get_items().get_by_name('Нет предмета')
        result_string = f'Действия видят {witnesses} человек\n\n'
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
            if self.player.item.usage[request - 1] == 'Выстрелить':
                for i in self.__locator.get_targets().get_all():
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
                    result_string += self.__locator.get_challenges().get_by_name('Точный выстрел').achieved()
                    if location_npcs[request - 1].get_name() == 'Эрих Содерс':
                        result_string += f'\n\n{self.__locator.get_challenges().get_by_name('Личное прощание').achieved()}'
                    result_string += f'\n\nДиана: С {location_npcs[request - 1].get_name()} покончено, отличная работа.'
                    self.player_view.response(result_string)
                else:
                    kills[0] += 1
                    self.player.found_disguises.append(location_npcs[request - 1].get_disguise())
                if witnesses > 0:
                    bodies[0] += 1
                    return self.combat()
                else:
                    return self.player_view.response(self.__locator.location_status(self.player.current_location))
            elif self.player.item.usage[request - 1] == 'Отменить действие':
                return self.player_view.response(self.__locator.location_status(self.player.current_location))
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
                    return self.player_view.response(self.__locator.location_status(self.player.current_location))
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
                    return self.player_view.response(self.__locator.location_status(self.player.current_location))
            elif self.player.item.usage[request - 1] == 'Ударить (летально)':
                for i in self.__locator.get_targets().get_all():
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
                    return self.player_view.response(self.__locator.location_status(self.player.current_location))
            elif self.player.item.usage[request - 1] == 'Бросить (летально)':
                self.player.current_location.set_items(self.player.current_location.get_items() + [self.player.item])
                self.player.inventory.remove(self.player.item)
                for i in self.__locator.get_targets().get_all():
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
                    return self.player_view.response(self.__locator.location_status(self.player.current_location))
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
                        if self.player.item == self.__locator.get_items().get_by_name('Монета'):
                            self.player.current_location.set_items(self.player.current_location.get_items() + [self.player.item])
                        return self.safe_move()
                    else:
                        return self.player_view.response(self.__locator.location_status(self.player.current_location))
                if self.player.item == self.__locator.get_items().get_by_name('Монета'):
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
                        return self.player_view.response(self.__locator.location_status(self.player.current_location))
                    elif second_request == 2:
                        kills[0] += 1
                        return self.player_view.response(self.__locator.location_status(self.player.current_location))
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
                    return self.player_view.response(self.__locator.location_status(self.player.current_location))
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
                            return self.player_view.response(self.__locator.location_status(self.player.current_location))
                        elif request == 1:
                            self.player_view.response('\n\n1. Выйти\n2. Повредить сердце')
                            request = self.player_view.request()
                            while request.isdigit() == False:
                                self.player_view.response('Введите номер ответа')
                                request = self.player_view.request()
                            request = int(request)
                            if request == 1:
                                return self.player_view.response(self.__locator.location_status(self.player.current_location))
                            elif request == 2:
                                self.__locator.get_targets().get_by_name('Эрих Содерс').alive = False
                                result_string = f'{self.__locator.get_challenges().get_by_name('Бессердечный').achieved()}\n\n'
                                result_string += 'Диана: 47-й, без сердца для пересадки Содерс не выживет. Ты смог от него избавиться даже не прикасаясь, изящный ход.'
                                self.player_view.response(result_string)
                                return self.player_view.response(self.__locator.location_status(self.player.current_location))
                    else:
                        return self.player_view.response('Вне зоны действия')
            elif self.player.item.usage[request - 1] == 'Задушить':
                for i in self.__locator.get_targets().get_all():
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
                    return self.player_view.response(self.__locator.location_status(self.player.current_location))

    def combat(self):
        pass

def combat():
    global kills
    global bodies
    global player_lvl
    global combat_count
    current_kills = 0
    current_bodies = 0
    enemies = []
    for i in find_location_npcs(player.current_location):
        if i.guard == True:
            enemies.append(i)
    if enemies == []:
        return location_status(player.current_location)
    combat_count[0] += 1
    buttons = ['A', 'D', 'W', 'X', 'S', 'Q', 'E', 'Z']
    print(f'\n\nНачался бой\n1. Прятаться (5/10)\n2. Напасть')
    t = input()
    while t.isdigit() == False:
        t = input()
    t = int(t)
    if t == 1:
        if random.randrange(1, 11) <= 5:
            print('\n\nВаша маскировка раскрыта, при перемещении в любую локацию вас будут узнавать.')
            player.compromised_disguises.append(player.__disguise)
            return player.__disguise
        else:
            with open('save_file.dat', 'wb') as f:
                pickle.dump([smoking_kills, stretch, personal_goodbye, no_smoking, human_error, suit_only, silent_assasin, sauna_assasination, sushi, heartless, silent_assasin_suit_only, no_evidence, ghost_machine, straight_shot, hold_hair, piano_man, hurt_oneself, tasteless, master_assasin, player_lvl], f, protocol=2)
            print('\n\nВы умерли. Миссия провалена.')
            sys.exit()
    elif t == 2:
        for i in enemies:
            enemy_health = 100
            while enemy_health > 0:
                current_button = random.choice(buttons)
                crit = random.randint(1,11)
                if pistol in player.inventory or silenced_pistol in player.inventory:
                    print('\n\n1. Использовать пистолет\n2. Не использовать')
                    t = input()
                    while t.isdigit() == False:
                        t = input()
                    t = int(t)
                    if t == 2:
                        print(f'\n\nНажимайте как можно быстрее: {current_button}')
                        s_time = tm.time()
                        t = input()
                        e_time = tm.time()
                        if e_time - s_time <= 2 and t.upper() == current_button:
                            if crit <= 5:
                                enemy_health -= 50 
                            else:
                                enemy_health -= 25
                        else:
                            player.health -= 25
                            if player.health != 0:
                                print('\n\nПромах. Вы пропустили удар.')
                            else:
                                with open('save_file.dat', 'wb') as f:
                                    pickle.dump([smoking_kills, stretch, personal_goodbye, no_smoking, human_error, suit_only, silent_assasin, sauna_assasination, sushi, heartless, silent_assasin_suit_only, no_evidence, ghost_machine, straight_shot, hold_hair, piano_man, hurt_oneself, tasteless, master_assasin, player_lvl], f, protocol=2)
                                print('\n\nВы умерли. Миссия провалена.')
                                sys.exit()
                    if t == 1:
                        current_kills += 1
                        print(f'\n\nНажимайте как можно быстрее: {current_button}')
                        s_time = tm.time()
                        t = input()
                        e_time = tm.time()
                        if e_time - s_time <= 2 and t.upper() == current_button:
                            if crit <= 5:
                                enemy_health -= 100 
                            else:
                                enemy_health -= 50
                        else:
                            player.health -= 25
                            if player.health != 0:
                                print('\n\nПромах. Вы пропустили удар.')
                            else:
                                with open('save_file.dat', 'wb') as f:
                                    pickle.dump([smoking_kills, stretch, personal_goodbye, no_smoking, human_error, suit_only, silent_assasin, sauna_assasination, sushi, heartless, silent_assasin_suit_only, no_evidence, ghost_machine, straight_shot, hold_hair, piano_man, hurt_oneself, tasteless, master_assasin, player_lvl], f, protocol=2)
                                print('\n\nВы умерли. Миссия провалена.')
                                sys.exit()
                else:
                    print(f'\n\nНажимайте как можно быстрее: {current_button}')
                    s_time = tm.time()
                    t = input()
                    e_time = tm.time()
                    if e_time - s_time <= 2 and t.upper() == current_button:
                        if crit <= 5:
                            enemy_health -= 50 
                        else:
                            enemy_health -= 25
                    else:
                        player.health -= 25
                        if player.health != 0:
                            print('\n\nПромах. Вы пропустили удар.')
                        else:
                            with open('save_file.dat', 'wb') as f:
                                    pickle.dump([player_lvl], f, protocol=2)
                            print('\n\nВы умерли. Миссия провалена.')
                            sys.exit()
                enemy_attack = random.randint(1,10)
                if enemy_attack > 7 :
                    current_button = random.choice(buttons)
                    print(f'\n\n{i.print_name()} атакует, нажимайте как можно быстрее: {current_button}')
                    s_time = tm.time()
                    t = input()
                    e_time = tm.time()
                    if e_time - s_time <= 2 and t.upper() == current_button:
                        print('\n\nВы увернулись')
                    else:
                        player.health -= 25
                        if player.health != 0:
                            print('\n\nВы пропустили удар')
                        else:
                            with open('save_file.dat', 'wb') as f:
                                    pickle.dump([player_lvl], f, protocol=2)
                            print('\n\nВы умерли. Миссия провалена.')
                            sys.exit()
            print(f'\n\n{i.print_name()} обезврежен')
            tm.sleep(2)
            i.alive = False
            player.found_disguises.append(i.__disguise)
            if location_witnesses(player.current_location) > 0:
                current_bodies += 1
        bodies[0] += current_bodies
        kills[0] += current_kills
        print('\n\nУбийств невинных:', current_kills)
        return f'Тел найдено: {current_bodies}'