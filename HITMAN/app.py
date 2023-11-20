import sys
from Settings.actions import *
import pickle

while True:
    t = input()
    if t.upper() == 'W':
        time += 0.5
        print(move())
    if t.upper() == 'I':
        print(inventory(time, yuki, soders))
    if t.upper() == 'E':
        time += 1
        print(search(time, yuki, soders))
    if t.upper() == 'S':
        print(status(time, yuki, soders))
    if t.upper() == 'F':
        time += 1
        interaction = interact(time, yuki, soders)
        print(interaction)
        if interaction == location_status(player.location) and player.location == morgue:
            soders = 0
    if t.upper() == 'Q':
        with open('/Users/alexey/Python/Orange-Team/HITMAN/Settings/savefile.dat', 'wb') as f:
            pickle.dump([player_lvl], f, protocol=2)
        sys.exit()
    if player.disguise != 'VIP - пациент':
        so = 1
    if ((target_status[int(time)%9] == player.location.name) and (yuki == 1)) or ((player.location.name == 'Операционная') and (soders == 1)):
        print('\n\nВы находитесь в одной локации с целью')
    if morgue_info == 0 and player.location == morgue:
        print('\n\nВы нашли файл на компьютере. Это заметки о Кураторе и его нейрочипе. В них приводятся подробные сведения об устройстве чипа и принципе его работы, а также описание того, как изменение дозы влияет на настроение Куратора. Судя по всему, увеличение дозы приводит к улучшению его настроения, а уменьшение, напротив, возвращает его в привычное подавленное состояние. Что любопытно, научный сотрудник, похоже, сам менял дозу Куратора без его ведома: для этого он использовал пульт управления чипом, который куратор хранит в своей спальне.')
        morgue_info = 1
    if cigar_info == 0 and cigars in player.inventory:
        print('\n\nДиана: Это пачка сигарет. Не территории клиники «Гама» курение строго запрещено, так что эти сигареты — явная контрабанда.')
        cigar_info = 1
    if cigar_info2 == 0 and player.location == cable_car:
        print('\n\nДиана: Значит, Юки Ямадзаки выронила свои сигареты по пути к клинике. Интересно. Юки Ямадзаки уронила свои сигареты, когда поднималась на фуникулере по прибытии в клинику. Если верить её охране, это её ужасно взбесило. Может быть, тебе удастся утолить её «жажду», 47-й? Сигареты в «Гаме» запрещены, но не все следуют этому правилу...')
        cigar_info2 = 1
    if poison_info == 0 and player.location == restaurant:
        print('\n\nДиана: Ядовитая Рыба фугу и адвокат в поисках острых ощущений — убийственная комбинация. Не так давно из-за ошибки повара один из пациентов отравился ядовитой рыбой, и с тех пор фугу здесь под строжайшим запретом. Но, судя по всему, Юки Ямадзаки пытается уговорить шеф-повара подать ей последнюю рыбу из его запасов. Разве мы вправе отказывает ей в таком удовольствии, 47-й?')
        poison_info = 1
    if chip_info == 0 and chip_control in player.inventory:
        print('\n\nДиана: Нейрочип для изменения настроения. Интересно... Доктор Каташи Ито, он же Куратор, проводит сейчас какое-то медицинское испытание. Интересно. Хранилище органов находится в ведении Куратора, а значит, у него точно есть доступ к сердцу, которое должны пересадить Содерсу. 47-й, я рекомендую найти отчёт сотрудника и выяснить, для чего нужен этот нейроимплантат. Может пригодиться.')
        chip_info = 1
    if yoga_info == 0 and player.location == resort:
        print('\n\nДиана: Расписание занятий по йоге. Имя Юки Ямадзаки — в каждой графе. Что ж, судя по всему, Юки Ямадзаки — настоящий фанат йоги. Из расписания у горячего источника видно, что она заняла тренера на целый день. Готов размяться, 47-й?')
        yoga_info = 1
    if yuki == 0 and soders == 0 and final == 0:
        print('\n\nВсе цели убиты. Найдте выход с миссии.')
        final = 1
    if final == 1 and (player.location == cable_car or player.location == garage or player.location == helipad or player.location == mountain_path):
        print('\n\n1. Завершить миссию')
        t = input()
        print('\n\nДиана: Миссия выполнена, хорошая работа, 47-ой.')
        print(rating(so))
    if (fugu_poison in player.inventory or rat_poison in player.inventory or deadly_poison in player.inventory or emetic_poison in player.inventory) and player.disguise == 'Шеф' and player.location == restaurant and poison_kill == 0:
        print('\n\n1. Отравить роллы\n2. Не отравлять роллы')
        t = input()
        while t.isdigit() == False:
            t = input()
        t = int(t)
        if t == 2:
            print(player.location.name)
        elif t == 1:
            for i in range(len(poisons)):
                if poisons[i] in player.inventory:
                    print(f'{i+1}. {poisons[i].name}')
            t = input()
            while t.isdigit() == False:
                t = input()
            t = int(t)
            if poisons[t-1].deadly == True:
                yuki = 0
                print('Диана: Грамотный ход 47-ой. С Юки Ямадзаки покончено.')
            else:
                print('Цели стало плохо и она направилась в ванную. Пойти за ней?\n1. Да\n2. Нет')
                t = input()
                while t.isdigit() == False:
                    t = input()
                t = int(t)
                if t == 1:
                    print('1. Утопить цель\n2. Уйти')
                    t = input()
                    while t.isdigit() == False:
                        t = input()
                    t = int(t)
                    if t == 2:
                        print(player.location.name)
                        poison_kill = 1
                    elif t == 1:
                        yuki = 0
                        poison_kill = 1
                        print('Цель убита. Хорошая работа.')
                elif t == 2:
                    poison_kill = 1
                    print(player.location.name)
    if player.location == water_control_room and sauna_kill == 0:
        print('\n')
        print('1. Увеличить температуру в бане\n2. Уйти')
        t = input()
        while t.isdigit() == False:
            t = input()
        t = int(t)
        if t == 1:
            sauna_kill = 1
            print('Все люди вышли из бани из-за высокой температуры.\n')
            if yuki == 1:
                print('Юки Ямадзаки: Наконец-то парилка свободна!\nЮки Ямадзаки вошла в баню\n\n1. Запереть дверь в парилку\n2. Уйти')
                t = input()
                while t.isdigit() == False:
                    t = input()
                t = int(t)
                if t == 1:
                    yuki = 0
                    print('Диана: С Юки Ямадзаки покончено. Отличная работа, агент.')
                elif t == 2:
                    print(player.location.name)
            else:
                print(player.location.name)
        elif t == 2:
            print(player.location.name)
    if player.disguise == 'Инструктор по йоге' and yoga_kill == 0 and player.location == resort and yuki == 1:
        print('\n')
        yoga_kill = 1
        print('Юки Ямадзаки: Наконец-то, сколько можно вас ждать!\n1. Начать тренировку по йоге\n2. Уйти')
        t = input()
        while t.isdigit() == False:
            t = input()
        t = int(t)
        if t == 1:
            print('Агент 47: Приступим, эта тренировка смертельно вам понравится.\nЮки Ямадзаки отозвала всю охрану и вывела всех людей из зоны отдыха\n1. Толкнуть Юки Ямадзаки с горы\n2. Завершить тренировку')
            t = input()
            while t.isdigit() == False:
                t = input()
            t = int(t)
            if t == 1:
                yuki = 0
                print('Диана: Отлично сработано. Юки Ямадзаки нас больше не побеспокоит.')
            if t == 2:
                print(player.location.name)
    if player.location == target_suite and cigars in player.inventory and cigar_place == 0:
        print('\n')
        print('1. Положить пачку сигарет\n2. Оставить пачку сигарет')
        t = input()
        while t.isdigit() == False:
            t = input()
        t = int(t)
        if t == 1:
            cigar_place = 1
            print('1. Выйти из номера\n2. Пойти на балкон')
            t = input()
            while t.isdigit() == False:
                t = input()
            t = int(t)
            if t == 1:
                player.location = hall
                print(player.location.name)
            elif t == 2:
                print('1. Создать утечку газа у обогревателя\n2. Уйти из номера')
                t = input()
                while t.isdigit() == False:
                    t = input()
                t = int(t)
                if t == 1:
                    if wrench in player.inventory:
                        print('1. Выйти из номера')
                        input()
                        player.location = hall
                        yuki = 0
                        print('Юки Ямадзаки: Пачка сиграрет? Как я могла ее не заметить!\nЮки Ямадзаки вышла на балкон и воспользовалась зажигалкой, что привело к взрыву.\nДиана: Это было умно, 47-й. Юки Ямадзаки больше нас не побеспокоит.')
                    else:
                        print('У вас нет гаечного ключа')
                        print(player.location.name)
                elif t == 2:
                    player.location = hall
                    print(player.location.name)
        elif t == 2:
            player.location = hall
            print(player.location.name)
    if player.location == target_suite and cigars in player.inventory and cigar_place == 1:
        print('\n')
        print('1. Выйти из номера\n2. Пойти на балкон')
        t = input()
        while t.isdigit() == False:
            t = input()
        t = int(t)
        if t == 1:
            player.location = hall
            print(player.location.name)
        elif t == 2:
            print('1. Создать утечку газа у обогревателя\n2. Уйти из номера')
            t = input()
            while t.isdigit() == False:
                t = input()
            t = int(t)
            if t == 1:
                if wrench in player.inventory:
                    print('1. Выйти из номера')
                    input()
                    player.location = hall
                    yuki = 0
                    print('Юки Ямадзаки: Пачка сиграрет? Как я могла ее не заметить!\nЮки Ямадзаки вышла на балкон и воспользовалась зажигалкой, что привело к взрыву.\nДиана: Это было умно, 47-й. Юки Ямадзаки больше нас не побеспокоит.')
                else:
                    print('У вас нет гаечного ключа')
                    print(player.location.name)
            elif t == 2:
                player.location = hall
                print(player.location.name)
    if (player.location == pilot_room or player.location == helipad) and pilot_info == 0:
        pilot_info = 1
        print('\n\nДиана: 47-й, у меня есть сведения о пилоте. Мне удалось извлечь кое-какие данные из системы безопасности клиники. Главный хирург, Николя Лоран, похоже, часто встречается с пилотом вертолёта у выхода из мед-комплекса. А если верить слухам, у главного хирурга дрожат руки.')
    if 'Главный хирург' in player.found_disguises:
        chief_surgeon = 0
    if player.disguise == 'Пилот' and player.location == helipad and chief_surgeon.alive == True and get_chief_surgeon == 0:
        get_chief_surgeon = 1
        print('\n\nГлавный хирург вышел из мед-комплекса\nГлавный хирург: У тебя еще остались те таблетки?\n47-й: Конечно, следуй за мной.')
        print('\n1. Пойти в комнату пилота\n2. Уйти')
        t = input()
        while t.isdigit() == False:
            t = input()
        t = int(t)
        if t == 2:
            print(status())
        if t == 1:
            player.location = pilot_room
            print('\n\n1. Усмирить главного хирурга\n2. Уйти')
            t = input()
            while t.isdigit() == False:
                t = input()
            t = int(t)
            if t == 2:
                print(player.location.name)
            if t == 1:
                player.found_disguises.append('Главный хирург')
                print(player.location.name)
    if player.location == operation_room and player.disguise == 'Главный хирург' and surgeon_kill == 0 and soders == 1:
        print('\n\n1. Управлять операционным роботом\n2. Не управлять')
        t = input()
        while t.isdigit() == False:
            t = input()
        t = int(t)
        if t == 1:
            print('\n\n1. Убить Эриха Содерса\n2. Уйти')
            t = input()
            while t.isdigit() == False:
                t = input()
            t = int(t)
            if t == 1:
                soders = 0
                surgeon_kill = 1
                print('\n\nДиана: Умно, 47-й. С Содерсом покончено.')
            if t == 2:
                print(player.location.name)
    if 'Охранник' in player.found_disguises or 'Телохранитель' in player.found_disguises:
        player.inventory.append(pistol)
    if player.location == server_room and soders == 1:
        print('\n\n1. Повредить серверы\n2. Не повреждать')
        t = input()
        while t.isdigit() == False:
            t = input()
        t = int(t)
        if t == 1:
            soders = 0
            print('\n\nХирург: Что происходит с роботом?! Как его отключить?! Пациент сейчас умрет!')
            print('Диана: Это было впечатляюще, агент. Эрих Содерс мертв.')
        if t == 2:
            print(player.location.name)
    if player.location == security_room and ai_info == 0:
        ai_info = 1
        print('\n\nИнтересно. Руководство для KAI, искусственного интеллекта клиники «Гама». Значит, местный искусственный интеллект по имени KAI не только поддерживает работу систем здания, но и управляет роботом в операционной. Именно там сейчас находится Содерс. В руководстве говорится, что после остановки сердца пациента искусственный интеллект автоматически начинает его реанимацию, что очень некстати. Однако... У директора клиники есть доступ к главному компьютеру. Справишься с управлением целой клиникой, 47-й?')