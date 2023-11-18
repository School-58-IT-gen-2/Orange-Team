import random
import sys
import time as tm
from Settings.locations import *
from Settings.setup import *

def interact():
    global witnesses
    global target_status
    global time
    global yuki
    global soders
    global location_status
    global current_location
    global bodies
    global kills
    global found_disguise
    global current_item
    global current_inventory
    if current_inventory.count(current_item) == 0:
        current_item = 'Нет предмета'
    t = location_status[current_location]
    start = t[0]
    end = t[1]
    witnesses = random.randrange(start,end)
    print(f'\n\nДействия видят {witnesses} человек\n')
    item_use = item_usage[current_item]
    if item_use == []:
        return 'Нет действий с этим предметом'
    else:
        for i in range(len(item_use)):
            print(f'{i+1}. {item_use[i]}')
    t = input()
    if t.isdigit():
        t = int(t)
        if item_use[t-1] == 'Выстрелить':
            if ((target_status[int(time)%9] == current_location) and (yuki == 1)):
                print('\n\n1. Выстрелить в цель\n2. Выстрелить в охранника')
                t = input()
                while t.isdigit() == False:
                    t = input()
                t = int(t)
                if t == 1:
                    yuki = 0
                    if witnesses > 0:
                        bodies += 1
                        return combat()
                    else:
                        return combat()
                elif t == 2:
                    kills += 1
                    if witnesses > 0:
                        bodies += 1
                        return combat()
                    else:
                        for i in range(2, len(location_status[current_location])):
                            found_disguise.append(location_status[current_location][i])
                        return combat()
            elif (current_location == 'Операционная') and (soders == 1):
                print('\n\n1. Выстрелить в цель\n2. Выстрелить в охранника')
                t = input()
                while t.isdigit() == False:
                    t = input()
                t = int(t)
                if t == 1:
                    soders = 0
                    return combat()
                elif t == 2:
                    bodies += 1
                    kills += 1
                    return combat()
            else:
                kills += 1
                if witnesses > 0:
                    bodies += 1
                    return combat
                else:
                    for i in range(2, len(location_status[current_location])):
                            found_disguise.append(location_status[current_location][i])
                    return status()
        elif item_use[t-1] == 'Отменить действие':
            return status()
        elif item_use[t-1] == 'Ударить':
            if witnesses == 0:
                for i in range(2, len(location_status[current_location])):
                            found_disguise.append(location_status[current_location][i])
                return status()
            else:
                for i in range(2, len(location_status[current_location])):
                            found_disguise.append(location_status[current_location][i])
                return combat()
        elif item_use[t-1] == 'Бросить':
            objects_room[current_location].append(current_item)
            current_inventory.remove(current_item)
            if witnesses == 0:
                for i in range(2, len(location_status[current_location])):
                            found_disguise.append(location_status[current_location][i])
                return status()
            else:
                for i in range(2, len(location_status[current_location])):
                            found_disguise.append(location_status[current_location][i])
                return combat()
        elif item_use[t-1] == 'Ударить (летально)':
            if ((target_status[int(time)%9] == current_location) and (yuki == 1)):
                print('1. Атакова цель\n2. Атаковать охранника')
                t = input()
                while t.isdigit() == False:
                    t = input()
                t = int(t)
                if t == 1:
                    yuki = 0
                    if witnesses > 0:
                        bodies += 1
                        return combat()
                    else:
                        return status()
                elif t == 2:
                    kills += 1
                    if witnesses > 0:
                        bodies += 1
                        return combat()
                    else:
                        for i in range(2, len(location_status[current_location])):
                            found_disguise.append(location_status[current_location][i])
                        return status()
        elif item_use[t-1] == 'Бросить (летально)':
            if ((target_status[int(time)%9] == current_location) and (yuki == 1)):
                objects_room[current_location].append(current_item)
                current_inventory.remove(current_item)
                print('\n\n1. Атакова цель\n2. Атаковать охранника')
                t = input()
                while t.isdigit() == False:
                    t = input()
                t = int(t)
                if t == 1:
                    yuki = 0
                    if witnesses > 0:
                        
                        bodies += 1
                        return combat()
                    else:
                        return status()
                elif t == 2:
                    kills += 1
                    if witnesses > 0:
                        bodies += 1
                        return combat()
                    else:
                        for i in range(2, len(location_status[current_location])):
                            found_disguise.append(location_status[current_location][i])
                            return status()
            else:
                kills += 1
                if witnesses > 0:
                    bodies += 1
                    return combat()
                else:
                    for i in range(2, len(location_status[current_location])):
                        found_disguise.append(location_status[current_location][i])
                        return status()
        elif item_use[t-1] == 'Бросить для отвлечения':
            if current_item == 'Монета':
                objects_room[current_location].append(current_item)
            current_inventory.remove(current_item)
            return safe_move()
        elif item_use[t-1] == 'Усмирить':
            if witnesses == 0:
                for i in range(2, len(location_status[current_location])):
                            found_disguise.append(location_status[current_location][i])
                return status()
            else:
                for i in range(2, len(location_status[current_location])):
                            found_disguise.append(location_status[current_location][i])
                return combat()
        elif item_use[t-1] == 'Использовать':
            if current_location == 'Морг':
                current_inventory.remove(current_item)
                print('\n\nНейрочип подействовал на одного из работников морга и тот отправился в комнату, где хранится сердце, которое должны пересадить Эриху Содерсу. Последовать за ним?\n1. Да\n2. Нет')
                t = input()
                while t.isdigit() == False:
                    t = input()
                t = int(t)
                if t == 2:
                    return current_location
                elif t == 1:
                    print('\n\n1. Выйти\n2. Повредить сердце')
                    t = input()
                    while t.isdigit() == False:
                        t = input()
                    t = int(t)
                    if t == 1:
                        return current_location
                    elif t == 2:
                        soders = 0
                        print('\n\nДиана: 47-й, без сердца для пересадки Содерс не выживет. Ты смог от него избавиться даже не прикасаясь, изящный ход.')
                        return current_location
            else:
                return '\n\nВне зоны действия'
    else:
        if t == 'w' or t == 'W':
            return move()
        elif t == 'i' or t == 'I':
            return inventory()
        elif t == 'e' or t == 'e':
            return search()
        elif t == 's' or t == 's':
            return status()    
