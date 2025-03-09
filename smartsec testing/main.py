import telebot

from constants import TELEGRAM_BOT_TOKEN
from funcs import question_asking, delete_ReplyKeyboard

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


# Обработчик события при получении команды start
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(
        message.chat.id,
        f"Я - <b>автоматическая система тестирования</b>.",
        parse_mode='html',
        # Вывод альтернативной клавиатуры для выбора предложенных ответов
        # (в зависимости от параметра будут предложены разные варианты в клавиатуре)
        # reply_markup=markUpSave('start')
    )


#Обработчик события при получении текстового сообщения
@bot.message_handler(content_types=['text'])
def dialog(message):
    if message.chat.type == 'private':
        # Бот смотрит на полученные сообщения и в зависимости от них отвечает
        match message.text:
            case '1':
                bot.send_poll(
                    message.chat.id,
                    'Что такое конфиденциальность в контексте информационной безопасности?',
                    [
                        'Обеспечение доступа к информации только авторизованным лицам',
                        'Гарантия того, что информация всегда доступна.',
                        'Защита информации от повреждения.',
                        'Хранение данных в облачных сервисах.'
                    ],
                    type='quiz',
                    correct_option_id=0,
                    explanation='Это в первую очередь обеспечение доступа к информации только авторизованным лицам'
                )
            case '2':
                question_asking(message, bot)
            case _:
                bot.send_message(
                    message.chat.id,
                    "Жди теста"
                )


@bot.callback_query_handler(func=lambda callback: callback.data)
def check_callback_data(callback):
    if callback.data == 'right answer':
        delete_ReplyKeyboard(callback.message, bot)
        bot.send_message(callback.message.chat.id, 'Правильный ответ!')
    elif callback.data == 'wrong answer':
        delete_ReplyKeyboard(callback.message, bot)
        bot.send_message(callback.message.chat.id, 'Неправильный ответ!')

print('START')
# Заставляет бота работать бесперебойно(пока на машине запущен код)
bot.polling(none_stop=True)
