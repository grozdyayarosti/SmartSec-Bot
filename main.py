import telebot

from constants import TELEGRAM_BOT_TOKEN
from funcs import ask_mistral

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


# Обработчик события при получении команды start
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(
        message.chat.id,
        f"Доброго времени суток, {message.from_user.first_name}!\nЯ - <b>{bot.get_me().first_name}</b>.\nЧто вас интересует?",
        parse_mode='html',
        # Вывод альтернативной клавиатуры для выбора предложенных ответов(в зависимости от параметра будут предложены разные варианты в клавиатуре)
        reply_markup=markUpSave('start')
    )


#Обработчик события при получении текстового сообщения
@bot.message_handler(content_types=['text'])
def dialog(message):
    if message.chat.type == 'private':
        # Бот смотрит на полученные сообщения и в зависимости от них отвечает
        match message.text:
            case 'Вопрос по ИБ':
                mesg = bot.send_message(
                    message.chat.id,
                    "Задайте вопрос по ИБ",
                    reply_markup=markUpSave('empty')
                )
                # Метод, который ждёт ответного сообщения от пользователя и запускает метод recordName
                bot.register_next_step_handler(mesg, question_trigger)

            case _:
                bot.send_message(message.chat.id, "К сожалению, я могу вам ответить только на предложенные команды🥺")


def question_trigger(message):
    response = ask_mistral(message.text)
    mesg = bot.send_message(
        chat_id=message.chat.id,
        text=response,
        reply_markup=markUpSave('start')
    )


# Функция, которая в зависимости от полученного параметра создаёт markup - альетарнативную клавиатуру с разными вариантами ответа
def markUpSave(mode):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    if mode == 'start':
        item1 = telebot.types.KeyboardButton("Вопрос по ИБ")
        item2 = telebot.types.KeyboardButton("Заглушка")
        markup.add(item1, item2)

    elif mode == 'empty':
        markup = telebot.types.ReplyKeyboardRemove()

    return markup


# Заставляет бота работать бесперебойно(пока на машине запущен код)
bot.polling(none_stop=True)
