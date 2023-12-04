import random
from Model.location_variables import npcs
from Model.location_variables import disguises


class Location:

    def __init__(self, name, locations, disguise, witnesses, loot):
        self.name = name
        self.locations = locations
        self.disguise = disguise
        self.witnesses = witnesses
        self.loot = loot

    def find_location_npcs(self):
        location_npcs = []
        for i in npcs:
            if i.move() == self and i.alive == True:
                location_npcs.append(i)
        return location_npcs

    def location_witnesses(self):
        location_npcs = self.find_location_npcs()
        location_witnesses = self.witnesses
        for i in location_npcs:
            if random.randrange(11) <= i.witness_chance and i.alive == True:
                location_witnesses += 1
        return location_witnesses

    def location_status(self):
        result_string = f'{self.name}\n'
        location_npcs = self.find_location_npcs()
        location_disguises = []
        for i in location_npcs:
            if i.alive == True:
                location_disguises.append(i.disguise)
        if location_npcs != []:
            if self.witnesses > 0:
                result_string += f'\nНа локации находятся:\n\n{self.witnesses} Пациент'
            for i in range(1, len(disguises)+1):
                if disguises[i] in location_disguises:
                    result_string += f'\n{location_disguises.count(disguises[i]), disguises[i]}'
            result_string += f'\n\nВсего {self.location_witnesses()} свидетелей'
            return result_string
        else:
            result_string += '\nНа локации нет свидетелей'
            return result_string
