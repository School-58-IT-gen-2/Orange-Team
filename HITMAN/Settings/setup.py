import sys
import pickle
from Settings.locations import *
from Settings.loot import *
import os

class Player:

    def __init__(self, inventory, health, location, found_disguises, item, compromised_disguises, disguise):
        self.inventory = inventory
        self.health = health
        self.location = location
        self.found_disguises = found_disguises
        self.item = item
        self.compromised_disguises = compromised_disguises
        self.disguise = disguise

player_lvl = 10

class Challenge:

    def __init__(self, name, description, completed):
        self.name = name
        self.description = description
        self.completed = completed

    def achieved(self):
        global player_lvl
        if self.completed == False:
            self.completed = True
            player_lvl += 5
            return f'\n\nИспытание выполнено: {self.name}'
        return ''
    
smoking_kills = Challenge('Курение убивает', 'Убейте Юки Ямадзаки во время того, как она курит сигареты.', False)
stretch = Challenge('Хорошая растяжка', 'Убейте Юки Ямадзаки, подстроив несчастный случай во время занятий йогой.', False)
personal_goodbye = Challenge('Личное прощание', 'Убейте Эриха Содерса выстрелом из пистолета.', False)
no_smoking = Challenge('Не курить!', 'Положите пачку сигарет в номере Юки Ямадзаки.', False)
human_error = Challenge('(Не) врачебная ошибка', 'Убейте Эриха Содерса, самостоятельно проведя операцию.', False)
suit_only = Challenge('Только костюм', '1. Завершите миссию\n2. Сделайте это в маскировке VIP - пациента', False)
silent_assasin = Challenge('Бесшумный убийца', '1. Завершите миссию\n2. Убивайте только цели\n3. Ни одно тело не должно быть обнаружено\n 4. Не дайте себя заметить', False)
sauna_assasination = Challenge('Убийство в парилке', 'Убейте Юки Ямадзаки, заперев ее в парилке.', False)
sushi = Challenge('Приятного аппетита', 'Отравите роллы Юки Ямадзаки ядом рыбы фугу.', False)
heartless = Challenge('Бессердечный', 'Повредите сердце Эриха содерса.', False)
silent_assasin_suit_only = Challenge('Бесшумный убйца. Только костюм.', '1. Завершите миссию\n2. Убивайте только цели\n3. Ни одно тело не должно быть обнаружено\n 4. Не дайте себя заметить\n5. Сделайте это в маскировке VIP - пациента', False)
no_evidence = Challenge('Без улик', 'Завершите миссию, не давая обнаружить тела.', False)
ghost_machine = Challenge('Призрак в машине', 'Повредите сервера KAI.', False)
straight_shot = Challenge('Точный выстрел', 'Убейте цель выстрелом из пистолета.', False)
hold_hair = Challenge('Подержи волосы', 'Убейте цель, утопив ее.', False)
piano_man = Challenge('Пианист', 'Убейте цель при помощи удавки.', False)
hurt_oneself = Challenge('Так можно и пораниться', 'Убейте цель, подстроив несчастный случай.', False)
tasteless = Challenge('Без вкуса, без следа', 'Устраните цель, отравив ее.', False)
master_assasin = Challenge('Мастер-убийца', f'1. Выполните {straight_shot.name}\n2. Выполните {hold_hair.name}\n3. Выполните {piano_man.name}\n4. Выполните {hurt_oneself.name}\n5. Выполните {tasteless.name}', False)

challenges = [smoking_kills, stretch, personal_goodbye, no_smoking, human_error, suit_only, silent_assasin, sauna_assasination, sushi, heartless, silent_assasin_suit_only, no_evidence, ghost_machine, straight_shot, hold_hair, piano_man, hurt_oneself, tasteless, master_assasin]

lvl_unlocks = {
    1: ['Номер 47-го', suite, 'VIP - пациент'],
    2: ['Зона спа', spa, 'VIP - пациент'],
    3: ['Горная тропа (в маскировке ниндзя)', mountain_path, 'Ниндзя'],
    4: ['Ресторан', restaurant, 'VIP - пациент'],
    5: ['Спальня персонала (в маскировке работника "ГАМА")', chip_room, 'Работник "ГАМА"'],
    6: ['Кухня (в маскировке шефа)', kitchen, 'Шеф'],
    7: ['Внутренний сад (в маскировке работника "ГАМА")', garden, 'Работник "ГАМА"'],
    8: ['Морг', morgue, 'VIP - пациент'],
    9: ['Оперционная (в маскировке хирурга)', operation_room, 'Хирург']
}

