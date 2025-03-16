import telebot
from telebot import types

from database_connection import DatabaseCursor
from constants import TELEGRAM_BOT_TOKEN
from funcs import delete_ReplyKeyboard


bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
active_quizzes : dict[str:types.Poll] = dict()


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
                with DatabaseCursor() as cursor:
                    # TODO добавить поле explanation
                    cursor.execute("SELECT * FROM questions LIMIT 1;")
                    question = cursor.fetchone()
                    question_id = question[0]
                    question_text = question[1]
                    cursor.execute(
                        f"""
                            SELECT a.text, ar.is_correct 
                              FROM answer_results ar left join answers a 
                                ON ar.answer_id = a.id
                             WHERE ar.question_id = {question_id};
                        """
                    )
                    answers = cursor.fetchall()

                answers_text = []
                correct_answer = None
                for index, (answer, is_correct) in enumerate(answers):
                    answers_text.append(answer)
                    if is_correct:
                        correct_answer = index

                poll_message = bot.send_poll(
                    message.chat.id,
                    question_text,
                    answers_text,
                    type='quiz',
                    is_anonymous=False,
                    correct_option_id=correct_answer,
                    explanation='Это в первую очередь обеспечение доступа к информации только авторизованным лицам'
                )
                active_quizzes[message.chat.username] = poll_message.poll
            case _:
                bot.send_message(
                    message.chat.id,
                    "Жди теста"
                )


@bot.poll_answer_handler()
def handle_poll_answer(quiz_answer: types.PollAnswer):
    checked_poll = active_quizzes.get(quiz_answer.user.username, dict())
    if quiz_answer.poll_id == checked_poll.id:
        is_correct_answer = checked_poll.correct_option_id == quiz_answer.option_ids[0]
        poll_question = checked_poll.question
        # TODO добавить дату ответа на вопрос
        query = f'''
            INSERT INTO testing_results(user_id, question_id, is_correct_answer)
                VALUES(
                    (
                     SELECT id 
                       FROM public.users 
                      WHERE login = '{quiz_answer.user.username}'
                    ),
                    (
                     SELECT id 
                       FROM public.questions 
                      WHERE text = '{poll_question}'
                    ),
                    {is_correct_answer}
                )
        '''
        with DatabaseCursor() as cursor:
            cursor.execute(query)
        bot.send_message(
            quiz_answer.user.id,
            "Ответ записан"
        )
        del active_quizzes[quiz_answer.user.username]

print('BOT IS STARTED')
# Заставляет бота работать бесперебойно(пока на машине запущен код)
bot.polling(none_stop=True)
