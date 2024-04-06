#Класс, описывающий испытания на локации
class Challenge:

    def __init__(self, name, description, completed=False):
        self.name = name
        self.description = description
        self.completed = completed

    #Уведомление о выполнении условий испытания
    def achieved(self):
        if self.completed == False:
            self.completed = True
            return f'Испытание выполнено: {self.name}'
        return ''