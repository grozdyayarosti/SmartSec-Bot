from typing import Any
import telebot
from telebot import types
import time

from db_connection import Database
from constants import TELEGRAM_BOT_TOKEN, TESTING_QUESTION_COUNT


# TODO защита от игнора
class TGTestingBot(telebot.TeleBot):
    def __init__(self):
        super().__init__(TELEGRAM_BOT_TOKEN)
        # TODO завести БД под эту историю
        self.active_quizzes : dict[str: types.Poll] = dict()
        self.testing_quizzes = dict()

    def start_bot(self, message: types.Message):
        # TODO регистрация пользователя
        # TODO добавить смайлики на сообщения
        self.send_message(
            message.chat.id,
            f"Я - автоматическая система тестирования <b>SmartSec Testing</b>.\n"
            f"",
            parse_mode='html',
            # Вывод альтернативной клавиатуры для выбора предложенных ответов
            # (в зависимости от параметра будут предложены разные варианты в клавиатуре)
            # reply_markup=markUpSave('start')
        )

        with Database() as db:
            is_completed = db.check_testing_completeness(message.chat.username)
            total_count, correct_count = db.get_user_statistics(message.chat.username)

        if is_completed:
            self.send_message(
                message.chat.id,
                f"Вы прошли тестирование! Ожидайте регулярных вопросов...\n\n"
                f"📊 Ваша статистика:\n<b>✍️ {correct_count}/{total_count} "
                f"({100 * round(correct_count/total_count, 4)})%</b>",
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
                f"({round(100 * correct_count/total_count, 2)}%)</b>",
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

        self.testing_quizzes[user_name] = {"question_number": 1}
        # TODO счетчик результатов (то есть оценка прохождения тестирования)
        # варианты:
        # 1. хранение состояния в справочнике и юз handle_poll_answer
        # 2. хранение состояния в справочнике и юз register_next_step_handler_by_chat_id
        # 3. прикрутить коллбек
        # 4. через Машина состояний (FSM)
        self.send_quiz(user_id,user_name)
        # time.sleep(5)

        # self.end_testing(user_id, user_name)


    def end_testing(self, user_id, user_name):
        self.send_message(user_id,f"Тестирование окончено!")
        with Database() as db:
            is_correct = db.check_last_answer()
            db.set_testing_completed(is_correct, user_name)

        result_text = "Вы успешно сдали тестирование!" if is_correct else "Вы провалили тестирование!"
        self.send_message(
            user_id,
            result_text,
            parse_mode='html')


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
        # TODO перемешивание вариантов ответов
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
        if self.testing_quizzes.get(user_name):
            self.testing_quizzes[user_name].update({'poll': poll_message.poll})

    def check_quiz_result(self, quiz_answer: types.PollAnswer):
        trigger_poll = self.active_quizzes.pop(quiz_answer.user.username)
        is_correct_answer = trigger_poll.correct_option_id == quiz_answer.option_ids[0]
        poll_question = trigger_poll.question
        user_name = quiz_answer.user.username
        with Database() as db:
            db.send_testing_results_to_db(
                user_name,
                poll_question,
                is_correct_answer
            )
        self.send_message(
            quiz_answer.user.id,
            "Ответ записан"
        )

        if self.testing_quizzes.get(user_name):
            current_question_number = self.testing_quizzes[user_name]['question_number']
            if current_question_number < TESTING_QUESTION_COUNT:
                # TODO организовать неповторяемость вопросов
                self.testing_quizzes[user_name].update({'question_number': current_question_number + 1})
                self.send_quiz(quiz_answer.user.id, user_name)
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