def status():
    global location_status
    global current_location
    t = location_status[current_location]
    if len(t) > 2:
        print(f'\n\n{current_location}')
        print('На локации можно получить маскировки:')
        for i in range(2, len(t)):
            print(t[i])
        if yuki == 1:
            print('\nЮки Ямадзаки:',target_status[int(time)%9])
        else:
            print('Юки Ямадзаки мертва')
        if soders == 1:
            print('Эрих Содерс: Операционная')
        else:
            print('Эрих Содерс мертв')
        print(f'\nТекущая маскировка: {current_disguise}')
        return f'Предмет в руках: {current_item}'
    else:
        print(f'\n\n{current_location}')
        if yuki == 1:
            print('Юки Ямадзаки:',target_status[int(time)%9])
        else:
            print('Юки Ямадзаки мертва')
        if soders == 1:
            print('Эрих Содерс: Операционная')
        else:
            print('Эрих Содерс мертв')
        print(f'\nТекущая маскировка: {current_disguise}')
        return f'Предмет в руках: {current_item}'
def inventory():
    global current_disguise
    global current_item
    global so
    global time
    inventory = []
    print('\n')
    for i in objects:
        if current_inventory.count(i) > 0:
            if i == 'Пистолет без глушителя':
                inventory.append(i+'(1)')
            else:
                inventory.append(i+'('+str(current_inventory.count(i))+')')
    inventory.append('Убрать предмет из рук')
    inventory.append(current_disguise)
    for i in range(len(inventory)-2):
        print(str(i+1)+'.', inventory[i])
    print(f'\nСейчас в руках: {current_item}')
    print(f'{len(inventory)-1}. Убрать предмет из рук')
    print(f'\n{len(inventory)}. {current_disguise}')
    t = input()
    if t.isdigit() == True:
        t = int(t)
    else:
        if t == 'w' or t == 'W':
            time += 0.5
            return move()
        if t == 'e' or t == 'E':
            time += 1
            return search()
        if t == 's' or t == 'S':
            return status()
        if t == 'f' or t == 'F':
            return interact()
        if t == 'q' or t == 'Q':
            sys.exit()
    if inventory[t-1] == current_disguise:
        print('\n')
        for i in range(len(found_disguise)):
            print(str(i+1)+'.', found_disguise[i])
        t = input()
        while t.isdigit() == False:
            t = input()
        t = int(t)
        current_disguise = found_disguise[t-1]
        so = 1
        return f'\n\nТекущая маскировка: {current_disguise}'
    elif inventory[t-1] == 'Убрать предмет из рук':
        current_item = 'Нет предмета'
        return f'\n\nСейчас в руках: {current_item}'
    elif inventory[t-1] == 'Пистолет без глушителя':
        if current_disguise == 'Охранник' or current_disguise == 'Телохранитель':
            current_item = 'Пистолет без глушителя'
            return f'\n\nСейчас в руках: {current_item}'
        else:
            print('Пистолет без глушителя -- это не легальное оружие. Достать предмет?\n1. Да\n2. Нет')
            t = input()
            while t.isdigit() == False:
                t = input()
            t = int(t)
            if t == 1:
                current_item = 'Пистолет без глушителя'
            else:
                return inventory()
    else:
        current_item = inventory[t-1][:-3]
        return f'\n\nСейчас в руках: {current_item}'
