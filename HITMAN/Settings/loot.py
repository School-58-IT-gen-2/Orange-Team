class Item:
    def __init__(self, name, usage, illegal, deadly):
        self.name = name
        self.usage = usage
        self.illegal = illegal
        self.deadly = deadly

pistol = Item('Пистолет без глушителя', ['Выстрелить', 'Отменить действие'], True, True)
kitchen_knife = Item('Кухонный нож', ['Бросить (летально)', 'Ударить (летально)', 'Отменить действие'], False, True)
scissors = Item('Ножницы', ['Бросить (летально)', 'Ударить (летально)', 'Отменить действие'], False, True)
rat_poison = Item('Крысиный яд', [], False, False)
fugu_poison = Item('Яд рыбы Фугу', [], False, True)
hammer = Item('Молоток', ['Бросить', 'Ударить', 'Отменить действие'], False, False)
wrench = Item('Гаечный ключ', ['Бросить', 'Ударить', 'Отменить действие'], False, False)
chip_control = Item('Пульт для управления нейрочипом', ['Использовать', 'Отменить действие'], False, False)
cigars = Item('Пачка сигарет', [], False, False)
bust = Item('Бюст', ['Бросить', 'Ударить', 'Отменить действие'], False, False)
can = Item('Жестяная банка', ['Бросить для отвлечения', 'Отменить действие'], False, False)
scalpel = Item('Скальпель', ['Бросить (летально)', 'Ударить (летально)', 'Отменить действие'], False, True)
coin = Item('Монета', ['Бросить для отвлечения', 'Отменить действие'], False, False)
arms = Item('Нет предмета', ['Усмирить', 'Отменить действие'], False, False)
keycard = Item('Ключ-карта', [], False, False)
silenced_pistol = Item('Пистолет с глушителем', ['Выстрелить', 'Отменить действие'], True, True)
fiber_wire = Item('Удавка', ['Задушить', 'Отменить действие'], False, True)
deadly_poison = Item('Смертельный яд', [], False, True)
emetic_poison = Item('Рвотный яд', [], False, False)
disposable_scrambler = Item('Электронный дешифровщик', [], False, False)
combat_knife = Item('Боевой нож', ['Бросить (летально)', 'Ударить (летально)', 'Отменить действие'], False, True)

disguises = {
    1: 'VIP - пациент',
    2: 'Охранник',
    3: 'Телохранитель',
    4: 'Шеф',
    5: 'Механик',
    6: 'Хирург',
    7: 'Инструктор по йоге',
    8: 'Работник морга',
    9: 'Работник "ГАМА"',
    10: 'Директор клиники',
    11: 'Пилот',
    12: 'Главный хирург',
    13: 'Ниндзя'
}

objects = [
    pistol,
    kitchen_knife,
    scissors,
    rat_poison,
    fugu_poison,
    hammer,
    wrench,
    chip_control,
    cigars,
    bust,
    can,
    scalpel,
    coin,
    arms,
    keycard,
    silenced_pistol,
    fiber_wire,
    deadly_poison,
    emetic_poison,
    disposable_scrambler,
    combat_knife
]

def item_by_name(item_name):
    item_names = {
        'Пистолет без глушителя': pistol,
        'Кухонный нож': kitchen_knife,
        'Ножницы': scissors,
        'Крысиный яд': rat_poison,
        'Яд рыбы Фугу': fugu_poison,
        'Молоток': hammer,
        'Гаечный ключ': wrench,
        'Пульт для управления нейрочипом': chip_control,
        'Пачка сигарет': cigars,
        'Бюст': bust,
        'Жестяная банка': can,
        'Скальпель': scalpel,
        'Монета': coin,
        'Нет предмета': arms,
        'Ключ-карта': keycard,
        'Пистолет с глушителем': silenced_pistol,
        'Удавка': fiber_wire,
        'Смертельный яд': deadly_poison,
        'Рвотный яд': emetic_poison,
        'Электронный дешифровщик': disposable_scrambler,
        'Боевой нож': combat_knife
    }
    return item_names[item_name]