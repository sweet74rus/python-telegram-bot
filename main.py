import telebot
import re
import requests
from telebot import types

bot = telebot.TeleBot('5133726676:AAFYkB4pOCGEaPKmXAQ3o3hFW4t8xDsHLj8')

holiday_url = 'https://holidayapi.com/v1/holidays?pretty&key=c2475528-0e37-4d01-acaf-5192189a7adb&country=RU&language=RU'
holiday_token = 'c2475528-0e37-4d01-acaf-5192189a7adb'


@bot.message_handler(commands=['start', 'help'])
def cmd_start(message):
    keyboard = types.InlineKeyboardMarkup()
    button_reg = types.InlineKeyboardButton(text='Регистрация', callback_data='reg')
    keyboard.add(button_reg)
    button_holiday = types.InlineKeyboardButton(text='Праздники', callback_data='holiday')
    keyboard.add(button_holiday)
    question = 'Привет, меня зовут Боб. Чем я могу помочь?'
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'reg':
        bot.send_message(call.message.chat.id, 'Как тебя зовут?')
        bot.register_next_step_handler(call.message, get_name)
    elif call.data == 'holiday':
        bot.send_message(call.message.chat.id, 'Введи дату в таком формате: ДД-ММ-ГГГГ')
        bot.register_next_step_handler(call.message, get_holiday_data)


name = ''
surname = ''
age = 0


@bot.message_handler(content_types=['text'])
def start(message):
    bot.send_message(message.from_user.id, 'Введите /start.')


def get_holiday_data(message):
    a = re.match('([0-9]{1,2})-([0-9]{1,2})-([0-9]{4})', message.text)
    try:
        holiday_data = requests.get(holiday_url + f'&year=2021&month={a[2]}&day={a[1]}').json()
        bot.send_message(message.from_user.id, holiday_data['holidays'][0]['name'])
    except Exception:
        bot.send_message(message.from_user.id, 'В этот день нет праздника :(')


def get_name(message):
    global name
    name = message.text
    bot.send_message(message.from_user.id, 'Какая у тебя фамилия?')
    bot.register_next_step_handler(message, get_surname)


def get_surname(message):
    global surname
    surname = message.text
    bot.send_message(message.from_user.id, 'Сколько тебе лет?')
    bot.register_next_step_handler(message, get_age)


def get_age(message):
    global age
    while age <= 0:
        try:
            age = int(message.text)
        except Exception:
            bot.send_message(message.from_user.id, 'Цифрами пожалуйста')
        word = get_true_age_word()
        bot.send_message(message.from_user.id, f'Тебе {age} {word}, '
                                               f'тебя зовут {name}, '
                                               f' твоя фамилия {surname}?')


def get_true_age_word():
    god = '234'
    word = 'лет'
    a = str(age)

    if len(a) > 1:
        if str(age)[-1] in god and str(age)[0] != '1':
            word = 'года'
        elif str(age)[-1] == '1' and str(age)[0] != '1':
            word = 'год'
    else:
        if str(age) == '1':
            word = 'год'
        elif str(age) in god:
            word = 'года'

    return word


bot.infinity_polling()
