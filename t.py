import telebot
from telebot import types
import sys
import random
enemy_health = 100
enemies = ["a",'b']
playerinventory = ['pistol']
buttons = ['A', 'D', 'W', 'X', 'S', 'Q', 'E', 'Z']
bot = telebot.TeleBot('6940674100:AAGD6JEpmnSsVWevH28jwV5wMikyeszH2m8')
@bot.message_handler(commands=['start'])
def welcome(message):
    mesg = bot.send_message(message.chat.id,'Please send me message')
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Сайт Хабр", url='https://habr.com/ru/all/')
    markup.add(button1)
    bot.register_next_step_handler(mesg,test)


def test(message):
    bot.send_message(message.chat.id,'You send me message')

bot.polling(none_stop=True, interval=0) #обязательная для работы бота часть