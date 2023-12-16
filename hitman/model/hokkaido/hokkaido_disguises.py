from model.common.disguise import Disguise


class HokkaidoDisguises():
    def __init__(self):
        self.__disguises = {
                'VIP - пациент': Disguise('VIP - пациент'),
                'Охранник': Disguise('Охранник'),
                'Телохранитель': Disguise('Телохранитель'),
                'Шеф': Disguise('Шеф'),
                'Механик': Disguise('Механик'),
                'Хирург': Disguise('Хирург'),
                'Инструктор по йоге': Disguise('Инструктор по йоге'),
                'Работник морга': Disguise('Работник морга'),
                'Работник "ГАМА"': Disguise('Работник "ГАМА"'),
                'Директор клиники': Disguise('Директор клиники'),
                'Пилот': Disguise('Пилот'),
                'Главный хирург': Disguise('Главный хирург'),
                'Ниндзя': Disguise('Ниндзя')
        }

    def get_by_name(self, name):
        return self.__disguises[name]
    
    def get_all(self):
        return list(self.__disguises.values())