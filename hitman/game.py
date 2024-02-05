import sys
import pickle
import os

from controller.controller import PlayerController
from model.hokkaido.hokkaido_events import HokkaidoEvents
from model.player.player import Player
from model.player.player_info import *
from model.hokkaido.hokkaido_locator import HokkaidoLocator
from model.hokkaido.hokkaido_challenges import HokkaidoChallenges
from view.console_view import ConsoleView
from config.net_config import NetConfig

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup,ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, PollAnswerHandler, PollHandler

#Загрузка испытаний из файла сохранения
os.chdir('hitman')
if os.stat('save_file.dat').st_size != 0:
    with open('save_file.dat', 'rb') as f:
        challenges = pickle.load(f)
else:
    challenges = HokkaidoChallenges()

#Определение стандартных значений для старта игры
events = HokkaidoEvents()
locator = HokkaidoLocator(challenges)
player = Player(location=locator.get_location_by_name('Номер 47-го'),
                inventory=[],
                health=100,
                item=locator.get_items().get_by_name('Нет предмета'),
                compromised_disguises=[],
                disguise='VIP - пациент',
                found_disguises=['VIP - пациент'])

controller = PlayerController(player=player, locator=locator, player_view=ConsoleView())

#Основной код, который выполняет контроллер
def main(controller: PlayerController):
    controller.start()
    while True:
        request = controller.player_view.request()
        if request.upper() == 'W':
            controller.move()
            time[0] += 0.5
        elif request.upper() == 'S':
            controller.status()
        elif request.upper() == 'C':
            controller.see_challenges()
        elif request.upper() == 'E':
            controller.search()
            time[0] += 1
        elif request.upper() == 'I':
            controller.inventory()
        elif request.upper() == 'F':
            controller.interact()
            time[0] += 1
        elif request.upper() == 'Q':
            with open('save_file.dat', 'wb') as f:
                pickle.dump([locator.get_challenges(), player_lvl], f, protocol=2)
            sys.exit()
        
        if events.get_by_name('Компьютер в морге').completed == False and player.current_location.get_name() == 'Морг':
            controller.player_view.response('Вы нашли файл на компьютере. Это заметки о Кураторе и его нейрочипе. В них приводятся подробные сведения об устройстве чипа и принципе его работы, а также описание того, как изменение дозы влияет на настроение Куратора. Судя по всему, увеличение дозы приводит к улучшению его настроения, а уменьшение, напротив, возвращает его в привычное подавленное состояние. Что любопытно, научный сотрудник, похоже, сам менял дозу Куратора без его ведома: для этого он использовал пульт управления чипом, который куратор хранит в своей спальне.')
            events.get_by_name('Компьютер в морге').completed = True

        if player.disguise != 'VIP - пациент':
            so[0] = 1
        
        if events.get_by_name('Информация о сигаретах 1').completed == False and locator.get_items().get_by_name('Пачка сигарет') in player.inventory:
            controller.player_view.response('Диана: Это пачка сигарет. Не территории клиники «Гама» курение строго запрещено, так что эти сигареты — явная контрабанда.')
            events.get_by_name('Информация о сигаретах 1').completed = True
        
        if events.get_by_name('Информация о сигаретах 2').completed == False and player.current_location.get_name() == 'Канатная дорога':
            controller.player_view.response('Диана: Значит, Юки Ямадзаки выронила свои сигареты по пути к клинике. Интересно. Юки Ямадзаки уронила свои сигареты, когда поднималась на фуникулере по прибытии в клинику. Если верить её охране, это её ужасно взбесило. Может быть, тебе удастся утолить её «жажду», 47-й? Сигареты в «Гаме» запрещены, но не все следуют этому правилу...')
            events.get_by_name('Информация о сигаретах 2').completed = True
        
        if events.get_by_name('Информация о суши').completed == False and player.current_location.get_name() == 'Ресторан':
            controller.player_view.response('Диана: Ядовитая Рыба фугу и адвокат в поисках острых ощущений — убийственная комбинация. Не так давно из-за ошибки повара один из пациентов отравился ядовитой рыбой, и с тех пор фугу здесь под строжайшим запретом. Но, судя по всему, Юки Ямадзаки пытается уговорить шеф-повара подать ей последнюю рыбу из его запасов. Разве мы вправе отказывает ей в таком удовольствии, 47-й?')
            events.get_by_name('Информация о суши').completed = True
        
        if events.get_by_name('Информация о чипе').completed == False and locator.get_items().get_by_name('Пульт для управления нейрочипом') in player.inventory:
            controller.player_view.response('Диана: Нейрочип для изменения настроения. Интересно... Доктор Каташи Ито, он же Куратор, проводит сейчас какое-то медицинское испытание. Интересно. Хранилище органов находится в ведении Куратора, а значит, у него точно есть доступ к сердцу, которое должны пересадить Содерсу. 47-й, я рекомендую найти отчёт сотрудника и выяснить, для чего нужен этот нейроимплантат. Может пригодиться.')
            events.get_by_name('Информация о чипе').completed = True
        
        if events.get_by_name('Расписание занятий по йоге').completed == False and player.current_location.get_name() == 'Зона отдыха':
            controller.player_view.response('Диана: Расписание занятий по йоге. Имя Юки Ямадзаки — в каждой графе. Что ж, судя по всему, Юки Ямадзаки — настоящий фанат йоги. Из расписания у горячего источника видно, что она заняла тренера на целый день. Готов размяться, 47-й?')
            events.get_by_name('Расписание занятий по йоге').completed = True
        
        if locator.get_targets().get_by_name('Юки Ямадзаки').alive == False and locator.get_targets().get_by_name('Эрих Содерс').alive == False and events.get_by_name('Все цели убиты').completed == False:
            controller.player_view.response('Все цели убиты. Найдте выход с миссии.')
            events.get_by_name('Все цели убиты').completed = True
        
        if events.get_by_name('Все цели убиты').completed == True and (player.current_location.get_name() == 'Канатная дорога' or player.current_location.get_name() == 'Гараж' or player.current_location.get_name() == 'Вертолетная площадка' or player.current_location.get_name() == 'Горная тропа'):
            controller.player_view.response('1. Завершить миссию')
            controller.player_view.request()
            controller.player_view.response('Диана: Миссия выполнена, хорошая работа, 47-ой.')
            controller.rating()
        
        if (locator.get_items().get_by_name('Яд рыбы Фугу') in player.inventory or locator.get_items().get_by_name('Крысиный яд') in player.inventory or locator.get_items().get_by_name('Смертельный яд') in player.inventory or locator.get_items().get_by_name('Рвотный яд') in player.inventory) and player.disguise == 'Шеф' and player.current_location.get_name() == 'Ресторан' and events.get_by_name('Убийство ядом').completed == False:
            controller.player_view.response('1. Отравить роллы\n2. Не отравлять роллы')
            request = controller.player_view.request()
            while request.isdigit() == False:
                controller.player_view.response('Введите номер ответа')
                request = controller.player_view.request()
            request = int(request)
            if request == 2:
                controller.player_view.response(locator.location_status(player.current_location))
            elif request == 1:
                events.get_by_name('Убийство ядом').completed = True
                poisons = [locator.get_items().get_by_name('Яд рыбы Фугу'), locator.get_items().get_by_name('Крысиный яд'), locator.get_items().get_by_name('Смертельный яд'), locator.get_items().get_by_name('Рвотный яд')]
                result_string = ''
                for i in range(len(poisons)):
                    if poisons[i] in player.inventory:
                        result_string += f'{i+1}. {poisons[i].name}\n'
                controller.player_view.response(result_string)
                request = controller.player_view.request()
                while request.isdigit() == False:
                    controller.player_view.response('Введите номер ответа')
                    request = controller.player_view.request()
                request = int(request)
                player.inventory.remove(poisons[request - 1])
                if poisons[request - 1].deadly == True:
                    result_string = ''
                    if poisons[request - 1] == locator.get_items().get_by_name('Яд рыбы Фугу'):
                        controller.player_view.response(f'{locator.get_challenges().get_by_name('Приятного аппетита').achieved()}')
                    locator.get_targets().get_by_name('Юки Ямадзаки').alive = False
                    controller.player_view.response(locator.get_challenges().get_by_name('Без вкуса, без следа').achieved())
                    result_string += '\n\nДиана: Грамотный ход 47-ой. С Юки Ямадзаки покончено.'
                    controller.player_view.response(result_string)
                else:
                    controller.player_view.response('Цели стало плохо и она направилась в ванную. Пойти за ней?\n\n1. Да\n2. Нет')
                    request = controller.player_view.request()
                    while request.isdigit() == False:
                        controller.player_view.response('Введите номер ответа')
                        request = controller.player_view.request()
                    request = int(request)
                    if request == 1:
                        controller.player_view.response('1. Утопить цель\n2. Уйти')
                        request = controller.player_view.request()
                        while request.isdigit() == False:
                            controller.player_view.response('Введите номер ответа')
                            request = controller.player_view.request()
                        request = int(request)
                        if request == 2:
                            controller.player_view.response(locator.location_status(player.current_location))
                        elif request == 1:
                            controller.player_view.response(f'{locator.get_challenges().get_by_name('Подержи волосы').achieved()}')
                            controller.player_view.response(f'{locator.get_challenges().get_by_name('Так можно и пораниться').achieved()}')
                            result_string = 'Диана: Цель убита. Хорошая работа.'
                            locator.get_targets().get_by_name('Юки Ямадзаки').alive = False
                            controller.player_view.response(result_string)
                    elif request == 2:
                        controller.player_view.response(locator.location_status(player.current_location))
        
        if player.current_location.get_name() == 'Комната управления системой водоснабжения спа' and events.get_by_name('Убийство в сауне').completed == False:
            controller.player_view.response('1. Увеличить температуру в бане\n2. Уйти')
            request = controller.player_view.request()
            while request.isdigit() == False:
                controller.player_view.response('Введите номер ответа')
                request = controller.player_view.request()
            request = int(request)
            if request == 1:
                events.get_by_name('Убийство в сауне').completed = True
                controller.player_view.response('Все люди вышли из бани из-за высокой температуры.')
                if locator.get_targets().get_by_name('Юки Ямадзаки').alive == True:
                    controller.player_view.response('Юки Ямадзаки: Наконец-то парилка свободна!\nЮки Ямадзаки вошла в баню\n\n1. Запереть дверь в парилку\n2. Уйти')
                    request = controller.player_view.request()
                    while request.isdigit() == False:
                        controller.player_view.response('Введите номер ответа')
                        request = controller.player_view.request()
                    request = int(request)
                    if request == 1:
                        locator.get_targets().get_by_name('Юки Ямадзаки').alive = False
                        controller.player_view.response(f'{locator.get_challenges().get_by_name('Убийство в парилке').achieved()}')
                        controller.player_view.response(f'{locator.get_challenges().get_by_name('Так можно и пораниться').achieved()}')
                        result_string = 'Диана: С Юки Ямадзаки покончено. Отличная работа, агент.'
                        controller.player_view.response(result_string)
                    elif request == 2:
                        controller.player_view.response(locator.location_status(player.current_location))
                else:
                    controller.player_view.response(locator.location_status(player.current_location))
            elif request == 2:
                controller.player_view.response(locator.location_status(player.current_location))
        
        if player.disguise == 'Инструктор по йоге' and events.get_by_name('Убийство во время йоги').completed == False and player.current_location == 'Зона отдыха' and locator.get_targets().get_by_name('Юки Ямадзаки').alive == True:
            events.get_by_name('Убийство во время йоги').completed = True
            controller.player_view.response('Юки Ямадзаки: Наконец-то, сколько можно вас ждать!\n\n1. Начать тренировку по йоге\n2. Уйти')
            request = controller.player_view.request()
            while request.isdigit() == False:
                controller.player_view.response('Введите номер ответа')
                request = controller.player_view.request()
            request = int(request)
            if request == 1:
                controller.player_view.response('Агент 47: Приступим, эта тренировка смертельно вам понравится.\nЮки Ямадзаки отозвала всю охрану и вывела всех людей из зоны отдыха\n\n1. Толкнуть Юки Ямадзаки с горы\n2. Завершить тренировку')
                request = controller.player_view.request()
                while request.isdigit() == False:
                    controller.player_view.response('Введите номер ответа')
                    request = controller.player_view.request()
                request = int(request)
                if request == 1:
                    locator.get_targets().get_by_name('Юки Ямадзаки').alive = False
                    controller.player_view.response(f'{locator.get_challenges().get_by_name('Хорошая растяжка').achieved()}')
                    controller.player_view.response(f'{locator.get_challenges().get_by_name('Так можно и пораниться').achieved()}')
                    result_string = 'Диана: Отлично сработано. Юки Ямадзаки нас больше не побеспокоит.'
                    controller.player_view.response(result_string)
                if request == 2:
                    controller.player_view.response(locator.location_status(player.current_location))
        
        if player.current_location.get_name() == 'Номер Юки Ямадзаки' and locator.get_items().get_by_name('Пачка сигарет') in player.inventory and events.get_by_name('Сигареты на столе').completed == False:
            controller.player_view.response('1. Положить пачку сигарет\n2. Оставить пачку сигарет')
            request = controller.player_view.request()
            while request.isdigit() == False:
                controller.player_view.response('Введите номер ответа')
                request = controller.player_view.request()
            request = int(request)
            if request == 1:
                player.inventory.remove(locator.get_items().get_by_name('Пачка сигарет'))
                controller.player_view.response(f'{locator.get_challenges().get_by_name('Не курить!').achieved()}')
                result_string = '1. Выйти из номера\n2. Пойти на балкон'
                controller.player_view.response(result_string)
                events.get_by_name('Сигареты на столе').completed = True
                request = controller.player_view.request()
                while request.isdigit() == False:
                    controller.player_view.response('Введите номер ответа')
                    request = controller.player_view.request()
                request = int(request)
                if request == 1:
                    player.current_location = locator.get_location_by_name('Холл')
                    controller.player_view.response(locator.location_status(player.current_location))
                elif request == 2:
                    controller.player_view.response('1. Создать утечку газа у обогревателя\n2. Уйти из номера')
                    request = controller.player_view.request()
                    while request.isdigit() == False:
                        controller.player_view.response('Введите номер ответа')
                        request = controller.player_view.request()
                    request = int(request)
                    if request == 1:
                        if locator.get_items().get_by_name('Гаечный ключ') in player.inventory:
                            controller.player_view.response('1. Выйти из номера')
                            controller.player_view.request()
                            player.current_location = locator.get_location_by_name('Холл')
                            if locator.get_targets().get_by_name('Юки Ямадзаки').alive == True:
                                locator.get_targets().get_by_name('Юки Ямадзаки').alive = False
                                controller.player_view.response(f'{locator.get_challenges().get_by_name('Курение убивает').achieved()}')
                                controller.player_view.response(f'{locator.get_challenges().get_by_name('Так можно и пораниться').achieved()}')
                                result_string = 'Юки Ямадзаки: Пачка сиграрет? Как я могла ее не заметить!\nЮки Ямадзаки вышла на балкон и воспользовалась зажигалкой, что привело к взрыву.\n\nДиана: Это было умно, 47-й. Юки Ямадзаки больше нас не побеспокоит.'
                                controller.player_view.response(result_string)
                        else:
                            controller.player_view.response('У вас нет гаечного ключа')
                    elif request == 2:
                        player.current_location = locator.get_location_by_name('Холл')
                        controller.player_view.response(locator.location_status(player.current_location))
            elif request == 2:
                player.current_location = locator.get_location_by_name('Холл')
                controller.player_view.response(locator.location_status(player.current_location))
        
        if player.current_location.get_name() == 'Номер Юки Ямадзаки' and events.get_by_name('Сигареты на столе').completed == True:
            controller.player_view.response('1. Выйти из номера\n2. Пойти на балкон')
            request = controller.player_view.request()
            while request.isdigit() == False:
                controller.player_view.response('Введите номер ответа')
                request = controller.player_view.request()
            request = int(request)
            if request == 1:
                player.current_location = locator.get_location_by_name('Холл')
                controller.player_view.response(locator.location_status(player.current_location))
            elif request == 2:
                controller.player_view.response('1. Создать утечку газа у обогревателя\n2. Уйти из номера')
                while request.isdigit() == False:
                    controller.player_view.response('Введите номер ответа')
                    request = controller.player_view.request()
                request = int(request)
                if request == 1:
                    if locator.get_items().get_by_name('Гаечный ключ') in player.inventory:
                            controller.player_view.response('1. Выйти из номера')
                            controller.player_view.request()
                            player.current_location = locator.get_location_by_name('Холл')
                            if locator.get_targets().get_by_name('Юки Ямадзаки').alive == True:
                                locator.get_targets().get_by_name('Юки Ямадзаки').alive = False
                                controller.player_view.response(f'{locator.get_challenges().get_by_name('Курение убивает').achieved()}')
                                controller.player_view.response(f'{locator.get_challenges().get_by_name('Так можно и пораниться').achieved()}')
                                result_string = 'Юки Ямадзаки: Пачка сиграрет? Как я могла ее не заметить!\nЮки Ямадзаки вышла на балкон и воспользовалась зажигалкой, что привело к взрыву.\n\nДиана: Это было умно, 47-й. Юки Ямадзаки больше нас не побеспокоит.'
                                controller.player_view.response(result_string)
                    else:
                        controller.player_view.response('У вас нет гаечного ключа')
                elif request == 2:
                    player.current_location = locator.get_location_by_name('Холл')
                    controller.player_view.response(locator.location_status(player.current_location))
        
        if (player.current_location.get_name() == 'Комната пилота' or player.current_location.get_name() == 'Вертолетная площадка') and events.get_by_name('Информация о пилоте').completed == False:
            events.get_by_name('Информация о пилоте').completed = True
            controller.player_view.response('Диана: 47-й, у меня есть сведения о пилоте. Мне удалось извлечь кое-какие данные из системы безопасности клиники. Главный хирург, Николя Лоран, похоже, часто встречается с пилотом вертолёта у выхода из мед-комплекса. А если верить слухам, у главного хирурга дрожат руки.')
        
        if player.disguise == 'Пилот' and player.current_location.get_name() == 'Вертолетная площадка' and locator.get_npcs().get_by_name('Nicholas Laurent').alive == True and events.get_by_name('Устранение главного хирурга').completed == False:
            events.get_by_name('Устранение главного хирурга').completed = True
            controller.player_view.response('Главный хирург вышел из мед-комплекса\nГлавный хирург: У тебя еще остались те таблетки?\n47-й: Конечно, следуй за мной.\n\n1. Пойти в комнату пилота\n2. Уйти')
            request = controller.player_view.request()
            while request.isdigit() == False:
                controller.player_view.response('Введите номер ответа')
                request = controller.player_view.request()
            request = int(request)
            if request == 2:
                controller.player_view.response(locator.location_status(player.current_location))
            elif request == 1:
                player.current_location = locator.get_location_by_name('Комната пилота')
                controller.player_view.response('1. Усмирить главного хирурга\n2. Уйти')
                request = controller.player_view.request()
                while request.isdigit() == False:
                    controller.player_view.response('Введите номер ответа')
                    request = controller.player_view.request()
                request = int(request)
                if request == 2:
                    controller.player_view.response(locator.location_status(player.current_location))
                if request == 1:
                    locator.get_npcs().get_by_name('Nicholas Laurent').alive = False
                    player.found_disguises.append('Главный хирург')
                    controller.player_view.response(locator.location_status(player.current_location))
        
        if player.current_location.get_name() == 'Операционная' and player.disguise == 'Главный хирург' and events.get_by_name('Убийство в операционной').completed == False and locator.get_targets().get_by_name('Эрих Содерс').alive == True:
            controller.player_view.response('1. Управлять операционным роботом\n2. Не управлять')
            request = controller.player_view.request()
            while request.isdigit() == False:
                controller.player_view.response('Введите номер ответа')
                request = controller.player_view.request()
            request = int(request)
            if request == 1:
                controller.player_view.response('1. Убить Эриха Содерса\n2. Уйти')
                request = controller.player_view.request()
                while request.isdigit() == False:
                    controller.player_view.response('Введите номер ответа')
                    request = controller.player_view.request()
                request = int(request)
                if request == 1:
                    locator.get_targets().get_by_name('Эрих Содерс').alive = False
                    controller.player_view.response(f'{locator.get_challenges().get_by_name('(Не) врачебная ошибка').achieved()}')
                    controller.player_view.response(f'{locator.get_challenges().get_by_name('Так можно и пораниться').achieved()}')
                    result_string = 'Диана: Умно, 47-й. С Содерсом покончено.'
                    controller.player_view.response(result_string)
                    events.get_by_name('Убийство в операционной').completed = True
                if request == 2:
                    controller.player_view.response(locator.location_status(player.current_location))
            elif request == 2:
                controller.player_view.response(locator.location_status(player.current_location))
        
        if 'Охранник' in player.found_disguises or 'Телохранитель' in player.found_disguises:
            player.inventory.append(locator.get_items().get_by_name('Пистолет без глушителя'))
        
        if player.current_location.get_name() == 'Комната с серверами' and locator.get_targets().get_by_name('Эрих Содерс').alive == True:
            controller.player_view.response('1. Повредить серверы\n2. Не повреждать')
            request = controller.player_view.request()
            while request.isdigit() == False:
                controller.player_view.response('Введите номер ответа')
                request = controller.player_view.request()
            request = int(request)
            if request == 1:
                locator.get_targets().get_by_name('Эрих Содерс').alive = False
                controller.player_view.response(f'{locator.get_challenges().get_by_name('Призрак в машине').achieved()}')
                controller.player_view.response(f'{locator.get_challenges().get_by_name('Так можно и пораниться').achieved()}')
                result_string = 'Хирург: Что происходит с роботом?! Как его отключить?! Пациент сейчас умрет!\n\nДиана: Это было впечатляюще, агент. Эрих Содерс мертв.'
                controller.player_view.response(result_string)
            if request == 2:
                controller.player_view.response(locator.location_status(player.current_location))
        
        if player.current_location.get_name() == 'Комната охраны' and events.get_by_name('Информация об ИИ').completed == False:
            events.get_by_name('Информация об ИИ').completed = True
            controller.player_view.response('Интересно. Руководство для KAI, искусственного интеллекта клиники «Гама». Значит, местный искусственный интеллект по имени KAI не только поддерживает работу систем здания, но и управляет роботом в операционной. Именно там сейчас находится Содерс. В руководстве говорится, что после остановки сердца пациента искусственный интеллект автоматически начинает его реанимацию, что очень некстати. Однако... У директора клиники есть доступ к главному компьютеру. Справишься с управлением целой клиникой, 47-й?')

main(controller)