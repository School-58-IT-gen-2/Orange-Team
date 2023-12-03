from Controller.controller import *


player = Player([], 100, hokkaido_locations[0], [], arms, [], 'Телохранитель')
controller = PlayerController(player)
while True:
    controller.move()