def combat():
    current_kills = 0
    current_bodies = 0
    enemies = []
    for i in find_location_npcs(player.location):
        if i.guard == True:
            enemies.append(i)
    if enemies == []:
        return ''
    global kills
    global bodies
    global combat_count
    buttons = ['A', 'D', 'W', 'X', 'S']
    print(f'\n\nНачался бой\n1. Прятаться (5/10)\n2. Напасть')
    t = input()
    while t.isdigit() == False:
        t = input()
    t = int(t)
    if t == 1:
        if random.randrange(1, 11) <= 5:
            print('\n\nВаша маскировка раскрыта, при перемещении в любую локацию вас будут узнавать.')
            player.compromised_disguises.append(player.disguise)
            return player.disguise
        else:
            print('\n\nВы умерли. Миссия провалена.')
            sys.exit()
    elif t == 2:
        for i in enemies:
            enemy_health = 100
            while enemy_health > 0:
                tm.sleep(random.randint(1,3))
                current_button = random.choice(buttons)
                crit = random.randint(1,11)
                if pistol in player.inventory:
                    print('\n\n1. Использовать пистолет\n2. Не использовать')
                    t = input()
                    while t.isdigit() == False:
                        t = input()
                    t = int(t)
                    if t == 1:
                        while t not in buttons :
                            print(f'\n\nНажимайте как можно быстрее: {current_button}')
                            t = input()
                        if t.upper() == current_button:
                            if crit <= 5 :
                                enemy_health -= 100
                            else:
                                enemy_health -= 50
                        else:
                            print('\n\nПромах')
                    if t == 2:
                        current_kills += 1
                        while '' not in buttons:
                            t = input(f'\n\nНажимайте как можно быстрее: {current_button}\n')
                        if t == current_button:
                            if crit <= 5 :
                                enemy_health -= 50 
                            else:
                                enemy_health -= 25
                        else:
                            print('\n\nПромах')
                else:
                    while '' not in buttons:
                        t = input(f'\n\nНажимайте как можно быстрее: {current_button}\n')
                    if t == current_button:
                        if crit <= 5 :
                            enemy_health -= 50 
                        else:
                            enemy_health -= 25
                    else:
                        print('\n\nПромах')
                enemy_attack = random.randint(1,10)
                if enemy_attack > 7 :
                    current_button = random.choice(buttons)
                    print(f'\n\n{i.disguise} атакует, нажимайте как можно быстрее: {current_button}\n')
                    s_time = tm.time()
                    i = input()
                    e_time = tm.time()
                    if e_time - s_time <= 1.7 and i == current_button:
                        print('\n\nВы увернулись')
                        time.sleep(3)
                    else:
                        player.health -= 25
                        if player.health != 0:
                            print('\n\nВы пропустили удар')
                        else:
                            print('\n\nВы умерли. Миссия провалена.')
                            sys.exit()
                        tm.sleep(3)
            print(f'\n\n{i.disguise} обезврежен')
            i.disguise.append(player.found_disguises)
            if location_witnesses(player.location) > 0:
                current_bodies += 1
        print('\n\nУбийств невинных:', current_kills)
        print('Тел найдено:', current_bodies)
        bodies += current_bodies
        kills += current_kills

def safe_move():
    global current_location
    location = locations[current_location]
    print('\n')
    for i in range(len(location)):
        print(str(i+1)+'.',location[i+1])
    t = input()
    while t.isdigit() == False:
        t = input()
    t = int(t)
    current_location = location[t]
    return f'\n\n{location[t]}'

