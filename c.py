import telebot
from telebot import types
import sys
import random
enemy_health = 100
enemies = ["a",'b']
playerinventory = ['pistol']
buttons = ['A', 'D', 'W', 'X', 'S', 'Q', 'E', 'Z']
bot = telebot.TeleBot('6940674100:AAGD6JEpmnSsVWevH28jwV5wMikyeszH2m8')
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)


@bot.message_handler(commands=['start'])
def start(message):
    global current_message
    global kills
    global bodies
    global player_lvl
    global combat_count
    current_kills = 0
    current_bodies = 0
    enemies = ["a",'b']
    playerinventory = ['pistol']
    buttons = ['A', 'D', 'W', 'X', 'S', 'Q', 'E', 'Z']
    current_message = message
    response("Начался бой")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('1. Прятаться (5/10)')
    btn2 = types.KeyboardButton('2. Напасть')
    markup.add(btn1)
    print("добавляю кнопки")
    markup.add(btn2)
    request()
    x = request()
    print("b                                                                                                 b\n\n\n\n\n")
    print(x)
    print("b                                                                                                 b\n\n\n\n\n")
    if x.text == '1. Прятаться (5/10)':
        print("yes")
        bot.send_message(x.chat.id,'Ha Ha ha HA  (смех злодgjijguynея)')
        if random.randrange(1, 11) <= 5:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            response("Ваша маскировка раскрыта, при перемещении в любую локацию вас будут узнавать.")
            #player.compromised_disguises.append(player.disguise)
            return 0#player.disguise
        else:
            #with open('save_file.dat', 'wb') as f:
            #pickle.dump([smoking_kills, stretch, personal_goodbye, no_smoking, human_error, suit_only, silent_assasin, sauna_assasination, sushi, heartless, silent_assasin_suit_only, no_evidence, ghost_machine, straight_shot, hold_hair, piano_man, hurt_oneself, tasteless, master_assasin, player_lvl], f, protocol=2)
            response("Вы умерли. Миссия провалена.")
            sys.exit()

    elif current_message.text == '2. Напасть':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        bot.send_message(current_message.from_user.id, "Ваша мfctctvtcvggvdcgvefc", reply_markup=markup)
        for i in enemies:
            enemy_health = 100
            while enemy_health > 0:
                if 'pistol' in playerinventory or 'silenced_pistol' in playerinventory:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    btn = types.KeyboardButton('1. Использовать пистолет')
                    btn3 = types.KeyboardButton("2. Не использовать'")
                    markup.add(btn, btn3)
                    msg = bot.send_message(message.from_user.id, "пистолет?", reply_markup=markup)
                    bot.register_next_step_handler(msg, gun)
def gun(message):
    global enemy_health
    current_button = random.choice(buttons)
    crit = random.randint(1,11)
    if message.text == '1. Использовать пистолет':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in buttons:
            btn = types.KeyboardButton(i)
            markup.add(btn)
        msg = bot.message_handler(message.from_user.id, f'Нажимайте как можно быстрее: {current_button}', reply_markup=markup)
        bot.register_next_step_handler(msg,check)
def check(message):
    print("cheeeeck")
    global enemy_health
    current_button = random.choice(buttons)
    crit = random.randint(1,11)
    if message.text.upper() == current_button:
        if crit <= 5:
            enemy_health -= 50 
        else:
            enemy_health -= 25



def response(message):
    global current_message
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    bot.send_message(current_message.from_user.id, message, reply_markup=markup)




def request():
    global current_message
    print("nen z ,sk")
    mesg = bot.send_message(current_message.chat.id,'Ha Ha ha HA  (смех злодея)')
    bot.register_next_step_handler(mesg,requester)
    print(current_message)
    return current_message


@bot.message_handler(content_types=['text'])
def requester(message):
    global current_message
    current_message = message
    print("njn")
    print(current_message)
    return message
            
bot.polling(none_stop=True, interval=0) #обязательная для работы бота часть