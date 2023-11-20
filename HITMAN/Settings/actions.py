import random
import sys
import time as tm
from Settings.locations import *
from Settings.setup import *
import pickle

def interact():
    global bodies
    global kills
    global yuki
    global soders
    global target_status
    witnesses = location_witnesses(player.location)
    location_npcs = find_location_npcs(player.location)
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
            if ((target_status[int(time[0])%9] == player.location.name) and (yuki[0] == 1)):
                print(f'\n\n1. Выстрелить в Юки Ямадзаки')
                for i in range(1, len(location_npcs)):
                    print(f'{i+1}. Выстрелить в {location_npcs[i].disguise}')
            elif (player.location.name == 'Операционная') and (soders[0] == 1):
                print(f'\n\n1. Выстрелить в Эрих Содерс')
                for i in range(1, len(location_npcs)):
                    print(f'{i+1}. Выстрелить в {location_npcs[i].disguise}')
            else:
                if location_npcs == []:
                    return '\n\nНа локации никого нет'
                print('\n')
                for i in range(len(location_npcs)):
                    print(f'{i+1}. Выстрелить в {location_npcs[i].disguise}')
            t = input()
            while t.isdigit() == False:
                t = input()
            t = int(t)
            if ((target_status[int(time[0])%9] == player.location.name) and (yuki[0] == 1)) and t == 1:
                print(straight_shot.achieved())
                yuki[0] = 0
                if witnesses > 0:
                    bodies[0] += 1
                    return combat()
                else:
                    return '\n\nДиана: С Юки Ямадзаки покончено, отличная работа.'
            elif (player.location.name == 'Операционная') and (soders[0] == 1) and t == 1:
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
                player.found_disguises.append(location_npcs[t-1].disguise)
                if witnesses > 0:
                    bodies[0] += 1
                    kills[0] += 1
                    return combat()
                else:
                    kills[0] += 1
                    return location_status(player.location)
        elif player.item.usage[t-1] == 'Отменить действие':
            return location_status(player.location)
        elif player.item.usage[t-1] == 'Ударить':
            if location_npcs == []:
                    return '\n\nНа локации никого нет'
            print('\n')
            for i in range(len(location_npcs)):
                    print(f'{i+1}. Ударить {location_npcs[i].disguise}')
            t = input()
            while t.isdigit() == False:
                t = input()
            t = int(t)
            location_npcs[t-1].alive = False
            player.found_disguises.append(location_npcs[t-1].disguise)
            if witnesses > 0:
                bodies[0] += 1
                return combat()
            else:
                return location_status(player.location)
        elif player.item.usage[t-1] == 'Бросить':
            if location_npcs == []:
                    return '\n\nНа локации никого нет'
            print('\n')
            player.location.loot.append(player.item)
            player.inventory.remove(player.item)
            for i in range(len(location_npcs)):
                    print(f'{i+1}. Бросить в {location_npcs[i].disguise}')
            t = input()
            while t.isdigit() == False:
                t = input()
            t = int(t)
            location_npcs[t-1].alive = False
            player.found_disguises.append(location_npcs[t-1].disguise)
            if witnesses > 0:
                bodies[0] += 1
                return combat()
            else:
                return location_status(player.location)
        elif player.item.usage[t-1] == 'Ударить (летально)':
            if ((target_status[int(time[0])%9] == player.location.name) and (yuki[0] == 1)):
                print(f'\n\n1. Ударить Юки Ямадзаки')
                for i in range(1, len(location_npcs)):
                    print(f'{i+1}. Ударить {location_npcs[i].disguise}')
            else:
                if location_npcs == []:
                    return '\n\nНа локации никого нет'
                print('\n')
                for i in range(len(location_npcs)):
                    print(f'{i+1}. Ударить {location_npcs[i].disguise}')
            t = input()
            while t.isdigit() == False:
                t = input()
            t = int(t)
            if ((target_status[int(time[0])%9] == player.location) and (yuki[0] == 1)) and t == 1:
                yuki[0] = 0
                if witnesses > 0:
                    bodies[0] += 1
                    return combat()
                else:
                    return '\n\nДиана: С Юки Ямадзаки покончено, отличная работа.'
            else:
                location_npcs[t-1].alive = False
                player.found_disguises.append(location_npcs[t-1].disguise)
                if witnesses > 0:
                    bodies[0] += 1
                    kills += 1
                    return combat()
                else:
                    kills += 1
                    return location_status(player.location)
        elif player.item.usage[t-1] == 'Бросить (летально)':
            player.location.loot.append(player.item)
            player.inventory.remove(player.item)
            if ((target_status[int(time[0])%9] == player.location.name) and (yuki[0] == 1)):
                print(f'\n\n1. Бросить в Юки Ямадзаки')
                for i in range(1, len(location_npcs)):
                    print(f'{i+1}. Бросить в {location_npcs[i].disguise}')
            else:
                if location_npcs == []:
                    return '\n\nНа локации никого нет'
                print('\n')
                for i in range(len(location_npcs)):
                    print(f'{i+1}. Бросить в {location_npcs[i].disguise}')
            t = input()
            while t.isdigit() == False:
                t = input()
            t = int(t)
            if ((target_status[int(time[0])%9] == player.location) and (yuki[0] == 1)) and t == 1:
                yuki[0] = 0
                if witnesses > 0:
                    bodies[0] += 1
                    return combat()
                else:
                    return '\n\nДиана: С Юки Ямадзаки покончено, отличная работа.'
            else:
                location_npcs[t-1].alive = False
                player.found_disguises.append(location_npcs[t-1].disguise)
                if witnesses > 0:
                    bodies[0] += 1
                    kills[0] += 1
                    return combat()
                else:
                    kills[0] += 1
                    return location_status(player.location)
        elif player.item.usage[t-1] == 'Бросить для отвлечения':
            if location_npcs == []:
                    return '\n\nНа локации никого нет'
            if player.item == coin:
                player.location.loot.append(player.item)
            player.inventory.remove(player.item)
            print('\n')
            for i in range(len(location_npcs)):
                    print(f'{i+1}. Отвлечь {location_npcs[i].disguise}')
            print(f'{len(location_npcs)+1}. Отвлечь для перемещения')
            t = input()
            while t.isdigit() == False:
                t = input()
            t = int(t)
            if t > len(location_npcs):
                return safe_move()
            else:
                print(f'\n\n1. Вырубить {location_npcs[t-1].disguise}\n2. Убить {location_npcs[t-1].disguise}')
                x = input()
                while x.isdigit() == False:
                    x = input()
                x = int(x)
                if x == 1:
                    player.found_disguises.append(location_npcs[t-1].disguise)
                    location_npcs[t-1].alive = False
                    return location_status(player.location)
                if x == 2:
                    kills[0] += 1
                    location_npcs[t-1].alive = False
                    player.found_disguises.append(location_npcs[t-1].disguise)
                    return location_status(player.location)
        elif player.item.usage[t-1] == 'Усмирить':
            if location_npcs == []:
                    return '\n\nНа локации никого нет'
            print('\n')
            for i in range(len(location_npcs)):
                    print(f'{i+1}. Усмирить {location_npcs[i].disguise}')
            t = input()
            while t.isdigit() == False:
                t = input()
            t = int(t)
            location_npcs[t-1].alive = False
            player.found_disguises.append(location_npcs[t-1].disguise)
            if witnesses > 0:
                bodies[0] += 1
                return combat()
            else:
                return location_status(player.location)
        elif player.item.usage[t-1] == 'Использовать':
            if player.location == morgue:
                player.inventory.remove(player.item)
                print('\n\nНейрочип подействовал на одного из работников морга и тот отправился в комнату, где хранится сердце, которое должны пересадить Эриху Содерсу. Последовать за ним?\n1. Да\n2. Нет')
                t = input()
                while t.isdigit() == False:
                    t = input()
                t = int(t)
                if t == 2:
                    return player.location.name
                elif t == 1:
                    print('\n\n1. Выйти\n2. Повредить сердце')
                    t = input()
                    while t.isdigit() == False:
                        t = input()
                    t = int(t)
                    if t == 1:
                        return player.location.name
                    elif t == 2:
                        print(heartless.achieved())
                        soders[0] = 0
                        print('\n\nДиана: 47-й, без сердца для пересадки Содерс не выживет. Ты смог от него избавиться даже не прикасаясь, изящный ход.')
                        return location_status(player.location)
            elif player.item.usage[t-1] == 'Задушить':
                if ((target_status[int(time[0])%9] == player.location.name) and (yuki[0] == 1)):
                    print(f'\n\n1. Задушить Юки Ямадзаки')
                    for i in range(1, len(location_npcs)):
                        print(f'{i+1}. Ударить {location_npcs[i].disguise}')
                else:
                    if location_npcs == []:
                        return '\n\nНа локации никого нет'
                    print('\n')
                    for i in range(len(location_npcs)):
                        print(f'{i+1}. Задушить {location_npcs[i].disguise}')
                t = input()
                while t.isdigit() == False:
                    t = input()
                t = int(t)
                if ((target_status[int(time[0])%9] == player.location) and (yuki[0] == 1)) and t == 1:
                    print(piano_man.achieved())
                    yuki[0] = 0
                    if witnesses > 0:
                        bodies[0] += 1
                        return combat()
                    else:
                        return '\n\nДиана: С Юки Ямадзаки покончено, отличная работа.'
                else:
                    location_npcs[t-1].alive = False
                    player.found_disguises.append(location_npcs[t-1].disguise)
                    if witnesses > 0:
                        bodies[0] += 1
                        kills += 1
                        return combat()
                    else:
                        kills += 1
                        return location_status(player.location)
            else:
                return '\n\nВне зоны действия'

