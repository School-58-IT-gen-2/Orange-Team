#Класс, описывающий маскировки на локации
class Disguise():

    def __init__(self, name):
        self.__name = name

    def get_name(self):
        return self.__name