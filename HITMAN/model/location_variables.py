from model.locator import Locator

locator = Locator()


class LocationVariables:

    def __init__(self, locations=None):
        if locations is None:
            locations = 'Хоккайдо'
        self.npcs = locator.get_npcs(locations)
        self.locations = locator.get_locations(locations)
        self.challenges = locator.get_challenges(locations)
        self.objects = locator.get_objects(locations)
        self.disguises = locator.get_disguises(locations)
        self.targets = {}

