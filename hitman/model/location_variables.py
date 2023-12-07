from hitman.model.locator import Locator


class LocationVariables:

    def __init__(self, locations=None):
        self.locator = Locator()
        if locations is None:
            locations = 'Хоккайдо'
        self.npcs = self.locator.get_npcs(locations)
        self.locations = self.locator.get_locations(locations)
        self.challenges = self.locator.get_challenges(locations)
        self.objects = self.locator.get_objects(locations)
        self.disguises = self.locator.get_disguises(locations)
        self.targets = {}

