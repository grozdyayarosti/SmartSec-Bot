import random
from typing import Any

import psycopg2
import datetime

from constants import PG_DBNAME, PG_USER, PG_PASSWORD, PG_HOST, PG_PORT


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

    def check_last_answer(self):
        self.cursor.execute(f"""
            select is_correct_answer from testing_results tr
            WHERE is_correct_answer
            and answer_date IS NOT NULL
            order by answer_date desc
            limit 1;
        """)
        is_correct = self.cursor.fetchone()
        return False
        # return is_correct[0]

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


    def get_quiz_question_data(self) -> dict[str: str]:
        random_number = random.randint(1, 3)
        self.cursor.execute(f"SELECT * FROM questions WHERE id={random_number};")
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