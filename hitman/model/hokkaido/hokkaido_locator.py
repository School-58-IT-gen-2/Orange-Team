import random
from hitman.model.common.location import Location
from hitman.model.hokkaido.hokkaido_items import HokkaidoItems
from hitman.model.hokkaido.hokkaido_npcs import HokkaidoNPCs
from hitman.model.hokkaido.hokkaido_disguises import HokkaidoDisguises
from hitman.model.hokkaido.hokkaido_challenges import HokkaidoChalLenges

class HokkaidoLocator():
    def __init__(self):
        items = HokkaidoItems()
        disguises = HokkaidoDisguises()

        self.__npcs = HokkaidoNPCs()
        self.__challenges = HokkaidoChalLenges()
        self.__init_location = 'Номер 47-го'
        self.__locations = {
            'Номер 47-го':
                Location(
                name='Номер 47-го',
                connetcted_locations={
                    1: 'Канатная дорога',
                    2: 'Холл'
                },
                disguise=[
                    disguises.get_by_name('VIP - пациент')
                ],
                witnesses=0,
                items=[
                    items.get_by_name('Ножницы'),
                    items.get_by_name('Бюст'),
                    items.get_by_name('Пачка сигарет'),
                    items.get_by_name('Монета')
                ]
            ),
            'Канатная дорога':
                Location(
                    name='Канатная дорога',
                    connetcted_locations={
                        1: 'Номер 47-го',
                        2: 'Холл'
                    },
                    disguise=[
                        disguises.get_by_name('VIP - пациент'),
                        disguises.get_by_name('Охранник'),
                        disguises.get_by_name('Телохранитель'),
                        disguises.get_by_name('Шеф'),
                        disguises.get_by_name('Механик'),
                        disguises.get_by_name('Хирург'),
                        disguises.get_by_name('Инструктор по йоге'),
                        disguises.get_by_name('Работник морга'),
                        disguises.get_by_name('Работник "ГАМА"'),
                        disguises.get_by_name('Директор клиники'),
                        disguises.get_by_name('Главный хирург')
                    ],
                    witnesses=0,
                    items=[items.get_by_name('Жестяная банка')]
                ),
            # 'Холл': hall,
            # 'Зона спа': spa,
            # 'Ресторан': restaurant,
            # 'Внутренний сад': garden,
            # 'Мед-комплекс': medical_center,
            # 'Комната охраны': security_room,
            # 'Зона отдыха': resort,
            # 'Гараж': garage,
            # 'Коридор за барной стойкой': bar,
            # 'Кухня': kitchen,
            # 'Спальня персонала': chip_room,
            # 'Морг': morgue,
            # 'Операционная': operation_room,
            # 'Номер Юки Ямадзаки': target_suite,
            # 'Комната управления системой водоснабжения спа': water_control_room,
            # 'Вертолетная площадка': helipad,
            # 'Комната пилота': pilot_room,
            # 'Мед-комплекс (2 этаж)': medical_center_level_2,
            # 'Комната директора клиники': director_room,
            # 'Комната с серверами': server_room,
            # 'Двор перед гаражом': garage_entrence,
            # 'Горная тропа': mountain_path
        }
    def get_location_by_name(self, location_name):
        return self.__locations[location_name]

    def get_npcs(self):
        return self.__npcs

    def get_challenges(self):
        return self.__challenges

    def get_init_location(self):
        return self.__init_location

    def find_location_npcs(self, location):
        location_npcs = []
        for i in self.__npcs.get_all():
            if i.move() == location and i.alive == True:
                location_npcs.append(i)
        return location_npcs

    def location_witnesses(self, location):
        location_npcs = self.find_location_npcs(location)
        location_witnesses = location.get_witnesses()
        for i in location_npcs:
            if random.randrange(11) <= i.witness_chance and i.alive == True:
                location_witnesses += 1
        return location_witnesses

    def location_status(self, location):
        result_string = f'{location.get_name()}\n'
        location_npcs = self.find_location_npcs(location)
        location_disguises = []
        for i in location_npcs:
            if i.alive == True:
                location_disguises.append(i.get_disguise())
        if location_npcs != []:
            witnesses = location.get_witnesses()
            disguises = location.get_disguise()
            if witnesses > 0:
                result_string += f'\nНа локации находятся:\n\n{witnesses} Пациент'
            for i in range(1, len(disguises)+1):
                if disguises[i] in location_disguises:
                    result_string += f'\n{location_disguises.count(disguises[i]), disguises[i]}'
            result_string += f'\n\nВсего {self.location_witnesses(location)} свидетелей'
            return result_string
        else:
            result_string += '\nНа локации нет свидетелей'
            return result_string

