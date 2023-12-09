import pickle
import sys

from hitman.view.player_view import PlayerView
from hitman.model.player.player import Player
from hitman.view.console_view import ConsoleView
from hitman.model.hokkaido.hokkaido_locator import HokkaidoLocator

class PlayerController():

    def __init__(self,
                 player=Player(HokkaidoLocator().get_init_location()),
                 player_view:PlayerView=None,
                 locator=HokkaidoLocator(),
                 location_name=None):

        if player_view:
            self.player_view = player_view
        else:
            self.player_view = ConsoleView()
        if locator:
            self.__locator = locator
        self.player = player
        if location_name:
            player.set_location(self.__locator.get_location_by_name(location_name))


    
    def search(self):
        for i in self.player.current_location.get_items():
            self.player.inventory.append(i)
        self.player.current_location.set_items([])
        return self.inventory()
    
    def status(self):
        global time
        global targets
        self.player_view.response(f'1. Статус {self.player.current_location.__name}\n2. Общий статус')
        request = self.player_view.request()
        while request.isdigit() == False:
            self.player_view.response('Введите номер ответа')
            request = self.player_view.request()
        request = int(request)
        if request == 2:
            result_string = ''
            for i in range(len(targets)):
                if list(targets.values())[i] == 1:
                    result_string += f'{list(targets.keys())[0].__name}: {list(targets.keys())[0].move.__name}\n'
                else:
                    result_string += f'{list(targets.keys())[0].__name}: Цель устранена\n'
            result_string += f'\n\nТекущая маскировка: {self.disguise}\n'
            result_string += f'Предмет в руках: {self.item.__name}'
            return self.player_view.response(result_string)
    
    def inventory(self):
        inventory = []
        result_string = ''
        for i in objects:
            if self.inventory.count(i) > 0:
                if i == pistol or i == silenced_pistol:
                    inventory.append(i.__name + ' (1)')
                else:
                    inventory.append(i.__name + ' (' + str(self.inventory.count(i)) + ')')
        inventory.append('Убрать предмет из рук')
        inventory.append(self.disguise)
        for i in range(len(inventory)-2):
            result_string += f'{str(i+1)+".", inventory[i]}\n'
        result_string += f'\nСейчас в руках: {self.item.__name}\n'
        result_string += f'{len(inventory)-1}. Убрать предмет из рук\n'
        result_string += f'\n{len(inventory)}. {self.disguise}'
        self.player_view.response(result_string)
        request = self.player_view.request()
        if request.isdigit():
            request = int(request)
        else:
            if request.upper() == 'W':
                return self.move()
            elif request.upper() == 'E':
                return self.search()
            elif request.upper() == 'S':
                return self.status()
            elif request.upper() == 'F':
                return self.interact()
            elif request.upper() == 'Q':
                with open('save_file.dat', 'wb') as f:
                    pickle.dump([i for i in challenges] + [player_lvl], f, protocol=2)
                sys.exit()
            else:
                return self.inventory()
        if inventory[request-1] == self.player.disguise:
            result_string = ''
            for i in range(len(self.player.found_disguises)):
                result_string += f'{str(i+1)+".", self.player.found_disguises[i]}\n'
            self.player_view.response(result_string)
            request = self.player_view.request()
            while request.isdigit() == False:
                self.player_view.response('Введите номер ответа')
                request = self.player_view.request()
            request = int(request)
            self.player.disguise = self.player.found_disguises[t-1]
            return self.player_view.response(f'Текущая маскировка: {self.player.disguise}')
        elif inventory[t-1] == 'Убрать предмет из рук':
            self.player.item = arms
            return self.player_view.response(f'Сейчас в руках: {self.player.item.__name}')
        elif item_by_name(inventory[t-1][:-4]).illegal:
            if self.player.disguise == 'Охранник' or self.player.disguise == 'Телохранитель':
                self.player.item = item_by_name(inventory[t-1][:-4])
                return self.player_view.response(f'Сейчас в руках: {self.player.item.__name}')
            else:
                self.player_view.response(f'{inventory[t-1][:-4]} -- это нелегальный прдмет. Достать предмет?\n1. Да\n2. Нет')
                request = self.player_view.request()
                while request.isdigit() == False:
                    self.player_view.response('Введите номер ответа')
                    request = self.player_view.request()
                request = int(request)
                if request == 1:
                    self.player.item = item_by_name(inventory[t-1][:-4])
                    return self.player_view.response(f'Сейчас в руках: {self.player.item.__name}')
                else:
                    return self.inventory()
        else:
            self.player.item = item_by_name(inventory[t-1][:-4])
            return self.player_view.response(f'Сейчас в руках: {self.player.item.__name}')
    
    def see_challenges(self):
        global challenges
        result_string = ''
        for i in range(len(challenges)):
            if challenges[i].completed == True:
                result_string += f"{i+1}. {challenges[i].__name + ' (выполнено)'}\n"
            else:
                result_string += f'{i+1}. {challenges[i].__name}\n'
        result_string += f'\n\n{len(challenges) + 1}. Выйти'
        self.player_view.response(result_string)
        request = self.player_view.request()
        while request.isdigit() == False:
            self.player_view.response('Введите номер ответа')
            request = self.player_view.request()
        request = int(request)
        if request > len(challenges):
            return self.player_view.response(self.player.current_location.location_status())
        else:
            self.player_view.response(f'{challenges[request-1].__name}\n\n{challenges[request - 1].description}\n\n1. Назад')
            self.player_view.request()
            return(self.see_challenges())
        
    def move(self):
        global bodies
        global suspicion_count
        result_string = ''
        for i in range(len(self.player.current_location.__locations)):
            result_string += f"{(str(i+1)+'.',self.player.current_location.__locations[i + 1])}\n"
        result_string += (f'\n{len(self.player.current_location.__locations) + 1}. Отменить действие')
        self.player_view.response(result_string)
        request = self.player_view.request()
        while request.isdigit() == False:
            self.player_view.response('Введите номер ответа')
            request = self.player_view.request()
        request = int(request)
        if request > len(self.player.current_location.__locations):
            return self.player_view.response(self.player.current_location.location_status())
        for i in locations:
            if i.__name == self.player.current_location.__locations[request]:
                move_to_location = i
        if move_to_location.__name == 'Комната с серверами':
            if self.player.disguise == 'Директор клиники' or keycard in self.player.inventory or disposable_scrambler in self.player.inventory:
                self.player.current_location = move_to_location
                return self.player_view.response(f'{self.player.current_location.location_status()}')
            else:
                return self.player_view.response('Для входа необходима маскировка директора клиники или ключ-карта')
        else:
            if self.player.disguise in self.player.compromised_disguises:
                if self.player.current_location.find_location_npcs() != []:
                    location_npc = self.player.current_location.find_location_npcs()[random.randrange(len(self.player.current_location.find_location_npcs()))]
                    result_string = location_npc.suspicion()
                    result_string += '\n\n1. Напасть (3/10)\n2. Уйти'
                    self.player_view.response(result_string)
                    request = self.player_view.request()
                    while request.isdigit() == False:
                        self.player_view.response('Введите номер ответа')
                        request = self.player_view.request()
                    request = int(request)
                    if request == 2:
                        return self.player_view.response(f'{self.player.current_location.location_status()}')
                    else:
                        if random.randrange(1, 11) <= 3:
                            location_npc.alive = False
                            self.player.found_disguises.append(location_npc.__disguise)
                            self.player.current_location = move_to_location
                            result_string = f'Вам удалось тихо устранить {location_npc.get_name()}'
                            result_string += f'\n\n\n{self.player.current_location.location_status()}'
                            return self.player_view.response(result_string)
                        else:
                            return self.combat()
                else:
                    self.player.current_location = move_to_location
                    return self.player_view.response(f'{self.player.current_location.location_status()}')
            else:
                if (self.player.item.illegal == True and self.player.disguise != 'Охранник' and self.player.disguise != 'Телохранитель'):
                    self.player.current_location = move_to_location
                    if self.player.current_location.find_location_npcs() != []:
                        location_npc = self.player.current_location.find_location_npcs()[random.randrange(len(self.player.current_location.find_location_npcs()))]
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
                                return combat()
                        else:
                            if random.randrange(1, 11) <= 7:
                                self.player.compromised_disguises.append(self.player.disguise)
                                result_string = 'Ваша маскировка раскрыта, при перемещении в любую локацию вас будут узнавать.\n'
                                result_string += f'\n\n{self.player.current_location.location_status()}'
                                return self.player_view.response(result_string)
                else:
                    if self.player.disguise in move_to_location.__disguise:
                        self.player.current_location = move_to_location
                        return self.player_view.response(f'{self.player.current_location.location_status()}')
                    else:
                        if self.player.current_location.location_witnesses() > 10:
                            chance = 10
                        else:
                            chance = self.player.current_location.location_witnesses()
                        result_string = f'{self.player.current_location.location_status()}'
                        result_string += f'\n\nУ вас нет подходящей маскировки. Переместиться на локацию? ({10-chance}/10)\n1. Да\n2. Нет'
                        self.player_view.response(result_string)
                        request = self.player_view.request()
                        while request.isdigit() == False:
                            self.player_view.response('Введите номер ответа')
                            request = self.player_view.request()
                        request = int(request)
                        if request == 2:
                            return self.player_view.response(f'{self.player.current_location.location_status()}')
                        else:
                            if random.randrange(1,11) <= 10-chance:
                                self.player.current_location = move_to_location
                                return self.player_view.response(f'{self.player.current_location.location_status()}')
                            else:
                                if self.player.current_location.find_location_npcs() != []:
                                    location_npc = self.player.current_location.find_location_npcs()[random.randrange(len(self.player.current_location.find_location_npcs()))]
                                    result_string = location_npc.suspicion()
                                    result_string += '\n\n1. Напасть (5/10)\n2. Уйти'
                                    self.player_view.response(result_string)
                                    request = self.player_view.request()
                                    while request.isdigit() == False:
                                        self.player_view.response('Введите номер ответа')
                                        request = self.player_view.request()
                                    request = int(request)
                                    if request == 2:
                                        return self.player_view.response(f'{self.player.current_location.location_status()}')
                                    else:
                                        if random.randrange(1, 11) <= 5:
                                            if self.player.current_location.location_witnesses() > 0:
                                                bodies[0] += 1
                                            location_npc.alive = False
                                            self.player.found_disguises.append(location_npc.__disguise)
                                            self.player.current_location = move_to_location
                                            result_string = f'Вам тихо удалось устранить {location_npc.get_name()}'
                                            result_string += f'\n\n\n{self.player.current_location.location_status()}'
                                            return self.player_view.response(result_string)
                                        else:
                                            return self.combat()
                                else:
                                    self.player.current_location = move_to_location
                                    return self.player_view.response(f'{self.player.current_location.location_status()}')
                                
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