from model.player.player_info import time


class NPC:

    def __init__(self, guard, disguise, alive, route, witness_chance, name):
        self.guard = guard
        self.__disguise = disguise
        self.alive = alive
        self.route = route
        self.witness_chance = witness_chance
        self.name = name

    def get_disguise(self):
        return self.__disguise

    def get_name(self):
        return f'{self.__disguise} ({self.name})'

    def move(self):
        if self.alive == True:
            location = self.route[int(time[0])%len(self.route)]
            return location
        else:
            return False
    
    def suspicion(self):
        global suspicion_count
        if self.alive == True:
            suspicion_count[0] += 1
            return f'{self.get_name()}: Эй, ты не можешь здесь находится!'
        else:
            return False