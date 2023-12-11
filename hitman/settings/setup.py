import sys
import pickle
from settings.locations import *
from settings.loot import *
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

def tutorial():
    print('Брифинг:\nДиана: Добро пожаловать на тренировку повышенной сложности. Прототипом этого задания стала операция в Сиднее. Целью был Кэлвин Риттер, знаменитый грабитель по прозвищу Воробей. Тебе нужно проникнуть на яхту, изолировать, а затем устранить цель и скрыться — всё незаметно. Запомни: ты агент МКА, самый опасный человек в любой ситуации. Но грубой силой в нашем деле многого не добьёшься, а настоящий профессионал никогда не привлекает внимания. Удачи, новичок.')
    print('\nЭто обучающий сегмент, здесь вам необходимо выполнять инструкции, в основной игре у вас будет полная свобода выбора.')
    print('\n\nНажмите "S", чтобы осмотреться.')
    t = input()
    while t.upper() != 'S':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\n1. Статус Пристань\n2. Общий статус')
    t = input()
    while t != '1' and t != '2':
        t = input()
    t = int(t)
    if t == 1:
        print('\n\nПристань\n\nНа локации нет свидетелей')
    elif t == 2:
        print('Кэлвин Риттер: Бар\n\nТекущая маскировка: Тренировочный костюм\nПредмет в руках: Нет предмета')
    print('\n\nОтлично, теперь обыщите текущую локацию. Намжмите "E", чтобы добавить в инвентарь все предметы на локации.')
    t = input()
    while t.upper() != 'E':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\n1. Пистолет с глушителем (1)\n2. Удавка (1)\n3. Монета (1)\n\nСейчас в руках: Нет предмета\n4. Убрать предмет из рук\n\n5. Тренировочный костюм')
    print('\n\nЗамечательно, теперь переместитесь в ангар. Нажмите "W" для перемещения.')
    t = input()
    while t.upper() != 'W':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\n1. Ангар\n2. Нижняя палуба\n3. Верхняя палуба')
    t = input()
    while t != '1':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\nУ вас нет подходящей маскировки. Переместиться на локацию? (10/10)\n1. Да\n2. Нет')
    t = input()
    while t != '1':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\nАнгар\n\nНа локации находятся:\n\n1 Инженер\n\nВсего 1 свидетелей')
    print('\n\nОтлично. Теперь откройте инвентарь, нажав "I" и возмите в руки монету.')
    t = input()
    while t.upper() != 'I':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\n1. Пистолет с глушителем (1)\n2. Удавка (1)\n3. Монета (1)\n\nСейчас в руках: Нет предмета\n4. Убрать предмет из рук\n\n5. Тренировочный костюм')
    t = input()
    while t.upper() != '3':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\nСейчас в руках: Монета')
    print('\n\nТак держать. Теперь используйте ее, чтобы отвлечь инженера и вырубить его. Для использования предмета в руках нажмите "F".')
    t = input()
    while t.upper() != 'F':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\nДействия видят 1 человек\n\n1. Бросить для отвлечения\n2. Отменить действие')
    t = input()
    while t.upper() != '1':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\n1. Отвлечь Инженер (Joseph Harding)\n2. Отвлечь для перемещения')
    t = input()
    while t.upper() != '1':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\n1. Вырубить Инжeнер (Joseph Harding)\n2. Убить Инженер (Joseph Harding)')
    t = input()
    while t != '1' and t != '2':
        t = input()
    t = int(t)
    if t == 2:
        print('\n\nУбийства кого-либо кроме целей негативно сказывается на вашем рейтенге задания.')
    print('\n\nОтлично, теперь откройте инвентарь и смените текущую маскировку на инженера.')
    t = input()
    while t.upper() != 'I':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\n1. Пистолет с глушителем (1)\n2. Удавка (1)\n\nСейчас в руках: Нет предмета\n3. Убрать предмет из рук\n\n4. Тренировочный костюм')
    t = input()
    while t.upper() != '4':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\n1. Тренировочный костюм\n2. Инженер')
    t = input()
    while t.upper() != '2':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\nТекущая маскировка: Инженер')
    print('\n\nВеликолепно, теперь пройдите в гараж, а затем в раздевалку персонала.')
    t = input()
    while t.upper() != 'W':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\n1. Пристань\n2. Гараж')
    t = input()
    while t.upper() != '2':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\nГараж\n\nНа локации находятся:\n\n3 Инженер\n\nВсего 2 свидетелей')
    t = input()
    while t.upper() != 'W':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\n1. Раздевалка персонала\n2. Ангар')
    t = input()
    while t.upper() != '1':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\nРаздевалка персонала\n\nНа локации находятся:\n\n1 Экипаж яхты\n\nВсего 0 свидетелей')
    print('\n\nВеликолепно, усмирите экипаж яхты, чтобы забрать его маскировку. Чтобы усмирить человека, необходимо нажать "F", не имея ничего в руках.')
    t = input()
    while t.upper() != 'F':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\nДействия видят 0 человек\n\n1. Усмирить\n2. Отменить действие')
    t = input()
    while t.upper() != '1':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\n1. Усмирить Экипаж яхты (Joseph Reeves)')
    t = input()
    while t.upper() != '1':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('Замечательно, теперь смените свою маскировку и поднимитесь на верхнюю палубу.')
    t = input()
    while t.upper() != 'I':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\n1. Пистолет с глушителем (1)\n2. Удавка (1)\n\nСейчас в руках: Нет предмета\n3. Убрать предмет из рук\n\n4. Инженер')
    t = input()
    while t.upper() != '4':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\n1. Тренировочный костюм\n2. Инженер\n3. Экипаж яхты')
    t = input()
    while t.upper() != '3':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\nТекущая маскировка: Экипаж яхты')
    t = input()
    while t.upper() != 'W':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\n1. Верхняя палуба\n2. Гараж')
    t = input()
    while t.upper() != '1':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\nВерхняя палуба\n\nНа локации находятся:\n\n3 Экипаж яхты\n3 Охранник\n\nВсего 5 свидетелей')
    print('Замечательно. К сожалению проход в лючную каюту Риттера ограждают его телохранители. Но можно пролезть в нее через окно.\n\n1. Пролезть в каюту Риттера')
    t = input()
    while t.upper() != '1':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('Настал решающий момент, достаньте пистолет с глушителем из инвентаря и выстрелете в вашу цель.')
    t = input()
    while t.upper() != 'I':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\n1. Пистолет с глушителем (1)\n2. Удавка (1)\n\nСейчас в руках: Нет предмета\n3. Убрать предмет из рук\n\n4. Экипаж яхты')
    t = input()
    while t.upper() != '1':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('Пистолет с глушителем -- это нелегальный прдмет. Достать предмет?\n1. Да\n2. Нет')
    t = input()
    while t.upper() != '1':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\nСейчас в руках: Пистолет с глушителем')
    t = input()
    while t.upper() != 'F':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\nДействия видят 0 человек\n\n1. Выстрелить\n2. Отменить действие')
    t = input()
    while t.upper() != '1':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\n1. Выстрелить в Кэлвина Риттера')
    t = input()
    while t.upper() != '1':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\nДиана: Цель устранена, неплохо для новичка.')
    print('\n\nВсе цели убиты. Найдте выход с миссии.')
    print('\n\nНаправляйтесь на выход с миссии на пристани.')
    t = input()
    while t.upper() != 'W':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\n1. Пристань\n2. Гараж')
    t = input()
    while t.upper() != '1':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\nПристань\n\nНа локации нет свидетелей')
    print('\n\n1. Завершить мисиию')
    t = input()
    while t.upper() != '1':
        print('\n\nВ обучении вам необходимо следовать инструкции.')
        t = input()
    print('\n\nОбучение пройдено.\n\n1. Пройти еще раз\n2. Приступить к новой миссии')
    t = input()
    while t.isdigit() == False:
        t = input()
    t = int(t)
    if t == 1:
        return(tutorial())
    return ''

