from model.locations import Location
from hokkaido.hokkaido_loot import *


suite = Location('Номер 47-го', {
    1: 'Канатная дорога', 
    2: 'Холл'
}, ['VIP - пациент'], 0, [scissors, bust, cigars, coin])

cable_car = Location('Канатная дорога', {1: 'Номер 47-го', 2: 'Холл'}, ['VIP - пациент', 'Охранник', 'Телохранитель', 'Шеф', 'Механик', 'Хирург', 'Инструктор по йоге', 'Работник морга', 'Работник "ГАМА"', 'Директор клиники', 'Главный хирург'], 0, [can])

hall = Location('Холл', {
    1: 'Мед-комплекс',
    2: 'Комната охраны',
    3: 'Зона спа',
    4: 'Ресторан',
    5: 'Внутренний сад',
    6: 'Номер 47-го',
    7: 'Канатная дорога',
    8: 'Номер Юки Ямадзаки'
    }, ['VIP - пациент', 'Охранник', 'Телохранитель', 'Шеф', 'Механик', 'Хирург', 'Инструктор по йоге', 'Работник морга', 'Работник "ГАМА"', 'Директор клиники', 'Главный хирург'], 2, [can, can])

spa = Location('Зона спа', {
    1: 'Зона отдыха',
    2: 'Холл'
}, ['VIP - пациент', 'Охранник', 'Телохранитель', 'Шеф', 'Механик', 'Хирург', 'Инструктор по йоге', 'Работник морга', 'Работник "ГАМА"', 'Директор клиники', 'Главный хирург'], 8, [scissors])

restaurant = Location('Ресторан', {
    1: 'Барная стойка',
    2: 'Кухня',
    3: 'Холл',
    4: 'Внутренний сад'
}, ['VIP - пациент', 'Охранник', 'Телохранитель', 'Шеф', 'Механик', 'Хирург', 'Инструктор по йоге', 'Работник морга', 'Работник "ГАМА"', 'Директор клиники', 'Главный хирург'], 5, [])

garden = Location('Внутренний сад', {
    1: 'Холл',
    2: 'Ресторан',
    3: 'Мед-комплекс',
    4: 'Барная стойка'
}, ['VIP - пациент', 'Охранник', 'Телохранитель', 'Шеф', 'Механик', 'Хирург', 'Инструктор по йоге', 'Работник морга', 'Работник "ГАМА"', 'Директор клиники', 'Главный хирург'], 0, [hammer])

medical_center = Location('Мед-комплекс', {
    1: 'Холл',
    2: 'Внутренний сад',
    3: 'Операционная',
    4: 'Комната управления системой водоснабжения спа',
    5: 'Морг',
    6: 'Вертолетная площадка',
    7: 'Мед-комплекс (2 этаж)',
    8: 'Двор перед гаражом'
}, ['Телохранитель', 'Хирург', 'Работник морга', 'Директор клиники', 'Главный хирург'], 0, [scalpel])

security_room = Location('Комната охраны', {1: 'Холл'}, ['Охранник', 'Телохранитель', 'Директор клиники'], 0, [keycard])

resort = Location('Зона отдыха', {1: 'Зона спа', 2: 'Двор перед гаражом'}, ['VIP - пациент', 'Охранник', 'Телохранитель', 'Шеф', 'Механик', 'Хирург', 'Инструктор по йоге', 'Работник морга', 'Работник "ГАМА"', 'Директор клиники', 'Главный хирург'], 7, [can, coin])

garage = Location('Гараж', {
    1: 'Морг',
    2: 'Двор перед гаражом',
    3: 'Спальня персонала'
}, ['Охранник', 'Телохранитель', 'Механик', 'Хирург', 'Инструктор по йоге', 'Работник морга', 'Работник "ГАМА"', 'Директор клиники', 'Главный хирург'], 0, [hammer, wrench, rat_poison])

bar = Location('Коридор за барной стойкой', {
    1: 'Ресторан',
    2: 'Морг',
    3: 'Спальня персонала',
    4: 'Мед-комплекс',
    5: 'Внутренний сад',
    6: 'Комната пилота'
}, ['Охранник', 'Телохранитель', 'Шеф', 'Директор клиники', 'Главный хирург'], 0, [rat_poison])

kitchen = Location('Кухня', {1: 'Ресторан', 2: 'Спальня персонала'}, ['Охранник', 'Телохранитель', 'Шеф', 'Работник "ГАМА"', 'Директор клиники'], 0, [rat_poison, fugu_poison])

