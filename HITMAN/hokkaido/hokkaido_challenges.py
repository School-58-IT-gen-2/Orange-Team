from HITMAN.model.challenges import Challenge


smoking_kills = Challenge('Курение убивает', 'Убейте Юки Ямадзаки во время того, как она курит сигареты.', False)
stretch = Challenge('Хорошая растяжка', 'Убейте Юки Ямадзаки, подстроив несчастный случай во время занятий йогой.', False)
personal_goodbye = Challenge('Личное прощание', 'Убейте Эриха Содерса выстрелом из пистолета.', False)
no_smoking = Challenge('Не курить!', 'Положите пачку сигарет в номере Юки Ямадзаки.', False)
human_error = Challenge('(Не) врачебная ошибка', 'Убейте Эриха Содерса, самостоятельно проведя операцию.', False)
suit_only = Challenge('Только костюм', '1. Завершите миссию\n2. Сделайте это в маскировке VIP - пациента', False)
silent_assasin = Challenge('Бесшумный убийца', '1. Завершите миссию\n2. Убивайте только цели\n3. Ни одно тело не должно быть обнаружено\n 4. Не дайте себя заметить', False)
sauna_assasination = Challenge('Убийство в парилке', 'Убейте Юки Ямадзаки, заперев ее в парилке.', False)
sushi = Challenge('Приятного аппетита', 'Отравите роллы Юки Ямадзаки ядом рыбы фугу.', False)
heartless = Challenge('Бессердечный', 'Повредите сердце Эриха содерса.', False)
silent_assasin_suit_only = Challenge('Бесшумный убйца. Только костюм.', '1. Завершите миссию\n2. Убивайте только цели\n3. Ни одно тело не должно быть обнаружено\n 4. Не дайте себя заметить\n5. Сделайте это в маскировке VIP - пациента', False)
no_evidence = Challenge('Без улик', 'Завершите миссию, не давая обнаружить тела.', False)
ghost_machine = Challenge('Призрак в машине', 'Повредите сервера KAI.', False)
straight_shot = Challenge('Точный выстрел', 'Убейте цель выстрелом из пистолета.', False)
hold_hair = Challenge('Подержи волосы', 'Убейте цель, утопив ее.', False)
piano_man = Challenge('Пианист', 'Убейте цель при помощи удавки.', False)
hurt_oneself = Challenge('Так можно и пораниться', 'Убейте цель, подстроив несчастный случай.', False)
tasteless = Challenge('Без вкуса, без следа', 'Устраните цель, отравив ее.', False)
master_assasin = Challenge('Мастер-убийца', f'1. Выполните {straight_shot.name}\n2. Выполните {hold_hair.name}\n3. Выполните {piano_man.name}\n4. Выполните {hurt_oneself.name}\n5. Выполните {tasteless.name}', False)

hokkaido_challenges = [smoking_kills, stretch, personal_goodbye, no_smoking, human_error, suit_only, silent_assasin, sauna_assasination, sushi, heartless, silent_assasin_suit_only, no_evidence, ghost_machine, straight_shot, hold_hair, piano_man, hurt_oneself, tasteless, master_assasin]