from hitman.model.global_variables import time, suspicion_count


class NPC:

    def __init__(self, guard, disguise, alive, route, witness_chance, name):
        self.guard = guard
        self.disguise = disguise
        self.alive = alive
        self.route = route
        self.witness_chance = witness_chance
        self.name = name

    def get_name(self):
        return f'{self.disguise} ({self.name})'

    def move(self):
        if self.alive == True:
            location = self.route[int(time)%len(self.route)]
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