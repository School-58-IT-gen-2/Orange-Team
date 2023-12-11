from controller.controller import PlayerController
from model.hokkaido.hokkaido_items import HokkaidoItems
from model.player.player import Player
from model.player.player_info import time
from model.hokkaido.hokkaido_locator import HokkaidoLocator


player = Player(location=HokkaidoLocator().get_location_by_name('Номер 47-го'),
                inventory=[],
                health=100,
                item=HokkaidoItems().get_by_name('Нет предмета'),
                compromised_disguises=[],
                disguise='Телохранитель')
controller = PlayerController(player=player)
while True:
    controller.move()
    time[0] += 1