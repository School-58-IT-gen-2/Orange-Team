from model.common.challenges import Challenge


#Класс, описывающий испытания в Хоккаидо
class HokkaidoChallenges:
    def __init__(self):
        self.__challenges = {
            'Курение убивает':
                Challenge('Курение убивает', 'Убейте Юки Ямадзаки во время того, как она курит сигареты.', False),
            'Хорошая растяжка':
                Challenge('Хорошая растяжка', 'Убейте Юки Ямадзаки, подстроив несчастный случай во время занятий йогой.', False),
            'Хорошая растяжка':
                Challenge('Хорошая растяжка', 'Убейте Юки Ямадзаки, подстроив несчастный случай во время занятий йогой.', False),
            'Личное прощание':
                Challenge('Личное прощание', 'Убейте Эриха Содерса выстрелом из пистолета.', False),
            'Не курить!':
                Challenge('Не курить!', 'Положите пачку сигарет в номере Юки Ямадзаки.', False),
            '(Не) врачебная ошибка':
                Challenge('(Не) врачебная ошибка', 'Убейте Эриха Содерса, самостоятельно проведя операцию.', False),
            'Только костюм':
                Challenge('Только костюм', '1. Завершите миссию\n2. Сделайте это в маскировке VIP - пациента', False),
            'Бесшумный убийца':
                Challenge('Бесшумный убийца', '1. Завершите миссию\n2. Убивайте только цели\n3. Ни одно тело не должно быть обнаружено\n4. Не дайте себя заметить', False),
            'Убийство в парилке':
                Challenge('Убийство в парилке', 'Убейте Юки Ямадзаки, заперев ее в парилке.', False),
            'Приятного аппетита':
                Challenge('Приятного аппетита', 'Отравите роллы Юки Ямадзаки ядом рыбы фугу.', False),
            'Бессердечный':
                Challenge('Бессердечный', 'Повредите сердце Эриха содерса.', False),
            'Бесшумный убийца. Только костюм.':
                Challenge('Бесшумный убийца. Только костюм.', '1. Завершите миссию\n2. Убивайте только цели\n3. Ни одно тело не должно быть обнаружено\n4. Не дайте себя заметить\n5. Сделайте это в маскировке VIP - пациента', False),
            'Без улик':
                Challenge('Без улик', 'Завершите миссию, не давая обнаружить тела.', False),
            'Призрак в машине':
                Challenge('Призрак в машине', 'Повредите сервера KAI.', False),
            'Точный выстрел':
                Challenge('Точный выстрел', 'Убейте цель выстрелом из пистолета.', False),
            'Подержи волосы':
                Challenge('Подержи волосы', 'Убейте цель, утопив ее.', False),
            'Пианист':
                Challenge('Пианист', 'Убейте цель при помощи удавки.', False),
            'Так можно и пораниться':
                Challenge('Так можно и пораниться', 'Убейте цель, подстроив несчастный случай.', False),
            'Без вкуса, без следа':
                Challenge('Без вкуса, без следа', 'Устраните цель, отравив ее.', False),
            'Мастер-убийца':
                Challenge('Мастер-убийца', f'1. Выполните Точный выстрел\n2. Выполните Подержи волосы\n3. Выполните Пианист\n4. Выполните Так можно и пораниться\n5. Выполните Без вкуса, без следа', False)
        }

    def get_by_name(self, name):
        return self.__challenges[name]
    
    def get_all(self):
        return list(self.__challenges.values())