def status():
    global time
    global soders
    global yuki
    print(f'\n\n1. Статус {player.location.name}\n2. Общий статус')
    t = input()
    while t.isdigit() == False:
        t = input()
    t = int(t)
    if t == 1:
        return location_status(player.location)
    if t == 2:
        if yuki[0] == 1:
            print('\nЮки Ямадзаки:',target_status[int(time[0])%9])
        else:
            print('Юки Ямадзаки мертва')
        if soders[0] == 1:
            print('Эрих Содерс: Операционная')
        else:
            print('Эрих Содерс мертв')
        print(f'\nТекущая маскировка: {player.disguise}')
        return f'Предмет в руках: {player.item.name}'
    
def inventory():
    inventory = []
    print('\n')
    for i in objects:
        if player.inventory.count(i) > 0:
            if i == pistol:
                inventory.append(i.name+' (1)')
            else:
                inventory.append(i.name+' ('+str(player.inventory.count(i))+')')
    inventory.append('Убрать предмет из рук')
    inventory.append(player.disguise)
    for i in range(len(inventory)-2):
        print(str(i+1)+'.', inventory[i])
    print(f'\nСейчас в руках: {player.item.name}')
    print(f'{len(inventory)-1}. Убрать предмет из рук')
    print(f'\n{len(inventory)}. {player.disguise}')
    t = input()
    if t.isdigit() == True:
        t = int(t)
    else:
        if t == 'w' or t == 'W':
            return move()
        if t == 'e' or t == 'E':
            return search()
        if t == 's' or t == 'S':
            return status()
        if t == 'f' or t == 'F':
            return interact()
        if t == 'q' or t == 'Q':
            with open('/Users/alexey/Python/Orange-Team/HITMAN/Settings/savefile.dat', 'wb') as f:
                pickle.dump([smoking_kills, stretch, personal_goodbye, no_smoking, human_error, suit_only, silent_assasin, sauna_assasination, sushi, heartless, silent_assasin_suit_only, no_evidence, ghost_machine, straight_shot, hold_hair, piano_man, hurt_oneself, tasteless, master_assasin, player_lvl], f, protocol=2)
            sys.exit()
    if inventory[t-1] == player.disguise:
        print('\n')
        for i in range(len(player.found_disguises)):
            print(str(i+1)+'.', player.found_disguises[i])
        t = input()
        while t.isdigit() == False:
            t = input()
        t = int(t)
        player.disguise = player.found_disguises[t-1]
        return f'\n\nТекущая маскировка: {player.disguise}'
    elif inventory[t-1] == 'Убрать предмет из рук':
        player.item = arms
        return f'\n\nСейчас в руках: {player.item.name}'
    elif item_by_name(inventory[t-1][:-4]).illegal:
        if player.disguise == 'Охранник' or player.disguise == 'Телохранитель':
            player.item = item_by_name(inventory[t-1][:-4])
            return f'\n\nСейчас в руках: {player.item.name}'
        else:
            print(f'\n\n{inventory[t-1][:-4]} -- это нелегальный прдмет. Достать предмет?\n1. Да\n2. Нет')
            t = input()
            while t.isdigit() == False:
                t = input()
            t = int(t)
            if t == 1:
                player.item = item_by_name(inventory[t-1][:-4])
                return location_status(player.location)
            else:
                return inventory()
    else:
        player.item = item_by_name(inventory[t-1][:-4])
        return f'\n\nСейчас в руках: {player.item.name}'

