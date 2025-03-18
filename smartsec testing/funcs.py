import telebot
from telebot import types
import time

from database_connection import DatabaseCursor
from constants import TELEGRAM_BOT_TOKEN

class TGTestingBot(telebot.TeleBot):
    def __init__(self):
        super().__init__(TELEGRAM_BOT_TOKEN)
        self.active_quizzes : dict[str:types.Poll] = dict()

    def start_message(self, message):
        self.send_message(
            message.chat.id,
            f"Я - <b>автоматическая система тестирования</b>.",
            parse_mode='html',
            # Вывод альтернативной клавиатуры для выбора предложенных ответов
            # (в зависимости от параметра будут предложены разные варианты в клавиатуре)
            # reply_markup=markUpSave('start')
        )

    def send_quiz(self, message):
        if message.chat.type == 'private':
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

                    poll_message = self.send_poll(
                        message.chat.id,
                        question_text,
                        answers_text,
                        type='quiz',
                        is_anonymous=False,
                        correct_option_id=correct_answer,
                        explanation='Это в первую очередь обеспечение доступа к информации только авторизованным лицам'
                    )
                    self.active_quizzes[message.chat.username] = poll_message.poll
                case _:
                    self.send_message(
                        message.chat.id,
                        "Жди теста"
                    )

    def check_quiz_result(self, quiz_answer):
        checked_poll = self.active_quizzes.get(quiz_answer.user.username, dict())
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
            self.send_message(
                quiz_answer.user.id,
                "Ответ записан"
            )
            del self.active_quizzes[quiz_answer.user.username]

def delete_ReplyKeyboard(msg, bot):
    delete_keyboard_msg = bot.send_message(msg.chat.id, 'Пожалуйста, подождите . . . ',
                                           reply_markup=types.ReplyKeyboardRemove())
    time.sleep(0.5)
    bot.delete_message(msg.chat.id, delete_keyboard_msg.id)
