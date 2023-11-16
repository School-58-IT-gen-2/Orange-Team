import random
from Settings.locations import *
from Settings.loot import *

class Player:

    def __init__(self, inventory, health, location, found_disguises, item, compromised_disguises, disguise):
        self.inventory = inventory
        self.health = health
        self.location = location
        self.found_disguises = found_disguises
        self.item = item
        self.compromised_disguises = compromised_disguises
        self.disguise = disguise

player = Player([], 100, suite, ['VIP - пациент'], arms, [], 'VIP - пациент')

class NPC:

    def __init__(self, guard, disguise, alive, route, witness_chance):
        self.guard = guard
        self.disguise = disguise
        self.alive = alive
        self.route = route
        self.witness_chance = witness_chance

    def move(self):
        if self.alive == True:
            location = self.route[int(time)%len(self.route)]
            return location_by_name(location)
        else:
            return False
    
    def investigate(self):
        if self.alive == True:
            og_route = self.route
            og_witness_chance = self.witness_chance
            self.route = {0: self.move()}
            self.witness_chance = 0
            return [og_route, og_witness_chance]
        else:
            return False

    def panic(self):
        if self.alive == True:
            og_route = self.route
            og_witness_chance = self.witness_chance
            if self.guard == True:
                return True
            else:
                self.route = {0: (self.move()).locations[random.randrange(1, len(self.move().locations)+1)]}
            return [og_route, og_witness_chance]
        else:
            return False
    
    def calm_down(self, og_route, og_witness_chance):
        if self.alive == True:
            self.witness_chance = og_witness_chance
            self.route = og_route
            return self.move()
        else:
            return False
    
    def suspicion(self):
        global suspicion_count
        if self.alive == True:
            suspicion_count += 1
            return f'\n\n{self.disguise}: Эй, ты не должен сдесь находится!'
        else:
            return False
        

guard_cable_car_1 = NPC(True, 'Телохранитель', True, {0: 'Канатная дорога'}, 5)
guard_cable_car_2 = NPC(True, 'Телохранитель', True, {0: 'Канатная дорога'}, 5)
guard_hall_1 = NPC(True, 'Охранник', True, {0: 'Холл'}, 7)
guard_hall_2 = NPC(True, 'Охранник', True, {0: 'Холл'}, 7)
guard_hall_3 = NPC(True, 'Охранник', True, {0: 'Холл', 1: 'Комната охраны'}, 8)
guard_spa_1 = NPC(True, 'Охранник', True, {0: 'Зона спа'}, 4)
guard_restaurant_1 = NPC(True, 'Охранник', True, {0: 'Ресторан'}, 6)
guard_restaurant_2 = NPC(True, 'Охранник', True, {0: 'Ресторан'}, 8)
guard_garden_1 = NPC(True, 'Охранник', True, {0: 'Внутренний сад'}, 3)
guard_garden_2 = NPC(True, 'Охранник', True, {0: 'Внутренний сад'}, 5)
guard_medical_center_1 = NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс'}, 2)
guard_medical_center_2 = NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс'}, 2)
guard_medical_center_3 = NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс'}, 1)
guard_medical_center_4 = NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс', 1: 'Операционная'}, 2)
guard_security_room = NPC(True, 'Охранник', True, {0: 'Комната охраны'}, 1)
guard_garage = NPC(True, 'Охранник', True, {0: 'Гараж'}, 7)
guard_bar = NPC(True, 'Охранник', True, {0: 'Барная стойка'}, 2)
guard_morgue = NPC(True, 'Телохранитель', True, {0: 'Морг'}, 2)
guard_target_suite_1 = NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки'}, 1)
guard_target_suite_2 = NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки'}, 7)
guard_target_suite_3 = NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки'}, 8)
guard_target_suite_4 = NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки'}, 5)
guard_helipad_1 = NPC(True, 'Телохранитель', True, {0: 'Вертолетная площадка'}, 8)
guard_helipad_2 = NPC(True, 'Телохранитель', True, {0: 'Вертолетная площадка'}, 9)
guard_medical_center_level_2_1 = NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс (2 этаж)'}, 3)
guard_medical_center_level_2_2 = NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс (2 этаж)'}, 5)
guard_medical_center_level_2_3 = NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс (2 этаж)'}, 1)
guard_medical_center_level_2_4 = NPC(True, 'Телохранитель', True, {0: 'Мед-комплекс (2 этаж)'}, 6)
target_guard = NPC(True, 'Телохранитель', True, {0: 'Номер Юки Ямадзаки', 1: 'Холл', 2: 'Ресторан', 3: 'Холл', 4: 'Зона спа', 5: 'Зона отдыха', 6: 'Зона спа', 7: 'Холл', 8: 'Номер Юки Ямадзаки'}, 8)