def combat():
    global kills
    global bodies
    global player_lvl
    global combat_count
    current_kills = 0
    current_bodies = 0
    enemies = []
    for i in find_location_npcs(player.location):
        if i.guard == True:
            enemies.append(i)
    if enemies == []:
        return location_status(player.location)
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
            player.compromised_disguises.append(player.disguise)
            return player.disguise
        else:
            with open('/Users/alexey/Python/Orange-Team/HITMAN/Settings/savefile.dat', 'wb') as f:
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
                                with open('/Users/alexey/Python/Orange-Team/HITMAN/Settings/savefile.dat', 'wb') as f:
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
                                with open('/Users/alexey/Python/Orange-Team/HITMAN/Settings/savefile.dat', 'wb') as f:
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
                            with open('/Users/alexey/Python/Orange-Team/HITMAN/Settings/savefile.dat', 'wb') as f:
                                    pickle.dump([player_lvl], f, protocol=2)
                            print('\n\nВы умерли. Миссия провалена.')
                            sys.exit()
                enemy_attack = random.randint(1,10)
                if enemy_attack > 7 :
                    current_button = random.choice(buttons)
                    print(f'\n\n{i.disguise} атакует, нажимайте как можно быстрее: {current_button}')
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
                            with open('/Users/alexey/Python/Orange-Team/HITMAN/Settings/savefile.dat', 'wb') as f:
                                    pickle.dump([player_lvl], f, protocol=2)
                            print('\n\nВы умерли. Миссия провалена.')
                            sys.exit()
            print(f'\n\n{i.disguise} обезврежен')
            tm.sleep(2)
            i.alive = False
            player.found_disguises.append(i.disguise)
            if location_witnesses(player.location) > 0:
                current_bodies += 1
        bodies[0] += current_bodies
        kills[0] += current_kills
        print('\n\nУбийств невинных:', current_kills)
        return f'Тел найдено: {current_bodies}'

