import random
import threading
from typing import Any
import telebot
from telebot import types
# import time

from db_connection import Database
from constants import TELEGRAM_BOT_TOKEN, TESTING_QUESTION_COUNT, TESTING_COMPLETE_RESULT, \
    ANSWER_TO_TESTING_QUESTION_TIME, REGULAR_COMPLETE_RESULT, MY_ID


# TODO добавить смайлики на сообщения

class TGTestingBot(telebot.TeleBot):
    def __init__(self):
        super().__init__(TELEGRAM_BOT_TOKEN)
        self.scheduler = None

    def start_bot(self, message: types.Message):
        user_name = message.chat.username if message.chat.username is not None else message.chat.id
        with Database() as db:
            is_registered = db.user_registration(user_name, message.chat.id)
            is_completed = db.check_testing_completeness(user_name)
            total_count, correct_count = db.get_user_statistics(user_name)
        total_percentages = 100 * correct_count / (total_count if total_count > 0 else 1)

        if is_registered:
            start_text = (f"👋🏻 Привет! Я - автоматическая система тестирования\n<b>SmartSec Testing</b>.\n\n"
                          f"❗️ <b>Вам необходимо пройти тестирование</b>\n"
                          f"<b>Для старта нажмите:\n<i>«Начать тестирование»</i></b>\n\n"
                          f"Тестирование состоит из 50 вопросов.\n"
                          f"У вас есть {ANSWER_TO_TESTING_QUESTION_TIME} секунд на ответ.\n"
                          f"📩 Если вы прошли тестирование, то <b>будете получать регулярные вопросы "
                          f"от бота раз в 3 суток</b>.\n\n"
                          f"📊 Спустя месяц при статистике ответов на регулярные вопросы ниже 60% "
                          f"<b>необходимо заново пройти тестирование</b>.\n"
                          f"Используйте команду <b>/start</b> для получения своей статистики "
                          f"и начала тестирования.\n\n"
                          f"Желаем успехов!")
            self.send_message(message.chat.id, start_text, parse_mode='html')

        if is_completed:
            self.send_message(
                message.chat.id,
                f"Вы уже прошли тестирование!\n"
                f"Ожидайте регулярных вопросов...\n\n"
                f"📊 Ваша статистика по регулярным вопросам:\n<b>✍️ {correct_count}/{total_count} "
                f"({float(f'{total_percentages:.2f}')})%</b>",
                parse_mode='html')
        else:
            to_testing_btn = types.InlineKeyboardButton(text='Начать тестирование',
                                                     callback_data='go_testing')  # Добавление кнопки
            to_testing_markup = types.InlineKeyboardMarkup(row_width=1).add(to_testing_btn)
            self.send_message(
                message.chat.id,
                f"Вы ещё не прошли тестирование!\n\n"
                f"📊 Ваша статистика по регулярным вопросам:\n<b>✍️ {correct_count}/{total_count} "
                f"({float(f'{total_percentages:.2f}')}%)</b>",
                parse_mode='html',
                reply_markup=to_testing_markup)

    def start_testing(self, callback: telebot.types.CallbackQuery, scheduler):
        self.scheduler = scheduler
        self.scheduler.pause_scheduler()
        user_id = callback.from_user.id
        user_name = callback.from_user.username if callback.from_user.username is not None else user_id

        self.edit_message_reply_markup(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=None
        )
        self.send_message(user_id,f"Тестирование начато!")

        with Database() as db:
            db.clear_user_testing_statistics(user_name)
        self.send_quiz(user_id, user_name, True)

    def end_testing(self, user_id: int, user_name: str):
        self.send_message(user_id,f"Тестирование окончено!")
        with Database() as db:
            correct_answers_count = db.calc_user_testing_result(user_name)
            result = round(correct_answers_count / TESTING_QUESTION_COUNT, 4)
            is_complete = result >= TESTING_COMPLETE_RESULT
            db.set_testing_completed(is_complete, user_name)
            # db.clear_user_results(user_name)
        result_text = "Вы успешно сдали тестирование!" if is_complete else "Вы провалили тестирование!"
        self.send_message(
            user_id,
            result_text,
            parse_mode='html')
        self.scheduler.resume_scheduler()

    def recalculating_statistics(self, user_id: int, user_name: str):
        with Database() as db:
            total_count, correct_count = db.get_user_statistics(user_name)
        if total_count >= 10:
            with Database() as db:
                is_completed = (correct_count / total_count) >= REGULAR_COMPLETE_RESULT
                is_loss_completeness = db.checking_user_loss_completeness(is_completed, user_name)
                if is_loss_completeness:
                    db.set_testing_completed(is_completed, user_name)
                    db.clear_user_regular_questions(user_name)
                    db.clear_user_results(user_name)
                    self.send_message(user_id,
                        f"⚠️⚠️⚠️\n"
                        f"Ваша статистика правильных ответов упала ниже 60% и будет сброшена!!!\n"
                        f"Необходимо заново пройти тестирование")

    def send_quiz(self, user_id: int, user_name: str, is_user_testing: bool):
        with Database() as db:
            question_data    = db.get_quiz_question_data(user_name, is_user_testing)
            question_id      = question_data["question_id"]
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
                db.add_question_to_user_testing_statistics(user_name,
                                                           question_id,
                                                           poll_message.poll.correct_option_id,
                                                           poll_message.poll.id)
            # time.sleep(ANSWER_TO_TESTING_QUESTION_TIME)
            testing_question_timer = threading.Timer(ANSWER_TO_TESTING_QUESTION_TIME,
                                                     self.handle_testing_timeout,
                                                     args=[user_name, user_id, question_id])
            testing_question_timer.start()
        else:
            with Database() as db:
                last_regular_question_data = db.get_user_regular_question_data(user_name)
                is_answering_last_question = db.check_user_answering_last_reqular_question(user_name)
            if not is_answering_last_question:
                self.send_empty_reqular_answer(user_name,
                                               user_id,
                                               last_regular_question_data["question_text"],
                                               last_regular_question_data["poll_message_id"])
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
                db.add_question_to_buffer_statistics(user_name,
                                                     poll_message.poll.correct_option_id,
                                                     question_data["question_text"],
                                                     poll_message.poll.id,
                                                     poll_message.message_id)

    def handle_testing_timeout(self, user_name: str, user_id: int, question_id: int):
        with Database() as db:
            is_answering = db.check_answer_existing(user_name, question_id)
        if not is_answering:
            self.send_empty_testing_answer(user_name, user_id, question_id)

    def send_empty_testing_answer(self, user_name: str, user_id: int, question_id: int):
        with Database() as db:
            db.set_answer_to_testing_statistics(user_name, question_id, False)
            current_question_number = db.get_user_testing_question_number(user_name)
        self.send_message(
            user_id,
            "❌ Ответ записан (время истекло)"
        )
        if current_question_number < TESTING_QUESTION_COUNT:
            self.send_quiz(user_id, user_name, True)
        else:
            self.end_testing(user_id, user_name)

    def send_empty_reqular_answer(self, user_name: str, user_id: int, question_text: str, poll_message_id: int):
        if poll_message_id is not None:
            self.stop_poll(
                chat_id=user_id,
                message_id=poll_message_id
            )
        with Database() as db:
            db.send_user_regular_results_to_db(
                user_name,
                question_text,
                False
            )
        self.send_message(
            user_id,
            "❌ Ответ записан (время истекло)"
        )
        self.recalculating_statistics(user_id, user_name)

    def check_quiz_result(self, quiz_answer: types.PollAnswer):
        user_id = quiz_answer.user.id
        user_name = quiz_answer.user.username if quiz_answer.user.username is not None else user_id
        user_answer_id = quiz_answer.option_ids[0]

        with Database() as db:
            is_user_testing = db.check_user_testing(user_name)
            if is_user_testing:
                correct_answer_id, poll_question_id = db.get_user_testing_question_data(
                    user_name,
                    quiz_answer.poll_id)
                is_correct_answer = correct_answer_id == user_answer_id
                current_question_number = db.get_user_testing_question_number(user_name)
            else:
                last_regular_question_data = db.get_user_regular_question_data(user_name)
                db.clear_user_regular_questions(user_name)
                is_correct_answer = last_regular_question_data["correct_option_id"] == user_answer_id
                db.send_user_regular_results_to_db(
                    user_name,
                    last_regular_question_data["question_text"],
                    is_correct_answer
                )
        self.send_message(
            user_id,
            ("✅" if is_correct_answer else "❌") + " Ответ записан"
        )

        if is_user_testing:
            with Database() as db:
                db.set_answer_to_testing_statistics(user_name, poll_question_id, is_correct_answer)
            if current_question_number < TESTING_QUESTION_COUNT:
                self.send_quiz(user_id, user_name, True)
            else:
                self.end_testing(user_id, user_name)
        else:
            self.recalculating_statistics(user_id, user_name)

    # FIXME отправлять всем пользователям
    def testing_is_not_available(self):
        self.send_message(
            MY_ID,
            "❌ Тестирование недоступно ❌"
        )

    @staticmethod
    def parse_answers_data(answers_data: list[tuple[Any, ...]]) -> dict:
        answers_text_list = []
        correct_answer = None
        for index, (answer, is_correct) in enumerate(answers_data):
            answers_text_list.append(answer)
            if is_correct:
                correct_answer = index
        return {"answers_text_list": answers_text_list, "correct_answer": correct_answer}
