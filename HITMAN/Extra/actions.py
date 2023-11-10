import random
import sys
from locations import *
from loot import *
from setup import *

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
        elif item_use[t-1] == 'Бросить для отвлечения':
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
    global kills
    global bodies
    global combat_count
    combat_count += 1
    if pistol == 0:
        chance = 2
    else:
        chance = 7
    print(f'\n\nНачался бой\n1. Прятаться (5/10)\n2. Вступить в бой ({chance}/10)')
    t = input()
    while t.isdigit() == False:
        t = input()
    t = int(t)
    if t == 1:
        if random.randrange(1, 11) <= 5:
            print('\n\nВаша маскировка раскрыта, при перемещении в любую локацию будет начинаться бой.')
            bad_disguise.append(current_disguise)
            return current_disguise
        else:
            print('\n\nВы умерли. Миссия провалена.')
            sys.exit()
    elif t == 2:
        if random.randrange(1, 11) <= chance:
            current_kills = 0
            current_bodies = 0
            current_kills += random.randrange(1,6)
            current_bodies += random.randrange(current_kills // 2,current_kills)
            kills += current_kills
            bodies += current_bodies
            print('\n\nУбийств невинных:',current_kills)
            print('Тел найдело:',current_bodies)
            return inventory()
        else:
            print('\n\nВы умерли. Миссия провалена.')
            sys.exit()
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
    global current_location
    global witnesses
    location = locations[current_location]
    print('\n')
    for i in range(len(location)):
        print(str(i+1)+'.',location[i+1])
    print(f'{len(location)+1}. Отменить действие')
    x = input()
    while x.isdigit() == False:
        x = input()
    x = int(x)
    if x > len(location):
        return status()
    t = location[x]
    a = location_status[t]
    start = a[0]
    end = a[1]
    witnesses = random.randrange(start,end)
    if location[x] == 'Комната с серверами':
        if current_disguise == 'Директор клиники' or 'Ключ-карта' in current_inventory:
            current_location = location[x]
            return f'\n\n{location[x]}'
        else:
            return '\n\nДля входа необходима маскировка директора клиники или ключ-карта'
    else:
        if current_disguise in location_disguise[t]:
            current_location = location[x]
            return f'\n\n{location[x]}'
        else:
            print(f'У вас нет подходящей маскировки. Переместиться на локацию? ({10-witnesses}/10)\n1. Да\n2. Нет')
            t = input()
            while t.isdigit() == False:
                t = input()
            t = int(t)
            if t == 2:
                return f'\n\n{current_location}'
            elif t == 1:
                if random.randrange(1,11) <= 10-witnesses:
                    current_location = location[x]
                    return f'\n\n{current_location}'
                else:
                    return combat()
def search():
    for i in objects_room[current_location]:
        current_inventory.append(i)
    return inventory()
def rating():
    print('\n')
    print(f'Тел найдено: {bodies}')
    print(f'Убито невинных: {kills}')
    print(f'Вы начали бой {combat_count} раз')
    return f'Ваш рейтинг: {int(5-(bodies*0.5)-(kills*0.7)-(combat_count*0.25))}/5'