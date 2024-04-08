class Challenge:
    """Класс, описывающий испытания на локации"""
    def __init__(self, name, description, completed=False):
        self.name = name
        self.description = description
        self.completed = completed

    def achieved(self):
        """Уведомление о выполнении условий испытания"""
        self.completed = True
        return f'Испытание выполнено: {self.name}'