os.chdir('hitman')
if os.stat('save_file.dat').st_size != 0:
    with open('save_file.dat', 'rb') as f:
        smoking_kills, stretch, personal_goodbye, no_smoking, human_error, suit_only, silent_assasin, sauna_assasination, sushi, heartless, silent_assasin_suit_only, no_evidence, ghost_machine, straight_shot, hold_hair, piano_man, hurt_oneself, tasteless, master_assasin, player_lvl = pickle.load(f)
else:
    print('Пройти обучение?\n1. Да\n2. Нет')
    t = input()
    while t.isdigit() == False:
        t = input()
    t = int(t)
    if t == 1:
        print(tutorial())

challenges = [smoking_kills, stretch, personal_goodbye, no_smoking, human_error, suit_only, silent_assasin, sauna_assasination, sushi, heartless, silent_assasin_suit_only, no_evidence, ghost_machine, straight_shot, hold_hair, piano_man, hurt_oneself, tasteless, master_assasin]

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
            print(f'{i+1}. {carry_on_items[i].__name}')
        t = input()
        while t.isdigit() == False:
            t = input()
        t = int(t)
        start_inventory.append(carry_on_items[t-1])
        carry_on_items.remove(carry_on_items[t-1])
        print('\n\nВыберите второй предмет сняряжения:\n')
        for i in range(len(carry_on_items)):
            print(f'{i+1}. {carry_on_items[i].__name}')
        t = input()
        while t.isdigit() == False:
            t = input()
        t = int(t)
        start_inventory.append(carry_on_items[t-1])
    print('\n\nДиана: Удачи, агент.')
    if start_location[1] == suite:
        print('\n\nДиана: Добро пожаловать на Хоккайдо, 47-й. Частная клиника «Гама» оказывает медицинские услуги высочайшего уровня представителям мировой элиты, выходя при необходимости за рамки закона. Частично здание находится под управлением искусственного интеллекта — KAI. Система контролирует доступ пациентов в разные части клиники и даже принимает участие в ряде медицинских процедур. Эрих Содерс уже находится в операционной, где он проходит предварительную подготовку с применением стволовых клеток. Это крайне противоречивая процедура ещё не одобрена властями Японии. Юки Ямадзаки уже прибыла. Она находится либо в своём номере, либо в ресторане, либо в спа-зоне клиники. Содерсу скоро введут наркоз. Сделай так, чтобы он больше никогда не проснулся. Удачи, 47-й.')
    return Player(start_inventory, 100, start_location[1], [start_location[2]], arms, [], start_location[2])