chip_room = Location('Спальня персонала', {
    1: 'Кухня',
    2: 'Гараж',
    3: 'Барная стойка',
    4: 'Морг'
}, ['Охранник', 'Телохранитель', 'Шеф', 'Механик', 'Хирург', 'Инструктор по йоге', 'Работник морга', 'Работник "ГАМА"', 'Директор клиники', 'Главный хирург'], 0, [chip_control, coin])

morgue = Location('Морг', {
    1: 'Барная стойка',
    2: 'Мед-комплекс',
    3: 'Спальня персонала',
    4: 'Гараж',
    5: 'Операционная'
}, ['Телохранитель', 'Хирург', 'Работник морга', 'Директор клиники', 'Главный хирург'], 0, [scalpel])

operation_room = Location('Операционная', {1: 'Мед-комплекс'}, ['Хирург', 'Директор клиники', 'Главный хирург'], 0, [scalpel, coin])

target_suite = Location('Номер Юки Ямадзаки', {1: 'Холл'}, ['Телохранитель'], 0, [bust, can])

water_control_room = Location('Комната управления системой водоснабжения спа', {1: 'Мед-комплекс', 2: 'Двор перед гаражом'}, ['Телохранитель', 'Директор клиники'], 0, [])

helipad = Location('Вертолетная площадка', {
    1: 'Комната пилота',
    2: 'Мед-комплекс',
    3: 'Мед-комплекс (2 этаж)',
    4: 'Двор перед гаражом'
}, ['Охранник', 'Телохранитель', 'Директор клиники', 'Хирург', 'Главный хирург', 'Пилот'], 0, [])

pilot_room = Location('Комната пилота', {1: 'Барная стойка', 2: 'Вертолетная площадка'}, ['Директор клиники', 'Телохранитель', 'Пилот', 'Охранник', 'Главный хирург', 'Хирург'], 0, [wrench])

medical_center_level_2 = Location('Мед-комплекс (2 этаж)', {
    1: 'Мед-комплекс',
    2: 'Комната директора клиники',
    3: 'Комната с серверами',
    4: 'Вертолетная площадка'
}, ['Телохранитель', 'Хирург', 'Работник морга', 'Директор клиники', 'Главный хирург'], 0, [])

director_room = Location('Комната директора клиники', {1: 'Мед-комплекс (2 этаж)'}, ['Директор клиники'], 0, [])

server_room = Location('Комната с серверами', {1: 'Мед-комплекс (2 этаж)'}, ['Директор клиники'], 0, [])

garage_entrence = Location('Двор перед гаражом', {1: 'Гараж', 2: 'Зона отдыха', 3: 'Горная тропа', 4: 'Вертолетная площадка', 5: 'Мед-комплекс', 6: 'Комната управления системой водоснабжения спа'}, ['Охранник', 'Телохранитель', 'Механик', 'Хирург', 'Инструктор по йоге', 'Работник морга', 'Работник "ГАМА"', 'Директор клиники', 'Главный хирург'], 0, [])

mountain_path = Location('Горная тропа', {1: 'Двор перед гаражом'}, ['Охранник', 'Телохранитель', 'Механик', 'Хирург', 'Инструктор по йоге', 'Работник морга', 'Работник "ГАМА"', 'Директор клиники', 'Главный хирург'], 0, [])

hokkaido_locations = [suite, cable_car, hall, spa, restaurant, garden, medical_center, security_room, resort, garage, bar, kitchen, chip_room, morgue, operation_room, target_suite, water_control_room, helipad, pilot_room, medical_center_level_2, director_room, server_room, garage_entrence, mountain_path]

def hokkaido_location_by_name(location_name):
    locations_names = {
        'Номер 47-го': suite,
        'Канатная дорога': cable_car,
        'Холл': hall,
        'Зона спа': spa,
        'Ресторан': restaurant,
        'Внутренний сад': garden,
        'Мед-комплекс': medical_center,
        'Комната охраны': security_room,
        'Зона отдыха': resort,
        'Гараж': garage,
        'Коридор за барной стойкой': bar,
        'Кухня': kitchen,
        'Спальня персонала': chip_room,
        'Морг': morgue,
        'Операционная': operation_room,
        'Номер Юки Ямадзаки': target_suite,
        'Комната управления системой водоснабжения спа': water_control_room,
        'Вертолетная площадка': helipad,
        'Комната пилота': pilot_room,
        'Мед-комплекс (2 этаж)': medical_center_level_2,
        'Комната директора клиники': director_room,
        'Комната с серверами': server_room,
        'Двор перед гаражом': garage_entrence,
        'Горная тропа': mountain_path
    }
    return locations_names[location_name]