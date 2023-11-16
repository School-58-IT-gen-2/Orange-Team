class Item:
    def __init__(self, name, usage, breakable, poison, illegal, deadly, distraction):
        self.name = name
        self.usage = usage
        self.breakable = breakable
        self.poison = poison
        self.illegal = illegal
        self.deadly = deadly
        self.distraction = distraction

pistol = Item('Пистолет без глушителя', ['Выстрелить', 'Отменить действие'], False, False, True, True, False)
kitchen_knife = Item('Кухонный нож', ['Бросить (летально)', 'Ударить (летально)', 'Отменить действие'], False, False, True, True, False)
scissors = Item('Ножницы', ['Бросить (летально)', 'Ударить (летально)', 'Отменить действие'], False, False, False, True, False)
rat_poison = Item('Крысиный яд', [], True, True, False, False, False)
fugu_poison = Item('Яд рыбы Фугу', [], True, True, False, True, False)
hammer = Item('Молоток', ['Бросить', 'Ударить', 'Отменить действие'], False, False, False, False, False)
wrench = Item('Гаечный ключ', ['Бросить', 'Ударить', 'Отменить действие'], False, False, False, False, False)
chip_control = Item('Пульт для управления нейрочипом', ['Использовать', 'Отменить действие'], True, False, False, False, False)
cigars = Item('Пачка сигарет', [], True, False, False, False, False)
bust = Item('Бюст', ['Бросить', 'Ударить', 'Отменить действие'], False, False, False, False, False)
can = Item('Жестяная банка', ['Бросить для отвлечения', 'Отменить действие'], True, False, False, False, True)
scalpel = Item('Скальпель', ['Бросить (летально)', 'Ударить (летально)', 'Отменить действие'], False, False, True, True, False)
coin = Item('Монета', ['Бросить для отвлечения', 'Отменить действие'], False, False, False, False, True)
arms = Item('Нет предмета', ['Усмирить', 'Отменить действие'], False, False, True, False, False)
keycard = Item('Ключ-карта', [], True, False, False, False, False)

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
    12: 'Главный хирург'
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
    keycard
]