player = start()

class NPC:

    def __init__(self, guard, disguise, alive, route, witness_chance, name):
        self.guard = guard
        self.disguise = disguise
        self.alive = alive
        self.route = route
        self.witness_chance = witness_chance
        self.name = name

    def print_name(self):
        return f'{self.disguise} ({self.name})'

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
            return f'\n\n{self.print_name()}: Эй, ты не можешь здесь находится!'
        else:
            return False

guard_cable_car_1 = NPC(True, 'Телохранитель', True, {0: 'Канатная дорога'}, 5, 'Shoichi Kataoka')
guard_cable_car_2 = NPC(True, 'Телохранитель', True, {0: 'Канатная дорога'}, 5, 'Hidaka Uno')
guard_hall_1 = NPC(True, 'Охранник', True, {0: 'Холл'}, 8, 'Nikica Pranjić')
guard_hall_2 = NPC(True, 'Охранник', True, {0: 'Холл'}, 8, 'Toshimi Shinden')
guard_hall_3 = NPC(True, 'Охранник', True, {0: 'Холл', 1: 'Комната охраны'}, 8, 'Hans Hansson')
guard_spa_1 = NPC(True, 'Охранник', True, {0: 'Зона спа'}, 4, 'Masashi Morioka')
guard_restaurant_1 = NPC(True, 'Охранник', True, {0: 'Ресторан'}, 8, 'Tadao Motsuzuki')
guard_restaurant_2 = NPC(True, 'Охранник', True, {0: 'Ресторан'}, 9, 'Hidetoshi Higa')
guard_garden_1 = NPC(True, 'Охранник', True, {0: 'Внутренний сад'}, 3, 'Oliver Drabløs')
guard_garden_2 = NPC(True, 'Охранник', True, {0: 'Внутренний сад'}, 5, 'Yasuaki Inagaki')
guard_medical_center_1 = NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс'}, 6, 'Junya Andou')
guard_medical_center_2 = NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс'}, 7, 'Homare Kanai')
guard_medical_center_3 = NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс'}, 6, 'Toshihisa Taniguchi')
guard_medical_center_4 = NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс', 1: 'Операционная'}, 9, 'Shuusuke Seki')
guard_security_room = NPC(True, 'Охранник', True, {0: 'Комната охраны'}, 9, 'Kyuuya Sugiyama')
guard_garage = NPC(True, 'Охранник', True, {0: 'Гараж'}, 7, 'Max Gerber')
guard_bar = NPC(True, 'Охранник', True, {0: 'Барная стойка'}, 2, 'John Maverick')
guard_morgue = NPC(True, 'Телохранитель', True, {0: 'Морг'}, 2, 'Miamoto San')
guard_target_suite_1 = NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки', 1: 'Холл'}, 8, 'Kyouta Shinden')
guard_target_suite_2 = NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки', 1: 'Холл'}, 9, 'Hayaki Fukasawa')
guard_target_suite_3 = NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки'}, 8, 'Kaimei Kuroki')
guard_target_suite_4 = NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки'}, 7, 'Kou Tokunaga')
guard_target_suite_5 = NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки'}, 7, 'Salvio Parra Rojo')
guard_target_suite_6 = NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки'}, 7, 'Yoshikazu Sasaki')
guard_helipad_1 = NPC(True, 'Телохранитель', True, {0: 'Вертолетная площадка'}, 8, 'Samuel Santos Lima')
guard_helipad_2 = NPC(True, 'Телохранитель', True, {0: 'Вертолетная площадка'}, 9, 'Rafn Helguson')
guard_medical_center_level_2_1 = NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс (2 этаж)'}, 8, 'Hayato Shinden')
guard_medical_center_level_2_2 = NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс (2 этаж)'}, 9, 'Shuusuke Kitajima')
guard_medical_center_level_2_3 = NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс (2 этаж)'}, 7, 'Sorahiko Satou')
guard_medical_center_level_2_4 = NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс (2 этаж)'}, 8, 'Satomu Sugiyama')
target_guard_1 = NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки', 1: 'Холл', 2: 'Ресторан', 3: 'Холл', 4: 'Зона спа', 5: 'Зона отдыха', 6: 'Зона спа', 7: 'Холл', 8: 'Номер Юки Ямадзаки'}, 8, 'Nokadota')
target_guard_2 = NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки', 1: 'Холл', 2: 'Ресторан', 3: 'Холл', 4: 'Зона спа', 5: 'Зона отдыха', 6: 'Зона спа', 7: 'Холл', 8: 'Номер Юки Ямадзаки'}, 8, 'Yuuto Saiki')

