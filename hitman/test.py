from controller.controller import PlayerController
from hitman.model.hokkaido.hokkaido_items import arms
from hitman.model.player.player import Player

player = Player(inventory=[],
                health=100,
                item=arms,
                compromised_disguises=[],
                disguise='Телохранитель')
controller = PlayerController(player)
while True:
    controller.move()