def move():
    global time
    global bodies
    print('\n')
    for i in range(len(player.location.locations)):
        print(str(i+1)+'.',player.location.locations[i+1])
    print(f'{len(player.location.locations)+1}. Отменить действие')
    x = input()
    while x.isdigit() == False:
        x = input()
    x = int(x)
    if x > len(player.location.locations):
        return status()
    for i in locations:
        if i.name == player.location.locations[x]:
            move_to_location = i
    if move_to_location.name == 'Комната с серверами':
        if player.disguise == 'Директор клиники' or 'Ключ-карта' in player.inventory:
            player.location = move_to_location
            time += 0.5
            return f'\n\n{player.location.name}'
        else:
            return '\n\nДля входа необходима маскировка директора клиники или ключ-карта'
    else:
        if player.disguise in player.compromised_disguises:
            if find_location_npcs(player.location) != []:
                npc = find_location_npcs(player.location)[random.randrange(len(find_location_npcs(player.location)))]
                print(npc.suspicion())
                print('\n1. Напасть (5/10)\n2. Уйти')
                t = input()
                while t.isdigit() == False:
                    t = input()
                t = int(t)
                if t == 2:
                    time += 0.5
                    return f'\n\n{player.location.name}'
                if t == 1:
                    if random.randrange(1, 11) <= 5:
                        npc.alive = False
                        player.found_disguises.append(npc.disguise)
                        player.location = move_to_location
                        print(f'\nВам удалось тихо устранить {npc.disguise}')
                        time += 0.5
                        return f'\n\n{player.location.name}'
                    else:
                        return combat()
            else:
                player.location = move_to_location
                time += 0.5
                return f'\n\n{player.location.name}'
        else:
            if player.disguise in move_to_location.disguise:
                player.location = move_to_location
                time += 0.5
                return f'\n\n{player.location.name}'
            else:
                if location_witnesses(player.location) > 10:
                    chance = 10
                else:
                    chance = location_witnesses(player.location)
                print(location_status(player.location))
                print(f'\nУ вас нет подходящей маскировки. Переместиться на локацию? ({10-chance}/10)\n1. Да\n2. Нет')
                t = input()
                while t.isdigit() == False:
                    t = input()
                t = int(t)
                if t == 2:
                    return f'\n\n{player.location.name}'
                elif t == 1:
                    if random.randrange(1,11) <= 10-chance:
                        player.location = move_to_location
                        time += 0.5
                        return f'\n\n{player.location.name}'
                    else:
                        if find_location_npcs(player.location) != []:
                            npc = find_location_npcs(player.location)[random.randrange(len(find_location_npcs(player.location)))]
                            print(npc.suspicion())
                            print('\n1. Напасть (5/10)\n2. Уйти')
                            t = input()
                            while t.isdigit() == False:
                                t = input()
                            t = int(t)
                            if t == 2:
                                time += 0.5
                                return f'\n\n{player.location.name}'
                            if t == 1:
                                if random.randrange(1, 11) <= 5:
                                    if location_witnesses(player.location) > 0:
                                        bodies += 1
                                    npc.alive = False
                                    player.found_disguises.append(npc.disguise)
                                    player.location = move_to_location
                                    print(f'\nВам удалось устранить {npc.disguise}')
                                    time += 0.5
                                    return f'\n\n{player.location.name}'
                                else:
                                    return combat()
                        else:
                            player.location = move_to_location
                            time += 0.5
                            return f'\n\n{player.location.name}'

def search():
    for i in player.location.loot:
        player.inventory.append(i)
    player.location.loot = []
    return inventory()

def location_witnesses(location):
    location_npcs = find_location_npcs(location)
    witnesses = 0
    for i in location_npcs:
        if random.randrange(11) <= i.witness_chance:
            witnesses += 1
    return witnesses + location.witnesses

def location_status(location):
    location_npcs = []
    print(f'\n\nНа локации находятся:\n\n{location.witnesses} Пациент')
    for i in npcs:
        if i.route[int(time)%len(i.route)] == location.name:
            location_npcs.append(i.disguise)
    for i in range(1, len(disguises)+1):
        if disguises[i] in location_npcs:
            print(location_npcs.count(disguises[i]), disguises[i])
    return f'\nВсего {location_witnesses(location)} свидетелей'

def find_location_npcs(location):
    location_npcs = []
    for i in npcs:
        if i.route[int(time)%len(i.route)] == location.name and i.alive == True:
            location_npcs.append(i)
    return location_npcs

while True:
    print(move())