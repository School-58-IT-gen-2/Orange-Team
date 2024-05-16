from model.hitman_adapter import HitmanAdapter

from model.common.challenges import Challenge
from model.common.disguises import Disguise
from model.common.items import Item
from model.common.location import Location
from model.common.npcs import NPC, Target
from model.common.events import Event


adapter = HitmanAdapter()

items = {i[0]: Item(name=i[0], usage=i[5].split('/') if i[5] else [], legal=i[3], lethal=i[4], weapon=i[2]) for i in adapter.get_all('items')}

hokkaido_challenges = {i[0]: Challenge(name=i[0], description=i[2], url=i[3], xp=i[4], type=adapter.get_by_id('challenge_types', i[5])[0][0]) for i in adapter.get_all('hokkaido_challenges')}
hokkaido_disguises = {i[0]: Disguise(name=i[0], url=i[2]) for i in adapter.get_all('hokkaido_disguises')}
hokkaido_locations = {i[0]: Location(name=i[0], connetcted_locations=[adapter.get_by_id('hokkaido_locations', l)[0][0] for l in adapter.get_by_id('hokkaido_locations_connections', i[1])[0][1]], disguise=[hokkaido_disguises[adapter.get_by_id('hokkaido_disguises', j)[0][0]] for j in i[3]], witnesses=i[4], items=[items[adapter.get_by_id('items', k)[0][0]] for k in i[2]], url=i[5]) for i in adapter.get_all('hokkaido_locations')}
hokkaido_npcs = {i[0]: NPC(guard=i[2], disguise=hokkaido_disguises[adapter.get_by_id('hokkaido_disguises', i[3])[0][0]], route={j: adapter.get_by_id('hokkaido_locations', i[5][j])[0][0] for j in range(len(i[5]))}, witness_chance=i[4], name=i[0]) for i in adapter.get_all('hokkaido_npcs')}
hokkaido_targets = {i[0]: Target(route={j: adapter.get_by_id('hokkaido_locations', i[2][j])[0][0] for j in range(len(i[2]))}, name=i[0]) for i in adapter.get_all('hokkaido_targets')}
hokkaido_events = {i[0]: Event(name=i[0]) for i in adapter.get_all('hokkaido_events')}

ica_challenges = {i[0]: Challenge(name=i[0], description=i[2], url=i[3], xp=i[4], type=adapter.get_by_id('challenge_types', i[5])[0][0]) for i in adapter.get_all('ica_challenges')}
ica_disguises = {i[0]: Disguise(name=i[0], url=i[2]) for i in adapter.get_all('ica_disguises')}
ica_locations = {i[0]: Location(name=i[0], connetcted_locations=[adapter.get_by_id('ica_locations', l)[0][0] for l in adapter.get_by_id('ica_locations_connections', i[1])[0][1]], disguise=[ica_disguises[adapter.get_by_id('ica_disguises', j)[0][0]] for j in i[3]], witnesses=i[4], items=[items[adapter.get_by_id('items', k)[0][0]] for k in i[2]], url=i[5]) for i in adapter.get_all('ica_locations')}
ica_npcs = {i[0]: NPC(guard=i[2], disguise=ica_disguises[adapter.get_by_id('ica_disguises', i[3])[0][0]], route={j: adapter.get_by_id('ica_locations', i[5][j])[0][0] for j in range(len(i[5]))}, witness_chance=i[4], name=i[0]) for i in adapter.get_all('ica_npcs')}
ica_targets = {i[0]: Target(route={j: adapter.get_by_id('ica_locations', i[2][j])[0][0] for j in range(len(i[2]))}, name=i[0]) for i in adapter.get_all('ica_targets')}
ica_events = {i[0]: Event(name=i[0]) for i in adapter.get_all('ica_events')}

missions = {'hokkaido': {'challenges': hokkaido_challenges, 'disguises': hokkaido_disguises, 'locations': hokkaido_locations, 'npcs': hokkaido_npcs, 'targets': hokkaido_targets, 'events': hokkaido_events, 'items': items}, 'ica': {'challenges': ica_challenges, 'disguises': ica_disguises, 'locations': ica_locations, 'npcs': ica_npcs, 'targets': ica_targets, 'events': ica_events, 'items': items}}

hokkaido_lvl_unlocks = {
            1: ['Номер 47-го', 'VIP - пациент'],
            2: ['Зона спа', 'VIP - пациент'],
            3: ['Горная тропа', 'Ниндзя'],
            4: ['Ресторан', 'VIP - пациент'],
            5: ['Спальня персонала', 'Работник "ГАМА"'],
            6: ['Кухня', 'Шеф'],
            7: ['Внутренний сад', 'Работник "ГАМА"'],
            8: ['Морг', 'VIP - пациент'],
            9: ['Операционная', 'Хирург']
        }
