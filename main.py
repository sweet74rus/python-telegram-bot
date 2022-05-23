import sqlite3
import telebot
import re
import requests
from telebot import types

conn = sqlite3.connect('Database/DeliveryDB.db', check_same_thread=False)
cursor = conn.cursor()

bot = telebot.TeleBot('TOKEN')

holiday_url = 'https://holidayapi.com/v1/holidays?pretty&key=c2475528-0e37-4d01-acaf-5192189a7adb&country=RU&language=RU'
holiday_token = 'c2475528-0e37-4d01-acaf-5192189a7adb'

order_sets = ['Coca-cola, Пицца 4 сыра', 'Lipton, Пепперони фреш', 'Pepsi, Мясная x 2']
order = ''

name = ''
surname = ''
age = 0


@bot.message_handler(commands=['start', 'help'])
def cmd_start(message):
    keyboard = types.InlineKeyboardMarkup()
    button_reg = types.InlineKeyboardButton(text='Регистрация', callback_data='reg')
    keyboard.add(button_reg)
    button_holiday = types.InlineKeyboardButton(text='Праздники', callback_data='holiday')
    keyboard.add(button_holiday)
    button_order = types.InlineKeyboardButton(text='Сделать заказ', callback_data='order')
    keyboard.add(button_order)
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
    elif call.data == 'yes':
        bot.send_message(call.message.chat.id, 'Вы успешно зарегистрированы!')
        write_table_user()
    elif call.data == 'order':
        keyboard = types.InlineKeyboardMarkup()
        i = 0
        for set in order_sets:
            keyboard.add(types.InlineKeyboardButton(text=f'{set}', callback_data='set' + str(i)))
            i += 1

        bot.send_message(call.message.chat.id, text='Выберите набор', reply_markup=keyboard)

    for i in range(len(order_sets)):
        if call.data == 'set' + str(i):
            bot.send_message(call.message.chat.id, f'Вы выбрали {order_sets[i]}, всё верно?')


@bot.message_handler(content_types=['text'])
def start(message):
    bot.send_message(message.from_user.id, 'Введите /start.')


# Получить название праздника
def get_holiday_data(message):
    a = re.match('([0-9]{1,2})-([0-9]{1,2})-([0-9]{4})', message.text)
    try:
        holiday_data = requests.get(holiday_url + f'&year=2021&month={a[2]}&day={a[1]}').json()
        bot.send_message(message.from_user.id, holiday_data['holidays'][0]['name'])
    except Exception:
        bot.send_message(message.from_user.id, 'В этот день нет праздника :(')


# Регистрация пользователя
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

        bot.register_next_step_handler(message, write_table_user)

        keyboard = types.InlineKeyboardMarkup()
        button_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
        keyboard.add(button_yes)
        button_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
        keyboard.add(button_no)
        question = f'Тебе {age} {word}, тебя зовут {name}, твоя фамилия {surname}?'
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


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


# Оформление заказа
def order_checkout(message):
    keyboard = types.InlineKeyboardMarkup()

    for set in order_sets:
        keyboard.add(types.InlineKeyboardButton(text=f'{set}', callback_data='set'))

    bot.send_message(message.from_user.id, text='Выберите набор', reply_markup=keyboard)


# Работа с таблицами базы данных
def write_table_user():
    db_table_val(name, surname, age)


def db_table_val(FirstName: str, LastName: str, Age: int):
    cursor.execute('INSERT INTO Users (FirstName, LastName, Age) VALUES (?, ?, ?)', (FirstName, LastName, Age))
    conn.commit()


bot.infinity_polling()
