from Model.npcs import NPC
from Hokkaido.hokkaido_locations import *


guard_cable_car_1 = NPC(True, 'Телохранитель', True, {0: cable_car}, 5, 'Shoichi Kataoka')
guard_cable_car_2 = NPC(True, 'Телохранитель', True, {0: cable_car}, 5, 'Hidaka Uno')
guard_hall_1 = NPC(True, 'Охранник', True, {0: hall}, 8, 'Nikica Pranjić')
guard_hall_2 = NPC(True, 'Охранник', True, {0: hall}, 8, 'Toshimi Shinden')
guard_hall_3 = NPC(True, 'Охранник', True, {0: hall, 1: security_room}, 8, 'Hans Hansson')
guard_spa_1 = NPC(True, 'Охранник', True, {0: spa}, 4, 'Masashi Morioka')
guard_restaurant_1 = NPC(True, 'Охранник', True, {0: restaurant}, 8, 'Tadao Motsuzuki')
guard_restaurant_2 = NPC(True, 'Охранник', True, {0: restaurant}, 9, 'Hidetoshi Higa')
guard_garden_1 = NPC(True, 'Охранник', True, {0: garden}, 3, 'Oliver Drabløs')
guard_garden_2 = NPC(True, 'Охранник', True, {0: garden}, 5, 'Yasuaki Inagaki')
guard_medical_center_1 = NPC(True, 'Телохранитель', True, {0: medical_center}, 6, 'Junya Andou')
guard_medical_center_2 = NPC(True, 'Телохранитель', True, {0: medical_center}, 7, 'Homare Kanai')
guard_medical_center_3 = NPC(True, 'Телохранитель', True, {0: medical_center}, 6, 'Toshihisa Taniguchi')
guard_medical_center_4 = NPC(True, 'Телохранитель', True, {0: medical_center, 1: operation_room}, 9, 'Shuusuke Seki')
guard_security_room = NPC(True, 'Охранник', True, {0: security_room}, 9, 'Kyuuya Sugiyama')
guard_garage = NPC(True, 'Охранник', True, {0: garage}, 7, 'Max Gerber')
guard_bar = NPC(True, 'Охранник', True, {0: bar}, 2, 'John Maverick')
guard_morgue = NPC(True, 'Телохранитель', True, {0: morgue}, 2, 'Miamoto San')
guard_target_suite_1 = NPC(True, 'Телохранитель', True, {0: target_suite, 1: hall}, 8, 'Kyouta Shinden')
guard_target_suite_2 = NPC(True, 'Телохранитель', True, {0: target_suite, 1: hall}, 9, 'Hayaki Fukasawa')
guard_target_suite_3 = NPC(True, 'Телохранитель', True, {0: target_suite}, 8, 'Kaimei Kuroki')
guard_target_suite_4 = NPC(True, 'Телохранитель', True, {0: target_suite}, 7, 'Kou Tokunaga')
guard_target_suite_5 = NPC(True, 'Телохранитель', True, {0: target_suite}, 7, 'Salvio Parra Rojo')
guard_target_suite_6 = NPC(True, 'Телохранитель', True, {0: target_suite}, 7, 'Yoshikazu Sasaki')
guard_helipad_1 = NPC(True, 'Телохранитель', True, {0: helipad}, 8, 'Samuel Santos Lima')
guard_helipad_2 = NPC(True, 'Телохранитель', True, {0: helipad}, 9, 'Rafn Helguson')
guard_medical_center_level_2_1 = NPC(True, 'Телохранитель', True, {0: medical_center_level_2}, 8, 'Hayato Shinden')
guard_medical_center_level_2_2 = NPC(True, 'Телохранитель', True, {0: medical_center_level_2}, 9, 'Shuusuke Kitajima')
guard_medical_center_level_2_3 = NPC(True, 'Телохранитель', True, {0: medical_center_level_2}, 7, 'Sorahiko Satou')
guard_medical_center_level_2_4 = NPC(True, 'Телохранитель', True, {0: medical_center_level_2}, 8, 'Satomu Sugiyama')
target_guard_1 = NPC(True, 'Телохранитель', True, {0: target_suite, 1: hall, 2: restaurant, 3: hall, 4: spa, 5: resort, 6: spa, 7: hall, 8: target_suite}, 8, 'Nokadota')
target_guard_2 = NPC(True, 'Телохранитель', True, {0: target_suite, 1: hall, 2: restaurant, 3: hall, 4: spa, 5: resort, 6: spa, 7: hall, 8: target_suite}, 8, 'Yuuto Saiki')

staff_spa_1 = NPC(False, 'Работник "ГАМА"', True, {0: spa, 1: resort}, 7, 'Tamika Oomori')
staff_spa_2 = NPC(False, 'Работник "ГАМА"', True, {0: spa}, 8, 'Harumi Sakei')
staff_restaurant_1 = NPC(False, 'Работник "ГАМА"', True, {0: restaurant}, 7, 'Kouko Yoshioka')
staff_restaurant_2 = NPC(False, 'Работник "ГАМА"', True, {0: restaurant}, 8, 'Risae Oosawa')
staff_garden_1 = NPC(False, 'Работник "ГАМА"', True, {0: garden}, 1, 'Maury Veich')
staff_garden_2 = NPC(False, 'Работник "ГАМА"', True, {0: garden}, 3, 'Johan Ishibashi')
surgeon_medical_center = NPC(False, 'Хирург', True, {0: medical_center, 1: operation_room}, 9, 'Saita Shinoda')
mechanic_garage = NPC(False, 'Механик', True, {0: garage}, 1, 'Tomochika Honma')
yoga_coach = NPC(False, 'Инструктор по йоге', True, {0: garage, 1: 'Спальня персонала'}, 1, 'J. Brooke')
chef_1 = NPC(False, 'Шеф', True, {0: kitchen}, 7, 'Ikkei Tsutsui')
chef_2 = NPC(False, 'Шеф', True, {0: kitchen}, 8, 'Minao Morishita')
morgue_worker_1 = NPC(False, 'Работник морга', True, {0: morgue}, 6, 'Katshi Ito')
morgue_worker_2 = NPC(False, 'Работник морга', True, {0: morgue}, 7, 'Tenri Shinosaki')
morgue_worker_3 = NPC(False, 'Работник морга', True, {0: morgue}, 5, 'Shoudai Kurosawa')
surgeon_operation_room_1 = NPC(False, 'Хирург', True, {0: operation_room}, 7, 'Kii Ine')
surgeon_operation_room_2 = NPC(False, 'Хирург', True, {0: operation_room}, 9, 'Emiri Nimiya')
surgeon_operation_room_3 = NPC(False, 'Хирург', True, {0: operation_room}, 8, 'Gakushi Yamaoka')
chief_surgeon = NPC(False, 'Главный хирург', True, {0: operation_room}, 7, 'Nicholas Laurent')
pilot = NPC(False, 'Пилот', True, {0: pilot_room}, 3, 'Nails')
director = NPC(False, 'Директор клиники', True, {0: hall, 1: garden, 2: hall, 3: medical_center, 4: medical_center_level_2, 5: director_room, 6: director_room, 7:director_room, 8: medical_center_level_2, 9: medical_center, 10: hall}, 7, 'Akira Nakamura')

hokkaido_npcs = [guard_cable_car_1, 
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
        guard_target_suite_6,
        guard_target_suite_5,
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
        target_guard_1,
        target_guard_2,
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