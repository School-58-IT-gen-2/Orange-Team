from hitman.model.hokkaido.hokkaido_locator import HokkaidoLocator

class Player:

    def __init__(self,
                 inventory=None,
                 health=None,
                 found_disguises=None,
                 item=None,
                 compromised_disguises=None,
                 disguise=None,
                 locator=None,
                 location_name=None):

        if locator:
            self.__locator = locator
        else:
            self.__locator = HokkaidoLocator()

        if location_name:
            self.current_location = self.__locator.get_location_by_name(location_name)
        else:
            self.current_location = self.__locator.get_init_location()
        self.inventory = inventory
        self.health = health
        self.found_disguises = found_disguises
        self.item = item
        self.compromised_disguises = compromised_disguises
        self.disguise = disguise


