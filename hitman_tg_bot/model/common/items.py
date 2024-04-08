class Item:
    """Класс, описывающий предметы на локации"""    
    def __init__(self, name, usage, legal, lethal, weapon):
        self.name = name
        self.usage = usage
        self.legal = legal
        self.lethal = lethal
        self.weapon = weapon