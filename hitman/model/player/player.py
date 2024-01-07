#Класс, описывающий игрока
class Player:

    def __init__(self,
                 location=None,
                 inventory=None,
                 health=None,
                 found_disguises=None,
                 item=None,
                 compromised_disguises=None,
                 disguise=None
                 ):

        self.current_location = location
        self.inventory = inventory
        self.health = health
        self.found_disguises = found_disguises
        self.item = item
        self.compromised_disguises = compromised_disguises
        self.disguise = disguise