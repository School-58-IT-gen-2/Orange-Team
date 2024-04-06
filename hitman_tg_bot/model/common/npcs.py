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
    def move(self, time):
        location = self.route[int(time)%len(self.route)]
        return location

    def suspicion(self):
        return f'{self.name} ({self.disguise.name}): Эй, подойди сюда!'

#Класс, описывающий цели на локации 
class Target:

    def __init__(self, route, name, alive=True):
        self.route = route
        self.name = name
        self.alive = alive

    #Определяет положение цели в определенный момент времени
    def move(self, time):
        location = self.route[int(time)%len(self.route)]
        return location
    
    def kill(self):
        self.alive = False
        return f'{self.name} больше нас не побеспокоит. Отличная работа, 47-й.'