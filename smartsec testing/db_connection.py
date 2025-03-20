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

    def get_quiz_question_data(self) -> dict[str: str]:
        self.cursor.execute("SELECT * FROM questions LIMIT 1;")
        question = self.cursor.fetchone()
        return {"question_id": question[0],
                "question_text": question[1],
                "is_required": question[2],
                "explanation": question[3]}

    def get_question_answers(self, question_id) -> list[tuple[Any, ...]]:
        self.cursor.execute(
            f"""
                SELECT a.text, ar.is_correct 
                  FROM answer_results ar left join answers a 
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
                    (
                     SELECT id 
                       FROM public.users 
                      WHERE login = '{username}'
                    ),
                    (
                     SELECT id 
                       FROM public.questions 
                      WHERE text = '{poll_question}'
                    ),
                    {is_correct_answer},
                    '{date}'
                )
        '''
        self.cursor.execute(query)