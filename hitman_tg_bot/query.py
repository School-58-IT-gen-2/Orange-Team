from model.locations_values import *

def is_skip(query):
    return 'SKIP' in query

def is_begin(query):
    return query == 'ТПН' or query == 'ХоккЯП' or query == 'СТ'

def is_spawn_player(query):
    return 'НАЧИ' in query

def is_knock_jason_portman(query):
    return 'УДП' in query

def is_choose_equipment(query):
    return 'choose_pistol' in query or 'choose_item_1' in query or 'choose_item_2' in query or 'CSL' in query or query == 'Выбор снаряжения'

def is_basic_move(query):
    return 'basic_move' in query

def is_safe_move(query):
    return 'SM' in query

def is_npc_attack(query):
    return "НПД" in query

def is_no_disguise_move(query):
    return 'ПРТ' in query

def is_disguise_menu(query):
    return 'МАСК' in query

def is_change_disguise(query):
    return 'МСК' in query

def is_choose_legal_item(query):
    if query[:-4] in list(items.keys()):
        return items[query[:-4]].legal
    return False

def is_choose_illegal_item(query):
    if query[:-4] in list(items.keys()):
        if items[query[:-4]].legal == False:
            return True
    return False

def is_choose_weapon(query):
    return 'WP' in query

def is_choose_weapon_action(query):
    return 'CWA' in query

def is_interact_lethal(query):
    return 'ITR' in query and ('летально' in query or 'Выстрелить' in query or 'Задушить' in query)

def is_interact_non_lethal(query):
    return 'ITR' in query and ('летально' in query or 'Выстрелить' in query or 'Задушить' in query or 'Использовать' in query or 'Бросить для отвлечения' in query) == False

def is_distract(query):
    return 'Бросить для отвлечения' in query

def is_kill(query):
    return 'KILL' in query

def is_knock_out(query):
    return 'KNOCK' in query

def is_distract_npc(query):
    return 'DIS' in query

def is_confirm_kill(query):
    return 'con_kill' in query

def is_confirm_knock(query):
    return 'con_knock' in query

def is_confirm_distract_kill(query):
    return 'CDKL' in query

def is_confirm_distract_knock(query):
    return 'CDKN' in query

def is_use(query):
    return 'Использовать' in query

def is_destroy_heart_2(query):
    return 'DH1' in query

def is_destroy_heart(query):
    return 'DH2' in query

def is_yoga_kill_2(query):
    return query == 'ТЮЯ'

def is_surgeon_knock_out_2(query):
    return 'УГХ' in query

def is_sushi_kill_2(query):
    return 'ОСЮ' in query

def is_private_meeting_kill(query):
    return query == 'ЗЦУ' or query == 'ЗЦИП'
