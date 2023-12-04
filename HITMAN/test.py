from Controller.controller import *


player = Player([], 100, locations[0], [], arms, [], 'Телохранитель')
controller = PlayerController(player)
while True:
    controller.move()