if os.stat('/Users/alexey/Python/Orange-Team/HITMAN/Settings/savefile.dat').st_size != 0:
    with open('/Users/alexey/Python/Orange-Team/HITMAN/Settings/savefile.dat', 'rb') as f:
        smoking_kills, stretch, personal_goodbye, no_smoking, human_error, suit_only, silent_assasin, sauna_assasination, sushi, heartless, silent_assasin_suit_only, no_evidence, ghost_machine, straight_shot, hold_hair, piano_man, hurt_oneself, tasteless, master_assasin, player_lvl = pickle.load(f)

def start():
    carry_on_items = [fiber_wire, deadly_poison, emetic_poison, disposable_scrambler, combat_knife, coin]
    global player_lvl
    print('Брифинг:\nДиана: Доброе утро, 47-й. Совет директоров одобрил ликвидацию Эриха Содерса. После Колорадо мы решили пристально изучить личные дела Содерса и выяснили, что его недавно доставили в частную клинику «Гама» на японском острове Хоккайдо для срочной операции на сердце. Без «Провиденс» тут явно не обошлось. Содерс страдает от редкой врожденной патологии — транспозиции органов: его внутренние органы в теле расположены зеркально. Для трансплантации ему необходимо правостороннее сердце, и он явно предал МКА, чтобы получить его. Его приняли прошлой ночью и сейчас он готовится к трёхэтапной операции. Под видом Тобиаса Рипера, крупного бизнесмена, ты отправляешься в «Гаму» для стандартного медицинского обследования, о формальностях мы уже позаботились. В таких условиях придётся импровизировать и самостоятельно добывать снаряжение. Кроме того, тебе нужно ликвидировать Юки Ямадзаки — она адвокат из Токио, работает на «Провиденс». Содерс уже передал Ямадзаки доступ к нашей базе клиентов и согласился предоставить полный список оперативных сотрудников МКА после завершения операции. Этого допустить никак нельзя. Содерс должен заплатить за своё предательство — это послужит хорошим уроком его нанимателям. На кону будущее и репутация МКА. Какой бы властью и могуществом ни обладала «Провиденс», пора поставить их на место. Я оставлю тебя подготавливаться.\n\nВведите любой символ, чтобы начать задание.')
    input()
    print('\n\nВыберите начальную локацию:\n')
    for i in range(1, 10):
        if i <= player_lvl // 10:
            print(f'{i}. {lvl_unlocks[i][0]}')
    t = input()
    while t.isdigit() == False:
        t = input()
    t = int(t)
    start_location = lvl_unlocks[t]
    start_inventory = []
    if player_lvl // 10 > 9:
        print('\n\nВыберите пистолет:\n')
        print('1. Пистолет с глушителем\n2. Пистолет без глушителя')
        t = input()
        while t.isdigit() == False:
            t = input()
        t = int(t)
        if t == 1:
            start_inventory.append(silenced_pistol)
        if t == 2:
            start_inventory.append(pistol)
        print('\n\nВыберите первый предмет сняряжения:\n')
        for i in range(len(carry_on_items)):
            print(f'{i+1}. {carry_on_items[i].name}')
        t = input()
        while t.isdigit() == False:
            t = input()
        t = int(t)
        start_inventory.append(carry_on_items[t-1])
        carry_on_items.remove(carry_on_items[t-1])
        print('\n\nВыберите второй предмет сняряжения:\n')
        for i in range(len(carry_on_items)):
            print(f'{i+1}. {carry_on_items[i].name}')
        t = input()
        while t.isdigit() == False:
            t = input()
        t = int(t)
        start_inventory.append(carry_on_items[t-1])
    if start_location[1] == suite:
        print('\n\nДиана: Добро пожаловать на Хоккайдо, 47-й. Частная клиника «Гама» оказывает медицинские услуги высочайшего уровня представителям мировой элиты, выходя при необходимости за рамки закона. Частично здание находится под управлением искусственного интеллекта — KAI. Система контролирует доступ пациентов в разные части клиники и даже принимает участие в ряде медицинских процедур. Эрих Содерс уже находится в операционной, где он проходит предварительную подготовку с применением стволовых клеток. Это крайне противоречивая процедура ещё не одобрена властями Японии. Юки Ямадзаки уже прибыла. Она находится либо в своём номере, либо в ресторане, либо в спа-зоне клиники. Содерсу скоро введут наркоз. Сделай так, чтобы он больше никогда не проснулся. Удачи, 47-й.')
    return Player(start_inventory, 100, start_location[1], [start_location[2]], arms, [], start_location[2])

player = start()

class NPC:

    def __init__(self, guard, disguise, alive, route, witness_chance):
        self.guard = guard
        self.disguise = disguise
        self.alive = alive
        self.route = route
        self.witness_chance = witness_chance

    def move(self):
        if self.alive == True:
            location = self.route[int(time)%len(self.route)]
            return location_by_name(location)
        else:
            return False
    
    def suspicion(self):
        global suspicion_count
        if self.alive == True:
            suspicion_count[0] += 1
            return f'\n\n{self.disguise}: Эй, ты не можешь здесь находится!'
        else:
            return False
        

