import telebot
import psycopg2

from constants import TELEGRAM_BOT_TOKEN, PG_DBNAME, PG_USER, PG_PASSWORD, PG_HOST, PG_PORT
from funcs import delete_ReplyKeyboard

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

                conn = psycopg2.connect(
                    dbname=PG_DBNAME,
                    user=PG_USER,
                    password=PG_PASSWORD,
                    host=PG_HOST,
                    port=PG_PORT
                )
                cur = conn.cursor()
                cur.execute("SELECT * FROM questions;")
                question = cur.fetchone()
                question_id = question[0]
                question_text = question[1]
                cur.execute(
                    f"""
                        SELECT a.text, ar.is_correct 
                          FROM answer_results ar left join answers a 
                            ON ar.answer_id = a.id
                         WHERE ar.question_id = {question_id};
                    """
                )
                answers = cur.fetchall()
                answers_text = []
                correct_index = 0
                for index, (answer, is_correct) in enumerate(answers):
                    answers_text.append(answer)
                    if is_correct:
                        correct_index = index

                conn.commit()
                cur.close()
                conn.close()

                bot.send_poll(
                    message.chat.id,
                    question_text,
                    answers_text,
                    type='quiz',
                    correct_option_id=correct_index,
                    explanation='Это в первую очередь обеспечение доступа к информации только авторизованным лицам'
                )
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
