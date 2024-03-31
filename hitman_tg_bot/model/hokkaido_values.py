from model.hitman_adapter import HitmanAdapter

from model.common.challenges import Challenge
from model.common.disguises import Disguise
from model.common.items import Item
from model.common.location import Location
from model.common.npcs import NPC, Target


adapter = HitmanAdapter()

challenges = {i[0]: Challenge(name=i[0], description=i[2]) for i in adapter.get_all('Challenges')}
disguises = {i[0]: Disguise(name=i[0]) for i in adapter.get_all('Disguise')}
items = {i[0]: Item(name=i[0], usage=i[5].split('/') if i[5] else [], legal=i[3], lethal=i[4], weapon=i[2]) for i in adapter.get_all('Items')}
locations = {i[0]: Location(name=i[0], connetcted_locations=[adapter.get_by_id('Locations', l)[0][0] for l in adapter.get_by_id('Locations Connection', i[1])[0][1]], disguise=[disguises[adapter.get_by_id('Disguise', j)[0][0]] for j in i[3]], witnesses=i[4], items=[items[adapter.get_by_id('Items', k)[0][0]] for k in i[2]]) for i in adapter.get_all('Locations')}
npcs = {i[0]: NPC(guard=i[2], disguise=disguises[adapter.get_by_id('Disguise', i[3])[0][0]], route={j: adapter.get_by_id('Locations', i[5][j])[0][0] for j in range(len(i[5]))}, witness_chance=i[4], name=i[0]) for i in adapter.get_all('NPCs')}
targets = {i[0]: Target(route={j: adapter.get_by_id('Locations', i[2][j])[0][0] for j in range(len(i[2]))}, name=i[0]) for i in adapter.get_all('Targets')}

lvl_unlocks = {
            1: ['Номер 47-го', locations['Номер 47-го'], disguises['VIP - пациент']],
            2: ['Зона спа', locations['Зона спа'], disguises['VIP - пациент']],
            3: ['Горная тропа', locations['Горная тропа'], disguises['Ниндзя']],
            4: ['Ресторан', locations['Ресторан'], disguises['VIP - пациент']],
            5: ['Спальня персонала', locations['Спальня персонала'], disguises['Работник "ГАМА"']],
            6: ['Кухня', locations['Кухня'], disguises['Шеф']],
            7: ['Внутренний сад', locations['Внутренний сад'], disguises['Работник "ГАМА"']],
            8: ['Морг', locations['Морг'], disguises['VIP - пациент']],
            9: ['Оперционная', locations['Операционная'], disguises['Хирург']]
        }

carry_on_items = [
    'Удавка', 
    'Смертельный яд', 
    'Рвотный яд', 
    'Электронный дешифровщик', 
    'Боевой нож', 
    'Монета']

start_location = ''
start_disguise = ''
start_items = []
