class NPC:
    """Класс, описывающий NPC на локации"""
    def __init__(self, guard, disguise, route, witness_chance, name, alive=True):
        self.guard = guard
        self.disguise = disguise
        self.alive = alive
        self.route = route
        self.witness_chance = witness_chance
        self.name = name
    
    def move(self, time: int):
        """Определяет положение NPC в определенный момент времени"""
        location = self.route[int(time)%len(self.route)]
        return location

    def suspicion(self):
        return f'{self.name} ({self.disguise.name}): Эй, подойди сюда!'


class Target:
    """Класс, описывающий цели на локации """
    def __init__(self, route, name, alive=True):
        self.route = route
        self.name = name
        self.alive = alive

    def move(self, time: int):
        """Определяет положение цели в определенный момент времени"""
        location = self.route[int(time)%len(self.route)]
        return location
    
    def kill(self):
        self.alive = False
        return f'Диана: {self.name} больше нас не побеспокоит. Отличная работа, 47-й.'