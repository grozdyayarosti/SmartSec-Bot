import random
from typing import Any

import psycopg2
import datetime

from constants import PG_DBNAME, PG_USER, PG_PASSWORD, PG_HOST, PG_PORT

# TODO переписать на ORM
class Database:
    def __init__(self):
        ...

    def __enter__(self):
        self.conn = psycopg2.connect(
            dbname=PG_DBNAME,
            user=PG_USER,
            password=PG_PASSWORD,
            host=PG_HOST,
            port=PG_PORT
        )
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()

    def check_testing_completeness(self, username: str) -> bool:
        self.cursor.execute(f"SELECT is_completed FROM users WHERE login='{username}';")
        is_completed = self.cursor.fetchone()
        return is_completed[0]

    def calc_user_testing_result(self, user_name: str):
        query = f"""
            select count(*) 
              from public.testing_track 
             where user_name='{user_name}'
               and is_correct = true
        """
        self.cursor.execute(query)
        correct_answers_count = self.cursor.fetchone()[0]
        self.clear_user_testing_track(user_name)
        return correct_answers_count

    def set_testing_completed(self, is_completed: bool, username: str):
        self.cursor.execute(f"""
            UPDATE users SET is_completed = {is_completed}
            WHERE
            id = (select id from users where login='{username}');
        """)

    def get_user_statistics(self, username: str) -> tuple:
        self.cursor.execute(f"""
            SELECT COUNT(*) AS total_count,
                   COUNT(*) FILTER(WHERE is_correct_answer) AS true_count
              FROM testing_results
             WHERE user_id = (SELECT id FROM users WHERE login='{username}');
        """)
        user_statistics = self.cursor.fetchone()
        return user_statistics


    def get_quiz_question_data(self, is_user_testing: bool) -> dict[str: str]:
        if is_user_testing:
            query = """
              SELECT id, text, is_required, explanation 
                FROM public.questions 
               WHERE is_required 
                 AND id NOT IN (SELECT question_id 
                                  FROM testing_track)
            """
            self.cursor.execute(query)
        else:
            random_number = random.randint(1, 3)
            self.cursor.execute(f"SELECT * FROM questions WHERE id={random_number}")
        question = self.cursor.fetchone()
        return {"question_id": question[0],
                "question_text": question[1],
                "is_required": question[2],
                "explanation": question[3]}

    def get_question_answers(self, question_id) -> list[tuple[Any, ...]]:
        self.cursor.execute(
            f"""
                SELECT a.text, ar.is_correct 
                  FROM answer_results ar 
                       LEFT JOIN answers a 
                            ON ar.answer_id = a.id
                 WHERE ar.question_id = {question_id};
            """
        )
        answers = self.cursor.fetchall()
        return answers

    def send_testing_results_to_db(self, username, poll_question, is_correct_answer):
        date = datetime.date.today()
        query = f'''
            INSERT INTO testing_results(user_id, question_id, is_correct_answer, answer_date)
                   VALUES(
                       (SELECT id
                          FROM public.users
                         WHERE login = '{username}'),
                       (SELECT id 
                          FROM public.questions 
                         WHERE text = '{poll_question}'),
                       {is_correct_answer},
                       '{date}'
                   )
        '''
        self.cursor.execute(query)

    def clear_user_testing_track(self, user_name: str):
        query = f"""
                DELETE FROM testing_track WHERE user_name = '{user_name}'
            """
        self.cursor.execute(query)

    def add_question_to_testing_track(self, user_name: str, question_id: int):
        query = f"""
            INSERT INTO public.testing_track (user_name, question_id, is_correct)
            VALUES('{user_name}', {question_id}, NULL)
        """
        self.cursor.execute(query)

    def set_answer_to_testing_track(self, user_name: str, poll_question: str, is_correct: bool):

        query = f"""
            UPDATE public.testing_track 
               SET is_correct = {is_correct}
             where user_name = '{user_name}' 
               and question_id = (SELECT id 
                                    FROM public.questions 
                                   WHERE text = '{poll_question}')
        """
        self.cursor.execute(query)

    def check_user_testing(self, user_name: str):
        query = f"""
            select exists(
                select 1
                  from testing_track
                 where user_name = '{user_name}'
            )
        """
        self.cursor.execute(query)
        is_testing = self.cursor.fetchone()[0]
        return is_testing

    def get_user_testing_question_number(self, user_name: str):
        query = f"""
            select count(*)
              from testing_track 
             where user_name = '{user_name}'
        """
        self.cursor.execute(query)
        current_question_number = self.cursor.fetchone()[0]
        return current_question_number


    def check_answer_existing(self, user_name: str, question_id: int):
        query = f"""
            select exists(
                select 1
                  from testing_track 
                 where user_name = '{user_name}'
                   and question_id = {question_id}
                   and is_correct IS NOT NULL
             )
        """
        self.cursor.execute(query)
        is_existing = self.cursor.fetchone()[0]
        return is_existing

    def add_question_track(self, user_name: str, correct_option_id: int, question: str, poll_id: str):
        query = f"""
            INSERT INTO active_question_track (user_name, correct_option_id, question, poll_id)
            VALUES('{user_name}', {correct_option_id}, '{question}', '{poll_id}')
        """
        self.cursor.execute(query)

    def get_active_question_data(self, user_name: str, poll_id: str):
        query = f"""
            SELECT correct_option_id, question
              FROM public.active_question_track 
             WHERE user_name = '{user_name}'
               and poll_id = '{poll_id}'
        """
        self.cursor.execute(query)
        obj = self.cursor.fetchone()
        correct_option_id, question = obj
        clear_data_query = f"""
            DELETE FROM public.active_question_track 
             WHERE user_name = '{user_name}'
               AND poll_id = '{poll_id}'
        """
        self.cursor.execute(clear_data_query)
        return correct_option_id, question