staff_spa_1 = NPC(False, 'Работник "ГАМА"', True, {0: 'Зона спа', 1: 'Зона отдыха'}, 7)
staff_spa_2 = NPC(False, 'Работник "ГАМА"', True, {0: 'Зона спа'}, 8)
staff_restaurant_1 = NPC(False, 'Работник "ГАМА"', True, {0: 'Ресторан'}, 7)
staff_restaurant_2 = NPC(False, 'Работник "ГАМА"', True, {0: 'Ресторан'}, 8)
staff_garden_1 = NPC(False, 'Работник "ГАМА"', True, {0: 'Внутренний сад'}, 1)
staff_garden_2 = NPC(False, 'Работник "ГАМА"', True, {0: 'Внутренний сад'}, 3)
surgeon_medical_center = NPC(False, 'Хирург', True, {0: 'Мед-комплекс', 1: 'Операционная'}, 1)
mechanic_garage = NPC(False, 'Механик', True, {0: 'Гараж'}, 1)
yoga_coach = NPC(False, 'Инструктор по йоге', True, {0: 'Гараж', 1: 'Спальня персонала'}, 1)
chef_1 = NPC(False, 'Шеф', True, {0: 'Кухня'}, 2)
chef_2 = NPC(False, 'Шеф', True, {0: 'Кухня'}, 5)
morgue_worker_1 = NPC(False, 'Работник морга', True, {0: 'Морг'}, 3)
morgue_worker_2 = NPC(False, 'Работник морга', True, {0: 'Морг'}, 3)
morgue_worker_3 = NPC(False, 'Работник морга', True, {0: 'Морг'}, 1)
surgeon_operation_room_1 = NPC(False, 'Хирург', True, {0: 'Операционная'}, 7)
surgeon_operation_room_2 = NPC(False, 'Хирург', True, {0: 'Операционная'}, 9)
surgeon_operation_room_3 = NPC(False, 'Хирург', True, {0: 'Операционная'}, 8)
chief_surgeon = NPC(False, 'Главный хирург', True, {0: 'Операционная'}, 7)
pilot = NPC(False, 'Пилот', True, {0: 'Комната пилота'}, 8)
director = NPC(False, 'Директор клиники', True, {0: 'Холл', 1: 'Внутренний сад', 2: 'Холл', 3: 'Мед-комплекс', 4: 'Мед-комплекс (2 этаж)', 5: 'Комната директора клиники', 6: 'Комната директора клиники', 7:'Комната директора клиники', 8: 'Мед-комплекс (2 этаж)', 9: 'Мед-комплекс', 10: 'Холл'}, 7)

npcs = [guard_cable_car_1, 
        guard_cable_car_2, 
        guard_hall_1, 
        guard_hall_2, 
        guard_hall_3, 
        guard_spa_1, 
        guard_restaurant_1, 
        guard_restaurant_2, 
        guard_garden_1, 
        guard_garden_2,
        guard_security_room,
        guard_garage,
        guard_bar,
        guard_morgue,
        guard_target_suite_1,
        guard_target_suite_2,
        guard_target_suite_3,
        guard_target_suite_4,
        guard_medical_center_1, 
        guard_medical_center_2, 
        guard_medical_center_3, 
        guard_medical_center_4, 
        guard_helipad_1, 
        guard_helipad_2, 
        guard_medical_center_level_2_1, 
        guard_medical_center_level_2_2, 
        guard_medical_center_level_2_3, 
        guard_medical_center_level_2_4, 
        target_guard, 
        staff_spa_1, 
        staff_spa_2, 
        staff_restaurant_1, 
        staff_restaurant_2, 
        surgeon_medical_center, 
        mechanic_garage, 
        yoga_coach, 
        chef_1, 
        chef_2, 
        morgue_worker_1, 
        morgue_worker_2, 
        morgue_worker_3, 
        surgeon_operation_room_1, 
        surgeon_operation_room_2, 
        surgeon_operation_room_3, 
        chief_surgeon, 
        pilot, 
        director]

def rating():
    print('\n')
    print(f'Тел найдено: {bodies}')
    print(f'Убито невинных: {kills}')
    print(f'Вы начали бой {combat_count} раз')
    print(f'Вы были замечены {suspicion_count} раз')
    return f'Ваш рейтинг: {int(5-(bodies*0.5)-(kills*0.7)-(combat_count*0.1)-(suspicion_count*0.2))}/5'

target_status = {
    0: 'Номер Юки Ямадзаки',
    1: 'Холл',
    2: 'Ресторан',
    3: 'Холл',
    4: 'Зона спа',
    5: 'Зона отдыха',
    6: 'Зона спа',
    7: 'Холл',
    8: 'Номер Юки Ямадзаки'
}

suspicion_count = 0
kills = 0
bodies = 0
time = 0
soders = 1
yuki = 1
morgue_info = 0
cigar_info = 0
cigar_info2 = 0
poison_info = 0
chip_info = 0
yoga_info = 0
final = 0
poison_kill = 0
combat_count = 0
poisons = ['Яд рыбы Фугу', 'Крысиный яд']
so = 0
sauna_kill = 0
yoga_kill = 0
cigar_kill = 0
cigar_place = 0
pistol = 0
pilot_info = 0
chief_surgeon = 1
get_chief_surgeon = 0
surgeon_kill = 0
ai_info = 0

print(staff_garden_1.move().name)
og_route = staff_garden_1.panic()[0]
current_time = time
for i in range(10):
    if time - current_time == 3:
        staff_garden_1.calm_down(og_route, staff_garden_1.witness_chance)
    print(staff_garden_1.move().name)
    time+=1