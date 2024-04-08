class Event:
    """Класс, описывающий событие на локации"""
    def __init__(self, name, completed=False):
        self.name = name
        self.completed = completed