# suite = Location('Номер 47-го', {
#     1: 'Канатная дорога',
#     2: 'Холл'
# }, ['VIP - пациент'], 0, [scissors, bust, cigars, coin])
#
# cable_car = Location('Канатная дорога', {1: 'Номер 47-го', 2: 'Холл'}, ['VIP - пациент', 'Охранник', 'Телохранитель', 'Шеф', 'Механик', 'Хирург', 'Инструктор по йоге', 'Работник морга', 'Работник "ГАМА"', 'Директор клиники', 'Главный хирург'], 0, [can])
#
# hall = Location('Холл', {
#     1: 'Мед-комплекс',
#     2: 'Комната охраны',
#     3: 'Зона спа',
#     4: 'Ресторан',
#     5: 'Внутренний сад',
#     6: 'Номер 47-го',
#     7: 'Канатная дорога',
#     8: 'Номер Юки Ямадзаки'
#     }, ['VIP - пациент', 'Охранник', 'Телохранитель', 'Шеф', 'Механик', 'Хирург', 'Инструктор по йоге', 'Работник морга', 'Работник "ГАМА"', 'Директор клиники', 'Главный хирург'], 2, [can, can])
#
# spa = Location('Зона спа', {
#     1: 'Зона отдыха',
#     2: 'Холл'
# }, ['VIP - пациент', 'Охранник', 'Телохранитель', 'Шеф', 'Механик', 'Хирург', 'Инструктор по йоге', 'Работник морга', 'Работник "ГАМА"', 'Директор клиники', 'Главный хирург'], 8, [scissors])
#
# restaurant = Location('Ресторан', {
#     1: 'Барная стойка',
#     2: 'Кухня',
#     3: 'Холл',
#     4: 'Внутренний сад'
# }, ['VIP - пациент', 'Охранник', 'Телохранитель', 'Шеф', 'Механик', 'Хирург', 'Инструктор по йоге', 'Работник морга', 'Работник "ГАМА"', 'Директор клиники', 'Главный хирург'], 5, [])
#
# garden = Location('Внутренний сад', {
#     1: 'Холл',
#     2: 'Ресторан',
#     3: 'Мед-комплекс',
#     4: 'Барная стойка'
# }, ['VIP - пациент', 'Охранник', 'Телохранитель', 'Шеф', 'Механик', 'Хирург', 'Инструктор по йоге', 'Работник морга', 'Работник "ГАМА"', 'Директор клиники', 'Главный хирург'], 0, [hammer])
#
# medical_center = Location('Мед-комплекс', {
#     1: 'Холл',
#     2: 'Внутренний сад',
#     3: 'Операционная',
#     4: 'Комната управления системой водоснабжения спа',
#     5: 'Морг',
#     6: 'Вертолетная площадка',
#     7: 'Мед-комплекс (2 этаж)',
#     8: 'Двор перед гаражом'
# }, ['Телохранитель', 'Хирург', 'Работник морга', 'Директор клиники', 'Главный хирург'], 0, [scalpel])
#
# security_room = Location('Комната охраны', {1: 'Холл'}, ['Охранник', 'Телохранитель', 'Директор клиники'], 0, [keycard])
#
# resort = Location('Зона отдыха', {1: 'Зона спа', 2: 'Двор перед гаражом'}, ['VIP - пациент', 'Охранник', 'Телохранитель', 'Шеф', 'Механик', 'Хирург', 'Инструктор по йоге', 'Работник морга', 'Работник "ГАМА"', 'Директор клиники', 'Главный хирург'], 7, [can, coin])
#
# garage = Location('Гараж', {
#     1: 'Морг',
#     2: 'Двор перед гаражом',
#     3: 'Спальня персонала'
# }, ['Охранник', 'Телохранитель', 'Механик', 'Хирург', 'Инструктор по йоге', 'Работник морга', 'Работник "ГАМА"', 'Директор клиники', 'Главный хирург'], 0, [hammer, wrench, rat_poison])
#
# bar = Location('Коридор за барной стойкой', {
#     1: 'Ресторан',
#     2: 'Морг',
#     3: 'Спальня персонала',
#     4: 'Мед-комплекс',
#     5: 'Внутренний сад',
#     6: 'Комната пилота'
# }, ['Охранник', 'Телохранитель', 'Шеф', 'Директор клиники', 'Главный хирург'], 0, [rat_poison])
#
# kitchen = Location('Кухня', {1: 'Ресторан', 2: 'Спальня персонала'}, ['Охранник', 'Телохранитель', 'Шеф', 'Работник "ГАМА"', 'Директор клиники'], 0, [rat_poison, fugu_poison])
#
# chip_room = Location('Спальня персонала', {
#     1: 'Кухня',
#     2: 'Гараж',
#     3: 'Барная стойка',
#     4: 'Морг'
# }, ['Охранник', 'Телохранитель', 'Шеф', 'Механик', 'Хирург', 'Инструктор по йоге', 'Работник морга', 'Работник "ГАМА"', 'Директор клиники', 'Главный хирург'], 0, [chip_control, coin])
#
# morgue = Location('Морг', {
#     1: 'Барная стойка',
#     2: 'Мед-комплекс',
#     3: 'Спальня персонала',
#     4: 'Гараж',
#     5: 'Операционная'
# }, ['Телохранитель', 'Хирург', 'Работник морга', 'Директор клиники', 'Главный хирург'], 0, [scalpel])
#
# operation_room = Location('Операционная', {1: 'Мед-комплекс'}, ['Хирург', 'Директор клиники', 'Главный хирург'], 0, [scalpel, coin])
#
# target_suite = Location('Номер Юки Ямадзаки', {1: 'Холл'}, ['Телохранитель'], 0, [bust, can])
#
# water_control_room = Location('Комната управления системой водоснабжения спа', {1: 'Мед-комплекс', 2: 'Двор перед гаражом'}, ['Телохранитель', 'Директор клиники'], 0, [])
#
# helipad = Location('Вертолетная площадка', {
#     1: 'Комната пилота',
#     2: 'Мед-комплекс',
#     3: 'Мед-комплекс (2 этаж)',
#     4: 'Двор перед гаражом'
# }, ['Охранник', 'Телохранитель', 'Директор клиники', 'Хирург', 'Главный хирург', 'Пилот'], 0, [])
#
# pilot_room = Location('Комната пилота', {1: 'Барная стойка', 2: 'Вертолетная площадка'}, ['Директор клиники', 'Телохранитель', 'Пилот', 'Охранник', 'Главный хирург', 'Хирург'], 0, [wrench])
#
# medical_center_level_2 = Location('Мед-комплекс (2 этаж)', {
#     1: 'Мед-комплекс',
#     2: 'Комната директора клиники',
#     3: 'Комната с серверами',
#     4: 'Вертолетная площадка'
# }, ['Телохранитель', 'Хирург', 'Работник морга', 'Директор клиники', 'Главный хирург'], 0, [])
#
# director_room = Location('Комната директора клиники', {1: 'Мед-комплекс (2 этаж)'}, ['Директор клиники'], 0, [])
#
# server_room = Location('Комната с серверами', {1: 'Мед-комплекс (2 этаж)'}, ['Директор клиники'], 0, [])
#
# garage_entrence = Location('Двор перед гаражом', {1: 'Гараж', 2: 'Зона отдыха', 3: 'Горная тропа', 4: 'Вертолетная площадка', 5: 'Мед-комплекс', 6: 'Комната управления системой водоснабжения спа'}, ['Охранник', 'Телохранитель', 'Механик', 'Хирург', 'Инструктор по йоге', 'Работник морга', 'Работник "ГАМА"', 'Директор клиники', 'Главный хирург'], 0, [])
#
# mountain_path = Location('Горная тропа', {1: 'Двор перед гаражом'}, ['Охранник', 'Телохранитель', 'Механик', 'Хирург', 'Инструктор по йоге', 'Работник морга', 'Работник "ГАМА"', 'Директор клиники', 'Главный хирург'], 0, [])
#
# hokkaido_locations = [suite, cable_car, hall, spa, restaurant, garden, medical_center, security_room, resort, garage, bar, kitchen, chip_room, morgue, operation_room, target_suite, water_control_room, helipad, pilot_room, medical_center_level_2, director_room, server_room, garage_entrence, mountain_path]

