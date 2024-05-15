from hitman_tg_bot.model.hitman_adapter import HitmanAdapter


adapter = HitmanAdapter()

lst = list(adapter.get_by_id('users', 1648778328))

def create_locations_values(challenges, npcs, targets, events, locations, items, disguises):
    "Создание словаря с данными о локации"
    pass


def create_user(user_id: int):
    """Создание объекта класса информации о пользователе"""
    locations_values = {}
    saved_data = {}
    lst = list(adapter.get_by_id('users', user_id))[0]
    missions = ['hokkaido', 'ica']
    for j in range(6, len(lst), 3):
        saved_data[missions[(j - 6) // 3]] = {'challenges': lst[j], 'disguises': lst[j + 1], 'locations': lst[j + 2]}
    
    print(lst[5])
    print(saved_data)
    
create_user(1648778328)