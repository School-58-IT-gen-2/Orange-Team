from hitman.hokkaido.hokkaido_npcs import hokkaido_npcs
from hitman.hokkaido.hokkaido_challenges import hokkaido_challenges
from hitman.hokkaido.hokkaido_locations import hokkaido_locations, hokkaido_objects, hokkaido_disguises


class Locator:
    def __init__(self):
        self.npcs = {'Хоккайдо': hokkaido_npcs}
        self.locations = {'Хоккайдо': hokkaido_locations}
        self.objects = {'Хоккайдо': hokkaido_objects}
        self.disguises = {'Хоккайдо': hokkaido_disguises}
        self.challenges = {'Хоккайдо': hokkaido_challenges}

    def get_npcs(self, location_name):
        return self.npcs[location_name]
    
    def get_locations(self, location_name):
        return self.locations[location_name]
    
    def get_objects(self, location_name):
        return self.objects[location_name]
    
    def get_disguises(self, location_name):
        return self.disguises[location_name]
    
    def get_challenges(self, location_name):
        return self.challenges[location_name]