def safe_move():
    global time
    print('\n')
    for i in range(len(player.location.locations)):
        print(str(i+1)+'.',player.location.locations[i+1])
    t = input()
    while t.isdigit() == False:
        t = input()
    t = int(t)
    player.location = location_by_name(player.location.locations[t])
    return f'\n\n{player.location.name}'

def move():
    global bodies
    global suspicion_count
    print('\n')
    for i in range(len(player.location.locations)):
        print(str(i+1)+'.',player.location.locations[i+1])
    print(f'{len(player.location.locations)+1}. Отменить действие')
    x = input()
    while x.isdigit() == False:
        x = input()
    x = int(x)
    if x > len(player.location.locations):
        return location_status(player.location)
    for i in locations:
        if i.name == player.location.locations[x]:
            move_to_location = i
    if move_to_location.name == 'Комната с серверами':
        if player.disguise == 'Директор клиники' or keycard in player.inventory or disposable_scrambler in player.inventory:
            player.location = move_to_location
            return f'\n\n{location_status(player.location)}'
        else:
            return '\n\nДля входа необходима маскировка директора клиники или ключ-карта'
    else:
        if player.disguise in player.compromised_disguises:
            if find_location_npcs(player.location) != []:
                npc = find_location_npcs(player.location)[random.randrange(len(find_location_npcs(player.location)))]
                print(npc.suspicion())
                print('\n1. Напасть (3/10)\n2. Уйти')
                t = input()
                while t.isdigit() == False:
                    t = input()
                t = int(t)
                if t == 2:
                    return f'\n\n{location_status(player.location)}'
                if t == 1:
                    if random.randrange(1, 11) <= 3:
                        npc.alive = False
                        player.found_disguises.append(npc.disguise)
                        player.location = move_to_location
                        print(f'\nВам удалось тихо устранить {npc.disguise}')
                        return f'\n\n{location_status(player.location)}'
                    else:
                        return combat()
            else:
                player.location = move_to_location
                return f'\n\n{location_status(player.location)}'
        else:
            if (player.item.illegal == True and player.disguise != 'Охранник' and player.disguise != 'Телохранитель'):
                player.location = move_to_location
                if find_location_npcs(player.location) != []:
                    npc = find_location_npcs(player.location)[random.randrange(len(find_location_npcs(player.location)))]
                    suspicion_count[0] += 1
                    print(f'\n\n{npc.disguise}: Он вооружен!\n')
                    print('1. Напасть (3/10)\n2. Скрыться (7/10)')
                    t = input()
                    while t.isdigit() == False:
                        t = input()
                    t = int(t)
                    if t == 1:
                        if random.randrange(1, 11) <= 3:
                            npc.alive = False
                            return f'\n\nВам удалось тихо устранить {npc.disguise}'
                        else:
                            return combat()
                    if t == 2:
                        if random.randrange(1, 11) <= 7:
                            player.compromised_disguises.append(player.disguise)
                            print('\n\nВаша маскировка раскрыта, при перемещении в любую локацию вас будут узнавать.')
                            return f'\n\n{location_status(player.location)}'
            else:
                if player.disguise in move_to_location.disguise:
                    player.location = move_to_location
                    return f'\n\n{location_status(player.location)}'
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
                        return f'\n\n{location_status(player.location)}'
                    elif t == 1:
                        if random.randrange(1,11) <= 10-chance:
                            player.location = move_to_location
                            return f'\n\n{location_status(player.location)}'
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
                                    return f'\n\n{location_status(player.location)}'
                                if t == 1:
                                    if random.randrange(1, 11) <= 5:
                                        if location_witnesses(player.location) > 0:
                                            bodies[0] += 1
                                        npc.alive = False
                                        player.found_disguises.append(npc.disguise)
                                        player.location = move_to_location
                                        print(f'\nВам удалось устранить {npc.disguise}')
                                        return f'\n\n{location_status(player.location)}'
                                    else:
                                        return combat()
                            else:
                                player.location = move_to_location
                                return f'\n\n{location_status(player.location)}'

