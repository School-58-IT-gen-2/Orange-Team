from model.hitman_adapter import HitmanAdapter

from model.common.challenges import Challenge
from model.common.disguises import Disguise
from model.common.items import Item
from model.common.location import Location
from model.common.npcs import NPC, Target
from model.common.events import Event


adapter = HitmanAdapter()

challenges = {i[0]: Challenge(name=i[0], description=i[2]) for i in adapter.get_all('Challenges')}
disguises = {i[0]: Disguise(name=i[0]) for i in adapter.get_all('Disguise')}
items = {i[0]: Item(name=i[0], usage=i[5].split('/') if i[5] else [], legal=i[3], lethal=i[4], weapon=i[2]) for i in adapter.get_all('Items')}
locations = {i[0]: Location(name=i[0], connetcted_locations=[adapter.get_by_id('Locations', l)[0][0] for l in adapter.get_by_id('Locations Connection', i[1])[0][1]], disguise=[disguises[adapter.get_by_id('Disguise', j)[0][0]] for j in i[3]], witnesses=i[4], items=[items[adapter.get_by_id('Items', k)[0][0]] for k in i[2]]) for i in adapter.get_all('Locations')}
npcs = {i[0]: NPC(guard=i[2], disguise=disguises[adapter.get_by_id('Disguise', i[3])[0][0]], route={j: adapter.get_by_id('Locations', i[5][j])[0][0] for j in range(len(i[5]))}, witness_chance=i[4], name=i[0]) for i in adapter.get_all('NPCs')}
targets = {i[0]: Target(route={j: adapter.get_by_id('Locations', i[2][j])[0][0] for j in range(len(i[2]))}, name=i[0]) for i in adapter.get_all('Targets')}
events = {i[0]: Event(name=i[0]) for i in adapter.get_all('Events')}

lvl_unlocks = {
            1: ['Номер 47-го', 'VIP - пациент'],
            2: ['Зона спа', 'VIP - пациент'],
            3: ['Горная тропа', 'Ниндзя'],
            4: ['Ресторан', 'VIP - пациент'],
            5: ['Спальня персонала', 'Работник "ГАМА"'],
            6: ['Кухня', 'Шеф'],
            7: ['Внутренний сад', 'Работник "ГАМА"'],
            8: ['Морг', 'VIP - пациент'],
            9: ['Оперционная', 'Хирург']
        }

carry_on_items = [
    'Удавка', 
    'Смертельный яд', 
    'Рвотный яд', 
    'Электронный дешифровщик', 
    'Боевой нож', 
    'Монета']
