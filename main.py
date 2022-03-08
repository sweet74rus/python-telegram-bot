import telebot

bot = telebot.TeleBot('5133726676:AAFYkB4pOCGEaPKmXAQ3o3hFW4t8xDsHLj8')


@bot.message_handler(commands=['start', 'help'])
def welcome(message):
    bot.reply_to(message, 'Привет, меня зовут Боб. Чем я могу помочь?')


name = ''
surname = ''
age = 0


@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/reg':
        bot.send_message(message.from_user.id, 'Как тебя зовут?')
        bot.register_next_step_handler(message, get_name)
    else:
        bot.send_message(message.from_user.id, 'Напиши /reg')


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
        bot.send_message(message.from_user.id, f'Тебе {age} {get_true_age_word()}, '
                                               f'тебя зовут {name}, '
                                               f' твоя фамилия {surname}')


def get_true_age_word():
    god = '1234'
    word = 'лет'

    if str(age)[-1] in god and str(age)[0] != '1':
        word = 'год'

    return word

bot.infinity_polling()