guard_cable_car_1 = NPC(True, 'Телохранитель', True, {0: 'Канатная дорога'}, 5)
guard_cable_car_2 = NPC(True, 'Телохранитель', True, {0: 'Канатная дорога'}, 5)
guard_hall_1 = NPC(True, 'Охранник', True, {0: 'Холл'}, 8)
guard_hall_2 = NPC(True, 'Охранник', True, {0: 'Холл'}, 8)
guard_hall_3 = NPC(True, 'Охранник', True, {0: 'Холл', 1: 'Комната охраны'}, 8)
guard_spa_1 = NPC(True, 'Охранник', True, {0: 'Зона спа'}, 4)
guard_restaurant_1 = NPC(True, 'Охранник', True, {0: 'Ресторан'}, 8)
guard_restaurant_2 = NPC(True, 'Охранник', True, {0: 'Ресторан'}, 9)
guard_garden_1 = NPC(True, 'Охранник', True, {0: 'Внутренний сад'}, 3)
guard_garden_2 = NPC(True, 'Охранник', True, {0: 'Внутренний сад'}, 5)
guard_medical_center_1 = NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс'}, 6)
guard_medical_center_2 = NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс'}, 7)
guard_medical_center_3 = NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс'}, 6)
guard_medical_center_4 = NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс', 1: 'Операционная'}, 9)
guard_security_room = NPC(True, 'Охранник', True, {0: 'Комната охраны'}, 9)
guard_garage = NPC(True, 'Охранник', True, {0: 'Гараж'}, 7)
guard_bar = NPC(True, 'Охранник', True, {0: 'Барная стойка'}, 2)
guard_morgue = NPC(True, 'Телохранитель', True, {0: 'Морг'}, 2)
guard_target_suite_1 = NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки'}, 8)
guard_target_suite_2 = NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки'}, 9)
guard_target_suite_3 = NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки'}, 8)
guard_target_suite_4 = NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки'}, 7)
guard_helipad_1 = NPC(True, 'Телохранитель', True, {0: 'Вертолетная площадка'}, 8)
guard_helipad_2 = NPC(True, 'Телохранитель', True, {0: 'Вертолетная площадка'}, 9)
guard_medical_center_level_2_1 = NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс (2 этаж)'}, 8)
guard_medical_center_level_2_2 = NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс (2 этаж)'}, 9)
guard_medical_center_level_2_3 = NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс (2 этаж)'}, 7)
guard_medical_center_level_2_4 = NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс (2 этаж)'}, 8)
target_guard = NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки', 1: 'Холл', 2: 'Ресторан', 3: 'Холл', 4: 'Зона спа', 5: 'Зона отдыха', 6: 'Зона спа', 7: 'Холл', 8: 'Номер Юки Ямадзаки'}, 8)

staff_spa_1 = NPC(False, 'Работник "ГАМА"', True, {0: 'Зона спа', 1: 'Зона отдыха'}, 7)
staff_spa_2 = NPC(False, 'Работник "ГАМА"', True, {0: 'Зона спа'}, 8)
staff_restaurant_1 = NPC(False, 'Работник "ГАМА"', True, {0: 'Ресторан'}, 7)
staff_restaurant_2 = NPC(False, 'Работник "ГАМА"', True, {0: 'Ресторан'}, 8)
staff_garden_1 = NPC(False, 'Работник "ГАМА"', True, {0: 'Внутренний сад'}, 1)
staff_garden_2 = NPC(False, 'Работник "ГАМА"', True, {0: 'Внутренний сад'}, 3)
surgeon_medical_center = NPC(False, 'Хирург', True, {0: 'Мед-комплекс', 1: 'Операционная'}, 9)
mechanic_garage = NPC(False, 'Механик', True, {0: 'Гараж'}, 1)
yoga_coach = NPC(False, 'Инструктор по йоге', True, {0: 'Гараж', 1: 'Спальня персонала'}, 1)
chef_1 = NPC(False, 'Шеф', True, {0: 'Кухня'}, 7)
chef_2 = NPC(False, 'Шеф', True, {0: 'Кухня'}, 8)
morgue_worker_1 = NPC(False, 'Работник морга', True, {0: 'Морг'}, 6)
morgue_worker_2 = NPC(False, 'Работник морга', True, {0: 'Морг'}, 7)
morgue_worker_3 = NPC(False, 'Работник морга', True, {0: 'Морг'}, 1)
surgeon_operation_room_1 = NPC(False, 'Хирург', True, {0: 'Операционная'}, 7)
surgeon_operation_room_2 = NPC(False, 'Хирург', True, {0: 'Операционная'}, 9)
surgeon_operation_room_3 = NPC(False, 'Хирург', True, {0: 'Операционная'}, 8)
chief_surgeon = NPC(False, 'Главный хирург', True, {0: 'Операционная'}, 7)
pilot = NPC(False, 'Пилот', True, {0: 'Комната пилота'}, 3)
director = NPC(False, 'Директор клиники', True, {0: 'Холл', 1: 'Внутренний сад', 2: 'Холл', 3: 'Мед-комплекс', 4: 'Мед-комплекс (2 этаж)', 5: 'Комната директора клиники', 6: 'Комната директора клиники', 7:'Комната директора клиники', 8: 'Мед-комплекс (2 этаж)', 9: 'Мед-комплекс', 10: 'Холл'}, 7)

