from controller.controller import PlayerController
from model.hokkaido.hokkaido_items import HokkaidoItems
from model.player.player import Player
from model.player.player_info import time
from model.hokkaido.hokkaido_locator import HokkaidoLocator


player = Player(location=HokkaidoLocator().get_location_by_name('Номер 47-го'),
                inventory=[HokkaidoItems().get_by_name('Пистолет с глушителем')],
                health=100,
                item=HokkaidoItems().get_by_name('Нет предмета'),
                compromised_disguises=[],
                disguise='VIP - пациент',
                found_disguises=['VIP - пациент'])
controller = PlayerController(player=player)
while True:
    request = controller.player_view.request()
    if request.upper() == 'W':
        controller.move()
        time[0] += 0.5
    elif request.upper() == 'S':
        controller.status()
    elif request.upper() == 'C':
        controller.see_challenges()
    elif request.upper() == 'E':
        controller.search()
        time[0] += 1
    elif request.upper() == 'I':
        controller.inventory()