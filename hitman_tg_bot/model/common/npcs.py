from model.player.player_info import time, suspicion_count


#Класс, описывающий NPC на локации
class NPC:

    def __init__(self, guard, disguise, route, witness_chance, name, alive=True):
        self.guard = guard
        self.disguise = disguise
        self.alive = alive
        self.route = route
        self.witness_chance = witness_chance
        self.name = name
    
    #Определяет положение NPC в определенный момент времени
    def move(self):
        location = self.route[int(time[0])%len(self.route)]
        return location

    def suspicion(self):
        global suspicion_count
        suspicion_count[0] += 1
        return f'{self.name} ({self.disguise.name}): Эй, подойди сюда!'

#Класс, описывающий цели на локации 
class Target:

    def __init__(self, route, name, alive=True):
        self.route = route
        self.name = name
        self.alive = alive

    #Определяет положение цели в определенный момент времени
    def move(self):
        location = self.route[int(time[0])%len(self.route)]
        return location
    
    def kill(self):
        self.alive = False
        return f'{self.name} больше нас не побеспокоит. Отличная работа, 47-й.'