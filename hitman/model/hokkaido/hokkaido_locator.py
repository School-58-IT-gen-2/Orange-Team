import random
from model.common.location import Location
from model.hokkaido.hokkaido_items import HokkaidoItems
from model.hokkaido.hokkaido_npcs import HokkaidoNPCs, HokkaidoTargets
from model.hokkaido.hokkaido_disguises import HokkaidoDisguises
from model.hokkaido.hokkaido_challenges import HokkaidoChalLenges

class HokkaidoLocator():
    def __init__(self):
        self.__items = HokkaidoItems()
        self.__disguises = HokkaidoDisguises()
        self.__npcs = HokkaidoNPCs()
        self.__challenges = HokkaidoChalLenges()
        self.__targets = HokkaidoTargets()
        self.__locations = {
            'Номер 47-го':
                Location(
                name='Номер 47-го',
                connetcted_locations={
                    1: 'Канатная дорога',
                    2: 'Холл'
                },
                disguise=[
                    self.__disguises.get_by_name('VIP - пациент')
                ],
                witnesses=0,
                items=[
                    self.__items.get_by_name('Ножницы'),
                    self.__items.get_by_name('Бюст'),
                    self.__items.get_by_name('Пачка сигарет'),
                    self.__items.get_by_name('Монета')
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
                        self.__disguises.get_by_name('VIP - пациент'),
                        self.__disguises.get_by_name('Охранник'),
                        self.__disguises.get_by_name('Телохранитель'),
                        self.__disguises.get_by_name('Шеф'),
                        self.__disguises.get_by_name('Механик'),
                        self.__disguises.get_by_name('Хирург'),
                        self.__disguises.get_by_name('Инструктор по йоге'),
                        self.__disguises.get_by_name('Работник морга'),
                        self.__disguises.get_by_name('Работник "ГАМА"'),
                        self.__disguises.get_by_name('Директор клиники'),
                        self.__disguises.get_by_name('Главный хирург'),
                        self.__disguises.get_by_name('Пилот')
                    ],
                    witnesses=0,
                    items=[
                        self.__items.get_by_name('Жестяная банка')
                    ]
                ),
            'Холл':
                Location(
                    name='Холл',
                    connetcted_locations={
                        1: 'Мед-комплекс',
                        2: 'Комната охраны',
                        3: 'Зона спа',
                        4: 'Ресторан',
                        5: 'Внутренний сад',
                        6: 'Номер 47-го',
                        7: 'Канатная дорога',
                        8: 'Номер Юки Ямадзаки'
                    }, 
                    disguise=[
                        self.__disguises.get_by_name('VIP - пациент'),
                        self.__disguises.get_by_name('Охранник'),
                        self.__disguises.get_by_name('Телохранитель'),
                        self.__disguises.get_by_name('Шеф'),
                        self.__disguises.get_by_name('Механик'),
                        self.__disguises.get_by_name('Хирург'),
                        self.__disguises.get_by_name('Инструктор по йоге'),
                        self.__disguises.get_by_name('Работник морга'),
                        self.__disguises.get_by_name('Работник "ГАМА"'),
                        self.__disguises.get_by_name('Директор клиники'),
                        self.__disguises.get_by_name('Главный хирург'),
                        self.__disguises.get_by_name('Пилот')
                    ],
                    witnesses=2,
                    items=[
                        self.__items.get_by_name('Жестяная банка'),
                        self.__items.get_by_name('Жестяная банка'),
                    ]
                ),
            'Зона спа':
                Location(
                    name='Зона спа',
                    connetcted_locations={
                        1: 'Зона отдыха',
                        2: 'Холл'
                    }, 
                    disguise=[
                        self.__disguises.get_by_name('VIP - пациент'),
                        self.__disguises.get_by_name('Охранник'),
                        self.__disguises.get_by_name('Телохранитель'), 
                        self.__disguises.get_by_name('Шеф'),
                        self.__disguises.get_by_name('Механик'),
                        self.__disguises.get_by_name('Хирург'), 
                        self.__disguises.get_by_name('Инструктор по йоге'), 
                        self.__disguises.get_by_name('Работник морга'), 
                        self.__disguises.get_by_name('Работник "ГАМА"'), 
                        self.__disguises.get_by_name('Директор клиники'), 
                        self.__disguises.get_by_name('Главный хирург'),
                        self.__disguises.get_by_name('Пилот')
                    ], 
                    witnesses=8, 
                    items=[
                        self.__items.get_by_name('Ножницы')
                    ]
                ),
            'Ресторан':
                Location(
                    name='Ресторан',
                    connetcted_locations={
                        1: 'Коридор за барной стойкой',
                        2: 'Кухня',
                        3: 'Холл',
                        4: 'Внутренний сад'
                    }, 
                    disguise=[
                        self.__disguises.get_by_name('VIP - пациент'),
                        self.__disguises.get_by_name('Охранник'),
                        self.__disguises.get_by_name('Телохранитель'), 
                        self.__disguises.get_by_name('Шеф'),
                        self.__disguises.get_by_name('Механик'),
                        self.__disguises.get_by_name('Хирург'), 
                        self.__disguises.get_by_name('Инструктор по йоге'), 
                        self.__disguises.get_by_name('Работник морга'), 
                        self.__disguises.get_by_name('Работник "ГАМА"'), 
                        self.__disguises.get_by_name('Директор клиники'), 
                        self.__disguises.get_by_name('Главный хирург'),
                        self.__disguises.get_by_name('Пилот')
                    ], 
                    witnesses=5, 
                    items=[]
                ),
            'Внутренний сад':
                Location(
                    name='Внутренний сад',
                    connetcted_locations={
                        1: 'Холл',
                        2: 'Ресторан',
                        3: 'Мед-комплекс',
                        4: 'Коридор за барной стойкой'
                    }, 
                    disguise=[
                        self.__disguises.get_by_name('VIP - пациент'),
                        self.__disguises.get_by_name('Охранник'),
                        self.__disguises.get_by_name('Телохранитель'), 
                        self.__disguises.get_by_name('Шеф'),
                        self.__disguises.get_by_name('Механик'),
                        self.__disguises.get_by_name('Хирург'), 
                        self.__disguises.get_by_name('Инструктор по йоге'), 
                        self.__disguises.get_by_name('Работник морга'), 
                        self.__disguises.get_by_name('Работник "ГАМА"'), 
                        self.__disguises.get_by_name('Директор клиники'), 
                        self.__disguises.get_by_name('Главный хирург'),
                        self.__disguises.get_by_name('Пилот')
                    ], 
                    witnesses=0, 
                    items=[
                        self.__items.get_by_name('Молоток')
                    ]
                ),
            'Мед-комплекс':
                Location(
                    name='Мед-комплекс',
                    connetcted_locations={
                        1: 'Холл',
                        2: 'Внутренний сад',
                        3: 'Операционная',
                        4: 'Комната управления системой водоснабжения спа',
                        5: 'Морг',
                        6: 'Вертолетная площадка',
                        7: 'Мед-комплекс (2 этаж)',
                        8: 'Двор перед гаражом'
                    },
                    disguise=[
                        self.__disguises.get_by_name('Телохранитель'), 
                        self.__disguises.get_by_name('Хирург'), 
                        self.__disguises.get_by_name('Работник морга'), 
                        self.__disguises.get_by_name('Директор клиники'), 
                        self.__disguises.get_by_name('Главный хирург')
                    ], 
                    witnesses=0, 
                    items=[
                        self.__items.get_by_name('Скальпель')
                    ]
                ),
            'Комната охраны':
                Location(
                    name='Комната охраны',
                    connetcted_locations={
                        1: 'Холл'
                    }, 
                    disguise=[
                        self.__disguises.get_by_name('Охранник'),
                        self.__disguises.get_by_name('Телохранитель'), 
                        self.__disguises.get_by_name('Директор клиники')
                    ], 
                    witnesses=0, 
                    items=[
                        self.__items.get_by_name('Ключ-карта')
                    ]
                ),
            'Зона отдыха':
                Location(
                    name='Зона отдыха',
                    connetcted_locations={
                        1: 'Зона спа', 
                        2: 'Двор перед гаражом'
                    }, 
                    disguise=[
                        self.__disguises.get_by_name('VIP - пациент'),
                        self.__disguises.get_by_name('Охранник'),
                        self.__disguises.get_by_name('Телохранитель'), 
                        self.__disguises.get_by_name('Шеф'),
                        self.__disguises.get_by_name('Механик'),
                        self.__disguises.get_by_name('Хирург'), 
                        self.__disguises.get_by_name('Инструктор по йоге'), 
                        self.__disguises.get_by_name('Работник морга'), 
                        self.__disguises.get_by_name('Работник "ГАМА"'), 
                        self.__disguises.get_by_name('Директор клиники'), 
                        self.__disguises.get_by_name('Главный хирург'),
                        self.__disguises.get_by_name('Пилот')
                    ], 
                    witnesses=7, 
                    items=[
                        self.__items.get_by_name('Монета'),
                        self.__items.get_by_name('Монета')
                    ]
                ),
            'Гараж':
                Location(
                    name='Гараж',
                    connetcted_locations={
                        1: 'Морг',
                        2: 'Двор перед гаражом',
                        3: 'Спальня персонала'
                    }, 
                    disguise=[
                        self.__disguises.get_by_name('Охранник'),
                        self.__disguises.get_by_name('Телохранитель'), 
                        self.__disguises.get_by_name('Механик'),
                        self.__disguises.get_by_name('Хирург'), 
                        self.__disguises.get_by_name('Инструктор по йоге'), 
                        self.__disguises.get_by_name('Работник морга'), 
                        self.__disguises.get_by_name('Работник "ГАМА"'), 
                        self.__disguises.get_by_name('Директор клиники'), 
                        self.__disguises.get_by_name('Главный хирург'),
                        self.__disguises.get_by_name('Пилот')
                    ], 
                    witnesses=0, 
                    items=[
                        self.__items.get_by_name('Молоток'),
                        self.__items.get_by_name('Гаечный ключ'),
                        self.__items.get_by_name('Крысиный яд'),
                    ]
                ),
            'Коридор за барной стойкой':
                Location(
                    name='Коридор за барной стойкой',
                    connetcted_locations={
                        1: 'Ресторан',
                        2: 'Морг',
                        3: 'Спальня персонала',
                        4: 'Внутренний сад',
                        5: 'Комната пилота'
                    }, 
                    disguise=[
                        self.__disguises.get_by_name('Охранник'),
                        self.__disguises.get_by_name('Телохранитель'), 
                        self.__disguises.get_by_name('Шеф'),
                        self.__disguises.get_by_name('Хирург'), 
                        self.__disguises.get_by_name('Инструктор по йоге'), 
                        self.__disguises.get_by_name('Работник морга'), 
                        self.__disguises.get_by_name('Работник "ГАМА"'), 
                        self.__disguises.get_by_name('Директор клиники'), 
                        self.__disguises.get_by_name('Главный хирург'),
                        self.__disguises.get_by_name('Пилот')
                    ], 
                    witnesses=0, 
                    items=[
                        self.__items.get_by_name('Крысиный яд'),
                    ]
                ),
            'Кухня':
                Location(
                    name='Зона отдыха',
                    connetcted_locations={
                        1: 'Ресторан', 
                        2: 'Спальня персонала'
                    }, 
                    disguise=[
                        self.__disguises.get_by_name('Охранник'),
                        self.__disguises.get_by_name('Телохранитель'), 
                        self.__disguises.get_by_name('Шеф'),
                        self.__disguises.get_by_name('Работник "ГАМА"'), 
                        self.__disguises.get_by_name('Директор клиники'), 
                    ], 
                    witnesses=0, 
                    items=[
                        self.__items.get_by_name('Крысиный яд'),
                        self.__items.get_by_name('Яд рыбы Фугу')
                    ]
                ),
            'Спальня персонала':
                Location(
                    name='Спальня персонала',
                    connetcted_locations={
                        1: 'Кухня',
                        2: 'Гараж',
                        3: 'Коридор за барной стойкой',
                        4: 'Морг'
                    }, 
                    disguise=[
                        self.__disguises.get_by_name('Охранник'),
                        self.__disguises.get_by_name('Телохранитель'), 
                        self.__disguises.get_by_name('Шеф'),
                        self.__disguises.get_by_name('Механик'),
                        self.__disguises.get_by_name('Хирург'), 
                        self.__disguises.get_by_name('Инструктор по йоге'), 
                        self.__disguises.get_by_name('Работник морга'), 
                        self.__disguises.get_by_name('Работник "ГАМА"'), 
                        self.__disguises.get_by_name('Директор клиники'), 
                        self.__disguises.get_by_name('Главный хирург')
                    ], 
                    witnesses=0, 
                    items=[
                        self.__items.get_by_name('Пульт для управления нейрочипом'),
                        self.__items.get_by_name('Монета')
                    ]
                ),
            'Операционная':
                Location(
                    name='Операционная',
                    connetcted_locations={
                        1: 'Мед-комплекс'
                    }, 
                    disguise=[
                        self.__disguises.get_by_name('Хирург'),  
                        self.__disguises.get_by_name('Директор клиники'), 
                        self.__disguises.get_by_name('Главный хирург')
                    ], 
                    witnesses=0, 
                    items=[
                        self.__items.get_by_name('Скальпель')
                    ]
                ),
            'Номер Юки Ямадзаки':
                Location(
                    name='Номер Юки Ямадзаки',
                    connetcted_locations={
                        1: 'Холл'
                    }, 
                    disguise=[
                        self.__disguises.get_by_name('Телохранитель'),  
                    ], 
                    witnesses=0, 
                    items=[
                        self.__items.get_by_name('Бюст'),
                        self.__items.get_by_name('Жестяная банка')
                    ]
                ),
            'Комната управления системой водоснабжения спа':
                Location(
                    name='Комната управления системой водоснабжения спа',
                    connetcted_locations={
                        1: 'Мед-комплекс', 
                        2: 'Двор перед гаражом'
                    }, 
                    disguise=[
                        self.__disguises.get_by_name('Директор клиники'), 
                        self.__disguises.get_by_name('Телохранитель')
                    ], 
                    witnesses=0, 
                    items=[]
                ),
            'Вертолетная площадка':
                Location(
                    name='Вертолетная площадка',
                    connetcted_locations={
                        1: 'Комната пилота',
                        2: 'Мед-комплекс',
                        3: 'Мед-комплекс (2 этаж)',
                        4: 'Двор перед гаражом'
                    }, 
                    disguise=[
                        self.__disguises.get_by_name('Охранник'),
                        self.__disguises.get_by_name('Телохранитель'), 
                        self.__disguises.get_by_name('Хирург'), 
                        self.__disguises.get_by_name('Работник морга'),  
                        self.__disguises.get_by_name('Директор клиники'), 
                        self.__disguises.get_by_name('Главный хирург'),
                        self.__disguises.get_by_name('Пилот')
                    ], 
                    witnesses=0, 
                    items=[
                        self.__items.get_by_name('Крысиный яд')
                    ]
                ),
            'Комната пилота':
                Location(
                    name='Комната пилота',
                    connetcted_locations={
                        1: 'Коридор за барной стойкой', 
                        2: 'Вертолетная площадка'
                    }, 
                    disguise=[
                        self.__disguises.get_by_name('Охранник'),
                        self.__disguises.get_by_name('Телохранитель'), 
                        self.__disguises.get_by_name('Хирург'), 
                        self.__disguises.get_by_name('Работник морга'),  
                        self.__disguises.get_by_name('Директор клиники'), 
                        self.__disguises.get_by_name('Главный хирург'),
                        self.__disguises.get_by_name('Пилот')
                    ], 
                    witnesses=0, 
                    items=[
                        self.__items.get_by_name('Гаечный ключ')
                    ]
                ),
            'Мед-комплекс (2 этаж)':
                Location(
                    name='Мед-комплекс (2 этаж)',
                    connetcted_locations={
                        1: 'Мед-комплекс',
                        2: 'Комната директора клиники',
                        3: 'Комната с серверами',
                        4: 'Вертолетная площадка'
                    },
                    disguise=[
                        self.__disguises.get_by_name('Телохранитель'), 
                        self.__disguises.get_by_name('Хирург'), 
                        self.__disguises.get_by_name('Работник морга'), 
                        self.__disguises.get_by_name('Директор клиники'), 
                        self.__disguises.get_by_name('Главный хирург')
                    ], 
                    witnesses=0, 
                    items=[]
                ),
            'Комната директора клиники':
                Location(
                    name='Комната директора клиники',
                    connetcted_locations={
                        1: 'Мед-комплекс (2 этаж)'
                    },
                    disguise=[
                        self.__disguises.get_by_name('Директор клиники'), 
                    ], 
                    witnesses=0, 
                    items=[]
                ),
            'Комната с серверами':
                Location(
                    name='Комната с серверами',
                    connetcted_locations={
                        1: 'Мед-комплекс (2 этаж)'
                    },
                    disguise=[
                        self.__disguises.get_by_name('Директор клиники'), 
                    ], 
                    witnesses=0, 
                    items=[]
                ),
            'Двор перед гаражом':
                Location(
                    name='Двор перед гаражом',
                    connetcted_locations={
                        1: 'Гараж', 
                        2: 'Зона отдыха', 
                        3: 'Горная тропа', 
                        4: 'Вертолетная площадка', 
                        5: 'Мед-комплекс', 
                        6: 'Комната управления системой водоснабжения спа'
                    }, 
                    disguise=[
                        self.__disguises.get_by_name('Охранник'),
                        self.__disguises.get_by_name('Телохранитель'), 
                        self.__disguises.get_by_name('Механик'),
                        self.__disguises.get_by_name('Хирург'), 
                        self.__disguises.get_by_name('Инструктор по йоге'), 
                        self.__disguises.get_by_name('Работник морга'), 
                        self.__disguises.get_by_name('Работник "ГАМА"'), 
                        self.__disguises.get_by_name('Директор клиники'), 
                        self.__disguises.get_by_name('Главный хирург'),
                        self.__disguises.get_by_name('Пилот')
                    ], 
                    witnesses=0, 
                    items=[]
                ),
            'Горная тропа':
                Location(
                    name='Горная тропа',
                    connetcted_locations={
                        1: 'Двор перед гаражом'
                    }, 
                    disguise=[
                        self.__disguises.get_by_name('Охранник'),
                        self.__disguises.get_by_name('Телохранитель'), 
                        self.__disguises.get_by_name('Механик'),
                        self.__disguises.get_by_name('Хирург'), 
                        self.__disguises.get_by_name('Инструктор по йоге'), 
                        self.__disguises.get_by_name('Работник морга'), 
                        self.__disguises.get_by_name('Работник "ГАМА"'), 
                        self.__disguises.get_by_name('Директор клиники'), 
                        self.__disguises.get_by_name('Главный хирург'),
                        self.__disguises.get_by_name('Пилот')
                    ], 
                    witnesses=0, 
                    items=[]
                ),
            'Морг':
                Location(
                    name='Морг',
                    connetcted_locations={
                    1: 'Коридор за барной стойкой',
                    2: 'Мед-комплекс',
                    3: 'Спальня персонала',
                    4: 'Гараж',
                    },
                    disguise=[
                        self.__disguises.get_by_name('Телохранитель'), 
                        self.__disguises.get_by_name('Хирург'), 
                        self.__disguises.get_by_name('Работник морга'), 
                        self.__disguises.get_by_name('Директор клиники'), 
                        self.__disguises.get_by_name('Главный хирург')
                    ], 
                    witnesses=0, 
                    items=[
                        self.__items.get_by_name('Скальпель'),
                    ]
                )
        }
                
    def find_location_npcs(self, location_name):
        location_npcs = []
        for i in self.__npcs.get_all():
            if i.move() == location_name and i.alive == True:
                location_npcs.append(i)
        return location_npcs

    def location_witnesses(self, location_name):
        location_npcs = self.find_location_npcs(location_name)
        location_witnesses = self.get_location_by_name(location_name).get_witnesses()
        for i in location_npcs:
            if random.randrange(11) <= i.witness_chance and i.alive == True:
                location_witnesses += 1
        return location_witnesses

    def location_status(self, location):
        result_string = f'{location.get_name()}\n'
        location_npcs = self.find_location_npcs(location.get_name())
        location_disguises = []
        for i in location_npcs:
            location_disguises.append(i.get_disguise())
        if self.location_witnesses(location.get_name()) != 0:
            result_string += '\nНа локации находятся:\n'
            if location.get_witnesses() > 0:
                result_string += f'\n{location.get_witnesses()} Пациент'
            for i in self.__disguises.get_all():
                if i.get_name() in location_disguises:
                    result_string += f'\n{location_disguises.count(i.get_name())} {i.get_name()}'
            return result_string
        else:
            result_string += '\nНа локации нет свидетелей'
            return result_string

    def get_location_by_name(self, location_name):
        return self.__locations[location_name]

    def get_npcs(self):
        return self.__npcs

    def get_challenges(self):
        return self.__challenges

    def get_locations(self):
        return self.__locations
    
    def get_disguise_by_name(self, disuise):
        return self.__disguises.get_by_name(disuise)
    
    def get_items(self):
        return self.__items
    
    def get_targets(self):
        return self.__targets