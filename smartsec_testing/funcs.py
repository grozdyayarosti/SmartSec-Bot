from typing import Any
import telebot
from telebot import types
import time

from db_connection import Database
from constants import TELEGRAM_BOT_TOKEN

class TGTestingBot(telebot.TeleBot):
    def __init__(self):
        super().__init__(TELEGRAM_BOT_TOKEN)
        self.active_quizzes : dict[str: types.Poll] = dict()

    def start_message(self, message: types.Message):
        self.send_message(
            message.chat.id,
            f"Я - автоматическая система тестирования.",
            parse_mode='html',
            # Вывод альтернативной клавиатуры для выбора предложенных ответов
            # (в зависимости от параметра будут предложены разные варианты в клавиатуре)
            # reply_markup=markUpSave('start')
        )

    def user_request_responding(self, message: types.Message):
        if message.chat.type == 'private':
            match message.text:
                case '1':
                    self.send_quiz(
                        message.chat.id,
                        message.chat.username)
                case _:
                    self.send_message(
                        message.chat.id,
                        "Жди теста"
                    )

    def send_quiz(self, user_id: int, user_name: str):
        with Database() as db:
            question_data = db.get_quiz_question_data()
            question_id = question_data["question_id"]
            raw_answers_data = db.get_question_answers(question_id)

        answers_data = self.parse_answers_data(raw_answers_data)

        poll_message = self.send_poll(
            chat_id=user_id,
            question=question_data["question_text"],
            options=answers_data["answers_text_list"],
            type='quiz',
            is_anonymous=False,
            correct_option_id=answers_data["correct_answer"],
            explanation=question_data["explanation"]
        )
        self.active_quizzes[user_name] = poll_message.poll

    def check_quiz_result(self, quiz_answer: types.PollAnswer):
        trigger_poll = self.active_quizzes.pop(quiz_answer.user.username)
        is_correct_answer = trigger_poll.correct_option_id == quiz_answer.option_ids[0]
        poll_question = trigger_poll.question
        username = quiz_answer.user.username
        with Database() as db:
            db.send_testing_results_to_db(
                username,
                poll_question,
                is_correct_answer
            )
        self.send_message(
            quiz_answer.user.id,
            "Ответ записан"
        )

    def delete_ReplyKeyboard(self, msg: types.Message):
        delete_keyboard_msg = self.send_message(msg.chat.id, 'Пожалуйста, подождите . . . ',
                                               reply_markup=types.ReplyKeyboardRemove())
        time.sleep(0.5)
        self.delete_message(msg.chat.id, delete_keyboard_msg.id)

    @staticmethod
    def parse_answers_data(answers_data: list[tuple[Any, ...]]) -> dict:
        answers_text_list = []
        correct_answer = None
        for index, (answer, is_correct) in enumerate(answers_data):
            answers_text_list.append(answer)
            if is_correct:
                correct_answer = index
        return {"answers_text_list": answers_text_list, "correct_answer": correct_answer}