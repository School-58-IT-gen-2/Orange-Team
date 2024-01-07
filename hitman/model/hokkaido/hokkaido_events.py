from model.common.events import Event


#Класс, описывающий события в Хоккаидо
class HokkaidoEvents:
    def __init__(self):
        self.__events = {
            'Компьютер в морге': Event('Компьютер в морге'),
            'Информация о сигаретах 1': Event('Информация о сигаретах 1'),
            'Информация о сигаретах 2': Event('Информация о сигаретах 2'),
            'Информация о суши': Event('Информация о суши'),
            'Информация о чипе': Event('Информация о чипе'),
            'Расписание занятий по йоге': Event('Расписание занятий по йоге'),
            'Все цели убиты': Event('Все цели убиты'),
            'Убийство ядом': Event('Убийство ядом'),
            'Убийство в сауне': Event('Убийство в сауне'),
            'Убийство во время йоги': Event('Убийство во время йоги'),
            'Убийство сигаретами': Event('Убийство сигаретами'),
            'Сигареты на столе': Event('Сигареты на столе'),
            'Информация о пилоте': Event('Информация о пилоте'),
            'Устранение главного хирурга': Event('Устранение главного хирурга'),
            'Убийство в операционной': Event('Убийство в операционной'),
            'Информация об ИИ': Event('Информация об ИИ')
        }

    def get_by_name(self, name):
        return self.__events[name]
    
    def get_all(self):
        return list(self.__events.values())