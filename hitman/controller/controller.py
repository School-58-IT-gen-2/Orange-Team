import pickle
import sys
import random

from view.player_view import PlayerView
from model.player.player_info import *
from model.player.player import Player
from view.console_view import ConsoleView
from model.hokkaido.hokkaido_locator import HokkaidoLocator

class PlayerController():

    def __init__(self,
                 player=Player(location=HokkaidoLocator().get_location_by_name('Номер 47-го')),
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
            for i in self.player.current_location.get_items():
                result_string += f'{i.name}\n'
        self.player.current_location.set_items([])
        return self.player_view.response(result_string)
    
    def status(self):
        global time
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
            return self.player_view.response(result_string)
    
    def inventory(self):
        inventory = []
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
            if self.__locator.get_disguise_by_name(self.player.disguise) == 'Директор клиники' or self.__locator.get_items().get_by_name('Ключ-карта') in self.player.inventory or self.__locator.get_items().get_by_name('Электронный дешифровщик') in self.player.inventory:
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
                        result_string = f'\n\nУ вас нет подходящей маскировки. Переместиться на локацию? ({10-chance}/10)\n1. Да\n2. Нет'
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
                                
def interact():
    global bodies
    global kills
    global yuki
    global soders
    global target_status
    witnesses = location_witnesses(player.current_location)
    location_npcs = find_location_npcs(player.current_location)
    if player.inventory.count(player.item) == 0:
        player.item = arms
    print(f'\n\nДействия видят {witnesses} человек\n')
    if player.item.usage == []:
        return '\n\nНет действий с этим предметом'
    else:
        for i in range(len(player.item.usage)):
            print(f'{i+1}. {player.item.usage[i]}')
        t = input()
        while t.isdigit() == False:
            t = input()
        t = int(t)
        if player.item.usage[t-1] == 'Выстрелить':
            if ((target_status[int(time[0])%9] == player.current_location.__name) and (yuki[0] == 1)):
                print(f'\n\n1. Выстрелить в Юки Ямадзаки')
                for i in range(1, len(location_npcs)):
                    print(f'{i+1}. Выстрелить в {location_npcs[i].print_name()}')
            elif (player.current_location.__name == 'Операционная') and (soders[0] == 1):
                print(f'\n\n1. Выстрелить в Эрих Содерс')
                for i in range(1, len(location_npcs)):
                    print(f'{i+1}. Выстрелить в {location_npcs[i].print_name()}')
            else:
                if location_npcs == []:
                    return '\n\nНа локации никого нет'
                print('\n')
                for i in range(len(location_npcs)):
                    print(f'{i+1}. Выстрелить в {location_npcs[i].print_name()}')
            t = input()
            while t.isdigit() == False:
                t = input()
            t = int(t)
            if ((target_status[int(time[0])%9] == player.current_location.__name) and (yuki[0] == 1)) and t == 1:
                print(straight_shot.achieved())
                yuki[0] = 0
                if witnesses > 0:
                    bodies[0] += 1
                    return combat()
                else:
                    return '\n\nДиана: С Юки Ямадзаки покончено, отличная работа.'
            elif (player.current_location.__name == 'Операционная') and (soders[0] == 1) and t == 1:
                print(straight_shot.achieved())
                print(personal_goodbye.achieved())
                soders[0] = 0
                if witnesses > 0:
                    bodies[0] += 1
                    return combat()
                else:
                    return '\n\nДиана: Содерс нас больше не побеспокоит, отличная работа.'
            else:
                location_npcs[t-1].alive = False
                player.found_disguises.append(location_npcs[t-1].__disguise)
                if witnesses > 0:
                    bodies[0] += 1
                    kills[0] += 1
                    return combat()
                else:
                    kills[0] += 1
                    return location_status(player.current_location)
        elif player.item.usage[t-1] == 'Отменить действие':
            return location_status(player.current_location)
        elif player.item.usage[t-1] == 'Ударить':
            if location_npcs == []:
                    return '\n\nНа локации никого нет'
            print('\n')
            for i in range(len(location_npcs)):
                    print(f'{i+1}. Ударить {location_npcs[i].print_name()}')
            t = input()
            while t.isdigit() == False:
                t = input()
            t = int(t)
            location_npcs[t-1].alive = False
            player.found_disguises.append(location_npcs[t-1].__disguise)
            if witnesses > 0:
                bodies[0] += 1
                return combat()
            else:
                return location_status(player.current_location)
        elif player.item.usage[t-1] == 'Бросить':
            if location_npcs == []:
                    return '\n\nНа локации никого нет'
            print('\n')
            player.current_location.__items.append(player.item)
            player.inventory.remove(player.item)
            for i in range(len(location_npcs)):
                    print(f'{i+1}. Бросить в {location_npcs[i].print_name()}')
            t = input()
            while t.isdigit() == False:
                t = input()
            t = int(t)
            location_npcs[t-1].alive = False
            player.found_disguises.append(location_npcs[t-1].__disguise)
            if witnesses > 0:
                bodies[0] += 1
                return combat()
            else:
                return location_status(player.current_location)
        elif player.item.usage[t-1] == 'Ударить (летально)':
            if ((target_status[int(time[0])%9] == player.current_location.__name) and (yuki[0] == 1)):
                print(f'\n\n1. Ударить Юки Ямадзаки')
                for i in range(1, len(location_npcs)):
                    print(f'{i+1}. Ударить {location_npcs[i].print_name()}')
            else:
                if location_npcs == []:
                    return '\n\nНа локации никого нет'
                print('\n')
                for i in range(len(location_npcs)):
                    print(f'{i+1}. Ударить {location_npcs[i].print_name()}')
            t = input()
            while t.isdigit() == False:
                t = input()
            t = int(t)
            if ((target_status[int(time[0])%9] == player.current_location) and (yuki[0] == 1)) and t == 1:
                yuki[0] = 0
                if witnesses > 0:
                    bodies[0] += 1
                    return combat()
                else:
                    return '\n\nДиана: С Юки Ямадзаки покончено, отличная работа.'
            else:
                location_npcs[t-1].alive = False
                player.found_disguises.append(location_npcs[t-1].__disguise)
                if witnesses > 0:
                    bodies[0] += 1
                    kills[0] += 1
                    return combat()
                else:
                    kills[0] += 1
                    return location_status(player.current_location)
        elif player.item.usage[t-1] == 'Бросить (летально)':
            player.current_location.__items.append(player.item)
            player.inventory.remove(player.item)
            if ((target_status[int(time[0])%9] == player.current_location.__name) and (yuki[0] == 1)):
                print(f'\n\n1. Бросить в Юки Ямадзаки')
                for i in range(1, len(location_npcs)):
                    print(f'{i+1}. Бросить в {location_npcs[i].print_name()}')
            else:
                if location_npcs == []:
                    return '\n\nНа локации никого нет'
                print('\n')
                for i in range(len(location_npcs)):
                    print(f'{i+1}. Бросить в {location_npcs[i].print_name()}')
            t = input()
            while t.isdigit() == False:
                t = input()
            t = int(t)
            if ((target_status[int(time[0])%9] == player.current_location) and (yuki[0] == 1)) and t == 1:
                yuki[0] = 0
                if witnesses > 0:
                    bodies[0] += 1
                    return combat()
                else:
                    return '\n\nДиана: С Юки Ямадзаки покончено, отличная работа.'
            else:
                location_npcs[t-1].alive = False
                player.found_disguises.append(location_npcs[t-1].__disguise)
                if witnesses > 0:
                    bodies[0] += 1
                    kills[0] += 1
                    return combat()
                else:
                    kills[0] += 1
                    return location_status(player.current_location)
        elif player.item.usage[t-1] == 'Бросить для отвлечения':
            if location_npcs == []:
                    return '\n\nНа локации никого нет'
            if witnesses > 3:
                print('\n\nНа локации слишком много свидетелей\n')
                print('1. Отвлечь для перемещения\n2. Отменить действие')
                t = input()
                while t.isdigit() == False:
                    t = input()
                t = int(t)
                if t == 1:
                    player.inventory.remove(player.item)
                    return safe_move()
                else:
                    print('\n\n')
                    return player.current_location.__name
            if player.item == coin:
                player.current_location.__items.append(player.item)
            player.inventory.remove(player.item)
            print('\n')
            for i in range(len(location_npcs)):
                    print(f'{i+1}. Отвлечь {location_npcs[i].print_name()}')
            print(f'{len(location_npcs)+1}. Отвлечь для перемещения')
            t = input()
            while t.isdigit() == False:
                t = input()
            t = int(t)
            if t > len(location_npcs):
                return safe_move()
            else:
                print(f'\n\n1. Вырубить {location_npcs[t-1].print_name()}\n2. Убить {location_npcs[t-1].print_name()}')
                x = input()
                while x.isdigit() == False:
                    x = input()
                x = int(x)
                if x == 1:
                    player.found_disguises.append(location_npcs[t-1].__disguise)
                    location_npcs[t-1].alive = False
                    return location_status(player.current_location)
                if x == 2:
                    kills[0] += 1
                    location_npcs[t-1].alive = False
                    player.found_disguises.append(location_npcs[t-1].__disguise)
                    return location_status(player.current_location)
        elif player.item.usage[t-1] == 'Усмирить':
            if location_npcs == []:
                    return '\n\nНа локации никого нет'
            print('\n')
            for i in range(len(location_npcs)):
                    print(f'{i+1}. Усмирить {location_npcs[i].print_name()}')
            t = input()
            while t.isdigit() == False:
                t = input()
            t = int(t)
            location_npcs[t-1].alive = False
            player.found_disguises.append(location_npcs[t-1].__disguise)
            if witnesses > 0:
                bodies[0] += 1
                return combat()
            else:
                return location_status(player.current_location)
        elif player.item.usage[t-1] == 'Использовать':
            if player.current_location == morgue:
                player.inventory.remove(player.item)
                print('\n\nНейрочип подействовал на одного из работников морга и тот отправился в комнату, где хранится сердце, которое должны пересадить Эриху Содерсу. Последовать за ним?\n1. Да\n2. Нет')
                t = input()
                while t.isdigit() == False:
                    t = input()
                t = int(t)
                if t == 2:
                    return player.current_location.__name
                elif t == 1:
                    print('\n\n1. Выйти\n2. Повредить сердце')
                    t = input()
                    while t.isdigit() == False:
                        t = input()
                    t = int(t)
                    if t == 1:
                        return player.current_location.__name
                    elif t == 2:
                        print(heartless.achieved())
                        soders[0] = 0
                        print('\n\nДиана: 47-й, без сердца для пересадки Содерс не выживет. Ты смог от него избавиться даже не прикасаясь, изящный ход.')
                        return location_status(player.current_location)
            else:
                return '\n\nВне зоны действия'
        elif player.item.usage[t-1] == 'Задушить':
            if ((target_status[int(time[0])%9] == player.current_location.__name) and (yuki[0] == 1)):
                print(f'\n\n1. Задушить Юки Ямадзаки')
                for i in range(1, len(location_npcs)):
                    print(f'{i+1}. Задушить {location_npcs[i].print_name()}')
            else:
                if location_npcs == []:
                    return '\n\nНа локации никого нет'
                print('\n')
                for i in range(len(location_npcs)):
                    print(f'{i+1}. Задушить {location_npcs[i].print_name()}')
            t = input()
            while t.isdigit() == False:
                t = input()
            t = int(t)
            if ((target_status[int(time[0])%9] == player.current_location.__name) and (yuki[0] == 1)) and t == 1:
                print(piano_man.achieved())
                yuki[0] = 0
                if witnesses > 0:
                    bodies[0] += 1
                    return combat()
                else:
                    return '\n\nДиана: С Юки Ямадзаки покончено, отличная работа.'
            else:
                location_npcs[t-1].alive = False
                player.found_disguises.append(location_npcs[t-1].__disguise)
                if witnesses > 0:
                    bodies[0] += 1
                    kills[0] += 1
                    return combat()
                else:
                    kills[0] += 1
                    return location_status(player.current_location)
    
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

def safe_move():
    global time
    print('\n')
    for i in range(len(player.current_location.__locations)):
        print(str(i+1) +'.', player.current_location.__locations[i + 1])
    t = input()
    while t.isdigit() == False:
        t = input()
    t = int(t)
    player.current_location = location_by_name(player.current_location.__locations[t])
    return f'\n\n{player.current_location.__name}'