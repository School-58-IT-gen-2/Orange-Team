from model.player.player_info import time, suspicion_count


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
        location = self.route[int(time[0])%len(self.route)]
        return location
    
    def suspicion(self):
        global suspicion_count
        suspicion_count[0] += 1
        return f'{self.get_name()}: Эй, подойди сюда!'
    
class Target:

    def __init__(self, alive, route, name):
        self.alive = alive
        self.route = route
        self.name = name

    def move(self):
        location = self.route[int(time[0])%len(self.route)]
        return location