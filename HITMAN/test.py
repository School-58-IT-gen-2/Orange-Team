from controller.controller import *


player = Player(inventory=[],
                health=100,
                found_disguises=[],
                item=arms,
                compromised_disguises=[],
                disguise='Телохранитель')
controller = PlayerController(player)
while True:
    controller.move()