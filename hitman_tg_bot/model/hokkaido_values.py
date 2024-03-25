from hitman_adapter import HitmanAdapter

from common.challenges import Challenge
from common.disguises import Disguise
from common.items import Item
from common.location import Location
from common.npcs import NPC, Target


adapter = HitmanAdapter()

hallenges = {i[0]: Challenge(i[0], i[2]) for i in adapter.get_all('Challenges')}
disguises = {i[0]: Disguise(i[0]) for i in adapter.get_all('Disguise')}
items = {i[0]: Item(i[0], i[5], i[3], i[4], i[2]) for i in adapter.get_all('Items')}
locations = {i[0]: Location(i[0], [adapter.get_by_id('Locations', l)[0][0] for l in adapter.get_by_id('Locations Connection', i[1])[0][1]], [disguises[adapter.get_by_id('Disguise', j)[0][0]] for j in i[3]], i[4], [items[adapter.get_by_id('Items', k)[0][0]] for k in i[2]]) for i in adapter.get_all('Locations')}
npcs = {i[0]: NPC(i[2], i[3], i[6], i[4], i[0]) for i in adapter.get_all('NPCs')}

for i in locations.values():
    print(i.get_name(), i.get_connected_locations())