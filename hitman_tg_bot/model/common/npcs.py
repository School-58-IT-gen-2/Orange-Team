from player.player_info import time, suspicion_count


#Класс, описывающий NPC на локации
class NPC:

    def __init__(self, guard, disguise, route, witness_chance, name, alive=True):
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
    
    #Определяет положение NPC в определенный момент времени
    def move(self):
        location = self.route[int(time[0])%len(self.route)]
        return location

    def suspicion(self):
        global suspicion_count
        suspicion_count[0] += 1
        return f'{self.get_name()}: Эй, подойди сюда!'

#Класс, описывающий цели на локации 
class Target:

    def __init__(self, alive, route, name):
        self.alive = alive
        self.route = route
        self.name = name

    #Определяет положение цели в определенный момент времени
    def move(self):
        location = self.route[int(time[0])%len(self.route)]
        return location
    
    def get_name(self):
        return f'{self.name}'