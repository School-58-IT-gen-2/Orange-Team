from Model.locator import Locator


locator = Locator()

def init():
    global npcs
    global locations
    global challenges
    global objects
    global disguises
    global targets
    npcs = locator.get_npcs('Хоккайдо')
    locations = locator.get_locations('Хоккайдо')
    challenges = locator.get_challenges('Хоккайдо')
    objects = locator.get_objects('Хоккайдо')
    disguises = locator.get_disguises('Хоккайдо')
    targets = {}