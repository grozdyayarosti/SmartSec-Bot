import random
from typing import Any
import telebot
from telebot import types
import time

from db_connection import Database
from constants import TELEGRAM_BOT_TOKEN, TESTING_QUESTION_COUNT, TESTING_COMPLETE_RESULT, \
    ANSWER_TO_TESTING_QUESTION_TIME


# TODO защита от игнора регулярных вопросов
# TODO добавить смайлики на сообщения
# TODO вычисление максимально старого вопроса для регулярной отправки
# FIXME (после игнора и по дефолту "Ответ записан" мгновенный, после успевания за 10 сек "Ответ записан" приходится ждать 10 сек).
#  Возможно придётся time.sleep() вывести в многопоток или асинк
class TGTestingBot(telebot.TeleBot):
    def __init__(self):
        super().__init__(TELEGRAM_BOT_TOKEN)

    def start_bot(self, message: types.Message):

        with Database() as db:
            db.user_registration(message.chat.username)
            is_completed = db.check_testing_completeness(message.chat.username)
            total_count, correct_count = db.get_user_statistics(message.chat.username)

        self.send_message(
            message.chat.id,
            f"Я - автоматическая система тестирования <b>SmartSec Testing</b>.\n"
            f"",
            parse_mode='html'
        )

        if is_completed:
            self.send_message(
                message.chat.id,
                f"Вы прошли тестирование! Ожидайте регулярных вопросов...\n\n"
                f"📊 Ваша статистика:\n<b>✍️ {correct_count}/{total_count} "
                f"({float(f'{100 * correct_count/total_count:.2f}')})%</b>",
                parse_mode='html')
        else:
            to_testing_btn = types.InlineKeyboardButton(text='Начать тестирование',
                                                     callback_data='go_testing')  # Добавление кнопки
            to_testing_markup = types.InlineKeyboardMarkup(row_width=1).add(to_testing_btn)
            # to_home_markup.add(to_home_btn)
            self.send_message(
                message.chat.id,
                f"Вы ещё не прошли тестирование!\n\n"
                f"📊 Ваша статистика:\n<b>✍️ {correct_count}/{total_count} "
                f"({float(f'{100 * correct_count/total_count:.2f}')}%)</b>",
                parse_mode='html',
                reply_markup=to_testing_markup)

    def start_testing(self, callback: telebot.types.CallbackQuery):
        user_id = callback.from_user.id
        user_name = callback.from_user.username
        self.edit_message_reply_markup(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=None
        )
        self.send_message(user_id,f"Тестирование начато!")

        with Database() as db:
            db.clear_user_testing_statistics(user_name)
        self.send_quiz(user_id, user_name, True)

    def end_testing(self, user_id, user_name):
        self.send_message(user_id,f"Тестирование окончено!")
        with Database() as db:
            correct_answers_count = db.calc_user_testing_result(user_name)
            result = round(correct_answers_count / TESTING_QUESTION_COUNT, 4)
            is_complete = result >= TESTING_COMPLETE_RESULT
            db.set_testing_completed(is_complete, user_name)
        result_text = "Вы успешно сдали тестирование!" if is_complete else "Вы провалили тестирование!"
        self.send_message(
            user_id,
            result_text,
            parse_mode='html')

    def send_quiz(self, user_id: int, user_name: str, is_user_testing: bool):
        with Database() as db:
            question_data = db.get_quiz_question_data(is_user_testing)
            question_id = question_data["question_id"]
            raw_answers_data = db.get_question_answers(question_id)

        # Перемешивание вариантов ответа
        random.shuffle(raw_answers_data)
        answers_data = self.parse_answers_data(raw_answers_data)

        if is_user_testing:
            poll_message = self.send_poll(
                chat_id=user_id,
                question=question_data["question_text"],
                options=answers_data["answers_text_list"],
                type='quiz',
                is_anonymous=False,
                correct_option_id=answers_data["correct_answer"],
                explanation=question_data["explanation"],
                open_period=ANSWER_TO_TESTING_QUESTION_TIME
            )
            with Database() as db:
                db.add_question_to_user_testing_statistics(user_name, question_id)
                db.add_question_track(user_name,
                                      poll_message.poll.correct_option_id,
                                      question_data["question_text"],
                                      poll_message.poll.id)
                time.sleep(ANSWER_TO_TESTING_QUESTION_TIME)
                is_answering = db.check_answer_existing(user_name, question_id)
            if not is_answering:
                self.send_empty_testing_answer(user_name, user_id, question_data["question_text"])
        else:
            poll_message = self.send_poll(
                chat_id=user_id,
                question=question_data["question_text"],
                options=answers_data["answers_text_list"],
                type='quiz',
                is_anonymous=False,
                correct_option_id=answers_data["correct_answer"],
                explanation=question_data["explanation"]
            )
            with Database() as db:
                db.add_question_track(user_name,
                                      poll_message.poll.correct_option_id,
                                      question_data["question_text"],
                                      poll_message.poll.id)

    def send_empty_testing_answer(self, user_name: str, user_id: int, poll_question: str):
        with Database() as db:
            db.set_answer_to_testing_statistics(user_name, poll_question, False)
            current_question_number = db.get_user_testing_question_number(user_name)
        self.send_message(
            user_id,
            "❌ Ответ записан"
        )
        if current_question_number < TESTING_QUESTION_COUNT:
            self.send_quiz(user_id, user_name, True)
        else:
            self.end_testing(user_id, user_name)

    def check_quiz_result(self, quiz_answer: types.PollAnswer):
        user_name = quiz_answer.user.username
        with Database() as db:
            correct_option_id, poll_question = db.get_user_active_question_data(user_name, quiz_answer.poll_id)
            is_correct_answer = correct_option_id == quiz_answer.option_ids[0]
            is_user_testing = db.check_user_testing(user_name)
            if is_user_testing:
                current_question_number = db.get_user_testing_question_number(user_name)
            else:
                db.send_testing_results_to_db(
                    user_name,
                    poll_question,
                    is_correct_answer
                )
        self.send_message(
            quiz_answer.user.id,
            ("✅" if is_correct_answer else "❌") + " Ответ записан"
        )

        if is_user_testing:
            with Database() as db:
                db.set_answer_to_testing_statistics(user_name, poll_question, is_correct_answer)
            if current_question_number < TESTING_QUESTION_COUNT:
                self.send_quiz(quiz_answer.user.id, user_name, True)
            else:
                self.end_testing(quiz_answer.user.id, quiz_answer.user.username)


    @staticmethod
    def parse_answers_data(answers_data: list[tuple[Any, ...]]) -> dict:
        answers_text_list = []
        correct_answer = None
        for index, (answer, is_correct) in enumerate(answers_data):
            answers_text_list.append(answer)
            if is_correct:
                correct_answer = index
        return {"answers_text_list": answers_text_list, "correct_answer": correct_answer}
