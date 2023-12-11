from model.hokkaido.hokkaido_locator import HokkaidoLocator

class Player:

    def __init__(self,
                 location,
                 inventory=None,
                 health=None,
                 found_disguises=None,
                 item=None,
                 compromised_disguises=None,
                 disguise=None,
                 locator=None):

        self.current_location = location
        self.inventory = inventory
        self.health = health
        self.found_disguises = found_disguises
        self.item = item
        self.compromised_disguises = compromised_disguises
        self.disguise = disguise

    def set_location(self, location):
        self.current_location = location
