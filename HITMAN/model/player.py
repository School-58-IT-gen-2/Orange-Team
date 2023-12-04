class Player:

    def __init__(self,
                 inventory=None,
                 health=None,
                 location=None,
                 found_disguises=None,
                 item=None,
                 compromised_disguises=None,
                 disguise=None):
        self.inventory = inventory
        self.health = health
        self.location = location
        self.found_disguises = found_disguises
        self.item = item
        self.compromised_disguises = compromised_disguises
        self.disguise = disguise

    def set_location(self, location):
        self.location = location
