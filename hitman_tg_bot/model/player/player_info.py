import os
import pickle


player_lvl = [10]

#Загружает уровень игрока, если файл сохранения не пустой
if os.stat('./hitman/save_file.dat').st_size != 0:
    with open('./hitman/save_file.dat', 'rb') as f:
        challenges, player_lvl = pickle.load(f)

suspicion_count = [0]
kills = [0]
bodies = [0]
time = [0]
final = 0
combat_count = [0]
so = [0]