def search():
    for i in player.location.loot:
        player.inventory.append(i)
    player.location.loot = []
    return inventory()

def location_witnesses(location):
    location_npcs = find_location_npcs(location)
    witnesses = 0
    for i in location_npcs:
        if random.randrange(11) <= i.witness_chance and i.alive == True:
            witnesses += 1
    return witnesses + location.witnesses

def location_status(location):
    print(f'\n\n{location.name}\n')
    location_npcs = find_location_npcs(location)
    location_disguises = []
    for i in location_npcs:
        if i.alive == True:
            location_disguises.append(i.disguise)
    if location_npcs != []:
        if location.witnesses > 0:
            print(f'На локации находятся:\n\n{location.witnesses} Пациент')
        for i in range(1, len(disguises)+1):
            if disguises[i] in location_disguises:
                print(location_disguises.count(disguises[i]), disguises[i])
        return f'\nВсего {location_witnesses(location)} свидетелей'
    else:
        return 'На локации нет свидетелей'

def find_location_npcs(location):
    location_npcs = []
    for i in npcs:
        if i.route[int(time[0])%len(i.route)] == location.name:
            location_npcs.append(i)
    return location_npcs

def see_challenges():
    global challenges
    for i in range(len(challenges)):
        if challenges[i].completed == True:
            print(f'{i+1}. {challenges[i].name + ' (выполнено)'}')
        else:
            print(f'{i+1}. {challenges[i].name}')
    print(f'{len(challenges) + 1}. Выйти')
    t = input()
    while t.isdigit() == False:
        t = input()
    t = int(t)
    if t > len(challenges):
        return location_status(player.location)
    else:
        print(f'\n\n{challenges[t-1].name}\n\n{challenges[t-1].description}\n\n1. Назад')
        input()
        return(see_challenges())