npcs = [guard_cable_car_1, 
        guard_cable_car_2, 
        guard_hall_1, 
        guard_hall_2, 
        guard_hall_3, 
        guard_spa_1, 
        guard_restaurant_1, 
        guard_restaurant_2, 
        guard_garden_1, 
        guard_garden_2,
        guard_security_room,
        guard_garage,
        guard_bar,
        guard_morgue,
        guard_target_suite_1,
        guard_target_suite_2,
        guard_target_suite_3,
        guard_target_suite_4,
        guard_medical_center_1, 
        guard_medical_center_2, 
        guard_medical_center_3, 
        guard_medical_center_4, 
        guard_helipad_1, 
        guard_helipad_2, 
        guard_medical_center_level_2_1, 
        guard_medical_center_level_2_2, 
        guard_medical_center_level_2_3, 
        guard_medical_center_level_2_4, 
        target_guard, 
        staff_spa_1, 
        staff_spa_2, 
        staff_restaurant_1, 
        staff_restaurant_2, 
        surgeon_medical_center, 
        mechanic_garage, 
        yoga_coach, 
        chef_1, 
        chef_2, 
        morgue_worker_1, 
        morgue_worker_2, 
        morgue_worker_3, 
        surgeon_operation_room_1, 
        surgeon_operation_room_2, 
        surgeon_operation_room_3, 
        chief_surgeon, 
        pilot, 
        director]

def rating():
    global player_lvl
    print('\n')
    print(f'Тел найдено: {bodies[0]}')
    print(f'Убито невинных: {kills[0]}')
    print(f'Вы начали бой {combat_count[0]} раз')
    print(f'Вы были замечены {suspicion_count[0]} раз')
    rating = int(5-(bodies[0]*0.5)-(kills[0]*0.7)-(combat_count[0]*0.1)-(suspicion_count[0]*0.2))
    if rating < 0:
        rating = 0
    print(f'Ваш рейтинг: {rating}/5')
    if int(rating) == 5 and so[0] == 1:
        print(silent_assasin.achieved())
        print('Бесшумный убийца.')
    elif int(rating) == 5 and so[0] == 0:
        print(silent_assasin_suit_only.achieved())
        print('Бесшумный убийца.')
    elif so[0] == 0:
        print(suit_only.achieved())
    if bodies[0] == 0:
        print(no_evidence.achieved())
    if straight_shot.completed == True and hold_hair.completed == True and piano_man.completed == True and hurt_oneself.completed == True and tasteless.completed == True:
        print(master_assasin.achieved())
    player_lvl += rating
    for i in challenges:
        if i.completed == True:
            print(i.name)
    with open('/Users/alexey/Python/Orange-Team/HITMAN/Settings/savefile.dat', 'wb') as f:
        pickle.dump([smoking_kills, stretch, personal_goodbye, no_smoking, human_error, suit_only, silent_assasin, sauna_assasination, sushi, heartless, silent_assasin_suit_only, no_evidence, ghost_machine, straight_shot, hold_hair, piano_man, hurt_oneself, tasteless, master_assasin, player_lvl], f, protocol=2)
    return sys.exit()

target_status = {
    0: 'Номер Юки Ямадзаки',
    1: 'Холл',
    2: 'Ресторан',
    3: 'Холл',
    4: 'Зона спа',
    5: 'Зона отдыха',
    6: 'Зона спа',
    7: 'Холл',
    8: 'Номер Юки Ямадзаки'
}

def print_soders():
    return soders

suspicion_count = [0]
kills = [0]
bodies = [0]
time = [0]
soders = [1]
yuki = [1]
morgue_info = 0
cigar_info = 0
cigar_info2 = 0
poison_info = 0
chip_info = 0
yoga_info = 0
final = 0
poison_kill = 0
combat_count = [0]
poisons = [fugu_poison, rat_poison, deadly_poison, emetic_poison]
so = [0]
sauna_kill = 0
yoga_kill = 0
cigar_kill = 0
cigar_place = 0
pilot_info = 0
get_chief_surgeon = 0
surgeon_kill = 0
ai_info = 0