staff_spa_1 = NPC(False, 'Работник "ГАМА"', True, {0: 'Зона спа', 1: 'Зона отдыха'}, 7, 'Tamika Oomori')
staff_spa_2 = NPC(False, 'Работник "ГАМА"', True, {0: 'Зона спа'}, 8, 'Harumi Sakei')
staff_restaurant_1 = NPC(False, 'Работник "ГАМА"', True, {0: 'Ресторан'}, 7, 'Kouko Yoshioka')
staff_restaurant_2 = NPC(False, 'Работник "ГАМА"', True, {0: 'Ресторан'}, 8, 'Risae Oosawa')
staff_garden_1 = NPC(False, 'Работник "ГАМА"', True, {0: 'Внутренний сад'}, 1, 'Maury Veich')
staff_garden_2 = NPC(False, 'Работник "ГАМА"', True, {0: 'Внутренний сад'}, 3, 'Johan Ishibashi')
surgeon_medical_center = NPC(False, 'Хирург', True, {0: 'Мед-комплекс', 1: 'Операционная'}, 9, 'Saita Shinoda')
mechanic_garage = NPC(False, 'Механик', True, {0: 'Гараж'}, 1, 'Tomochika Honma')
yoga_coach = NPC(False, 'Инструктор по йоге', True, {0: 'Гараж', 1: 'Спальня персонала'}, 1, 'J. Brooke')
chef_1 = NPC(False, 'Шеф', True, {0: 'Кухня'}, 7, 'Ikkei Tsutsui')
chef_2 = NPC(False, 'Шеф', True, {0: 'Кухня'}, 8, 'Minao Morishita')
morgue_worker_1 = NPC(False, 'Работник морга', True, {0: 'Морг'}, 6, 'Katshi Ito')
morgue_worker_2 = NPC(False, 'Работник морга', True, {0: 'Морг'}, 7, 'Tenri Shinosaki')
morgue_worker_3 = NPC(False, 'Работник морга', True, {0: 'Морг'}, 5, 'Shoudai Kurosawa')
surgeon_operation_room_1 = NPC(False, 'Хирург', True, {0: 'Операционная'}, 7, 'Kii Ine')
surgeon_operation_room_2 = NPC(False, 'Хирург', True, {0: 'Операционная'}, 9, 'Emiri Nimiya')
surgeon_operation_room_3 = NPC(False, 'Хирург', True, {0: 'Операционная'}, 8, 'Gakushi Yamaoka')
chief_surgeon = NPC(False, 'Главный хирург', True, {0: 'Операционная'}, 7, 'Nicholas Laurent')
pilot = NPC(False, 'Пилот', True, {0: 'Комната пилота'}, 3, 'Nails')
director = NPC(False, 'Директор клиники', True, {0: 'Холл', 1: 'Внутренний сад', 2: 'Холл', 3: 'Мед-комплекс', 4: 'Мед-комплекс (2 этаж)', 5: 'Комната директора клиники', 6: 'Комната директора клиники', 7:'Комната директора клиники', 8: 'Мед-комплекс (2 этаж)', 9: 'Мед-комплекс', 10: 'Холл'}, 7, 'Akira Nakamura')

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
        guard_target_suite_6,
        guard_target_suite_5,
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
        target_guard_1,
        target_guard_2,
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
    with open('save_file.dat', 'wb') as f:
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